from pathlib import Path
import re

base=Path('.github/prepare_30136.py')
exec(compile(base.read_text(),str(base),'exec'),{'__name__':'__main__','__file__':str(base)})

def rep(path, old, new, label):
    p=Path(path); s=p.read_text()
    if old not in s: raise SystemExit('3.0.137 target missing: '+label)
    p.write_text(s.replace(old,new,1))

rep('app/build.gradle','versionCode 30136','versionCode 30137','Gradle code')
rep('app/build.gradle',"versionName '3.0.136'","versionName '3.0.137'",'Gradle name')
rep('app/src/main/AndroidManifest.xml','iCE Onhand 3.0.136','iCE Onhand 3.0.137','manifest')

p=Path('app/src/main/java/com/iceinventory/onhand/MainActivity.java')
s=p.read_text()
s=s.replace('Onhand Inventory 3.0.136','Onhand Inventory 3.0.137',1)

# Hard rule: a device already marked COUNT USER can never create a new Master PIN.
# It must present the existing project PIN. If an older/unprotected file has no
# PIN hash, the user is told to return to the original Master phone / protected file.
pat=r'''    private void ensureMasterPin\(Runnable next\)\{.*?\n    private void unlockMasterWithPin\(\)\{'''
replacement='''    private void ensureMasterPin(Runnable next){
        String role=deviceRole();
        String existing=prefs().getString(KEY_MASTER_PIN_HASH,"");

        if(ROLE_MASTER.equals(role)){
            if(!existing.isEmpty()){next.run();return;}
            // Legacy Master device with no PIN yet: allow it to establish one below.
        } else if(ROLE_COUNT_USER.equals(role)){
            if(existing.isEmpty()){
                new AlertDialog.Builder(this)
                        .setTitle("Master PIN Required")
                        .setMessage("This phone is a COUNT USER and cannot create or replace the Master PIN. Use the original Master phone, or load a protected working file shared from the Master phone.")
                        .setPositiveButton("OK",null).show();
                return;
            }
            unlockMasterWithPin(next);
            return;
        }

        // Only an unassigned phone, or a legacy Master phone, may establish the first PIN.
        EditText pin=masterPinEntry("New 4-digit Master PIN");
        AlertDialog dialog=new AlertDialog.Builder(this).setTitle("Create Master PIN").setMessage("This phone will become the Master device. The PIN is required to transfer Master access.").setView(pin).setPositiveButton("Continue",null).setNegativeButton("Cancel",null).create();
        dialog.setOnShowListener(x->dialog.getButton(AlertDialog.BUTTON_POSITIVE).setOnClickListener(v->{String value=pin.getText().toString();if(!validMasterPin(value)){toast("Master PIN must be exactly 4 digits");return;}String current=savedUserName();prefs().edit().putString(KEY_DEVICE_ROLE,ROLE_MASTER).putString(KEY_MASTER_PIN_HASH,hashMasterPin(value)).putString(KEY_MASTER_USER,current).apply();refreshOperatorStatus();dialog.dismiss();toast("Master PIN created — this phone is now MASTER");next.run();}));
        dialog.show();
    }

    private void unlockMasterWithPin(){'''
s,n=re.subn(pat,replacement,s,count=1,flags=re.S)
if n!=1: raise SystemExit('3.0.137 target missing: ensureMasterPin block')

# The yellow main-screen title is the store/project name, not the imported file name.
# Keep the full source filename separately (existing last_import_filename preference),
# and derive CHEV2620 from names such as "ONHAND CHEV2620 MASTER-08-31-2026.txt".
old='''                String inventoryName=selectedName.trim();
                int dot=inventoryName.lastIndexOf('.');if(dot>0)inventoryName=inventoryName.substring(0,dot);
                if(!inventoryName.isEmpty()) {
                    db.renameSession(sessionId,inventoryName);
                    sessionName=inventoryName;
                }'''
new='''                String inventoryName=projectNameFromImportedFile(selectedName);
                if(!inventoryName.isEmpty()) {
                    db.renameSession(sessionId,inventoryName);
                    sessionName=inventoryName;
                }'''
if old not in s: raise SystemExit('3.0.137 target missing: imported filename/session rename')
s=s.replace(old,new,1)

anchor='''    private String importFileNameKey(){'''
helper='''    private String projectNameFromImportedFile(String fileName){
        String n=fileName==null?"":fileName.trim();
        int slash=Math.max(n.lastIndexOf('/'),n.lastIndexOf('\\\\'));if(slash>=0)n=n.substring(slash+1);
        int dot=n.lastIndexOf('.');if(dot>0)n=n.substring(0,dot);
        String upper=n.toUpperCase(Locale.US);
        if(upper.startsWith("ONHAND ")){
            String rest=n.substring(7).trim();
            String restUpper=rest.toUpperCase(Locale.US);
            int master=restUpper.indexOf(" MASTER-");
            if(master>0)rest=rest.substring(0,master).trim();
            if(!rest.isEmpty())return rest;
        }
        return n;
    }

'''
if anchor not in s: raise SystemExit('3.0.137 target missing: importFileNameKey anchor')
s=s.replace(anchor,helper+anchor,1)

p.write_text(s)

main=p.read_text()
checks={
 'version':'Onhand Inventory 3.0.137',
 'count role explicit':'else if(ROLE_COUNT_USER.equals(role))',
 'count no-pin block':'This phone is a COUNT USER and cannot create or replace the Master PIN.',
 'count pin unlock':'unlockMasterWithPin(next);',
 'master role refresh':'refreshOperatorStatus();',
 'master role lock':'Master Device Required',
 'store title parser':'private String projectNameFromImportedFile(String fileName)',
 'store title not filename':'String inventoryName=projectNameFromImportedFile(selectedName);'
}
missing=[k for k,v in checks.items() if v not in main]
if missing: raise SystemExit('3.0.137 verification failed: '+', '.join(missing))
print('Prepared iCE Onhand 3.0.137: Master PIN hard lock + store title separated from source filename')
