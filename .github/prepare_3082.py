from pathlib import Path
import runpy, re

# Preserve the verified 3.0.81 behavior first.
runpy.run_path('.github/prepare_3081.py', run_name='__main__')

# -----------------------------------------------------------------------------
# 3.0.82 DATA SAFETY: append-only quantity history + local recovery snapshots.
# Existing inventory rows are not migrated/re-keyed; safety tables are additive.
# -----------------------------------------------------------------------------
p=Path('app/src/main/java/com/iceinventory/onhand/InventoryDb.java')
s=p.read_text()

if 'private static final int DB_VERSION = 2;' in s:
    s=s.replace('private static final int DB_VERSION = 2;','private static final int DB_VERSION = 3;',1)

# Recovery data classes.
marker='''    public static final class Session {\n        public long id;\n        public String name;\n    }\n'''
extra='''    public static final class Snapshot {\n        public long id;\n        public long sessionId;\n        public long createdAt;\n        public String reason;\n        public int lineCount;\n        public int unitTotal;\n    }\n\n    public static final class History {\n        public long id;\n        public long sessionId;\n        public String barcode;\n        public String description;\n        public int quantityDelta;\n        public String location;\n        public String source;\n        public long createdAt;\n    }\n'''
if 'public static final class Snapshot' not in s:
    if marker not in s: raise SystemExit('3.0.82 DB target missing: Session class')
    s=s.replace(marker,marker+'\n'+extra,1)

# Ensure upgrade creates only additive safety tables.
old='''    @Override public void onUpgrade(SQLiteDatabase db, int oldVersion, int newVersion) {\n        if (oldVersion < 2) ensurePriceColumn(db);\n    }\n'''
new='''    @Override public void onUpgrade(SQLiteDatabase db, int oldVersion, int newVersion) {\n        if (oldVersion < 2) ensurePriceColumn(db);\n        if (oldVersion < 3) ensureRecoveryTables(db);\n    }\n'''
if old in s:
    s=s.replace(old,new,1)
elif 'if (oldVersion < 3) ensureRecoveryTables(db);' not in s:
    raise SystemExit('3.0.82 DB target missing: onUpgrade')

# verifyReady is always called at app start; make it self-healing.
old='''        ensurePriceColumn(db);\n        ensureDefaults(db);\n    }\n\n    public long createSession'''
new='''        ensurePriceColumn(db);\n        ensureDefaults(db);\n        ensureRecoveryTables(db);\n    }\n\n    public long createSession'''
if old in s:
    s=s.replace(old,new,1)
elif 'ensureRecoveryTables(db);\n    }\n\n    public long createSession' not in s:
    raise SystemExit('3.0.82 DB target missing: verifyReady end')

# Also initialize on every writable open, protecting old installs even if version metadata is odd.
old='''            ensurePriceColumn(db);\n            ensureDefaults(db);\n        }\n    }\n'''
new='''            ensurePriceColumn(db);\n            ensureDefaults(db);\n            ensureRecoveryTables(db);\n        }\n    }\n'''
if old in s:
    s=s.replace(old,new,1)

