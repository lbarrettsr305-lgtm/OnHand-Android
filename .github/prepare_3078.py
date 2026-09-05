from pathlib import Path
import runpy

# Preserve every approved 3.0.77 feature first: scan visibility, exports,
# TXT/Excel headers, logo, import behavior, and existing inventory workflow.
runpy.run_path('.github/prepare_3077.py', run_name='__main__')

p=Path('app/src/main/java/com/iceinventory/onhand/QuantityActivity.java')
s=p.read_text()

def rep(old,new,label):
    global s
    if old not in s: raise SystemExit('3.0.78 target missing: '+label)
    s=s.replace(old,new,1)

# Keep a reference to the Cases screen scroll view so pressing multiply can lift
# the entry row and custom keypad into a comfortable visible position.
rep('''    private Button addButton;\n    private int total;\n''',
'''    private Button addButton;\n    private ScrollView scroll;\n    private int total;\n''','scroll field')

rep('''        ScrollView scroll=new ScrollView(this);\n''',
'''        scroll=new ScrollView(this);\n''','scroll instance field')

# Make the large multiplication sign between the two fields an explicit action,
# not just a label. Tapping it always moves input to Number of Cases.
rep('''        TextView times=text("×",30,Color.BLACK,true);times.setGravity(Gravity.CENTER);\n''',
'''        TextView times=text("×",30,Color.BLACK,true);times.setGravity(Gravity.CENTER);\n        times.setClickable(true);times.setContentDescription("Multiply and enter number of cases");\n        times.setOnClickListener(v->focusCasesForMultiply());\n''','clickable multiply sign')

# Raise the custom keypad: put it directly under the two entry fields/hints,
# before Total and Add Count. Slightly shorten keys so the whole pad stays clear
# of the Samsung navigation area.
rep('''        keypad.setPadding(0,dp(10),0,0);\n''','''        keypad.setPadding(0,dp(4),0,dp(2));\n''','keypad top spacing')
s=s.replace('lp.width=0;lp.height=dp(54);lp.columnSpec=GridLayout.spec(GridLayout.UNDEFINED,1f);',
            'lp.width=0;lp.height=dp(48);lp.columnSpec=GridLayout.spec(GridLayout.UNDEFINED,1f);')
rep('''        body.addView(keypad);\n''',
'''        body.addView(keypad,body.indexOfChild(totalRow));\n''','raise keypad above total')

# Button actions use the known key value directly. This removes any dependency
# on focus quirks or on reading the rendered Button text back from Android.
old='''            Button b=new Button(this);b.setText(k);b.setAllCaps(false);b.setTextSize(18);b.setTextColor(Color.BLACK);\n            b.setFocusable(false);b.setFocusableInTouchMode(false);\n            b.setOnClickListener(v->pressKey(((Button)v).getText().toString()));\n'''
new='''            Button b=new Button(this);b.setText(k);b.setAllCaps(false);b.setTextSize(18);b.setTextColor(Color.BLACK);\n            b.setFocusable(false);b.setFocusableInTouchMode(false);\n            final String key=k;\n            b.setOnClickListener(v->{\n                if("×".equals(key)||"x".equalsIgnoreCase(key)||"*".equals(key)){focusCasesForMultiply();return;}\n                if("=".equals(key)){recalc();if(total>0)finishWithQuantity();return;}\n                pressKey(key);\n            });\n'''
if old not in s: raise SystemExit('3.0.78 target missing: keypad click listener')
s=s.replace(old,new,1)

# Replace the Cases focus handlers. Do not scroll all the way to the bottom;
# instead position the operand row near the top so the raised custom keypad is
# immediately below it.
old='''        perUnit.setOnFocusChangeListener((v,has)->{if(has){active=perUnit;hideKeyboard();}});\n        perUnit.setOnTouchListener((v,event)->{if(event.getAction()==android.view.MotionEvent.ACTION_DOWN){active=perUnit;perUnit.requestFocus();hideKeyboard();}return false;});\n        perUnit.setOnClickListener(v->{active=perUnit;perUnit.requestFocus();hideKeyboard();});\n        cases.setOnFocusChangeListener((v,has)->{if(has){active=cases;hideKeyboard();scroll.postDelayed(()->scroll.fullScroll(View.FOCUS_DOWN),120);}});\n        cases.setOnTouchListener((v,event)->{if(event.getAction()==android.view.MotionEvent.ACTION_DOWN){active=cases;cases.requestFocus();hideKeyboard();scroll.postDelayed(()->scroll.fullScroll(View.FOCUS_DOWN),120);}return false;});\n        cases.setOnClickListener(v->{active=cases;cases.requestFocus();hideKeyboard();scroll.postDelayed(()->scroll.fullScroll(View.FOCUS_DOWN),120);});\n'''
new='''        perUnit.setOnFocusChangeListener((v,has)->{if(has){active=perUnit;hideKeyboard();}});\n        perUnit.setOnTouchListener((v,event)->{if(event.getAction()==android.view.MotionEvent.ACTION_DOWN){active=perUnit;perUnit.requestFocus();hideKeyboard();}return false;});\n        perUnit.setOnClickListener(v->{active=perUnit;perUnit.requestFocus();hideKeyboard();});\n        cases.setOnFocusChangeListener((v,has)->{if(has){active=cases;hideKeyboard();raiseCasesKeypad();}});\n        cases.setOnTouchListener((v,event)->{if(event.getAction()==android.view.MotionEvent.ACTION_DOWN){focusCasesForMultiply();}return false;});\n        cases.setOnClickListener(v->focusCasesForMultiply());\n'''
if old not in s: raise SystemExit('3.0.78 target missing: Cases focus handlers')
s=s.replace(old,new,1)

