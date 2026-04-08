import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  Image,
  TextInput,
  Alert,
  ActivityIndicator,
} from 'react-native';
import { Search, Scan, Activity, Wind, Leaf, Sun, Droplet, CloudRain } from 'lucide-react-native';
import { Label, AmbientCard } from '../components';
import { colors } from '../theme';
import { useStore } from '../store';
import { api } from '../api/client';
import { getBestPlantImage } from '../utils';

type CuratedPlant = {
  slug: string;
  plant_name: string;
  category?: string;
  description?: string;
  image_url?: string;
  reference_images?: Array<{
    url?: string;
    image_url?: string;
    path?: string;
  }>;
};

// North India seasons: Dec-Feb Winter, Mar-May Summer, Jun-Sep Monsoon, Oct-Nov Autumn
function getSeasonalInsight(): { icon: React.ReactNode; title: string; text: string } {
  const month = new Date().getMonth(); // 0 = Jan
  if (month >= 11 || month <= 1) {
    return {
      icon: <Wind size={24} color={colors.primaryDark} strokeWidth={1.5} />,
      title: 'Winter Dormancy',
      text: 'Reduce watering as light drops. Move frost-sensitive plants indoors and away from cold drafts.',
    };
  }
  if (month >= 2 && month <= 4) {
    return {
      icon: <Sun size={24} color={colors.primaryDark} strokeWidth={1.5} />,
      title: 'Spring Growth',
      text: 'Ideal time to repot and fertilise. Increase watering gradually as temperatures rise.',
    };
  }
  if (month >= 5 && month <= 8) {
    return {
      icon: <CloudRain size={24} color={colors.primaryDark} strokeWidth={1.5} />,
      title: 'Monsoon Watch',
      text: 'Check soil moisture before watering — roots can rot fast. Improve drainage and watch for fungal spots.',
    };
  }
  // Oct–Nov: Autumn
  return {
    icon: <Leaf size={24} color={colors.primaryDark} strokeWidth={1.5} />,
    title: 'Autumn Transition',
    text: 'Ease up on fertiliser as growth slows. A great time to propagate cuttings before winter.',
  };
}

const featuredPlants = [
  { name: 'Ficus Elastica', sub: 'Rubber Plant', img: require('../assets/images/ficus.jpg') },
  { name: 'Calathea Ornata', sub: 'Pinstripe', img: require('../assets/images/calathea.jpg') },
];

const CURATED_SEEDS: CuratedPlant[] = [
  { slug: 'parlour-palm', plant_name: 'Parlour Palm', category: 'Indoor Tropical', description: 'Graceful indoor palm with feathery fronds.' },
  { slug: 'kalanchoe-indoor', plant_name: 'Kalanchoe Indoor', category: 'Indoor Flowering', description: 'Succulent with colorful flower clusters.' },
  { slug: 'bamboo-palm', plant_name: 'Bamboo Palm', category: 'Indoor Tropical', description: 'Graceful tropical palm with airy fronds.' },
  { slug: 'boston-fern-variant', plant_name: 'Boston Fern (Variant)', category: 'Indoor Tropical', description: 'Feathery fronds, air-purifying, and humidity-loving.' },
  { slug: 'monstera-adansonii', plant_name: 'Monstera Adansonii', category: 'Indoor Climber', description: 'Compact Monstera with fenestrated leaves.' },
  { slug: 'kentia-palm', plant_name: 'Kentia Palm', category: 'Indoor Tropical', description: 'Elegant tall palm with graceful fronds.' },
];