# Add safety-table creation before ensureDefaults method.
marker='''    private void ensureDefaults(SQLiteDatabase db) {\n'''
helpers='''    private void ensureRecoveryTables(SQLiteDatabase db) {\n        db.execSQL("CREATE TABLE IF NOT EXISTS scan_history (id INTEGER PRIMARY KEY AUTOINCREMENT, session_id INTEGER NOT NULL, barcode TEXT NOT NULL DEFAULT '', description TEXT NOT NULL DEFAULT '', quantity_delta INTEGER NOT NULL DEFAULT 0, location TEXT NOT NULL DEFAULT '', source TEXT NOT NULL DEFAULT '', created_at INTEGER NOT NULL)");\n        db.execSQL("CREATE INDEX IF NOT EXISTS idx_scan_history_session_time ON scan_history(session_id,created_at DESC)");\n        db.execSQL("CREATE TABLE IF NOT EXISTS recovery_snapshots (id INTEGER PRIMARY KEY AUTOINCREMENT, session_id INTEGER NOT NULL, created_at INTEGER NOT NULL, reason TEXT NOT NULL DEFAULT '', line_count INTEGER NOT NULL DEFAULT 0, unit_total INTEGER NOT NULL DEFAULT 0)");\n        db.execSQL("CREATE INDEX IF NOT EXISTS idx_recovery_snapshots_session_time ON recovery_snapshots(session_id,created_at DESC)");\n        db.execSQL("CREATE TABLE IF NOT EXISTS recovery_snapshot_items (snapshot_id INTEGER NOT NULL, barcode TEXT NOT NULL, description TEXT NOT NULL DEFAULT '', price TEXT NOT NULL DEFAULT '', quantity INTEGER NOT NULL DEFAULT 0, location TEXT NOT NULL DEFAULT '', updated_at INTEGER NOT NULL)");\n        db.execSQL("CREATE INDEX IF NOT EXISTS idx_recovery_snapshot_items_id ON recovery_snapshot_items(snapshot_id)");\n    }\n\n'''
if 'private void ensureRecoveryTables(SQLiteDatabase db)' not in s:
    if marker not in s: raise SystemExit('3.0.82 DB target missing: ensureDefaults marker')
    s=s.replace(marker,helpers+marker,1)

# Journal add/increment path without changing quantity semantics.
old='''                db.update("items", cv, "id=?", new String[]{String.valueOf(c.getLong(0))});\n                return;\n'''
new='''                db.update("items", cv, "id=?", new String[]{String.valueOf(c.getLong(0))});\n                recordHistory(sessionId,safeBarcode,description,quantity,safeLocation,"COUNT");\n                return;\n'''
if old in s:
    s=s.replace(old,new,1)
else:
    raise SystemExit('3.0.82 DB target missing: addOrIncrement update')

old='''        db.insertOrThrow("items", null, cv);\n    }\n\n    public void setQuantity'''
new='''        db.insertOrThrow("items", null, cv);\n        recordHistory(sessionId,safeBarcode,description,quantity,safeLocation,"COUNT");\n    }\n\n    public void setQuantity'''
if old in s:
    s=s.replace(old,new,1)
else:
    raise SystemExit('3.0.82 DB target missing: addOrIncrement insert')

# Replace mutation methods so edits/subtractions/deletes are also auditable.
pat=r'''    public void setQuantity\(long id, int quantity\) \{.*?\n    \}\n\n    public void incrementQuantity'''
repl='''    public void setQuantity(long id, int quantity) {\n        Row before=rowById(id);\n        ContentValues cv = new ContentValues();\n        cv.put("quantity", quantity);\n        cv.put("updated_at", System.currentTimeMillis());\n        getWritableDatabase().update("items", cv, "id=?", new String[]{String.valueOf(id)});\n        if(before!=null)recordHistory(before.sessionId,before.barcode,before.description,quantity-before.quantity,before.location,"SET");\n    }\n\n    public void incrementQuantity'''
s2,n=re.subn(pat,lambda m:repl,s,count=1,flags=re.S)
if n!=1: raise SystemExit('3.0.82 DB target missing: setQuantity')
s=s2

pat=r'''    public void incrementQuantity\(long id, int delta\) \{.*?\n    \}\n\n    public void updateItem'''
repl='''    public void incrementQuantity(long id, int delta) {\n        Row before=rowById(id);\n        SQLiteDatabase db=getWritableDatabase();\n        db.execSQL("UPDATE items SET quantity=quantity+?, updated_at=? WHERE id=?",\n                new Object[]{delta,System.currentTimeMillis(),id});\n        if(before!=null)recordHistory(before.sessionId,before.barcode,before.description,delta,before.location,"ADJUST");\n    }\n\n    public void updateItem'''
s2,n=re.subn(pat,lambda m:repl,s,count=1,flags=re.S)
if n!=1: raise SystemExit('3.0.82 DB target missing: incrementQuantity')
s=s2

