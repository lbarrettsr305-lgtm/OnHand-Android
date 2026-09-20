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

p.write_text(s)

main=p.read_text()
checks={
 'version':'Onhand Inventory 3.0.137',
 'count role explicit':'else if(ROLE_COUNT_USER.equals(role))',
 'count no-pin block':'This phone is a COUNT USER and cannot create or replace the Master PIN.',
 'count pin unlock':'unlockMasterWithPin(next);',
 'master role refresh':'refreshOperatorStatus();',
 'master role lock':'Master Device Required'
}
missing=[k for k,v in checks.items() if v not in main]
if missing: raise SystemExit('3.0.137 verification failed: '+', '.join(missing))
print('Prepared iCE Onhand 3.0.137: COUNT USER cannot self-promote; existing Master PIN is required')