# Add explicit helpers before pressKey. The multiply action always selects Cases,
# keeps the Samsung keyboard closed, and raises the custom keypad.
marker='''    private void pressKey(String key){\n'''
helpers='''    private void raiseCasesKeypad(){\n        if(scroll==null||cases==null)return;\n        View row=(View)cases.getParent();\n        if(row==null)return;\n        scroll.postDelayed(()->scroll.smoothScrollTo(0,Math.max(0,row.getTop()-dp(8))),60);\n    }\n\n    private void focusCasesForMultiply(){\n        if(cases==null)return;\n        active=cases;\n        cases.setShowSoftInputOnFocus(false);\n        cases.requestFocus();\n        cases.setSelection(cases.getText().length());\n        hideKeyboard();\n        raiseCasesKeypad();\n    }\n\n'''
if marker not in s: raise SystemExit('3.0.78 target missing: pressKey marker')
s=s.replace(marker,helpers+marker,1)

# Keep pressKey itself defensive as well, including alternate multiply characters.
old='''    private void pressKey(String key){\n        if(active==null)active=perUnit;\n        if("×".equals(key)){active=cases;cases.requestFocus();cases.setSelection(cases.getText().length());hideKeyboard();return;}\n        if("=".equals(key)){recalc();if(total>0)finishWithQuantity();return;}\n        active.requestFocus();hideKeyboard();\n        String s=active.getText().toString();\n        if("Clear".equals(key)){active.setText("");active.setSelection(0);return;}\n        if("⌫".equals(key)){if(!s.isEmpty())active.setText(s.substring(0,s.length()-1));active.setSelection(active.getText().length());return;}\n        if(s.length()<9)active.setText(s+key);\n        active.setSelection(active.getText().length());\n    }\n'''
new='''    private void pressKey(String key){\n        if(active==null)active=perUnit;\n        if("×".equals(key)||"x".equalsIgnoreCase(key)||"*".equals(key)){focusCasesForMultiply();return;}\n        if("=".equals(key)){recalc();if(total>0)finishWithQuantity();return;}\n        active.requestFocus();hideKeyboard();\n        String s=active.getText().toString();\n        if("Clear".equals(key)){active.setText("");active.setSelection(0);return;}\n        if("⌫".equals(key)){if(!s.isEmpty())active.setText(s.substring(0,s.length()-1));active.setSelection(active.getText().length());return;}\n        if(s.length()<9)active.setText(s+key);\n        active.setSelection(active.getText().length());\n    }\n'''
if old not in s: raise SystemExit('3.0.78 target missing: pressKey method')
s=s.replace(old,new,1)
p.write_text(s)

# Advance visible/installable version while preserving all other 3.0.77 behavior.
p=Path('app/src/main/java/com/iceinventory/onhand/MainActivity.java')
s=p.read_text()
if 'TextView app=text("Onhand Inventory 3.0.77",19,Color.WHITE,true);' not in s: raise SystemExit('3.0.78 target missing: visible version')
s=s.replace('TextView app=text("Onhand Inventory 3.0.77",19,Color.WHITE,true);',
            'TextView app=text("Onhand Inventory 3.0.78",19,Color.WHITE,true);',1)
p.write_text(s)

p=Path('app/build.gradle')
s=p.read_text().replace('versionCode 30077','versionCode 30078',1).replace("versionName '3.0.77'","versionName '3.0.78'",1)
if 'versionCode 30078' not in s or "versionName '3.0.78'" not in s: raise SystemExit('3.0.78 target missing: Gradle version')
p.write_text(s)

p=Path('app/src/main/AndroidManifest.xml')
s=p.read_text().replace('android:label="iCE Onhand 3.0.77"','android:label="iCE Onhand 3.0.78"',1)
if 'android:label="iCE Onhand 3.0.78"' not in s: raise SystemExit('3.0.78 target missing: manifest version')
p.write_text(s)

print('Prepared iCE Onhand 3.0.78: reliable × to Cases + raised custom keypad')
