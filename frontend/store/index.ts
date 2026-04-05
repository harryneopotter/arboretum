import React, { createContext, useContext, useState, useCallback, useEffect } from 'react';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { api, ApiError, type TelemetryEvent } from '../api/client';

// ---------------------------------------------------------------------------
// UUID v4 generator (no external dependency needed)
// ---------------------------------------------------------------------------
function generateUUID(): string {
  return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, (c) => {
    const r = (Math.random() * 16) | 0;
    return (c === 'x' ? r : (r & 0x3) | 0x8).toString(16);
  });
}

// Types
export type Screen = 'ONBOARDING' | 'HOME' | 'IDENTIFY' | 'RESULTS' | 'PROFILE' | 'DIAGNOSIS' | 'SETTINGS' | 'SEARCH_RESULTS' | 'MY_PLANTS' | 'EDIT_PROFILE' | 'FULL_CARE_GUIDE';

export interface Plant {
  id: string;
  slug?: string;
  plant_name: string;
  category?: string;
  description?: string;
  image_url?: string;
  care?: {
    watering_frequency?: string;
    light_requirements?: string;
    soil_type?: string;
    temperature_range?: string;
  };
  common_problems?: any[];
  alternate_names?: string[];
}

export interface DiagnosisProblem {
  symptom: string;
  possible_causes: string[];
  fix: string;
  prevention: string;
}

export interface UserProfile {
  name: string;
  email: string;
  location: string;
  bio: string;
  avatarUrl?: string;
}

export interface SearchResult {
  slug: string;
  plant_name: string;
  score: number;
  category?: string;
  description?: string;
}

interface AppState {
  // Navigation
  currentScreen: Screen;
  navigate: (screen: Screen) => void;
  goBack: () => void;
  
  // Search
  searchQuery: string;
  searchResults: SearchResult[];
  isSearching: boolean;
  searchError: string | null;
  searchPlants: (query: string) => Promise<void>;
  
  // Plant details
  currentPlant: Plant | null;
  loadPlantError: string | null;
  loadPlant: (id: string) => Promise<Plant | null>;
  
  // Identification
  identificationResults: any[];
  identifiedPlant: Plant | null;
  identificationMessage: string | null;
  identifyImage: (imageBase64: string) => Promise<void>;

  // Diagnosis
  diagnosis: DiagnosisProblem | null;
  diagnosisMessage: string | null;
  isDiagnosing: boolean;
  diagnosePlant: (plantId: string, symptom: string) => Promise<void>;
  
  // Saved plants
  savedPlants: string[];
  savePlant: (id: string) => void;
  removePlant: (id: string) => void;
  isSaved: (id: string) => boolean;
  
  // Loading states
  isLoading: boolean;

  // User profile
  profile: UserProfile;
  updateProfile: (updates: Partial<UserProfile>) => void;

  // Navigation history (for contextual back buttons)
  previousScreen: Screen | null;
}

const AppContext = createContext<AppState | undefined>(undefined);

