from pathlib import Path
import runpy

# Preserve every approved 3.0.51 behavior first.
runpy.run_path('.github/prepare_3051.py', run_name='__main__')

p=Path('app/src/main/java/com/iceinventory/onhand/MainActivity.java')
s=p.read_text()

# Manual barcode entry / saved match: highlight the matched item yellow and reveal it in the list.
old='''    private void useSavedBarcodeMatch(InventoryDb.Row row,boolean flexible) {\n        if(row==null)return;\n        String actual=row.barcode==null?"":row.barcode.trim();\n        barcode.setText(actual);barcode.setSelection(actual.length());\n        description.setText(row.description==null?"":row.description);\n        currentPrice=row.price==null?"":row.price;\n        if(flexible)toast("Matched saved barcode: "+actual);\n        focusQuantity();\n    }\n'''
new='''    private void useSavedBarcodeMatch(InventoryDb.Row row,boolean flexible) {\n        if(row==null)return;\n        String actual=row.barcode==null?"":row.barcode.trim();\n        barcode.setText(actual);barcode.setSelection(actual.length());\n        description.setText(row.description==null?"":row.description);\n        currentPrice=row.price==null?"":row.price;\n        highlightAndRevealBarcode(actual);\n        if(flexible)toast("Matched saved barcode: "+actual);\n        focusQuantity();\n    }\n\n    private void highlightAndRevealBarcode(String code) {\n        lastBarcode=code==null?"":code.trim();\n        applyFilter();\n        if(list==null||lastBarcode.isEmpty())return;\n        for(int i=0;i<visibleRows.size();i++) {\n            InventoryDb.Row r=visibleRows.get(i);\n            if(r!=null&&lastBarcode.equals(r.barcode)) {\n                final int pos=i;\n                list.post(()->list.smoothScrollToPosition(pos));\n                break;\n            }\n        }\n    }\n'''
if old not in s: raise SystemExit('3.0.52 target missing: saved barcode match')
s=s.replace(old,new,1)

# Manual typing: tapping an existing barcode selects the whole value so typing replaces it.
old='''                barcode.setShowSoftInputOnFocus(true);\n                barcode.postDelayed(()->showKeyboard(barcode),60);\n'''
new='''                barcode.setShowSoftInputOnFocus(true);\n                barcode.postDelayed(barcode::selectAll,30);\n                barcode.postDelayed(()->showKeyboard(barcode),60);\n'''
if old not in s: raise SystemExit('3.0.52 target missing: barcode touch')
s=s.replace(old,new,1)

# Bluetooth/wedge scanner: on the first character of a new scan, clear any old barcode immediately.
old='''                    if(hardwareScanBuffer.length()==0) {\n                        barcode.setShowSoftInputOnFocus(false);\n                        hideKeyboard();\n                        barcode.requestFocus();\n                    }\n                    hardwareScanLastKeyMs=now;\n'''
new='''                    if(hardwareScanBuffer.length()==0) {\n                        barcode.setShowSoftInputOnFocus(false);\n                        hideKeyboard();\n                        barcode.requestFocus();\n                        barcode.setText("");\n                    }\n                    hardwareScanLastKeyMs=now;\n'''
if old not in s: raise SystemExit('3.0.52 target missing: hardware scan start')
s=s.replace(old,new,1)

p.write_text(s)
print('Prepared iCE Onhand 3.0.52: manual match yellow/reveal + barcode replace-on-scan/type')
