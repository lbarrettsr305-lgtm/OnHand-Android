from pathlib import Path

base=Path('.github/prepare_30135.py')
exec(compile(base.read_text(),str(base),'exec'),{'__name__':'__main__','__file__':str(base)})

def rep(path, old, new, label):
    p=Path(path); s=p.read_text()
    if old not in s:
        raise SystemExit('3.0.135 TEST target missing: '+label)
    p.write_text(s.replace(old,new,1))

rep('app/build.gradle',
    "applicationId 'com.iceinventory.onhand'",
    "applicationId 'com.iceinventory.onhand.test'",
    'test application id')

p=Path('app/src/main/AndroidManifest.xml'); s=p.read_text()
s=s.replace('android:label="iCE Onhand 3.0.135"',
            'android:label="iCE Onhand TEST 3.0.135"',1)
p.write_text(s)

p=Path('app/src/main/java/com/iceinventory/onhand/MainActivity.java'); s=p.read_text()
s=s.replace('Onhand Inventory 3.0.135','Onhand TEST 3.0.135',1)
p.write_text(s)

print('Prepared side-by-side iCE Onhand TEST 3.0.135 package')
