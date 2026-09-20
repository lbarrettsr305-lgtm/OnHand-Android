from pathlib import Path

base=Path('.github/prepare_30133.py')
exec(compile(base.read_text(),str(base),'exec'),{'__name__':'__main__','__file__':str(base)})

def rep(path, old, new, label):
    p=Path(path); s=p.read_text()
    if old not in s: raise SystemExit('3.0.134 target missing: '+label)
    p.write_text(s.replace(old,new,1))

rep('app/build.gradle','versionCode 30133','versionCode 30134','Gradle code')
rep('app/build.gradle',"versionName '3.0.133'","versionName '3.0.134'",'Gradle name')
rep('app/src/main/AndroidManifest.xml','iCE Onhand 3.0.133','iCE Onhand 3.0.134','manifest')

p=Path('app/src/main/java/com/iceinventory/onhand/MainActivity.java'); s=p.read_text()
s=s.replace('Onhand Inventory 3.0.133','Onhand Inventory 3.0.134',1)
old='''        titleSession=text(sessionName,17,gold(),true);
        heading.addView(ice);heading.addView(app);heading.addView(titleSession);'''
new='''        titleSession=text(sessionName,16,gold(),true);
        titleSession.setMaxLines(2);
        operatorStatus=text(operatorStatusText(),13,Color.rgb(120,255,140),true);
        operatorStatus.setSingleLine(true);
        operatorStatus.setPadding(0,dp(2),0,dp(2));
        heading.addView(ice);heading.addView(app);heading.addView(titleSession);heading.addView(operatorStatus);'''
if old not in s: raise SystemExit('3.0.134 target missing: actual header insertion')
s=s.replace(old,new,1)
p.write_text(s)

main=p.read_text()
checks={'version':'Onhand Inventory 3.0.134','header assignment':'operatorStatus=text(operatorStatusText()','header attachment':'heading.addView(operatorStatus)','compact store title':'titleSession=text(sessionName,16'}
missing=[k for k,v in checks.items() if v not in main]
if missing: raise SystemExit('3.0.134 verification failed: '+', '.join(missing))
print('Prepared iCE Onhand 3.0.134: fixed visible username and role under wrapped store name')
