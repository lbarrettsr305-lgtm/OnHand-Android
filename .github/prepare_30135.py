from pathlib import Path

base=Path('.github/prepare_30134.py')
exec(compile(base.read_text(),str(base),'exec'),{'__name__':'__main__','__file__':str(base)})

def rep(path, old, new, label):
    p=Path(path); s=p.read_text()
    if old not in s: raise SystemExit('3.0.135 target missing: '+label)
    p.write_text(s.replace(old,new,1))

rep('app/build.gradle','versionCode 30134','versionCode 30135','Gradle code')
rep('app/build.gradle',"versionName '3.0.134'","versionName '3.0.135'",'Gradle name')
rep('app/src/main/AndroidManifest.xml','iCE Onhand 3.0.134','iCE Onhand 3.0.135','manifest')

p=Path('app/src/main/java/com/iceinventory/onhand/MainActivity.java'); s=p.read_text()
s=s.replace('Onhand Inventory 3.0.134','Onhand Inventory 3.0.135',1)

old='''        operatorStatus=text(operatorStatusText(),13,Color.rgb(120,255,140),true);
        operatorStatus.setSingleLine(true);
        operatorStatus.setPadding(0,dp(2),0,dp(2));'''
new='''        String safeOperatorStatus;
        try{safeOperatorStatus=operatorStatusText();}
        catch(Throwable roleError){Log.w(TAG,"Operator status startup fallback",roleError);safeOperatorStatus="User: NOT SET  •  Role: COUNT USER";}
        operatorStatus=text(safeOperatorStatus,13,Color.rgb(120,255,140),true);
        operatorStatus.setSingleLine(true);
        operatorStatus.setPadding(0,dp(2),0,dp(2));'''
if old not in s: raise SystemExit('3.0.135 target missing: operator status block')
s=s.replace(old,new,1)

old='''        if(savedUserName().isEmpty())root.postDelayed(()->promptUserName(false),450);'''
new='''        try{
            if(savedUserName().isEmpty())root.postDelayed(()->{
                try{promptUserName(false);}
                catch(Throwable promptError){Log.e(TAG,"Username prompt suppressed to keep startup alive",promptError);}
            },650);
        }catch(Throwable promptScheduleError){Log.e(TAG,"Username prompt scheduling suppressed",promptScheduleError);}'''
if old not in s: raise SystemExit('3.0.135 target missing: startup username prompt')
s=s.replace(old,new,1)

p.write_text(s)

main=p.read_text()
checks={
 'version':'Onhand Inventory 3.0.135',
 'safe operator':'Operator status startup fallback',
 'safe prompt':'Username prompt suppressed to keep startup alive',
 'master pin':'KEY_MASTER_PIN_HASH',
 'master role':'ROLE_MASTER'
}
missing=[k for k,v in checks.items() if v not in main]
if missing: raise SystemExit('3.0.135 verification failed: '+', '.join(missing))
print('Prepared iCE Onhand 3.0.135: Android 10 safe startup around user/role UI')
