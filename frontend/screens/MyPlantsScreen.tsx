import React from 'react';
import { useEffect, useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  Image,
  ActivityIndicator,
} from 'react-native';
import { Plus, Droplet } from 'lucide-react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { colors } from '../theme';
import { api } from '../api/client';
import { Plant, useStore } from '../store';
import { getPlantImage } from '../utils';

export default function MyPlantsScreen({ navigate }: { navigate: (s: string) => void }) {
  const { savedPlants, loadPlant } = useStore();
  const [plants, setPlants] = useState<Plant[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    let mounted = true;

    const loadPlants = async () => {
      setIsLoading(true);
      try {
        const data = await Promise.all(
          savedPlants.map(async (id) => api.getPlant(id))
        );
        if (mounted) {
          setPlants(data.filter(Boolean) as Plant[]);
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
    await loadPlant(plant.slug || plant.id);
    navigate('PROFILE');
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
                  source={plant.image_url ? { uri: plant.image_url } : getPlantImage(plant.slug || plant.plant_name)}
                  style={styles.plantImage}
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
                <View style={styles.waterButton}>
                  <Droplet size={20} color={colors.primary} strokeWidth={2} />
                </View>
              </View>
            </TouchableOpacity>
          ))
        ) : (
          <TouchableOpacity style={styles.emptyCard} onPress={() => navigate('IDENTIFY')}>
            <Text style={styles.emptyText}>Add a New Plant</Text>
            <Text style={styles.emptySubtext}>Identify or search for plants</Text>
          </TouchableOpacity>
        )}
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
});
