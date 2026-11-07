"""Add saved-barcode correction, preserving count and batch quantities."""
from pathlib import Path
p=Path("app/src/main/java/com/iceinventory/onhand/InventoryDb.java")
s=p.read_text()
marker="    public double quantityForBarcode(long sessionId, String barcode) {"
assert s.count(marker)==1
method='''    /** Correct an identifier across the current inventory without adding count events. */
    public void correctBarcode(long sessionId,String oldBarcode,String newBarcode,String changedBy) {
        String oldCode=oldBarcode==null?"":oldBarcode.trim();
        String newCode=newBarcode==null?"":newBarcode.trim();
        if(sessionId<=0||oldCode.isEmpty()||newCode.isEmpty())throw new IllegalArgumentException("Enter the correct barcode");
        if(!newCode.matches("[0-9A-Za-z._-]+"))throw new IllegalArgumentException("Barcode cannot contain spaces or special characters");
        if(oldCode.equals(newCode))throw new IllegalArgumentException("Enter a different barcode");
        SQLiteDatabase sql=getWritableDatabase();
        sql.beginTransaction();
        try {
            String[] oldArgs={String.valueOf(sessionId),oldCode};
            String[] newArgs={String.valueOf(sessionId),newCode};
            try(Cursor c=sql.rawQuery("SELECT 1 FROM items WHERE session_id=? AND barcode=? LIMIT 1",oldArgs)){
                if(!c.moveToFirst())throw new IllegalArgumentException("The original item is no longer in this inventory");
            }
            String[] tables={"items","scan_history","store_setup_new_items","retail_price_changes"};
            for(String table:tables){
                try(Cursor c=sql.rawQuery("SELECT 1 FROM "+table+" WHERE session_id=? AND barcode=? COLLATE NOCASE LIMIT 1",newArgs)){
                    if(c.moveToFirst())throw new IllegalArgumentException("That barcode already exists in this inventory. No counts were changed. Review the two items before correcting.");
                }
            }
            createRecoverySnapshot(sessionId,"Before barcode correction: "+oldCode+" to "+newCode);
            ContentValues values=new ContentValues();values.put("barcode",newCode);
            // Keep row IDs, count timestamps, locations, deltas and batch history ranges.
            for(String table:tables)sql.update(table,values,"session_id=? AND barcode=?",oldArgs);
            sql.execSQL("CREATE TABLE IF NOT EXISTS barcode_corrections (id INTEGER PRIMARY KEY AUTOINCREMENT, session_id INTEGER NOT NULL, old_barcode TEXT NOT NULL, new_barcode TEXT NOT NULL, changed_by TEXT NOT NULL DEFAULT '', changed_at INTEGER NOT NULL)");
            ContentValues audit=new ContentValues();
            audit.put("session_id",sessionId);audit.put("old_barcode",oldCode);audit.put("new_barcode",newCode);
            audit.put("changed_by",changedBy==null?"":changedBy);audit.put("changed_at",System.currentTimeMillis());
            sql.insertOrThrow("barcode_corrections",null,audit);
            sql.setTransactionSuccessful();
        } finally {sql.endTransaction();}
    }

'''
p.write_text(s.replace(marker,method+marker,1))
p=Path("app/src/main/java/com/iceinventory/onhand/MainActivity.java")
s=p.read_text()
def replace_once(old,new):
    global s
    assert s.count(old)==1,old[:100]
    s=s.replace(old,new,1)
replace_once('    private static final int REQ_PICK_MANUAL_ITEM_PHOTO=1018;',
             '    private static final int REQ_PICK_MANUAL_ITEM_PHOTO=1018;\n    private static final int REQ_CORRECT_BARCODE_SCAN=1019;\n    private EditText pendingBarcodeCorrectionEntry;')
replace_once('''        TextView info=text(details,15,Color.BLACK,false);box.addView(info);
        EditText adjustment''','''        TextView info=text(details,15,Color.BLACK,false);box.addView(info);
        Button correctBarcode=button("Correct Barcode",0);
        box.addView(correctBarcode,new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT,dp(48)));
        EditText adjustment''')
replace_once('''        dialog.setOnShowListener(x->{
            dialog.getButton(AlertDialog.BUTTON_POSITIVE).setOnClickListener(v->{
                String raw=adjustment''','''        correctBarcode.setOnClickListener(v->{
            dialog.dismiss();
            ensureMasterPin(()->showCorrectBarcodeDialog(r));
        });
        dialog.setOnShowListener(x->{
            dialog.getButton(AlertDialog.BUTTON_POSITIVE).setOnClickListener(v->{
                String raw=adjustment''')
