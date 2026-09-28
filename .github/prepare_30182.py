#!/usr/bin/env python3
from pathlib import Path
import runpy

root = Path(__file__).resolve().parents[1]
runpy.run_path(str(root / ".github" / "prepare_30181.py"), run_name="__main__")

gradle = root / "app" / "build.gradle"
s = gradle.read_text()
s = s.replace("versionCode 30181", "versionCode 30182")
s = s.replace("versionName '3.0.181'", "versionName '3.0.182'")
gradle.write_text(s)

manifest = root / "app" / "src" / "main" / "AndroidManifest.xml"
s_manifest = manifest.read_text().replace("iCE Onhand 3.0.181", "iCE Onhand 3.0.182")
manifest.write_text(s_manifest)

main = root / "app" / "src" / "main" / "java" / "com" / "iceinventory" / "onhand" / "MainActivity.java"
s_main = main.read_text().replace("Onhand Inventory 3.0.181", "Onhand Inventory 3.0.182")
main.write_text(s_main)

monthly = root / "app" / "src" / "main" / "java" / "com" / "iceinventory" / "onhand" / "MonthlyInventoryActivity.java"
s = monthly.read_text()
old = 'adjustCount=button("POST-COUNT CORRECTIONS / ADDONS");adjustCount.setSingleLine(false);adjustCount.setMaxLines(2);adjustCount.setTypeface(android.graphics.Typeface.DEFAULT,android.graphics.Typeface.BOLD);'
new = 'adjustCount=button("POST-COUNT\\nCORRECTIONS / ADDONS");adjustCount.setSingleLine(false);adjustCount.setMaxLines(2);adjustCount.setTextSize(16);adjustCount.setMinHeight(dp(86));adjustCount.setMinimumHeight(dp(86));adjustCount.setPadding(dp(8),dp(6),dp(8),dp(6));adjustCount.setTypeface(android.graphics.Typeface.DEFAULT,android.graphics.Typeface.BOLD);'
if old not in s:
    raise SystemExit("Post-count button source not found")
s = s.replace(old, new, 1)
layout_old = "root.addView(adjustCount,params(54));"
if s.count(layout_old) != 1:
    raise SystemExit("Post-count button layout source not found")
s = s.replace(layout_old, "root.addView(adjustCount,params(86));", 1)
monthly.write_text(s)

checks = {
    "version": "versionName '3.0.182'" in gradle.read_text(),
    "manifest": "iCE Onhand 3.0.182" in s_manifest,
    "header": "Onhand Inventory 3.0.182" in s_main,
    "two-line label": 'POST-COUNT\\nCORRECTIONS / ADDONS' in s,
    "button height": 'adjustCount.setMinHeight(dp(86))' in s,
    "layout height": 'root.addView(adjustCount,params(86))' in s,
}
failed = [name for name, ok in checks.items() if not ok]
if failed:
    raise SystemExit("3.0.182 verification failed: " + ", ".join(failed))
print("Prepared iCE OnHand 3.0.182: readable two-line post-count button")
