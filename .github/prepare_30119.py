from pathlib import Path

# Preserve 3.0.118, then make scan testing optional and sharing immediately available.
base=Path('.github/prepare_30118.py')
exec(compile(base.read_text(),str(base),'exec'),{'__name__':'__main__','__file__':str(base)})

p=Path('app/build.gradle')
g=p.read_text().replace('versionCode 30118','versionCode 30119',1).replace("versionName '3.0.118'","versionName '3.0.119'",1)
if 'versionCode 30119' not in g or "versionName '3.0.119'" not in g: raise SystemExit('3.0.119 Gradle target missing')
p.write_text(g)

p=Path('app/src/main/java/com/iceinventory/onhand/MainActivity.java')
s=p.read_text().replace('Onhand Inventory 3.0.118','Onhand Inventory 3.0.119',1)
if 'Onhand Inventory 3.0.119' not in s: raise SystemExit('3.0.119 visible version target missing')
p.write_text(s)

p=Path('app/src/main/AndroidManifest.xml')
m=p.read_text().replace('iCE Onhand 3.0.118','iCE Onhand 3.0.119',1)
if 'iCE Onhand 3.0.119' not in m: raise SystemExit('3.0.119 manifest version target missing')
p.write_text(m)

p=Path('app/src/main/java/com/iceinventory/onhand/MonthlyInventoryActivity.java')
s=p.read_text()

old='loadDevice=button("3. Load & Verify on This Device");loadDevice.setOnClickListener(v->confirmLoadDevice());'
new='loadDevice=button("3. Test Scan on This Device");loadDevice.setOnClickListener(v->confirmTestScan());'
if old not in s: raise SystemExit('3.0.119 target missing: load button')
s=s.replace(old,new,1)

old='b.append(deviceLoaded?"\\n✓ LOADED AND VERIFIED ON THIS DEVICE":"\\n○ LOAD AND VERIFY ON THIS DEVICE");'
new='b.append(deviceLoaded?"\\n✓ TEST SCAN READY — PRESS BACK TO SHARE":"\\n○ TEST SCAN ON THIS DEVICE (OPTIONAL)");'
if old not in s: raise SystemExit('3.0.119 target missing: progress wording')
s=s.replace(old,new,1)

old='private void confirmLoadDevice(){new android.app.AlertDialog.Builder(this).setTitle("Load OnHand Count File").setMessage("Create a new inventory on this device from the verified Petrosoft data? All quantities will start at zero.").setPositiveButton("Load & Verify",(d,w)->loadOnDevice()).setNegativeButton("Cancel",null).show();}'
new='private void confirmTestScan(){new android.app.AlertDialog.Builder(this).setTitle("Test Scan").setMessage("Open a temporary zero-quantity inventory for a test scan? Press Back after testing to return and share the count file.").setPositiveButton("Start Test Scan",(d,w)->loadOnDevice()).setNegativeButton("Cancel",null).show();}'
if old not in s: raise SystemExit('3.0.119 target missing: confirmation')
s=s.replace(old,new,1)

old='Toast.makeText(this,"Loaded "+rows.size()+" barcodes. Test a scan, then press Back to share the file.",Toast.LENGTH_LONG).show();'
new='Toast.makeText(this,"Test inventory ready with "+rows.size()+" barcodes. Test a scan, then press Back to share.",Toast.LENGTH_LONG).show();'
if old not in s: raise SystemExit('3.0.119 target missing: test message')
s=s.replace(old,new,1)

old='shareOnHand.setEnabled(onHandCreated&&deviceLoaded&&onHandUri!=null);'
new='shareOnHand.setEnabled(onHandCreated&&onHandUri!=null);'
if old not in s: raise SystemExit('3.0.119 target missing: share gate')
s=s.replace(old,new,1)

checks={
    'test scan label':'3. Test Scan on This Device' in s,
    'no load and verify label':'3. Load & Verify on This Device' not in s,
    'optional test wording':'TEST SCAN ON THIS DEVICE (OPTIONAL)' in s,
    'direct share enabled':'shareOnHand.setEnabled(onHandCreated&&onHandUri!=null)' in s,
    'back to share instruction':'Press Back after testing to return and share the count file.' in s,
    'Android share targets':'Quick Share, Bluetooth, Drive or email' in s,
}
missing=[k for k,v in checks.items() if not v]
if missing: raise SystemExit('3.0.119 verification failed: '+', '.join(missing))
p.write_text(s)
print('Prepared iCE Onhand 3.0.119: optional test scan, no file reload, direct share, Back-to-share return')
