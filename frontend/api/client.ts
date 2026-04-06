/**
 * API Client for Arboretum FastAPI Backend
 */

const DEFAULT_API_URL = 'https://arboretum-backend-1088270338886.us-central1.run.app';

export const API_URL = process.env.EXPO_PUBLIC_API_URL || DEFAULT_API_URL;
const BETA_LOGGING_ENABLED = process.env.EXPO_PUBLIC_BETA_LOGGING !== 'false';

export type ApiErrorCode = 'HTTP' | 'NETWORK' | 'TIMEOUT';

export class ApiError extends Error {
  code: ApiErrorCode;
  status?: number;

  constructor(message: string, code: ApiErrorCode, status?: number) {
    super(message);
    this.name = 'ApiError';
    this.code = code;
    this.status = status;
  }
}

function parseErrorMessage(text: string, status: number): string {
  if (!text) return `Request failed with status ${status}`;
  try {
    const parsed = JSON.parse(text) as { detail?: string };
    return parsed.detail || text;
  } catch {
    return text;
  }
}

async function fetchJson<T>(
  path: string,
  init: RequestInit = {},
  timeoutMs: number = 30000,
): Promise<T> {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), timeoutMs);

  try {
    const response = await fetch(`${API_URL}${path}`, {
      ...init,
      signal: controller.signal,
    });

    if (!response.ok) {
      const text = await response.text().catch(() => '');
      throw new ApiError(
        parseErrorMessage(text, response.status),
        'HTTP',
        response.status,
      );
    }

    return await response.json();
  } catch (error) {
    if (error instanceof ApiError) {
      throw error;
    }
    if (error instanceof DOMException && error.name === 'AbortError') {
      throw new ApiError('Request timed out. Please try again.', 'TIMEOUT');
    }
    throw new ApiError('Network request failed. Check your connection.', 'NETWORK');
  } finally {
    clearTimeout(timer);
  }
}

type Plant = {
  id: string;
  slug?: string;
  plant_name: string;
  category: string;
  description: string;
  image_url?: string;
  reference_images?: Array<{
    url?: string;
    image_url?: string;
    path?: string;
  }>;
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

type UserProfile = {
  name: string;
  email: string;
  location: string;
  bio: string;
  avatar_url?: string;
};

export type TelemetryEvent = {
  device_id?: string;
  session_id?: string;
  screen?: string;
  action: string;
  target?: string;
  status?: string;
  source?: string;
  request_data?: Record<string, unknown>;
  response_data?: Record<string, unknown>;
  error_text?: string;
};

export const api = {
  telemetry: {
    logEvent: async (event: TelemetryEvent): Promise<void> => {
      if (!BETA_LOGGING_ENABLED) return;
      try {
        await fetchJson('/events', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            ...event,
            source: event.source || 'frontend',
          }),
        }, 10000);
      } catch {
        // Beta telemetry must never block the user flow.
      }
    },
    listEvents: async (adminToken: string, limit: number = 100): Promise<any[]> => {
      try {
        return await fetchJson<any[]>(`/events/admin?limit=${encodeURIComponent(limit)}`, {
          headers: { 'X-Admin-Token': adminToken },
        }, 15000);
      } catch {
        return [];
      }
    },
  },

  // User: profile
  user: {
    getProfile: async (deviceId: string): Promise<UserProfile | null> => {
      try {
        return await fetchJson<UserProfile | null>(`/user/${deviceId}/profile`, {}, 15000);
      } catch { return null; }
    },
    updateProfile: async (deviceId: string, profile: Partial<UserProfile>): Promise<void> => {
      try {
        await fetchJson(`/user/${deviceId}/profile`, {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(profile),
        }, 15000);
      } catch { /* offline – local already updated */ }
    },
    getSaved: async (deviceId: string): Promise<string[]> => {
      try {
        return await fetchJson<string[]>(`/user/${deviceId}/saved`, {}, 15000);
      } catch { return []; }
    },
    savePlant: async (deviceId: string, plantId: string): Promise<void> => {
      try {
        await fetchJson(`/user/${deviceId}/saved/${encodeURIComponent(plantId)}`, { method: 'POST' }, 15000);
      } catch { /* offline – local already updated */ }
    },
    removePlant: async (deviceId: string, plantId: string): Promise<void> => {
      try {
        await fetchJson(`/user/${deviceId}/saved/${encodeURIComponent(plantId)}`, { method: 'DELETE' }, 15000);
      } catch { /* offline – local already updated */ }
    },
    addHistory: async (deviceId: string, entry: { plant_id?: string; plant_name?: string; symptom: string; result?: object }): Promise<void> => {
      try {
        await fetchJson(`/user/${deviceId}/history`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(entry),
        }, 15000);
      } catch { /* offline */ }
    },
  },

  // Search plants by text
  search: async (query: string, limit: number = 10): Promise<SearchResult[]> => {
    return await fetchJson<SearchResult[]>('/search', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query, limit }),
    }, 15000);
  },

  // Get plant by ID
  getPlant: async (id: string): Promise<Plant | null> => {
    return await fetchJson<Plant | null>(`/plant/${encodeURIComponent(id)}`, {}, 15000);
  },

  // Identify plant from image
  identify: async (imageBase64: string): Promise<{ matches: any[], plant: Plant | null; message?: string }> => {
    return await fetchJson<{ matches: any[], plant: Plant | null; message?: string }>('/identify', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ image: imageBase64 }),
    }, 45000);
  },

  // Diagnose plant problems from symptoms
  diagnose: async (plantId: string, symptom: string): Promise<{ problem: DiagnosisProblem | null; message?: string }> => {
    try {
      return await fetchJson<{ problem: DiagnosisProblem | null; message?: string }>('/diagnose', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ plant_id: plantId, symptom }),
      }, 20000);
    } catch (error) {
      console.error('Diagnosis failed:', error);
      return { problem: null, message: 'Diagnosis request failed' };
    }
  },

  // Health check
  health: async (): Promise<boolean> => {
    try {
      await fetchJson('/health', {}, 10000);
      return true;
    } catch {
      return false;
    }
  },
};
