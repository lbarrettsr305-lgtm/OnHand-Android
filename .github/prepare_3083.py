from pathlib import Path
import re
import runpy

# Preserve the complete, verified 3.0.82 recovery/data-protection release first.
runpy.run_path('.github/prepare_3082_release.py', run_name='__main__')

# -----------------------------------------------------------------------------
# InventoryDb: export ledger + journal-range batch reconstruction + scan sequence.
# -----------------------------------------------------------------------------
p=Path('app/src/main/java/com/iceinventory/onhand/InventoryDb.java')
s=p.read_text()

if 'import java.util.LinkedHashMap;' not in s:
    s=s.replace('import java.util.ArrayList;\n', 'import java.util.ArrayList;\nimport java.util.LinkedHashMap;\nimport java.util.HashMap;\nimport java.util.Map;\nimport java.util.Collections;\n', 1)

if 'public long scanSequence;' not in s:
    s=s.replace('        public long updatedAt;\n', '        public long updatedAt;\n        public long scanSequence;\n', 1)

if 'public static final class ExportBatch' not in s:
    marker='''    public InventoryDb(Context context) {\n'''
    extra='''    public static final class ExportBatch {\n        public long id;\n        public long sessionId;\n        public int batchNumber;\n        public String exportType;\n        public long createdAt;\n        public long firstHistoryId;\n        public long lastHistoryId;\n        public int lineCount;\n        public int unitTotal;\n        public String filename;\n    }\n\n'''
    if marker not in s: raise SystemExit('3.0.83 DB target missing: constructor marker')
    s=s.replace(marker, extra+marker, 1)

needle='''        db.execSQL("CREATE INDEX IF NOT EXISTS idx_recovery_snapshot_items_id ON recovery_snapshot_items(snapshot_id)");\n'''
addition='''        db.execSQL("CREATE TABLE IF NOT EXISTS export_batches (id INTEGER PRIMARY KEY AUTOINCREMENT, session_id INTEGER NOT NULL, batch_no INTEGER NOT NULL DEFAULT 0, export_type TEXT NOT NULL DEFAULT 'NEW', created_at INTEGER NOT NULL, first_history_id INTEGER NOT NULL DEFAULT 0, last_history_id INTEGER NOT NULL DEFAULT 0, line_count INTEGER NOT NULL DEFAULT 0, unit_total INTEGER NOT NULL DEFAULT 0, filename TEXT NOT NULL DEFAULT '')");\n        db.execSQL("CREATE INDEX IF NOT EXISTS idx_export_batches_session_time ON export_batches(session_id,created_at DESC,id DESC)");\n        db.execSQL("CREATE INDEX IF NOT EXISTS idx_export_batches_session_type ON export_batches(session_id,export_type,batch_no)");\n'''
if 'CREATE TABLE IF NOT EXISTS export_batches' not in s:
    if needle not in s: raise SystemExit('3.0.83 DB target missing: recovery table anchor')
    s=s.replace(needle, needle+addition, 1)

old='''"SELECT id,session_id,barcode,description,price,quantity,location,updated_at FROM items WHERE session_id=? ORDER BY updated_at DESC",\n'''
new='''"SELECT i.id,i.session_id,i.barcode,i.description,i.price,i.quantity,i.location,i.updated_at,COALESCE((SELECT MIN(h.id) FROM scan_history h WHERE h.session_id=i.session_id AND h.barcode=i.barcode AND h.location=i.location),i.id) FROM items i WHERE i.session_id=? ORDER BY i.updated_at DESC",\n'''
if old in s:s=s.replace(old,new,1)
elif 'COALESCE((SELECT MIN(h.id) FROM scan_history h' not in s:raise SystemExit('3.0.83 DB target missing: items query')

old='''        r.updatedAt=c.getLong(7);\n        return r;\n'''
new='''        r.updatedAt=c.getLong(7);\n        if(c.getColumnCount()>8)r.scanSequence=c.getLong(8);else r.scanSequence=r.id;\n        return r;\n'''
if old in s:s=s.replace(old,new,1)
elif 'r.scanSequence=' not in s:raise SystemExit('3.0.83 DB target missing: rowFromCursor')

