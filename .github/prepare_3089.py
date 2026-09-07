from pathlib import Path

base=Path('.github/prepare_3088.py')
exec(compile(base.read_text(),str(base),'exec'),{'__name__':'__main__','__file__':str(base)})

p=Path('app/src/main/java/com/iceinventory/onhand/MainActivity.java')
s=p.read_text()
old='''                db.incrementQuantity(r.id,amount);lastBarcode=r.barcode;refreshList();noteCountForSafety();dialog.dismiss();
                toast(amount<0?"Subtracted "+Math.abs(amount)+" • New quantity "+next:"Added "+amount+" • New quantity "+next);
'''
new='''                db.incrementQuantity(r.id,amount);lastBarcode=r.barcode;refreshList();noteCountForSafety();dialog.dismiss();
                barcode.setText("");description.setText("");qty.setText("");currentPrice="";
                focusBarcodeWithoutKeyboard();
                toast(amount<0?"Subtracted "+Math.abs(amount)+" • New quantity "+next:"Added "+amount+" • New quantity "+next);
'''
if old not in s:raise SystemExit('3.0.89 target missing: manual adjustment completion')
s=s.replace(old,new,1)
s=s.replace('Onhand Inventory 3.0.88','Onhand Inventory 3.0.89')
if 'Onhand Inventory 3.0.89' not in s:raise SystemExit('3.0.89 target missing: title version')
p.write_text(s)

p=Path('app/build.gradle');s=p.read_text().replace('versionCode 30088','versionCode 30089',1).replace("versionName '3.0.88'","versionName '3.0.89'",1)
if 'versionCode 30089' not in s or "versionName '3.0.89'" not in s:raise SystemExit('3.0.89 target missing: Gradle version')
p.write_text(s)

p=Path('app/src/main/AndroidManifest.xml');s=p.read_text().replace('iCE Onhand 3.0.88','iCE Onhand 3.0.89')
if 'iCE Onhand 3.0.89' not in s:raise SystemExit('3.0.89 target missing: manifest version')
p.write_text(s)

main=Path('app/src/main/java/com/iceinventory/onhand/MainActivity.java').read_text()
checks={'manual inputs cleared':'barcode.setText("");description.setText("");qty.setText("");currentPrice="";','barcode focus restored':'focusBarcodeWithoutKeyboard();','quantity adjustment preserved':'db.incrementQuantity(r.id,amount)'}
missing=[k for k,v in checks.items() if v not in main]
if missing:raise SystemExit('3.0.89 verification failed: '+', '.join(missing))
print('Prepared iCE Onhand 3.0.89: manual quantity adjustments return to bright Barcode input')
