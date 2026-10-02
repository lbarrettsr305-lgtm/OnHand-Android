#!/usr/bin/env python3
from pathlib import Path
import re
import runpy

root = Path(__file__).resolve().parents[1]
runpy.run_path(str(root / ".github" / "prepare_30201.py"), run_name="__main__")

gradle = root / "app" / "build.gradle"
s = gradle.read_text()
if "versionName '3.0.201'" not in s or "versionCode 30201" not in s:
    raise SystemExit("3.0.201 version source not found")
s = s.replace("versionCode 30201", "versionCode 30202", 1)
s = s.replace("versionName '3.0.201'", "versionName '3.0.202'", 1)
gradle.write_text(s)

manifest = root / "app" / "src" / "main" / "AndroidManifest.xml"
s = manifest.read_text()
if "iCE Onhand 3.0.201" not in s:
    raise SystemExit("3.0.201 app label not found")
manifest.write_text(s.replace("iCE Onhand 3.0.201", "iCE Onhand 3.0.202", 1))

main = root / "app" / "src" / "main" / "java" / "com" / "iceinventory" / "onhand" / "MainActivity.java"
s = main.read_text()
if "Onhand Inventory 3.0.201" not in s:
    raise SystemExit("3.0.201 screen version not found")
s = s.replace("Onhand Inventory 3.0.201", "Onhand Inventory 3.0.202", 1)

old_new = '''newMonthly.setTextSize(15);
            newMonthly.setOnClickListener'''
new_new = '''newMonthly.setTextSize(12);
            newMonthly.setSingleLine(true);
            newMonthly.setMaxLines(1);
            newMonthly.setIncludeFontPadding(false);
            newMonthly.setPadding(0,0,0,0);
            newMonthly.setOnClickListener'''
if s.count(old_new) != 1:
    raise SystemExit("Start New Petrosoft button style target missing or ambiguous")
s = s.replace(old_new, new_new, 1)

lines = s.splitlines()
monthly_matches = [i for i, line in enumerate(lines) if line.strip().startswith("Button monthly=button(") and "monthlyWorkflowMode?" in line]
if len(monthly_matches) != 1:
    raise SystemExit("Resume Petrosoft button target missing or ambiguous")
i = monthly_matches[0]
lines[i+1:i+1] = [
    "        monthly.setTextSize(12);",
    "        monthly.setSingleLine(true);",
    "        monthly.setMaxLines(1);",
    "        monthly.setIncludeFontPadding(false);",
    "        monthly.setPadding(dp(4),0,dp(4),0);",
]
s = "\\n".join(lines) + "\\n"
main.write_text(s)

checks = {
    "app version": "versionName '3.0.202'" in gradle.read_text(),
    "start button stays full-width while fitting on one line": "newMonthly.setTextSize(12);" in main.read_text() and "newMonthly.setSingleLine(true);" in main.read_text(),
    "resume button stays full-width while fitting on one line": "monthly.setTextSize(12);" in main.read_text() and "monthly.setSingleLine(true);" in main.read_text(),
    "settings remains corrected": 'button("⚙ SETTINGS",0)' in main.read_text(),
}
failed = [name for name, ok in checks.items() if not ok]
if failed:
    raise SystemExit("3.0.202 verification failed: " + ", ".join(failed))
print("Prepared iCE Onhand 3.0.202: full Petrosoft button labels fit on one line")
