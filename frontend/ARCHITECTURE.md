# Arboretum Plant Care App - Architecture Document

## 1. Overview & Creative North Star: "The Digital Arboretum"

**App Name:** The Arboretum
**Platform:** React Native (Expo) - Android
**Design Philosophy:** A high-end editorial experience that feels like flipping through a premium gardening journal.

**Creative Direction:**
- Intentional asymmetry and tonal depth
- Overlapping botanical imagery with floating typography  
- Nested surfaces without rigid grids
- Quiet, sophisticated gallery for organic life

---

## 2. Color & Surface Architecture (Tonal Layering)

### Core Palette

| Token | Hex | Usage |
|-------|-----|-------|
| `primary` | #23472b | CTAs, active states |
| `primary_container` | #3a5f41 | Branding, labels, icons |
| `tertiary_fixed` | #b9f0ba | Success states, badges |
| `surface` | #f8faf6 | Screen backgrounds |
| `surface_container_lowest` | #ffffff | Cards, elevated surfaces |
| `surface_container_low` | #f2f4f0 | Secondary sections |
| `surface_container_high` | #e8ece6 | Section backgrounds |
| `on_surface` | #191c1a | Text (never pure black) |
| `outline_variant` | rgba(25,28,26,0.15) | Ghost borders |

### The "No-Line" Rule
**CRITICAL:** No 1px solid borders. Use background color shifts and white space only.

---

## 3. Typography: Editorial Authority

| Level | Size | Weight | Usage |
|-------|------|--------|-------|
| **Display** | 56px | Bold | Botanical Names |
| **Headline** | 32px | Semibold | Section intros |
| **Title** | 22px | Medium | Card headers |
| **Body** | 16px | Regular | Care instructions |
| **Label** | 12px | Bold | Scientific names |

**Rules:** Uppercase labels, wide tracking (4%), left-aligned only.

---

## 4. Spacing & Radius

### Spacing
xs: 4px, sm: 8px, md: 12px, base: 16px, lg: 24px, xl: 32px, 2xl: 48px, 3xl: 80px

### Border Radius
- sm: 8px (icons)
- base: 16px (inputs)
- lg: 24px (cards)
- xl: 32px (large cards)
- 2xl: 48px (hero containers)

---

## 5. Elevation & Depth

**NO traditional drop shadows.** Use Ambient Depth:

