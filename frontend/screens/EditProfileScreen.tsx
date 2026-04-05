import React, { useEffect, useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  TextInput,
  Image,
  Alert,
} from 'react-native';
import { ArrowLeft, Camera, Check } from 'lucide-react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useStore } from '../store';
import * as ImagePicker from 'expo-image-picker';

const colors = {
  primary: '#23472b',
  primaryContainer: '#3a5f41',
  tertiaryFixed: '#b9f0ba',
  surface: '#f8faf6',
  surfaceContainerLowest: '#ffffff',
  surfaceContainerLow: '#f2f4f0',
  surfaceContainerHigh: '#e8ece6',
  text: '#191c1a',
  textMuted: '#3a5f41',
};

export default function EditProfileScreen({ navigate }: { navigate: (s: string) => void }) {
  const { profile, updateProfile } = useStore();
  const [name, setName] = useState(profile.name);
  const [email, setEmail] = useState(profile.email);
  const [location, setLocation] = useState(profile.location);
  const [bio, setBio] = useState(profile.bio);
  const [avatarUrl, setAvatarUrl] = useState(profile.avatarUrl || '');

  useEffect(() => {
    setName(profile.name);
    setEmail(profile.email);
    setLocation(profile.location);
    setBio(profile.bio);
    setAvatarUrl(profile.avatarUrl || '');
  }, [profile]);

  const handleSave = () => {
    updateProfile({
      name,
      email,
      location,
      bio,
      avatarUrl: avatarUrl || undefined,
    });
    navigate('SETTINGS');
  };

  const handlePickAvatar = async () => {
    const { status } = await ImagePicker.requestMediaLibraryPermissionsAsync();
    if (status !== 'granted') {
      Alert.alert('Permission needed', 'Gallery access is required to change your profile photo.');
      return;
    }
    const result = await ImagePicker.launchImageLibraryAsync({
      mediaTypes: ['images'],
      allowsEditing: true,
      quality: 0.8,
      aspect: [1, 1],
    });
    if (!result.canceled && result.assets[0]?.uri) {
      setAvatarUrl(result.assets[0].uri);
    }
  };

  return (
    <SafeAreaView style={styles.container}>
      {/* Header */}
      <View style={styles.header}>
        <TouchableOpacity style={styles.backButton} onPress={() => navigate('SETTINGS')}>
          <ArrowLeft size={24} color={colors.text} strokeWidth={1.5} />
        </TouchableOpacity>
        <Text style={styles.headline}>Edit Profile</Text>
        <TouchableOpacity style={styles.saveButton} onPress={handleSave}>
          <Check size={20} color={colors.primary} strokeWidth={2} />
        </TouchableOpacity>
      </View>

      <ScrollView style={styles.scrollView} showsVerticalScrollIndicator={false}>
        {/* Avatar Section */}
        <View style={styles.avatarSection}>
          <View style={styles.avatarContainer}>
            <Image
              source={avatarUrl ? { uri: avatarUrl } : require('../assets/images/avatar.jpg')}
              style={styles.avatar}
            />
            <TouchableOpacity style={styles.cameraButton} onPress={handlePickAvatar}>
              <Camera size={16} color={colors.primary} strokeWidth={2} />
            </TouchableOpacity>
          </View>
          <Text style={styles.changePhotoText}>Change Photo</Text>
        </View>

        {/* Form Fields */}
        <View style={styles.form}>
          {[
            { label: 'FULL NAME', value: name, onChange: setName, placeholder: 'Enter your name' },
            { label: 'EMAIL', value: email, onChange: setEmail, placeholder: 'Enter your email', keyboard: 'email-address' },
            { label: 'LOCATION', value: location, onChange: setLocation, placeholder: 'Enter your city' },
            { label: 'BIO', value: bio, onChange: setBio, placeholder: 'Tell us about yourself', multiline: true },
          ].map((field, index) => (
            <View key={index} style={styles.field}>
              <Text style={styles.fieldLabel}>{field.label}</Text>
              <TextInput
                style={[styles.input, field.multiline && styles.inputMultiline]}
                value={field.value}
                onChangeText={field.onChange}
                placeholder={field.placeholder}
                placeholderTextColor={colors.textMuted}
                keyboardType={(field.keyboard || 'default') as any}
                multiline={field.multiline || false}
                numberOfLines={field.multiline ? 3 : 1}
              />
            </View>
          ))}
        </View>
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: colors.surface },
  header: { flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between', paddingHorizontal: 24, paddingTop: 32, paddingBottom: 16 },
  backButton: { width: 44, height: 44, borderRadius: 9999, backgroundColor: colors.surfaceContainerLowest, alignItems: 'center', justifyContent: 'center' },
  headline: { fontSize: 28, fontWeight: '600', color: colors.text, letterSpacing: -0.5 },
  saveButton: { width: 44, height: 44, borderRadius: 9999, backgroundColor: colors.tertiaryFixed, alignItems: 'center', justifyContent: 'center' },
  scrollView: { flex: 1 },
  avatarSection: { alignItems: 'center', paddingVertical: 32 },
  avatarContainer: { position: 'relative', marginBottom: 12 },
  avatar: { width: 100, height: 100, borderRadius: 50 },
  cameraButton: { position: 'absolute', bottom: 0, right: 0, width: 32, height: 32, borderRadius: 16, backgroundColor: colors.surfaceContainerLowest, alignItems: 'center', justifyContent: 'center', borderWidth: 2, borderColor: colors.surface },
  changePhotoText: { fontSize: 14, fontWeight: '500', color: colors.primary },
  form: { paddingHorizontal: 24, paddingBottom: 48 },
  field: { marginBottom: 20 },
  fieldLabel: { fontSize: 12, fontWeight: '700', color: colors.primary, letterSpacing: 1, marginBottom: 8 },
  input: { backgroundColor: colors.surfaceContainerLowest, borderRadius: 16, paddingHorizontal: 16, paddingVertical: 16, fontSize: 16, color: colors.text, fontWeight: '500', borderWidth: 1, borderColor: 'rgba(25,28,26,0.1)' },
  inputMultiline: { minHeight: 100, textAlignVertical: 'top', paddingTop: 16 },
});
