from pathlib import Path
import runpy

# Preserve every approved 3.0.54 behavior first.
runpy.run_path('.github/prepare_3054.py', run_name='__main__')

p=Path('app/src/main/java/com/iceinventory/onhand/MainActivity.java')
s=p.read_text()

# Bluetooth scanners on some Samsung/Android profiles arrive through the IME/InputConnection
# instead of physical KeyEvents. Watch the Barcode text for a fast scan burst and submit it
# through the exact same handleScannedBarcode() lookup used by the phone camera scanner.
old='''    private int hardwareScanGeneration=0;\n'''
new='''    private int hardwareScanGeneration=0;\n    private boolean barcodeInternalUpdate=false;\n    private long barcodeTextLastMs=0L;\n    private int barcodeTextRapidChanges=0;\n    private int barcodeTextGeneration=0;\n'''
if old not in s: raise SystemExit('3.0.55 target missing: scanner generation field')
s=s.replace(old,new,1)

old='''        barcode.setOnFocusChangeListener((v,has)->{if(!has)barcode.setShowSoftInputOnFocus(false);});\n        barcode.setOnEditorActionListener((v,action,event)->{\n'''
new='''        barcode.setOnFocusChangeListener((v,has)->{if(!has)barcode.setShowSoftInputOnFocus(false);});\n        barcode.addTextChangedListener(new TextWatcher(){\n            @Override public void beforeTextChanged(CharSequence s,int st,int c,int a){}\n            @Override public void onTextChanged(CharSequence s,int st,int before,int count){\n                if(barcodeInternalUpdate)return;\n                String value=s==null?\"\":s.toString().trim();\n                long now=System.currentTimeMillis();\n                if(value.isEmpty()){\n                    barcodeTextRapidChanges=0;\n                    barcodeTextLastMs=0L;\n                    barcodeTextGeneration++;\n                    return;\n                }\n                long gap=barcodeTextLastMs==0L?9999L:now-barcodeTextLastMs;\n                if(count>=4)barcodeTextRapidChanges=8;\n                else if(gap<=100L)barcodeTextRapidChanges++;\n                else barcodeTextRapidChanges=1;\n                barcodeTextLastMs=now;\n\n                // Full-string IME commits or very fast character bursts are scanner input.\n                if(value.length()>=8&&(count>=4||barcodeTextRapidChanges>=8)){\n                    final String candidate=value;\n                    final int token=++barcodeTextGeneration;\n                    barcode.postDelayed(()->{\n                        if(token!=barcodeTextGeneration||barcodeInternalUpdate)return;\n                        String current=barcode.getText().toString().trim();\n                        if(!candidate.equals(current))return;\n                        barcodeTextRapidChanges=0;\n                        barcodeTextLastMs=0L;\n                        barcodeTextGeneration++;\n                        handleScannedBarcode(candidate);\n                    },280);\n                }\n            }\n            @Override public void afterTextChanged(Editable e){}\n        });\n        barcode.setOnEditorActionListener((v,action,event)->{\n'''
if old not in s: raise SystemExit('3.0.55 target missing: barcode focus/editor block')
s=s.replace(old,new,1)

# Any explicit lookup cancels a pending IME-burst lookup, preventing duplicate scans.
old='''    private void handleScannedBarcode(String rawCode) {\n        String code=maybeGtin(rawCode==null?\"\":rawCode.trim());\n'''
new='''    private void handleScannedBarcode(String rawCode) {\n        barcodeTextGeneration++;\n        String code=maybeGtin(rawCode==null?\"\":rawCode.trim());\n'''
if old not in s: raise SystemExit('3.0.55 target missing: handleScannedBarcode start')
s=s.replace(old,new,1)

# Programmatic barcode updates must not look like an IME scanner burst.
old='''        barcode.setShowSoftInputOnFocus(false);\n        barcode.setText(code);barcode.setSelection(code.length());\n'''
new='''        barcode.setShowSoftInputOnFocus(false);\n        barcodeInternalUpdate=true;\n        try { barcode.setText(code);barcode.setSelection(code.length()); }\n        finally { barcodeInternalUpdate=false; }\n'''
if old not in s: raise SystemExit('3.0.55 target missing: handle barcode setText')
s=s.replace(old,new,1)

old='''        barcode.setText(scanned);\n        barcode.setSelection(scanned.length());\n        handleScannedBarcode(scanned);\n'''
new='''        barcodeInternalUpdate=true;\n        try { barcode.setText(scanned);barcode.setSelection(scanned.length()); }\n        finally { barcodeInternalUpdate=false; }\n        handleScannedBarcode(scanned);\n'''
if old not in s: raise SystemExit('3.0.55 target missing: hardware commit barcode setText')
s=s.replace(old,new,1)

old='''                String partial=hardwareScanBuffer.toString();\n                barcode.setText(partial);\n                barcode.setSelection(partial.length());\n'''
new='''                String partial=hardwareScanBuffer.toString();\n                barcodeInternalUpdate=true;\n                try { barcode.setText(partial);barcode.setSelection(partial.length()); }\n                finally { barcodeInternalUpdate=false; }\n'''
if old not in s: raise SystemExit('3.0.55 target missing: hardware partial barcode setText')
s=s.replace(old,new,1)

p.write_text(s)
print('Prepared iCE Onhand 3.0.55: Bluetooth IME scan bursts automatically trigger saved-item lookup')
