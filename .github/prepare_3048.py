from pathlib import Path
import runpy

# Preserve every approved 3.0.47 behavior first.
runpy.run_path('.github/prepare_3047.py', run_name='__main__')

# --- MainActivity: force Bluetooth/hardware scanner keystrokes into Barcode,
# regardless of which EditText currently has focus. Soft-keyboard typing is untouched. ---
p=Path('app/src/main/java/com/iceinventory/onhand/MainActivity.java')
s=p.read_text()

old='''    private String pendingExportFileName="";\n'''
new='''    private String pendingExportFileName="";\n    private final StringBuilder hardwareScanBuffer=new StringBuilder();\n    private long hardwareScanLastKeyMs=0L;\n'''
if old not in s: raise SystemExit('3.0.48 target missing: scanner buffer fields')
s=s.replace(old,new,1)

old='''        buildUi();\n        refreshLocations();\n        refreshList();\n'''
new='''        buildUi();\n        refreshLocations();\n        refreshList();\n        barcode.postDelayed(this::focusBarcodeWithoutKeyboard,120);\n'''
if old not in s: raise SystemExit('3.0.48 target missing: initializeApp focus')
s=s.replace(old,new,1)

marker='''    private void scanBarcode() {\n'''
method='''    @Override public boolean dispatchKeyEvent(KeyEvent event) {\n        if(event!=null&&event.getDeviceId()>0&&event.getAction()==KeyEvent.ACTION_DOWN&&barcode!=null) {\n            int key=event.getKeyCode();\n            if(key==KeyEvent.KEYCODE_ENTER||key==KeyEvent.KEYCODE_NUMPAD_ENTER||key==KeyEvent.KEYCODE_TAB) {\n                String scanned=hardwareScanBuffer.toString().trim();\n                hardwareScanBuffer.setLength(0);\n                hardwareScanLastKeyMs=0L;\n                if(!scanned.isEmpty()) {\n                    barcode.setShowSoftInputOnFocus(false);\n                    hideKeyboard();\n                    barcode.setText(scanned);\n                    barcode.setSelection(scanned.length());\n                    handleScannedBarcode(scanned);\n                    return true;\n                }\n            } else {\n                int unicode=event.getUnicodeChar();\n                if(unicode>0&&!Character.isISOControl(unicode)) {\n                    long now=System.currentTimeMillis();\n                    if(now-hardwareScanLastKeyMs>750L)hardwareScanBuffer.setLength(0);\n                    hardwareScanLastKeyMs=now;\n                    hardwareScanBuffer.append((char)unicode);\n                    return true;\n                }\n            }\n        }\n        return super.dispatchKeyEvent(event);\n    }\n\n'''
if marker not in s: raise SystemExit('3.0.48 target missing: scanBarcode marker')
s=s.replace(marker,method+marker,1)
p.write_text(s)

# --- QuantityActivity: calculator-style multiply flow.
# Example: 10 -> x -> 20 -> = immediately returns 200 to the main Count field. ---
p=Path('app/src/main/java/com/iceinventory/onhand/QuantityActivity.java')
s=p.read_text()

old='''        TextView info=text("ⓘ  Enter the quantity you want to add.\\n     You can enter a single amount\\n     or use multiply (Qty × Cases).",15,Color.rgb(0,60,180),true);\n'''
new='''        TextView info=text("ⓘ  Multiply in one simple flow: Qty → × → Cases → =\\n     Example: 10 × 20 = 200\\n     Press = and 200 is inserted into Count automatically.",15,Color.rgb(0,60,180),true);\n'''
if old not in s: raise SystemExit('3.0.48 target missing: multiply instructions')
s=s.replace(old,new,1)

old='''        String[] keys={"1","2","3","⌫","4","5","6","Clear","7","8","9","","","0","00",""};\n'''
new='''        String[] keys={"1","2","3","⌫","4","5","6","Clear","7","8","9","×","0","00","=",""};\n'''
if old not in s: raise SystemExit('3.0.48 target missing: multiply keypad')
s=s.replace(old,new,1)

old='''    private void pressKey(String key){\n        if(active==null)active=perUnit;\n        String s=active.getText().toString();\n        if("Clear".equals(key)){active.setText("");return;}\n        if("⌫".equals(key)){\n            if(!s.isEmpty())active.setText(s.substring(0,s.length()-1));\n            return;\n        }\n        if(s.length()<9)active.setText(s+key);\n        active.setSelection(active.getText().length());\n    }\n'''
new='''    private void pressKey(String key){\n        if(active==null)active=perUnit;\n        if("×".equals(key)){\n            active=cases;\n            cases.requestFocus();\n            cases.setSelection(cases.getText().length());\n            return;\n        }\n        if("=".equals(key)){\n            recalc();\n            if(total>0)finishWithQuantity();\n            return;\n        }\n        String s=active.getText().toString();\n        if("Clear".equals(key)){active.setText("");return;}\n        if("⌫".equals(key)){\n            if(!s.isEmpty())active.setText(s.substring(0,s.length()-1));\n            return;\n        }\n        if(s.length()<9)active.setText(s+key);\n        active.setSelection(active.getText().length());\n    }\n'''
if old not in s: raise SystemExit('3.0.48 target missing: pressKey flow')
s=s.replace(old,new,1)
p.write_text(s)

print('Prepared iCE Onhand 3.0.48: forced Bluetooth scan routing + one-step multiply equals flow')
