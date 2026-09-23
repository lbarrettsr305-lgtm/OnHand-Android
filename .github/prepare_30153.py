from pathlib import Path

base = Path('.github/prepare_30152.py')
exec(compile(base.read_text(), str(base), 'exec'), {'__name__': '__main__', '__file__': str(base)})


def rep(path, old, new):
    target = Path(path)
    source = target.read_text()
    if source.count(old) != 1:
        raise SystemExit('3.0.153 expected one target: ' + old[:120])
    target.write_text(source.replace(old, new, 1))


rep('app/build.gradle', 'versionCode 30152', 'versionCode 30153')
rep('app/build.gradle', "versionName '3.0.152'", "versionName '3.0.153'")
rep('app/src/main/AndroidManifest.xml', 'iCE Onhand 3.0.152', 'iCE Onhand 3.0.153')
rep(
    'app/src/main/java/com/iceinventory/onhand/MainActivity.java',
    'Onhand Inventory 3.0.152',
    'Onhand Inventory 3.0.153',
)

print('Prepared iCE OnHand 3.0.153: finalized Add Qty visibility above numeric keyboard')
