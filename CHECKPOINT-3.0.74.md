# iCE Onhand Inventory 3.0.74 Recovery Checkpoint

Date: 2026-09-04
Base commit: bff7f5c8110b8e48c3b5bb7972a0ecfcb40cd460

## Verified changes
- Cases screen made more compact and auto-scrolls to reveal the full custom keypad and ADD COUNT area on the Samsung Android 16 test device.
- Samsung system keyboard remains hidden on the Cases screen.
- Cases multiplication logic is unchanged.
- Main primary action is now **SCAN COUNT ACCURATELY** on two lines.
- Primary action is a bold blue button with white text so it stands out without looking like a warning/delete action.
- Scanner/count logic remains unchanged from the proven stable workflow.
- Replace / Append / Cancel import choice preserved.
- Location Quantity Report preserved.
- Internet Items With Pictures export preserved.
- Verified glossy iCE Inventory LLC scanner-figure logo preserved.

## Build verification
- Canonical workflow: Build OnHand APK
- Workflow run: 33928363397
- Artifact ID: 9957653571
- Artifact name: iCE-Onhand-Inventory-3.0.74-signed
- Artifact digest: sha256:1e3229bb4b6d928b8083d036d158b25d3e6ece813cc22d1b355366ac45d1857e
- Extracted APK SHA-256: 8612e404a004819e5740349bc771e18b387eeeb596e571c08b925965e080f033
- APK signature verification passed.

Next version: 3.0.75
