from pathlib import Path

# Build on the verified Excel-first 3.0.84 source.
base = Path('.github/prepare_3084.py')
exec(compile(base.read_text(), str(base), 'exec'), {'__name__': '__main__', '__file__': str(base)})

p = Path('app/src/main/java/com/iceinventory/onhand/MainActivity.java')
s = p.read_text()

def rep(old, new, label):
    global s
    if old not in s:
        raise SystemExit('3.0.85 target missing: ' + label)
    s = s.replace(old, new, 1)

rep('''    private static final int REQ_BACKUP_FOLDER=1082;\n''',
    '''    private static final int REQ_BACKUP_FOLDER=1082;\n    private static final int REQ_RESTORE_EXTERNAL=1085;\n''',
    'restore request code')

rep('''    private static final String KEY_BACKUP_TREE_URI="recovery_backup_tree_uri";\n''',
    '''    private static final String KEY_BACKUP_TREE_URI="recovery_backup_tree_uri";\n    private static final String KEY_SAFETY_SETUP_PROMPTED="safety_setup_prompted_3085";\n''',
    'safety setup key')

rep('''    private long lastSafetyCheckpoint=0L;\n    private int countsSinceSafetyCheckpoint=0;\n''',
    '''    private long lastSafetyCheckpoint=0L;\n    private int countsSinceSafetyCheckpoint=0;\n    private final android.os.Handler safetyHandler=new android.os.Handler(android.os.Looper.getMainLooper());\n    private final Runnable pendingCountBackup=this::automaticCountCheckpoint;\n''',
    'debounced backup fields')

rep('''        barcode.postDelayed(this::focusBarcodeWithoutKeyboard,120);\n    }\n''',
    '''        barcode.postDelayed(this::focusBarcodeWithoutKeyboard,120);\n        barcode.postDelayed(this::showDataSafetySetupIfNeeded,450);\n    }\n''',
    'startup recovery prompt')

rep('''    @Override protected void onPause(){\n        super.onPause();\n        safetyCheckpoint("App background",false);\n    }\n''',
    '''    @Override protected void onPause(){\n        safetyHandler.removeCallbacks(pendingCountBackup);\n        if(countsSinceSafetyCheckpoint>0)automaticCountCheckpoint();\n        else safetyCheckpoint("App background",false);\n        super.onPause();\n    }\n''',
    'forced pending backup on pause')

handler_anchor = '''        if(requestCode==REQ_BACKUP_FOLDER){\n'''
restore_handler = '''        if(requestCode==REQ_RESTORE_EXTERNAL){\n            if(resultCode==RESULT_OK&&data!=null&&data.getData()!=null)readExternalRecoveryBackup(data.getData());\n            return;\n        }\n'''
if handler_anchor not in s:
    raise SystemExit('3.0.85 target missing: activity result handler')
s = s.replace(handler_anchor, restore_handler + handler_anchor, 1)

rep('''    }    private void noteCountForSafety(){\n        countsSinceSafetyCheckpoint++;\n        if(countsSinceSafetyCheckpoint>=10)safetyCheckpoint("Automatic after 10 counts",false);\n    }\n\n''',
    '''    }    private void noteCountForSafety(){\n        countsSinceSafetyCheckpoint++;\n        safetyHandler.removeCallbacks(pendingCountBackup);\n        safetyHandler.postDelayed(pendingCountBackup,900L);\n    }\n\n    private void automaticCountCheckpoint(){\n        if(db==null||sessionId<=0||countsSinceSafetyCheckpoint<=0)return;\n        try{\n            db.createRecoverySnapshot(sessionId,"Automatic after saved count");\n            lastSafetyCheckpoint=System.currentTimeMillis();countsSinceSafetyCheckpoint=0;\n            writeExternalSafetyBackup("Automatic after saved count",false);\n        }catch(Exception e){Log.e(TAG,"Automatic count backup failed",e);}\n    }\n\n''',
    'automatic saved-count backup')

