# iCE Onhand Inventory 3.0.71 Recovery Checkpoint

Date: 2026-09-04

## Known-good release
- Version: 3.0.71
- Main commit: `ee9c7e1e96c2463cebfc2d6b8b3db4a345813cc7`
- Canonical workflow: `.github/workflows/build-apk.yml`
- GitHub Actions run: `33923571110` (run #153)
- Result: SUCCESS
- APK signing key verification: SUCCESS
- APK signature verification: SUCCESS
- Artifact ID: `9955972416`
- Artifact name: `iCE-Onhand-Inventory-3.0.71-signed`
- Artifact digest: `sha256:a645ceb1e9bb71592844a1c61f93ebdad934934a1303b9df4026ec6dff0e7a13`

## 3.0.71 fix
The Samsung soft keyboard was appearing when entering the Cases/Add Quantity screen and covering the lower calculator controls.

The 3.0.71 prep script `.github/prepare_3071.py` preserves 3.0.70 and then:
- keeps the Android/Samsung soft keyboard hidden when QuantityActivity opens or resumes;
- hides it again when Quantity per Unit or Number of Cases receives focus;
- keeps `setShowSoftInputOnFocus(false)` on both fields;
- sets QuantityActivity `windowSoftInputMode="stateAlwaysHidden|adjustResize"`;
- preserves the app's custom calculator keypad and existing case multiplication flow, including `10 × 20 = 200` and returning the result to Count.

## Preservation rule
Do not redesign or replace unrelated working screens. Preserve the verified glossy iCE Inventory LLC scanner-figure logo, Bluetooth/scanner behavior, count logic, Cases multiplication, Internet Items With Pictures export, Options, Sort, passcode, import/export, locations and all other working features unless the user specifically asks to change them.

## Logo reference
Continue using the verified glossy green/gold scanner-figure iCE Inventory LLC logo from the 3.0.70 preparation chain. Do not replace it with the old circular logo.

## Recovery instructions
If a future chat needs to resume this project, read this checkpoint first, inspect the current `main`, compare any newer work to this known-good release, and continue from the latest confirmed working state without asking the user to re-explain the project.
