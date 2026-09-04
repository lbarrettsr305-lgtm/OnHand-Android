from pathlib import Path
import runpy, shutil

# Preserve every working 3.0.68 feature first, including the proven scanner,
# Internet Items With Pictures export, Options, Sort, passcode and export behavior.
runpy.run_path('.github/prepare_3068.py', run_name='__main__')

# Lock the exact glossy green/gold scanner-figure logo that was added for 3.0.66
# into one master resource for 3.0.69. Do not use the circular fallback logo.
logo_src = Path('app/src/main/res/drawable/ice_inventory_logo_3066.webp')
logo_dst = Path('app/src/main/res/drawable/ice_inventory_master_3069.webp')
if not logo_src.exists():
    raise SystemExit('3.0.69 target missing: exact glossy iCE Inventory logo source')
shutil.copyfile(logo_src, logo_dst)

p = Path('app/src/main/java/com/iceinventory/onhand/MainActivity.java')
s = p.read_text()

def rep(old, new, label):
    global s
    if old not in s:
        raise SystemExit('3.0.69 target missing: ' + label)
    s = s.replace(old, new, 1)

# Visible version.
rep('TextView app=text("Onhand Inventory 3.0.68",19,Color.WHITE,true);',
    'TextView app=text("Onhand Inventory 3.0.69",19,Color.WHITE,true);',
    'visible version')

# Force the exact master logo in the app header. Fail the build if the old circular
# logo remains referenced by the generated MainActivity.
if 'R.drawable.ice_onhand_approved' not in s:
    raise SystemExit('3.0.69 target missing: old header logo reference')
s = s.replace('R.drawable.ice_onhand_approved', 'R.drawable.ice_inventory_master_3069')
if 'R.drawable.ice_onhand_approved' in s:
    raise SystemExit('3.0.69 circular header logo reference still present')

# Fix the main Add Count control seen clipped on the Samsung test screen.
old_add = 'Button add=button("＋ Add Count",1);add.setTypeface(Typeface.DEFAULT,Typeface.BOLD);add.setOnClickListener(v->addItem());'
new_add = 'Button add=button("＋ Add Count",1);add.setTypeface(Typeface.DEFAULT,Typeface.BOLD);add.setTextSize(14);add.setSingleLine(true);add.setGravity(Gravity.CENTER);add.setPadding(dp(4),0,dp(4),0);add.setOnClickListener(v->addItem());'
rep(old_add, new_add, 'Add Count button')

# Give Add Count slightly more horizontal room and a little more height while
# preserving the existing Cases and New Location actions.
rep('actionBar.addView(add,new LinearLayout.LayoutParams(0,dp(52),1.35f));',
    'actionBar.addView(add,new LinearLayout.LayoutParams(0,dp(58),1.55f));',
    'Add Count layout')
rep('LinearLayout.LayoutParams ml=new LinearLayout.LayoutParams(0,dp(52),1.0f);ml.setMargins(dp(4),0,dp(4),0);',
    'LinearLayout.LayoutParams ml=new LinearLayout.LayoutParams(0,dp(58),1.0f);ml.setMargins(dp(4),0,dp(4),0);',
    'Cases layout')
rep('actionBar.addView(addLoc,new LinearLayout.LayoutParams(0,dp(52),1.35f));',
    'actionBar.addView(addLoc,new LinearLayout.LayoutParams(0,dp(58),1.25f));',
    'New Location layout')

p.write_text(s)

# Advance Android package version so 3.0.69 installs over 3.0.68.
p = Path('app/build.gradle')
s = p.read_text()
s = s.replace('versionCode 30068', 'versionCode 30069', 1)
s = s.replace("versionName '3.0.68'", "versionName '3.0.69'", 1)
if 'versionCode 30069' not in s or "versionName '3.0.69'" not in s:
    raise SystemExit('3.0.69 target missing: Gradle version')
p.write_text(s)

# Force both Android launcher icon paths to the exact master logo and remove the
# circular fallback from the manifest.
p = Path('app/src/main/AndroidManifest.xml')
s = p.read_text()
s = s.replace('android:label="iCE Onhand 3.0.68"', 'android:label="iCE Onhand 3.0.69"', 1)
s = s.replace('@drawable/ice_onhand_approved', '@drawable/ice_inventory_master_3069')
if '@drawable/ice_inventory_master_3069' not in s:
    raise SystemExit('3.0.69 target missing: launcher master logo')
if '@drawable/ice_onhand_approved' in s or '@mipmap/ice_launcher' in s:
    raise SystemExit('3.0.69 old launcher fallback still present')
p.write_text(s)

print('Prepared iCE Onhand 3.0.69: exact glossy master logo + Add Count layout fix')
