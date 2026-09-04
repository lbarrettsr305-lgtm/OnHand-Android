# iCE Onhand Inventory 3.0.68 Recovery Checkpoint

Date: 2026-09-04

## Current known-good version
- Version: 3.0.68
- Main commit: `da4a7919457cd676b026ffa9d9a13661c7c5a646`
- Prep script: `.github/prepare_3068.py`
- Build workflow: `.github/workflows/build-apk.yml`

## Approved logo
- Approved logo source: `app/src/main/res/drawable/ice_onhand_approved.png`
- Historical source blob SHA: `699a46639adcb199f60800c75d2aa5121cb8dba9`
- 3.0.68 uses this approved green/gold circular iCE barcode logo for the in-app header and Android application icon/round icon.
- Do not replace it with a generated/recreated logo or the Android default icon.

## Internet Items With Pictures export
- Regular inventory export remains the existing tab-delimited TXT export.
- Internet-added items have a separate `Internet Items With Pictures` export.
- The separate export is an HTML report with columns for Picture, Barcode, Description, Quantity, Location, and Price.
- Associated product image URLs already stored by Internet item lookup are used for the picture column.
- If no image URL exists, the report displays `No picture available`.
- The report references online image URLs, so an internet connection is needed to display those images when the HTML report is opened.

## Signed build verification
- Canonical workflow run ID: `33906223314`
- Build job ID: `101131675072`
- Artifact ID: `9949606679`
- Artifact name: `iCE-Onhand-Inventory-3.0.68-signed`
- Artifact digest: `sha256:357eb89faeca22bd82f9df4941c92a64a648e1eff1c6d5e4d874e6c2b749f09e`
- Prepare 3.0.68, signing-key verification, signed release build, APK rename, APK signature verification, and artifact upload all completed successfully.

## APK inspection
- APK output: `iCE-Onhand-Inventory-3.0.68.apk`
- Compiled APK contains `Onhand Inventory 3.0.68`, `Internet Items With Pictures`, `No picture available`, and `text/html` report support.
- The compiled 128x128 application logo extracted from the APK is the approved circular green/gold iCE barcode design, not the generic Android robot.

## Preservation rule
Preserve all existing working 3.0.67 and earlier functionality unless the user explicitly requests a change. Future incremental work should build on 3.0.68.

## Future-chat recovery
If chat history is missing, read this checkpoint and inspect `main` before making changes. The next normal version should be 3.0.69, using `.github/prepare_3069.py` and calling `.github/prepare_3068.py` first.

## Immediate user test
1. Install 3.0.68 over 3.0.67.
2. Verify the app/Files icon shows the approved circular green/gold iCE barcode logo instead of the Android robot.
3. Verify the logo in the app header is the same approved logo.
4. Export regular inventory and confirm the normal TXT export is unchanged.
5. Choose `Internet Items With Pictures`, save/open the HTML file while online, and verify associated product pictures appear with the Internet items.
