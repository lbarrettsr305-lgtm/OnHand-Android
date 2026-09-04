from pathlib import Path
import runpy

# Preserve every working 3.0.65 feature first.
runpy.run_path('.github/prepare_3065.py', run_name='__main__')

p = Path('app/src/main/java/com/iceinventory/onhand/MainActivity.java')
s = p.read_text()

# Advance the visible version number.
s = s.replace('TextView app=text("Onhand Inventory 3.0.65",19,Color.WHITE,true);',
              'TextView app=text("Onhand Inventory 3.0.66",19,Color.WHITE,true);', 1)

# Replace the temporary vector logo with the saved enhanced iCE Inventory logo.
s = s.replace('logo.setImageResource(R.drawable.ice_onhand_logo_3064);',
              'logo.setImageResource(R.drawable.ice_inventory_logo_3066);', 1)
if 'R.drawable.ice_inventory_logo_3066' not in s:
    raise SystemExit('3.0.66 target missing: in-app logo')

p.write_text(s)

# Advance Android package version so 3.0.66 installs over 3.0.65.
p = Path('app/build.gradle')
s = p.read_text()
s = s.replace('versionCode 30065', 'versionCode 30066', 1)
s = s.replace("versionName '3.0.65'", "versionName '3.0.66'", 1)
if 'versionCode 30066' not in s or "versionName '3.0.66'" not in s:
    raise SystemExit('3.0.66 target missing: Gradle version')
p.write_text(s)

# Use the enhanced logo for the launcher/app-list icon and keep label synchronized.
p = Path('app/src/main/AndroidManifest.xml')
s = p.read_text()
s = s.replace('android:label="iCE Onhand 3.0.65"', 'android:label="iCE Onhand 3.0.66"', 1)
s = s.replace('android:icon="@drawable/ice_onhand_logo_3064"',
              'android:icon="@drawable/ice_inventory_logo_3066"', 1)
if '@drawable/ice_inventory_logo_3066' not in s:
    raise SystemExit('3.0.66 target missing: launcher logo')
p.write_text(s)

print('Prepared iCE Onhand 3.0.66: enhanced saved iCE Inventory logo')
