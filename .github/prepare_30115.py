from pathlib import Path

# Preserve 3.0.114 and add the required store prefix plus an immediate import/line-item summary.
base=Path('.github/prepare_30114.py')
exec(compile(base.read_text(),str(base),'exec'),{'__name__':'__main__','__file__':str(base)})

p=Path('app/build.gradle')
g=p.read_text().replace('versionCode 30114','versionCode 30115',1).replace("versionName '3.0.114'","versionName '3.0.115'",1)
if 'versionCode 30115' not in g or "versionName '3.0.115'" not in g: raise SystemExit('3.0.115 Gradle target missing')
p.write_text(g)

p=Path('app/src/main/java/com/iceinventory/onhand/MainActivity.java')
s=p.read_text().replace('Onhand Inventory 3.0.114','Onhand Inventory 3.0.115',1)
if 'Onhand Inventory 3.0.115' not in s: raise SystemExit('3.0.115 visible version target missing')
p.write_text(s)

p=Path('app/src/main/AndroidManifest.xml')
m=p.read_text().replace('iCE Onhand 3.0.114','iCE Onhand 3.0.115',1)
if 'iCE Onhand 3.0.115' not in m: raise SystemExit('3.0.115 manifest version target missing')
p.write_text(m)

monthly=Path('app/src/main/java/com/iceinventory/onhand/MonthlyInventoryActivity.java').read_text()
checks={
    'required store name':'STORE NAME / FILE PREFIX — REQUIRED' in monthly,
    'import locked until store':'chooseSource.setEnabled(!storeName().isEmpty()&&!sourceReady)' in monthly,
    'store prefix first':'base()+" ONHAND COUNT-"+day()+".txt"' in monthly,
    'import confirmation':'✓ IMPORTED:' in monthly,
    'line item count':'ONHAND WORKING FILE:' in monthly and 'products.size()+" LINE ITEMS' in monthly,
    'blank GTIN count':'BLANK GTIN EXCLUDED:' in monthly,
    'email attachment staged':'ATTACHMENT READY:' in monthly,
}
missing=[k for k,v in checks.items() if not v]
if missing: raise SystemExit('3.0.115 verification failed: '+', '.join(missing))
print('Prepared iCE Onhand 3.0.115: required store prefix and visible import/OnHand line-item summary')
