# Build Guide - Arboretum APK

## ✅ Fixed Issues

| Issue | Fix |
|-------|-----|
| `package.json not exist` | Git repo initialized, all files committed |
| Missing projectId | Added to `app.json` |
| No android.package | Added `com.arboretum.plants` |

---

## 🚀 Option 1: EAS Cloud Build (Recommended)

**Prerequisites:**
- Expo account: [expo.dev/signup](https://expo.dev/signup)

**Commands:**
```bash
cd /home/workspace/plant-app/arboretum

# Login to Expo
npx eas login

# Configure project (one-time)
npx eas project:init

# Build APK
npx eas build --platform android --profile preview
```

**Output:** Download URL via email/CLI (~10-15 min)

---

## 🏠 Option 2: Local Build (No Cloud)

**Prerequisites:**
- Android SDK installed
- JAVA_HOME set
- Android NDK (optional)

**Commands:**
```bash
cd /home/workspace/plant-app/arboretum

# Run build script
./build-local.sh

# Or manual:
npx expo prebuild --platform android
cd android && ./gradlew assembleRelease
```

**Output:** `android/app/build/outputs/apk/release/app-release.apk`

---

## 📱 Option 3: Expo Go (Fastest, No Build)

Run instantly without building APK:

```bash
cd /home/workspace/plant-app/arboretum
npx expo start --android
```

Then scan QR code with Expo Go app.

---

## 🔧 Troubleshooting

| Error | Solution |
|-------|----------|
| "package.json does not exist" | Run `git init && git add -A && git commit -m "init"` |
| "Cannot find module" | Run `npm install` |
| "Gradle not found" | Install Android Studio + SDK |
| "EAS project not configured" | Run `npx eas project:init` |

---

## 📦 Build Profiles

| Profile | Use | Output |
|---------|-----|--------|
| `preview` | Testing | APK |
| `production` | Play Store | AAB |
| `development` | Dev client | APK with Metro |
