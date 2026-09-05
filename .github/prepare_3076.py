from pathlib import Path
import runpy

# Preserve every approved 3.0.75 behavior first.
runpy.run_path('.github/prepare_3075.py', run_name='__main__')

# 3.0.76: keep the just-scanned item visible at the top, keep the previous scan
# directly below it, hide the Samsung keyboard after scans, and make both Cases
# operands reliable targets for the app's custom keypad.
p=Path('app/src/main/java/com/iceinventory/onhand/MainActivity.java')
s=p.read_text()

def rep(old,new,label):
    global s
    if old not in s: raise SystemExit('3.0.76 target missing: '+label)
    s=s.replace(old,new,1)

rep('    private String lastBarcode="";\n',
    '    private String lastBarcode="";\n    private String previousBarcode="";\n',
    'previous scan field')

rep('''        qty.setInputType(InputType.TYPE_CLASS_NUMBER);styleEntry(qty);installScannerImeWatcher(qty);\n''',
'''        qty.setInputType(InputType.TYPE_CLASS_NUMBER);styleEntry(qty);installScannerImeWatcher(qty);\n        qty.setShowSoftInputOnFocus(false);\n        qty.setOnTouchListener((v,event)->{\n            if(event.getAction()==MotionEvent.ACTION_DOWN){qty.setShowSoftInputOnFocus(true);qty.postDelayed(()->showKeyboard(qty),60);}\n            return false;\n        });\n        qty.setOnFocusChangeListener((v,has)->{if(!has)qty.setShowSoftInputOnFocus(false);});\n''','quantity keyboard policy')

rep('''    private void focusQuantity() {\n        qty.requestFocus();\n        qty.setSelection(qty.getText().length());\n        qty.postDelayed(()->showKeyboard(qty),80);\n    }\n''',
'''    private void focusQuantity() {\n        qty.setShowSoftInputOnFocus(false);\n        qty.requestFocus();\n        qty.setSelection(qty.getText().length());\n        qty.postDelayed(this::hideKeyboard,40);\n        qty.postDelayed(this::hideKeyboard,180);\n    }\n''','focus quantity without keyboard')

rep('''        lastBarcode=code==null?"":code.trim();\n        applyFilter();\n''',
'''        String next=code==null?"":code.trim();\n        if(!next.isEmpty()&&!next.equals(lastBarcode)){previousBarcode=lastBarcode;}\n        lastBarcode=next;\n        applyFilter();\n''','scan order tracking')

rep('''        sortVisibleRows();\n        SharedPreferences p=prefs();\n''',
'''        sortVisibleRows();\n        if(lastBarcode!=null&&!lastBarcode.isEmpty()){\n            for(int i=0;i<visibleRows.size();i++){InventoryDb.Row r=visibleRows.get(i);if(r!=null&&lastBarcode.equals(r.barcode)){if(i>0){visibleRows.remove(i);visibleRows.add(0,r);}break;}}\n        }\n        if(previousBarcode!=null&&!previousBarcode.isEmpty()&&!previousBarcode.equals(lastBarcode)){\n            for(int i=0;i<visibleRows.size();i++){InventoryDb.Row r=visibleRows.get(i);if(r!=null&&previousBarcode.equals(r.barcode)){if(i!=1){visibleRows.remove(i);visibleRows.add(Math.min(1,visibleRows.size()),r);}break;}}\n        }\n        SharedPreferences p=prefs();\n''','pin current and previous scans')

rep('''        for(int i=0;i<visibleRows.size();i++) {\n            InventoryDb.Row r=visibleRows.get(i);\n            if(r!=null&&lastBarcode.equals(r.barcode)) {\n                final int pos=i;\n                list.post(()->list.setSelection(pos));\n                break;\n            }\n        }\n''','        list.post(()->list.setSelection(0));\n','reveal current row')

rep('TextView app=text("Onhand Inventory 3.0.75",19,Color.WHITE,true);','TextView app=text("Onhand Inventory 3.0.76",19,Color.WHITE,true);','visible version')
p.write_text(s)

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

