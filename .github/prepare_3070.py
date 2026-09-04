from pathlib import Path
import runpy

# Preserve every working 3.0.69 feature first, including the proven scanner,
# Internet Items With Pictures export, Options, Sort, passcode and Add Count layout.
runpy.run_path('.github/prepare_3069.py', run_name='__main__')

p = Path('app/src/main/java/com/iceinventory/onhand/MainActivity.java')
s = p.read_text()

def rep(old, new, label):
    global s
    if old not in s:
        raise SystemExit('3.0.70 target missing: ' + label)
    s = s.replace(old, new, 1)

rep('TextView app=text("Onhand Inventory 3.0.69",19,Color.WHITE,true);',
    'TextView app=text("Onhand Inventory 3.0.70",19,Color.WHITE,true);',
    'visible version')

# The 3.0.69 copied WEBP is corrupt on-device. Point the UI at the new verified
# raster asset and make the header area slightly larger so the full approved mark
# remains recognizable without changing scan/count behavior.
s = s.replace('R.drawable.ice_inventory_master_3069', 'R.drawable.ice_inventory_master_3070')
if 'R.drawable.ice_inventory_master_3069' in s:
    raise SystemExit('3.0.70 old corrupt header logo reference still present')
rep('LinearLayout.LayoutParams lpLogo=new LinearLayout.LayoutParams(dp(68),dp(68));',
    'LinearLayout.LayoutParams lpLogo=new LinearLayout.LayoutParams(dp(86),dp(86));',
    'header logo size')
p.write_text(s)

p = Path('app/build.gradle')
s = p.read_text().replace('versionCode 30069','versionCode 30070',1).replace("versionName '3.0.69'","versionName '3.0.70'",1)
if 'versionCode 30070' not in s or "versionName '3.0.70'" not in s:
    raise SystemExit('3.0.70 target missing: Gradle version')
p.write_text(s)

p = Path('app/src/main/AndroidManifest.xml')
s = p.read_text().replace('android:label="iCE Onhand 3.0.69"','android:label="iCE Onhand 3.0.70"',1)
s = s.replace('@drawable/ice_inventory_master_3069', '@drawable/ice_inventory_master_3070')
if '@drawable/ice_inventory_master_3069' in s:
    raise SystemExit('3.0.70 old corrupt launcher logo reference still present')
p.write_text(s)

# Remove the generated corrupt 3.0.69 copy so it cannot be used accidentally.
bad = Path('app/src/main/res/drawable/ice_inventory_master_3069.webp')
if bad.exists():
    bad.unlink()

print('Prepared iCE Onhand 3.0.70: verified glossy raster logo + preserved 3.0.69 behavior')
