# iCE Onhand Inventory — Recovery Checkpoint 3.0.65

Saved: 2026-09-04
Repository: lbarrettsr305-lgtm/OnHand-Android
Checkpoint branch: checkpoint-3.0.65-2026-09-04
Checkpoint source commit: 38c4fec3ab9d557ad925e4362628752584afdba0

## Current working version
- Version: 3.0.65
- Signed release APK built successfully.
- APK signature verification passed.
- GitHub Actions build run: 33899084873
- Artifact: iCE-Onhand-Inventory-3.0.65-signed
- Artifact ID: 9946939154

## Latest fix completed
The Options screen on the Samsung test phone was cutting off the current value under **Unknown Barcode Behavior** near the bottom of the dialog.

3.0.65 changes only that visibility issue while preserving earlier working behavior:
- Unknown Barcode Behavior now uses a taller two-line button.
- The second line explicitly shows `Current: <mode>`.
- Extra bottom spacer and ScrollView padding allow the whole final control to scroll above the fixed Done action.
- Android versionCode/versionName advanced to 30065 / 3.0.65 for in-place update.

Implementation is in `.github/prepare_3065.py`, which builds on `.github/prepare_3064.py` and all earlier retained features.

## Preferred logo reference saved
The user identified the older iCE Inventory LLC running-scanner logo shown in the 3.0.39 APK screenshot as the preferred logo direction, but asked for it to be brighter and less dull. An enhanced high-resolution version was created and saved persistently in the ChatGPT Library at:

`/OnHand-Android Checkpoints/iCE-Inventory-Logo-Enhanced-2026-09-04.png`

Use this enhanced logo as the preferred visual reference for the next app icon/logo update unless the user provides a newer replacement.

## Important preservation rule
Do not redesign or replace unrelated working screens. Continue from this checkpoint and make only the specific changes requested. Preserve scanner, inventory, export, passcode, sort, logo, and other already-working behavior unless explicitly asked to change them.

## Recovery instructions for a future chat
If conversation context is lost, open this repository and read this file first. Use branch `checkpoint-3.0.65-2026-09-04` as the known-good recovery point. Compare any newer `main` state against this checkpoint before making changes. Also retrieve the preferred enhanced logo from the ChatGPT Library path above.

## Immediate test to perform
Install 3.0.65 over the existing app, open **Options**, scroll to **Unknown Barcode Behavior**, and confirm both the control label and the `Current:` value are fully visible above **Done**.
