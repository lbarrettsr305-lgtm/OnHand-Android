# iCE Onhand Inventory 3.0.70 Recovery Checkpoint

Date: 2026-09-04

## Current verified version
- Version: 3.0.70
- Main commit: `1f7abb24cd99607821d39464215f51dab200ce95`
- Prep script: `.github/prepare_3070.py`
- Canonical workflow: `.github/workflows/build-apk.yml`

## Why 3.0.70 was needed
- 3.0.69 fixed the Add Count clipping but the in-app logo appeared blank.
- Root cause: the generated 3.0.69 WEBP resource was corrupt/unreadable.
- 3.0.70 replaces that resource with a verified WebP payload decoded during build.

## Approved logo
The only approved logo is the glossy black/green/gold full iCE Inventory LLC mark with:
- running/scanner figure
- green scan beam / barcode
- `iCE`
- `INVENTORY`
- `LLC`
- `SCAN • COUNT • CONTROL`

Do not replace it with the circular simplified barcode logo or Android default icon.

3.0.70 uses `.github/assets/ice_inventory_master_3070.b64`, decoded by `.github/prepare_3070.py` into `app/src/main/res/drawable/ice_inventory_master_3070.webp` during the build.

## APK logo verification
- The finished APK was extracted after the signed build.
- The compiled approved logo resource is a valid 128x128 WebP.
- Extracted resource size: 7,124 bytes.
- SHA-256: `4c2fe00f2758b728954f68d5c242c0d266a7ebe4a48056568ee5fa9443b77926`
- It was opened and visually verified as the exact glossy scanner-figure iCE Inventory LLC logo.
- The old corrupt 3.0.69 generated copy is removed during preparation.

## Preserved behavior
- Scanner/count logic is unchanged from 3.0.69.
- Add Count button fix from 3.0.69 is preserved.
- Cases multiplication, locations, Options, passcodes, sorting, regular TXT export, and Internet Items With Pictures export are preserved.
- User reported the core scanner workflow survived a roughly four-hour real inventory scan before this logo-only correction; protect that scan behavior.

## Signed build verification
- Canonical workflow run ID: `33918753171`
- Build job ID: `101171927665`
- Artifact ID: `9954195442`
- Artifact name: `iCE-Onhand-Inventory-3.0.70-signed`
- Artifact digest: `sha256:9378dd19b62f44f103545831f6454432d262177f765129455b277d43576cfbae`
- Prepare 3.0.70, signing-key restore/verification, signed release build, rename, APK signature verification, and artifact upload all completed successfully.

## Future work
Future incremental Android work should build on 3.0.70 and call `.github/prepare_3070.py` first. Do not alter the proven scanning logic unless explicitly requested.

Planned future major phase after Android is fully stabilized: offline-first multi-user cloud projects, raw customer TXT/Excel validation/normalization, separate original user counts, shared Internet Products, combined UPC totals, and final Qty / UPC / Description / Price export.