append=r'''
    private String batchKey(String barcode,String location) {
        return (barcode==null?"":barcode)+"\u0001"+(location==null?"":location);
    }

    public long maxHistoryId(long sessionId) {
        ensureRecoveryTables(getReadableDatabase());
        try(Cursor c=getReadableDatabase().rawQuery("SELECT COALESCE(MAX(id),0) FROM scan_history WHERE session_id=?",new String[]{String.valueOf(sessionId)})) {
            return c.moveToFirst()?c.getLong(0):0L;
        }
    }

    public long firstHistoryIdAfter(long sessionId,long afterExclusive,long throughInclusive) {
        ensureRecoveryTables(getReadableDatabase());
        try(Cursor c=getReadableDatabase().rawQuery("SELECT COALESCE(MIN(id),0) FROM scan_history WHERE session_id=? AND id>? AND id<=?",new String[]{String.valueOf(sessionId),String.valueOf(afterExclusive),String.valueOf(throughInclusive)})) {
            return c.moveToFirst()?c.getLong(0):0L;
        }
    }

    public long lastNewBatchHistoryId(long sessionId) {
        ensureRecoveryTables(getReadableDatabase());
        try(Cursor c=getReadableDatabase().rawQuery("SELECT COALESCE(MAX(last_history_id),0) FROM export_batches WHERE session_id=? AND export_type='NEW'",new String[]{String.valueOf(sessionId)})) {
            return c.moveToFirst()?c.getLong(0):0L;
        }
    }

    public int nextBatchNumber(long sessionId) {
        ensureRecoveryTables(getReadableDatabase());
        try(Cursor c=getReadableDatabase().rawQuery("SELECT COALESCE(MAX(batch_no),0)+1 FROM export_batches WHERE session_id=? AND export_type='NEW'",new String[]{String.valueOf(sessionId)})) {
            return c.moveToFirst()?Math.max(1,c.getInt(0)):1;
        }
    }

    public List<Row> batchRows(long sessionId,long afterExclusive,long throughInclusive) {
        ArrayList<Row> out=new ArrayList<>();
        if(sessionId<=0||throughInclusive<=afterExclusive)return out;
        ensureRecoveryTables(getReadableDatabase());
        HashMap<String,Row> current=new HashMap<>();
        for(Row r:items(sessionId))current.put(batchKey(r.barcode,r.location),r);
        LinkedHashMap<String,Row> grouped=new LinkedHashMap<>();
        try(Cursor c=getReadableDatabase().rawQuery("SELECT id,barcode,description,quantity_delta,location,created_at FROM scan_history WHERE session_id=? AND id>? AND id<=? ORDER BY id ASC",new String[]{String.valueOf(sessionId),String.valueOf(afterExclusive),String.valueOf(throughInclusive)})) {
            while(c.moveToNext()) {
                long historyId=c.getLong(0);String code=c.getString(1)==null?"":c.getString(1);String desc=c.getString(2)==null?"":c.getString(2);int delta=c.getInt(3);String loc=c.getString(4)==null?"":c.getString(4);long when=c.getLong(5);
                String key=batchKey(code,loc);Row r=grouped.get(key);
                if(r==null) {
                    r=new Row();r.id=historyId;r.sessionId=sessionId;r.barcode=code;r.description=desc;r.location=loc;r.quantity=0;r.updatedAt=when;r.scanSequence=historyId;
                    Row now=current.get(key);r.price=now==null||now.price==null?"":now.price;grouped.put(key,r);
                }
                r.quantity+=delta;if(!desc.trim().isEmpty())r.description=desc;r.updatedAt=when;
            }
        }
        for(Row r:grouped.values())if(r.quantity!=0)out.add(r);
        return out;
    }

    public List<Row> itemsInScanOrder(long sessionId) {
        ArrayList<Row> rows=new ArrayList<>(items(sessionId));
        Collections.sort(rows,(a,b)->{long ax=a.scanSequence>0?a.scanSequence:a.id;long bx=b.scanSequence>0?b.scanSequence:b.id;int x=Long.compare(ax,bx);return x!=0?x:Long.compare(a.id,b.id);});
        return rows;
    }

    public long recordExportBatch(long sessionId,int batchNumber,String exportType,long firstHistoryId,long lastHistoryId,int lineCount,int unitTotal,String filename) {
        ensureRecoveryTables(getWritableDatabase());ContentValues cv=new ContentValues();cv.put("session_id",sessionId);cv.put("batch_no",Math.max(0,batchNumber));cv.put("export_type",exportType==null?"NEW":exportType);cv.put("created_at",System.currentTimeMillis());cv.put("first_history_id",Math.max(0L,firstHistoryId));cv.put("last_history_id",Math.max(0L,lastHistoryId));cv.put("line_count",Math.max(0,lineCount));cv.put("unit_total",unitTotal);cv.put("filename",filename==null?"":filename);return getWritableDatabase().insertOrThrow("export_batches",null,cv);
    }

    public List<ExportBatch> newExportBatches(long sessionId,int limit) {
        ArrayList<ExportBatch> out=new ArrayList<>();ensureRecoveryTables(getReadableDatabase());int safe=Math.max(1,Math.min(limit,100));
        try(Cursor c=getReadableDatabase().rawQuery("SELECT id,session_id,batch_no,export_type,created_at,first_history_id,last_history_id,line_count,unit_total,filename FROM export_batches WHERE session_id=? AND export_type='NEW' ORDER BY batch_no DESC,id DESC LIMIT "+safe,new String[]{String.valueOf(sessionId)})) {
            while(c.moveToNext()) {ExportBatch b=new ExportBatch();b.id=c.getLong(0);b.sessionId=c.getLong(1);b.batchNumber=c.getInt(2);b.exportType=c.getString(3);b.createdAt=c.getLong(4);b.firstHistoryId=c.getLong(5);b.lastHistoryId=c.getLong(6);b.lineCount=c.getInt(7);b.unitTotal=c.getInt(8);b.filename=c.getString(9);out.add(b);}
        }
        return out;
    }
'''
if 'public long recordExportBatch' not in s:
    idx=s.rfind('\n}')
    if idx<0:raise SystemExit('3.0.83 DB target missing: final brace')
    s=s[:idx]+append+s[idx:]
