from pathlib import Path

# Preserve 3.0.121, then return from sharing directly into counting on the primary device.
base=Path('.github/prepare_30121.py')
exec(compile(base.read_text(),str(base),'exec'),{'__name__':'__main__','__file__':str(base)})

p=Path('app/build.gradle')
g=p.read_text().replace('versionCode 30121','versionCode 30122',1).replace("versionName '3.0.121'","versionName '3.0.122'",1)
if 'versionCode 30122' not in g or "versionName '3.0.122'" not in g: raise SystemExit('3.0.122 Gradle target missing')
p.write_text(g)

p=Path('app/src/main/java/com/iceinventory/onhand/MainActivity.java')
s=p.read_text().replace('Onhand Inventory 3.0.121','Onhand Inventory 3.0.122',1)
if 'Onhand Inventory 3.0.122' not in s: raise SystemExit('3.0.122 visible version target missing')
p.write_text(s)

p=Path('app/src/main/AndroidManifest.xml')
m=p.read_text().replace('iCE Onhand 3.0.121','iCE Onhand 3.0.122',1)
if 'iCE Onhand 3.0.122' not in m: raise SystemExit('3.0.122 manifest version target missing')
p.write_text(m)

p=Path('app/src/main/java/com/iceinventory/onhand/MonthlyInventoryActivity.java')
s=p.read_text()

old='private static final int PICK_SOURCE=5101,SAVE_MASTER=5102,SAVE_ONHAND=5103,PICK_COUNTS=5104,SAVE_COMBINED=5105,SAVE_CLIENT=5106,SAVE_AUDIT=5107;'
new='private static final int PICK_SOURCE=5101,SAVE_MASTER=5102,SAVE_ONHAND=5103,PICK_COUNTS=5104,SAVE_COMBINED=5105,SAVE_CLIENT=5106,SAVE_AUDIT=5107,SHARE_ONHAND=5108;'
if old not in s: raise SystemExit('3.0.122 target missing: request codes')
s=s.replace(old,new,1)

old='private boolean sourceReady,masterCreated,onHandCreated,deviceLoaded,countsReady,validated;'
new='private boolean sourceReady,masterCreated,onHandCreated,deviceLoaded,countsReady,validated,countLaunchPending;\n    private long deviceSessionId=-1;'
if old not in s: raise SystemExit('3.0.122 target missing: state fields')
s=s.replace(old,new,1)

old='@Override protected void onActivityResult(int request,int result,Intent data){super.onActivityResult(request,result,data);if(result!=RESULT_OK||data==null)return;try{'
new='@Override protected void onActivityResult(int request,int result,Intent data){super.onActivityResult(request,result,data);if(request==SHARE_ONHAND){launchCountAfterShare();return;}if(result!=RESULT_OK||data==null)return;try{'
if old not in s: raise SystemExit('3.0.122 target missing: activity result')
s=s.replace(old,new,1)

old='deviceLoaded=true;String loadedName=base()+" "+day();'
new='deviceLoaded=true;deviceSessionId=id;String loadedName=base()+" "+day();'
if old not in s: raise SystemExit('3.0.122 target missing: loaded session')
s=s.replace(old,new,1)

old='Toast.makeText(this,"Test inventory ready with "+rows.size()+" barcodes. Test a scan, then press Back to share.",Toast.LENGTH_LONG).show();showProgress();setEnabledState();Intent test=new Intent(this,MainActivity.class);'
new='String ready=countLaunchPending?"Inventory ready with "+rows.size()+" barcodes. Begin counting on this machine.":"Test inventory ready with "+rows.size()+" barcodes. Test a scan, then press Back to share.";countLaunchPending=false;Toast.makeText(this,ready,Toast.LENGTH_LONG).show();showProgress();setEnabledState();Intent test=new Intent(this,MainActivity.class);'
if old not in s: raise SystemExit('3.0.122 target missing: ready message')
s=s.replace(old,new,1)

old='showNextStep();startActivity(Intent.createChooser(i,"Share with users — Quick Share, Bluetooth, Drive or email"));}'
new='startActivityForResult(Intent.createChooser(i,"Share with users — Quick Share, Bluetooth, Drive or email"),SHARE_ONHAND);}'
if old not in s: raise SystemExit('3.0.122 target missing: share launch')
s=s.replace(old,new,1)

anchor='''    private void showNextStep(){'''
method='''    private void launchCountAfterShare(){showNextStep();if(deviceLoaded&&deviceSessionId>0){String loadedName=base()+" "+day();Intent count=new Intent(this,MainActivity.class);count.putExtra(EXTRA_SESSION_ID,deviceSessionId);count.putExtra(EXTRA_SESSION_NAME,loadedName);Toast.makeText(this,"Shared file complete. Begin counting on this machine.",Toast.LENGTH_LONG).show();startActivity(count);}else{countLaunchPending=true;loadOnDevice();}}

'''+anchor
if anchor not in s: raise SystemExit('3.0.122 target missing: next step method')
s=s.replace(anchor,method,1)

old='private void showNextStep(){nextStep.setText("NEXT STEP\\nUsers import the shared file and complete the physical count.\\nWhen all users finish, press 5. Select All User Count Files.");nextStep.setVisibility(View.VISIBLE);chooseCounts.setBackgroundColor(Color.rgb(255,193,7));chooseCounts.setTextColor(Color.BLACK);status.setText("FILE SHARED / READY FOR USERS\\n\\nNext: complete the physical inventory. After all users export their counts, press 5. Select All User Count Files.");status.setTextColor(Color.rgb(180,235,255));}'
new='private void showNextStep(){nextStep.setText("COUNTING STARTED ON THIS MACHINE\\nContinue the physical count here.\\nAfter every user finishes and exports, press 5. Select All User Count Files.");nextStep.setVisibility(View.VISIBLE);chooseCounts.setBackgroundColor(Color.rgb(255,193,7));chooseCounts.setTextColor(Color.BLACK);status.setText("PHYSICAL COUNT IN PROGRESS\\n\\nAfter all users export their counts, return here and press 5. Select All User Count Files.");status.setTextColor(Color.rgb(180,235,255));}'
if old not in s: raise SystemExit('3.0.122 target missing: next-step wording')
s=s.replace(old,new,1)

checks={
    'share result launches count':'if(request==SHARE_ONHAND){launchCountAfterShare();return;}' in s,
    'chooser result requested':'startActivityForResult(Intent.createChooser' in s,
    'existing test session reused':'deviceLoaded&&deviceSessionId>0' in s,
    'fresh count created when needed':'countLaunchPending=true;loadOnDevice()' in s,
    'count instruction':'Begin counting on this machine.' in s,
    'post-count continuation':'After every user finishes and exports, press 5.' in s,
}
missing=[k for k,v in checks.items() if not v]
if missing: raise SystemExit('3.0.122 verification failed: '+', '.join(missing))
p.write_text(s)
print('Prepared iCE Onhand 3.0.122: share file, then automatically launch counting on this machine')