pat=r'''    public void updateItem\(long id, String description, String price, int quantity, String location\) \{.*?\n    \}\n\n    public void deleteItem'''
repl='''    public void updateItem(long id, String description, String price, int quantity, String location) {\n        Row before=rowById(id);\n        ContentValues cv=new ContentValues();\n        cv.put("description",description==null?"":description.trim());\n        cv.put("price",price==null?"":price.trim());\n        cv.put("quantity",quantity);\n        cv.put("location",location==null||location.trim().isEmpty()?"Main":location.trim());\n        cv.put("updated_at",System.currentTimeMillis());\n        getWritableDatabase().update("items",cv,"id=?",new String[]{String.valueOf(id)});\n        if(before!=null)recordHistory(before.sessionId,before.barcode,description,quantity-before.quantity,location,"EDIT");\n    }\n\n    public void deleteItem'''
s2,n=re.subn(pat,lambda m:repl,s,count=1,flags=re.S)
if n!=1: raise SystemExit('3.0.82 DB target missing: updateItem')
s=s2

pat=r'''    public void deleteItem\(long id\) \{.*?\n    \}\n\n    public List<Row> items'''
repl='''    public void deleteItem(long id) {\n        Row before=rowById(id);\n        getWritableDatabase().delete("items", "id=?", new String[]{String.valueOf(id)});\n        if(before!=null)recordHistory(before.sessionId,before.barcode,before.description,-before.quantity,before.location,"DELETE");\n    }\n\n    public List<Row> items'''
s2,n=re.subn(pat,lambda m:repl,s,count=1,flags=re.S)
if n!=1: raise SystemExit('3.0.82 DB target missing: deleteItem')
s=s2

