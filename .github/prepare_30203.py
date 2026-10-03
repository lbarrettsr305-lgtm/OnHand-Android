#!/usr/bin/env python3
from pathlib import Path
import runpy

root = Path(__file__).resolve().parents[1]
runpy.run_path(str(root / ".github" / "prepare_30202.py"), run_name="__main__")

gradle = root / "app" / "build.gradle"
s = gradle.read_text()
if "versionName '3.0.202'" not in s or "versionCode 30202" not in s:
    raise SystemExit("3.0.202 version source not found")
s = s.replace("versionCode 30202", "versionCode 30203", 1)
s = s.replace("versionName '3.0.202'", "versionName '3.0.203'", 1)
gradle.write_text(s)

manifest = root / "app" / "src" / "main" / "AndroidManifest.xml"
s = manifest.read_text()
if "iCE Onhand 3.0.202" not in s:
    raise SystemExit("3.0.202 app label not found")
manifest.write_text(s.replace("iCE Onhand 3.0.202", "iCE Onhand 3.0.203", 1))

main = root / "app" / "src" / "main" / "java" / "com" / "iceinventory" / "onhand" / "MainActivity.java"
s = main.read_text()
if "Onhand Inventory 3.0.202" not in s:
    raise SystemExit("3.0.202 screen version not found")
s = s.replace("Onhand Inventory 3.0.202", "Onhand Inventory 3.0.203", 1)
old = "↩ RESUME PETROSOFT MONTHLY INVENTORY"
if s.count(old) != 1:
    raise SystemExit("Petrosoft resume label target missing or ambiguous")
s = s.replace(old, "↩ RESUME PETROSOFT MONTHLY", 1)
main.write_text(s)

app = root / "app" / "src" / "main" / "java" / "com" / "iceinventory" / "onhand" / "OnHandApplication.java"
s = app.read_text()
old = "params.topMargin=dp(activity,4);params.rightMargin=dp(activity,5);"
if s.count(old) != 1:
    raise SystemExit("Floating Help button position target missing or ambiguous")
s = s.replace(old, "params.topMargin=dp(activity,24);params.rightMargin=dp(activity,5);", 1)
app.write_text(s)

checks = {
    "app version": "versionName '3.0.203'" in gradle.read_text(),
    "short Petrosoft resume label": "↩ RESUME PETROSOFT MONTHLY" in main.read_text() and "↩ RESUME PETROSOFT MONTHLY INVENTORY" not in main.read_text(),
    "Help lowered below status bar": "params.topMargin=dp(activity,24);" in app.read_text(),
    "Settings remains clear": 'button("⚙ SETTINGS",0)' in main.read_text(),
}
failed = [name for name, ok in checks.items() if not ok]
if failed:
    raise SystemExit("3.0.203 verification failed: " + ", ".join(failed))
print("Prepared iCE Onhand 3.0.203: lowered Help shortcut and shortened Petrosoft resume label")
