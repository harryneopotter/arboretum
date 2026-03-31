# 🌿 Arboretum - Local Development Setup

Complete plant identification app with **React Native frontend + FastAPI backend**.

## 📦 What's Included

- `frontend/` - React Native Expo app
- `backend/` - FastAPI Python server
- `scripts/` - Startup helpers
- **QDrant remains cloud-hosted** (already configured)

## 🚀 Quick Start

### 1. Backend (Terminal 1)
```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r app/requirements.txt
./start-backend.sh        # or: uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Backend runs at: `http://localhost:8000`

### 2. Frontend (Terminal 2)
```bash
cd frontend
npm install
npx expo start --web      # For web testing
# OR
npx expo start --android  # For Android (need Android Studio)
```

Frontend runs at: `http://localhost:8081`

## ⚙️ Configuration

Backend config is in `backend/app/config.py`:
- QDrant URL: Uses your existing cloud instance
- Collections: `plants` and `plant-images` (already populated with 75 plants)

## 📱 Testing the App

1. Open browser to: `http://localhost:8081`
2. Click "Identify Plant" → upload a plant photo
3. The backend identifies it using the cloud QDrant database

## ✅ Prerequisites

- **Node.js 18+** (for frontend)
- **Python 3.10+** (for backend)
- **Android Studio** (optional, for Android builds)

## 🔌 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `http://localhost:8000/health` | GET | Check backend status |
| `http://localhost:8000/identify` | POST | Identify plant from image |
| `http://localhost:8000/search` | POST | Search plants by text |
| `http://localhost:8000/plant/{id}` | GET | Get plant details |

## 🌐 Network Notes

- Frontend → Backend: `localhost:8000` (local network)
- Backend → QDrant: Cloud (already configured)
- No internet needed except for QDrant calls which use your existing cloud instance