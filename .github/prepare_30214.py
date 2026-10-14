#!/usr/bin/env python3
from pathlib import Path
import runpy

script_dir = Path(__file__).resolve().parent
root = script_dir.parent if script_dir.name == ".github" else script_dir
workflow = root / ".github/workflows/build-apk.yml"

# Recreate the validated 3.0.213 template corrections, then advance one release.
w = workflow.read_text()
for new, old in [
    ("Prepare and verify 3.0.214 import flow fix", "Prepare and verify 3.0.213 import template fixes"),
    (".github/prepare_30214.py", ".github/prepare_30213.py"),
    ("iCE-Onhand-Inventory-3.0.214", "iCE-Onhand-Inventory-3.0.213"),
]:
    if new not in w:
        raise SystemExit("3.0.214 workflow seed missing: " + new)
    w = w.replace(new, old)
workflow.write_text(w)
runpy.run_path(str(root / ".github/prepare_30213.py"), run_name="__main__")

w = workflow.read_text()
for old, new in [
    ("Prepare and verify 3.0.213 import template fixes", "Prepare and verify 3.0.214 import flow fix"),
    (".github/prepare_30213.py", ".github/prepare_30214.py"),
    ("iCE-Onhand-Inventory-3.0.213", "iCE-Onhand-Inventory-3.0.214"),
]:
    if old not in w:
        raise SystemExit("3.0.213 workflow marker missing: " + old)
    w = w.replace(old, new)
workflow.write_text(w)

main = root / "app/src/main/java/com/iceinventory/onhand/MainActivity.java"
s = main.read_text()
start = s.find("    private void showImportMenu() {")
end = s.find("\n    private void startImportFormatFlow()", start)
if start < 0 or end < 0:
    raise SystemExit("Import menu method boundaries missing")
menu = s[start:end]
old_counter = "if(!hasAdminAccess()){startImportFormatFlow();return;}"
old_master = "else startImportFormatFlow();"
if menu.count(old_counter) != 1 or menu.count(old_master) != 1:
    raise SystemExit("Import menu format handoff missing or ambiguous")
menu = menu.replace(old_counter, "if(!hasAdminAccess()){importCsv();return;}", 1)
menu = menu.replace(old_master, "else importCsv();", 1)
s = s[:start] + menu + s[end:]
main.write_text(s)

fmt_path = root / "app/src/main/java/com/iceinventory/onhand/FormatConfigActivity.java"
f = fmt_path.read_text()
old_help = '"Choose the preset matching your file. Fleet Feet uses Barcode, Item Number, Description, Size, with no quantity column. CSV and tab-delimited text files are supported; barcode must remain included.";'
new_help = '"Choose and save the preset matching your file here. To import, return Home, tap START / IMPORT, choose Shared User / Standard TXT File, then select the customer file. Fleet Feet uses Barcode, Item Number, Description, Size. CSV and tab-delimited TXT are supported.";'
if f.count(old_help) != 1:
    raise SystemExit("Import setup instructions missing or ambiguous")
f = f.replace(old_help, new_help, 1)
if f.count('"SAVE IMPORT FORMAT"') != 1:
    raise SystemExit("Import format save button missing or ambiguous")
f = f.replace('"SAVE IMPORT FORMAT"', '"SAVE FORMAT"', 1)
fmt_path.write_text(f)

gradle = root / "app/build.gradle"
g = gradle.read_text()
if "versionCode 30213" not in g or "versionName '3.0.213'" not in g:
    raise SystemExit("3.0.213 Gradle version missing")
gradle.write_text(g.replace("versionCode 30213", "versionCode 30214", 1).replace("versionName '3.0.213'", "versionName '3.0.214'", 1))

manifest = root / "app/src/main/AndroidManifest.xml"
m = manifest.read_text()
if m.count("iCE Onhand 3.0.213") != 1:
    raise SystemExit("3.0.213 app label missing")
manifest.write_text(m.replace("iCE Onhand 3.0.213", "iCE Onhand 3.0.214", 1))

if s.count("Onhand Inventory 3.0.213") != 1:
    raise SystemExit("3.0.213 home label missing")
s = s.replace("Onhand Inventory 3.0.213", "Onhand Inventory 3.0.214", 1)
main.write_text(s)

checks = {
    "import menu opens file picker": "if(!hasAdminAccess()){importCsv();return;}" in menu and "else importCsv();" in menu,
    "settings explain actual import steps": "tap START / IMPORT" in f and "select the customer file" in f,
    "Fleet Feet template retained": 'String[] fields={"barcode","item_number","description","size"};' in f,
    "save format label": '"SAVE FORMAT"' in f,
    "version labels": "versionName '3.0.214'" in gradle.read_text() and "iCE Onhand 3.0.214" in manifest.read_text() and "Onhand Inventory 3.0.214" in main.read_text(),
    "workflow points to release": ".github/prepare_30214.py" in workflow.read_text() and "3.0.214" in workflow.read_text(),
}
failed = [name for name, passed in checks.items() if not passed]
if failed:
    raise SystemExit("3.0.214 validation failed: " + ", ".join(failed))
print("Prepared iCE OnHand 3.0.214: import menu opens file picker with saved template; setup instructions clarified.")
