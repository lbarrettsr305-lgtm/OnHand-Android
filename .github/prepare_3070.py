from pathlib import Path
import runpy, base64

# Preserve every working 3.0.69 feature first, including the proven scanner,
# Internet Items With Pictures export, Options, Sort, passcode and Add Count layout.
runpy.run_path('.github/prepare_3069.py', run_name='__main__')

# Recreate the exact approved glossy green/gold scanner-figure logo from a
# verified base64 payload. This avoids the corrupt WEBP that caused the blank
# header in 3.0.69.
payload = Path('.github/assets/ice_inventory_master_3070.b64').read_text().strip()
logo_bytes = base64.b64decode(payload, validate=True)
if len(logo_bytes) < 5000 or not logo_bytes.startswith(b'RIFF') or b'WEBP' not in logo_bytes[:16]:
    raise SystemExit('3.0.70 verified logo payload is invalid')
logo_path = Path('app/src/main/res/drawable/ice_inventory_master_3070.webp')
logo_path.write_bytes(logo_bytes)

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

# Point every generated in-app reference at the verified logo. Preserve the
# existing 96dp header dimensions from 3.0.67+ so no working layout is changed.
s = s.replace('R.drawable.ice_inventory_master_3069', 'R.drawable.ice_inventory_master_3070')
if 'R.drawable.ice_inventory_master_3069' in s:
    raise SystemExit('3.0.70 old corrupt header logo reference still present')
if 'LinearLayout.LayoutParams lpLogo=new LinearLayout.LayoutParams(dp(96),dp(96));' not in s:
    raise SystemExit('3.0.70 expected preserved header logo size missing')
p.write_text(s)

# Advance Android version only; scanner/count behavior is otherwise unchanged.
p = Path('app/build.gradle')
s = p.read_text().replace('versionCode 30069','versionCode 30070',1).replace("versionName '3.0.69'","versionName '3.0.70'",1)
if 'versionCode 30070' not in s or "versionName '3.0.70'" not in s:
    raise SystemExit('3.0.70 target missing: Gradle version')
p.write_text(s)

# Use the same verified image for normal and round launcher icon references.
p = Path('app/src/main/AndroidManifest.xml')
s = p.read_text().replace('android:label="iCE Onhand 3.0.69"','android:label="iCE Onhand 3.0.70"',1)
s = s.replace('@drawable/ice_inventory_master_3069', '@drawable/ice_inventory_master_3070')
if '@drawable/ice_inventory_master_3069' in s:
    raise SystemExit('3.0.70 old corrupt launcher logo reference still present')
p.write_text(s)

# Remove the generated corrupt 3.0.69 copy so it cannot be selected accidentally.
bad = Path('app/src/main/res/drawable/ice_inventory_master_3069.webp')
if bad.exists():
    bad.unlink()

print('Prepared iCE Onhand 3.0.70: verified glossy logo + preserved 3.0.69 scan/count behavior')
