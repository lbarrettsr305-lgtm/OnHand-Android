from pathlib import Path

base=Path('.github/prepare_3087.py')
exec(compile(base.read_text(),str(base),'exec'),{'__name__':'__main__','__file__':str(base)})

p=Path('app/src/main/java/com/iceinventory/onhand/FormatConfigActivity.java')
s=p.read_text()
old='''        LinearLayout root=new LinearLayout(this);root.setOrientation(LinearLayout.VERTICAL);root.setBackgroundColor(dark());
'''
new='''        LinearLayout root=new LinearLayout(this);root.setOrientation(LinearLayout.VERTICAL);root.setBackgroundColor(dark());
        root.setOnApplyWindowInsetsListener((v,insets)->{
            v.setPadding(0,0,0,insets.getSystemWindowInsetBottom());
            return insets;
        });
'''
if old not in s:raise SystemExit('3.0.88 target missing: format root')
s=s.replace(old,new,1)
old='''        setContentView(root);
        renderRows();
'''
new='''        setContentView(root);
        root.requestApplyInsets();
        renderRows();
'''
if old not in s:raise SystemExit('3.0.88 target missing: setContentView')
s=s.replace(old,new,1)
p.write_text(s)

p=Path('app/src/main/java/com/iceinventory/onhand/MainActivity.java')
s=p.read_text().replace('Onhand Inventory 3.0.87','Onhand Inventory 3.0.88')
if 'Onhand Inventory 3.0.88' not in s:raise SystemExit('3.0.88 target missing: title version')
p.write_text(s)

p=Path('app/build.gradle');s=p.read_text().replace('versionCode 30087','versionCode 30088',1).replace("versionName '3.0.87'","versionName '3.0.88'",1)
if 'versionCode 30088' not in s or "versionName '3.0.88'" not in s:raise SystemExit('3.0.88 target missing: Gradle version')
p.write_text(s)

p=Path('app/src/main/AndroidManifest.xml');s=p.read_text().replace('iCE Onhand 3.0.87','iCE Onhand 3.0.88')
if 'iCE Onhand 3.0.88' not in s:raise SystemExit('3.0.88 target missing: manifest version')
p.write_text(s)

fmt=Path('app/src/main/java/com/iceinventory/onhand/FormatConfigActivity.java').read_text()
checks={'fixed file footer':'root.addView(save,sp)','navigation safe area':'getSystemWindowInsetBottom()','insets requested':'root.requestApplyInsets()'}
missing=[k for k,v in checks.items() if v not in fmt]
if missing:raise SystemExit('3.0.88 verification failed: '+', '.join(missing))
print('Prepared iCE Onhand 3.0.88: Continue to File stays above Android navigation controls')
