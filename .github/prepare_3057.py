from pathlib import Path
import runpy

# Preserve every approved 3.0.56 behavior first.
runpy.run_path('.github/prepare_3056.py', run_name='__main__')

p=Path('app/src/main/java/com/iceinventory/onhand/MainActivity.java')
s=p.read_text()

# 3.0.55 installed an older Barcode-only IME watcher that evaluates the entire
# Barcode field. If a previous barcode is still displayed, that older watcher can
# see old+new as one value before the 3.0.56 field-independent scanner router gets
# a chance to replace it. Disable only that legacy watcher; 3.0.56's
# installScannerImeWatcher() remains the single authority for Bluetooth IME scans.
old='''                if(barcodeInternalUpdate)return;\n                String value=s==null?"":s.toString().trim();\n'''
new='''                if(barcodeInternalUpdate||barcodeTextGeneration>=0)return;\n                String value=s==null?"":s.toString().trim();\n'''
if old not in s: raise SystemExit('3.0.57 target missing: legacy barcode IME watcher')
s=s.replace(old,new,1)

p.write_text(s)
print('Prepared iCE Onhand 3.0.57: one Bluetooth IME router only; new scans replace existing barcode without legacy append conflict')