# Append recovery/history helpers before final class brace.
append='''\n    private Row rowById(long id) {\n        try (Cursor c=getReadableDatabase().rawQuery(\n                "SELECT id,session_id,barcode,description,price,quantity,location,updated_at FROM items WHERE id=? LIMIT 1",\n                new String[]{String.valueOf(id)})) {\n            return c.moveToFirst()?rowFromCursor(c):null;\n        }\n    }\n\n    private void recordHistory(long sessionId,String barcode,String description,int quantityDelta,String location,String source) {\n        if(sessionId<=0)return;\n        ensureRecoveryTables(getWritableDatabase());\n        ContentValues cv=new ContentValues();\n        cv.put("session_id",sessionId);\n        cv.put("barcode",barcode==null?"":barcode.trim());\n        cv.put("description",description==null?"":description.trim());\n        cv.put("quantity_delta",quantityDelta);\n        cv.put("location",location==null?"":location.trim());\n        cv.put("source",source==null?"":source);\n        cv.put("created_at",System.currentTimeMillis());\n        getWritableDatabase().insert("scan_history",null,cv);\n    }\n\n    public long createRecoverySnapshot(long sessionId,String reason) {\n        if(sessionId<=0)return -1L;\n        SQLiteDatabase sql=getWritableDatabase();\n        ensureRecoveryTables(sql);\n        boolean own=!sql.inTransaction();\n        if(own)sql.beginTransaction();\n        try {\n            int lines=0,units=0;\n            try(Cursor c=sql.rawQuery("SELECT COUNT(*),COALESCE(SUM(quantity),0) FROM items WHERE session_id=?",new String[]{String.valueOf(sessionId)})){\n                if(c.moveToFirst()){lines=c.getInt(0);units=c.getInt(1);}\n            }\n            ContentValues cv=new ContentValues();\n            cv.put("session_id",sessionId);cv.put("created_at",System.currentTimeMillis());\n            cv.put("reason",reason==null?"Automatic":reason);cv.put("line_count",lines);cv.put("unit_total",units);\n            long snapshotId=sql.insertOrThrow("recovery_snapshots",null,cv);\n            sql.execSQL("INSERT INTO recovery_snapshot_items(snapshot_id,barcode,description,price,quantity,location,updated_at) SELECT ?,barcode,description,price,quantity,location,updated_at FROM items WHERE session_id=?",new Object[]{snapshotId,sessionId});\n            ArrayList<Long> oldIds=new ArrayList<>();\n            try(Cursor c=sql.rawQuery("SELECT id FROM recovery_snapshots WHERE session_id=? ORDER BY created_at DESC,id DESC",new String[]{String.valueOf(sessionId)})){\n                int i=0;while(c.moveToNext()){i++;if(i>12)oldIds.add(c.getLong(0));}\n            }\n            for(Long oldId:oldIds){\n                sql.delete("recovery_snapshot_items","snapshot_id=?",new String[]{String.valueOf(oldId)});\n                sql.delete("recovery_snapshots","id=?",new String[]{String.valueOf(oldId)});\n            }\n            if(own)sql.setTransactionSuccessful();\n            return snapshotId;\n        } finally {if(own)sql.endTransaction();}\n    }\n\n    public List<Snapshot> recoverySnapshots(long sessionId) {\n        ArrayList<Snapshot> out=new ArrayList<>();\n        ensureRecoveryTables(getReadableDatabase());\n        try(Cursor c=getReadableDatabase().rawQuery("SELECT id,session_id,created_at,reason,line_count,unit_total FROM recovery_snapshots WHERE session_id=? ORDER BY created_at DESC,id DESC LIMIT 12",new String[]{String.valueOf(sessionId)})){\n            while(c.moveToNext()){\n                Snapshot x=new Snapshot();x.id=c.getLong(0);x.sessionId=c.getLong(1);x.createdAt=c.getLong(2);x.reason=c.getString(3);x.lineCount=c.getInt(4);x.unitTotal=c.getInt(5);out.add(x);\n            }\n        }\n        return out;\n    }\n\n    public boolean restoreRecoverySnapshot(long sessionId,long snapshotId) {\n        if(sessionId<=0||snapshotId<=0)return false;\n        SQLiteDatabase sql=getWritableDatabase();ensureRecoveryTables(sql);sql.beginTransaction();\n        try {\n            long belongs=0;try(Cursor c=sql.rawQuery("SELECT COUNT(*) FROM recovery_snapshots WHERE id=? AND session_id=?",new String[]{String.valueOf(snapshotId),String.valueOf(sessionId)})){if(c.moveToFirst())belongs=c.getLong(0);}\n            if(belongs==0)return false;\n            sql.delete("items","session_id=?",new String[]{String.valueOf(sessionId)});\n            sql.execSQL("INSERT INTO items(session_id,barcode,description,price,quantity,location,updated_at) SELECT ?,barcode,description,price,quantity,location,updated_at FROM recovery_snapshot_items WHERE snapshot_id=?",new Object[]{sessionId,snapshotId});\n            sql.setTransactionSuccessful();return true;\n        } finally {sql.endTransaction();}\n    }\n\n    public List<History> scanHistory(long sessionId,int limit) {\n        ArrayList<History> out=new ArrayList<>();ensureRecoveryTables(getReadableDatabase());\n        int safe=Math.max(1,Math.min(limit,250));\n        try(Cursor c=getReadableDatabase().rawQuery("SELECT id,session_id,barcode,description,quantity_delta,location,source,created_at FROM scan_history WHERE session_id=? ORDER BY created_at DESC,id DESC LIMIT "+safe,new String[]{String.valueOf(sessionId)})){\n            while(c.moveToNext()){History h=new History();h.id=c.getLong(0);h.sessionId=c.getLong(1);h.barcode=c.getString(2);h.description=c.getString(3);h.quantityDelta=c.getInt(4);h.location=c.getString(5);h.source=c.getString(6);h.createdAt=c.getLong(7);out.add(h);}\n        }\n        return out;\n    }\n'''
if 'public long createRecoverySnapshot' not in s:
    idx=s.rfind('\n}')
    if idx<0: raise SystemExit('3.0.82 DB target missing: final brace')
    s=s[:idx]+append+s[idx:]

p.write_text(s)

# -----------------------------------------------------------------------------
# MainActivity: recovery center + selected external backup folder + checkpoints.
# -----------------------------------------------------------------------------
p=Path('app/src/main/java/com/iceinventory/onhand/MainActivity.java')
s=p.read_text()

