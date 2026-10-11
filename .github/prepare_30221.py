#!/usr/bin/env python3
from pathlib import Path
import runpy

root=Path(__file__).resolve().parent.parent
workflow=root/".github/workflows/build-apk.yml"
runpy.run_path(str(root/".github/prepare_30220.py"),run_name="__main__")
w=workflow.read_text()
for old,new in [
    ("Prepare and verify 3.0.220 external scanner flow","Prepare and verify 3.0.221 import location prompt"),
    (".github/prepare_30220.py",".github/prepare_30221.py"),
    ("iCE-Onhand-Inventory-3.0.220","iCE-Onhand-Inventory-3.0.221"),
]:
    if old not in w: raise SystemExit("3.0.220 workflow marker missing: "+old)
    w=w.replace(old,new)
workflow.write_text(w)

main=root/"app/src/main/java/com/iceinventory/onhand/MainActivity.java"
s=main.read_text()
old='''            String importedName=importFileName(uri);
            db.replaceSession(sessionId,importedName);
            sessionName=importedName;'''
new='''            String importedName=importFileName(uri);
            db.replaceSession(sessionId,importedName);
            // A replacement import begins a new count: require the operator to
            // confirm its starting location instead of carrying the old one over.
            prefs().edit().remove(confirmedLocationKey(sessionId)).apply();
            confirmedLocation="";
            confirmedLocationSession=-1L;
            sessionName=importedName;'''
if s.count(old)!=1: raise SystemExit("Import replacement location reset point missing or ambiguous")
s=s.replace(old,new,1)
old='''            refreshLocations();refreshList();
            toast("Replaced current inventory with "+rows.size()+" rows: "+importedName);'''
new='''            refreshLocations();refreshList();
            toast("Replaced current inventory with "+rows.size()+" rows: "+importedName);
            showLocationStep();'''
if s.count(old)!=1: raise SystemExit("Successful import completion point missing or ambiguous")
s=s.replace(old,new,1)
main.write_text(s)

gradle=root/"app/build.gradle"
g=gradle.read_text()
if "versionCode 30220" not in g or "versionName '3.0.220'" not in g: raise SystemExit("3.0.220 Gradle version missing")
gradle.write_text(g.replace("versionCode 30220","versionCode 30221",1).replace("versionName '3.0.220'","versionName '3.0.221'",1))
manifest=root/"app/src/main/AndroidManifest.xml"
m=manifest.read_text()
if m.count("iCE Onhand 3.0.220")!=1: raise SystemExit("3.0.220 manifest label missing")
manifest.write_text(m.replace("iCE Onhand 3.0.220","iCE Onhand 3.0.221",1))
s=main.read_text()
if s.count("Onhand Inventory 3.0.220")!=1: raise SystemExit("3.0.220 home label missing")
main.write_text(s.replace("Onhand Inventory 3.0.220","Onhand Inventory 3.0.221",1))

s=main.read_text()
checks={
    "old location cleared after replacement": 'prefs().edit().remove(confirmedLocationKey(sessionId)).apply();' in s and 'confirmedLocationSession=-1L;' in s,
    "location picker shown after successful import": 'toast("Replaced current inventory with "+rows.size()+" rows: "+importedName);\n            showLocationStep();' in s,
    "scanner focus and highlight retained": 'barcode.post(this::focusBarcodeWithoutKeyboard)' in s and 'private void scrollToLastBarcode()' in s,
    "automatic increment retained": 'auto_increment_count' in s,
    "shared scanner settings retained": 'UNKNOWN_BARCODE_MODE=' in s and 'MAXIMUM_QTY=' in s,
    "release labels": "versionName '3.0.221'" in gradle.read_text() and "iCE Onhand 3.0.221" in manifest.read_text() and "Onhand Inventory 3.0.221" in s,
    "workflow points to release": ".github/prepare_30221.py" in workflow.read_text() and "3.0.221" in workflow.read_text(),
}
failed=[name for name,passed in checks.items() if not passed]
if failed: raise SystemExit("3.0.221 validation failed: "+", ".join(failed))
print("Prepared iCE OnHand 3.0.221: successful replacement imports clear the previous location and prompt for a new starting location.")
