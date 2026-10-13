#!/usr/bin/env python3
from pathlib import Path
import runpy

script_dir = Path(__file__).resolve().parent
root = script_dir.parent if script_dir.name == ".github" else script_dir
workflow = root / ".github/workflows/build-apk.yml"

# Rebuild from the tested import replacement release.
w=workflow.read_text()
for new,old in [
    ("Prepare and verify 3.0.219 replace import instructions","Prepare and verify 3.0.218 import replacement behavior"),
    (".github/prepare_30219.py",".github/prepare_30218.py"),
    ("iCE-Onhand-Inventory-3.0.219","iCE-Onhand-Inventory-3.0.218"),
]:
    if new not in w:raise SystemExit("3.0.219 workflow seed missing: "+new)
    w=w.replace(new,old)
workflow.write_text(w)
runpy.run_path(str(root/".github/prepare_30218.py"),run_name="__main__")

w=workflow.read_text()
for old,new in [
    ("Prepare and verify 3.0.218 import replacement behavior","Prepare and verify 3.0.219 replace import instructions"),
    (".github/prepare_30218.py",".github/prepare_30219.py"),
    ("iCE-Onhand-Inventory-3.0.218","iCE-Onhand-Inventory-3.0.219"),
]:
    if old not in w:raise SystemExit("3.0.218 workflow marker missing: "+old)
    w=w.replace(old,new)
workflow.write_text(w)

main=root/"app/src/main/java/com/iceinventory/onhand/MainActivity.java"
s=main.read_text()
old='Choose the button matching the columns in the customer file. The file picker opens next.'
new='Choose the button matching the file columns. Import replaces the active inventory and renames it from the selected file.'
if s.count(old)!=1:raise SystemExit("Import format instructions missing or ambiguous")
s=s.replace(old,new,1)
main.write_text(s)

gradle=root/"app/build.gradle"
g=gradle.read_text()
if "versionCode 30218" not in g or "versionName '3.0.218'" not in g:raise SystemExit("3.0.218 Gradle version missing")
gradle.write_text(g.replace("versionCode 30218","versionCode 30219",1).replace("versionName '3.0.218'","versionName '3.0.219'",1))

manifest=root/"app/src/main/AndroidManifest.xml"
m=manifest.read_text()
if m.count("iCE Onhand 3.0.218")!=1:raise SystemExit("3.0.218 manifest label missing")
manifest.write_text(m.replace("iCE Onhand 3.0.218","iCE Onhand 3.0.219",1))

s=main.read_text()
if s.count("Onhand Inventory 3.0.218")!=1:raise SystemExit("3.0.218 home label missing")
main.write_text(s.replace("Onhand Inventory 3.0.218","Onhand Inventory 3.0.219",1))

checks={
    "replace and rename instruction visible":new in main.read_text(),
    "import parser replaces selected inventory": "db.replaceSession(sessionId,importedName);" in main.read_text(),
    "CSV and tab formats supported": "parseLine(String line, char delimiter)" in (root/"app/src/main/java/com/iceinventory/onhand/CsvUtils.java").read_text(),
    "version labels": "versionName '3.0.219'" in gradle.read_text() and "iCE Onhand 3.0.219" in manifest.read_text() and "Onhand Inventory 3.0.219" in main.read_text(),
    "workflow release markers": ".github/prepare_30219.py" in workflow.read_text() and "3.0.219" in workflow.read_text(),
}
failed=[k for k,v in checks.items() if not v]
if failed:raise SystemExit("3.0.219 validation failed: "+", ".join(failed))
print("Prepared iCE OnHand 3.0.219 with clear replace-and-rename import instructions.")