# Imports.
if 'import android.database.Cursor;' not in s:
    s=s.replace('import android.content.SharedPreferences;\n','import android.content.SharedPreferences;\nimport android.database.Cursor;\n',1)
if 'import android.provider.DocumentsContract;' not in s:
    if 'import android.provider.MediaStore;\n' in s:
        s=s.replace('import android.provider.MediaStore;\n','import android.provider.MediaStore;\nimport android.provider.DocumentsContract;\n',1)
    else:
        s=s.replace('import android.os.Vibrator;\n','import android.os.Vibrator;\nimport android.provider.DocumentsContract;\n',1)
if 'import java.io.OutputStreamWriter;' not in s:
    s=s.replace('import java.io.OutputStream;\n','import java.io.OutputStream;\nimport java.io.OutputStreamWriter;\n',1)

# Request code and settings key.
if 'REQ_BACKUP_FOLDER' not in s:
    s=s.replace('    private static final int REQ_QUANTITY=1004;\n','    private static final int REQ_QUANTITY=1004;\n    private static final int REQ_BACKUP_FOLDER=1082;\n',1)
if 'KEY_BACKUP_TREE_URI' not in s:
    key_anchor='    private static final String KEY_COMPACT="compact_list";\n'
    if key_anchor not in s: raise SystemExit('3.0.82 Main target missing: compact key')
    s=s.replace(key_anchor,key_anchor+'    private static final String KEY_BACKUP_TREE_URI="recovery_backup_tree_uri";\n',1)

# Checkpoint state.
field_anchor='    private String pendingExportFileName="";\n'
if 'lastSafetyCheckpoint' not in s:
    if field_anchor not in s: raise SystemExit('3.0.82 Main target missing: pending export field')
    s=s.replace(field_anchor,field_anchor+'    private long lastSafetyCheckpoint=0L;\n    private int countsSinceSafetyCheckpoint=0;\n',1)

# Make initial local checkpoint after UI/database initialization.
old='''        buildUi();\n        refreshLocations();\n        refreshList();\n    }\n'''
new='''        buildUi();\n        refreshLocations();\n        refreshList();\n        safetyCheckpoint("App opened",false);\n    }\n'''
if old in s:
    s=s.replace(old,new,1)
else:
    raise SystemExit('3.0.82 Main target missing: initializeApp end')

# Add Recovery controls to Options after Zero PIN button (created in 3.0.59 chain).
anchor='''        box.addView(zeroPin,new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT,dp(50)));\n'''
insert='''        TextView safety=text("Data Safety / Recovery",16,gold(),true);safety.setPadding(dp(6),dp(10),0,dp(2));box.addView(safety);\n        Button recovery=button("Recovery Center",1);recovery.setOnClickListener(v->showRecoveryCenter());\n        box.addView(recovery,new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT,dp(50)));\n        Button backupFolder=button(backupFolderButtonLabel(),0);backupFolder.setOnClickListener(v->chooseBackupFolder());\n        box.addView(backupFolder,new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT,dp(50)));\n'''
if 'Button recovery=button("Recovery Center"' not in s:
    if anchor not in s: raise SystemExit('3.0.82 Main target missing: zeroPin option anchor')
    s=s.replace(anchor,anchor+insert,1)

# Add automatic checkpoint after successful add count by hooking proven refresh path in addItem.
# Restrict to the first occurrence inside addItem method using a regex region.
m=re.search(r'    private void addItem\(\) \{(.*?)\n    \}\n',s,re.S)
if not m: raise SystemExit('3.0.82 Main target missing: addItem method')
block=m.group(0)
if 'noteCountForSafety();' not in block:
    # Insert just before method closes, after existing successful workflow. This may also execute on early-validation returns only if reached.
    pos=block.rfind('\n    }')
    block2=block[:pos]+'\n        noteCountForSafety();'+block[pos:]
    s=s[:m.start()]+block2+s[m.end():]

