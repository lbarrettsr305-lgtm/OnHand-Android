from pathlib import Path

base=Path('.github/prepare_30127.py')
exec(compile(base.read_text(),str(base),'exec'),{'__name__':'__main__','__file__':str(base)})

p=Path('app/build.gradle')
g=p.read_text().replace('versionCode 30127','versionCode 30128',1).replace("versionName '3.0.127'","versionName '3.0.128'",1)
if 'versionCode 30128' not in g: raise SystemExit('3.0.128 Gradle target missing')
p.write_text(g)

p=Path('app/src/main/java/com/iceinventory/onhand/MainActivity.java')
s=p.read_text().replace('Onhand Inventory 3.0.127','Onhand Inventory 3.0.128',1)
replaced=False
for old in ('⬇ Import CSV','↓ Import','⬇ Import'):
    if old in s:
        s=s.replace(old,'↓ START HERE — IMPORT',1)
        replaced=True
        break
if not replaced: raise SystemExit('3.0.128 import button target missing')
p.write_text(s)

p=Path('app/src/main/AndroidManifest.xml')
m=p.read_text().replace('iCE Onhand 3.0.127','iCE Onhand 3.0.128',1)
if 'iCE Onhand 3.0.128' not in m: raise SystemExit('3.0.128 manifest version missing')
p.write_text(m)

print('Prepared iCE Onhand 3.0.128: START HERE arrow added to Import button')
