# iCE Onhand Inventory 3.0.69 Recovery Checkpoint

Date: 2026-09-04

## Current known-good build candidate
- Version: 3.0.69
- Main commit: `51f8d5adc7e9ca669862e9e6ed621d07e0ff297c`
- Prep script: `.github/prepare_3069.py`
- Build workflow: `.github/workflows/build-apk.yml`

## Scanner preservation rule
The user reported a real approximately four-hour inventory scanning session on the pre-3.0.69 Android build with the core scanning/count workflow working well. 3.0.69 intentionally does not alter the scanner/count logic. Preserve the proven scanner behavior unless the user explicitly requests a scanner change.

## Exact approved logo
The user rejected the simplified circular iCE barcode logo. The exact approved logo is the glossy green/gold design with:
- running/scanner figure
- green barcode beam
- `iCE INVENTORY LLC`
- `SCAN • COUNT • CONTROL`

The exact source already stored in the repository is:
`app/src/main/res/drawable/ice_inventory_logo_3066.webp`

During 3.0.69 preparation it is copied to one master resource:
`app/src/main/res/drawable/ice_inventory_master_3069.webp`

Both the in-app header and Android `icon` / `roundIcon` references are forced to this master resource. Do not revert to `ice_onhand_approved.png`, the circular logo, generic Android robot icon, or a recreated logo.

## Add Count layout fix
The Samsung test screenshot showed `+ Add Count` wrapping and clipping at the bottom. 3.0.69 keeps the action unchanged but:
- makes the label single-line
- centers it
- uses a 14sp label
- gives it more horizontal weight
- raises the action row from 52dp to 58dp

Cases and New Location remain present and functional.

## Internet Items export
Preserve the working 3.0.68 behavior:
- regular inventory export remains normal tab-delimited TXT
- `Internet Items With Pictures` remains a separate HTML report
- internet product pictures are included from stored image URLs

## Signed build verification
Canonical workflow run ID: `33915197781`
Build job ID: `101160635290`
Artifact ID: `9952897935`
Artifact name: `iCE-Onhand-Inventory-3.0.69-signed`
Artifact ZIP digest: `sha256:fd3e59c98350345045824855d79572d1c73176e323af548216d307a831cee0ec`
APK SHA-256: `ca512124fc485bf4c9896989047c89c46770b590c0950a1c2e15eb4d76958bd1`
APK size: 1,313,332 bytes

Prepare 3.0.69, signing-key verification, signed release build, rename, APK signature verification, and artifact upload all completed successfully.

APK inspection confirmed compiled strings for:
- `Onhand Inventory 3.0.69`
- `Internet Items With Pictures`
- `No picture available`
- `text/html`
- `Add Count`

## Planned multi-user cloud phase after Android is fully stable
The user wants the final Android app completed first. After that, planned architecture is:
1. Create a new inventory project from one original import file.
2. Distribute the same original project/import data to multiple users/scanners.
3. Each user scans independently and keeps an immutable original user count file.
4. Upload/sync each user's count to a shared cloud project.
5. Create a combined master count while preserving every original user file.
6. Keep a master-detail/audit view showing user/device/location/count information.
7. Share Internet Products by barcode across users so if one user finds an unknown product, another user scanning the same barcode can reuse the description/picture instead of searching again.
8. Export a combined Internet Products file/report.
9. Design offline-first so scanning continues during weak/no internet and sync happens later.
10. Firebase is the current recommended cloud direction because it can later support Android and an iPhone/iPad version.

## Future pill counting idea
The user also asked about counting pills from a camera scan. This is a possible later feature: scan the product barcode, photograph loose pills on a contrasting tray, computer-vision count visible pills, show detected pills for operator review, then insert the confirmed total into Quantity. Treat this as inventory assistance, not as a sole medication-dispensing control.

## iOS direction
After Android is complete and stable, the user wants a separate iPhone/iPad version with compatible inventory/project files and the same cloud backend.

## Future-chat recovery
If chat history disappears, read this checkpoint first, inspect `main`, and continue from 3.0.69. The next normal Android version should be 3.0.70 with `.github/prepare_3070.py` calling `.github/prepare_3069.py` first.

## Immediate user test for 3.0.69
1. Install 3.0.69 over 3.0.68.
2. Confirm the APK/app icon shows the exact glossy green/gold scanner-figure iCE Inventory LLC logo.
3. Open the app and confirm the same exact logo is used in the header.
4. Confirm `+ Add Count` is fully visible on one line and not clipped.
5. Confirm normal scanning/counting remains unchanged.
6. Confirm both regular TXT export and Internet Items With Pictures still work.
