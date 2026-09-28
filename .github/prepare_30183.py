#!/usr/bin/env python3
from pathlib import Path
import runpy

root = Path(__file__).resolve().parents[1]
runpy.run_path(str(root / ".github" / "prepare_30182.py"), run_name="__main__")

gradle = root / "app" / "build.gradle"
s = gradle.read_text().replace("versionCode 30182", "versionCode 30183").replace("versionName '3.0.182'", "versionName '3.0.183'")
gradle.write_text(s)

manifest = root / "app" / "src" / "main" / "AndroidManifest.xml"
manifest.write_text(manifest.read_text().replace("iCE Onhand 3.0.182", "iCE Onhand 3.0.183"))

main = root / "app" / "src" / "main" / "java" / "com" / "iceinventory" / "onhand" / "MainActivity.java"
s = main.read_text().replace("Onhand Inventory 3.0.182", "Onhand Inventory 3.0.183")
old = '''                .setTitle(master?"SELECT MASTER NAME":"SELECT COUNTER NAME")
                .setMessage(master?"Choose the authorized Master using this phone. The selected name is remembered and added to reports.":"Choose the counter using this phone. The selected name is remembered and added to completed-count filenames.")
                .setItems(counters,(d,which)->saveSelectedCounterName(counters[which],continueExport))'''
new = '''                .setTitle(master?"SELECT MASTER NAME — TAP A NAME":"SELECT COUNTER NAME — TAP A NAME")
                .setItems(counters,(d,which)->saveSelectedCounterName(counters[which],continueExport))'''
if s.count(old) != 1:
    raise SystemExit("Counter-name dialog source not found")
s = s.replace(old, new, 1)
main.write_text(s)

checks = {
    "version": "versionName '3.0.183'" in gradle.read_text(),
    "counter title": "SELECT COUNTER NAME — TAP A NAME" in s,
    "master title": "SELECT MASTER NAME — TAP A NAME" in s,
    "approved counters": '"RobertFad","JoseFad","QuselahJ","MataiJ","DelilahW","AdrianB","HailahJ"' in s,
    "protected addition": "verifyMasterPinForNewCounter" in s,
    "conflicting message removed": "Choose the counter using this phone" not in s,
}
failed = [name for name, ok in checks.items() if not ok]
if failed:
    raise SystemExit("3.0.183 verification failed: " + ", ".join(failed))
print("Prepared iCE OnHand 3.0.183: visible scrollable counter and Master name lists")
