#!/usr/bin/env python3
from pathlib import Path
import runpy

root = Path(__file__).resolve().parents[1]
runpy.run_path(str(root / ".github" / "prepare_30198.py"), run_name="__main__")

gradle = root / "app" / "build.gradle"
s = gradle.read_text()
if "versionName '3.0.198'" not in s or "versionCode 30198" not in s:
    raise SystemExit("3.0.198 version source not found")
s = s.replace("versionCode 30198", "versionCode 30199", 1)
s = s.replace("versionName '3.0.198'", "versionName '3.0.199'", 1)
gradle.write_text(s)

manifest = root / "app" / "src" / "main" / "AndroidManifest.xml"
s = manifest.read_text()
if "iCE Onhand 3.0.198" not in s:
    raise SystemExit("3.0.198 app label not found")
manifest.write_text(s.replace("iCE Onhand 3.0.198", "iCE Onhand 3.0.199", 1))

main = root / "app" / "src" / "main" / "java" / "com" / "iceinventory" / "onhand" / "MainActivity.java"
s = main.read_text()
if "Onhand Inventory 3.0.198" not in s:
    raise SystemExit("3.0.198 screen version not found")
s = s.replace("Onhand Inventory 3.0.198", "Onhand Inventory 3.0.199", 1)

old_banner = 'currentLocationBanner=text("CURRENT LOCATION: NOT SET",17,gold(),true);\n        currentLocationBanner.setGravity(Gravity.CENTER);\n        currentLocationBanner.setPadding(dp(8),dp(7),dp(8),dp(7));\n        currentLocationBanner.setBackgroundColor(darkGreen());\n        currentLocationBanner.setOnClickListener(v->showLocationStep());\n        root.addView(currentLocationBanner,new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT,dp(44)));'
new_banner = 'currentLocationBanner=text("CURRENT LOCATION\\nNOT SET",18,Color.WHITE,true);\n        currentLocationBanner.setMaxLines(2);\n        currentLocationBanner.setGravity(Gravity.CENTER);\n        currentLocationBanner.setPadding(dp(8),dp(4),dp(8),dp(4));\n        currentLocationBanner.setBackgroundColor(green());\n        root.addView(currentLocationBanner,new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT,dp(58)));'
if s.count(old_banner) != 1:
    raise SystemExit("Current location banner layout target missing or ambiguous")
s = s.replace(old_banner, new_banner, 1)

old_refresh = 'if(currentLocationBanner!=null)currentLocationBanner.setText("CURRENT LOCATION: "+\n                (confirmedLocationSession==sessionId&&!confirmedLocation.isEmpty()?confirmedLocation.toUpperCase(java.util.Locale.US):"NOT SET"));'
new_refresh = 'if(currentLocationBanner!=null)currentLocationBanner.setText("CURRENT LOCATION\\n"+\n                (confirmedLocationSession==sessionId&&!confirmedLocation.isEmpty()?confirmedLocation.toUpperCase(java.util.Locale.US):"NOT SET"));'
if s.count(old_refresh) != 1:
    raise SystemExit("Current location text refresh target missing or ambiguous")
s = s.replace(old_refresh, new_refresh, 1)

checks = {
    "app version": "versionName '3.0.199'" in gradle.read_text(),
    "manifest version": "iCE Onhand 3.0.199" in manifest.read_text(),
    "large two-line current location banner": 'text("CURRENT LOCATION\\nNOT SET",18,Color.WHITE,true)' in main.read_text() and 'dp(58)' in main.read_text(),
    "selected location shown on second line": 'setText("CURRENT LOCATION\\n"+' in main.read_text(),
    "settings label retained": 'button("⚙\\nSETTINGS",0)' in main.read_text(),
}
failed = [name for name, ok in checks.items() if not ok]
if failed:
    raise SystemExit("3.0.199 verification failed: " + ", ".join(failed))
print("Prepared iCE Onhand 3.0.199: prominent two-line current location banner")
