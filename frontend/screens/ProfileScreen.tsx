// ProfileScreen.tsx - Wired to store
import React from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  Image,
} from 'react-native';
import { ArrowLeft, Droplet, Sun, Heart } from 'lucide-react-native';
import { Label } from '../components';
import { colors } from '../theme';
import { useStore } from '../store';
import { getPlantImage } from '../utils';

export default function ProfileScreen({ navigate }: { navigate: (s: string) => void }) {
  const { currentPlant, savePlant, removePlant, isSaved } = useStore();

  if (!currentPlant) {
    return (
      <View style={styles.container}>
        <TouchableOpacity onPress={() => navigate('HOME')}>
          <ArrowLeft size={24} />
        </TouchableOpacity>
        <Text>Loading...</Text>
      </View>
    );
  }

  const plantId = currentPlant.slug || currentPlant.id || 'unknown';
  const saved = isSaved(plantId);
  const heroImage = currentPlant.image_url
    ? { uri: currentPlant.image_url }
    : getPlantImage(currentPlant.slug || currentPlant.plant_name);
  const commonProblems = currentPlant.common_problems || [];

  return (
    <View style={styles.container}>
      <TouchableOpacity style={styles.backBtn} onPress={() => navigate('RESULTS')}>
        <ArrowLeft size={24} color={colors.surface} strokeWidth={1.5} />
      </TouchableOpacity>

      <TouchableOpacity style={styles.saveBtn} onPress={() => saved ? removePlant(plantId) : savePlant(plantId)}>
        <Heart size={24} color={saved ? colors.tertiaryFixed : colors.surface} fill={saved ? colors.tertiaryFixed : 'transparent'} strokeWidth={1.5} />
      </TouchableOpacity>

      <ScrollView showsVerticalScrollIndicator={false}>
        <Image source={heroImage} style={styles.heroImage} />

        <View style={styles.content}>
          <Label style={styles.family}>{currentPlant.category || 'Tropical'}</Label>
          <Text style={styles.name}>{currentPlant.plant_name}</Text>

          {currentPlant.alternate_names?.length ? (
            <View style={styles.altNames}>
              {currentPlant.alternate_names.map((name) => (
                <View key={name} style={styles.altNameChip}>
                  <Text style={styles.altNameText}>{name}</Text>
                </View>
              ))}
            </View>
          ) : null}

          <View style={styles.tags}>
            <View style={styles.tag}><Text style={styles.tagText}>Easy Care</Text></View>
            <View style={styles.tag}><Text style={styles.tagText}>Air Purifying</Text></View>
          </View>

          <View style={styles.tabs}>
            <Text style={styles.tabActive}>Overview</Text>
            <Text style={styles.tab}>Care</Text>
            <Text style={styles.tab}>Problems</Text>
          </View>

          <View style={styles.careCard}>
            <View style={styles.careIcon}>
              <Droplet size={24} color={colors.primaryDark} strokeWidth={1.5} />
            </View>
            <View>
              <Text style={styles.careTitle}>Watering</Text>
              <Text style={styles.careText}>
                {currentPlant.care?.watering_frequency || 'Every 1-2 weeks'}
              </Text>
            </View>
          </View>

          <View style={styles.careCard}>
            <View style={styles.careIcon}>
              <Sun size={24} color={colors.primaryDark} strokeWidth={1.5} />
            </View>
            <View>
              <Text style={styles.careTitle}>Light</Text>
              <Text style={styles.careText}>
                {currentPlant.care?.light_requirements || 'Bright indirect'}
              </Text>
            </View>
          </View>

          {currentPlant.description && (
            <View style={styles.origin}>
              <Text style={styles.originTitle}>About</Text>
              <Text style={styles.originText}>{currentPlant.description}</Text>
            </View>
          )}

          {commonProblems.length > 0 && (
            <View style={styles.origin}>
              <Text style={styles.originTitle}>Common Problems</Text>
              {commonProblems.slice(0, 3).map((problem, index) => {
                const symptom = typeof problem === 'object' && problem && 'symptom' in problem ? String(problem.symptom) : `Issue ${index + 1}`;
                const fix = typeof problem === 'object' && problem && 'fix' in problem ? String(problem.fix) : '';
                return (
                  <View key={index} style={styles.problemCard}>
                    <Text style={styles.problemSymptom}>{symptom}</Text>
                    {fix ? <Text style={styles.problemFix}>{fix}</Text> : null}
                  </View>
                );
              })}
            </View>
          )}

          <TouchableOpacity 
            style={styles.guideBtn}
            onPress={() => navigate('FULL_CARE_GUIDE')}
          >
            <Text style={styles.guideText}>Full Care Guide</Text>
          </TouchableOpacity>

          <View style={{ height: 100 }} />
        </View>
      </ScrollView>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: colors.background },
  backBtn: { 
    position: 'absolute', top: 48, left: 24, zIndex: 20,
    width: 48, height: 48, borderRadius: 24, 
    backgroundColor: 'rgba(255,255,255,0.8)', 
    alignItems: 'center', justifyContent: 'center',
    shadowColor: colors.text, shadowOpacity: 0.1, shadowRadius: 8,
  },
  saveBtn: { 
    position: 'absolute', top: 48, right: 24, zIndex: 20,
    width: 48, height: 48, borderRadius: 24, 
    backgroundColor: 'rgba(255,255,255,0.8)', 
    alignItems: 'center', justifyContent: 'center',
    shadowColor: colors.text, shadowOpacity: 0.1, shadowRadius: 8,
  },
  heroImage: { width: '100%', height: 360 },
  content: { 
    marginTop: -40, backgroundColor: colors.background, 
    borderTopLeftRadius: 40, borderTopRightRadius: 40, 
    padding: 24, paddingTop: 32, minHeight: 500,
  },
  family: { marginBottom: 8 },
  name: { fontSize: 36, fontWeight: '700', color: colors.text, marginBottom: 16 },
  altNames: { flexDirection: 'row', flexWrap: 'wrap', gap: 8, marginBottom: 16 },
  altNameChip: { backgroundColor: colors.surfaceAlt, paddingHorizontal: 12, paddingVertical: 6, borderRadius: 9999 },
  altNameText: { fontSize: 12, fontWeight: '600', color: colors.primaryDark },
  tags: { flexDirection: 'row', flexWrap: 'wrap', gap: 8, marginBottom: 24 },
  tag: { backgroundColor: colors.surfaceAlt, paddingHorizontal: 14, paddingVertical: 6, borderRadius: 16 },
  tagText: { fontSize: 13, fontWeight: '500', color: colors.text },
  tabs: { flexDirection: 'row', gap: 24, marginBottom: 24, borderBottomWidth: 1, borderBottomColor: 'rgba(25,28,26,0.1)', paddingBottom: 12 },
  tab: { fontSize: 16, color: colors.textMuted },
  tabActive: { fontSize: 16, fontWeight: '600', color: colors.primary },
  careCard: { flexDirection: 'row', gap: 16, backgroundColor: colors.surface, borderRadius: 24, padding: 24, marginBottom: 16 },
  careIcon: { width: 48, height: 48, backgroundColor: '#e8ece6', borderRadius: 24, alignItems: 'center', justifyContent: 'center' },
  careTitle: { fontSize: 16, fontWeight: '600', color: colors.text, marginBottom: 4 },
  careText: { color: colors.textMuted, fontSize: 14, lineHeight: 20 },
  origin: { marginTop: 8, marginBottom: 24 },
  originTitle: { fontSize: 18, fontWeight: '600', color: colors.text, marginBottom: 8 },
  originText: { color: colors.textMuted, fontSize: 14, lineHeight: 22 },
  problemCard: { backgroundColor: colors.surface, borderRadius: 18, padding: 16, marginBottom: 12 },
  problemSymptom: { fontSize: 15, fontWeight: '600', color: colors.text, marginBottom: 4 },
  problemFix: { color: colors.textMuted, fontSize: 13, lineHeight: 18 },
  guideBtn: { backgroundColor: colors.primary, borderRadius: 24, padding: 18, alignItems: 'center', marginTop: 8 },
  guideText: { color: colors.surface, fontSize: 16, fontWeight: '600' },
});
