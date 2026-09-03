from pathlib import Path
import runpy

# Preserve every approved 3.0.53 behavior first.
runpy.run_path('.github/prepare_3053.py', run_name='__main__')

p=Path('app/src/main/java/com/iceinventory/onhand/MainActivity.java')
s=p.read_text()

# Track the latest delayed scanner commit so only the final character burst is committed.
old='''    private long hardwareScanLastKeyMs=0L;\n'''
new='''    private long hardwareScanLastKeyMs=0L;\n    private int hardwareScanGeneration=0;\n'''
if old not in s: raise SystemExit('3.0.54 target missing: scanner fields')
s=s.replace(old,new,1)

start=s.find('''    @Override public boolean dispatchKeyEvent(KeyEvent event) {\n''')
end=s.find('''    private void scanBarcode() {\n''', start)
if start<0 or end<0: raise SystemExit('3.0.54 target missing: scanner dispatch block')

method='''    private boolean commitHardwareScan() {\n        String scanned=hardwareScanBuffer.toString().trim();\n        if(scanned.isEmpty())return false;\n        hardwareScanBuffer.setLength(0);\n        hardwareScanLastKeyMs=0L;\n        hardwareScanGeneration++;\n        barcode.setShowSoftInputOnFocus(false);\n        hideKeyboard();\n        barcode.requestFocus();\n        barcode.setText(scanned);\n        barcode.setSelection(scanned.length());\n        handleScannedBarcode(scanned);\n        return true;\n    }\n\n    private void commitHardwareScanIfReady(int token) {\n        if(token!=hardwareScanGeneration)return;\n        commitHardwareScan();\n    }\n\n    @Override public boolean dispatchKeyEvent(KeyEvent event) {\n        if(event!=null&&event.getDeviceId()>=0&&event.getAction()==KeyEvent.ACTION_DOWN&&barcode!=null) {\n            int key=event.getKeyCode();\n            if(key==KeyEvent.KEYCODE_ENTER||key==KeyEvent.KEYCODE_NUMPAD_ENTER||key==KeyEvent.KEYCODE_TAB) {\n                commitHardwareScan();\n                return true;\n            }\n\n            int unicode=event.getUnicodeChar();\n            if(unicode>0&&!Character.isISOControl(unicode)) {\n                long now=System.currentTimeMillis();\n                boolean newBurst=hardwareScanBuffer.length()==0 || now-hardwareScanLastKeyMs>600L;\n                if(newBurst) {\n                    hardwareScanBuffer.setLength(0);\n                    hardwareScanGeneration++;\n                    barcode.setShowSoftInputOnFocus(false);\n                    hideKeyboard();\n                    barcode.requestFocus();\n                    // A new scanner burst always owns the field. Never append to an old barcode.\n                    barcode.setText(\"\");\n                    description.setText(\"\");\n                    currentPrice=\"\";\n                }\n                hardwareScanLastKeyMs=now;\n                hardwareScanBuffer.append((char)unicode);\n\n                // Show the new scan in Barcode as it arrives, replacing the previous value immediately.\n                String partial=hardwareScanBuffer.toString();\n                barcode.setText(partial);\n                barcode.setSelection(partial.length());\n\n                // Some wedge scanners do not send Enter/Tab. Commit after a short idle period.\n                final int token=++hardwareScanGeneration;\n                barcode.postDelayed(()->commitHardwareScanIfReady(token),350);\n                return true;\n            }\n        }\n        return super.dispatchKeyEvent(event);\n    }\n\n'''

s=s[:start]+method+s[end:]
p.write_text(s)

print('Prepared iCE Onhand 3.0.54: scanner always overwrites existing barcode + idle auto-commit')
