from pathlib import Path
import runpy

# Preserve 3.0.62: proven scanner, responsive New Location, scrollable Options,
# and separate Internet Items export.
runpy.run_path('.github/prepare_3062.py', run_name='__main__')

# Make the installed app version obvious both on the launcher/app list and
# inside the app header so there is no guessing which APK is running.
p = Path('app/src/main/AndroidManifest.xml')
s = p.read_text()
old = 'android:label="iCE Onhand Inventory"'
new = 'android:label="iCE Onhand 3.0.63"'
if old not in s:
    raise SystemExit('3.0.63 target missing: manifest app label')
s = s.replace(old, new, 1)
p.write_text(s)

p = Path('app/src/main/java/com/iceinventory/onhand/MainActivity.java')
s = p.read_text()
old = 'TextView app=text("Onhand Inventory",21,Color.WHITE,true);'
new = 'TextView app=text("Onhand Inventory 3.0.63",19,Color.WHITE,true);'
if old not in s:
    raise SystemExit('3.0.63 target missing: main header app name')
s = s.replace(old, new, 1)
p.write_text(s)

print('Prepared iCE Onhand 3.0.63: visible version number in app label and main header')
