import React, { createContext, useContext, useState, useCallback, useEffect } from 'react';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { api } from '../api/client';

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
  
  // Search
  searchQuery: string;
  searchResults: SearchResult[];
  isSearching: boolean;
  searchPlants: (query: string) => Promise<void>;
  
  // Plant details
  currentPlant: Plant | null;
  loadPlant: (id: string) => Promise<void>;
  
  // Identification
  identificationResults: any[];
  identifiedPlant: Plant | null;
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
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState<SearchResult[]>([]);
  const [isSearching, setIsSearching] = useState(false);
  const [currentPlant, setCurrentPlant] = useState<Plant | null>(null);
  const [identificationResults, setIdentificationResults] = useState<any[]>([]);
  const [identifiedPlant, setIdentifiedPlant] = useState<Plant | null>(null);
  const [diagnosis, setDiagnosis] = useState<DiagnosisProblem | null>(null);
  const [diagnosisMessage, setDiagnosisMessage] = useState<string | null>(null);
  const [isDiagnosing, setIsDiagnosing] = useState(false);
  const [savedPlants, setSavedPlants] = useState<string[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [deviceId, setDeviceId] = useState<string | null>(null);
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
      if (savedRaw) setSavedPlants(JSON.parse(savedRaw));
      if (profileRaw) setProfile(prev => ({ ...prev, ...JSON.parse(profileRaw) }));

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
        if (serverSaved && serverSaved.length > 0) {
          setSavedPlants(serverSaved);
          AsyncStorage.setItem('savedPlants', JSON.stringify(serverSaved)).catch(() => {});
        }
      } catch {
        // Backend offline — local data already shown
      }
    };
    init();
  }, []);

  const navigate = useCallback((screen: Screen) => {
    setPreviousScreen(prev => (screen !== prev ? (currentScreen as Screen) : prev));
    setCurrentScreen(screen);
  }, [currentScreen]);

  const searchPlants = useCallback(async (query: string) => {
    setSearchQuery(query);
    setIsSearching(true);
    try {
      const results = await api.search(query, 10);
      setSearchResults(results);
    } finally {
      setIsSearching(false);
    }
  }, []);

  const loadPlant = useCallback(async (id: string) => {
    setIsLoading(true);
    try {
      const plant = await api.getPlant(id);
      setCurrentPlant(plant);
    } finally {
      setIsLoading(false);
    }
  }, []);

  const identifyImage = useCallback(async (imageBase64: string) => {
    setIsLoading(true);
    try {
      const { matches, plant } = await api.identify(imageBase64);
      setIdentificationResults(matches);
      setIdentifiedPlant(plant);
      setCurrentPlant(plant);
    } finally {
      setIsLoading(false);
    }
  }, []);

  const diagnosePlant = useCallback(async (plantId: string, symptom: string) => {
    setIsDiagnosing(true);
    try {
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
    } finally {
      setIsDiagnosing(false);
    }
  }, [deviceId]);

  const savePlant = useCallback((id: string) => {
    setSavedPlants(prev => {
      const next = [...new Set([...prev, id])];
      AsyncStorage.setItem('savedPlants', JSON.stringify(next)).catch(() => {});
      return next;
    });
    if (deviceId) api.user.savePlant(deviceId, id);
  }, [deviceId]);

  const removePlant = useCallback((id: string) => {
    setSavedPlants(prev => {
      const next = prev.filter(p => p !== id);
      AsyncStorage.setItem('savedPlants', JSON.stringify(next)).catch(() => {});
      return next;
    });
    if (deviceId) api.user.removePlant(deviceId, id);
  }, [deviceId]);

  const updateProfile = useCallback((updates: Partial<UserProfile>) => {
    setProfile(prev => {
      const next = { ...prev, ...updates };
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
  }, [deviceId]);

  const isSaved = useCallback((id: string) => {
    return savedPlants.includes(id);
  }, [savedPlants]);

  const value: AppState = {
    currentScreen,
    navigate,
    searchQuery,
    searchResults,
    isSearching,
    searchPlants,
    currentPlant,
    loadPlant,
    identificationResults,
    identifiedPlant,
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
