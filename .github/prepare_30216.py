#!/usr/bin/env python3
from pathlib import Path
import runpy

script_dir = Path(__file__).resolve().parent
root = script_dir.parent if script_dir.name == ".github" else script_dir
workflow = root / ".github/workflows/build-apk.yml"

# Recreate 3.0.215, then fix the Android chooser dialog that hid its list items.
w = workflow.read_text()
for new, old in [
    ("Prepare and verify 3.0.216 import chooser display", "Prepare and verify 3.0.215 import format chooser"),
    (".github/prepare_30216.py", ".github/prepare_30215.py"),
    ("iCE-Onhand-Inventory-3.0.216", "iCE-Onhand-Inventory-3.0.215"),
]:
    if new not in w:
        raise SystemExit("3.0.216 workflow seed missing: " + new)
    w = w.replace(new, old)
workflow.write_text(w)
runpy.run_path(str(root / ".github/prepare_30215.py"), run_name="__main__")

w = workflow.read_text()
for old, new in [
    ("Prepare and verify 3.0.215 import format chooser", "Prepare and verify 3.0.216 import chooser display"),
    (".github/prepare_30215.py", ".github/prepare_30216.py"),
    ("iCE-Onhand-Inventory-3.0.215", "iCE-Onhand-Inventory-3.0.216"),
]:
    if old not in w:
        raise SystemExit("3.0.215 workflow marker missing: " + old)
    w = w.replace(old, new)
workflow.write_text(w)

main = root / "app/src/main/java/com/iceinventory/onhand/MainActivity.java"
s = main.read_text()
old_dialog = '''        String[] choices={"Use Saved Format","Fleet Feet — Barcode, Item Number, Description, Size","Victoria — Qty, Barcode, Description, Item Number, Location","Generic POS — Qty, Barcode, Description, Price"};
        new AlertDialog.Builder(this).setTitle("Choose Import File Format")
                .setMessage("Choose the column layout in your file. The file picker opens next.")
                .setItems(choices,(d,which)->{'''
new_dialog = '''        String[] choices={"Use Saved Format — use the current setup","Fleet Feet — Barcode, Item Number, Description, Size","Victoria — Qty, Barcode, Description, Item Number, Location","Generic POS — Qty, Barcode, Description, Price"};
        new AlertDialog.Builder(this).setTitle("Choose Format — file selection opens next")
                .setItems(choices,(d,which)->{'''
if s.count(old_dialog) != 1:
    raise SystemExit("Import chooser dialog layout missing or ambiguous")
s = s.replace(old_dialog, new_dialog, 1)
main.write_text(s)

gradle = root / "app/build.gradle"
g = gradle.read_text()
if "versionCode 30215" not in g or "versionName '3.0.215'" not in g:
    raise SystemExit("3.0.215 Gradle version missing")
gradle.write_text(g.replace("versionCode 30215", "versionCode 30216", 1).replace("versionName '3.0.215'", "versionName '3.0.216'", 1))

manifest = root / "app/src/main/AndroidManifest.xml"
m = manifest.read_text()
if m.count("iCE Onhand 3.0.215") != 1:
    raise SystemExit("3.0.215 app label missing")
manifest.write_text(m.replace("iCE Onhand 3.0.215", "iCE Onhand 3.0.216", 1))

if s.count("Onhand Inventory 3.0.215") != 1:
    raise SystemExit("3.0.215 home label missing")
s = s.replace("Onhand Inventory 3.0.215", "Onhand Inventory 3.0.216", 1)
main.write_text(s)

checks = {
    "chooser presents visible list items": ".setMessage(" not in new_dialog and ".setItems(choices" in new_dialog,
    "all expected layouts are listed": all(x in new_dialog for x in ["Fleet Feet", "Victoria", "Generic POS", "Use Saved Format"]),
    "format choice continues to file picker": "importCsv();" in s[s.find("private void showStandardImportFormatDialog"):s.find("private void startImportFormatFlow")],
    "release labels": "versionName '3.0.216'" in gradle.read_text() and "iCE Onhand 3.0.216" in manifest.read_text() and "Onhand Inventory 3.0.216" in s,
    "workflow points to release": ".github/prepare_30216.py" in workflow.read_text() and "3.0.216" in workflow.read_text(),
}
failed = [name for name, passed in checks.items() if not passed]
if failed:
    raise SystemExit("3.0.216 validation failed: " + ", ".join(failed))
print("Prepared iCE OnHand 3.0.216: import format choices display before selecting the customer file.")
