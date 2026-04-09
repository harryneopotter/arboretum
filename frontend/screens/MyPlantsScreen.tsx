import React from 'react';
import { useEffect, useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  ActivityIndicator,
  Alert,
} from 'react-native';
import { Image } from 'expo-image';
import { Plus, Droplet } from 'lucide-react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { colors } from '../theme';
import { api } from '../api/client';
import { Plant, useStore } from '../store';
import { getBestPlantImage } from '../utils';

export default function MyPlantsScreen({ navigate }: { navigate: (s: string) => void }) {
  const { savedPlants, loadPlant, loadPlantError } = useStore();
  const [plants, setPlants] = useState<Plant[]>([]);
  const [unavailableIds, setUnavailableIds] = useState<string[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    let mounted = true;

    const loadPlants = async () => {
      setIsLoading(true);
      try {
        const data = await Promise.allSettled(
          savedPlants.map(async (id) => ({ id, plant: await api.getPlant(id) }))
        );
        if (mounted) {
          const available: Plant[] = [];
          const unavailable: string[] = [];
          for (let index = 0; index < data.length; index += 1) {
            const result = data[index];
            const savedId = savedPlants[index];
            if (result.status === 'fulfilled' && result.value.plant) {
              available.push(result.value.plant);
            } else if (savedId) {
              unavailable.push(savedId);
            }
          }
          setPlants(available);
          setUnavailableIds(unavailable);
        }
      } finally {
        if (mounted) {
          setIsLoading(false);
        }
      }
    };

    loadPlants();

    return () => {
      mounted = false;
    };
  }, [savedPlants]);

  const handleOpenPlant = async (plant: Plant) => {
    const loadedPlant = await loadPlant(plant.slug || plant.id);
    if (loadedPlant) {
      navigate('PROFILE');
    } else {
      Alert.alert('Plant unavailable', loadPlantError || 'This saved plant profile could not be loaded right now.');
    }
  };

  const handleOpenCareGuide = async (plant: Plant) => {
    const loadedPlant = await loadPlant(plant.slug || plant.id);
    if (loadedPlant) {
      navigate('FULL_CARE_GUIDE');
    } else {
      Alert.alert('Care guide unavailable', loadPlantError || 'This plant profile could not be loaded right now.');
    }
  };

  const handleRetryUnavailable = async () => {
    if (savedPlants.length === 0) return;
    setIsLoading(true);
    try {
      const data = await Promise.allSettled(
        savedPlants.map(async (id) => ({ id, plant: await api.getPlant(id) }))
      );
      const available: Plant[] = [];
      const unavailable: string[] = [];
      for (let index = 0; index < data.length; index += 1) {
        const result = data[index];
        const savedId = savedPlants[index];
        if (result.status === 'fulfilled' && result.value.plant) {
          available.push(result.value.plant);
        } else if (savedId) {
          unavailable.push(savedId);
        }
      }
      setPlants(available);
      setUnavailableIds(unavailable);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <SafeAreaView style={styles.container}>
      <View style={styles.header}>
        <View>
          <Text style={styles.label}>MY COLLECTION</Text>
          <Text style={styles.headline}>My Plants</Text>
        </View>
        <TouchableOpacity style={styles.addButton} onPress={() => navigate('IDENTIFY')}>
          <Plus size={24} color={colors.primary} strokeWidth={2} />
        </TouchableOpacity>
      </View>

      <ScrollView style={styles.scrollView} showsVerticalScrollIndicator={false}>
        {isLoading ? (
          <View style={styles.loading}>
            <ActivityIndicator size="large" color={colors.primary} />
            <Text style={styles.loadingText}>Loading saved plants...</Text>
          </View>
        ) : plants.length > 0 ? (
          plants.map((plant) => (
            <TouchableOpacity
              key={plant.slug || plant.id}
              style={styles.plantCard}
              onPress={() => handleOpenPlant(plant)}
              activeOpacity={0.8}
            >
              <View style={styles.cardContent}>
                 <Image
                   source={getBestPlantImage(plant)}
                   style={styles.plantImage}
                   cachePolicy="disk"
                 />
                <View style={styles.plantInfo}>
                  <Text style={styles.plantName}>{plant.plant_name}</Text>
                  <View style={styles.waterInfo}>
                    <Droplet size={14} color={colors.primary} strokeWidth={2} style={styles.waterIcon} />
                    <Text style={styles.waterText}>
                      {plant.care?.watering_frequency || plant.category || 'Saved from search'}
                    </Text>
                  </View>
                </View>
                <TouchableOpacity style={styles.waterButton} onPress={() => handleOpenCareGuide(plant)} activeOpacity={0.8}>
                  <Droplet size={20} color={colors.primary} strokeWidth={2} />
                </TouchableOpacity>
              </View>
            </TouchableOpacity>
          ))
        ) : (
          <TouchableOpacity style={styles.emptyCard} onPress={() => navigate('IDENTIFY')}>
            <Text style={styles.emptyText}>Add a New Plant</Text>
            <Text style={styles.emptySubtext}>Identify or search for plants</Text>
          </TouchableOpacity>
        )}

        {!isLoading && unavailableIds.length > 0 ? (
          <View style={styles.unavailableCard}>
            <Text style={styles.unavailableTitle}>Some saved plants are temporarily unavailable</Text>
            <Text style={styles.unavailableText}>
              {unavailableIds.length} saved item{unavailableIds.length > 1 ? 's are' : ' is'} not loading right now.
            </Text>
            <TouchableOpacity style={styles.retryButton} onPress={handleRetryUnavailable} activeOpacity={0.8}>
              <Text style={styles.retryButtonText}>Retry loading</Text>
            </TouchableOpacity>
          </View>
        ) : null}
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: colors.surface },
  header: { flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between', paddingHorizontal: 24, paddingTop: 32, paddingBottom: 24 },
  label: { fontSize: 12, fontWeight: '700', color: colors.primary, letterSpacing: 1.5, marginBottom: 4 },
  headline: { fontSize: 32, fontWeight: '600', color: colors.text },
  addButton: { width: 48, height: 48, borderRadius: 16, backgroundColor: colors.surface, alignItems: 'center', justifyContent: 'center', shadowColor: colors.primary, shadowOffset: { width: 0, height: 0 }, shadowOpacity: 0.06, shadowRadius: 32, elevation: 4 },
  scrollView: { flex: 1, paddingHorizontal: 24, paddingBottom: 80 },
  loading: { paddingVertical: 64, alignItems: 'center' },
  loadingText: { marginTop: 12, color: colors.primaryDark },
  plantCard: { backgroundColor: colors.surface, borderRadius: 24, marginBottom: 16, padding: 16, shadowColor: colors.primary, shadowOffset: { width: 0, height: 0 }, shadowOpacity: 0.04, shadowRadius: 24, elevation: 2 },
  cardContent: { flexDirection: 'row', alignItems: 'center' },
  plantImage: { width: 64, height: 64, borderRadius: 16 },
  plantInfo: { flex: 1, marginLeft: 16 },
  plantName: { fontSize: 18, fontWeight: '500', color: colors.text, marginBottom: 4 },
  waterInfo: { flexDirection: 'row', alignItems: 'center' },
  waterIcon: { marginRight: 6 },
  waterText: { fontSize: 14, color: colors.primaryDark },
  waterButton: { width: 44, height: 44, borderRadius: 12, backgroundColor: colors.tertiaryFixed, alignItems: 'center', justifyContent: 'center' },
  emptyCard: { backgroundColor: colors.surfaceAlt, borderRadius: 24, padding: 24, alignItems: 'center', marginTop: 16, borderWidth: 2, borderColor: 'rgba(35,71,43,0.1)', borderStyle: 'dashed' },
  emptyText: { fontSize: 16, fontWeight: '600', color: colors.text, marginBottom: 4 },
  emptySubtext: { fontSize: 14, color: colors.primaryDark },
  unavailableCard: { backgroundColor: colors.surfaceAlt, borderRadius: 16, padding: 16, marginTop: 12, marginBottom: 24 },
  unavailableTitle: { fontSize: 15, fontWeight: '700', color: colors.text, marginBottom: 6 },
  unavailableText: { color: colors.primaryDark, marginBottom: 12 },
  retryButton: { alignSelf: 'flex-start', backgroundColor: colors.primary, borderRadius: 12, paddingHorizontal: 12, paddingVertical: 8 },
  retryButtonText: { color: colors.surface, fontWeight: '600' },
});
