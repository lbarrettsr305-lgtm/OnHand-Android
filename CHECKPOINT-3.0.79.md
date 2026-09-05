# iCE Onhand Inventory 3.0.79 — Verified Checkpoint

Date: 2026-09-05

Base commit: `90c8622f1f52cf270a40a72a007f2a94b84704c0`
Canonical workflow: `.github/workflows/build-apk.yml`
Workflow run: `33942469293` (run #181)
Result: SUCCESS
Artifact: `iCE-Onhand-Inventory-3.0.79-signed`
Artifact ID: `9962291075`
Artifact digest: `sha256:199595eaa66909b42cff3c11aefc5a3129030f2d1ba62ee82f4aa34b18ea1063`

## Verified 3.0.79 behavior

- Preserves the successful 3.0.78 Cases multiplication/input correction and raised custom keypad.
- Preserves current-scan-at-top / previous-count-below workflow inherited from prior approved builds.
- Preserves TXT and Excel inventory export with headers: Quantity, Barcode, Description, Price.
- Phone camera scan can continue automatically after the operator enters quantity and commits the count.
- Cancelling/backing out of the phone camera stops the continuous phone-scan cycle.
- Bluetooth/manual scanner behavior remains separate and unchanged.
- Unknown barcode lookup still uses structured barcode databases first.
- If no structured match is found, the app can offer a Google search using the exact barcode, then return focus to Description for manual entry.

## Recovery rule

Any new version should chain `.github/prepare_3079.py` and preserve this checkpoint unless the user explicitly requests a behavior change.

Next version: 3.0.80
