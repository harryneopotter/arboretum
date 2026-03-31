# The Arboretum

A React Native (Expo) Android app for plant identification and care.

## Features

- **Plant Identification** - Snap a photo to identify any plant
- **Search & Browse** - Search the botanical database
- **My Plants Collection** - Track your personal plant collection
- **Care Guides** - Detailed care instructions for each plant
- **Problem Diagnosis** - Identify plant health issues (coming soon)

## Screens (11 Total)

1. **OnboardingScreen** - First-time welcome with swipable slides
2. **HomeScreen** - Dashboard with search, identify, curated collection
3. **SearchResultsScreen** - Filtered plant search results
4. **MyPlantsScreen** - User's saved plants with watering reminders
5. **IdentifyScreen** - Camera/photo upload for identification
6. **ResultsScreen** - Display identification matches with confidence scores
7. **ProfileScreen** - Plant details with care summary
8. **FullCareGuideScreen** - Extended care details and troubleshooting
9. **DiagnosisScreen** - Problem identification placeholder
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

## Status: Ready for Testing

All screens implemented and fully navigable. The app includes:
- Bottom tab navigation with smart highlight rules
- Mock data for search results and plant profiles
- Full onboarding flow
- Working search → results → profile → care guide flow

## Next Steps

1. Connect to your FastAPI backend (`con_pFL0ToqgSlwYoFcE`)
2. Integrate Qdrant for image/text search
3. Add real camera functionality (currently mock)
4. Persist user plants to storage

## Local API URL

- Web/PC and Android defaults to `http://100.84.92.33:8000`
- Override with `EXPO_PUBLIC_API_URL` if your backend runs elsewhere

---

Built with the [Architectural Document](ARCHITECTURE.md) design system.
