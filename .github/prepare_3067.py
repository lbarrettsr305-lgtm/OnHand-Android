from pathlib import Path
import runpy

# Preserve every working 3.0.66 feature first.
runpy.run_path('.github/prepare_3066.py', run_name='__main__')

p = Path('app/src/main/java/com/iceinventory/onhand/MainActivity.java')
s = p.read_text()

# Advance the visible version number.
s = s.replace('TextView app=text("Onhand Inventory 3.0.66",19,Color.WHITE,true);',
              'TextView app=text("Onhand Inventory 3.0.67",19,Color.WHITE,true);', 1)

# Make the enhanced iCE Inventory logo large enough to be clearly visible in the header.
old = 'LinearLayout.LayoutParams lpLogo=new LinearLayout.LayoutParams(dp(68),dp(68));'
new = 'LinearLayout.LayoutParams lpLogo=new LinearLayout.LayoutParams(dp(96),dp(96));'
if old not in s:
    raise SystemExit('3.0.67 target missing: header logo size')
s = s.replace(old, new, 1)

p.write_text(s)

# Advance Android package version so 3.0.67 installs over 3.0.66.
p = Path('app/build.gradle')
s = p.read_text()
s = s.replace('versionCode 30066', 'versionCode 30067', 1)
s = s.replace("versionName '3.0.66'", "versionName '3.0.67'", 1)
if 'versionCode 30067' not in s or "versionName '3.0.67'" not in s:
    raise SystemExit('3.0.67 target missing: Gradle version')
p.write_text(s)

# Use proper launcher/adaptive icon resources and keep the app label synchronized.
p = Path('app/src/main/AndroidManifest.xml')
s = p.read_text()
s = s.replace('android:label="iCE Onhand 3.0.66"', 'android:label="iCE Onhand 3.0.67"', 1)
s = s.replace('android:icon="@drawable/ice_inventory_logo_3066"',
              'android:icon="@mipmap/ice_launcher"\n        android:roundIcon="@mipmap/ice_launcher_round"', 1)
if '@mipmap/ice_launcher' not in s or '@mipmap/ice_launcher_round' not in s:
    raise SystemExit('3.0.67 target missing: launcher icon resources')
p.write_text(s)

print('Prepared iCE Onhand 3.0.67: corrected launcher logo + larger in-app logo')
