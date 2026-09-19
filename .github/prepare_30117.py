from pathlib import Path

# Preserve 3.0.116 and add a clear first-step prompt in the empty inventory area.
base=Path('.github/prepare_30116.py')
exec(compile(base.read_text(),str(base),'exec'),{'__name__':'__main__','__file__':str(base)})

p=Path('app/build.gradle')
g=p.read_text().replace('versionCode 30116','versionCode 30117',1).replace("versionName '3.0.116'","versionName '3.0.117'",1)
if 'versionCode 30117' not in g or "versionName '3.0.117'" not in g: raise SystemExit('3.0.117 Gradle target missing')
p.write_text(g)

p=Path('app/src/main/java/com/iceinventory/onhand/MainActivity.java')
s=p.read_text().replace('Onhand Inventory 3.0.116','Onhand Inventory 3.0.117',1)
if 'Onhand Inventory 3.0.117' not in s: raise SystemExit('3.0.117 visible version target missing')
checks={
    'empty inventory prompt':'1. START A NEW INVENTORY\\nPRESS IMPORT BELOW' in s,
    'prompt only when empty':'emptyInventoryHint.setVisibility(allRows.isEmpty()?View.VISIBLE:View.GONE)' in s,
    'list restored after import':'list.setVisibility(allRows.isEmpty()?View.GONE:View.VISIBLE)' in s,
}
missing=[k for k,v in checks.items() if not v]
if missing: raise SystemExit('3.0.117 verification failed: '+', '.join(missing))
p.write_text(s)

p=Path('app/src/main/AndroidManifest.xml')
m=p.read_text().replace('iCE Onhand 3.0.116','iCE Onhand 3.0.117',1)
if 'iCE Onhand 3.0.117' not in m: raise SystemExit('3.0.117 manifest version target missing')
p.write_text(m)

print('Prepared iCE Onhand 3.0.117: empty inventory area now directs the user to Import')
