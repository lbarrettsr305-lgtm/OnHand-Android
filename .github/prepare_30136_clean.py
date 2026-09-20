from pathlib import Path

base=Path('.github/prepare_30136.py')
exec(compile(base.read_text(),str(base),'exec'),{'__name__':'__main__','__file__':str(base)})

def rep(path, old, new, label):
    p=Path(path); s=p.read_text()
    if old not in s: raise SystemExit('3.0.136C target missing: '+label)
    p.write_text(s.replace(old,new,1))

rep('app/build.gradle',"applicationId 'com.iceinventory.onhand'","applicationId 'com.iceinventory.onhand.clean136'",'clean applicationId')
rep('app/build.gradle','versionCode 30136','versionCode 40136','clean versionCode')
rep('app/build.gradle',"versionName '3.0.136'","versionName '3.0.136C'",'clean versionName')
rep('app/src/main/AndroidManifest.xml','iCE Onhand 3.0.136','iCE Onhand CLEAN 3.0.136C','clean manifest label')
rep('app/src/main/java/com/iceinventory/onhand/MainActivity.java','Onhand Inventory 3.0.136','Onhand Inventory 3.0.136C CLEAN TEST','clean visible version')

g=Path('app/build.gradle').read_text()
m=Path('app/src/main/AndroidManifest.xml').read_text()
main=Path('app/src/main/java/com/iceinventory/onhand/MainActivity.java').read_text()
checks={
 'unique package':"applicationId 'com.iceinventory.onhand.clean136'" in g,
 'clean version':"versionName '3.0.136C'" in g,
 'unique provider':'${applicationId}.fileprovider' in m,
 'android10 min sdk':'minSdk 24' in g,
 'visible clean test':'3.0.136C CLEAN TEST' in main,
 'no active inventory':'NO ACTIVE INVENTORY' in main
}
missing=[k for k,v in checks.items() if not v]
if missing: raise SystemExit('3.0.136C verification failed: '+', '.join(missing))
print('Prepared iCE Onhand 3.0.136C CLEAN: unique package for Android 10 install diagnosis')
