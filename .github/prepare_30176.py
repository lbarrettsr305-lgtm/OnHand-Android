from pathlib import Path

base = Path('.github/prepare_30175.py')
exec(compile(base.read_text(), str(base), 'exec'), {'__name__': '__main__', '__file__': str(base)})


def rep(path, old, new, label):
    p = Path(path); s = p.read_text()
    if s.count(old) != 1:
        raise SystemExit('3.0.176 target '+label+' count '+str(s.count(old)))
    p.write_text(s.replace(old, new, 1))


rep('app/build.gradle','versionCode 30175','versionCode 30176','code')
rep('app/build.gradle',"versionName '3.0.175'","versionName '3.0.176'",'name')
rep('app/src/main/AndroidManifest.xml','iCE Onhand 3.0.175','iCE Onhand 3.0.176','manifest')

main='app/src/main/java/com/iceinventory/onhand/MainActivity.java'
rep(main,'Onhand Inventory 3.0.175','Onhand Inventory 3.0.176','header')
rep(main,
'''        pendingExportInternetOnly=false;pendingBatchMode=2;pendingBatchNumber=0;long last=db.maxHistoryId(sessionId);pendingBatchFirstHistoryId=db.firstHistoryIdAfter(sessionId,0L,last);pendingBatchLastHistoryId=last;pendingBatchReplayId=0L;startExportFormatFlow();''',
'''        pendingExportInternetOnly=false;pendingBatchMode=2;pendingBatchNumber=db.nextCompleteExportNumber(sessionId);long last=db.maxHistoryId(sessionId);pendingBatchFirstHistoryId=db.firstHistoryIdAfter(sessionId,0L,last);pendingBatchLastHistoryId=last;pendingBatchReplayId=0L;startExportFormatFlow();''',
'complete export number')
rep(main,
'''    private String completeExportFileName(){String day=new SimpleDateFormat("yyyy-MM-dd_HHmm",Locale.US).format(new Date());String ext=pendingExportExcel?".xlsx":".txt";String user=safeFilePart(savedUserName());String prefix=user.isEmpty()?"":user+" - ";return prefix+safeFileName(sessionName)+"_COMPLETE_Seq"+seqText(pendingBatchFirstHistoryId)+"-"+seqText(pendingBatchLastHistoryId)+"_"+day+ext;}''',
'''    private String completeExportFileName(){String ext=pendingExportExcel?".xlsx":".txt";String store=safeFilePart(sessionName);String user=safeFilePart(savedUserName());if(store.isEmpty())store="Inventory";if(user.isEmpty())user="Counter";return store+"-"+user+"-"+String.format(Locale.US,"%02d",Math.max(1,pendingBatchNumber))+ext;}''',
'short complete filename')
rep(main,
'''                db.recordExportBatch(sessionId,0,"COMPLETE",pendingBatchFirstHistoryId,pendingBatchLastHistoryId,rows.size(),units,pendingExportFileName);''',
'''                db.recordExportBatch(sessionId,pendingBatchNumber,"COMPLETE",pendingBatchFirstHistoryId,pendingBatchLastHistoryId,rows.size(),units,pendingExportFileName);''',
'record complete number')

db='app/src/main/java/com/iceinventory/onhand/InventoryDb.java'
rep(db,
'''    public int nextBatchNumber(long sessionId) {
        ensureRecoveryTables(getReadableDatabase());
        try(Cursor c=getReadableDatabase().rawQuery("SELECT COALESCE(MAX(batch_no),0)+1 FROM export_batches WHERE session_id=? AND export_type='NEW'",new String[]{String.valueOf(sessionId)})) {
            return c.moveToFirst()?Math.max(1,c.getInt(0)):1;
        }
    }
''',
'''    public int nextBatchNumber(long sessionId) {
        ensureRecoveryTables(getReadableDatabase());
        try(Cursor c=getReadableDatabase().rawQuery("SELECT COALESCE(MAX(batch_no),0)+1 FROM export_batches WHERE session_id=? AND export_type='NEW'",new String[]{String.valueOf(sessionId)})) {
            return c.moveToFirst()?Math.max(1,c.getInt(0)):1;
        }
    }

    public int nextCompleteExportNumber(long sessionId) {
        ensureRecoveryTables(getReadableDatabase());
        try(Cursor c=getReadableDatabase().rawQuery("SELECT COALESCE(MAX(batch_no),0)+1 FROM export_batches WHERE session_id=? AND export_type='COMPLETE'",new String[]{String.valueOf(sessionId)})) {
            return c.moveToFirst()?Math.max(1,c.getInt(0)):1;
        }
    }
''',
'complete sequence query')

s=Path(main).read_text()
checks={
 'version':"versionName '3.0.176'" in Path('app/build.gradle').read_text(),
 'short name':'store+"-"+user+"-"+String.format(Locale.US,"%02d"' in s,
 'no complete seq':'_COMPLETE_Seq' not in s,
 'number query':'nextCompleteExportNumber' in Path(db).read_text(),
}
bad=[k for k,v in checks.items() if not v]
if bad: raise SystemExit('3.0.176 checks failed: '+', '.join(bad))
print('Prepared iCE OnHand 3.0.176: short STORE-USER-01 completed count filenames')