# Protect destructive operations with a forced local + external checkpoint.
old='''                .setPositiveButton("ZERO ALL",(d,w)->{\n                    int changed=db.zeroAllQuantities(sessionId);\n'''
new='''                .setPositiveButton("ZERO ALL",(d,w)->{\n                    safetyCheckpoint("Before Zero All",true);\n                    int changed=db.zeroAllQuantities(sessionId);\n'''
if old in s:
    s=s.replace(old,new,1)
else:
    raise SystemExit('3.0.82 Main target missing: Zero All action')

old='''            if(replaceCurrent) {\n                db.beginInventoryTransaction();\n'''
new='''            if(replaceCurrent) {\n                safetyCheckpoint("Before Replace Import",true);\n                db.beginInventoryTransaction();\n'''
if old in s:
    s=s.replace(old,new,1)
else:
    raise SystemExit('3.0.82 Main target missing: replace import action')

# Handle backup folder selection at the beginning of existing onActivityResult.
pat=r'''(@Override\s+(?:public|protected)\s+void onActivityResult\(int requestCode,int resultCode,Intent data\)\s*\{\n)'''
match=re.search(pat,s)
if not match: raise SystemExit('3.0.82 Main target missing: onActivityResult signature')
if 'requestCode==REQ_BACKUP_FOLDER' not in s:
    handler='''        if(requestCode==REQ_BACKUP_FOLDER){\n            if(resultCode==RESULT_OK&&data!=null&&data.getData()!=null){\n                Uri tree=data.getData();\n                int flags=data.getFlags()&(Intent.FLAG_GRANT_READ_URI_PERMISSION|Intent.FLAG_GRANT_WRITE_URI_PERMISSION);\n                try{getContentResolver().takePersistableUriPermission(tree,flags);}catch(Exception ignored){}\n                prefs().edit().putString(KEY_BACKUP_TREE_URI,tree.toString()).apply();\n                safetyCheckpoint("Backup folder selected",true);\n                toast("Recovery backup folder saved");\n            }\n            return;\n        }\n'''
    s=s[:match.end()]+handler+s[match.end():]

# Lifecycle checkpoint; throttle prevents camera-scanner pauses from creating excessive files.
if '@Override protected void onPause()' not in s and '@Override public void onPause()' not in s:
    marker='''    private SharedPreferences prefs(){return getSharedPreferences(SETTINGS,MODE_PRIVATE);}\n'''
    lifecycle='''    @Override protected void onPause(){\n        super.onPause();\n        safetyCheckpoint("App background",false);\n    }\n\n'''
    if marker not in s: raise SystemExit('3.0.82 Main target missing: prefs marker')
    s=s.replace(marker,lifecycle+marker,1)

