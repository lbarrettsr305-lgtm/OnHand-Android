from pathlib import Path

# Preserve 3.0.124, then rebuild the main screen after closing a monthly project.
base=Path('.github/prepare_30124.py')
exec(compile(base.read_text(),str(base),'exec'),{'__name__':'__main__','__file__':str(base)})

p=Path('app/build.gradle')
g=p.read_text().replace('versionCode 30124','versionCode 30125',1).replace("versionName '3.0.124'","versionName '3.0.125'",1)
if 'versionCode 30125' not in g or "versionName '3.0.125'" not in g: raise SystemExit('3.0.125 Gradle target missing')
p.write_text(g)

p=Path('app/src/main/java/com/iceinventory/onhand/MainActivity.java')
s=p.read_text().replace('Onhand Inventory 3.0.124','Onhand Inventory 3.0.125',1)
if 'Onhand Inventory 3.0.125' not in s: raise SystemExit('3.0.125 visible version target missing')
p.write_text(s)

p=Path('app/src/main/java/com/iceinventory/onhand/MonthlyInventoryActivity.java')
s=p.read_text()
old='Toast.makeText(this,"Monthly project closed and archived. It can be reopened if a correction is needed.",Toast.LENGTH_LONG).show();finish();'
new='Toast.makeText(this,"Monthly project closed and archived. Use Reopen Last Monthly Project if a correction is needed.",Toast.LENGTH_LONG).show();Intent home=new Intent(this,MainActivity.class);home.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK|Intent.FLAG_ACTIVITY_CLEAR_TASK);startActivity(home);finish();'
if old not in s: raise SystemExit('3.0.125 target missing: close navigation')
s=s.replace(old,new,1)
if 'Intent.FLAG_ACTIVITY_NEW_TASK|Intent.FLAG_ACTIVITY_CLEAR_TASK' not in s: raise SystemExit('3.0.125 verification failed: main screen not rebuilt')
p.write_text(s)

p=Path('app/src/main/AndroidManifest.xml')
m=p.read_text().replace('iCE Onhand 3.0.124','iCE Onhand 3.0.125',1)
if 'iCE Onhand 3.0.125' not in m: raise SystemExit('3.0.125 manifest version target missing')
p.write_text(m)
print('Prepared iCE Onhand 3.0.125: closed project immediately shows Reopen Last Monthly Project')