p.write_text(s)

# -----------------------------------------------------------------------------
# MainActivity: batch export choices, automatic naming, re-export, scan sort.
# -----------------------------------------------------------------------------
p=Path('app/src/main/java/com/iceinventory/onhand/MainActivity.java')
s=p.read_text()
field_anchor='''    private int countsSinceSafetyCheckpoint=0;\n'''
fields='''    private int pendingBatchMode=0; // 0=normal, 1=new, 2=complete, 3=re-export\n    private int pendingBatchNumber=0;\n    private long pendingBatchFirstHistoryId=0L;\n    private long pendingBatchLastHistoryId=0L;\n    private long pendingBatchReplayId=0L;\n'''
if 'private int pendingBatchMode=' not in s:
    if field_anchor not in s:raise SystemExit('3.0.83 Main target missing: safety field anchor')
    s=s.replace(field_anchor,field_anchor+fields,1)

pattern=r'''    private void showExportScopeDialog\(\) \{.*?\n    \}\n\n    private int internetItemCount\(\) \{'''
replacement=r'''    private void showExportScopeDialog() {
        int next=db.nextBatchNumber(sessionId);
        String[] choices={"Export New Counts Only (Batch "+String.format(Locale.US,"%02d",next)+")","Export Complete Inventory","Re-export Previous Batch","Internet Items With Pictures"};
        new AlertDialog.Builder(this).setTitle("Export Items").setItems(choices,(d,which)->{
            if(which==0){beginNewBatchExport();return;}if(which==1){beginCompleteInventoryExport();return;}if(which==2){showBatchReExportDialog();return;}
            pendingBatchMode=0;pendingExportInternetOnly=true;if(internetItemCount()==0){toast("No internet items to export");return;}showExportDialog();
        }).setNegativeButton("Cancel",null).show();
    }

    private void beginNewBatchExport() {
        long after=db.lastNewBatchHistoryId(sessionId),through=db.maxHistoryId(sessionId);
        if(through<=after){toast("No new counts since the last batch");return;}
        long first=db.firstHistoryIdAfter(sessionId,after,through);List<InventoryDb.Row> rows=db.batchRows(sessionId,after,through);
        if(rows.isEmpty()){toast("No net quantity changes to export");return;}
        pendingExportInternetOnly=false;pendingBatchMode=1;pendingBatchNumber=db.nextBatchNumber(sessionId);pendingBatchFirstHistoryId=first;pendingBatchLastHistoryId=through;pendingBatchReplayId=0L;showExportDialog();
    }

    private void beginCompleteInventoryExport() {
        pendingExportInternetOnly=false;pendingBatchMode=2;pendingBatchNumber=0;long last=db.maxHistoryId(sessionId);pendingBatchFirstHistoryId=db.firstHistoryIdAfter(sessionId,0L,last);pendingBatchLastHistoryId=last;pendingBatchReplayId=0L;showExportDialog();
    }

    private void showBatchReExportDialog() {
        List<InventoryDb.ExportBatch> batches=db.newExportBatches(sessionId,30);if(batches.isEmpty()){toast("No previous batches to re-export");return;}
        String[] labels=new String[batches.size()];SimpleDateFormat f=new SimpleDateFormat("MM/dd HH:mm",Locale.US);
        for(int i=0;i<batches.size();i++){InventoryDb.ExportBatch b=batches.get(i);labels[i]="Batch "+String.format(Locale.US,"%02d",b.batchNumber)+" • Seq "+b.firstHistoryId+"-"+b.lastHistoryId+" • "+b.lineCount+" lines • "+f.format(new Date(b.createdAt));}
        new AlertDialog.Builder(this).setTitle("Re-export Previous Batch").setItems(labels,(d,which)->{InventoryDb.ExportBatch b=batches.get(which);pendingExportInternetOnly=false;pendingBatchMode=3;pendingBatchNumber=b.batchNumber;pendingBatchFirstHistoryId=b.firstHistoryId;pendingBatchLastHistoryId=b.lastHistoryId;pendingBatchReplayId=b.id;showExportDialog();}).setNegativeButton("Cancel",null).show();
    }

    private String seqText(long n){return String.format(Locale.US,"%06d",Math.max(0L,n));}
    private String batchExportFileName(){String day=new SimpleDateFormat("yyyy-MM-dd_HHmm",Locale.US).format(new Date());return safeFileName(sessionName)+"_Batch"+String.format(Locale.US,"%02d",Math.max(1,pendingBatchNumber))+"_Seq"+seqText(pendingBatchFirstHistoryId)+"-"+seqText(pendingBatchLastHistoryId)+"_"+day+".txt";}
    private String completeExportFileName(){String day=new SimpleDateFormat("yyyy-MM-dd_HHmm",Locale.US).format(new Date());return safeFileName(sessionName)+"_COMPLETE_Seq"+seqText(pendingBatchFirstHistoryId)+"-"+seqText(pendingBatchLastHistoryId)+"_"+day+".txt";}
    private void resetBatchExportState(){pendingBatchMode=0;pendingBatchNumber=0;pendingBatchFirstHistoryId=0L;pendingBatchLastHistoryId=0L;pendingBatchReplayId=0L;}

    private int internetItemCount() {'''
