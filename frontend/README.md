# The Arboretum

A React Native (Expo) Android app for plant identification and care.

## Features

- **Plant Identification** - Snap a photo to identify any plant
- **Search & Browse** - Search the botanical database
- **My Plants Collection** - Track your personal plant collection
- **Care Guides** - Detailed care instructions for each plant
- **Problem Diagnosis** - Identify plant health issues using the backend diagnosis flow
- **Beta Telemetry** - Logs core beta/dev actions and response summaries for admin review

## Screens (11 Total)

1. **OnboardingScreen** - First-time welcome with swipable slides
2. **HomeScreen** - Dashboard with search, identify, curated collection
3. **SearchResultsScreen** - Filtered plant search results
4. **MyPlantsScreen** - User's saved plants with watering reminders
5. **IdentifyScreen** - Camera/photo upload for identification
6. **ResultsScreen** - Display identification matches with confidence scores
7. **ProfileScreen** - Plant details with care summary
8. **FullCareGuideScreen** - Extended care details and troubleshooting
9. **DiagnosisScreen** - Problem diagnosis backed by backend data
10. **SettingsScreen** - User preferences and app info
11. **EditProfileScreen** - Edit user profile information

## Project Structure

```
arboretum/
├── screens/
│   ├── HomeScreen.tsx
│   ├── SearchResultsScreen.tsx
│   ├── MyPlantsScreen.tsx
│   ├── IdentifyScreen.tsx
│   ├── ResultsScreen.tsx
│   ├── ProfileScreen.tsx
│   ├── FullCareGuideScreen.tsx
│   ├── DiagnosisScreen.tsx
│   ├── SettingsScreen.tsx
│   ├── EditProfileScreen.tsx
│   └── OnboardingScreen.tsx
├── components.tsx          # Reusable UI components
├── theme.ts                # Colors, spacing, design tokens
├── App.tsx                 # Main app with navigation
└── index.js                # Entry point
```

## Design System

### Philosophy: "The Digital Arboretum"
- Editorial, premium feel (like a gardening journal)
- Intentional asymmetry and tonal depth
- NO 1px borders - use background color shifts only
- Tonal layering: #ffffff on #f2f4f0 on #f8faf6

### Colors
- **Primary**: #23472b (Forest green)
- **Surface**: #f8faf6 (Off-white backgrounds)
- **Text**: #191c1a (Never pure black)
- **Accent**: #b9f0ba (Pale green)

### Typography
- **Font**: Inter
- **Labels**: 12px, uppercase, wide tracking
- **Display**: 56px for botanical names
- **Always left-aligned** (never center)

### Shadows
- Ambient shadow: 32px radius, 6% opacity
- No traditional drop shadows

## How to Run

```bash
# Install dependencies
npm install

# Start Expo development server
npm start
# or
expo start

# Run on Android
npm run android

# Run on iOS (requires macOS)
npm run ios
```

## Navigation Flow

```
ONBOARDING → HOME (first launch)
          ↓
        ┌─────────────┬──────────────┬──────────────┐
        ↓             ↓              ↓              ↓
   SEARCH_RESULTS  IDENTIFY      DIAGNOSIS      SETTINGS
        ↑             ↓              │              ↓
   PROFILE ← RESULTS                │         EDIT_PROFILE
        ↑                            │              ↑
   FULL_CARE ←──────────────────────┘          (back)
        ↑
   MY_PLANTS
```

## Dependencies

- React Native (Expo)
- Lucide React Native (icons)
- React Native Safe Area Context
- Expo Camera & Image Picker

## Status: Beta Hardening In Progress

Core screens are implemented and backend-connected, with active hardening for reliability and UX integrity. Current build includes:
- Search, identify, profile, and diagnosis flows backed by FastAPI/Qdrant
- Saved plants and profile sync by device ID
- Beta/dev telemetry for core actions
- Explicit error states for search/profile loading failures
- Candidate selection in identify results when top confidence is low

## Next Steps

1. Redeploy backend and verify Cloud Run latency/timeout behavior on real device traffic
2. Install and test the APK on a physical Android device
3. Complete broad UI regression pass so every visible control has intended behavior
4. Add automated tests and release checks

## Local API URL

- Web/PC and Android defaults to `https://arboretum-backend-1088270338886.us-central1.run.app`
- Override with `EXPO_PUBLIC_API_URL` if your backend runs elsewhere
- Set `EXPO_PUBLIC_BETA_LOGGING=false` only if you want to disable telemetry locally

---

Built with the [Architectural Document](ARCHITECTURE.md) design system.