marker="    private void showMoveLocation(InventoryDb.Row row) {"
assert s.count(marker)==1
method='''    private void showCorrectBarcodeDialog(InventoryDb.Row row){
        if(row==null||row.sessionId!=sessionId||!requireCurrentCount())return;
        final long correctionSession=sessionId;
        LinearLayout panel=new LinearLayout(this);panel.setOrientation(LinearLayout.VERTICAL);panel.setPadding(dp(16),dp(8),dp(16),0);
        panel.addView(text("Current barcode: "+row.barcode+"\\n"+row.description+"\\n\\nThis corrects the barcode in every location of this inventory. Quantities, locations, description and retail price are kept.",16,Color.WHITE,false));
        EditText replacement=new EditText(this);
        replacement.setSingleLine(true);replacement.setTextColor(Color.WHITE);replacement.setHintTextColor(Color.LTGRAY);
        replacement.setHint("Scan or type the correct barcode");
        replacement.setInputType(InputType.TYPE_CLASS_TEXT|InputType.TYPE_TEXT_FLAG_NO_SUGGESTIONS);
        panel.addView(replacement,new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT,dp(56)));
        Button scanReplacement=button("Scan Correct Barcode",1);
        panel.addView(scanReplacement,new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT,dp(48)));
        scanReplacement.setOnClickListener(v->{
            pendingBarcodeCorrectionEntry=replacement;
            startActivityForResult(new Intent(this,ScanActivity.class),REQ_CORRECT_BARCODE_SCAN);
        });
        AlertDialog dialog=new AlertDialog.Builder(this).setTitle("Correct Saved Barcode").setView(panel)
            .setNegativeButton("CANCEL",null).setPositiveButton("REVIEW CORRECTION",null).create();
        dialog.setOnDismissListener(d->{if(pendingBarcodeCorrectionEntry==replacement)pendingBarcodeCorrectionEntry=null;});
        dialog.setOnShowListener(d->dialog.getButton(AlertDialog.BUTTON_POSITIVE).setOnClickListener(v->{
            String corrected=replacement.getText().toString().trim();
            if(corrected.isEmpty()||!corrected.matches("[0-9A-Za-z._-]+")){replacement.setError("Scan or type the full barcode without spaces");return;}
            if(corrected.equals(row.barcode)){replacement.setError("Enter a different barcode");return;}
            if(sessionId!=correctionSession){toast("Inventory changed. Open the item again.");dialog.dismiss();return;}
            if(db.latestForBarcode(correctionSession,corrected)!=null){replacement.setError("That barcode already exists. No counts were changed.");return;}
            new AlertDialog.Builder(this).setTitle("Confirm Barcode Correction")
                .setMessage("Change\\n"+row.barcode+"\\nto\\n"+corrected+"?\\n\\nAll quantities and locations stay the same. Files already exported keep the old barcode; re-export the affected reports or batches after this correction.")
                .setNegativeButton("BACK",null)
                .setPositiveButton("CORRECT BARCODE",(confirm,which)->{
                    if(sessionId!=correctionSession||!requireCurrentCount())return;
                    try{
                        db.correctBarcode(correctionSession,row.barcode,corrected,savedUserName());
                        String oldImage=prefs().getString(IMAGE_KEY_PREFIX+row.barcode,"");
                        if(!oldImage.isEmpty()&&prefs().getString(IMAGE_KEY_PREFIX+corrected,"").isEmpty())
                            prefs().edit().putString(IMAGE_KEY_PREFIX+corrected,oldImage).apply();
                        dialog.dismiss();
                        barcode.setText("");description.setText("");qty.setText("");currentPrice="";updatePricePreview();
                        refreshList();highlightAndRevealBarcode(corrected);focusBarcodeWithoutKeyboard();
                        safetyCheckpoint("After barcode correction",true);
                        toast("Barcode corrected. Quantity and locations kept.");
                    }catch(Exception error){showError("Barcode was not corrected",error);}
                }).show();
        }));
        dialog.show();
        replacement.requestFocus();
        replacement.postDelayed(()->showKeyboard(replacement),100);
    }

'''
s=s.replace(marker,method+marker,1)
replace_once('''        if(requestCode==REQ_SCAN_LOCATION){
            if(resultCode''','''        if(requestCode==REQ_CORRECT_BARCODE_SCAN){
            if(resultCode==RESULT_OK&&data!=null&&pendingBarcodeCorrectionEntry!=null){
                String value=data.getStringExtra(ScanActivity.EXTRA_BARCODE);
                if(value!=null){pendingBarcodeCorrectionEntry.setText(value.trim());pendingBarcodeCorrectionEntry.setSelection(pendingBarcodeCorrectionEntry.length());}
            }
            pendingBarcodeCorrectionEntry=null;
            return;
        }
        if(requestCode==REQ_SCAN_LOCATION){
            if(resultCode''')
p.write_text(s)
b=Path("app/build.gradle");s=b.read_text()
assert "versionCode 30260" in s
b.write_text(s.replace("versionCode 30260","versionCode 30261").replace("versionName '3.0.260'","versionName '3.0.261'"))
print("Applied 3.0.261: protected saved-barcode correction with recovery and conflict checks.")
