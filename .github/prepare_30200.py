#!/usr/bin/env python3
from pathlib import Path
import runpy

root = Path(__file__).resolve().parents[1]
runpy.run_path(str(root / ".github" / "prepare_30199.py"), run_name="__main__")

gradle = root / "app" / "build.gradle"
s = gradle.read_text()
if "versionName '3.0.199'" not in s or "versionCode 30199" not in s:
    raise SystemExit("3.0.199 version source not found")
s = s.replace("versionCode 30199", "versionCode 30200", 1)
s = s.replace("versionName '3.0.199'", "versionName '3.0.200'", 1)
gradle.write_text(s)

manifest = root / "app" / "src" / "main" / "AndroidManifest.xml"
s = manifest.read_text()
if "iCE Onhand 3.0.199" not in s:
    raise SystemExit("3.0.199 app label not found")
manifest.write_text(s.replace("iCE Onhand 3.0.199", "iCE Onhand 3.0.200", 1))

main = root / "app" / "src" / "main" / "java" / "com" / "iceinventory" / "onhand" / "MainActivity.java"
s = main.read_text()
if "Onhand Inventory 3.0.199" not in s:
    raise SystemExit("3.0.199 screen version not found")
s = s.replace("Onhand Inventory 3.0.199", "Onhand Inventory 3.0.200", 1)

old = 'options.setPadding(dp(2),0,dp(2),0);'
new = 'options.setIncludeFontPadding(false);\n            options.setPadding(dp(2),0,dp(2),dp(8));'
if s.count(old) != 1:
    raise SystemExit("Settings button padding target missing or ambiguous")
s = s.replace(old, new, 1)
main.write_text(s)

checks = {
    "app version": "versionName '3.0.200'" in gradle.read_text(),
    "manifest version": "iCE Onhand 3.0.200" in manifest.read_text(),
    "settings content moved upward": "options.setIncludeFontPadding(false);" in main.read_text() and "options.setPadding(dp(2),0,dp(2),dp(8));" in main.read_text(),
    "current location banner retained": "currentLocationBanner.setMaxLines(2)" in main.read_text() and "currentLocationBanner.setBackgroundColor(green())" in main.read_text(),
    "settings label retained": 'button("⚙\\nSETTINGS",0)' in main.read_text(),
}
failed = [name for name, ok in checks.items() if not ok]
if failed:
    raise SystemExit("3.0.200 verification failed: " + ", ".join(failed))
print("Prepared iCE Onhand 3.0.200: settings text lifted clear of the gear button edge")
