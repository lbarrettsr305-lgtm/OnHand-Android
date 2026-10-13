#!/usr/bin/env python3
from pathlib import Path
import runpy

root = Path(__file__).resolve().parent.parent
workflow = root / ".github/workflows/build-apk.yml"
runpy.run_path(str(root / ".github/prepare_30224.py"), run_name="__main__")

w = workflow.read_text()
for old, new in [
    ("Prepare and verify 3.0.224 replacement location and export names", "Prepare and verify 3.0.225 start count import label"),
    (".github/prepare_30224.py", ".github/prepare_30225.py"),
    ("iCE-Onhand-Inventory-3.0.224", "iCE-Onhand-Inventory-3.0.225"),
]:
    if w.count(old) != 1:
        raise SystemExit("3.0.224 workflow marker missing or ambiguous: " + old)
    w = w.replace(old, new, 1)
workflow.write_text(w)

gradle = root / "app/build.gradle"
g = gradle.read_text()
if g.count("versionCode 30224") != 1 or g.count("versionName '3.0.224'") != 1:
    raise SystemExit("3.0.224 Gradle version missing or ambiguous")
g = g.replace("versionCode 30224", "versionCode 30225", 1)
g = g.replace("versionName '3.0.224'", "versionName '3.0.225'", 1)
gradle.write_text(g)

manifest = root / "app/src/main/AndroidManifest.xml"
m = manifest.read_text()
if m.count("iCE Onhand 3.0.224") != 1:
    raise SystemExit("3.0.224 manifest label missing or ambiguous")
manifest.write_text(m.replace("iCE Onhand 3.0.224", "iCE Onhand 3.0.225", 1))

main = root / "app/src/main/java/com/iceinventory/onhand/MainActivity.java"
s = main.read_text()
for old, new, label in [
    ('Button imp=button("↓ START / IMPORT",1);', 'Button imp=button("↓ START COUNT / IMPORT",1);', "bottom button label"),
    ('Onhand Inventory 3.0.224', 'Onhand Inventory 3.0.225', "home version label"),
]:
    if s.count(old) != 1:
        raise SystemExit(label + " missing or ambiguous")
    s = s.replace(old, new, 1)
main.write_text(s)

checks = {
    "button label": 'Button imp=button("↓ START COUNT / IMPORT",1);' in s,
    "Gradle version": "versionCode 30225" in g and "versionName '3.0.225'" in g,
    "manifest version": "iCE Onhand 3.0.225" in manifest.read_text(),
    "workflow version": "iCE-Onhand-Inventory-3.0.225" in workflow.read_text(),
}
failed = [name for name, passed in checks.items() if not passed]
if failed:
    raise SystemExit("3.0.225 validation failed: " + ", ".join(failed))
print("Prepared iCE OnHand 3.0.225: bottom action is START COUNT / IMPORT.")
