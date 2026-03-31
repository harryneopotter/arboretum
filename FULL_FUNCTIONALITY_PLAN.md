# Full Functionality Completion Checklist

This checklist turns Arboretum from a working prototype into a complete app. Items are ordered by dependency: finish P0 before moving on.

## P0 - Core Backend Correctness

### Backend
- [ ] Store `plant_slug` on every image point during ingest.
  - Owner: Backend / data ingest
  - Done when: every `plant-images` point includes a stable slug, `plant_name`, and image metadata.

- [ ] Change `POST /identify` to resolve the plant profile by exact slug.
  - Owner: Backend
  - Done when: the top image match always loads the correct plant profile without a fuzzy text search fallback.

- [ ] Make `IdentifyMatch` schema consistent.
  - Owner: Backend
  - Done when: every identify response includes `slug`, `plant_name`, `score`, and optional `image_url`.

- [ ] Add confidence handling to identification.
  - Owner: Backend
  - Done when: low-confidence results return an explicit “uncertain” state instead of silently forcing a plant.

- [ ] Verify `/search`, `/identify`, `/plant/{id}`, and `/diagnose` return stable JSON.
  - Owner: Backend / QA
  - Done when: all endpoint responses match the frontend expectations and no schema errors appear in normal flows.

### Security / Config
- [ ] Move all secrets to environment variables.
  - Owner: Backend / DevOps
  - Done when: Qdrant URL, Qdrant API key, and OpenAI key are not hardcoded in source.

- [ ] Update `backend/.env.example` to match real runtime needs.
  - Owner: Backend
  - Done when: a new developer can configure the backend from the example file alone.

## P1 - Data Quality And Ingest

### Data
- [ ] Audit the plant dataset for completeness.
  - Owner: Data / Backend
  - Done when: each plant has `plant_name`, `slug`, `alternate_names`, `category`, `description`, `care`, and `common_problems`.

- [ ] Enrich each plant with better reference images.
  - Owner: Data
  - Done when: each plant has multiple reference images from varied angles and lighting.

- [ ] Rebuild the Qdrant collections from clean ingest data.
  - Owner: Backend / DevOps
  - Done when: `plants` and `plant-images` are re-ingested with correct payloads and exact slug mapping.

- [ ] Verify ingest consistency with sample lookups.
  - Owner: QA / Backend
  - Done when: sampled image and text lookups return the intended plant every time.

## P2 - User Persistence

### Profile
- [ ] Add server-side profile persistence.
  - Owner: Backend / Frontend
  - Done when: name, email, location, and bio survive app restarts and device changes.

- [ ] Persist saved plants server-side.
  - Owner: Backend / Frontend
  - Done when: saved plants are synced instead of stored only in `AsyncStorage`.

- [ ] Persist diagnosis history.
  - Owner: Backend / Frontend
  - Done when: prior diagnoses can be reopened and reviewed later.

### Frontend State
- [ ] Replace local-only profile storage with synced profile data.
  - Owner: Frontend
  - Done when: edit/save actions update one source of truth.

- [ ] Replace local-only saved plant count with synced saved-plant state.
  - Owner: Frontend
  - Done when: `My Plants`, Home count, and Settings all read from the same saved source.

## P3 - Product Screens

### Home
- [ ] Replace the hardcoded “Curated Collection” cards.
  - Owner: Frontend
  - Done when: the section is driven by backend recommendations or curated data.

- [ ] Replace the hardcoded “Seasonal Insights” cards.
  - Owner: Frontend
  - Done when: insights are generated from plant data, region, or season logic.

- [ ] Make Home actions reflect real app state.
  - Owner: Frontend
  - Done when: counts, shortcuts, and sections reflect actual saved plants and current profile.

### Settings
- [ ] Turn static Settings rows into working screens or links.
  - Owner: Frontend
  - Done when: Privacy, Terms, Help, Notifications, and About have real destinations.

- [ ] Keep backend health visible in Settings.
  - Owner: Frontend
  - Done when: the app shows live API health and a refresh action.

