#!/usr/bin/env python3
from pathlib import Path
import runpy

root = Path(__file__).resolve().parents[1]
runpy.run_path(str(root / ".github" / "prepare_30197.py"), run_name="__main__")

gradle = root / "app" / "build.gradle"
s = gradle.read_text()
if "versionName '3.0.197'" not in s or "versionCode 30197" not in s:
    raise SystemExit("3.0.197 version source not found")
s = s.replace("versionCode 30197", "versionCode 30198", 1)
s = s.replace("versionName '3.0.197'", "versionName '3.0.198'", 1)
gradle.write_text(s)

manifest = root / "app" / "src" / "main" / "AndroidManifest.xml"
s = manifest.read_text()
if "iCE Onhand 3.0.197" not in s:
    raise SystemExit("3.0.197 app label not found")
manifest.write_text(s.replace("iCE Onhand 3.0.197", "iCE Onhand 3.0.198", 1))

main = root / "app" / "src" / "main" / "java" / "com" / "iceinventory" / "onhand" / "MainActivity.java"
s = main.read_text()
if "Onhand Inventory 3.0.197" not in s:
    raise SystemExit("3.0.197 screen version not found")
s = s.replace("Onhand Inventory 3.0.197", "Onhand Inventory 3.0.198", 1)

old = 'Button options=button("⚙ Options",0);options.setOnClickListener(v->showOptions());'
new = '''Button options=button("⚙\\nSETTINGS",0);
            options.setTextSize(12);
            options.setTypeface(Typeface.DEFAULT,Typeface.BOLD);
            options.setSingleLine(false);
            options.setMaxLines(2);
            options.setGravity(Gravity.CENTER);
            options.setPadding(dp(2),0,dp(2),0);
            options.setContentDescription("Settings and barcode behavior");
            options.setOnClickListener(v->showOptions());'''
if s.count(old) != 1:
    raise SystemExit("Settings button target missing or ambiguous")
s = s.replace(old, new, 1)
main.write_text(s)

checks = {
    "app version": "versionName '3.0.198'" in gradle.read_text(),
    "manifest version": "iCE Onhand 3.0.198" in manifest.read_text(),
    "visible settings label": 'button("⚙\\nSETTINGS",0)' in main.read_text(),
    "accessible settings description": 'setContentDescription("Settings and barcode behavior")' in main.read_text(),
}
failed = [name for name, ok in checks.items() if not ok]
if failed:
    raise SystemExit("3.0.198 verification failed: " + ", ".join(failed))
print("Prepared iCE Onhand 3.0.198: visible SETTINGS label beneath the gear")
