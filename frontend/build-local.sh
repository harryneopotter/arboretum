#!/bin/bash
# Local APK build without EAS cloud
# Uses Expo's prebuild + Gradle

set -e

echo "🌿 Arboretum - Local Android Build"
echo "===================================="

# Check for Android SDK
if [ -z "$ANDROID_SDK_ROOT" ] && [ -z "$ANDROID_HOME" ]; then
    echo "⚠️  Android SDK not found!"
    echo "Please set ANDROID_SDK_ROOT or ANDROID_HOME"
    exit 1
fi

cd "$(dirname "$0")"

echo "📦 Installing dependencies..."
npm install

echo "🔧 Running Expo prebuild..."
npx expo prebuild --platform android --clean

echo "🏗️  Building APK with Gradle..."
cd android
./gradlew assembleRelease

echo "✅ APK built!"
echo ""
echo "📱 Output: android/app/build/outputs/apk/release/app-release.apk"
echo ""
echo "📲 Install with:"
echo "  adb install android/app/build/outputs/apk/release/app-release.apk"
