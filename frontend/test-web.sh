#!/bin/bash
# Web preview script

echo "🌿 Starting Arboretum Web Preview..."
echo 

# Check if backend is running
if ! curl -s http://localhost:8000/health > /dev/null; then
  echo "⚠️  Backend not running. Starting it..."
  cd /home/.z/workspaces/con_pFL0ToqgSlwYoFcE && source venv/bin/activate && uvicorn app.main:app --host 0.0.0.0 --port 8000 &
  sleep 3
fi

echo "✅ Backend: http://localhost:8000"
echo "🚀 Starting web preview..."
echo ""

cd /home/workspace/plant-app/arboretum
npx expo start --web
