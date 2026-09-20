from pathlib import Path

base=Path('.github/prepare_30139.py')
exec(compile(base.read_text(),str(base),'exec'),{'__name__':'__main__','__file__':str(base)})

def rep(path, old, new, label):
    p=Path(path); s=p.read_text()
    if old not in s: raise SystemExit('3.0.140 target missing: '+label)
    p.write_text(s.replace(old,new,1))

rep('app/build.gradle','versionCode 30139','versionCode 30140','Gradle code')
rep('app/build.gradle',"versionName '3.0.139'","versionName '3.0.140'",'Gradle name')
rep('app/src/main/AndroidManifest.xml','iCE Onhand 3.0.139','iCE Onhand 3.0.140','manifest')

p=Path('app/src/main/java/com/iceinventory/onhand/MainActivity.java')
s=p.read_text().replace('Onhand Inventory 3.0.139','Onhand Inventory 3.0.140',1)

old='''        masterUserButton.setOnClickListener(v->{if(masterDevice)changeMasterPin();else unlockMasterWithPin();});'''
new='''        masterUserButton.setOnClickListener(v->{if(masterDevice)changeMasterPin();else ensureMasterPin(()->{});});'''
if old not in s: raise SystemExit('3.0.140 target missing: Master button click handler')
s=s.replace(old,new,1)

old='''        box.addView(masterUserButton,new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT,dp(58)));'''
new='''        box.addView(masterUserButton,new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT,dp(76)));'''
if old not in s: raise SystemExit('3.0.140 target missing: Master button height')
s=s.replace(old,new,1)
p.write_text(s)

main=p.read_text()
checks={
 'version':'Onhand Inventory 3.0.140',
 'correct click':'else ensureMasterPin(()->{});',
 'create path':'No Master PIN exists for this project.',
 'double pin':'Confirm Master PIN',
 'taller button':'ViewGroup.LayoutParams.MATCH_PARENT,dp(76)'
}
missing=[k for k,v in checks.items() if v not in main]
if missing: raise SystemExit('3.0.140 verification failed: '+', '.join(missing))
print('Prepared iCE Onhand 3.0.140: Master button now opens first-time PIN creation')
