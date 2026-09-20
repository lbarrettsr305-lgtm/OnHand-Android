from pathlib import Path
import re

base=Path('.github/prepare_30140.py')
exec(compile(base.read_text(),str(base),'exec'),{'__name__':'__main__','__file__':str(base)})

def rep(path, old, new, label):
    p=Path(path); s=p.read_text()
    if old not in s: raise SystemExit('3.0.141 target missing: '+label)
    p.write_text(s.replace(old,new,1))

rep('app/build.gradle','versionCode 30140','versionCode 30141','Gradle code')
rep('app/build.gradle',"versionName '3.0.140'","versionName '3.0.141'",'Gradle name')
rep('app/src/main/AndroidManifest.xml','iCE Onhand 3.0.140','iCE Onhand 3.0.141','manifest')

p=Path('app/src/main/java/com/iceinventory/onhand/MainActivity.java')
s=p.read_text().replace('Onhand Inventory 3.0.140','Onhand Inventory 3.0.141',1)

pat=r'''    private void readImport\(Uri uri\) \{.*?\n    private void performImport\(Uri uri,boolean replaceCurrent\) \{'''
replacement='''    private void readImport(Uri uri) {
        if(uri==null)return;
        new AlertDialog.Builder(this)
                .setTitle("Replace Current Inventory?")
                .setMessage("RECOMMENDED DEFAULT\\n\\nThis will safely replace the current inventory with the selected file. A recovery checkpoint is created first, and your User Name remains unchanged.\\n\\nUse Advanced Import Options only when a Master specifically needs to append another file.")
                .setPositiveButton("REPLACE CURRENT INVENTORY",(d,w)->performImport(uri,true))
                .setNeutralButton("ADVANCED OPTIONS",(d,w)->verifyMasterPinForAdvancedImport(()->showAdvancedImportOptions(uri)))
                .setNegativeButton("Cancel",null)
                .show();
    }

    private void verifyMasterPinForAdvancedImport(Runnable next){
        String expected=prefs().getString(KEY_MASTER_PIN_HASH,"");
        if(expected.isEmpty()){toast("Advanced import is locked until a Master PIN is created");return;}
        EditText pin=masterPinEntry("4-digit Master PIN");
        AlertDialog dialog=new AlertDialog.Builder(this)
                .setTitle("Protected Advanced Import")
                .setMessage("Enter the Master PIN. This unlocks advanced import for this action only and does not change this phone's role.")
                .setView(pin)
                .setPositiveButton("UNLOCK",null)
                .setNegativeButton("Cancel",null)
                .create();
        dialog.setOnShowListener(x->dialog.getButton(AlertDialog.BUTTON_POSITIVE).setOnClickListener(v->{
            if(!expected.equals(hashMasterPin(pin.getText().toString()))){toast("Incorrect Master PIN");pin.selectAll();return;}
            dialog.dismiss();
            next.run();
        }));
        dialog.show();
    }

    private void showAdvancedImportOptions(Uri uri){
        new AlertDialog.Builder(this)
                .setTitle("Advanced Import Options")
                .setMessage("Append keeps all current inventory rows and adds the selected file. Use this only when intentionally combining source files before counting.")
                .setPositiveButton("APPEND TO CURRENT INVENTORY",(d,w)->performImport(uri,false))
                .setNegativeButton("Cancel",null)
                .show();
    }

    private void performImport(Uri uri,boolean replaceCurrent) {'''
s,n=re.subn(pat,replacement,s,count=1,flags=re.S)
if n!=1: raise SystemExit('3.0.141 target missing: readImport block')
p.write_text(s)

# Add the safe import rule to in-app Help under Receiving a Shared Count File.
h=Path('app/src/main/java/com/iceinventory/onhand/HelpActivity.java')
helptext=h.read_text()
old='''7. Test one barcode, then begin counting.\\n\\nDo not choose Petrosoft Monthly or LiqPOS on a receiving count device. Those choices are for the person preparing the project.");'''
new='''7. Choose REPLACE CURRENT INVENTORY when prompted. This is the safe default and prevents duplicate items.\\n8. Confirm the store name and test one barcode, then begin counting.\\n\\nAdvanced Append is protected by the Master PIN and should only be used when a Master intentionally combines source files. Do not choose Petrosoft Monthly or LiqPOS on a receiving count device. Those choices are for the person preparing the project.");'''
if old not in helptext: raise SystemExit('3.0.141 target missing: shared-file Help text')
helptext=helptext.replace(old,new,1)
h.write_text(helptext)

main=p.read_text()
checks={
 'version':'Onhand Inventory 3.0.141',
 'replace default':'REPLACE CURRENT INVENTORY',
 'advanced button':'ADVANCED OPTIONS',
 'protected method':'verifyMasterPinForAdvancedImport',
 'pin verification':'expected.equals(hashMasterPin',
 'role unchanged':"does not change this phone's role",
 'append advanced':'APPEND TO CURRENT INVENTORY',
 'help safe default':'safe default and prevents duplicate items'
}
alltext=main+'\n'+h.read_text()
missing=[k for k,v in checks.items() if v not in alltext]
if missing: raise SystemExit('3.0.141 verification failed: '+', '.join(missing))
print('Prepared iCE Onhand 3.0.141: replace-default import with PIN-protected advanced append')
