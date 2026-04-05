import React from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  Alert,
} from 'react-native';
import { ArrowLeft } from 'lucide-react-native';
import { Label, AmbientCard } from '../components';
import { colors } from '../theme';
import { useStore } from '../store';

export default function SearchResultsScreen({ navigate }: { navigate: (s: string) => void }) {
  const { searchQuery, searchResults, loadPlant, isSearching, searchError, loadPlantError } = useStore();

  const handleSelect = async (slug: string) => {
    const loaded = await loadPlant(slug);
    if (loaded) {
      navigate('PROFILE');
    } else {
      Alert.alert('Plant unavailable', loadPlantError || 'This plant profile could not be loaded right now.');
    }
  };

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <TouchableOpacity onPress={() => navigate('HOME')} style={styles.backButton}>
          <ArrowLeft size={24} color={colors.text} strokeWidth={1.5} />
        </TouchableOpacity>
        <View style={styles.headerContent}>
          <Label>Search Results</Label>
          <View style={styles.queryRow}>
            <Text style={styles.query} numberOfLines={1}>{searchQuery}</Text>
            {isSearching && <Text style={styles.loading}>Searching...</Text>}
          </View>
        </View>
      </View>

      <ScrollView style={styles.results} showsVerticalScrollIndicator={false}>
        {searchError ? (
          <View style={styles.errorCard}>
            <Text style={styles.errorTitle}>Search unavailable</Text>
            <Text style={styles.errorText}>{searchError}</Text>
          </View>
        ) : null}

        {searchResults.length === 0 && !isSearching && (
          <View style={styles.empty}>
            <Text style={styles.emptyText}>
              {searchError ? 'Could not run search right now.' : 'No plants found matching your search.'}
            </Text>
            <Text style={styles.emptySub}>Try different keywords like plant names, symptoms, or care needs.</Text>
          </View>
        )}

        {searchResults.map((result, i) => (
          <TouchableOpacity
            key={result.slug || i}
            style={styles.resultCard}
            onPress={() => handleSelect(result.slug)}
            activeOpacity={0.8}
          >
            <AmbientCard>
              <View style={styles.resultContent}>
                <View style={styles.scoreBadge}>
                  <Text style={styles.scoreText}>{Math.round(result.score * 100)}%</Text>
                </View>
                <View style={styles.resultInfo}>
                  <Label style={styles.category}>{result.category || 'Plant'}</Label>
                  <Text style={styles.plantName}>{result.plant_name}</Text>
                  {result.description && (
                    <Text style={styles.description} numberOfLines={2}>
                      {result.description}
                    </Text>
                  )}
                </View>
              </View>
            </AmbientCard>
          </TouchableOpacity>
        ))}

        <View style={{ height: 100 }} />
      </ScrollView>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: colors.background },
  header: { flexDirection: 'row', alignItems: 'center', padding: 24, paddingTop: 60 },
  backButton: { width: 48, height: 48, alignItems: 'center', justifyContent: 'center' },
  headerContent: { marginLeft: 8, flex: 1 },
  queryRow: { flexDirection: 'row', alignItems: 'center', marginTop: 4 },
  query: { fontSize: 24, fontWeight: '600', color: colors.text },
  loading: { marginLeft: 8, color: colors.primaryDark, fontSize: 14 },
  results: { paddingHorizontal: 24 },
  errorCard: { backgroundColor: colors.surfaceAlt, borderRadius: 16, padding: 16, marginBottom: 16 },
  errorTitle: { fontSize: 16, fontWeight: '700', color: colors.text, marginBottom: 6 },
  errorText: { color: colors.textMuted, lineHeight: 20 },
  empty: { alignItems: 'center', padding: 40 },
  emptyText: { fontSize: 18, fontWeight: '500', color: colors.text, textAlign: 'center' },
  emptySub: { marginTop: 8, color: colors.textMuted, textAlign: 'center' },
  resultCard: { marginBottom: 16 },
  resultContent: { flexDirection: 'row', alignItems: 'flex-start' },
  scoreBadge: { 
    backgroundColor: colors.tertiaryFixed, 
    borderRadius: 16, 
    paddingHorizontal: 8, 
    paddingVertical: 4,
    marginRight: 12 
  },
  scoreText: { color: colors.primary, fontWeight: '600', fontSize: 12 },
  resultInfo: { flex: 1 },
  category: { marginBottom: 4 },
  plantName: { fontSize: 18, fontWeight: '500', color: colors.text, marginBottom: 4 },
  description: { color: colors.textMuted, fontSize: 14 },
});