rep('''    private void chooseBackupFolder(){\n        Intent i=new Intent(Intent.ACTION_OPEN_DOCUMENT_TREE);\n        i.addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION|Intent.FLAG_GRANT_WRITE_URI_PERMISSION|Intent.FLAG_GRANT_PERSISTABLE_URI_PERMISSION|Intent.FLAG_GRANT_PREFIX_URI_PERMISSION);\n        startActivityForResult(i,REQ_BACKUP_FOLDER);\n    }\n\n''',
    '''    private void chooseBackupFolder(){\n        Intent i=new Intent(Intent.ACTION_OPEN_DOCUMENT_TREE);\n        i.addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION|Intent.FLAG_GRANT_WRITE_URI_PERMISSION|Intent.FLAG_GRANT_PERSISTABLE_URI_PERMISSION|Intent.FLAG_GRANT_PREFIX_URI_PERMISSION);\n        startActivityForResult(i,REQ_BACKUP_FOLDER);\n    }\n\n    private void showDataSafetySetupIfNeeded(){\n        String folder=prefs().getString(KEY_BACKUP_TREE_URI,"");\n        if(folder!=null&&!folder.trim().isEmpty())return;\n        if(prefs().getBoolean(KEY_SAFETY_SETUP_PROMPTED,false))return;\n        prefs().edit().putBoolean(KEY_SAFETY_SETUP_PROMPTED,true).apply();\n        new AlertDialog.Builder(this).setTitle("Protect Your Inventory")\n                .setMessage("Choose a backup folder so counts remain recoverable if the app is accidentally deleted. If you reinstalled the app, restore an existing iCE OnHand backup now.")\n                .setPositiveButton("CHOOSE BACKUP FOLDER",(d,w)->chooseBackupFolder())\n                .setNeutralButton("RESTORE EXISTING BACKUP",(d,w)->chooseExternalRecoveryBackup())\n                .setNegativeButton("Later",null).show();\n    }\n\n    private void chooseExternalRecoveryBackup(){\n        Intent i=new Intent(Intent.ACTION_OPEN_DOCUMENT);i.addCategory(Intent.CATEGORY_OPENABLE);i.setType("text/plain");\n        startActivityForResult(i,REQ_RESTORE_EXTERNAL);\n    }\n\n    private void readExternalRecoveryBackup(Uri uri){\n        String restoredName="Recovered Inventory";boolean valid=false;java.util.ArrayList<String[]> rows=new java.util.ArrayList<>();\n        try(InputStream is=getContentResolver().openInputStream(uri);BufferedReader br=new BufferedReader(new InputStreamReader(is,StandardCharsets.UTF_8))){\n            String line=br.readLine();if(!"iCE OnHand Recovery Backup".equals(line))throw new Exception("This is not an iCE OnHand recovery backup.");\n            while((line=br.readLine())!=null){\n                if(line.startsWith("Inventory\\t")){restoredName=line.substring(10).trim();continue;}\n                if(line.equals("Barcode\\tDescription\\tPrice\\tQuantity\\tLocation\\tUpdatedAt")){valid=true;break;}\n            }\n            if(!valid)throw new Exception("The recovery backup header is incomplete.");\n            while((line=br.readLine())!=null){String[] c=line.split("\\t",-1);if(c.length>=6&&!c[0].trim().isEmpty())rows.add(c);}\n        }catch(Exception e){showError("Restore failed",e);return;}\n        final String inventoryName=restoredName.trim().isEmpty()?"Recovered Inventory":restoredName.trim();\n        new AlertDialog.Builder(this).setTitle("Restore External Backup?")\n                .setMessage("Inventory: "+inventoryName+"\\nItems: "+rows.size()+"\\n\\nThis will replace the currently displayed inventory.")\n                .setPositiveButton("RESTORE",(d,w)->restoreExternalRecoveryRows(inventoryName,rows))\n                .setNegativeButton("Cancel",null).show();\n    }\n\n    private void restoreExternalRecoveryRows(String inventoryName,java.util.ArrayList<String[]> rows){\n        boolean started=false;\n        try{\n            safetyCheckpoint("Before External Restore",true);\n            db.beginInventoryTransaction();started=true;db.clearSessionItems(sessionId);db.renameSession(sessionId,inventoryName);\n            for(String[] c:rows){\n                int amount;long when;try{amount=Integer.parseInt(c[3].trim());}catch(Exception ignored){amount=0;}\n                try{when=Long.parseLong(c[5].trim());}catch(Exception ignored){when=System.currentTimeMillis();}\n                String loc=c[4].trim().isEmpty()?"Main":c[4].trim();db.addLocation(loc);db.addOrIncrementAt(sessionId,c[0],c[1],c[2],amount,loc,when);\n            }\n            db.setInventoryTransactionSuccessful();sessionName=inventoryName;\n        }catch(Exception e){showError("Restore failed",e);return;}finally{if(started)db.endInventoryTransaction();}\n        refreshLocations();refreshList();safetyCheckpoint("After External Restore",true);toast("External backup restored • "+rows.size()+" lines");\n        new AlertDialog.Builder(this).setTitle("Keep Automatic Backups Active")\n                .setMessage("Select the folder containing your backups so OnHand can continue protecting every saved count.")\n                .setPositiveButton("CHOOSE BACKUP FOLDER",(d,w)->chooseBackupFolder()).setNegativeButton("Later",null).show();\n    }\n\n''',
    'external restore helpers')