### Profile And Plant Detail
- [ ] Keep plant details fully data-driven.
  - Owner: Frontend
  - Done when: care, light, humidity, alternate names, and common problems all come from plant payloads.

- [ ] Add a clear save/unsave control to plant profiles.
  - Owner: Frontend
  - Done when: saved state updates instantly and is reflected everywhere.

## P4 - Identification And Diagnosis Quality

### Identify
- [ ] Use top match consensus when the image result is ambiguous.
  - Owner: Backend
  - Done when: the endpoint can choose the best plant from the top 3 results rather than trusting one weak hit.

- [ ] Add a confidence threshold.
  - Owner: Backend
  - Done when: low-score image results are marked uncertain instead of being presented as certain.

- [ ] Improve the profile fetch path for identify.
  - Owner: Backend
  - Done when: the returned profile is the actual plant associated with the image match, not a fuzzy text-search guess.

### Diagnose
- [ ] Require a selected plant for diagnosis.
  - Owner: Frontend / Backend
  - Done when: diagnosis cannot run against an unknown plant context.

- [ ] Return structured diagnosis output.
  - Owner: Backend
  - Done when: causes, fixes, and prevention are clearly separated.

- [ ] Show graceful fallback when diagnosis is inconclusive.
  - Owner: Frontend
  - Done when: the UI explains uncertainty instead of failing silently.

## P5 - Notifications And Reminders

### Reminders
- [ ] Define reminder types.
  - Owner: Product / Frontend
  - Done when: watering, rotation, and fertilizer reminders are clearly specified.

- [ ] Implement local notifications first.
  - Owner: Frontend
  - Done when: reminders work on-device without backend scheduling.

- [ ] Add reminder preferences UI.
  - Owner: Frontend
  - Done when: users can enable, disable, and tune reminder intervals.

## P6 - Device And Build Reliability

### Connectivity
- [ ] Keep API URL configurable.
  - Owner: Frontend
  - Done when: `EXPO_PUBLIC_API_URL` overrides the default for phones, emulators, and local testing.

- [ ] Document the real phone backend URL workflow.
  - Owner: Docs / Frontend
  - Done when: a new tester can install the APK and connect it to the backend without guessing.

### Release
- [ ] Keep `.easignore` aligned with the actual build scope.
  - Owner: Frontend / DevOps
  - Done when: EAS upload size stays small and build artifacts do not include junk directories.

- [ ] Validate APK install and runtime on a physical device.
  - Owner: QA
  - Done when: the installed APK can search, identify, open profiles, save plants, and diagnose successfully.

## P7 - Tests And Verification

### Backend Tests
- [ ] Add endpoint tests for health and main routes.
  - Owner: Backend / QA
  - Done when: `/health`, `/search`, `/identify`, `/plant/{id}`, and `/diagnose` are covered.

- [ ] Add regression tests for exact slug matching.
  - Owner: Backend
  - Done when: identify no longer regresses to fuzzy profile lookup.

### Frontend Tests
- [ ] Add smoke tests for store actions and primary screens.
  - Owner: Frontend
  - Done when: search, save, profile editing, and diagnosis state are validated.

### E2E Checks
- [ ] Verify the main user journey end to end.
  - Owner: QA
  - Done when: a tester can search, identify, open a profile, save it, and run diagnosis without manual fixes.

## Suggested Execution Order

1. Fix exact image-to-profile lookup.
2. Clean up ingest metadata and Qdrant payloads.
3. Move profile and saved plants to server-side persistence.
4. Replace static Home and Settings content.
5. Improve identify confidence and diagnosis output.
6. Add notifications and reminders.
7. Add tests.
8. Validate the APK on a real phone.

## Definition Of Done

- Search returns the right plant.
- Identify returns the right plant profile and a confidence-aware match list.
- Profile, saved plants, and diagnosis history persist across sessions.
- Home and Settings no longer rely on placeholder content for core functionality.
- The APK installs and works on a physical phone against the live backend.
