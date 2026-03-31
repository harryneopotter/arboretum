# Arboretum - Copilot Instructions

## Project Overview
Full-stack plant identification app: **Expo React Native frontend** + **FastAPI backend** backed by **Qdrant cloud** (vector search). The frontend uses a custom Context-based store (no Redux/Zustand) with `AsyncStorage` for local persistence. The backend uses OpenAI embeddings + Qdrant for semantic image and text search.

## Dev Commands

### Backend
```bash
cd backend
python -m venv venv && venv\Scripts\activate   # Windows
pip install -r app/requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```
Health check: `curl http://localhost:8000/health`  
Interactive docs: `http://localhost:8000/docs`

### Frontend
```bash
cd frontend
npm install
npx expo start --web        # Web dev (port 8081)
npx expo start --android    # Android emulator
```
To test a single screen, navigate to it via the store's `navigate()` action.

## Architecture

### Data Flow
```
Frontend (React Native) → api/client.ts → FastAPI (port 8000) → Qdrant Cloud
```
- **Image identification**: base64 image → `/identify` → CLIP embeddings → `plant-images` collection → slug lookup → `/plant/{slug}` for full profile
- **Text search**: query string → `/search` → OpenAI `text-embedding-3-small` (dense) + sparse → `plants` collection
- **Diagnosis**: plant_id + symptom string → `/diagnose` → OpenAI GPT matches against stored `common_problems`

### Frontend State (`store/index.ts`)
Single `AppContext` holds **all** app state: navigation, search results, current plant, identification results, saved plants, user profile, and diagnosis. Every screen consumes it via `useStore()`. There is no separate routing library — `currentScreen` is a string enum, and `navigate(screen)` updates it in `App.tsx`.

### Backend Structure
- `routers/` — thin HTTP layer (request parsing, response shaping)
- `services/` — all Qdrant queries and embedding calls live here; routers must not call Qdrant directly
- `app/config.py` — `get_settings()` (cached) is the single source of config; never import env vars directly

### Qdrant Collections
| Collection | Vector | Content |
|---|---|---|
| `plants` | `plant-vector-dense` (1536d) + `plant-vector-sparse` | Plant text profiles |
| `plant-images` | `image-vector` (512d) | Reference plant images |

Plants are identified by a stable `slug` (e.g., `money_plant`). Image points should carry a `plant_slug` payload linking them back to the `plants` collection.

## Key Conventions

### Frontend
- **No border lines** — separation is done exclusively via background color shifts (`surface_container_low` → `surface_container_lowest`). Never add `1px solid` borders or dividers.
- **Shadows**: `shadowOpacity: 0.06`, `shadowRadius: 32`, `shadowColor: #23472b`. No heavy drop shadows.
- All design tokens (colors, spacing, radius, typography) are defined in `frontend/theme.ts`. Use these tokens, not raw hex values or hardcoded px.
- Screen files live in `frontend/screens/` and are named `*Screen.tsx`. Shared UI components go in `frontend/components.tsx`.
- Typography: uppercase + wide letter-spacing for labels, left-align all long-form text, never center editorial copy.

### Backend
- All Pydantic request/response models are in `app/models.py`. Add new schemas there, not inline in routers.
- `config.py` has hardcoded Qdrant credentials as defaults — these should move to `.env` (tracked in `FULL_FUNCTIONALITY_PLAN.md` as P0). Do not add more hardcoded secrets.
- Python: 4-space indentation. TypeScript/TSX: 2-space indentation.

### API Client (`frontend/api/client.ts`)
- Base URL is `EXPO_PUBLIC_API_URL` env var, falling back to a hardcoded LAN IP (`100.84.92.33:8000`). The LAN IP is intentional — the app is tested on a physical phone on the same network as the dev machine running the backend. To use a different machine or address, set `EXPO_PUBLIC_API_URL`.
- All API functions return safe fallback values (`[]`, `null`, `false`) on error — never throw to the caller.

### Saved Plants & Profile
Currently persisted only in `AsyncStorage` (local to device). The `savedPlants` array stores plant IDs/slugs as strings. Server-side sync is a planned P2 item.

## Manual Verification Checklist
No automated test suite exists. After changes, exercise:
1. `GET /health` returns `"status": "healthy"`
2. Text search returns results
3. Image upload through IdentifyScreen → ResultsScreen → ProfileScreen
4. Save/unsave a plant; verify count on HomeScreen
5. Any screen directly touched by the change
