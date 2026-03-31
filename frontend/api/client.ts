/**
 * API Client for Arboretum FastAPI Backend
 */

import { Platform } from 'react-native';

const DEFAULT_API_URL =
  Platform.OS === 'android'
    ? 'http://100.84.92.33:8000'
    : 'http://100.84.92.33:8000';

const API_URL = process.env.EXPO_PUBLIC_API_URL || DEFAULT_API_URL;

type Plant = {
  id: string;
  slug?: string;
  plant_name: string;
  category: string;
  description: string;
  image_url?: string;
  care?: {
    watering_frequency?: string;
    light_requirements?: string;
    soil_type?: string;
    temperature_range?: string;
  };
  common_problems?: Array<Record<string, unknown>>;
  alternate_names?: string[];
};

type SearchResult = {
  slug: string;
  plant_name: string;
  score: number;
  category?: string;
  description?: string;
};

type DiagnosisProblem = {
  symptom: string;
  possible_causes: string[];
  fix: string;
  prevention: string;
};

export const api = {
  // Search plants by text
  search: async (query: string, limit: number = 10): Promise<SearchResult[]> => {
    try {
      const response = await fetch(`${API_URL}/search`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query, limit }),
      });
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      return await response.json();
    } catch (error) {
      console.error('Search failed:', error);
      return [];
    }
  },

  // Get plant by ID
  getPlant: async (id: string): Promise<Plant | null> => {
    try {
      const response = await fetch(`${API_URL}/plant/${id}`);
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      return await response.json();
    } catch (error) {
      console.error('Get plant failed:', error);
      return null;
    }
  },

  // Identify plant from image
  identify: async (imageBase64: string): Promise<{ matches: any[], plant: Plant | null }> => {
    try {
      const response = await fetch(`${API_URL}/identify`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ image: imageBase64 }),
      });
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      return await response.json();
    } catch (error) {
      console.error('Identify failed:', error);
      return { matches: [], plant: null };
    }
  },

  // Diagnose plant problems from symptoms
  diagnose: async (plantId: string, symptom: string): Promise<{ problem: DiagnosisProblem | null; message?: string }> => {
    try {
      const response = await fetch(`${API_URL}/diagnose`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ plant_id: plantId, symptom }),
      });
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      return await response.json();
    } catch (error) {
      console.error('Diagnosis failed:', error);
      return { problem: null, message: 'Diagnosis request failed' };
    }
  },

  // Health check
  health: async (): Promise<boolean> => {
    try {
      const response = await fetch(`${API_URL}/health`);
      return response.ok;
    } catch {
      return false;
    }
  },
};
