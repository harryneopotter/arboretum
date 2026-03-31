import React, { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  Image,
  TextInput,
} from 'react-native';
import { Search, Scan, Activity, Wind, Leaf } from 'lucide-react-native';
import { Label, AmbientCard } from '../components';
import { colors } from '../theme';
import { useStore } from '../store';

const featuredPlants = [
  { name: 'Ficus Elastica', sub: 'Rubber Plant', img: require('../assets/images/ficus.jpg') },
  { name: 'Calathea Ornata', sub: 'Pinstripe', img: require('../assets/images/calathea.jpg') },
];

export default function HomeScreen({ navigate }: { navigate: (s: string) => void }) {
  const { searchPlants, searchResults, savedPlants, isLoading } = useStore();
  const [searchText, setSearchText] = useState('');

  const handleSearch = async () => {
    if (!searchText.trim()) return;
    await searchPlants(searchText);
    navigate('SEARCH_RESULTS');
  };

  return (
    <ScrollView style={styles.container} showsVerticalScrollIndicator={false}>
      <View style={styles.header}>
        <View>
          <Label>The Arboretum</Label>
          <Text style={styles.title}>Plant Care</Text>
        </View>
        <Image 
          source={require('../assets/images/avatar.jpg')} 
          style={styles.avatar} 
        />
      </View>

      <View style={styles.searchContainer}>
        <View style={styles.searchBox}>
          <Search size={20} color={colors.primaryDark} strokeWidth={1.5} />
          <TextInput 
            style={styles.searchText} 
            placeholder="Search plants or symptoms..."
            placeholderTextColor={colors.textMuted}
            value={searchText}
            onChangeText={setSearchText}
            returnKeyType="search"
            onSubmitEditing={handleSearch}
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
          onPress={() => navigate('DIAGNOSIS')}
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
          {isLoading && <Label>Loading...</Label>}
        </View>
        <ScrollView horizontal showsHorizontalScrollIndicator={false}>
          {featuredPlants.map((plant, i) => (
            <TouchableOpacity 
              key={i} 
              style={styles.plantCard} 
              onPress={() => navigate('PROFILE')}
            >
              <Image source={plant.img} style={styles.plantImage} />
              <Label style={styles.plantLabel}>{plant.sub}</Label>
              <Text style={styles.plantName}>{plant.name}</Text>
            </TouchableOpacity>
          ))}
        </ScrollView>
      </View>

      <View style={styles.seasonalSection}>
        <Text style={styles.sectionTitle}>Seasonal Insights</Text>
        <AmbientCard>
          <View style={styles.insightRow}>
            <View style={styles.windIcon}>
              <Wind size={24} color={colors.primaryDark} strokeWidth={1.5} />
            </View>
            <View>
              <Text style={styles.insightTitle}>Winter Dormancy</Text>
              <Text style={styles.insightText}>Reduce watering as light drops.</Text>
            </View>
          </View>
        </AmbientCard>
      </View>

      <View style={{ height: 100 }} />
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: colors.background },
  header: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', padding: 24, paddingTop: 48 },
  title: { fontSize: 32, fontWeight: '600', color: colors.text, marginTop: 8 },
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
  insightRow: { flexDirection: 'row', gap: 16 },
  windIcon: { width: 48, height: 48, backgroundColor: '#e8ece6', borderRadius: 16, alignItems: 'center', justifyContent: 'center' },
  insightTitle: { fontSize: 18, fontWeight: '500', color: colors.text, marginBottom: 4 },
  insightText: { color: colors.textMuted, fontSize: 14 },
});
