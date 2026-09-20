from pathlib import Path

base=Path('.github/prepare_30128.py')
exec(compile(base.read_text(),str(base),'exec'),{'__name__':'__main__','__file__':str(base)})

p=Path('app/build.gradle')
g=p.read_text().replace('versionCode 30128','versionCode 30129',1).replace("versionName '3.0.128'","versionName '3.0.129'",1)
if 'versionCode 30129' not in g: raise SystemExit('3.0.129 Gradle target missing')
p.write_text(g)

p=Path('app/src/main/java/com/iceinventory/onhand/MainActivity.java')
s=p.read_text().replace('Onhand Inventory 3.0.128','Onhand Inventory 3.0.129',1)
p.write_text(s)

p=Path('app/src/main/java/com/iceinventory/onhand/LiqPosInventoryActivity.java')
s=p.read_text()
if '7. Export LiqPOS Barcode-Quantity CSV' not in s: raise SystemExit('3.0.129 LiqPOS line 7 target missing')
s=s.replace('7. Export LiqPOS Barcode-Quantity CSV','7. Export LiqPOS CSV',1)
s=s.replace('\\\\n','\\n').replace('\\\\r','\\r').replace('\\\\t','\\t')
p.write_text(s)

p=Path('app/src/main/java/com/iceinventory/onhand/MonthlyInventoryActivity.java')
s=p.read_text()
if 'Return to Counting — Adjust This Device' not in s: raise SystemExit('3.0.129 return button target missing')
s=s.replace('Return to Counting — Adjust This Device','↩ Return to Counting / Adjust',1)
p.write_text(s)

p=Path('app/src/main/AndroidManifest.xml')
m=p.read_text().replace('iCE Onhand 3.0.128','iCE Onhand 3.0.129',1)
if 'iCE Onhand 3.0.129' not in m: raise SystemExit('3.0.129 manifest version missing')
p.write_text(m)

print('Prepared iCE Onhand 3.0.129: compact line 7 and return-to-counting labels')
