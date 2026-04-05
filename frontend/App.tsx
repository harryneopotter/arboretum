import React, { useEffect } from 'react';
import { View, StyleSheet, BackHandler } from 'react-native';
import { StatusBar } from 'expo-status-bar';
import { SafeAreaProvider, SafeAreaView } from 'react-native-safe-area-context';
import { AppProvider, useStore, Screen } from './store';
import { TouchableOpacity } from 'react-native';
import { Home, Camera, Activity, Settings, Leaf } from 'lucide-react-native';

import {
  HomeScreen,
  IdentifyScreen,
  ResultsScreen,
  ProfileScreen,
  DiagnosisScreen,
  SettingsScreen,
  SearchResultsScreen,
  MyPlantsScreen,
  EditProfileScreen,
  FullCareGuideScreen,
  OnboardingScreen,
} from './screens';

const colors = {
  primary: '#23472b',
  primaryContainer: '#3a5f41',
  surface: '#f8faf6',
  background: '#f8faf6',
  text: '#191c1a',
  tertiaryFixed: '#b9f0ba',
};

function AppContent() {
  const {
    currentScreen,
    navigate,
    goBack,
    identificationResults,
    identifiedPlant,
    identificationMessage,
    identifyImage,
    loadPlant,
    isLoading,
  } = useStore();

  useEffect(() => {
    const onHardwareBack = () => {
      if (currentScreen !== 'HOME' && currentScreen !== 'ONBOARDING') {
        goBack();
        return true;
      }
      return false;
    };

    const subscription = BackHandler.addEventListener('hardwareBackPress', onHardwareBack);
    return () => subscription.remove();
  }, [currentScreen, goBack]);

  const renderScreen = () => {
    switch (currentScreen) {
      case 'ONBOARDING':
        return <OnboardingScreen navigate={navigate} />;

      case 'HOME':
        return (
          <HomeScreen navigate={navigate} />
        );

      case 'IDENTIFY':
        return (
          <IdentifyScreen 
            navigate={navigate} 
            identifyPlant={identifyImage}
          />
        );

      case 'RESULTS':
        return (
          <ResultsScreen 
            navigate={navigate}
            matches={identificationResults}
            bestMatch={identifiedPlant}
            isLoading={isLoading}
            message={identificationMessage}
            onSelectMatch={async (slug) => {
              const loaded = await loadPlant(slug);
              if (loaded) {
                navigate('PROFILE');
                return true;
              }
              return false;
            }}
          />
        );

      case 'PROFILE':
        return <ProfileScreen navigate={navigate} />;

      case 'DIAGNOSIS':
        return <DiagnosisScreen navigate={navigate} />;

      case 'SETTINGS':
        return <SettingsScreen navigate={navigate} />;

      case 'SEARCH_RESULTS':
        return (
          <SearchResultsScreen navigate={navigate} />
        );

      case 'MY_PLANTS':
        return (
          <MyPlantsScreen navigate={navigate} />
        );

      case 'EDIT_PROFILE':
        return <EditProfileScreen navigate={navigate} />;

      case 'FULL_CARE_GUIDE':
        return <FullCareGuideScreen navigate={navigate} />;

      default:
        return <HomeScreen navigate={navigate} />;
    }
  };

  const navItems = [
    { id: 'HOME' as Screen, icon: Home },
    { id: 'IDENTIFY' as Screen, icon: Camera },
    { id: 'DIAGNOSIS' as Screen, icon: Activity },
    { id: 'MY_PLANTS' as Screen, icon: Leaf },
    { id: 'SETTINGS' as Screen, icon: Settings },
  ];

  const isIdentifyFlow = ['IDENTIFY', 'RESULTS', 'PROFILE', 'FULL_CARE_GUIDE'].includes(currentScreen);
  const isMyPlantsFlow = currentScreen === 'MY_PLANTS';

  return (
    <SafeAreaView style={styles.container} edges={['top', 'bottom']}>
      <StatusBar style="dark" />
      
      <View style={styles.content}>
        {renderScreen()}
      </View>

      {currentScreen !== 'ONBOARDING' && currentScreen !== 'SEARCH_RESULTS' && (
        <View style={styles.navBar}>
          {navItems.map((item) => {
            const Icon = item.icon;
            let isActive = currentScreen === item.id;
            if (item.id === 'IDENTIFY' && isIdentifyFlow) isActive = true;
            if (item.id === 'MY_PLANTS' && isMyPlantsFlow) isActive = true;

            return (
              <TouchableOpacity
                key={item.id}
                onPress={() => navigate(item.id)}
                style={[styles.navItem, isActive && styles.navItemActive]}
              >
                <Icon
                  size={24}
                  color={isActive ? colors.tertiaryFixed : colors.primaryContainer}
                  strokeWidth={isActive ? 2 : 1.5}
                />
                {isActive && <View style={styles.navDot} />}
              </TouchableOpacity>
            );
          })}
        </View>
      )}
    </SafeAreaView>
  );
}

export default function App() {
  return (
    <SafeAreaProvider>
      <AppProvider>
        <AppContent />
      </AppProvider>
    </SafeAreaProvider>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: colors.background },
  content: { flex: 1 },
  navBar: {
    flexDirection: 'row',
    justifyContent: 'space-around',
    padding: 16,
    paddingBottom: 24,
    backgroundColor: colors.surface,
    borderTopWidth: 1,
    borderTopColor: 'rgba(25,28,26,0.05)',
  },
  navItem: {
    alignItems: 'center',
    justifyContent: 'center',
    width: 48,
    height: 48,
    borderRadius: 24,
  },
  navItemActive: { backgroundColor: colors.primary },
  navDot: {
    width: 4,
    height: 4,
    borderRadius: 2,
    backgroundColor: colors.primary,
    marginTop: 4,
  },
});