rep('''        Button now=button("Create Backup Now",1);now.setOnClickListener(v->{safetyCheckpoint("Manual Backup",true);toast("Recovery backup created");});box.addView(now,new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT,dp(48)));\n        Button hist=button("View Scan / Count History",0);''',
    '''        Button now=button("Create Backup Now",1);now.setOnClickListener(v->{safetyCheckpoint("Manual Backup",true);toast("Recovery backup created");});box.addView(now,new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT,dp(48)));\n        Button restoreFile=button("Restore External Backup",1);restoreFile.setOnClickListener(v->chooseExternalRecoveryBackup());box.addView(restoreFile,new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT,dp(48)));\n        Button hist=button("View Scan / Count History",0);''',
    'Recovery Center restore button')

s = s.replace('Onhand Inventory 3.0.84','Onhand Inventory 3.0.85')
p.write_text(s)

p=Path('app/build.gradle');s=p.read_text().replace('versionCode 30084','versionCode 30085',1).replace("versionName '3.0.84'","versionName '3.0.85'",1)
if 'versionCode 30085' not in s or "versionName '3.0.85'" not in s:raise SystemExit('3.0.85 target missing: Gradle version')
p.write_text(s)
p=Path('app/src/main/AndroidManifest.xml');s=p.read_text().replace('iCE Onhand 3.0.84','iCE Onhand 3.0.85')
if 'iCE Onhand 3.0.85' not in s:raise SystemExit('3.0.85 target missing: manifest version')
p.write_text(s)

main=Path('app/src/main/java/com/iceinventory/onhand/MainActivity.java').read_text()
checks={'Excel default':'Export New Counts Only — Excel (.xlsx)','reinstall prompt':'Protect Your Inventory','external restore':'readExternalRecoveryBackup(Uri uri)','restore button':'Restore External Backup','saved-count backup':'Automatic after saved count','pause flush':'if(countsSinceSafetyCheckpoint>0)automaticCountCheckpoint()'}
missing=[k for k,v in checks.items() if v not in main]
if missing:raise SystemExit('3.0.85 verification failed: '+', '.join(missing))
print('Prepared iCE Onhand 3.0.85: uninstall-resistant external restore + automatic saved-count protection + Excel default')
