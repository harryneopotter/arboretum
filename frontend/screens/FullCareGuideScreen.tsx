import React from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
} from 'react-native';
import { ArrowLeft, Droplet, Sun, Droplets, Thermometer, Leaf, AlertCircle } from 'lucide-react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useStore } from '../store';
import { colors } from '../theme';

const fallbackSections = [
  { icon: Droplet, title: 'Watering', fallback: 'Every 1-2 weeks', detail: 'Allow the top layer of soil to dry before watering again.' },
  { icon: Sun, title: 'Light', fallback: 'Bright, indirect', detail: 'Keep near a bright window with filtered light.' },
  { icon: Droplets, title: 'Humidity', fallback: 'Moderate', detail: 'Raise humidity if the air is very dry.' },
  { icon: Thermometer, title: 'Temperature', fallback: '18-27C', detail: 'Protect the plant from cold drafts and sudden temperature swings.' },
  { icon: Leaf, title: 'Soil', fallback: 'Well draining', detail: 'Use a loose, airy potting mix that drains well.' },
];

export default function FullCareGuideScreen({ navigate }: { navigate: (s: string) => void }) {
  const { currentPlant } = useStore();

  const care = currentPlant?.care;
  const commonProblems = currentPlant?.common_problems || [];

  const sections = fallbackSections.map((section) => {
    const value =
      section.title === 'Watering'
        ? care?.watering_frequency
        : section.title === 'Light'
          ? care?.light_requirements
          : section.title === 'Soil'
            ? care?.soil_type
            : section.title === 'Temperature'
              ? care?.temperature_range
              : undefined;

    return {
      ...section,
      value: value || section.fallback,
    };
  });

  return (
    <SafeAreaView style={styles.container}>
      <View style={styles.header}>
        <TouchableOpacity style={styles.backButton} onPress={() => navigate('PROFILE')}>
          <ArrowLeft size={24} color={colors.text} strokeWidth={1.5} />
        </TouchableOpacity>
        <Text style={styles.headline}>Care Guide</Text>
        <View style={styles.placeholder} />
      </View>

      <ScrollView style={styles.scrollView} showsVerticalScrollIndicator={false}>
        {currentPlant ? (
          <>
            <Text style={styles.scientificName}>{currentPlant.category || 'Plant Profile'}</Text>
            <Text style={styles.commonName}>{currentPlant.plant_name}</Text>

            {currentPlant.description ? (
              <Text style={styles.introText}>{currentPlant.description}</Text>
            ) : null}

            {sections.map((section, index) => {
              const Icon = section.icon;
              return (
                <View key={index} style={styles.careCard}>
                  <View style={styles.careIconContainer}>
                    <Icon size={24} color={colors.primary} strokeWidth={1.5} />
                  </View>
                  <Text style={styles.careTitle}>{section.title}</Text>
                  <Text style={styles.careValue}>{section.value}</Text>
                  <Text style={styles.careDetail}>{section.detail}</Text>
                </View>
              );
            })}

            {commonProblems.length > 0 && (
              <>
                <Text style={styles.sectionHeader}>Common Problems</Text>
                {commonProblems.slice(0, 4).map((problem, index) => {
                  const symptom =
                    typeof problem === 'object' && problem && 'symptom' in problem
                      ? String(problem.symptom)
                      : `Problem ${index + 1}`;
                  const fix =
                    typeof problem === 'object' && problem && 'fix' in problem
                      ? String(problem.fix)
                      : '';
                  const causes =
                    typeof problem === 'object' && problem && 'possible_causes' in problem && Array.isArray(problem.possible_causes)
                      ? problem.possible_causes.map(String).join(', ')
                      : '';

                  return (
                    <View key={index} style={styles.problemCard}>
                      <View style={styles.problemHeader}>
                        <AlertCircle size={20} color={colors.primary} strokeWidth={2} />
                        <Text style={styles.problemSymptom}>{symptom}</Text>
                      </View>
                      <View style={styles.problemDetails}>
                        {causes ? <Text style={styles.problemText}>Causes: {causes}</Text> : null}
                        {fix ? <Text style={styles.problemText}>Fix: {fix}</Text> : null}
                      </View>
                    </View>
                  );
                })}
              </>
            )}
          </>
        ) : (
          <View style={styles.emptyState}>
            <Text style={styles.emptyTitle}>No plant selected</Text>
            <Text style={styles.emptyText}>
              Open a plant profile first, then return here for a care guide based on real plant data.
            </Text>
            <TouchableOpacity style={styles.emptyButton} onPress={() => navigate('HOME')}>
              <Text style={styles.emptyButtonText}>Go to Home</Text>
            </TouchableOpacity>
          </View>
        )}
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: colors.surface },
  header: { flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between', paddingHorizontal: 24, paddingTop: 32, paddingBottom: 16 },
  backButton: { width: 44, height: 44, borderRadius: 9999, backgroundColor: colors.surface, alignItems: 'center', justifyContent: 'center' },
  headline: { fontSize: 28, fontWeight: '600', color: colors.text, letterSpacing: -0.5 },
  placeholder: { width: 44 },
  scrollView: { flex: 1, paddingHorizontal: 24, paddingBottom: 48 },
  scientificName: { fontSize: 14, fontWeight: '700', color: colors.primary, letterSpacing: 0.5, textTransform: 'uppercase', marginTop: 8 },
  commonName: { fontSize: 32, fontWeight: '700', color: colors.text, marginBottom: 12, letterSpacing: -0.5 },
  introText: { color: colors.textMuted, fontSize: 15, lineHeight: 22, marginBottom: 24 },
  careCard: { backgroundColor: colors.surface, borderRadius: 24, padding: 20, marginBottom: 16, shadowColor: colors.primary, shadowOffset: { width: 0, height: 0 }, shadowOpacity: 0.04, shadowRadius: 24, elevation: 2 },
  careIconContainer: { width: 48, height: 48, borderRadius: 16, backgroundColor: colors.surfaceAlt, alignItems: 'center', justifyContent: 'center', marginBottom: 12 },
  careTitle: { fontSize: 12, fontWeight: '700', color: colors.primary, letterSpacing: 0.5, textTransform: 'uppercase', marginBottom: 4 },
  careValue: { fontSize: 20, fontWeight: '600', color: colors.text, marginBottom: 6 },
  careDetail: { fontSize: 14, color: colors.textMuted, lineHeight: 20 },
  sectionHeader: { fontSize: 22, fontWeight: '600', color: colors.text, marginBottom: 16, marginTop: 8 },
  problemCard: { backgroundColor: colors.surface, borderRadius: 24, padding: 20, marginBottom: 12 },
  problemHeader: { flexDirection: 'row', alignItems: 'center', marginBottom: 12 },
  problemSymptom: { fontSize: 16, fontWeight: '600', color: colors.text, marginLeft: 8 },
  problemDetails: { paddingLeft: 28 },
  problemText: { fontSize: 14, color: colors.textMuted, marginBottom: 4, lineHeight: 20 },
  emptyState: { paddingVertical: 64, alignItems: 'center' },
  emptyTitle: { fontSize: 24, fontWeight: '700', color: colors.text, marginBottom: 8 },
  emptyText: { textAlign: 'center', color: colors.textMuted, lineHeight: 22, marginBottom: 20 },
  emptyButton: { backgroundColor: colors.primary, paddingHorizontal: 20, paddingVertical: 14, borderRadius: 20 },
  emptyButtonText: { color: colors.surface, fontWeight: '600' },
});
