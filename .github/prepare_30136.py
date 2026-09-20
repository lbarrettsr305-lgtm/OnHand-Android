from pathlib import Path
import re

base=Path('.github/prepare_30135.py')
exec(compile(base.read_text(),str(base),'exec'),{'__name__':'__main__','__file__':str(base)})

def rep(path, old, new, label):
    p=Path(path); s=p.read_text()
    if old not in s: raise SystemExit('3.0.136 target missing: '+label)
    p.write_text(s.replace(old,new,1))

rep('app/build.gradle','versionCode 30135','versionCode 30136','Gradle code')
rep('app/build.gradle',"versionName '3.0.135'","versionName '3.0.136'",'Gradle name')
rep('app/src/main/AndroidManifest.xml','iCE Onhand 3.0.135','iCE Onhand 3.0.136','manifest')

p=Path('app/src/main/java/com/iceinventory/onhand/MainActivity.java')
s=p.read_text()
s=s.replace('Onhand Inventory 3.0.135','Onhand Inventory 3.0.136',1)

# A fresh/empty phone should never look like a real inventory is active.
s=s.replace('private String sessionName="Default Inventory";','private String sessionName="NO ACTIVE INVENTORY";',1)
s=s.replace('db.createSession("Default Inventory")','db.createSession("NO ACTIVE INVENTORY")',1)
s=s.replace('sessionName="Default Inventory";','sessionName="NO ACTIVE INVENTORY";',1)
if 'normalizeNoActiveInventoryName();' not in s:
    anchor_init='        buildUi();'
    if anchor_init not in s: raise SystemExit('3.0.136 target missing: initialize buildUi')
    s=s.replace(anchor_init,'        normalizeNoActiveInventoryName();\n        buildUi();',1)

anchor='''    private SharedPreferences prefs(){return getSharedPreferences(SETTINGS,MODE_PRIVATE);}
'''
helper='''    private void normalizeNoActiveInventoryName() {
        String n=sessionName==null?"":sessionName.trim();
        if((n.isEmpty()||"Default Inventory".equalsIgnoreCase(n))&&db.items(sessionId).isEmpty()) {
            db.renameSession(sessionId,"NO ACTIVE INVENTORY");
            sessionName="NO ACTIVE INVENTORY";
        }
    }

'''
if anchor not in s: raise SystemExit('3.0.136 target missing: prefs anchor')
s=s.replace(anchor,helper+anchor,1)

# A COUNT USER that already carries a project Master PIN hash must enter that
# existing PIN. It may not simply create a replacement PIN and promote itself.
pat=r'''    private void ensureMasterPin\(Runnable next\)\{.*?\n    private void changeMasterPin\(\)\{'''
replacement='''    private void ensureMasterPin(Runnable next){
        String existing=prefs().getString(KEY_MASTER_PIN_HASH,"");
        if(isMasterDevice()&&!existing.isEmpty()){next.run();return;}
        if(!existing.isEmpty()){unlockMasterWithPin(next);return;}
        EditText pin=masterPinEntry("New 4-digit Master PIN");
        AlertDialog dialog=new AlertDialog.Builder(this).setTitle("Create Master PIN").setMessage("This phone will become the Master device. The PIN is required to transfer Master access.").setView(pin).setPositiveButton("Continue",null).setNegativeButton("Cancel",null).create();
        dialog.setOnShowListener(x->dialog.getButton(AlertDialog.BUTTON_POSITIVE).setOnClickListener(v->{String value=pin.getText().toString();if(!validMasterPin(value)){toast("Master PIN must be exactly 4 digits");return;}String current=savedUserName();prefs().edit().putString(KEY_DEVICE_ROLE,ROLE_MASTER).putString(KEY_MASTER_PIN_HASH,hashMasterPin(value)).putString(KEY_MASTER_USER,current).apply();refreshOperatorStatus();dialog.dismiss();next.run();}));dialog.show();
    }

    private void unlockMasterWithPin(){unlockMasterWithPin(null);}

    private void unlockMasterWithPin(Runnable next){
        String expected=prefs().getString(KEY_MASTER_PIN_HASH,"");if(expected.isEmpty()){toast("This count file has no Master PIN. Use the original Master phone.");return;}
        EditText pin=masterPinEntry("4-digit Master PIN");AlertDialog dialog=new AlertDialog.Builder(this).setTitle("Transfer Master Access").setMessage("Enter the existing Master PIN. This phone cannot become Master without it.").setView(pin).setPositiveButton("Transfer",null).setNegativeButton("Cancel",null).create();
        dialog.setOnShowListener(x->dialog.getButton(AlertDialog.BUTTON_POSITIVE).setOnClickListener(v->{if(!expected.equals(hashMasterPin(pin.getText().toString()))){toast("Incorrect Master PIN");pin.selectAll();return;}String current=savedUserName();prefs().edit().putString(KEY_DEVICE_ROLE,ROLE_MASTER).putString(KEY_MASTER_USER,current).apply();refreshOperatorStatus();dialog.dismiss();toast("This phone is now the Master device");if(next!=null)next.run();}));dialog.show();
    }

    private void changeMasterPin(){'''
s,n=re.subn(pat,replacement,s,count=1,flags=re.S)
if n!=1: raise SystemExit('3.0.136 target missing: Master PIN methods')

p.write_text(s)

main=p.read_text()
checks={
 'version':'Onhand Inventory 3.0.136',
 'no active default':'sessionName="NO ACTIVE INVENTORY"',
 'empty legacy migration':'normalizeNoActiveInventoryName();',
 'import renames project':'db.renameSession(sessionId,inventoryName);',
 'count user uses existing pin':'if(!existing.isEmpty()){unlockMasterWithPin(next);return;}',
 'master pin callback':'private void unlockMasterWithPin(Runnable next)',
 'master role lock':'Master Device Required'
}
missing=[k for k,v in checks.items() if v not in main]
if missing: raise SystemExit('3.0.136 verification failed: '+', '.join(missing))
print('Prepared iCE Onhand 3.0.136: NO ACTIVE INVENTORY + imported project name + protected Master PIN transfer')
