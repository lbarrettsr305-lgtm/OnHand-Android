from pathlib import Path
import runpy

# Preserve every approved 3.0.77 feature first.
runpy.run_path('.github/prepare_3077.py', run_name='__main__')

p=Path('app/src/main/java/com/iceinventory/onhand/QuantityActivity.java')
s=p.read_text()

def rep(old,new,label):
    global s
    if old not in s:
        raise SystemExit('3.0.78 target missing: '+label)
    s=s.replace(old,new,1)

# Keep an explicit Cases-entry mode. This makes the app keypad write directly to
# Number of Cases rather than depending on Android/Samsung focus behavior.
rep('''    private Button addButton;\n    private int total;\n''',
'''    private Button addButton;\n    private ScrollView scroll;\n    private boolean enteringCases=false;\n    private int total;\n''','Cases input state')

rep('''        ScrollView scroll=new ScrollView(this);\n''',
'''        scroll=new ScrollView(this);\n''','scroll instance')

# The large multiplication symbol remains useful as an explicit Cases selector,
# but the fix below does not rely on it being tapped.
rep('''        TextView times=text("×",30,Color.BLACK,true);times.setGravity(Gravity.CENTER);\n''',
'''        TextView times=text("×",30,Color.BLACK,true);times.setGravity(Gravity.CENTER);\n        times.setClickable(true);\n        times.setOnClickListener(v->selectCasesInput());\n''','multiply selector')

# 3.0.75 already shortened the keypad and changed this padding. Raise the keypad
# much higher by placing it immediately under the Qty/Cases fields, before Total
# and ADD COUNT. Keep enough bottom space for Samsung navigation controls.
rep('''        keypad.setPadding(0,dp(4),0,dp(12));\n''',
'''        keypad.setPadding(0,dp(2),0,dp(4));\n''','keypad padding')
rep('''        body.addView(keypad);\n''',
'''        body.addView(keypad,body.indexOfChild(totalRow));\n''','raise keypad')

# Each key sends its known value directly. Numeric keys are routed by the
# enteringCases flag, so Cases always accepts input even if Android focus moves.
old='''            Button b=new Button(this);b.setText(k);b.setAllCaps(false);b.setTextSize(18);b.setTextColor(Color.BLACK);\n            b.setFocusable(false);b.setFocusableInTouchMode(false);\n            b.setOnClickListener(v->pressKey(((Button)v).getText().toString()));\n'''
new='''            Button b=new Button(this);b.setText(k);b.setAllCaps(false);b.setTextSize(18);b.setTextColor(Color.BLACK);\n            b.setFocusable(false);b.setFocusableInTouchMode(false);\n            final String key=k;\n            b.setOnClickListener(v->pressKey(key));\n'''
if old not in s:
    raise SystemExit('3.0.78 target missing: keypad click listener')
s=s.replace(old,new,1)

# Replace the prior focus-only targeting. Tapping either input now explicitly
# switches keypad destination; tapping Cases also scrolls the operand row upward.
old='''        perUnit.setOnFocusChangeListener((v,has)->{if(has){active=perUnit;hideKeyboard();}});\n        perUnit.setOnTouchListener((v,event)->{if(event.getAction()==android.view.MotionEvent.ACTION_DOWN){active=perUnit;perUnit.requestFocus();hideKeyboard();}return false;});\n        perUnit.setOnClickListener(v->{active=perUnit;perUnit.requestFocus();hideKeyboard();});\n        cases.setOnFocusChangeListener((v,has)->{if(has){active=cases;hideKeyboard();scroll.postDelayed(()->scroll.fullScroll(View.FOCUS_DOWN),120);}});\n        cases.setOnTouchListener((v,event)->{if(event.getAction()==android.view.MotionEvent.ACTION_DOWN){active=cases;cases.requestFocus();hideKeyboard();scroll.postDelayed(()->scroll.fullScroll(View.FOCUS_DOWN),120);}return false;});\n        cases.setOnClickListener(v->{active=cases;cases.requestFocus();hideKeyboard();scroll.postDelayed(()->scroll.fullScroll(View.FOCUS_DOWN),120);});\n'''
new='''        perUnit.setOnFocusChangeListener((v,has)->{if(has){enteringCases=false;active=perUnit;hideKeyboard();}});\n        perUnit.setOnTouchListener((v,event)->{if(event.getAction()==android.view.MotionEvent.ACTION_DOWN){selectPerUnitInput();}return false;});\n        perUnit.setOnClickListener(v->selectPerUnitInput());\n        cases.setOnFocusChangeListener((v,has)->{if(has){enteringCases=true;active=cases;hideKeyboard();raiseKeypad();}});\n        cases.setOnTouchListener((v,event)->{if(event.getAction()==android.view.MotionEvent.ACTION_DOWN){selectCasesInput();}return false;});\n        cases.setOnClickListener(v->selectCasesInput());\n'''
if old not in s:
    raise SystemExit('3.0.78 target missing: Cases focus handlers')
