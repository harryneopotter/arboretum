# Arboretum App - Status Summary

## ✅ Complete (Wired to Backend)

| Screen | API Connection | Data Flow |
|--------|----------------|-----------|
| **HomeScreen** | ✅ useStore | Search input → API → SearchResultsScreen |
| **SearchResultsScreen** | ✅ useStore | Displays live search results from Qdrant |
| **ProfileScreen** | ✅ useStore | Shows `currentPlant` data with save/unsave |

## ⚠️ Partially Wired (Needs Backend Enhancement)

| Screen | Missing | Current State |
|--------|---------|---------------|
| **IdentifyScreen** | Image upload | Needs camera → base64 → /identify endpoint |
| **ResultsScreen** | API results | Mock data (needs identifyImage response) |
| **MyPlantsScreen** | Saved plants persist | In-memory only (needs AsyncStorage) |

## 📱 UI Complete (Static Screens)

| Screen | Features |
|--------|----------|
| **OnboardingScreen** | 3-slide intro, Get Started CTA |
| **DiagnosisScreen** | Placeholder (Coming Soon) |
| **EditProfileScreen** | Form fields (not persisted) |
| **FullCareGuideScreen** | Extended plant details (static data) |
| **SettingsScreen** | Profile, preferences, about lists |

## 🔧 Architecture

```
Frontend (React Native/Expo)
├── App.tsx - Main with navigation state
├── store/index.ts - Global state (React Context)
│   ├── searchPlants(query) → calls api.search()
│   ├── loadPlant(id) → calls api.getPlant()
│   ├── identifyImage(img) → calls api.identify()
│   └── savedPlants[] + savePlant()/removePlant()
│
├── api/client.ts - HTTP client to FastAPI
│   └── API_URL defaults to localhost on web/PC and 10.0.2.2 on Android
│
└── screens/*.tsx - All 11 screens

Backend (FastAPI + Qdrant)
├── /search - Hybrid dense + sparse search
├── /identify - CLIP embedding + image search
├── /plant/{id} - Full plant profile
└── /health - Status check
```

## 🚀 Next Steps

1. **Start the Backend**
   ```bash
   cd /home/.z/workspaces/con_pFL0ToqgSlwYoFcE
   uvicorn app.main:app --host 0.0.0.0 --port 8000
   ```

2. **Run the App**
   ```bash
   cd /home/workspace/plant-app/arboretum
   npx expo start --android
   ```

3. **Complete Wiring**
   - Wire IdentifyScreen to `identifyImage(imageBase64)`
   - Wire ResultsScreen to use `identificationResults`
   - Add AsyncStorage for persisted saved plants

## 📊 Design Document

See `ARCHITECTURE.md` for complete design system:
- Tonal layering (#f8faf6 > #f2f4f0 > #ffffff)
- "No-line" rule (no borders)
- Typography: Inter, Editorial hierarchy
- Spacing: 4px base unit

## 🎯 Flow Completion

```
ONBOARDING → HOME ──┬── Search → SearchResults → Profile → FullCareGuide
                    ├── Identify → [CAMERA] → Results → Profile
                    ├── MyPlants (collection)
                    ├── Diagnosis (WIP)
                    └── Settings → EditProfile
```

All navigation flows implemented, 3 screens fully wired to backend.
