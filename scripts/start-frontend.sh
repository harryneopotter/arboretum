#!/bin/bash
cd ../frontend
npm install 2>/dev/null || echo "Dependencies already installed"
npx expo start --web
