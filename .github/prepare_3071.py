from pathlib import Path
import runpy

# Preserve every working 3.0.70 feature first, including the verified glossy logo,
# scanner/count behavior, Cases multiplication logic, exports, Options and Sort.
runpy.run_path('.github/prepare_3070.py', run_name='__main__')

# --- Quantity/Cases screen: never allow the Android/Samsung soft keyboard to
# cover the calculator. This screen already has its own numeric keypad. ---
p = Path('app/src/main/java/com/iceinventory/onhand/QuantityActivity.java')
s = p.read_text()

if 'import android.content.Context;' not in s:
    s = s.replace('import android.content.Intent;\n', 'import android.content.Intent;\nimport android.content.Context;\n', 1)
if 'import android.view.WindowManager;' not in s:
    s = s.replace('import android.view.ViewGroup;\n', 'import android.view.ViewGroup;\nimport android.view.WindowManager;\nimport android.view.inputmethod.InputMethodManager;\n', 1)

old = '''    @Override public void onCreate(Bundle savedInstanceState){\n        super.onCreate(savedInstanceState);\n        buildUi();\n    }\n'''
new = '''    @Override public void onCreate(Bundle savedInstanceState){\n        super.onCreate(savedInstanceState);\n        getWindow().setSoftInputMode(WindowManager.LayoutParams.SOFT_INPUT_STATE_ALWAYS_HIDDEN | WindowManager.LayoutParams.SOFT_INPUT_ADJUST_RESIZE);\n        buildUi();\n        hideKeyboard();\n    }\n\n    @Override protected void onResume(){\n        super.onResume();\n        hideKeyboard();\n    }\n'''
if old not in s:
    raise SystemExit('3.0.71 target missing: QuantityActivity onCreate')
s = s.replace(old, new, 1)

old_focus = '''        perUnit.setOnFocusChangeListener((v,has)->{if(has)active=perUnit;});\n        cases.setOnFocusChangeListener((v,has)->{if(has)active=cases;});\n'''
new_focus = '''        perUnit.setOnFocusChangeListener((v,has)->{if(has){active=perUnit;hideKeyboard();}});\n        cases.setOnFocusChangeListener((v,has)->{if(has){active=cases;hideKeyboard();}});\n'''
if old_focus not in s:
    raise SystemExit('3.0.71 target missing: QuantityActivity focus handlers')
s = s.replace(old_focus, new_focus, 1)

old_content = '        setContentView(outer);\n    }\n\n    private int value(EditText e){\n'
new_content = '''        setContentView(outer);\n        outer.postDelayed(this::hideKeyboard, 120);\n    }\n\n    private void hideKeyboard(){\n        try{\n            InputMethodManager imm=(InputMethodManager)getSystemService(Context.INPUT_METHOD_SERVICE);\n            View v=getWindow().getDecorView();\n            if(imm!=null && v!=null)imm.hideSoftInputFromWindow(v.getWindowToken(),0);\n        }catch(Exception ignored){}\n    }\n\n    private int value(EditText e){\n'''
if old_content not in s:
    raise SystemExit('3.0.71 target missing: QuantityActivity setContentView')
s = s.replace(old_content, new_content, 1)

# Keep the per-field soft-keyboard suppression explicit even if another future
# patch changes focus behavior.
if s.count('setShowSoftInputOnFocus(false);') < 2:
    raise SystemExit('3.0.71 expected soft-input suppression missing from Cases fields')
p.write_text(s)

# Advance visible app version.
p = Path('app/src/main/java/com/iceinventory/onhand/MainActivity.java')
s = p.read_text()
oldv = 'TextView app=text("Onhand Inventory 3.0.70",19,Color.WHITE,true);'
newv = 'TextView app=text("Onhand Inventory 3.0.71",19,Color.WHITE,true);'
if oldv not in s:
    raise SystemExit('3.0.71 target missing: visible version')
s = s.replace(oldv, newv, 1)
p.write_text(s)

# Advance Android package version so it installs over 3.0.70.
p = Path('app/build.gradle')
s = p.read_text().replace('versionCode 30070','versionCode 30071',1).replace("versionName '3.0.70'","versionName '3.0.71'",1)
if 'versionCode 30071' not in s or "versionName '3.0.71'" not in s:
    raise SystemExit('3.0.71 target missing: Gradle version')
p.write_text(s)

# Also declare the QuantityActivity keyboard policy at the Android activity level.
p = Path('app/src/main/AndroidManifest.xml')
s = p.read_text()
s = s.replace('android:label="iCE Onhand 3.0.70"', 'android:label="iCE Onhand 3.0.71"', 1)
old_activity = '''        <activity\n            android:name=".QuantityActivity"\n            android:exported="false"\n            android:screenOrientation="unspecified" />'''
new_activity = '''        <activity\n            android:name=".QuantityActivity"\n            android:exported="false"\n            android:screenOrientation="unspecified"\n            android:windowSoftInputMode="stateAlwaysHidden|adjustResize" />'''
if old_activity not in s:
    raise SystemExit('3.0.71 target missing: QuantityActivity manifest entry')
s = s.replace(old_activity, new_activity, 1)
p.write_text(s)

print('Prepared iCE Onhand 3.0.71: Cases screen keeps Samsung keyboard hidden; custom calculator remains visible')