s2,n=re.subn(pattern,lambda m:replacement,s,count=1,flags=re.S)
if n!=1:raise SystemExit('3.0.83 Main target missing: export scope method')
s=s2

old='''        String exportName=userExportFileName(exportUser,defaultName);\n        if(pendingExportInternetOnly)exportName=internetExportFileName(exportName);\n'''
new='''        String exportName=userExportFileName(exportUser,defaultName);\n        if(pendingBatchMode==1||pendingBatchMode==3)exportName=batchExportFileName();\n        else if(pendingBatchMode==2)exportName=completeExportFileName();\n        else if(pendingExportInternetOnly)exportName=internetExportFileName(exportName);\n'''
if old in s:s=s.replace(old,new,1)
elif 'pendingBatchMode==1||pendingBatchMode==3' not in s:raise SystemExit('3.0.83 Main target missing: export filename block')

old='''    private void saveToDownloads(String filename) {\n''';new='''    private void saveToDownloads(String filename) {\n        pendingExportFileName=filename;\n'''
if old in s and 'private void saveToDownloads(String filename) {\n        pendingExportFileName=filename;' not in s:s=s.replace(old,new,1)

pattern=r'''    private void writeExport\(Uri uri\) \{.*?\n    \}\n\n    private void readImport'''
replacement=r'''    private void writeExport(Uri uri) {
        if(uri==null)return;
        try(OutputStream os=getContentResolver().openOutputStream(uri)) {
            if(os==null)throw new Exception("No output stream");
            if(pendingExportInternetOnly){os.write(buildInternetItemsHtml().getBytes(StandardCharsets.UTF_8));toast("Internet items with pictures exported");}
            else if(pendingBatchMode==1||pendingBatchMode==3){
                long after=pendingBatchFirstHistoryId>0?pendingBatchFirstHistoryId-1:0L;List<InventoryDb.Row> rows=db.batchRows(sessionId,after,pendingBatchLastHistoryId);os.write(BatchExportText.exportRows(rows,prefs()).getBytes(StandardCharsets.UTF_8));
                if(pendingBatchMode==1){int units=0;for(InventoryDb.Row r:rows)units+=r.quantity;db.recordExportBatch(sessionId,pendingBatchNumber,"NEW",pendingBatchFirstHistoryId,pendingBatchLastHistoryId,rows.size(),units,pendingExportFileName);safetyCheckpoint("After Batch "+pendingBatchNumber,true);toast("Batch "+String.format(Locale.US,"%02d",pendingBatchNumber)+" exported • "+rows.size()+" lines");}
                else toast("Batch "+String.format(Locale.US,"%02d",pendingBatchNumber)+" re-exported");
            } else if(pendingBatchMode==2){
                List<InventoryDb.Row> rows=db.itemsInScanOrder(sessionId);os.write(TabTextUtils.exportRows(rows,prefs()).getBytes(StandardCharsets.UTF_8));int units=0;for(InventoryDb.Row r:rows)units+=r.quantity;db.recordExportBatch(sessionId,0,"COMPLETE",pendingBatchFirstHistoryId,pendingBatchLastHistoryId,rows.size(),units,pendingExportFileName);safetyCheckpoint("After Complete Export",true);toast("Complete inventory exported • "+rows.size()+" lines");
            } else {os.write(TabTextUtils.exportRows(db.items(sessionId),prefs()).getBytes(StandardCharsets.UTF_8));toast("Tab-delimited TXT exported");}
            if(!pendingExportInternetOnly)resetBatchExportState();
        } catch(Exception e){showError("Export failed",e);}
    }

    private void readImport'''
