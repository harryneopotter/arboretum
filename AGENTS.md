# Repository Guidelines

## Project Structure & Module Organization
- `frontend/` contains the Expo React Native app. `App.tsx` wires navigation, `screens/` holds feature screens, `api/` wraps backend calls, `theme.ts` centralizes design tokens, and `assets/` stores images/icons.
- `backend/` contains the FastAPI service. The app lives in `backend/app/`, with `routers/` for HTTP endpoints, `services/` for embedding and Qdrant logic, and `utils/` for shared helpers.
- `scripts/` contains local startup helpers for running both halves of the stack.

## Build, Test, and Development Commands
- Frontend install and start: `cd frontend && npm install && npm start`
- Web preview: `cd frontend && npm run web`
- Android or iOS dev launch: `cd frontend && npm run android` or `npm run ios`
- Backend setup and run: `cd backend && python -m venv venv && venv\Scripts\activate && pip install -r app/requirements.txt && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000`
- Health check: `curl http://localhost:8000/health`

## Coding Style & Naming Conventions
- Use the existing style in each language: 2-space indentation for TypeScript/TSX and 4-space indentation for Python.
- Name React Native screens as `*Screen.tsx` and keep shared UI in reusable modules such as `components.tsx`.
- Keep backend responsibilities separated: routers handle request/response flow, services handle data access and model logic.
- No formatter or linter is configured in the repo, so match surrounding code closely.

## Testing Guidelines
- There is no formal unit test suite checked in. Validate changes by running both apps, opening the Expo web preview, and exercising the backend endpoints.
- Minimum manual checks: `/health`, plant search, image identification, and any screen touched by the change.
- If you add tests, place them near the feature area and use clear names such as `*.test.tsx` or `test_*.py`.

## Commit & Pull Request Guidelines
- No Git history is available in this checkout, so use short imperative commits or Conventional Commit style, for example `fix: handle empty search results`.
- PRs should explain what changed, how to run it locally, and what was verified manually.
- Include screenshots or screen recordings for UI changes and mention any backend configuration updates.

## Security & Configuration Tips
- Backend configuration lives in `backend/app/config.py`; Qdrant is cloud-hosted and already expected by the app.
- Do not commit secrets, generated logs, or local environment files.