old='''        perUnit.setOnFocusChangeListener((v,has)->{if(has){active=perUnit;hideKeyboard();}});\n        cases.setOnFocusChangeListener((v,has)->{if(has){active=cases;hideKeyboard();scroll.postDelayed(()->scroll.fullScroll(View.FOCUS_DOWN),120);}});cases.setOnClickListener(v->{active=cases;hideKeyboard();scroll.postDelayed(()->scroll.fullScroll(View.FOCUS_DOWN),120);});\n'''
new='''        perUnit.setOnFocusChangeListener((v,has)->{if(has){active=perUnit;hideKeyboard();}});\n        perUnit.setOnTouchListener((v,event)->{if(event.getAction()==android.view.MotionEvent.ACTION_DOWN){active=perUnit;perUnit.requestFocus();hideKeyboard();}return false;});\n        perUnit.setOnClickListener(v->{active=perUnit;perUnit.requestFocus();hideKeyboard();});\n        cases.setOnFocusChangeListener((v,has)->{if(has){active=cases;hideKeyboard();scroll.postDelayed(()->scroll.fullScroll(View.FOCUS_DOWN),120);}});\n        cases.setOnTouchListener((v,event)->{if(event.getAction()==android.view.MotionEvent.ACTION_DOWN){active=cases;cases.requestFocus();hideKeyboard();scroll.postDelayed(()->scroll.fullScroll(View.FOCUS_DOWN),120);}return false;});\n        cases.setOnClickListener(v->{active=cases;cases.requestFocus();hideKeyboard();scroll.postDelayed(()->scroll.fullScroll(View.FOCUS_DOWN),120);});\n'''
if old not in s: raise SystemExit('3.0.76 target missing: Cases focus handlers')
s=s.replace(old,new,1)

# Preserve the 10 × 20 = 200 flow from 3.0.48 while keeping the selected operand active.
old='''    private void pressKey(String key){\n        if(active==null)active=perUnit;\n        if("×".equals(key)){\n            active=cases;\n            cases.requestFocus();\n            cases.setSelection(cases.getText().length());\n            return;\n        }\n        if("=".equals(key)){\n            recalc();\n            if(total>0)finishWithQuantity();\n            return;\n        }\n        String s=active.getText().toString();\n        if("Clear".equals(key)){active.setText("");return;}\n        if("⌫".equals(key)){\n            if(!s.isEmpty())active.setText(s.substring(0,s.length()-1));\n            return;\n        }\n        if(s.length()<9)active.setText(s+key);\n        active.setSelection(active.getText().length());\n    }\n'''
new='''    private void pressKey(String key){\n        if(active==null)active=perUnit;\n        if("×".equals(key)){active=cases;cases.requestFocus();cases.setSelection(cases.getText().length());hideKeyboard();return;}\n        if("=".equals(key)){recalc();if(total>0)finishWithQuantity();return;}\n        active.requestFocus();hideKeyboard();\n        String s=active.getText().toString();\n        if("Clear".equals(key)){active.setText("");active.setSelection(0);return;}\n        if("⌫".equals(key)){if(!s.isEmpty())active.setText(s.substring(0,s.length()-1));active.setSelection(active.getText().length());return;}\n        if(s.length()<9)active.setText(s+key);\n        active.setSelection(active.getText().length());\n    }\n'''
if old not in s: raise SystemExit('3.0.76 target missing: Cases pressKey')
s=s.replace(old,new,1)
p.write_text(s)

p=Path('app/build.gradle')
s=p.read_text().replace('versionCode 30075','versionCode 30076',1).replace("versionName '3.0.75'","versionName '3.0.76'",1)
if 'versionCode 30076' not in s or "versionName '3.0.76'" not in s: raise SystemExit('3.0.76 target missing: Gradle version')
p.write_text(s)

p=Path('app/src/main/AndroidManifest.xml')
s=p.read_text().replace('android:label="iCE Onhand 3.0.75"','android:label="iCE Onhand 3.0.76"',1)
if 'android:label="iCE Onhand 3.0.76"' not in s: raise SystemExit('3.0.76 target missing: manifest version')
p.write_text(s)

print('Prepared iCE Onhand 3.0.76: current scan row 1 + previous scan row 2 + keyboard hidden + reliable Cases second operand')