s2,n=re.subn(pattern,lambda m:replacement,s,count=1,flags=re.S)
if n!=1:raise SystemExit('3.0.83 Main target missing: writeExport method')
s=s2

old='''String[] choices={"Default order","Description A–Z","Description Z–A","Barcode","Quantity high to low","Quantity low to high","Location A–Z","Last scanned first"};'''
new='''String[] choices={"Default order","Description A–Z","Description Z–A","Barcode","Quantity high to low","Quantity low to high","Location A–Z","Last scanned first","Original scan order"};'''
if old in s:s=s.replace(old,new,1)
elif '"Original scan order"' not in s:raise SystemExit('3.0.83 Main target missing: sort choices')
old='''        else if(sortMode==7)c=(a,b)->Long.compare(b.updatedAt,a.updatedAt);\n        if(c!=null)java.util.Collections.sort(visibleRows,c);\n'''
new='''        else if(sortMode==7)c=(a,b)->Long.compare(b.updatedAt,a.updatedAt);\n        else if(sortMode==8)c=(a,b)->{long ax=a.scanSequence>0?a.scanSequence:a.id,bx=b.scanSequence>0?b.scanSequence:b.id;int x=Long.compare(ax,bx);return x!=0?x:Long.compare(a.id,b.id);};\n        if(c!=null)java.util.Collections.sort(visibleRows,c);\n'''
if old in s:s=s.replace(old,new,1)
elif 'sortMode==8' not in s:raise SystemExit('3.0.83 Main target missing: sort comparator')

s=s.replace('Onhand Inventory 3.0.82','Onhand Inventory 3.0.83')
p.write_text(s)

p=Path('app/build.gradle');s=p.read_text().replace('versionCode 30082','versionCode 30083',1).replace("versionName '3.0.82'","versionName '3.0.83'",1)
if 'versionCode 30083' not in s or "versionName '3.0.83'" not in s:raise SystemExit('3.0.83 target missing: Gradle version')
p.write_text(s)
p=Path('app/src/main/AndroidManifest.xml');s=p.read_text().replace('iCE Onhand 3.0.82','iCE Onhand 3.0.83')
if 'iCE Onhand 3.0.83' not in s:raise SystemExit('3.0.83 target missing: manifest version')
p.write_text(s)

db=Path('app/src/main/java/com/iceinventory/onhand/InventoryDb.java').read_text();main=Path('app/src/main/java/com/iceinventory/onhand/MainActivity.java').read_text()
checks={'export ledger':'CREATE TABLE IF NOT EXISTS export_batches','last batch marker':'lastNewBatchHistoryId(long sessionId)','batch reconstruction':'batchRows(long sessionId,long afterExclusive,long throughInclusive)','scan ordered rows':'itemsInScanOrder(long sessionId)','batch record':'recordExportBatch(long sessionId,int batchNumber','batch picker':'Export New Counts Only (Batch','complete export':'Export Complete Inventory','re-export':'Re-export Previous Batch','batch writer':'BatchExportText.exportRows(rows,prefs())','scan order sort':'Original scan order'}
missing=[]
for label,needle in checks.items():
    target=db if label in ('export ledger','last batch marker','batch reconstruction','scan ordered rows','batch record') else main
    if needle not in target:missing.append(label)
if missing:raise SystemExit('3.0.83 batch verification failed: '+', '.join(missing))
print('Prepared iCE Onhand 3.0.83: export ledger + new-count batches + complete export + re-export + original scan order')
