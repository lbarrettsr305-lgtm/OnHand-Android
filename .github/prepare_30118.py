from pathlib import Path

# Preserve 3.0.117 and add the scan-test return path plus full Android sharing guidance.
base=Path('.github/prepare_30117.py')
exec(compile(base.read_text(),str(base),'exec'),{'__name__':'__main__','__file__':str(base)})

p=Path('app/build.gradle')
g=p.read_text().replace('versionCode 30117','versionCode 30118',1).replace("versionName '3.0.117'","versionName '3.0.118'",1)
if 'versionCode 30118' not in g or "versionName '3.0.118'" not in g: raise SystemExit('3.0.118 Gradle target missing')
p.write_text(g)

p=Path('app/src/main/java/com/iceinventory/onhand/MainActivity.java')
s=p.read_text().replace('Onhand Inventory 3.0.117','Onhand Inventory 3.0.118',1)
if 'Onhand Inventory 3.0.118' not in s: raise SystemExit('3.0.118 visible version target missing')
if 'getLongExtra(MonthlyInventoryActivity.EXTRA_SESSION_ID,-1L)' not in s: raise SystemExit('3.0.118 requested store session selection missing')
p.write_text(s)

p=Path('app/src/main/AndroidManifest.xml')
m=p.read_text().replace('iCE Onhand 3.0.117','iCE Onhand 3.0.118',1)
if 'iCE Onhand 3.0.118' not in m: raise SystemExit('3.0.118 manifest version target missing')
p.write_text(m)

monthly=Path('app/src/main/java/com/iceinventory/onhand/MonthlyInventoryActivity.java').read_text()
checks={
    'readable disabled steps':'b.setTextColor(Color.WHITE)' in monthly,
    'share all users label':'4. Share File With All Users' in monthly,
    'test scan opens main':'Intent test=new Intent(this,MainActivity.class)' in monthly,
    'back instruction':'Test a scan, then press Back to share the file.' in monthly,
    'full Android chooser':'Quick Share, Bluetooth, Drive or email' in monthly,
}
missing=[k for k,v in checks.items() if not v]
if missing: raise SystemExit('3.0.118 verification failed: '+', '.join(missing))
print('Prepared iCE Onhand 3.0.118: readable steps, store-titled scan test, Back-to-share workflow, and Android sharing menu')
