import React, { createContext, useContext, useState, useCallback, useEffect } from 'react';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { api } from '../api/client';

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
}

const AppContext = createContext<AppState | undefined>(undefined);

export function AppProvider({ children }: { children: React.ReactNode }) {
  const [currentScreen, setCurrentScreen] = useState<Screen>('ONBOARDING');
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
  const [profile, setProfile] = useState<UserProfile>({
    name: 'Jane Doe',
    email: 'jane.doe@arboretum.app',
    location: 'New Delhi, India',
    bio: 'Plant enthusiast and urban gardener',
  });

  // Load saved plants from storage on mount
  useEffect(() => {
    const loadSaved = async () => {
      try {
        const saved = await AsyncStorage.getItem('savedPlants');
        if (saved) {
          setSavedPlants(JSON.parse(saved));
        }
        const storedProfile = await AsyncStorage.getItem('profile');
        if (storedProfile) {
          setProfile(JSON.parse(storedProfile));
        }
      } catch (e) {
        console.error('Failed to load saved plants:', e);
      }
    };
    loadSaved();
  }, []);

  // Save plants when changed
  useEffect(() => {
    AsyncStorage.setItem('savedPlants', JSON.stringify(savedPlants)).catch(e =>
      console.error('Failed to save plants:', e)
    );
  }, [savedPlants]);

  useEffect(() => {
    AsyncStorage.setItem('profile', JSON.stringify(profile)).catch(e =>
      console.error('Failed to save profile:', e)
    );
  }, [profile]);

  const navigate = useCallback((screen: Screen) => {
    setCurrentScreen(screen);
  }, []);

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
    } finally {
      setIsDiagnosing(false);
    }
  }, []);

  const savePlant = useCallback((id: string) => {
    setSavedPlants(prev => [...new Set([...prev, id])]);
  }, []);

  const removePlant = useCallback((id: string) => {
    setSavedPlants(prev => prev.filter(p => p !== id));
  }, []);

  const updateProfile = useCallback((updates: Partial<UserProfile>) => {
    setProfile(prev => ({ ...prev, ...updates }));
  }, []);

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
