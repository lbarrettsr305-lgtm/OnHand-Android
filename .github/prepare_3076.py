from pathlib import Path
import runpy

# Preserve every working 3.0.75 feature first.
runpy.run_path('.github/prepare_3075.py', run_name='__main__')

# 3.0.76 fixes two scan/count usability problems reported on the Samsung test phone:
# 1) after scanning, keep the Android keyboard hidden so the just-scanned item and prior item remain visible;
# 2) make the Cases second field a reliable custom-keypad target for entries such as 10 x 20 = 200.

p=Path('app/src/main/java/com/iceinventory/onhand/MainActivity.java')
s=p.read_text()

def rep(old,new,label):
    global s
    if old not in s:
        raise SystemExit('3.0.76 target missing: '+label)
    s=s.replace(old,new,1)

# The quantity field remains focused after a scan, but the system keyboard stays closed.
# A deliberate tap on Quantity opens the numeric keyboard.
old='''        qty=new EditText(this);qty.setSingleLine(true);qty.setText("");qty.setTextSize(19);qty.setGravity(Gravity.CENTER);\n        qty.setInputType(InputType.TYPE_CLASS_NUMBER);styleEntry(qty);\n'''
new='''        qty=new EditText(this);qty.setSingleLine(true);qty.setText("");qty.setTextSize(19);qty.setGravity(Gravity.CENTER);\n        qty.setInputType(InputType.TYPE_CLASS_NUMBER);styleEntry(qty);\n        qty.setShowSoftInputOnFocus(false);\n        qty.setOnTouchListener((v,event)->{\n            if(event.getAction()==MotionEvent.ACTION_DOWN){\n                qty.setShowSoftInputOnFocus(true);\n                qty.postDelayed(()->showKeyboard(qty),60);\n            }\n            return false;\n        });\n        qty.setOnFocusChangeListener((v,has)->{if(!has)qty.setShowSoftInputOnFocus(false);});\n'''
rep(old,new,'quantity tap keyboard behavior')

old='''    private void focusQuantity() {\n        qty.requestFocus();\n        qty.setSelection(qty.getText().length());\n        qty.postDelayed(()->showKeyboard(qty),80);\n    }\n'''
new='''    private void focusQuantity() {\n        qty.setShowSoftInputOnFocus(false);\n        qty.requestFocus();\n        qty.setSelection(qty.getText().length());\n        qty.postDelayed(this::hideKeyboard,40);\n        qty.postDelayed(this::hideKeyboard,180);\n    }\n'''
rep(old,new,'keep keyboard closed after scan')

# Always pin the barcode currently being worked on to row 1. The remaining rows retain
# their selected sort order, so the previous scanned/count item stays directly below it.
old='''        sortVisibleRows();\n        SharedPreferences p=prefs();\n'''
new='''        sortVisibleRows();\n        if(lastBarcode!=null&&!lastBarcode.trim().isEmpty()&&visibleRows.size()>1){\n            for(int i=0;i<visibleRows.size();i++){\n                InventoryDb.Row r=visibleRows.get(i);\n                if(r!=null&&lastBarcode.equals(r.barcode)){\n                    if(i>0){visibleRows.remove(i);visibleRows.add(0,r);}\n                    break;\n                }\n            }\n        }\n        SharedPreferences p=prefs();\n'''
rep(old,new,'pin current scanned item first')

# When a saved item is scanned, jump the list to its pinned first row rather than its old position.
old='''        for(int i=0;i<visibleRows.size();i++) {\n            InventoryDb.Row r=visibleRows.get(i);\n            if(r!=null&&lastBarcode.equals(r.barcode)) {\n                final int pos=i;\n                list.post(()->list.smoothScrollToPosition(pos));\n                break;\n            }\n        }\n'''
new='''        list.post(()->list.setSelection(0));\n'''
rep(old,new,'reveal pinned current item')

rep('TextView app=text("Onhand Inventory 3.0.75",19,Color.WHITE,true);',
    'TextView app=text("Onhand Inventory 3.0.76",19,Color.WHITE,true);',
    'visible version')
p.write_text(s)

# Cases calculator: make both fields explicit custom-keypad targets and prevent keypad
# buttons from stealing focus. This guarantees the second field receives digits.
p=Path('app/src/main/java/com/iceinventory/onhand/QuantityActivity.java')
s=p.read_text()

old='''        perUnit=new EditText(this);\n        perUnit.setTextSize(20);perUnit.setTextColor(Color.BLACK);perUnit.setSingleLine(true);perUnit.setGravity(Gravity.CENTER);\n        perUnit.setShowSoftInputOnFocus(false);\n        cases=new EditText(this);\n        cases.setTextSize(20);cases.setTextColor(Color.BLACK);cases.setSingleLine(true);cases.setGravity(Gravity.CENTER);\n        cases.setShowSoftInputOnFocus(false);\n'''
new='''        perUnit=new EditText(this);\n        perUnit.setTextSize(20);perUnit.setTextColor(Color.BLACK);perUnit.setSingleLine(true);perUnit.setGravity(Gravity.CENTER);\n        perUnit.setInputType(android.text.InputType.TYPE_CLASS_NUMBER);perUnit.setShowSoftInputOnFocus(false);\n        cases=new EditText(this);\n        cases.setTextSize(20);cases.setTextColor(Color.BLACK);cases.setSingleLine(true);cases.setGravity(Gravity.CENTER);\n        cases.setInputType(android.text.InputType.TYPE_CLASS_NUMBER);cases.setShowSoftInputOnFocus(false);\n'''
if old not in s: raise SystemExit('3.0.76 target missing: Cases input fields')
s=s.replace(old,new,1)