export function AppProvider({ children }: { children: React.ReactNode }) {
  const [currentScreen, setCurrentScreen] = useState<Screen>('ONBOARDING');
  const [previousScreen, setPreviousScreen] = useState<Screen | null>(null);
  const [navStack, setNavStack] = useState<Screen[]>(['ONBOARDING']);
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState<SearchResult[]>([]);
  const [isSearching, setIsSearching] = useState(false);
  const [searchError, setSearchError] = useState<string | null>(null);
  const [currentPlant, setCurrentPlant] = useState<Plant | null>(null);
  const [loadPlantError, setLoadPlantError] = useState<string | null>(null);
  const [identificationResults, setIdentificationResults] = useState<any[]>([]);
  const [identifiedPlant, setIdentifiedPlant] = useState<Plant | null>(null);
  const [identificationMessage, setIdentificationMessage] = useState<string | null>(null);
  const [diagnosis, setDiagnosis] = useState<DiagnosisProblem | null>(null);
  const [diagnosisMessage, setDiagnosisMessage] = useState<string | null>(null);
  const [isDiagnosing, setIsDiagnosing] = useState(false);
  const [savedPlants, setSavedPlants] = useState<string[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [deviceId, setDeviceId] = useState<string | null>(null);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [profile, setProfile] = useState<UserProfile>({
    name: 'Jane Doe',
    email: 'jane.doe@arboretum.app',
    location: 'New Delhi, India',
    bio: 'Plant enthusiast and urban gardener',
  });

  // On mount: load local first (fast), then sync from backend
  useEffect(() => {
    const init = async () => {
      // 1. Local data for instant render
      const [savedRaw, profileRaw] = await Promise.all([
        AsyncStorage.getItem('savedPlants'),
        AsyncStorage.getItem('profile'),
      ]).catch(() => [null, null] as [null, null]);
      let localSavedPlants: string[] = [];
      let localProfile: Partial<UserProfile> | null = null;
      try {
        localSavedPlants = savedRaw ? JSON.parse(savedRaw) : [];
      } catch {
        localSavedPlants = [];
      }
      try {
        localProfile = profileRaw ? JSON.parse(profileRaw) : null;
      } catch {
        localProfile = null;
      }
      if (localSavedPlants) setSavedPlants(localSavedPlants);
      if (localProfile) setProfile(prev => ({ ...prev, ...localProfile }));

      let currentSession = await AsyncStorage.getItem('sessionId').catch(() => null);
      if (!currentSession) {
        currentSession = generateUUID();
        await AsyncStorage.setItem('sessionId', currentSession).catch(() => {});
      }
      setSessionId(currentSession);

      // 2. Establish device identity
      let id = await AsyncStorage.getItem('deviceId').catch(() => null);
      if (!id) {
        id = generateUUID();
        await AsyncStorage.setItem('deviceId', id).catch(() => {});
      }
      setDeviceId(id);

      // 3. Sync from backend (overrides local when available)
      try {
        const [serverProfile, serverSaved] = await Promise.all([
          api.user.getProfile(id),
          api.user.getSaved(id),
        ]);
        if (serverProfile && (serverProfile.name || serverProfile.email)) {
          const merged: UserProfile = {
            name: serverProfile.name || 'Jane Doe',
            email: serverProfile.email || '',
            location: serverProfile.location || 'New Delhi, India',
            bio: serverProfile.bio || '',
            avatarUrl: serverProfile.avatar_url || undefined,
          };
          setProfile(merged);
          AsyncStorage.setItem('profile', JSON.stringify(merged)).catch(() => {});
        }
        const syncedSaved = Array.isArray(serverSaved) ? serverSaved : [];
        setSavedPlants(syncedSaved);
        AsyncStorage.setItem('savedPlants', JSON.stringify(syncedSaved)).catch(() => {});
      } catch {
        // Backend offline — local data already shown
      }

      void api.telemetry.logEvent({
        device_id: id ?? undefined,
        session_id: currentSession ?? undefined,
        screen: 'BOOT',
        action: 'app_launch',
        status: 'success',
        request_data: {
          source: 'beta',
        },
        response_data: {
          saved_plants: localSavedPlants.length,
          has_profile: Boolean(profileRaw),
        },
      });
    };
    init();
  }, []);

  const trackEvent = useCallback((event: Omit<TelemetryEvent, 'device_id' | 'session_id'>) => {
    if (!deviceId || !sessionId) return;
    void api.telemetry.logEvent({
      device_id: deviceId,
      session_id: sessionId,
      ...event,
    });
  }, [deviceId, sessionId]);

  const navigate = useCallback((screen: Screen) => {
    setPreviousScreen(currentScreen);
    setNavStack(prev => {
      if (prev[prev.length - 1] === screen) {
        return prev;
      }
      return [...prev, screen];
    });
    setCurrentScreen(screen);
    trackEvent({
      screen: currentScreen,
      action: 'screen_view',
      target: screen,
      status: 'success',
      request_data: { from: currentScreen, to: screen },
    });
  }, [currentScreen, trackEvent]);

  const goBack = useCallback(() => {
    setNavStack(prev => {
      if (prev.length <= 1) {
        if (currentScreen !== 'HOME') {
          setPreviousScreen(currentScreen);
          setCurrentScreen('HOME');
        }
        return ['HOME'];
      }
      const next = prev.slice(0, -1);
      const target = next[next.length - 1] || 'HOME';
      setPreviousScreen(currentScreen);
      setCurrentScreen(target);
      trackEvent({
        screen: currentScreen,
        action: 'screen_back',
        target,
        status: 'success',
        request_data: { from: currentScreen, to: target },
      });
      return next;
    });
  }, [currentScreen, trackEvent]);

  const searchPlants = useCallback(async (query: string) => {
    setSearchQuery(query);
    setIsSearching(true);
    setSearchError(null);
    try {
      trackEvent({
        screen: currentScreen,
        action: 'search',
        status: 'start',
        request_data: { query, limit: 10 },
      });
      const results = await api.search(query, 10);
      setSearchResults(results);
      trackEvent({
        screen: currentScreen,
        action: 'search',
        status: 'success',
        request_data: { query, limit: 10 },
        response_data: {
          result_count: results.length,
          top_result: results[0]
            ? {
                slug: results[0].slug,
                plant_name: results[0].plant_name,
                score: results[0].score,
              }
            : null,
        },
      });
    } catch (error) {
      setSearchResults([]);
      const message = error instanceof ApiError ? error.message : 'Search failed';
      setSearchError(message);
      trackEvent({
        screen: currentScreen,
        action: 'search',
        status: 'error',
        request_data: { query, limit: 10 },
        error_text: message,
      });
    } finally {
      setIsSearching(false);
    }
  }, [currentScreen, trackEvent]);

  const loadPlant = useCallback(async (id: string) => {
    setIsLoading(true);
    setLoadPlantError(null);
    try {
      trackEvent({
        screen: currentScreen,
        action: 'load_plant',
        target: id,
        status: 'start',
      });
      const plant = await api.getPlant(id);
      setCurrentPlant(plant);
      trackEvent({
        screen: currentScreen,
        action: 'load_plant',
        target: id,
        status: 'success',
        response_data: plant ? {
          plant_name: plant.plant_name,
          slug: plant.slug || id,
        } : {
          plant_name: null,
          slug: id,
        },
      });
      return plant;
    } catch (error) {
      const message = error instanceof ApiError ? error.message : 'Failed to load plant profile';
      setLoadPlantError(message);
      setCurrentPlant(null);
      trackEvent({
        screen: currentScreen,
        action: 'load_plant',
        target: id,
        status: 'error',
        error_text: message,
      });
      return null;
    } finally {
      setIsLoading(false);
    }
  }, [currentScreen, trackEvent]);

  const identifyImage = useCallback(async (imageBase64: string) => {
    setIsLoading(true);
    setIdentificationMessage(null);
    try {
      trackEvent({
        screen: currentScreen,
        action: 'identify',
        status: 'start',
        request_data: { image_length: imageBase64.length },
      });
      const { matches, plant, message } = await api.identify(imageBase64);
      setIdentificationResults(matches);
      setIdentifiedPlant(plant);
      setCurrentPlant(plant);
      setIdentificationMessage(message ?? null);
      trackEvent({
        screen: currentScreen,
        action: 'identify',
        status: 'success',
        request_data: { image_length: imageBase64.length },
        response_data: {
          match_count: matches.length,
          best_match: matches[0]
            ? {
                slug: matches[0].slug,
                plant_name: matches[0].plant_name,
                score: matches[0].score,
              }
            : null,
          plant_name: plant?.plant_name || null,
        },
      });
    } catch (error) {
      trackEvent({
        screen: currentScreen,
        action: 'identify',
        status: 'error',
        request_data: { image_length: imageBase64.length },
        error_text: error instanceof Error ? error.message : String(error),
      });
      throw error;
    } finally {
      setIsLoading(false);
    }
  }, [currentScreen, trackEvent]);

  const diagnosePlant = useCallback(async (plantId: string, symptom: string) => {
    setIsDiagnosing(true);
    try {
      trackEvent({
        screen: currentScreen,
        action: 'diagnose',
        target: plantId,
        status: 'start',
        request_data: { symptom },
      });
      const result = await api.diagnose(plantId, symptom);
      setDiagnosis(result.problem);
      setDiagnosisMessage(result.message ?? null);
      if (deviceId && result.problem) {
        api.user.addHistory(deviceId, {
          plant_id: plantId,
          symptom,
          result: result.problem as object,
        });
      }
      trackEvent({
        screen: currentScreen,
        action: 'diagnose',
        target: plantId,
        status: 'success',
        request_data: { symptom },
        response_data: {
          has_problem: Boolean(result.problem),
          message: result.message ?? null,
        },
      });
    } finally {
      setIsDiagnosing(false);
    }
  }, [currentScreen, deviceId, trackEvent]);

  const savePlant = useCallback((id: string) => {
    setSavedPlants(prev => {
      const next = [...new Set([...prev, id])];
      AsyncStorage.setItem('savedPlants', JSON.stringify(next)).catch(() => {});
      return next;
    });
    if (deviceId) api.user.savePlant(deviceId, id);
    trackEvent({
      screen: currentScreen,
      action: 'save_plant',
      target: id,
      status: 'success',
      response_data: { saved: true },
    });
  }, [currentScreen, deviceId, trackEvent]);

  const removePlant = useCallback((id: string) => {
    setSavedPlants(prev => {
      const next = prev.filter(p => p !== id);
      AsyncStorage.setItem('savedPlants', JSON.stringify(next)).catch(() => {});
      return next;
    });
    if (deviceId) api.user.removePlant(deviceId, id);
    trackEvent({
      screen: currentScreen,
      action: 'remove_plant',
      target: id,
      status: 'success',
      response_data: { saved: false },
    });
  }, [currentScreen, deviceId, trackEvent]);

  const updateProfile = useCallback((updates: Partial<UserProfile>) => {
    let nextProfile: UserProfile | null = null;
    setProfile(prev => {
      const next = { ...prev, ...updates };
      nextProfile = next;
      AsyncStorage.setItem('profile', JSON.stringify(next)).catch(() => {});
      if (deviceId) {
        api.user.updateProfile(deviceId, {
          name: next.name,
          email: next.email,
          location: next.location,
          bio: next.bio,
          avatar_url: next.avatarUrl,
        });
      }
      return next;
    });
    if (nextProfile) {
      trackEvent({
        screen: currentScreen,
        action: 'update_profile',
        status: 'success',
        request_data: {
          fields: Object.keys(updates),
        },
        response_data: {
          name: nextProfile.name,
          location: nextProfile.location,
        },
      });
    }
  }, [currentScreen, deviceId, trackEvent]);

  const isSaved = useCallback((id: string) => {
    return savedPlants.includes(id);
  }, [savedPlants]);

  const value: AppState = {
    currentScreen,
    navigate,
    goBack,
    searchQuery,
    searchResults,
    isSearching,
    searchError,
    searchPlants,
    currentPlant,
    loadPlantError,
    loadPlant,
    identificationResults,
    identifiedPlant,
    identificationMessage,
    identifyImage,
    diagnosis,
    diagnosisMessage,
    isDiagnosing,
    diagnosePlant,
    savedPlants: savedPlants,
    savePlant,
    removePlant,
    isSaved,
    isLoading,
    profile,
    updateProfile,
    previousScreen,
  };

  return React.createElement(AppContext.Provider, { value }, children);
}

export function useStore(): AppState {
  const context = useContext(AppContext);
  if (!context) {
    throw new Error('useStore must be used within AppProvider');
  }
  return context;
}
