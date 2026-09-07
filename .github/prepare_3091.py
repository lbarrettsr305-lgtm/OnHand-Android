from pathlib import Path

base=Path('.github/prepare_3090.py')
exec(compile(base.read_text(),str(base),'exec'),{'__name__':'__main__','__file__':str(base)})

p=Path('app/src/main/java/com/iceinventory/onhand/MainActivity.java')
s=p.read_text()
old='''                db.incrementQuantity(r.id,amount);lastBarcode=r.barcode;refreshList();noteCountForSafety();dialog.dismiss();
                barcode.setText("");description.setText("");qty.setText("");currentPrice="";
                focusBarcodeWithoutKeyboard();
'''
new='''                db.incrementQuantity(r.id,amount);refreshList();highlightAndRevealBarcode(r.barcode);noteCountForSafety();dialog.dismiss();
                barcode.setText("");description.setText("");qty.setText("");currentPrice="";
                focusBarcodeWithoutKeyboard();
'''
if old not in s:raise SystemExit('3.0.91 target missing: manual adjustment completion')
s=s.replace(old,new,1)
s=s.replace('Onhand Inventory 3.0.90','Onhand Inventory 3.0.91')
if 'Onhand Inventory 3.0.91' not in s:raise SystemExit('3.0.91 target missing: title version')
p.write_text(s)

p=Path('app/build.gradle');s=p.read_text().replace('versionCode 30090','versionCode 30091',1).replace("versionName '3.0.90'","versionName '3.0.91'",1)
if 'versionCode 30091' not in s or "versionName '3.0.91'" not in s:raise SystemExit('3.0.91 target missing: Gradle version')
p.write_text(s)

p=Path('app/src/main/AndroidManifest.xml');s=p.read_text().replace('iCE Onhand 3.0.90','iCE Onhand 3.0.91')
if 'iCE Onhand 3.0.91' not in s:raise SystemExit('3.0.91 target missing: manifest version')
p.write_text(s)

main=Path('app/src/main/java/com/iceinventory/onhand/MainActivity.java').read_text()
adapter=Path('app/src/main/java/com/iceinventory/onhand/InventoryAdapter.java').read_text()
checks={'manual scan-equivalent highlight':'refreshList();highlightAndRevealBarcode(r.barcode)' in main,'bright-yellow adapter state':'Color.rgb(255,215,0)' in adapter,'top-row reveal':'list.post(()->list.setSelection(0))' in main,'manual barcode readiness':'focusBarcodeWithoutKeyboard();' in main}
missing=[k for k,v in checks.items() if not v]
if missing:raise SystemExit('3.0.91 verification failed: '+', '.join(missing))
print('Prepared iCE Onhand 3.0.91: manual quantity updates jump to the bright-yellow top product row')