# Recovery/external-backup helpers go before toast() helper or final class brace.
helpers='''    private void noteCountForSafety(){\n        countsSinceSafetyCheckpoint++;\n        if(countsSinceSafetyCheckpoint>=10)safetyCheckpoint("Automatic after 10 counts",false);\n    }\n\n    private void safetyCheckpoint(String reason,boolean force){\n        if(db==null||sessionId<=0)return;\n        long now=System.currentTimeMillis();\n        if(!force&&countsSinceSafetyCheckpoint<10&&now-lastSafetyCheckpoint<120000L)return;\n        try{\n            db.createRecoverySnapshot(sessionId,reason);\n            lastSafetyCheckpoint=now;countsSinceSafetyCheckpoint=0;\n            writeExternalSafetyBackup(reason,force);\n        }catch(Exception e){Log.e(TAG,"Recovery checkpoint failed",e);}\n    }\n\n    private String backupFolderButtonLabel(){\n        String u=prefs().getString(KEY_BACKUP_TREE_URI,"");\n        return u==null||u.trim().isEmpty()?"Choose External Backup Folder":"External Backup Folder: Set";\n    }\n\n    private void chooseBackupFolder(){\n        Intent i=new Intent(Intent.ACTION_OPEN_DOCUMENT_TREE);\n        i.addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION|Intent.FLAG_GRANT_WRITE_URI_PERMISSION|Intent.FLAG_GRANT_PERSISTABLE_URI_PERMISSION|Intent.FLAG_GRANT_PREFIX_URI_PERMISSION);\n        startActivityForResult(i,REQ_BACKUP_FOLDER);\n    }\n\n    private void showRecoveryCenter(){\n        List<InventoryDb.Snapshot> snaps=db.recoverySnapshots(sessionId);\n        android.widget.ScrollView scroll=new android.widget.ScrollView(this);\n        LinearLayout box=new LinearLayout(this);box.setOrientation(LinearLayout.VERTICAL);box.setPadding(dp(12),dp(8),dp(12),dp(8));scroll.addView(box);\n        TextView info=text("Automatic checkpoints keep the last 12 recovery points for this inventory.",14,Color.WHITE,false);box.addView(info);\n        Button now=button("Create Backup Now",1);now.setOnClickListener(v->{safetyCheckpoint("Manual Backup",true);toast("Recovery backup created");});box.addView(now,new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT,dp(48)));\n        Button hist=button("View Scan / Count History",0);hist.setOnClickListener(v->showScanHistory());box.addView(hist,new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT,dp(48)));\n        if(snaps.isEmpty()){TextView none=text("No recovery points yet.",15,gold(),true);none.setPadding(0,dp(12),0,dp(8));box.addView(none);}\n        SimpleDateFormat f=new SimpleDateFormat("MMM d, h:mm a",Locale.US);\n        for(InventoryDb.Snapshot snap:snaps){\n            String label=f.format(new Date(snap.createdAt))+" • "+snap.lineCount+" lines • "+snap.unitTotal+" units\\n"+(snap.reason==null?"":snap.reason);\n            Button b=button(label,0);b.setOnClickListener(v->confirmRestoreSnapshot(snap));\n            LinearLayout.LayoutParams lp=new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT,dp(64));lp.setMargins(0,dp(4),0,0);box.addView(b,lp);\n        }\n        new AlertDialog.Builder(this).setTitle("Recovery Center").setView(scroll).setNegativeButton("Close",null).show();\n    }\n\n    private void confirmRestoreSnapshot(InventoryDb.Snapshot snap){\n        String when=new SimpleDateFormat("MMM d, h:mm a",Locale.US).format(new Date(snap.createdAt));\n        new AlertDialog.Builder(this).setTitle("Restore Inventory?")\n                .setMessage("Restore the inventory exactly as it was at "+when+"?\\n\\nA new safety checkpoint of the current inventory will be created first.")\n                .setPositiveButton("RESTORE",(d,w)->{\n                    safetyCheckpoint("Before Recovery Restore",true);\n                    if(db.restoreRecoverySnapshot(sessionId,snap.id)){refreshLocations();refreshList();safetyCheckpoint("After Recovery Restore",true);toast("Inventory restored");}\n                    else toast("Restore failed");\n                }).setNegativeButton("Cancel",null).show();\n    }\n\n    private void showScanHistory(){\n        List<InventoryDb.History> h=db.scanHistory(sessionId,100);\n        if(h.isEmpty()){toast("No count history yet");return;}\n        String[] rows=new String[h.size()];SimpleDateFormat f=new SimpleDateFormat("h:mm:ss a",Locale.US);\n        for(int i=0;i<h.size();i++){InventoryDb.History x=h.get(i);String sign=x.quantityDelta>0?"+":"";rows[i]=f.format(new Date(x.createdAt))+"  "+sign+x.quantityDelta+"  "+x.barcode+"  "+x.location+"  ["+x.source+"]";}\n        new AlertDialog.Builder(this).setTitle("Recent Count History").setItems(rows,null).setNegativeButton("Close",null).show();\n    }\n\n    private void writeExternalSafetyBackup(String reason,boolean preserveCopy){\n        String raw=prefs().getString(KEY_BACKUP_TREE_URI,"");if(raw==null||raw.trim().isEmpty())return;\n        try{\n            Uri tree=Uri.parse(raw);String clean=safeBackupName(sessionName);\n            String name=preserveCopy?"ICE_OnHand_"+clean+"_"+new SimpleDateFormat("yyyyMMdd_HHmmss",Locale.US).format(new Date())+".txt":"ICE_OnHand_"+clean+"_Latest.txt";\n            Uri doc=findBackupDocument(tree,name);\n            if(doc==null)doc=DocumentsContract.createDocument(getContentResolver(),tree,"text/plain",name);\n            if(doc==null)return;\n            try(OutputStream os=getContentResolver().openOutputStream(doc,"wt");OutputStreamWriter w=new OutputStreamWriter(os,StandardCharsets.UTF_8)){\n                w.write("iCE OnHand Recovery Backup\\n");w.write("Inventory\\t"+safeBackupField(sessionName)+"\\n");w.write("Reason\\t"+safeBackupField(reason)+"\\n");w.write("Saved\\t"+new SimpleDateFormat("yyyy-MM-dd HH:mm:ss",Locale.US).format(new Date())+"\\n\\n");\n                w.write("Barcode\\tDescription\\tPrice\\tQuantity\\tLocation\\tUpdatedAt\\n");\n                for(InventoryDb.Row r:db.items(sessionId)){w.write(safeBackupField(r.barcode)+"\\t"+safeBackupField(r.description)+"\\t"+safeBackupField(r.price)+"\\t"+r.quantity+"\\t"+safeBackupField(r.location)+"\\t"+r.updatedAt+"\\n");}\n                w.flush();\n            }\n        }catch(Exception e){Log.e(TAG,"External recovery backup failed",e);}\n    }\n\n    private Uri findBackupDocument(Uri tree,String name){\n        try{\n            String treeId=DocumentsContract.getTreeDocumentId(tree);Uri children=DocumentsContract.buildChildDocumentsUriUsingTree(tree,treeId);\n            String[] cols={DocumentsContract.Document.COLUMN_DOCUMENT_ID,DocumentsContract.Document.COLUMN_DISPLAY_NAME};\n            try(Cursor c=getContentResolver().query(children,cols,null,null,null)){\n                if(c!=null)while(c.moveToNext())if(name.equals(c.getString(1)))return DocumentsContract.buildDocumentUriUsingTree(tree,c.getString(0));\n            }\n        }catch(Exception ignored){}return null;\n    }\n\n    private String safeBackupName(String s){String x=s==null?"Inventory":s.trim().replaceAll("[^A-Za-z0-9._-]+","_");return x.isEmpty()?"Inventory":x;}\n    private String safeBackupField(String s){return s==null?"":s.replace('\\t',' ').replace('\\n',' ').replace('\\r',' ');}\n\n'''
if 'private void showRecoveryCenter()' not in s:
    marker='''    private void toast(String s) {\n'''
    if marker in s:
        s=s.replace(marker,helpers+marker,1)
    else:
        idx=s.rfind('\n}')
        if idx<0: raise SystemExit('3.0.82 Main target missing: final brace')
        s=s[:idx]+helpers+s[idx:]

# Version bump.
if 'TextView app=text("Onhand Inventory 3.0.81",19,Color.WHITE,true);' in s:
    s=s.replace('TextView app=text("Onhand Inventory 3.0.81",19,Color.WHITE,true);','TextView app=text("Onhand Inventory 3.0.82",19,Color.WHITE,true);',1)
else:
    raise SystemExit('3.0.82 Main target missing: visible version')
p.write_text(s)

p=Path('app/build.gradle')
s=p.read_text().replace('versionCode 30081','versionCode 30082',1).replace("versionName '3.0.81'","versionName '3.0.82'",1)
if 'versionCode 30082' not in s or "versionName '3.0.82'" not in s: raise SystemExit('3.0.82 target missing: Gradle version')
p.write_text(s)

p=Path('app/src/main/AndroidManifest.xml')
s=p.read_text().replace('android:label="iCE Onhand 3.0.81"','android:label="iCE Onhand 3.0.82"',1)
if 'android:label="iCE Onhand 3.0.82"' not in s: raise SystemExit('3.0.82 target missing: manifest version')
p.write_text(s)

print('Prepared iCE Onhand 3.0.82: scan history + 12 recovery snapshots + Recovery Center + external SAF backup folder + destructive-action checkpoints')
