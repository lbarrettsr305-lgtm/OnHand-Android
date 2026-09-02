from pathlib import Path

p=Path('app/src/main/java/com/iceinventory/onhand/MainActivity.java')
s=p.read_text()

# Centralize scan-to-quantity focus so camera and hardware scans behave identically.
anchor='    private void handleScannedBarcode(String code) {'
helper='''    private void focusQuantityAfterScan(){\n        if(qty==null) return;\n        qty.post(()->{\n            qty.requestFocus();\n            qty.setSelection(qty.length());\n        });\n    }\n\n'''
if helper not in s:
    if anchor not in s: raise SystemExit('handle scan anchor not found')
    s=s.replace(anchor, helper+anchor, 1)

# Every scan path that previously requested quantity focus now uses the stronger posted focus.
s=s.replace('qty.requestFocus();', 'focusQuantityAfterScan();')

# The replacement above also changes the helper body if applied after insertion; repair it.
s=s.replace('''        qty.post(()->{\n            focusQuantityAfterScan();\n            qty.setSelection(qty.length());\n        });''','''        qty.post(()->{\n            qty.requestFocus();\n            qty.setSelection(qty.length());\n        });''')

# After the hardware scanner terminator, force quantity focus again after scan processing.
old='''                    handleScannedBarcode(scanned);\n                    return true;'''
new='''                    handleScannedBarcode(scanned);\n                    focusQuantityAfterScan();\n                    return true;'''
if old not in s: raise SystemExit('hardware scanner completion anchor not found')
s=s.replace(old,new,1)

p.write_text(s)

b=Path('app/build.gradle')
g=b.read_text()
for old in ('30026','30025','30024','30023'):
    g=g.replace('versionCode '+old,'versionCode 30027')
for old in ('3.0.26','3.0.25','3.0.24','3.0.23'):
    g=g.replace("versionName '"+old+"'","versionName '3.0.27'")
b.write_text(g)
