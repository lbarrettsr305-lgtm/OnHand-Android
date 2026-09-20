from pathlib import Path
import re

base=Path('.github/prepare_30138.py')
try:
    exec(compile(base.read_text(),str(base),'exec'),{'__name__':'__main__','__file__':str(base)})
except SystemExit as e:
    if e.code not in (0,None):
        raise

def rep(path, old, new, label):
    p=Path(path); s=p.read_text()
    if old not in s: raise SystemExit('3.0.139 target missing: '+label)
    p.write_text(s.replace(old,new,1))

rep('app/build.gradle','versionCode 30138','versionCode 30139','Gradle code')
rep('app/build.gradle',"versionName '3.0.138'","versionName '3.0.139'",'Gradle name')
rep('app/src/main/AndroidManifest.xml','iCE Onhand 3.0.138','iCE Onhand 3.0.139','manifest')

p=Path('app/src/main/java/com/iceinventory/onhand/MainActivity.java')
s=p.read_text().replace('Onhand Inventory 3.0.138','Onhand Inventory 3.0.139',1)

# If no Master PIN exists anywhere in the project, the selected Audit Manager
# phone may perform the one-time initialization. Existing projects still require
# the current PIN before Master access can be transferred.
pat=r'''    private void ensureMasterPin\(Runnable next\)\{.*?\n    private void unlockMasterWithPin\(\)\{'''
replacement='''    private void ensureMasterPin(Runnable next){
        String existing=prefs().getString(KEY_MASTER_PIN_HASH,"");
        if(isMasterDevice()&&!existing.isEmpty()){next.run();return;}
        if(!existing.isEmpty()){unlockMasterWithPin(next);return;}

        LinearLayout fields=new LinearLayout(this);
        fields.setOrientation(LinearLayout.VERTICAL);
        fields.setPadding(dp(24),0,dp(24),0);
        EditText pin=masterPinEntry("New 4-digit Master PIN");
        EditText confirm=masterPinEntry("Confirm Master PIN");
        fields.addView(pin);
        fields.addView(confirm);

        AlertDialog dialog=new AlertDialog.Builder(this)
                .setTitle("Create Master PIN")
                .setMessage("No Master PIN exists for this project. This phone will become the Master device. Enter the same new PIN twice and keep it safe.")
                .setView(fields)
                .setPositiveButton("MAKE THIS PHONE MASTER",null)
                .setNegativeButton("Cancel",null)
                .create();
        dialog.setOnShowListener(x->dialog.getButton(AlertDialog.BUTTON_POSITIVE).setOnClickListener(v->{
            String value=pin.getText().toString();
            String confirmation=confirm.getText().toString();
            if(!validMasterPin(value)){toast("Master PIN must be exactly 4 digits");pin.selectAll();return;}
            if(!value.equals(confirmation)){toast("PINs do not match");confirm.selectAll();return;}
            String current=savedUserName();
            if(current.isEmpty()){toast("Set User Name first");dialog.dismiss();promptUserName(false);return;}
            prefs().edit()
                    .putString(KEY_DEVICE_ROLE,ROLE_MASTER)
                    .putString(KEY_MASTER_PIN_HASH,hashMasterPin(value))
                    .putString(KEY_MASTER_USER,current)
                    .apply();
            refreshOperatorStatus();
            dialog.dismiss();
            toast(current+" is now the Master Report User");
            next.run();
        }));
        dialog.show();
    }

    private void unlockMasterWithPin(){'''
s,n=re.subn(pat,replacement,s,count=1,flags=re.S)
if n!=1: raise SystemExit('3.0.139 target missing: ensureMasterPin block')

old='''        String masterActionLabel=masterDevice?"CHANGE MASTER PIN":(prefs().getString(KEY_MASTER_PIN_HASH,"").isEmpty()&&localMasterBootstrapAllowed()?"INITIALIZE THIS PHONE AS MASTER":"MAKE THIS PHONE MASTER — PIN REQUIRED");'''
new='''        String masterActionLabel=masterDevice?"CHANGE MASTER PIN":(prefs().getString(KEY_MASTER_PIN_HASH,"").isEmpty()?"MAKE THIS PHONE MASTER — CREATE PIN":"MAKE THIS PHONE MASTER — PIN REQUIRED");'''
if old not in s: raise SystemExit('3.0.139 target missing: Master action label')
s=s.replace(old,new,1)
p.write_text(s)

# Add a dedicated Master setup section to in-app Help.
h=Path('app/src/main/java/com/iceinventory/onhand/HelpActivity.java')
helptext=h.read_text()
anchor='''  section("3. Petrosoft Monthly Inventory",'''
master='''  section("3. Master Phone Setup and PIN",
   "Only the designated Audit Manager phone should be made the Master. The Master phone can combine count-user files and create final reports.\\n\\nFIRST MASTER SETUP\\n1. Set the User Name on the phone that will be the Master.\\n2. Open Options.\\n3. Tap MAKE THIS PHONE MASTER — CREATE PIN.\\n4. Enter a new 4-digit Master PIN.\\n5. Enter the same PIN again to confirm it.\\n6. Confirm the main screen shows Role: MASTER.\\n\\nThe first phone may create the Master PIN only when the project has no existing Master PIN. If a Master PIN already exists, changing or transferring Master access requires that existing PIN. Other phones remain COUNT USER devices and cannot open combined or final Master reports. Keep the Master PIN private and stored safely.");

  section("4. Petrosoft Monthly Inventory",'''
if anchor not in helptext: raise SystemExit('3.0.139 target missing: Help Petrosoft section')
helptext=helptext.replace(anchor,master,1)
for oldnum,newnum,title in [
    (4,5,'LiqPOS Inventory'),
    (5,6,'Scanning and Quantities'),
    (6,7,'Locations'),
    (7,8,'Sharing With Count Users'),
    (8,9,'Combining User Counts'),
    (9,10,'Exporting Reports'),
    (10,11,'Return to Counting / Adjust'),
    (11,12,'Close a Project Safely')]:
    old=f'  section("{oldnum}. {title}",'
    new=f'  section("{newnum}. {title}",'
    if old not in helptext: raise SystemExit('3.0.139 target missing: Help '+title)
    helptext=helptext.replace(old,new,1)
h.write_text(helptext)

main=p.read_text()
checks={
 'version':'Onhand Inventory 3.0.139',
 'first setup':'No Master PIN exists for this project.',
 'confirm field':'Confirm Master PIN',
 'double entry':'PINs do not match',
 'master role':'putString(KEY_DEVICE_ROLE,ROLE_MASTER)',
 'master user':'putString(KEY_MASTER_USER,current)',
 'first master label':'MAKE THIS PHONE MASTER — CREATE PIN',
 'existing transfer':'if(!existing.isEmpty()){unlockMasterWithPin(next);return;}',
 'help section':'Master Phone Setup and PIN'
}
alltext=main+'\n'+h.read_text()
missing=[k for k,v in checks.items() if v not in alltext]
if missing: raise SystemExit('3.0.139 verification failed: '+', '.join(missing))
print('Prepared iCE Onhand 3.0.139: first Master PIN recovery plus Help instructions')
