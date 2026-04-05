import React, { useState, useRef } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  Image,
  Alert,
  ActivityIndicator,
} from 'react-native';
import { Camera as CameraIcon, Scan, ArrowLeft, RefreshCw } from 'lucide-react-native';
import { Label, Button } from '../components';
import { colors } from '../theme';
import * as ImagePicker from 'expo-image-picker';

export default function IdentifyScreen({ navigate, identifyPlant }: { navigate: (s: string) => void, identifyPlant: (img: string) => Promise<void> }) {
  const [capturedImage, setCapturedImage] = useState<string | null>(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);

  const pickFromCamera = async () => {
    const { status } = await ImagePicker.requestCameraPermissionsAsync();
    if (status !== 'granted') {
      Alert.alert('Permission needed', 'Camera access is required to identify plants');
      return;
    }

    const result = await ImagePicker.launchCameraAsync({
      base64: true,
      quality: 0.8,
      allowsEditing: true,
      aspect: [1, 1],
    });

    if (!result.canceled && result.assets[0]?.base64) {
      setCapturedImage(result.assets[0].uri);
      handleIdentify(result.assets[0].base64);
    }
  };

  const pickFromGallery = async () => {
    const { status } = await ImagePicker.requestMediaLibraryPermissionsAsync();
    if (status !== 'granted') {
      Alert.alert('Permission needed', 'Gallery access is required');
      return;
    }

    const result = await ImagePicker.launchImageLibraryAsync({
      base64: true,
      quality: 0.8,
      allowsEditing: true,
      aspect: [1, 1],
    });

    if (!result.canceled && result.assets[0]?.base64) {
      setCapturedImage(result.assets[0].uri);
      handleIdentify(result.assets[0].base64);
    }
  };

  const handleIdentify = async (base64Image: string) => {
    setIsAnalyzing(true);
    try {
      await identifyPlant(base64Image);
      navigate('RESULTS');
    } catch (e) {
      const message = e instanceof Error && e.message ? e.message : 'Please try again with better lighting';
      Alert.alert('Failed to identify', message);
    } finally {
      setIsAnalyzing(false);
    }
  };

  if (isAnalyzing) {
    return (
      <View style={styles.container}>
        <View style={styles.loadingBox}>
          <ActivityIndicator size="large" color={colors.primary} />
          <Text style={styles.loadingText}>AI is analyzing...</Text>
          <Text style={styles.loadingSub}>Searching botanical database</Text>
        </View>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <TouchableOpacity style={styles.backBtn} onPress={() => navigate('HOME')}>
        <ArrowLeft size={24} color={colors.text} strokeWidth={1.5} />
      </TouchableOpacity>

      <View style={styles.header}>
        <Label>Botanical Vision</Label>
        <Text style={styles.title}>Identify Your{'\n'}Green Companion</Text>
      </View>

      {capturedImage ? (
        <View style={styles.previewContainer}>
          <Image source={{ uri: capturedImage }} style={styles.preview} />
          <View style={styles.previewOverlay}>
            <TouchableOpacity style={styles.retakeBtn} onPress={() => setCapturedImage(null)}>
              <RefreshCw size={20} color={colors.surface} />
              <Text style={styles.retakeText}>Retake</Text>
            </TouchableOpacity>
          </View>
        </View>
      ) : (
        <View style={styles.uploadContainer}>
          <View style={styles.iconWrapper}>
            <CameraIcon size={48} color={colors.primary} strokeWidth={1.5} />
          </View>
          <Text style={styles.uploadTitle}>Tap to Identify</Text>
          <Text style={styles.uploadText}>Position leaf or flower in center</Text>

          <TouchableOpacity style={styles.cameraBtn} onPress={pickFromCamera}>
            <Scan size={20} color={colors.surface} />
            <Text style={styles.cameraBtnText}>Take Photo</Text>
          </TouchableOpacity>

          <TouchableOpacity style={styles.galleryBtn} onPress={pickFromGallery}>
            <Text style={styles.galleryText}>Choose from Gallery</Text>
          </TouchableOpacity>
        </View>
      )}

      <Text style={styles.aiNote}>
        AI-powered plant matching
      </Text>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: colors.background },
  backBtn: { position: 'absolute', top: 56, left: 24, zIndex: 10, padding: 8 },
  header: { paddingHorizontal: 24, paddingTop: 60, paddingBottom: 24 },
  title: { fontSize: 32, fontWeight: '600', color: colors.text, marginTop: 8, lineHeight: 40 },
  uploadContainer: { flex: 1, marginHorizontal: 24, marginBottom: 24, backgroundColor: colors.surfaceAlt, borderRadius: 32, alignItems: 'center', justifyContent: 'center', padding: 32 },
  iconWrapper: { width: 80, height: 80, backgroundColor: colors.surface, borderRadius: 40, alignItems: 'center', justifyContent: 'center', marginBottom: 24 },
  uploadTitle: { fontSize: 22, fontWeight: '500', color: colors.text, marginBottom: 8 },
  uploadText: { color: colors.textMuted, textAlign: 'center', marginBottom: 32 },
  cameraBtn: { flexDirection: 'row', alignItems: 'center', backgroundColor: colors.primary, paddingHorizontal: 32, paddingVertical: 16, borderRadius: 24, marginBottom: 16 },
  cameraBtnText: { color: colors.surface, fontWeight: '600', marginLeft: 12, fontSize: 16 },
  galleryBtn: { padding: 12 },
  galleryText: { color: colors.primary, fontWeight: '500' },
  previewContainer: { flex: 1, marginHorizontal: 24, marginBottom: 24, borderRadius: 32, overflow: 'hidden' },
  preview: { flex: 1, width: '100%', height: '100%' },
  previewOverlay: { ...StyleSheet.absoluteFillObject, justifyContent: 'flex-end', padding: 24, backgroundColor: 'rgba(0,0,0,0.3)' },
  retakeBtn: { flexDirection: 'row', alignItems: 'center', alignSelf: 'center', backgroundColor: 'rgba(255,255,255,0.9)', paddingHorizontal: 20, paddingVertical: 12, borderRadius: 24 },
  retakeText: { marginLeft: 8, color: colors.text, fontWeight: '500' },
  loadingBox: { flex: 1, justifyContent: 'center', alignItems: 'center' },
  loadingText: { marginTop: 16, fontSize: 18, fontWeight: '500', color: colors.text },
  loadingSub: { marginTop: 8, color: colors.textMuted },
  aiNote: { textAlign: 'center', color: colors.textMutedLight, fontSize: 12, marginBottom: 32 },
});