old='''            Button b=new Button(this);b.setText(k);b.setAllCaps(false);b.setTextSize(18);b.setTextColor(Color.BLACK);\n            b.setOnClickListener(v->pressKey(((Button)v).getText().toString()));\n'''
new='''            Button b=new Button(this);b.setText(k);b.setAllCaps(false);b.setTextSize(18);b.setTextColor(Color.BLACK);\n            b.setFocusable(false);b.setFocusableInTouchMode(false);\n            b.setOnClickListener(v->pressKey(((Button)v).getText().toString()));\n'''
if old not in s: raise SystemExit('3.0.76 target missing: Cases keypad buttons')
s=s.replace(old,new,1)

# Replace the 3.0.75 focus/click handlers with touch-safe targeting for both operands.
old='''        perUnit.setOnFocusChangeListener((v,has)->{if(has){active=perUnit;hideKeyboard();}});\n        cases.setOnFocusChangeListener((v,has)->{if(has){active=cases;hideKeyboard();scroll.postDelayed(()->scroll.fullScroll(View.FOCUS_DOWN),120);}});cases.setOnClickListener(v->{active=cases;hideKeyboard();scroll.postDelayed(()->scroll.fullScroll(View.FOCUS_DOWN),120);});\n'''
new='''        perUnit.setOnFocusChangeListener((v,has)->{if(has){active=perUnit;hideKeyboard();}});\n        perUnit.setOnTouchListener((v,event)->{if(event.getAction()==android.view.MotionEvent.ACTION_DOWN){active=perUnit;perUnit.requestFocus();hideKeyboard();}return false;});\n        perUnit.setOnClickListener(v->{active=perUnit;perUnit.requestFocus();hideKeyboard();});\n        cases.setOnFocusChangeListener((v,has)->{if(has){active=cases;hideKeyboard();scroll.postDelayed(()->scroll.fullScroll(View.FOCUS_DOWN),120);}});\n        cases.setOnTouchListener((v,event)->{if(event.getAction()==android.view.MotionEvent.ACTION_DOWN){active=cases;cases.requestFocus();hideKeyboard();scroll.postDelayed(()->scroll.fullScroll(View.FOCUS_DOWN),120);}return false;});\n        cases.setOnClickListener(v->{active=cases;cases.requestFocus();hideKeyboard();scroll.postDelayed(()->scroll.fullScroll(View.FOCUS_DOWN),120);});\n'''
if old not in s: raise SystemExit('3.0.76 target missing: Cases focus handlers')
s=s.replace(old,new,1)

old='''    private void pressKey(String key){\n        if(active==null)active=perUnit;\n        String s=active.getText().toString();\n        if("Clear".equals(key)){active.setText("");return;}\n        if("⌫".equals(key)){\n            if(!s.isEmpty())active.setText(s.substring(0,s.length()-1));\n            return;\n        }\n        if(s.length()<9)active.setText(s+key);\n        active.setSelection(active.getText().length());\n    }\n'''
new='''    private void pressKey(String key){\n        if(active==null)active=perUnit;\n        active.requestFocus();\n        hideKeyboard();\n        String s=active.getText().toString();\n        if("Clear".equals(key)){active.setText("");active.setSelection(0);return;}\n        if("⌫".equals(key)){\n            if(!s.isEmpty())active.setText(s.substring(0,s.length()-1));\n            active.setSelection(active.getText().length());\n            return;\n        }\n        if(s.length()<9)active.setText(s+key);\n        active.setSelection(active.getText().length());\n    }\n'''
if old not in s: raise SystemExit('3.0.76 target missing: Cases pressKey')
s=s.replace(old,new,1)
p.write_text(s)

# Advance installable Android version.
p=Path('app/build.gradle')
s=p.read_text().replace('versionCode 30075','versionCode 30076',1).replace("versionName '3.0.75'","versionName '3.0.76'",1)
if 'versionCode 30076' not in s or "versionName '3.0.76'" not in s:
    raise SystemExit('3.0.76 target missing: Gradle version')
p.write_text(s)

p=Path('app/src/main/AndroidManifest.xml')
s=p.read_text().replace('android:label="iCE Onhand 3.0.75"','android:label="iCE Onhand 3.0.76"',1)
if 'android:label="iCE Onhand 3.0.76"' not in s:
    raise SystemExit('3.0.76 target missing: manifest version')
p.write_text(s)

print('Prepared iCE Onhand 3.0.76: current scan pinned first + scan keyboard hidden + reliable Cases second operand input')
