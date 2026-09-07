from pathlib import Path

base=Path('.github/prepare_3089.py')
exec(compile(base.read_text(),str(base),'exec'),{'__name__':'__main__','__file__':str(base)})

p=Path('app/src/main/java/com/iceinventory/onhand/MainActivity.java')
s=p.read_text()
old='''        TextView accuracy=text("SCAN COUNT ACCURATELY",9,Color.rgb(35,120,255),true);
        accuracy.setGravity(Gravity.CENTER);
        accuracy.setSingleLine(true);
        accuracy.setTextScaleX(0.84f);
        brandMark.addView(accuracy,new LinearLayout.LayoutParams(dp(112),dp(18)));
        LinearLayout.LayoutParams brandLp=new LinearLayout.LayoutParams(dp(112),dp(104));
'''
new='''        TextView accuracy=text("SCAN COUNT ACCURATELY",8,Color.rgb(35,120,255),true);
        accuracy.setGravity(Gravity.CENTER);
        accuracy.setSingleLine(true);
        accuracy.setTextScaleX(0.78f);
        brandMark.addView(accuracy,new LinearLayout.LayoutParams(dp(124),dp(18)));
        LinearLayout.LayoutParams brandLp=new LinearLayout.LayoutParams(dp(124),dp(104));
'''
if old not in s:raise SystemExit('3.0.90 target missing: accuracy slogan sizing')
s=s.replace(old,new,1)
old='''        titleSession=text(sessionName,19,gold(),true);
'''
new='''        titleSession=text(sessionName,17,gold(),true);
'''
if old not in s:raise SystemExit('3.0.90 target missing: inventory filename size')
s=s.replace(old,new,1)
s=s.replace('Onhand Inventory 3.0.89','Onhand Inventory 3.0.90')
if 'Onhand Inventory 3.0.90' not in s:raise SystemExit('3.0.90 target missing: title version')
p.write_text(s)

p=Path('app/build.gradle');s=p.read_text().replace('versionCode 30089','versionCode 30090',1).replace("versionName '3.0.89'","versionName '3.0.90'",1)
if 'versionCode 30090' not in s or "versionName '3.0.90'" not in s:raise SystemExit('3.0.90 target missing: Gradle version')
p.write_text(s)

p=Path('app/src/main/AndroidManifest.xml');s=p.read_text().replace('iCE Onhand 3.0.89','iCE Onhand 3.0.90')
if 'iCE Onhand 3.0.90' not in s:raise SystemExit('3.0.90 target missing: manifest version')
p.write_text(s)

main=Path('app/src/main/java/com/iceinventory/onhand/MainActivity.java').read_text()
checks={'smaller inventory filename':'titleSession=text(sessionName,17','full slogan width':'LinearLayout.LayoutParams(dp(124),dp(18))','manual-entry barcode focus':'focusBarcodeWithoutKeyboard();'}
missing=[k for k,v in checks.items() if v not in main]
if missing:raise SystemExit('3.0.90 verification failed: '+', '.join(missing))
print('Prepared iCE Onhand 3.0.90: smaller inventory filename and fully visible SCAN COUNT ACCURATELY')
