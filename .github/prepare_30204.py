#!/usr/bin/env python3
from pathlib import Path
import re
import runpy

root = Path(__file__).resolve().parents[1]
runpy.run_path(str(root / ".github" / "prepare_30203.py"), run_name="__main__")

gradle = root / "app" / "build.gradle"
s = gradle.read_text()
if "versionName '3.0.203'" not in s or "versionCode 30203" not in s:
    raise SystemExit("3.0.203 version source not found")
s = s.replace("versionCode 30203", "versionCode 30204", 1)
s = s.replace("versionName '3.0.203'", "versionName '3.0.204'", 1)
gradle.write_text(s)

manifest = root / "app" / "src" / "main" / "AndroidManifest.xml"
s = manifest.read_text()
if "iCE Onhand 3.0.203" not in s:
    raise SystemExit("3.0.203 app label not found")
manifest.write_text(s.replace("iCE Onhand 3.0.203", "iCE Onhand 3.0.204", 1))

main = root / "app" / "src" / "main" / "java" / "com" / "iceinventory" / "onhand" / "MainActivity.java"
s = main.read_text()
if "Onhand Inventory 3.0.203" not in s:
    raise SystemExit("3.0.203 screen version not found")
s = s.replace("Onhand Inventory 3.0.203", "Onhand Inventory 3.0.204", 1)

pattern = r'''    private void readImport\(Uri uri\) \{.*?\n    private void verifyMasterPinForAdvancedImport'''
replacement = r'''    private void readImport(Uri uri) {
        if(uri==null)return;
        if(!isMasterDevice()) {
            new AlertDialog.Builder(this)
                    .setTitle("Replace Current Inventory?")
                    .setMessage("RECOMMENDED DEFAULT\n\nThis replaces the current inventory with the selected shared store file. A recovery checkpoint is created first, and your User Name remains unchanged.")
                    .setPositiveButton("REPLACE CURRENT INVENTORY",(d,w)->performImport(uri,true))
                    .setNeutralButton("ADVANCED OPTIONS",(d,w)->verifyMasterPinForAdvancedImport(()->showAdvancedImportOptions(uri)))
                    .setNegativeButton("Cancel",null)
                    .show();
            return;
        }
        new AlertDialog.Builder(this)
                .setTitle("Add Count to Current Inventory?")
                .setMessage("RECOMMENDED FOR A MASTER COUNT IMPORT\n\nChoose ADD / MERGE to add Robert's completed regular count to the active Victoria inventory. Your existing Chief counts stay in place. Matching Barcode + Location quantities are combined; new items or locations are added.\n\nUse REPLACE only when loading a new starting inventory.")
                .setPositiveButton("ADD / MERGE USER COUNT",(d,w)->verifyMasterPinForAdvancedImport(()->performImport(uri,false)))
                .setNeutralButton("REPLACE INVENTORY",(d,w)->verifyMasterPinForAdvancedImport(()->confirmReplaceImport(uri)))
                .setNegativeButton("Cancel",null)
                .show();
    }

    private void confirmReplaceImport(Uri uri) {
        new AlertDialog.Builder(this)
                .setTitle("Replace All Current Inventory Data?")
                .setMessage("This will remove all existing count rows in the active inventory and load only the selected file. A recovery checkpoint is created first. For Robert's completed count, choose ADD / MERGE instead.")
                .setPositiveButton("REPLACE ALL DATA",(d,w)->performImport(uri,true))
                .setNegativeButton("Cancel",null)
                .show();
    }

    private void verifyMasterPinForAdvancedImport''';
s, n = re.subn(pattern, lambda match: replacement, s, count=1, flags=re.S)
if n != 1:
    raise SystemExit("3.0.204 target missing or ambiguous: Master-aware import prompt")
main.write_text(s)

checks = {
    "version": "versionName '3.0.204'" in gradle.read_text(),
    "screen version": "Onhand Inventory 3.0.204" in main.read_text(),
    "Master merge default": 'setPositiveButton("ADD / MERGE USER COUNT"' in main.read_text(),
    "Master PIN required for merge": 'verifyMasterPinForAdvancedImport(()->performImport(uri,false))' in main.read_text(),
    "replace requires confirmation": 'setPositiveButton("REPLACE ALL DATA"' in main.read_text(),
    "Count User replace behavior retained": 'setTitle("Replace Current Inventory?")' in main.read_text(),
    "merge uses additive import": "performImport(uri,false)" in main.read_text(),
}
failed = [name for name, ok in checks.items() if not ok]
if failed:
    raise SystemExit("3.0.204 verification failed: " + ", ".join(failed))
print("Prepared iCE Onhand 3.0.204: Master imports add/merge user counts by barcode and location; replace is PIN-protected and confirmed")
