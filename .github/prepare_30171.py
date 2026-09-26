from pathlib import Path

base = Path('.github/prepare_30170.py')
exec(compile(base.read_text(), str(base), 'exec'), {'__name__': '__main__', '__file__': str(base)})


def rep(path, old, new, label):
    p = Path(path)
    s = p.read_text()
    if s.count(old) != 1:
        raise SystemExit('3.0.171 target ' + label + ' count ' + str(s.count(old)))
    p.write_text(s.replace(old, new, 1))


rep('app/build.gradle', 'versionCode 30170', 'versionCode 30171', 'code')
rep('app/build.gradle', "versionName '3.0.170'", "versionName '3.0.171'", 'name')
rep('app/src/main/AndroidManifest.xml', 'iCE Onhand 3.0.170', 'iCE Onhand 3.0.171', 'manifest')
rep('app/src/main/java/com/iceinventory/onhand/MainActivity.java',
    'Onhand Inventory 3.0.170', 'Onhand Inventory 3.0.171', 'header')

db = 'app/src/main/java/com/iceinventory/onhand/InventoryDb.java'
rep(db,
'''    public void resetSessionForReplacementImport(long sessionId) {
''',
'''    public long clearAllInventoryData() {
        SQLiteDatabase sql=getWritableDatabase();
        ensureRecoveryTables(sql);
        sql.beginTransaction();
        try {
            sql.delete("recovery_snapshot_items",null,null);
            sql.delete("recovery_snapshots",null,null);
            sql.delete("export_batches",null,null);
            sql.delete("scan_history",null,null);
            sql.delete("items",null,null);
            sql.delete("sessions",null,null);
            sql.delete("locations",null,null);
            sql.delete("app_meta","key=?",new String[]{"location_master"});
            ensureDefaults(sql);
            long id=-1L;
            try(Cursor c=sql.rawQuery("SELECT id FROM sessions ORDER BY created_at DESC,id DESC LIMIT 1",null)){
                if(c.moveToFirst())id=c.getLong(0);
            }
            sql.setTransactionSuccessful();
            return id;
        } finally {sql.endTransaction();}
    }

    public void resetSessionForReplacementImport(long sessionId) {
''', 'database reset')

main = 'app/src/main/java/com/iceinventory/onhand/MainActivity.java'
rep(main,
'''        Button zeroPin=button(zeroPinButtonLabel(),0);
        zeroPin.setOnClickListener(v->changeZeroPasscode());
        box.addView(zeroPin,new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT,dp(50)));
''',
'''        Button zeroPin=button(zeroPinButtonLabel(),0);
        zeroPin.setOnClickListener(v->changeZeroPasscode());
        box.addView(zeroPin,new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT,dp(50)));
        if(masterDevice){
            Button clearAll=button("MASTER: CLEAR ALL INVENTORIES",2);
            clearAll.setTypeface(Typeface.DEFAULT,Typeface.BOLD);
            clearAll.setTextSize(15);
            clearAll.setOnClickListener(v->confirmClearAllInventories());
            LinearLayout.LayoutParams clearLp=new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT,dp(58));
            clearLp.setMargins(0,dp(8),0,0);box.addView(clearAll,clearLp);
        }
''', 'reset option button')

rep(main,
'''    private String installedVersion() {
''',
'''    private void confirmClearAllInventories(){
        if(!isMasterDevice()){toast("Only the Master phone can clear all inventories");return;}
        String expected=prefs().getString(KEY_MASTER_PIN_HASH,"");
        if(expected.isEmpty()){toast("Create the Master PIN first");return;}
        LinearLayout fields=new LinearLayout(this);fields.setOrientation(LinearLayout.VERTICAL);fields.setPadding(dp(22),0,dp(22),0);
        EditText pin=masterPinEntry("4-digit Master PIN");
        EditText word=new EditText(this);word.setSingleLine(true);word.setHint("Type CLEAR");word.setInputType(InputType.TYPE_CLASS_TEXT|InputType.TYPE_TEXT_FLAG_CAP_CHARACTERS);
        fields.addView(pin);fields.addView(word);
        AlertDialog dialog=new AlertDialog.Builder(this)
            .setTitle("Clear All OnHand Inventories?")
            .setMessage("This permanently removes every inventory project, item count, user batch, location total, scan history, and in-app recovery point from this phone. Chief, the Master role, Master PIN, and general settings are kept. Files already saved in Downloads or Google Drive are not deleted.\n\nEnter the Master PIN and type CLEAR to continue.")
            .setView(fields).setPositiveButton("CLEAR ALL INVENTORIES",null).setNegativeButton("Cancel",null).create();
        dialog.setOnShowListener(x->dialog.getButton(AlertDialog.BUTTON_POSITIVE).setOnClickListener(v->{
            if(!expected.equals(hashMasterPin(pin.getText().toString()))){toast("Incorrect Master PIN");pin.selectAll();return;}
            if(!"CLEAR".equals(word.getText().toString().trim().toUpperCase(Locale.US))){toast("Type CLEAR to confirm");word.selectAll();return;}
            try{
                long freshId=db.clearAllInventoryData();
                getSharedPreferences("monthly_workflow_state",MODE_PRIVATE).edit().clear().apply();
                getSharedPreferences("liqpos_workflow_state",MODE_PRIVATE).edit().clear().apply();
                new java.io.File(getFilesDir(),"monthly_workflow_source.xlsx").delete();
                java.io.File shared=new java.io.File(getCacheDir(),"shared");java.io.File[] cached=shared.listFiles();if(cached!=null)for(java.io.File file:cached)file.delete();
                activeSessionId=freshId;sessionId=freshId;sessionName="Default Inventory";lastBarcode="";currentLocation="Main";
                prefs().edit().putLong(KEY_ACTIVE_SESSION,freshId).apply();
                dialog.dismiss();refreshLocations();refreshList();refreshOperatorStatus();
                toast("All inventories cleared — Master settings kept");
                showNewSessionDialog();
            }catch(Exception e){showError("Could not clear inventories",e);}
        }));
        dialog.show();
    }

    private String installedVersion() {
''', 'reset confirmation flow')

inventory_db = Path(db).read_text()
main_text = Path(main).read_text()
checks = {
    'version': "versionName '3.0.171'" in Path('app/build.gradle').read_text(),
    'db reset': 'public long clearAllInventoryData()' in inventory_db,
    'preserve prefs': 'Chief, the Master role, Master PIN, and general settings are kept.' in main_text,
    'pin verify': 'expected.equals(hashMasterPin(pin.getText().toString()))' in main_text,
    'clear word': '"CLEAR".equals(word.getText().toString().trim().toUpperCase(Locale.US))' in main_text,
    'new prompt': 'showNewSessionDialog();' in main_text,
    'workflow reset': 'getSharedPreferences("monthly_workflow_state",MODE_PRIVATE).edit().clear().apply();' in main_text,
}
bad=[k for k,v in checks.items() if not v]
if bad: raise SystemExit('3.0.171 checks failed: '+', '.join(bad))
print('Prepared iCE OnHand 3.0.171: Master PIN protected clear-all inventory reset')
