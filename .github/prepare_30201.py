#!/usr/bin/env python3
from pathlib import Path
import runpy

root = Path(__file__).resolve().parents[1]
runpy.run_path(str(root / ".github" / "prepare_30200.py"), run_name="__main__")

gradle = root / "app" / "build.gradle"
s = gradle.read_text()
if "versionName '3.0.200'" not in s or "versionCode 30200" not in s:
    raise SystemExit("3.0.200 version source not found")
s = s.replace("versionCode 30200", "versionCode 30201", 1)
s = s.replace("versionName '3.0.200'", "versionName '3.0.201'", 1)
gradle.write_text(s)

manifest = root / "app" / "src" / "main" / "AndroidManifest.xml"
s = manifest.read_text()
if "iCE Onhand 3.0.200" not in s:
    raise SystemExit("3.0.200 app label not found")
manifest.write_text(s.replace("iCE Onhand 3.0.200", "iCE Onhand 3.0.201", 1))

main = root / "app" / "src" / "main" / "java" / "com" / "iceinventory" / "onhand" / "MainActivity.java"
s = main.read_text()
if "Onhand Inventory 3.0.200" not in s:
    raise SystemExit("3.0.200 screen version not found")
s = s.replace("Onhand Inventory 3.0.200", "Onhand Inventory 3.0.201", 1)

old = '''Button options=button("⚙\\nSETTINGS",0);
            options.setTextSize(12);
            options.setTypeface(Typeface.DEFAULT,Typeface.BOLD);
            options.setSingleLine(false);
            options.setMaxLines(2);
            options.setGravity(Gravity.CENTER);
            options.setIncludeFontPadding(false);
            options.setPadding(dp(2),0,dp(2),dp(8));
            options.setContentDescription("Settings and barcode behavior");
            options.setOnClickListener(v->showOptions());'''
new = '''Button options=button("⚙ SETTINGS",0);
            options.setTextSize(12);
            options.setTypeface(Typeface.DEFAULT,Typeface.BOLD);
            options.setSingleLine(true);
            options.setMaxLines(1);
            options.setGravity(Gravity.CENTER);
            options.setIncludeFontPadding(false);
            options.setPadding(dp(2),0,dp(2),0);
            options.setContentDescription("Settings and barcode behavior");
            options.setOnClickListener(v->showOptions());'''
if s.count(old) != 1:
    raise SystemExit("Settings button layout target missing or ambiguous")
s = s.replace(old, new, 1)
main.write_text(s)

checks = {
    "app version": "versionName '3.0.201'" in gradle.read_text(),
    "manifest version": "iCE Onhand 3.0.201" in manifest.read_text(),
    "single-line full SETTINGS label": 'button("⚙ SETTINGS",0)' in main.read_text() and "options.setMaxLines(1);" in main.read_text(),
    "settings button remains same row height": "sessionBar.addView(options,new LinearLayout.LayoutParams(0,dp(48),1));" in main.read_text(),
}
failed = [name for name, ok in checks.items() if not ok]
if failed:
    raise SystemExit("3.0.201 verification failed: " + ", ".join(failed))
print("Prepared iCE Onhand 3.0.201: single-line SETTINGS button fits the full 48dp home row")
