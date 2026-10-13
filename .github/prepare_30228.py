#!/usr/bin/env python3
"""Prepare 3.0.228: legible, two-line New Inventory / Import action."""
from pathlib import Path
import runpy

root = Path(__file__).resolve().parent.parent
workflow = root / ".github/workflows/build-apk.yml"

# The 3.0.227 preparation script reconstructs the earlier release chain.
# Temporarily give it its expected workflow markers.
w = workflow.read_text()
for new, old, expected in [
    ("Prepare and verify 3.0.228 responsive new inventory import button", "Prepare and verify 3.0.227 optional default qty and clean export columns", 1),
    (".github/prepare_30228.py", ".github/prepare_30227.py", 1),
    ("iCE-Onhand-Inventory-3.0.228", "iCE-Onhand-Inventory-3.0.227", 4),
]:
    if w.count(new) != expected:
        raise SystemExit("3.0.228 workflow marker missing or ambiguous: " + new)
    w = w.replace(new, old)
workflow.write_text(w)

runpy.run_path(str(root / ".github/prepare_30227.py"), run_name="__main__")

# Restore the current release names after the previous release is prepared.
w = workflow.read_text()
for old, new, expected in [
    ("Prepare and verify 3.0.227 optional default qty and clean export columns", "Prepare and verify 3.0.228 responsive new inventory import button", 1),
    (".github/prepare_30227.py", ".github/prepare_30228.py", 1),
    ("iCE-Onhand-Inventory-3.0.227", "iCE-Onhand-Inventory-3.0.228", 4),
]:
    if w.count(old) != expected:
        raise SystemExit("3.0.227 workflow marker missing or ambiguous: " + old)
    w = w.replace(old, new)
workflow.write_text(w)

gradle = root / "app/build.gradle"
g = gradle.read_text()
if g.count("versionCode 30227") != 1 or g.count("versionName '3.0.227'") != 1:
    raise SystemExit("3.0.227 version missing or ambiguous")
g = g.replace("versionCode 30227", "versionCode 30228", 1)
g = g.replace("versionName '3.0.227'", "versionName '3.0.228'", 1)
gradle.write_text(g)

manifest = root / "app/src/main/AndroidManifest.xml"
m = manifest.read_text()
if m.count("iCE Onhand 3.0.227") != 1:
    raise SystemExit("3.0.227 manifest label missing or ambiguous")
manifest.write_text(m.replace("iCE Onhand 3.0.227", "iCE Onhand 3.0.228", 1))

main = root / "app/src/main/java/com/iceinventory/onhand/MainActivity.java"
s = main.read_text()
old = 'Button imp=button("↓ START COUNT / IMPORT",1);'
new = ('Button imp=button("NEW INVENTORY\\n/ IMPORT",1);'
       'imp.setTextSize(12f);imp.setGravity(Gravity.CENTER);'
       'imp.setMaxLines(2);imp.setIncludeFontPadding(false);'
       'imp.setPadding(dp(2),0,dp(2),0);'
       'imp.setContentDescription("New inventory or import store file");')
if s.count(old) != 1:
    raise SystemExit("Bottom START COUNT / IMPORT button missing or ambiguous")
s = s.replace(old, new, 1)
if s.count("Onhand Inventory 3.0.227") != 1:
    raise SystemExit("3.0.227 visible version missing or ambiguous")
s = s.replace("Onhand Inventory 3.0.227", "Onhand Inventory 3.0.228", 1)
main.write_text(s)

checks = {
    "version": "versionCode 30228" in gradle.read_text(),
    "manifest": "iCE Onhand 3.0.228" in manifest.read_text(),
    "visible version": "Onhand Inventory 3.0.228" in main.read_text(),
    "button clear on two lines": 'button("NEW INVENTORY\\n/ IMPORT",1)' in main.read_text(),
    "import action preserved": 'imp.setOnClickListener(v->importCsv());' in main.read_text(),
    "button responsive text": "imp.setTextSize(12f)" in main.read_text() and "imp.setMaxLines(2)" in main.read_text(),
    "workflow 3.0.228": ".github/prepare_30228.py" in workflow.read_text() and "3.0.228" in workflow.read_text(),
}
failed = [k for k, passed in checks.items() if not passed]
if failed:
    raise SystemExit("3.0.228 validation failed: " + ", ".join(failed))
print("Prepared OnHand 3.0.228: bottom NEW INVENTORY / IMPORT fits in two lines without changing import behavior.")
