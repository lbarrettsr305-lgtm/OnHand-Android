from pathlib import Path
import runpy

# Preserve every approved 3.0.48 behavior first.
runpy.run_path('.github/prepare_3048.py', run_name='__main__')

# --- MainActivity: make Bluetooth/hardware scanner capture independent of device id.
# Some Android/Samsung scanner profiles report deviceId 0, so 3.0.48's >0 check
# could allow scanner characters to fall into whichever EditText had focus.
p=Path('app/src/main/java/com/iceinventory/onhand/MainActivity.java')
s=p.read_text()

old='''        if(event!=null&&event.getDeviceId()>0&&event.getAction()==KeyEvent.ACTION_DOWN&&barcode!=null) {\n'''
new='''        if(event!=null&&event.getAction()==KeyEvent.ACTION_DOWN&&barcode!=null) {\n'''
if old not in s: raise SystemExit('3.0.49 target missing: scanner device-id condition')
s=s.replace(old,new,1)

old='''                if(unicode>0&&!Character.isISOControl(unicode)) {\n                    long now=System.currentTimeMillis();\n                    if(now-hardwareScanLastKeyMs>750L)hardwareScanBuffer.setLength(0);\n                    hardwareScanLastKeyMs=now;\n                    hardwareScanBuffer.append((char)unicode);\n                    return true;\n                }\n'''
new='''                if(unicode>0&&!Character.isISOControl(unicode)) {\n                    long now=System.currentTimeMillis();\n                    if(now-hardwareScanLastKeyMs>750L)hardwareScanBuffer.setLength(0);\n                    if(hardwareScanBuffer.length()==0) {\n                        barcode.setShowSoftInputOnFocus(false);\n                        hideKeyboard();\n                        barcode.requestFocus();\n                    }\n                    hardwareScanLastKeyMs=now;\n                    hardwareScanBuffer.append((char)unicode);\n                    return true;\n                }\n'''
if old not in s: raise SystemExit('3.0.49 target missing: scanner printable-key block')
s=s.replace(old,new,1)
p.write_text(s)

# --- InventoryAdapter: protect quantities from accidental taps on neighboring descriptions.
# Only the current yellow-highlighted row keeps the quick +1 description-area action.
# Non-highlighted rows fall through to the normal row edit action instead of incrementing.
p=Path('app/src/main/java/com/iceinventory/onhand/InventoryAdapter.java')
s=p.read_text()

old='''        center.setClickable(true);\n        center.setFocusable(true);\n'''
new='''        center.setClickable(active);\n        center.setFocusable(active);\n'''
if old not in s: raise SystemExit('3.0.49 target missing: center clickable state')
s=s.replace(old,new,1)

old='''        // The whole description/details area is the fast +1 target, matching the proven older workflow.\n        center.setOnClickListener(v->listener.onAddOne(r));\n'''
new='''        // Quick +1 is allowed only on the currently highlighted yellow row.\n        // Touching a description on any other row must never change its quantity.\n        if(active)center.setOnClickListener(v->listener.onAddOne(r));\n'''
if old not in s: raise SystemExit('3.0.49 target missing: center fast +1 listener')
s=s.replace(old,new,1)
p.write_text(s)

print('Prepared iCE Onhand 3.0.49: global scanner capture + highlighted-row-only quick add')
