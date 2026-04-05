import React from 'react';
import { View, Text, StyleSheet, ScrollView, TouchableOpacity, Image, ActivityIndicator, Alert } from 'react-native';
import { Camera } from 'lucide-react-native';
import { Label, Button } from '../components';
import { colors } from '../theme';
import { Plant, SearchResult } from '../store';
import { getBestPlantImage } from '../utils';

export default function ResultsScreen({ 
  navigate, 
  matches, 
  bestMatch, 
  isLoading,
  message,
  onSelectMatch,
}: { 
  navigate: (s: string) => void, 
  matches: SearchResult[], 
  bestMatch: Plant | null,
  isLoading: boolean,
  message?: string | null,
  onSelectMatch: (slug: string) => Promise<boolean>,
}) {
  if (isLoading) {
    return (
      <View style={styles.center}>
        <ActivityIndicator size="large" color={colors.primary} />
        <Text style={styles.loadingText}>Analyzing...</Text>
      </View>
    );
  }

  const primaryCandidate = matches[0] || null;
  const secondaryMatches = bestMatch ? matches.slice(1, 4) : matches.slice(0, 4);
  const bestMatchScore = matches[0]?.score ?? 0;
  const bestMatchSource = getBestPlantImage(bestMatch || undefined);

  return (
    <ScrollView style={styles.container} showsVerticalScrollIndicator={false}>
      <View style={styles.header}>
        <View style={styles.badge}>
          <View style={styles.pulseDot} />
          <Text style={styles.badgeText}>Analysis Complete</Text>
        </View>
        <Text style={styles.title}>Identification Results</Text>
        <Text style={styles.subtitle}>
          {message || `${matches.length} potential matches found`}
        </Text>
      </View>

      <View style={styles.resultsContainer}>
        {bestMatch && (
          <TouchableOpacity style={styles.bestMatchCard} onPress={() => navigate('PROFILE')}>
            <View style={styles.matchBadge}>
              <Text style={styles.matchBadgeText}>{Math.round(bestMatchScore * 100)}% Match</Text>
            </View>
            <Image source={bestMatchSource} style={styles.bestMatchImage} />
            <View style={styles.bestMatchContent}>
              <Label>{bestMatch.category || 'Tropical Plant'}</Label>
              <Text style={styles.bestMatchName}>{bestMatch.plant_name}</Text>
              <Text style={styles.bestMatchDesc} numberOfLines={2}>
                {bestMatch.description || 'A beautiful houseplant perfect for indoor conditions.'}
              </Text>
              <Button onPress={() => navigate('PROFILE')}>
                View Full Profile
              </Button>
            </View>
          </TouchableOpacity>
        )}

        {secondaryMatches.length > 0 && (
          <View style={styles.secondaryContainer}>
            {secondaryMatches.map((match, i) => (
              <TouchableOpacity
                key={match.slug || i}
                style={styles.secondaryMatch}
                activeOpacity={0.85}
                onPress={async () => {
                  const ok = await onSelectMatch(match.slug);
                  if (!ok) {
                    Alert.alert('Plant unavailable', 'Could not open this candidate profile right now.');
                  }
                }}
              >
                <View style={{ flex: 1 }}>
                  <Label style={{ color: colors.textMutedLight, fontSize: 10, marginBottom: 4 }}>
                    {match.category || 'Related Species'}
                  </Label>
                  <Text style={styles.secondaryName}>{match.plant_name}</Text>
                </View>
                <Text style={styles.secondaryConf}>{Math.round(match.score * 100)}%</Text>
              </TouchableOpacity>
            ))}
          </View>
        )}

        {!bestMatch && primaryCandidate && (
          <View style={styles.retakeContainer}>
            <Text style={styles.retakeText}>No confident best match yet. Try selecting a candidate above or retake with better lighting.</Text>
          </View>
        )}

        <View style={styles.retakeContainer}>
          <Text style={styles.retakeText}>Not seeing a match? Try another photo.</Text>
          <Button variant="outline" onPress={() => navigate('IDENTIFY')}>
            Retake Photo
          </Button>
        </View>
      </View>

      <View style={{ height: 100 }} />
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: colors.background },
  center: { flex: 1, justifyContent: 'center', alignItems: 'center' },
  loadingText: { marginTop: 16, fontSize: 16, color: colors.textMuted },
  header: { paddingHorizontal: 24, paddingTop: 60, paddingBottom: 24 },
  badge: { flexDirection: 'row', alignItems: 'center', backgroundColor: colors.tertiaryFixed, paddingHorizontal: 16, paddingVertical: 8, borderRadius: 20, alignSelf: 'flex-start', marginBottom: 16 },
  pulseDot: { width: 8, height: 8, backgroundColor: colors.primary, borderRadius: 4, marginRight: 8 },
  badgeText: { fontSize: 12, fontWeight: '700', color: colors.primary },
  title: { fontSize: 32, fontWeight: '600', color: colors.text, marginBottom: 8 },
  subtitle: { color: colors.textMuted, fontSize: 16 },
  resultsContainer: { paddingHorizontal: 24 },
  bestMatchCard: { backgroundColor: colors.surface, borderRadius: 24, overflow: 'hidden', marginBottom: 24 },
  matchBadge: { position: 'absolute', top: 16, right: 16, backgroundColor: colors.tertiaryFixed, paddingHorizontal: 12, paddingVertical: 6, borderRadius: 20, zIndex: 1 },
  matchBadgeText: { fontSize: 12, fontWeight: '700', color: colors.primary },
  bestMatchImage: { height: 192, width: '100%' },
  bestMatchContent: { padding: 24 },
  bestMatchName: { fontSize: 22, fontWeight: '500', color: colors.text, marginBottom: 12 },
  bestMatchDesc: { color: colors.textMuted, fontSize: 14, marginBottom: 16, lineHeight: 20 },
  secondaryContainer: { gap: 12 },
  secondaryMatch: { backgroundColor: colors.surfaceAlt, borderRadius: 20, padding: 16, flexDirection: 'row', alignItems: 'center' },
  secondaryName: { fontSize: 16, fontWeight: '500', color: colors.text },
  secondaryConf: { fontSize: 16, fontWeight: '600', color: colors.primaryDark },
  retakeContainer: { marginTop: 32, alignItems: 'center' },
  retakeText: { color: colors.textMuted, marginBottom: 16 },
});