export default function HomeScreen({ navigate }: { navigate: (s: string) => void }) {
  const { savedPlants, isLoading, loadPlant, loadPlantError, currentPlant, searchPlants, isSearching } = useStore();
  const [searchText, setSearchText] = useState('');
  const [curatedPlants, setCuratedPlants] = useState<CuratedPlant[]>(CURATED_SEEDS);
  const [curatedLoading, setCuratedLoading] = useState(true);

  useEffect(() => {
    let mounted = true;
    const loadCuratedPlants = async () => {
      try {
        const hydrated = await Promise.allSettled(
          CURATED_SEEDS.map(async (seed) => {
            const profile = await api.getPlant(seed.slug);
            return profile
              ? {
                  slug: profile.slug || seed.slug,
                  plant_name: profile.plant_name || seed.plant_name,
                  category: profile.category || seed.category,
                  description: profile.description || seed.description,
                  image_url: profile.image_url,
                  reference_images: profile.reference_images,
                }
              : seed;
          })
        );
        if (mounted) {
          setCuratedPlants(
            hydrated.map((result, index) =>
              result.status === 'fulfilled' && result.value
                ? result.value
                : CURATED_SEEDS[index]
            )
          );
        }
      } catch {
        if (mounted) setCuratedPlants(CURATED_SEEDS);
      } finally {
        if (mounted) setCuratedLoading(false);
      }
    };

    loadCuratedPlants();
    return () => { mounted = false; };
  }, []);

  const handleSearch = async () => {
    if (!searchText.trim()) return;
    await searchPlants(searchText);
    navigate('SEARCH_RESULTS');
  };

  return (
    <ScrollView style={styles.container} showsVerticalScrollIndicator={false}>
      <View style={styles.header}>
        <Image
          source={require('../assets/logo.png')}
          style={styles.brandLogo}
          resizeMode="contain"
        />
        <Image 
          source={require('../assets/images/avatar.jpg')} 
          style={styles.avatar} 
        />
      </View>

      <View style={styles.searchContainer}>
        <View style={styles.searchBox}>
          {isSearching ? (
            <ActivityIndicator size="small" color={colors.primary} />
          ) : (
            <Search size={20} color={colors.primaryDark} strokeWidth={1.5} />
          )}
          <TextInput 
            style={styles.searchText} 
            placeholder="Search plants or symptoms..."
            placeholderTextColor={colors.textMuted}
            value={searchText}
            onChangeText={setSearchText}
            returnKeyType="search"
            onSubmitEditing={handleSearch}
            editable={!isSearching}
          />
        </View>
      </View>

      <View style={styles.heroContainer}>
        <TouchableOpacity 
          style={styles.identifyCard}
          onPress={() => navigate('IDENTIFY')}
        >
          <View style={styles.identifyIcon}>
            <Scan size={24} color="#b9f0ba" strokeWidth={1.5} />
          </View>
          <View>
            <Text style={styles.identifyTitle}>Identify Plant</Text>
            <Text style={styles.identifySubtitle}>Scan to discover species</Text>
          </View>
          <Image 
            source={require('../assets/images/monstera.jpg')}
            style={styles.identifyBg}
          />
        </TouchableOpacity>

        <TouchableOpacity 
          style={styles.diagnoseCard}
          onPress={() => {
            if (currentPlant) {
              navigate('DIAGNOSIS');
              return;
            }
            if (savedPlants.length > 0) {
              Alert.alert('Choose a plant first', 'Open one of your saved plants to run diagnosis.');
              navigate('MY_PLANTS');
              return;
            }
            Alert.alert('Identify a plant first', 'Capture or search a plant before diagnosing issues.');
            navigate('IDENTIFY');
          }}
        >
          <View>
            <Label style={styles.comingSoonLabel}>Plant Health</Label>
            <Text style={styles.diagnoseTitle}>Diagnose Problem</Text>
          </View>
          <View style={styles.diagnoseIcon}>
            <Activity size={24} color={colors.primaryDark} strokeWidth={1.5} />
          </View>
        </TouchableOpacity>

        <TouchableOpacity 
          style={styles.myPlantsCard}
          onPress={() => navigate('MY_PLANTS')}
        >
          <View>
            <Text style={styles.myPlantsTitle}>My Plants</Text>
            <Text style={styles.myPlantsCount}>{savedPlants.length} saved</Text>
          </View>
          <View style={styles.myPlantsIcon}>
            <Leaf size={24} color={colors.primary} strokeWidth={1.5} />
          </View>
        </TouchableOpacity>
      </View>

      <View style={styles.collectionSection}>
        <View style={styles.collectionHeader}>
          <Text style={styles.sectionTitle}>Curated Collection</Text>
          {(isLoading || curatedLoading) && <Label>Loading...</Label>}
        </View>
        <ScrollView horizontal showsHorizontalScrollIndicator={false}>
          {curatedPlants.length > 0 ? (
            curatedPlants.map((plant, i) => (
              <TouchableOpacity
                key={plant.slug || i}
                style={styles.plantCard}
                onPress={async () => {
                  const loadedPlant = await loadPlant(plant.slug);
                  if (loadedPlant) {
                    navigate('PROFILE');
                  } else {
                    Alert.alert('Plant unavailable', loadPlantError || 'This plant profile could not be loaded right now.');
                  }
                }}
              >
                <Image
                  source={getBestPlantImage(plant)}
                  style={styles.plantImage}
                />
                <Label style={styles.plantLabel}>{plant.category || 'Houseplant'}</Label>
                <Text style={styles.plantName}>{plant.plant_name}</Text>
              </TouchableOpacity>
            ))
          ) : (
            featuredPlants.map((plant, i) => (
              <TouchableOpacity
                key={i}
                style={styles.plantCard}
                onPress={() => navigate('PROFILE')}
              >
                <Image source={plant.img} style={styles.plantImage} />
                <Label style={styles.plantLabel}>{plant.sub}</Label>
                <Text style={styles.plantName}>{plant.name}</Text>
              </TouchableOpacity>
            ))
          )}
        </ScrollView>
      </View>

      <View style={styles.seasonalSection}>
        <Text style={styles.sectionTitle}>Seasonal Insights</Text>
        <AmbientCard>
          {(() => {
            const insight = getSeasonalInsight();
            return (
              <View style={styles.insightRow}>
                <View style={styles.windIcon}>{insight.icon}</View>
                <View style={styles.insightBody}>
                  <Text style={styles.insightTitle}>{insight.title}</Text>
                  <Text style={styles.insightText}>{insight.text}</Text>
                </View>
              </View>
            );
          })()}
        </AmbientCard>
      </View>

      <View style={{ height: 100 }} />
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: colors.background },
  header: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', padding: 24, paddingTop: 48, gap: 16 },
  brandLogo: { width: 230, height: 76, flexShrink: 1 },
  avatar: { width: 48, height: 48, borderRadius: 24 },
  searchContainer: { paddingHorizontal: 24, marginBottom: 24 },
  searchBox: { flexDirection: 'row', alignItems: 'center', backgroundColor: colors.surfaceAlt, borderRadius: 16, padding: 16 },
  searchText: { flex: 1, marginLeft: 12, fontSize: 16, color: colors.text },
  heroContainer: { padding: 24, gap: 16 },
  identifyCard: { backgroundColor: colors.primary, borderRadius: 24, padding: 24, minHeight: 140, justifyContent: 'space-between', overflow: 'hidden', position: 'relative' },
  identifyIcon: { width: 48, height: 48, backgroundColor: 'rgba(185,240,186,0.2)', borderRadius: 24, alignItems: 'center', justifyContent: 'center' },
  identifyTitle: { fontSize: 22, fontWeight: '500', color: colors.surface, marginTop: 16 },
  identifySubtitle: { color: 'rgba(255,255,255,0.8)', fontSize: 14 },
  identifyBg: { position: 'absolute', right: -48, bottom: -48, width: 256, height: 256, opacity: 0.2, borderRadius: 128 },
  diagnoseCard: { backgroundColor: colors.surfaceAlt, borderRadius: 24, padding: 24, flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between' },
  comingSoonLabel: { opacity: 0.6, marginBottom: 4 },
  diagnoseTitle: { fontSize: 20, fontWeight: '500', color: colors.text },
  diagnoseIcon: { width: 48, height: 48, backgroundColor: colors.surface, borderRadius: 24, alignItems: 'center', justifyContent: 'center' },
  myPlantsCard: { backgroundColor: '#e8ece6', borderRadius: 24, padding: 24, flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between' },
  myPlantsTitle: { fontSize: 20, fontWeight: '500', color: colors.text },
  myPlantsCount: { color: colors.textMuted, marginTop: 4 },
  myPlantsIcon: { width: 48, height: 48, backgroundColor: colors.surface, borderRadius: 24, alignItems: 'center', justifyContent: 'center' },
  collectionSection: { marginTop: 32, paddingLeft: 24 },
  collectionHeader: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', paddingRight: 24, marginBottom: 16 },
  sectionTitle: { fontSize: 22, fontWeight: '500', color: colors.text },
  plantCard: { width: 240, marginRight: 16 },
  plantImage: { height: 256, borderRadius: 24, width: '100%' },
  plantLabel: { marginVertical: 8 },
  plantName: { fontSize: 18, fontWeight: '500', color: colors.text },
  seasonalSection: { marginTop: 24, paddingHorizontal: 24, marginBottom: 32 },
  insightRow: { flexDirection: 'row', gap: 16, alignItems: 'flex-start' },
  insightBody: { flex: 1 },
  windIcon: { width: 48, height: 48, backgroundColor: '#e8ece6', borderRadius: 16, alignItems: 'center', justifyContent: 'center' },
  insightTitle: { fontSize: 18, fontWeight: '500', color: colors.text, marginBottom: 4 },
  insightText: { color: colors.textMuted, fontSize: 14 },
});
