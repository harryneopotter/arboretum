# Arboretum App Status

## Current State

The app is in beta-hardening mode. Core screens and backend wiring are in place, but release readiness depends on runtime stability and full UX behavior validation on a physical Android device.

## Implemented Flows

- Onboarding -> Home
- Search -> Search Results -> Profile -> Full Care Guide
- Identify -> Results -> Profile
- Save/unsave plants -> My Plants
- Profile edit -> local + backend profile sync
- Diagnosis flow with backend response rendering
- Beta telemetry posting for core actions

## Hardening Work Completed

- Search/identify/profile client now surfaces real request errors instead of silently converting failures to empty data.
- Results screen supports selecting secondary identify candidates.
- Home diagnosis shortcut now guides users to select/identify a plant first.
- My Plants now shows unavailable saved items and supports retry loading.
- Hardware back handling uses app-level history instead of always forcing Home.
- Backend telemetry routes enforce enable flag and admin-token protection.
- Backend hot-path Qdrant and embedding HTTP calls use async clients.

## Still Required Before Broad Beta

- Cloud Run smoke validation under real device traffic (search/identify/diagnose latency).
- End-to-end UI pass to confirm every visible control has intentional behavior.
- Final copy review for product claims vs actual model/data capability.
- APK regression pass after backend redeploy.

## Validation Commands

- `cd frontend && npx tsc --noEmit`
- `python -m compileall backend\\app -q`