Layer `surface_container_lowest` (#ffffff) on `surface_container_low` (#f2f4f0).

**Ambient Shadow Style:**
- shadowOpacity: 0.06
- shadowRadius: 32
- shadowColor: #23472b

---

## 6. Component Primitives

### Buttons ("Leaf" Interaction)
| Variant | Background | Text | Radius |
|---------|------------|------|--------|
| Primary | primary | white | lg (24px) |
| Secondary | surface_container_high | on_surface | lg |
| Outline | transparent | on_surface | lg + ghost border |

**States:** On press, shift to `primary_container`.

### Cards
- Background: `surface_container_lowest`
- Padding: 24px (`spacing-6`)
- **NO internal divider lines**
- Border radius: `lg` (24px)

### Inputs
- Background: `surface_container_low`
- Ghost border: 15% opacity
- Focus: 100% primary at 2px

### Labels
- Style: uppercase, bold, wide tracking
- Color: `primary_container`

---

## 7. Screen Inventory

### IMPLEMENTED (11 screens)

| Screen | Purpose | Entry Point | Key Features | Status |
|--------|---------|-------------|--------------|--------|
| **OnboardingScreen** | First-time welcome | App launch | Swipable slides, Get Started CTA | ✅ IMPLEMENTED |
| **HomeScreen** | Dashboard, discovery | Launch | Search bar, Identify/Diagnose cards, Curated scroll, Seasonal insight, "View All" → MyPlants | ✅ IMPLEMENTED |
| **SearchResultsScreen** | Display search results | Home search | Vertical list of AmbientCards, plant info | ✅ IMPLEMENTED |
| **MyPlantsScreen** | User plant collection | Home "View All" | Plant list, water reminders, add button | ✅ IMPLEMENTED |
| **IdentifyScreen** | Camera/photo upload | Home Identify | Upload container, tap-to-scan, AI info | ✅ IMPLEMENTED |
| **ResultsScreen** | Display ID matches | Identify scan | Best match (98%), secondary matches, retake | ✅ IMPLEMENTED |
| **ProfileScreen** | Plant care summary | Results View | Hero image, care cards, origin, "Full Care Guide" button | ✅ IMPLEMENTED |
| **FullCareGuideScreen** | Extended care details | Profile | 5 care sections, troubleshooting, pro tips | ✅ IMPLEMENTED |
| **DiagnosisScreen** | Symptom diagnosis | Home Diagnose | Symptom input, backend diagnosis result, fallback guidance | ✅ IMPLEMENTED |
| **SettingsScreen** | User preferences | Bottom nav | Profile card (tappable), preferences, about | ✅ IMPLEMENTED |
| **EditProfileScreen** | Edit user profile | Settings Profile | Avatar, form fields, save/cancel | ✅ IMPLEMENTED |

---

## 8. Missing Screens Analysis

### ALL REQUIRED SCREENS COMPLETED ✅

All critical screens for MVP have been implemented. The app now has a complete user flow:

1. **Onboarding** → teaches users about app features
2. **Home** → main discovery hub
3. **Search** → find plants by name/type
4. **My Plants** → personal collection tracker
5. **Identify** → camera-based identification
6. **Results** → match display
7. **Profile** → care summary
8. **Full Care Guide** → extended details
9. **Settings** → preferences
10. **Edit Profile** → user info management
11. **Diagnosis** → API-backed symptom analysis

---

## 9. Navigation Structure

### Bottom Tab Bar
```
[ HOME ]  [ IDENTIFY ]  [ DIAGNOSIS ]  [ SETTINGS ]
   🏠         📷            🌿             ⚙️
```

**Smart Highlight Rule:** When user is on RESULTS or PROFILE, the IDENTIFY tab remains highlighted.

### Stack Navigation
- Home Stack: Home → SearchResults → Profile
- Identify Stack: Home → Identify → Results → Profile
- Diagnosis Stack: Home → Diagnosis → ProblemDetail (future)
- Settings Stack: Settings → EditProfile → Notifications → PrivacyPolicy

---

## 10. Screen Generation Template

When requesting a new screen, provide:

1. **Screen name** (e.g., "SearchResultsScreen")
2. **Purpose** - What user does here
3. **Entry point** - How user arrives
4. **Key elements**:
   - Header text (display-lg or headline-lg)
   - Primary actions (Button variants)
   - Data display (cards, lists)
   - Background surfaces needed
5. **Navigation options** (back, next, tabs)
6. **Specific design notes**

### Example Request:
```
"Create SearchResultsScreen:
- Entry from Home > Search submit
- Header: Headline 'Search Results' + search input in surface_container_low
- List: Vertical scroll of PlantCards (surface_container_lowest, lg radius)
- Tap card → Profile. Back → Home.
- Use AmbientCard for each result with plant image, scientific name label, category."
```

---

## 11. API Integration Points

From your FastAPI backend (con_pFL0ToqgSlwYoFcE):

| Endpoint | Screen | Purpose |
|----------|--------|---------|
| POST /identify | IdentifyScreen | Upload image, get plant matches |
| GET /plant/{id} | ProfileScreen | Fetch full care details |
| GET /search?q= | SearchResultsScreen | Text search plants |
| POST /diagnose | ProblemDetailScreen | Identify plant problems |

---

## 12. Critical Design Rules Summary

**DO:**
- Use background color shifts, not borders
- Apply generous spacing (add `spacing-12` if unsure)
- Use high-quality, desaturated botanical photography
- Left-align all text (never center long-form)
- Use Inter font with editorial hierarchy

**DON'T:**
- Use 1px dividers or hairlines
- Use pure black (#000000) for text
- Use generic Material icons (use Lucide Light stroke)
- Center-align long-form editorial content

---

**Document version:** 1.0  
**Last updated:** For Arboretum React Native build
