from pathlib import Path

base=Path('.github/prepare_30143.py')
exec(compile(base.read_text(),str(base),'exec'),{'__name__':'__main__','__file__':str(base)})

def rep(path,old,new):
    p=Path(path);s=p.read_text()
    if s.count(old)!=1:raise SystemExit('3.0.144 expected one target: '+old[:70])
    p.write_text(s.replace(old,new,1))

rep('app/build.gradle','versionCode 30143','versionCode 30144')
rep('app/build.gradle',"versionName '3.0.143'","versionName '3.0.144'")
rep('app/src/main/AndroidManifest.xml','iCE Onhand 3.0.143','iCE Onhand 3.0.144')
m='app/src/main/java/com/iceinventory/onhand/MainActivity.java'
rep(m,'Onhand Inventory 3.0.143','Onhand Inventory 3.0.144')
rep(m,
'''        new AlertDialog.Builder(this).setTitle("Inventories / Previous")
                .setMessage("Previous inventories open for review only. Select CURRENT COUNT before scanning.")
                .setItems(names,(d,w)->{''',
'''        hideKeyboard();
        new AlertDialog.Builder(this).setTitle("Inventories / Previous — older files are read only")
                .setItems(names,(d,w)->{''')

source=Path(m).read_text()
assert '.setTitle("Inventories / Previous — older files are read only")' in source
assert '.setItems(names,(d,w)->{' in source
print('Prepared iCE OnHand 3.0.144: Master inventory picker displays file rows without a conflicting message')
