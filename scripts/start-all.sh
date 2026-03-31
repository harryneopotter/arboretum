#!/bin/bash
# Start both frontend and backend

echo "🌿 Starting Arboretum Full Stack..."

# Start backend
echo "🚀 Starting FastAPI Backend..."
cd ../backend
source venv/bin/activate 2>/dev/null || python3 -m venv venv && source venv/bin/activate && pip install -r app/requirements.txt
echo "✅ Backend ready at http://localhost:8000"
