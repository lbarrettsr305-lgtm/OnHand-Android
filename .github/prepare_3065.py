from pathlib import Path
import runpy

# Preserve every working 3.0.64 feature first.
runpy.run_path('.github/prepare_3064.py', run_name='__main__')

p = Path('app/src/main/java/com/iceinventory/onhand/MainActivity.java')
s = p.read_text()

# Advance the visible version number.
s = s.replace('TextView app=text("Onhand Inventory 3.0.64",19,Color.WHITE,true);',
              'TextView app=text("Onhand Inventory 3.0.65",19,Color.WHITE,true);', 1)

# The current Unknown Barcode Behavior value wraps onto a second line on the
# Samsung test phone. Give that control enough height and make the current
# selection explicit so the lower line is never hidden behind the Done bar.
old = '''        Button unknown=button("Unknown Barcode Behavior: "+friendlyUnknownMode(),0);\n        unknown.setOnClickListener(v->showUnknownBarcodeMode());\n        box.addView(unknown,new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT,dp(50)));\n'''
new = '''        Button unknown=button("Unknown Barcode Behavior\\nCurrent: "+friendlyUnknownMode(),0);\n        unknown.setTextSize(13);\n        unknown.setSingleLine(false);\n        unknown.setGravity(Gravity.CENTER);\n        unknown.setOnClickListener(v->showUnknownBarcodeMode());\n        box.addView(unknown,new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT,dp(72)));\n        View optionsBottomSpacer=new View(this);\n        box.addView(optionsBottomSpacer,new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT,dp(16)));\n'''
if old not in s:
    raise SystemExit('3.0.65 target missing: Unknown Barcode Behavior button')
s = s.replace(old, new, 1)

# Keep a little extra scroll room below the final control so the whole button
# can be moved above the fixed Done action on shorter displays.
old = '''        optionsScroll.setVerticalScrollBarEnabled(true);\n        optionsScroll.addView(box,new ScrollView.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT,ViewGroup.LayoutParams.WRAP_CONTENT));\n'''
new = '''        optionsScroll.setVerticalScrollBarEnabled(true);\n        optionsScroll.setPadding(0,0,0,dp(10));\n        optionsScroll.addView(box,new ScrollView.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT,ViewGroup.LayoutParams.WRAP_CONTENT));\n'''
if old not in s:
    raise SystemExit('3.0.65 target missing: Options ScrollView')
s = s.replace(old, new, 1)

p.write_text(s)

# Advance Android's package version so 3.0.65 installs as an in-place update.
p = Path('app/build.gradle')
s = p.read_text()
s = s.replace('versionCode 30064', 'versionCode 30065', 1)
s = s.replace("versionName '3.0.64'", "versionName '3.0.65'", 1)
if 'versionCode 30065' not in s or "versionName '3.0.65'" not in s:
    raise SystemExit('3.0.65 target missing: Gradle version')
p.write_text(s)

# Keep launcher label synchronized with the in-app version after 3.0.64 prep.
p = Path('app/src/main/AndroidManifest.xml')
s = p.read_text()
s = s.replace('android:label="iCE Onhand 3.0.64"', 'android:label="iCE Onhand 3.0.65"', 1)
p.write_text(s)

print('Prepared iCE Onhand 3.0.65: fully visible Unknown Barcode Behavior control')
