from pathlib import Path

base = Path('.github/prepare_30176.py')
exec(compile(base.read_text(), str(base), 'exec'), {'__name__': '__main__', '__file__': str(base)})


def rep(path, old, new, label):
    p = Path(path); s = p.read_text()
    if s.count(old) != 1:
        raise SystemExit('3.0.177 target '+label+' count '+str(s.count(old)))
    p.write_text(s.replace(old, new, 1))


rep('app/build.gradle','versionCode 30176','versionCode 30177','code')
rep('app/build.gradle',"versionName '3.0.176'","versionName '3.0.177'",'name')
rep('app/src/main/AndroidManifest.xml','iCE Onhand 3.0.176','iCE Onhand 3.0.177','manifest')

main='app/src/main/java/com/iceinventory/onhand/MainActivity.java'
rep(main,'Onhand Inventory 3.0.176','Onhand Inventory 3.0.177','header')

old='''    private void promptUserName(boolean continueExport) {
        EditText input=new EditText(this);
        input.setSingleLine(true);
        input.setHint("User name");
        input.setText(savedUserName());
        if(input.getText().length()>0)input.setSelection(input.getText().length());
        AlertDialog dialog=new AlertDialog.Builder(this)
                .setTitle("User Name")
                .setMessage("This name is saved on this device and added automatically to every export filename.")
                .setView(input)
                .setPositiveButton("Save",null)
                .setNegativeButton("Cancel",null)
                .create();
        dialog.setOnShowListener(x->dialog.getButton(AlertDialog.BUTTON_POSITIVE).setOnClickListener(v->{
            String n=input.getText().toString().trim();
            if(n.isEmpty()){toast("Enter a user name");return;}
            android.content.SharedPreferences.Editor editor=prefs().edit().putString(KEY_USER_NAME,n);
            if(isMasterDevice()&&savedMasterUserName().isEmpty())editor.putString(KEY_MASTER_USER,n);
            editor.apply();
            refreshOperatorStatus();
            dialog.dismiss();
            toast("User name saved: "+n);
            if(continueExport)showExportDialog();
        }));
        dialog.show();
    }
'''

new='''    private void promptUserName(boolean continueExport) {
        final String[] counters={"Chief","RobertFad","JoseFad","Lbsr","Lbjr","QuselahJ","MataiJ","DelilahW","AdrianB","HailahJ"};
        new AlertDialog.Builder(this)
                .setTitle("SELECT COUNTER NAME")
                .setMessage("Choose the person using this phone. The selected name is remembered and added to completed-count filenames.")
                .setItems(counters,(d,which)->saveSelectedCounterName(counters[which],continueExport))
                .setPositiveButton("ADD NEW COUNTER",(d,w)->verifyMasterPinForNewCounter(()->promptNewCounterName(continueExport)))
                .setNegativeButton("Cancel",null)
                .show();
    }

    private void saveSelectedCounterName(String name,boolean continueExport) {
        String n=name==null?"":name.trim();if(n.isEmpty()){toast("Select a counter name");return;}
        android.content.SharedPreferences.Editor editor=prefs().edit().putString(KEY_USER_NAME,n);
        if(isMasterDevice()&&savedMasterUserName().isEmpty())editor.putString(KEY_MASTER_USER,n);
        editor.apply();refreshOperatorStatus();toast("Counter selected: "+n);if(continueExport)showExportDialog();
    }

    private void verifyMasterPinForNewCounter(Runnable next) {
        String key=isMasterDevice()?KEY_MASTER_PIN_HASH:KEY_AUTHORIZED_MASTER_PIN_HASH;
        String expected=prefs().getString(key,"");
        if(expected.isEmpty()){toast(isMasterDevice()?"Create the Master PIN first":"Import the Master store file before adding a new counter");return;}
        EditText pin=masterPinEntry("4-digit Master PIN");
        AlertDialog dialog=new AlertDialog.Builder(this).setTitle("Master Approval Required").setMessage("Enter the Master PIN to add a name that is not in the approved Counter Name Lookup.").setView(pin).setPositiveButton("UNLOCK",null).setNegativeButton("Cancel",null).create();
        dialog.setOnShowListener(x->dialog.getButton(AlertDialog.BUTTON_POSITIVE).setOnClickListener(v->{if(!expected.equals(hashMasterPin(pin.getText().toString()))){toast("Incorrect Master PIN");pin.selectAll();return;}dialog.dismiss();next.run();}));dialog.show();
    }

    private void promptNewCounterName(boolean continueExport) {
        EditText input=new EditText(this);input.setSingleLine(true);input.setHint("New counter name");
        AlertDialog dialog=new AlertDialog.Builder(this).setTitle("ADD NEW COUNTER").setMessage("Enter the counter name exactly as it should appear in export filenames.").setView(input).setPositiveButton("SAVE",null).setNegativeButton("Cancel",null).create();
        dialog.setOnShowListener(x->dialog.getButton(AlertDialog.BUTTON_POSITIVE).setOnClickListener(v->{String n=input.getText().toString().trim();if(n.isEmpty()){toast("Enter a counter name");return;}dialog.dismiss();saveSelectedCounterName(n,continueExport);}));dialog.show();
    }
'''
rep(main,old,new,'counter name lookup')

s=Path(main).read_text()
checks={
 'version':"versionName '3.0.177'" in Path('app/build.gradle').read_text(),
 'lookup':'"Chief","RobertFad","JoseFad","Lbsr","Lbjr","QuselahJ","MataiJ","DelilahW","AdrianB","HailahJ"' in s,
 'new protected':'verifyMasterPinForNewCounter' in s and 'KEY_AUTHORIZED_MASTER_PIN_HASH' in s,
 'remembered':'putString(KEY_USER_NAME,n)' in s,
 'short filename':'nextCompleteExportNumber' in s,
}
bad=[k for k,v in checks.items() if not v]
if bad: raise SystemExit('3.0.177 checks failed: '+', '.join(bad))
print('Prepared iCE OnHand 3.0.177: approved Counter Name Lookup with Master-protected additions')
