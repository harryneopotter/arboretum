import React, { useEffect, useState } from 'react';
import { View, Text, StyleSheet, ScrollView, TouchableOpacity, Image } from 'react-native';
import { ChevronRight, RefreshCw } from 'lucide-react-native';
import { Label } from '../components';
import { colors } from '../theme';
import { api } from '../api/client';
import { useStore } from '../store';

export default function SettingsScreen({ navigate }: { navigate: (s: string) => void }) {
  const { profile, savedPlants } = useStore();
  const [backendHealthy, setBackendHealthy] = useState<boolean | null>(null);

  const loadHealth = async (onResult?: (healthy: boolean) => void) => {
    const healthy = await api.health();
    if (onResult) onResult(healthy);
    else setBackendHealthy(healthy);
  };

  useEffect(() => {
    let mounted = true;

    loadHealth((healthy) => {
      if (mounted) setBackendHealthy(healthy);
    });

    return () => {
      mounted = false;
    };
  }, []);

  const actionRows = [
    {
      title: 'Edit Profile',
      description: 'Update your name, email, location, and bio',
      onPress: () => navigate('EDIT_PROFILE'),
    },
    {
      title: 'My Plants',
      description: `${savedPlants.length} saved plants`,
      onPress: () => navigate('MY_PLANTS'),
    },
    {
      title: 'Diagnose Plant',
      description: 'Run the real symptom checker against the backend',
      onPress: () => navigate('DIAGNOSIS'),
    },
  ];

  const infoRows = [
    {
      title: 'Backend',
      description:
        backendHealthy === null ? 'Checking connection...' : backendHealthy ? 'FastAPI + Qdrant online' : 'Backend offline',
    },
    {
      title: 'App Version',
      description: '1.0.1',
    },
    {
      title: 'Location',
      description: profile.location,
    },
  ];

  return (
    <ScrollView style={styles.container} showsVerticalScrollIndicator={false}>
      <View style={styles.header}>
        <Label>TOTAL PLANTS</Label>
        <Text style={styles.count}>{savedPlants.length}</Text>
      </View>

      <View style={styles.statsRow}>
        <Label>{profile.name}</Label>
        <Label>{profile.location}</Label>
      </View>

      <View style={styles.content}>
        <TouchableOpacity
          style={styles.profileSection}
          activeOpacity={0.8}
          onPress={() => navigate('EDIT_PROFILE')}
        >
          <Image
            source={profile.avatarUrl ? { uri: profile.avatarUrl } : require('../assets/images/avatar.jpg')}
            style={styles.avatar}
          />
          <View style={styles.profileText}>
            <Text style={styles.name}>{profile.name}</Text>
            <Text style={styles.email}>{profile.email}</Text>
          </View>
          <ChevronRight size={20} color={colors.textMuted} strokeWidth={1.5} style={styles.chevron} />
        </TouchableOpacity>

        <View style={styles.section}>
          <Label>Quick Actions</Label>
          <View style={styles.list}>
            {actionRows.map((item) => (
              <TouchableOpacity key={item.title} style={styles.row} onPress={item.onPress} activeOpacity={0.8}>
                <View style={styles.rowText}>
                  <Text style={styles.itemTitle}>{item.title}</Text>
                  <Text style={styles.itemDescription}>{item.description}</Text>
                </View>
                <ChevronRight size={20} color={colors.textMuted} strokeWidth={1.5} />
              </TouchableOpacity>
            ))}
          </View>
        </View>

        <View style={styles.section}>
          <Label>App Info</Label>
          <View style={styles.list}>
            {infoRows.map((item) => (
              <View key={item.title} style={styles.row}>
                <View style={styles.rowText}>
                  <Text style={styles.itemTitle}>{item.title}</Text>
                  <Text style={styles.itemDescription}>{item.description}</Text>
                </View>
                {item.title === 'Backend' ? (
                  <TouchableOpacity onPress={() => loadHealth()}>
                    <RefreshCw size={18} color={colors.textMuted} strokeWidth={1.8} />
                  </TouchableOpacity>
                ) : null}
              </View>
            ))}
          </View>
        </View>
      </View>

      <View style={{ height: 100 }} />
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: colors.background },
  header: { padding: 24, paddingTop: 48, alignItems: 'center' },
  count: { fontSize: 56, fontWeight: '700', color: colors.text },
  statsRow: { flexDirection: 'row', justifyContent: 'space-around', marginBottom: 24, paddingHorizontal: 24 },
  content: { padding: 24 },
  profileSection: { flexDirection: 'row', alignItems: 'center', marginBottom: 24 },
  avatar: { width: 64, height: 64, borderRadius: 32, marginRight: 16 },
  profileText: { flex: 1 },
  name: { fontSize: 18, fontWeight: '500', color: colors.text },
  email: { color: colors.textMuted, marginTop: 2 },
  chevron: { marginLeft: 'auto' },
  section: { marginBottom: 24 },
  list: { borderRadius: 20, marginTop: 8, overflow: 'hidden', backgroundColor: colors.surface },
  row: { flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between', padding: 16, borderBottomWidth: 1, borderBottomColor: colors.surfaceAlt },
  rowText: { flex: 1, paddingRight: 12 },
  itemTitle: { fontSize: 16, fontWeight: '600', color: colors.text },
  itemDescription: { marginTop: 4, color: colors.textMuted, lineHeight: 20 },
});
