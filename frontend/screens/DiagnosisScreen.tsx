import React, { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  TextInput,
  ActivityIndicator,
} from 'react-native';
import { Leaf, AlertCircle } from 'lucide-react-native';
import { Label, Button } from '../components';
import { colors } from '../theme';
import { useStore } from '../store';

export default function DiagnosisScreen({ navigate }: { navigate: (s: string) => void }) {
  const { currentPlant, diagnosePlant, diagnosis, diagnosisMessage, isDiagnosing } = useStore();
  const [symptom, setSymptom] = useState('');

  const plantId = currentPlant?.slug || currentPlant?.id || '';

  const handleDiagnose = async () => {
    if (!plantId || !symptom.trim()) return;
    await diagnosePlant(plantId, symptom.trim());
  };

  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.content} showsVerticalScrollIndicator={false}>
      <View style={styles.iconContainer}>
        <Leaf size={40} color={colors.primaryDark} strokeWidth={1.5} />
        <View style={styles.badge}>
          <AlertCircle size={14} color={colors.primary} strokeWidth={2} />
        </View>
      </View>

      <Text style={styles.title}>Leaf Health Analysis</Text>
      <Label style={styles.comingSoon}>{currentPlant ? currentPlant.plant_name : 'Select a Plant First'}</Label>

      {currentPlant ? (
        <>
          <Text style={styles.description}>
            Describe the symptoms you are seeing and the backend will match them against the plant's known problem entries.
          </Text>

          <View style={styles.form}>
            <Text style={styles.fieldLabel}>Symptoms</Text>
            <TextInput
              style={styles.input}
              value={symptom}
              onChangeText={setSymptom}
              placeholder="Yellow leaves, brown spots, drooping stems..."
              placeholderTextColor={colors.textMuted}
              multiline
              textAlignVertical="top"
            />
            <Button onPress={handleDiagnose} style={styles.button} variant="primary">
              {isDiagnosing ? 'Analyzing...' : 'Analyze Symptoms'}
            </Button>
          </View>

          {isDiagnosing && (
            <View style={styles.loadingRow}>
              <ActivityIndicator size="small" color={colors.primary} />
              <Text style={styles.loadingText}>Checking plant health guidance...</Text>
            </View>
          )}

          {diagnosis && (
            <View style={styles.resultCard}>
              <Text style={styles.resultTitle}>{diagnosis.symptom}</Text>
              <Text style={styles.resultLabel}>Possible causes</Text>
              {diagnosis.possible_causes.map((cause) => (
                <Text key={cause} style={styles.resultItem}>- {cause}</Text>
              ))}
              <Text style={styles.resultLabel}>Fix</Text>
              <Text style={styles.resultBody}>{diagnosis.fix}</Text>
              <Text style={styles.resultLabel}>Prevention</Text>
              <Text style={styles.resultBody}>{diagnosis.prevention}</Text>
            </View>
          )}

          {!diagnosis && diagnosisMessage ? (
            <Text style={styles.message}>{diagnosisMessage}</Text>
          ) : null}
        </>
      ) : (
        <View style={styles.emptyState}>
          <Text style={styles.emptyText}>
            Open a plant profile or identify a plant first, then come back here to diagnose symptoms against real backend data.
          </Text>
          <View style={styles.emptyActions}>
            <Button onPress={() => navigate('HOME')}>Go to Home</Button>
            <Button variant="outline" onPress={() => navigate('IDENTIFY')}>Identify Plant</Button>
          </View>
        </View>
      )}
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: colors.background },
  content: { alignItems: 'center', justifyContent: 'center', padding: 24, paddingTop: 64, paddingBottom: 48 },
  iconContainer: { width: 96, height: 96, backgroundColor: colors.surfaceAlt, borderRadius: 48, alignItems: 'center', justifyContent: 'center', marginBottom: 24 },
  badge: { position: 'absolute', top: 0, right: 0, width: 24, height: 24, backgroundColor: colors.accent, borderRadius: 12, alignItems: 'center', justifyContent: 'center', borderWidth: 4, borderColor: colors.background },
  title: { fontSize: 32, fontWeight: '600', color: colors.text, textAlign: 'center', marginBottom: 16 },
  comingSoon: { backgroundColor: colors.surfaceAlt, paddingHorizontal: 16, paddingVertical: 8, borderRadius: 20, marginBottom: 24 },
  description: { textAlign: 'center', color: colors.textMuted, maxWidth: 320, lineHeight: 22, marginBottom: 24 },
  form: { width: '100%', marginBottom: 20 },
  fieldLabel: { fontSize: 12, fontWeight: '700', color: colors.primary, letterSpacing: 1, marginBottom: 8 },
  input: { minHeight: 120, backgroundColor: colors.surface, borderRadius: 20, padding: 16, color: colors.text, borderWidth: 1, borderColor: colors.border },
  button: { marginTop: 16 },
  loadingRow: { flexDirection: 'row', alignItems: 'center', gap: 10, marginBottom: 20 },
  loadingText: { color: colors.textMuted },
  resultCard: { width: '100%', backgroundColor: colors.surface, borderRadius: 24, padding: 20, marginTop: 12 },
  resultTitle: { fontSize: 18, fontWeight: '700', color: colors.text, marginBottom: 12 },
  resultLabel: { fontSize: 12, fontWeight: '700', color: colors.primary, letterSpacing: 0.8, textTransform: 'uppercase', marginTop: 12, marginBottom: 6 },
  resultItem: { color: colors.textMuted, lineHeight: 20 },
  resultBody: { color: colors.text, lineHeight: 22 },
  message: { marginTop: 16, color: colors.textMuted },
  emptyState: { width: '100%', alignItems: 'center' },
  emptyText: { textAlign: 'center', color: colors.textMuted, lineHeight: 22, marginBottom: 24 },
  emptyActions: { width: '100%', gap: 12 },
});
