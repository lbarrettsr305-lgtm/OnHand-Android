from pathlib import Path

base=Path('.github/prepare_30137.py')
try:
    exec(compile(base.read_text(),str(base),'exec'),{'__name__':'__main__','__file__':str(base)})
except SystemExit as e:
    if e.code not in (0,None):
        raise

def rep(path, old, new, label):
    p=Path(path); s=p.read_text()
    if old not in s: raise SystemExit('3.0.138 target missing: '+label)
    p.write_text(s.replace(old,new,1))

rep('app/build.gradle','versionCode 30137','versionCode 30138','Gradle code')
rep('app/build.gradle',"versionName '3.0.137'","versionName '3.0.138'",'Gradle name')
rep('app/src/main/AndroidManifest.xml','iCE Onhand 3.0.137','iCE Onhand 3.0.138','manifest')

p=Path('app/src/main/java/com/iceinventory/onhand/MainActivity.java')
s=p.read_text().replace('Onhand Inventory 3.0.137','Onhand Inventory 3.0.138',1)

# A phone that actually owns a locally-created LiqPOS or Monthly workflow may
# bootstrap the first Master PIN once. Imported/shared Count User phones cannot.
anchor='''    private boolean isMasterDevice(){return ROLE_MASTER.equals(deviceRole());}\n'''
helper='''    private boolean localMasterBootstrapAllowed(){
        boolean liq=getSharedPreferences("liqpos_workflow_state",MODE_PRIVATE).getBoolean("active",false);
        android.content.SharedPreferences mw=getSharedPreferences("monthly_workflow_state",MODE_PRIVATE);
        boolean monthly=mw.getBoolean("active",false)||mw.getBoolean("archived",false);
        return liq||monthly;
    }

'''
if anchor not in s: raise SystemExit('3.0.138 target missing: isMasterDevice anchor')
s=s.replace(anchor,anchor+helper,1)

old='''        } else if(ROLE_COUNT_USER.equals(role)){
            if(existing.isEmpty()){
                new AlertDialog.Builder(this)
                        .setTitle("Protected Master PIN Missing")
                        .setMessage("This is an older or unprotected count file. To make the Audit Manager phone MASTER: on the source/master phone create the 4-digit Master PIN and share the protected OnHand working file again. Import that protected file on this phone, then tap MAKE THIS PHONE MASTER and enter the PIN.")
                        .setPositiveButton("OK",null).show();
                return;
            }
            unlockMasterWithPin(next);
            return;
        }

        // Only an unassigned phone, or a legacy Master phone, may establish the first PIN.
        EditText pin=masterPinEntry("New 4-digit Master PIN");
        AlertDialog dialog=new AlertDialog.Builder(this).setTitle("Create Master PIN").setMessage("This phone will become the Master device. The PIN is required to transfer Master access.").setView(pin).setPositiveButton("Continue",null).setNegativeButton("Cancel",null).create();'''
new='''        } else if(ROLE_COUNT_USER.equals(role)){
            if(existing.isEmpty()){
                if(!localMasterBootstrapAllowed()){
                    new AlertDialog.Builder(this)
                            .setTitle("Protected Master PIN Missing")
                            .setMessage("This is a shared Count User phone. It cannot create the Master PIN. Use the source/master phone to create the PIN and share the protected working file again.")
                            .setPositiveButton("OK",null).show();
                    return;
                }
                // This phone owns the locally-created workflow and may initialize the first Master PIN.
            } else {
                unlockMasterWithPin(next);
                return;
            }
        }

        // Only an unassigned phone, a legacy Master phone, or the local workflow owner may establish the first PIN.
        EditText pin=masterPinEntry("New 4-digit Master PIN");
        AlertDialog dialog=new AlertDialog.Builder(this).setTitle("Initialize Master Phone").setMessage("Create the 4-digit Master PIN for this locally-created inventory. This phone will become MASTER. Share only the protected working file with Count Users.").setView(pin).setPositiveButton("Make Master",null).setNegativeButton("Cancel",null).create();'''
if old not in s: raise SystemExit('3.0.138 target missing: Count User bootstrap block')
s=s.replace(old,new,1)

old_btn='''        Button masterUserButton=button(masterDevice?"CHANGE MASTER PIN":"MAKE THIS PHONE MASTER — PIN REQUIRED",2);'''
new_btn='''        String masterActionLabel=masterDevice?"CHANGE MASTER PIN":(prefs().getString(KEY_MASTER_PIN_HASH,"").isEmpty()&&localMasterBootstrapAllowed()?"INITIALIZE THIS PHONE AS MASTER":"MAKE THIS PHONE MASTER — PIN REQUIRED");
        Button masterUserButton=button(masterActionLabel,2);'''
if old_btn not in s: raise SystemExit('3.0.138 target missing: Master action button')
s=s.replace(old_btn,new_btn,1)

p.write_text(s)

main=p.read_text()
checks={
 'version':'Onhand Inventory 3.0.138',
 'local bootstrap method':'private boolean localMasterBootstrapAllowed()',
 'liq owner':'liqpos_workflow_state',
 'monthly owner':'monthly_workflow_state',
 'shared phones blocked':'This is a shared Count User phone. It cannot create the Master PIN.',
 'bootstrap label':'INITIALIZE THIS PHONE AS MASTER',
 'bootstrap title':'Initialize Master Phone',
 'pin transfer preserved':'unlockMasterWithPin(next);'
}
missing=[k for k,v in checks.items() if v not in main]
if missing: raise SystemExit('3.0.138 verification failed: '+', '.join(missing))
print('Prepared iCE Onhand 3.0.138: locally-created workflow can initialize Master PIN; shared Count Users remain locked')
