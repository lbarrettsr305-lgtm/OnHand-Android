from pathlib import Path

# Preserve every verified 3.0.92 feature first, including batch consolidation.
base=Path('.github/prepare_3092.py')
exec(compile(base.read_text(),str(base),'exec'),{'__name__':'__main__','__file__':str(base)})

# -----------------------------------------------------------------------------
# 3.0.93: A replacement import is a NEW inventory cycle.
#
# 3.0.92 cleared only the live item rows. Because the same session_id was kept,
# export_batches and scan_history from the prior imported file remained. That made
# nextBatchNumber(sessionId) continue the old Batch number and could also let old
# journal rows participate in a newly-reset batch series.
#
# Keep the existing transaction-safe Replace Import flow, but reset all session
# state that belongs to the old counting cycle: live items, scan journal and batch
# ledger. Recovery snapshots are intentionally NOT removed; the pre-replace safety
# checkpoint remains available if the operator needs to recover the previous data.
# -----------------------------------------------------------------------------
p=Path('app/src/main/java/com/iceinventory/onhand/InventoryDb.java')
s=p.read_text()
marker='''    public void clearSessionItems(long sessionId) {\n        if(sessionId<=0)return;\n        getWritableDatabase().delete("items","session_id=?",new String[]{String.valueOf(sessionId)});\n    }\n\n'''
addition='''    public void clearSessionItems(long sessionId) {\n        if(sessionId<=0)return;\n        getWritableDatabase().delete("items","session_id=?",new String[]{String.valueOf(sessionId)});\n    }\n\n    public void resetSessionForReplacementImport(long sessionId) {\n        if(sessionId<=0)return;\n        android.database.sqlite.SQLiteDatabase sql=getWritableDatabase();\n        ensureRecoveryTables(sql);\n        String[] args=new String[]{String.valueOf(sessionId)};\n        sql.delete("items","session_id=?",args);\n        sql.delete("scan_history","session_id=?",args);\n        sql.delete("export_batches","session_id=?",args);\n    }\n\n'''
if 'public void resetSessionForReplacementImport(long sessionId)' not in s:
    if marker not in s:raise SystemExit('3.0.93 DB target missing: clearSessionItems')
    s=s.replace(marker,addition,1)
p.write_text(s)

p=Path('app/src/main/java/com/iceinventory/onhand/MainActivity.java')
s=p.read_text()
old='''                db.clearSessionItems(sessionId);\n'''
new='''                db.resetSessionForReplacementImport(sessionId);\n'''
if old not in s:raise SystemExit('3.0.93 Main target missing: replace-import clear call')
s=s.replace(old,new,1)
s=s.replace('Onhand Inventory 3.0.92','Onhand Inventory 3.0.93')
p.write_text(s)

# Advance installable package version.
p=Path('app/build.gradle')
s=p.read_text().replace('versionCode 30092','versionCode 30093',1).replace("versionName '3.0.92'","versionName '3.0.93'",1)
if 'versionCode 30093' not in s or "versionName '3.0.93'" not in s:
    raise SystemExit('3.0.93 target missing: Gradle version')
p.write_text(s)

p=Path('app/src/main/AndroidManifest.xml')
s=p.read_text().replace('iCE Onhand 3.0.92','iCE Onhand 3.0.93')
p.write_text(s)

# Build-time regression checks for this exact bug.
main=Path('app/src/main/java/com/iceinventory/onhand/MainActivity.java').read_text()
db=Path('app/src/main/java/com/iceinventory/onhand/InventoryDb.java').read_text()
checks={
    'replace import resets counting cycle':'db.resetSessionForReplacementImport(sessionId);' in main,
    'old items cleared':'sql.delete("items","session_id=?",args);' in db,
    'old scan journal cleared':'sql.delete("scan_history","session_id=?",args);' in db,
    'old batch ledger cleared':'sql.delete("export_batches","session_id=?",args);' in db,
    'batch numbering remains ledger based':'MAX(batch_no),0)+1 FROM export_batches' in db,
    '3.0.92 consolidation preserved':'Combine and Verify User Batches' in main,
}
missing=[k for k,v in checks.items() if not v]
if missing:raise SystemExit('3.0.93 verification failed: '+', '.join(missing))
print('Prepared iCE Onhand 3.0.93: replacement import starts a fresh Batch 01 cycle')