s=s.replace(old,new,1)

# The initial target is Quantity per Unit / Case.
rep('''        perUnit.requestFocus();active=perUnit;\n''',
'''        perUnit.requestFocus();active=perUnit;enteringCases=false;\n''','initial input target')

# Add explicit target helpers before pressKey.
marker='''    private void pressKey(String key){\n'''
helpers='''    private void raiseKeypad(){\n        if(scroll==null||cases==null)return;\n        View row=(View)cases.getParent();\n        if(row==null)return;\n        scroll.postDelayed(()->scroll.smoothScrollTo(0,Math.max(0,row.getTop()-dp(6))),50);\n    }\n\n    private void selectPerUnitInput(){\n        enteringCases=false;\n        active=perUnit;\n        perUnit.setShowSoftInputOnFocus(false);\n        perUnit.requestFocus();\n        perUnit.setSelection(perUnit.getText().length());\n        hideKeyboard();\n    }\n\n    private void selectCasesInput(){\n        enteringCases=true;\n        active=cases;\n        cases.setShowSoftInputOnFocus(false);\n        cases.requestFocus();\n        cases.setSelection(cases.getText().length());\n        hideKeyboard();\n        raiseKeypad();\n    }\n\n'''
if marker not in s:
    raise SystemExit('3.0.78 target missing: pressKey marker')
s=s.replace(marker,helpers+marker,1)

# Route every numeric key directly to the intended operand. This is the main
# correction for the reported problem: Cases no longer relies on focus to accept
# digits. × selects Cases; = calculates and returns the result to Count.
old='''    private void pressKey(String key){\n        if(active==null)active=perUnit;\n        if("×".equals(key)){active=cases;cases.requestFocus();cases.setSelection(cases.getText().length());hideKeyboard();return;}\n        if("=".equals(key)){recalc();if(total>0)finishWithQuantity();return;}\n        active.requestFocus();hideKeyboard();\n        String s=active.getText().toString();\n        if("Clear".equals(key)){active.setText("");active.setSelection(0);return;}\n        if("⌫".equals(key)){if(!s.isEmpty())active.setText(s.substring(0,s.length()-1));active.setSelection(active.getText().length());return;}\n        if(s.length()<9)active.setText(s+key);\n        active.setSelection(active.getText().length());\n    }\n'''
new='''    private void pressKey(String key){\n        if("×".equals(key)||"x".equalsIgnoreCase(key)||"*".equals(key)){selectCasesInput();return;}\n        if("=".equals(key)){recalc();if(total>0)finishWithQuantity();return;}\n        EditText target=enteringCases?cases:perUnit;\n        if(target==null)return;\n        active=target;\n        target.setShowSoftInputOnFocus(false);\n        hideKeyboard();\n        String current=target.getText().toString();\n        if("Clear".equals(key)){target.setText("");target.setSelection(0);return;}\n        if("⌫".equals(key)){\n            if(!current.isEmpty())target.setText(current.substring(0,current.length()-1));\n            target.setSelection(target.getText().length());\n            return;\n        }\n        if(("0".equals(key)||"00".equals(key)||"1".equals(key)||"2".equals(key)||"3".equals(key)||"4".equals(key)||"5".equals(key)||"6".equals(key)||"7".equals(key)||"8".equals(key)||"9".equals(key))&&current.length()<9){\n            target.setText(current+key);\n            target.setSelection(target.getText().length());\n        }\n    }\n'''
if old not in s:
    raise SystemExit('3.0.78 target missing: pressKey method')
s=s.replace(old,new,1)
p.write_text(s)

# Advance visible/installable version.
p=Path('app/src/main/java/com/iceinventory/onhand/MainActivity.java')
s=p.read_text()
if 'TextView app=text("Onhand Inventory 3.0.77",19,Color.WHITE,true);' not in s:
    raise SystemExit('3.0.78 target missing: visible version')
s=s.replace('TextView app=text("Onhand Inventory 3.0.77",19,Color.WHITE,true);',
            'TextView app=text("Onhand Inventory 3.0.78",19,Color.WHITE,true);',1)
p.write_text(s)

p=Path('app/build.gradle')
s=p.read_text().replace('versionCode 30077','versionCode 30078',1).replace("versionName '3.0.77'","versionName '3.0.78'",1)
if 'versionCode 30078' not in s or "versionName '3.0.78'" not in s:
    raise SystemExit('3.0.78 target missing: Gradle version')
p.write_text(s)

p=Path('app/src/main/AndroidManifest.xml')
s=p.read_text().replace('android:label="iCE Onhand 3.0.77"','android:label="iCE Onhand 3.0.78"',1)
if 'android:label="iCE Onhand 3.0.78"' not in s:
    raise SystemExit('3.0.78 target missing: manifest version')
p.write_text(s)

print('Prepared iCE Onhand 3.0.78: Cases accepts numeric input directly + keypad raised')
