# iCE Onhand Inventory 3.0.75 checkpoint

Verified recovery point for the corrected Android UI requested on 2026-09-04.

## Approved 3.0.75 changes
- `SCAN COUNT ACCURATELY` is a small bold blue motto directly under the glossy iCE Inventory LLC logo. It is not the main count button.
- Main green inventory action is restored to `+ ADD QTY`.
- Cases screen keeps the existing multiplication/count logic unchanged and adds more lower-screen clearance so the custom keypad's bottom `0 / 00` row can move above the Samsung Android navigation bar.
- Cases fields keep the Samsung system keyboard hidden and use the app's custom number keypad.

## Preserved working features
- Scanner and barcode/count logic intentionally unchanged.
- Exact glossy green/gold scanner-figure iCE Inventory LLC logo preserved.
- Replace / Append / Cancel import behavior preserved.
- Internet Items With Pictures export preserved.
- Location Quantity Report preserved.
- Existing sorting, options, passcodes, locations, and export behavior preserved.

## Signed build verification
- Source commit: `12f30348632bbcb04d5e1f3178e2c7f083986d80`
- Canonical workflow: `Build OnHand APK`
- Workflow run: `33930821704`
- Job: `101208872919`
- Signed artifact: `iCE-Onhand-Inventory-3.0.75-signed`
- Artifact ID: `9958487302`
- Artifact digest: `sha256:02497b55bc3ac12c18261be49ed0b739b671e19d66a2e7886bb741aef4bd3419`
- APK signature verification: passed
- Finished APK inspection confirmed strings `SCAN COUNT ACCURATELY`, `ADD QTY`, and `Onhand Inventory 3.0.75` are packaged in the APK.

Next Android version after this checkpoint: 3.0.76.
