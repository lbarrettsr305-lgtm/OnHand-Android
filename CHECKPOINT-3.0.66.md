# iCE Onhand Inventory — Recovery Checkpoint 3.0.66

Saved: 2026-09-04
Repository: lbarrettsr305-lgtm/OnHand-Android
Checkpoint branch: checkpoint-3.0.66-2026-09-04
Checkpoint source commit: f4f675111ef88f9f30e36ece21722f5de261bba5

## Current working version
- Version: 3.0.66
- Signed release APK built successfully.
- APK signature verification passed in the canonical GitHub Actions workflow.
- GitHub Actions build run: 33900936004
- Artifact: iCE-Onhand-Inventory-3.0.66-signed
- Artifact ID: 9947634819
- GitHub artifact digest: sha256:cafa155d1f0191dd0ff44e0ee1291de149139ff84cc86a9eb2a27cd267bd1021

## 3.0.66 logo update
The previous app logo was not the intended iCE Inventory branding and appeared dull. Version 3.0.66 installs the newly enhanced saved iCE Inventory logo:
- glossy black background
- brighter neon green and metallic gold treatment
- iCE INVENTORY LLC branding
- runner/scanner/barcode visual
- `SCAN • COUNT • CONTROL` tagline in the source artwork

Android drawable used by the build:
`app/src/main/res/drawable/ice_inventory_logo_3066.webp`

The full enhanced source logo is also saved persistently in the user's ChatGPT Library at:
`/OnHand-Android Checkpoints/iCE-Inventory-Logo-Enhanced-2026-09-04.png`

## Preserved 3.0.65 fix
The Options-screen fix remains intact:
- Unknown Barcode Behavior uses a taller two-line control.
- The selected behavior is visible on a `Current:` line.
- Extra bottom spacer and ScrollView padding allow the final control to scroll above Done.

## Build implementation
`.github/prepare_3066.py` first runs `.github/prepare_3065.py`, preserving all prior working features, then changes only the version and app/launcher logo for 3.0.66.

The canonical workflow is `.github/workflows/build-apk.yml`. It restores the permanent signing key, builds the release APK, verifies the APK signature, and uploads the signed artifact.

## Important preservation rule
Do not redesign or replace unrelated working screens. Continue from this checkpoint and make only specifically requested changes. Preserve scanner, inventory, quantity, multiplication, export/import, Options, passcode, sort, and other working behavior unless explicitly asked to change it.

## Recovery instructions for a future chat
If conversation context is lost, open this repository and read this file first. Use branch `checkpoint-3.0.66-2026-09-04` as the known-good recovery point. Compare any newer `main` state against this checkpoint before making changes.

## Immediate test
Install `iCE-Onhand-Inventory-3.0.66.apk` over the current app. Confirm the enhanced iCE Inventory logo appears as the Android app icon and in the app header, then test the Options screen to confirm the 3.0.65 Unknown Barcode Behavior visibility fix is still working.