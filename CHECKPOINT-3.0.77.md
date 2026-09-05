# iCE Onhand Inventory 3.0.77 Recovery Checkpoint

Date: 2026-09-05
Base main commit: `14af5fb9b9ca9a0680be1ed84f46277f24598b3f`
Canonical workflow: `Build OnHand APK` (`.github/workflows/build-apk.yml`)
Canonical run: `33940935891`
Canonical artifact: `iCE-Onhand-Inventory-3.0.77-signed`, artifact ID `9961804017`
Artifact digest: `sha256:346d7bbb1df658cb43531d047ca0db5ee0ba761482c0b61cbf990d3d5ab32325`
APK SHA-256 after extraction: `0e082f5c7f0cf15fb4019b51f9e03fa39886a42f00c7b77679996adc6be52d0e`

## Preserved / fixed behavior

- Exact verified glossy green/gold iCE Inventory LLC scanner-figure logo from 3.0.70 remains in the preparation chain.
- Small blue `SCAN COUNT ACCURATELY` slogan remains under the logo.
- Main green `ADD QTY` action remains restored.
- Import retains Replace / Append / Cancel behavior.
- Internet Items With Pictures remains a separate HTML export.
- Location Quantity Report remains a separate TXT report.
- 3.0.76 scan visibility fix is preserved: current scanned item is row 1, previous scanned item is row 2, and Samsung system keyboard remains hidden after a scan until Quantity is deliberately touched.
- 3.0.76 Cases fix is preserved: custom keypad can enter both operands and supports `10 × 20 = 200`.

## 3.0.77 export changes

- Standard inventory TXT exports now include a first-row header.
- Standard/default header order is exactly: `Quantity | Barcode | Description | Price`.
- Added true Microsoft Excel `.xlsx` export in addition to TXT; TXT was not removed.
- Excel uses the same selected output columns and header names as TXT.
- Excel header row is bold and frozen; Barcode is stored as text to preserve leading zeroes.
- Export choices are standard inventory TXT, standard inventory Excel (.xlsx), Internet Items With Pictures, and Location Quantity Report.

## Build verification

Canonical run `33940935891` completed successfully. Preparation, signing-key verification, signed release build, APK rename, APK signature verification, and artifact upload all passed.
