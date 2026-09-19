from pathlib import Path

# Preserve 3.0.115 and make Query Master a non-blocking optional export.
base=Path('.github/prepare_30115.py')
exec(compile(base.read_text(),str(base),'exec'),{'__name__':'__main__','__file__':str(base)})

p=Path('app/build.gradle')
g=p.read_text().replace('versionCode 30115','versionCode 30116',1).replace("versionName '3.0.115'","versionName '3.0.116'",1)
if 'versionCode 30116' not in g or "versionName '3.0.116'" not in g: raise SystemExit('3.0.116 Gradle target missing')
p.write_text(g)

p=Path('app/src/main/java/com/iceinventory/onhand/MainActivity.java')
s=p.read_text().replace('Onhand Inventory 3.0.115','Onhand Inventory 3.0.116',1)
if 'Onhand Inventory 3.0.116' not in s: raise SystemExit('3.0.116 visible version target missing')
p.write_text(s)

p=Path('app/src/main/AndroidManifest.xml')
m=p.read_text().replace('iCE Onhand 3.0.115','iCE Onhand 3.0.116',1)
if 'iCE Onhand 3.0.116' not in m: raise SystemExit('3.0.116 manifest version target missing')
p.write_text(m)

monthly=Path('app/src/main/java/com/iceinventory/onhand/MonthlyInventoryActivity.java').read_text()
checks={
    'optional tools section':'OPTIONAL TOOLS — NOT REQUIRED' in monthly,
    'optional query master':'Optional: Export Query Master Excel' in monthly,
    'onhand is step 2':'2. Create OnHand Count File — Tab Delimited' in monthly,
    'master no longer blocks onhand':'saveOnHand.setEnabled(sourceReady&&!onHandCreated)' in monthly,
    'final client report step 7':'7. Export Petrosoft Client Excel' in monthly,
}
missing=[k for k,v in checks.items() if not v]
if missing: raise SystemExit('3.0.116 verification failed: '+', '.join(missing))
print('Prepared iCE Onhand 3.0.116: Query Master is optional and no longer blocks OnHand creation')
