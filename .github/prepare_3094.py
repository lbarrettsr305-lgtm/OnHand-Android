from pathlib import Path

# Preserve every verified 3.0.93 feature first, including fresh Batch 01 reset.
base=Path('.github/prepare_3093.py')
exec(compile(base.read_text(),str(base),'exec'),{'__name__':'__main__','__file__':str(base)})

# -----------------------------------------------------------------------------
# 3.0.94: Make export navigation match the operator's mental model.
#
# OLD: Export -> format screen -> CONTINUE TO FILE -> Export Items -> destination.
# NEW: Export -> Export Items -> format screen -> CONTINUE TO FILE -> destination.
#
# This makes CONTINUE TO FILE actually continue toward the file destination instead
# of returning to another export-choice menu. Existing batch calculations, file
# naming, Downloads saving, document-picker/Drive saving, and export contents stay
# unchanged.
# -----------------------------------------------------------------------------
p=Path('app/src/main/java/com/iceinventory/onhand/MainActivity.java')
s=p.read_text()

old='''exp.setTypeface(Typeface.DEFAULT,Typeface.BOLD);exp.setOnClickListener(v->startExportFormatFlow());'''
new='''exp.setTypeface(Typeface.DEFAULT,Typeface.BOLD);exp.setOnClickListener(v->showExportScopeDialog());'''
if old not in s:raise SystemExit('3.0.94 target missing: Export button flow')
s=s.replace(old,new,1)

old='''        if(requestCode==REQ_EXPORT_FORMAT){\n            showExportScopeDialog();\n            return;\n        }\n'''
new='''        if(requestCode==REQ_EXPORT_FORMAT){\n            showExportDialog();\n            return;\n        }\n'''
if old not in s:raise SystemExit('3.0.94 target missing: export format result flow')
s=s.replace(old,new,1)

old='''            pendingBatchMode=0;pendingExportInternetOnly=true;if(internetItemCount()==0){toast("No internet items to export");return;}showExportDialog();'''
new='''            pendingBatchMode=0;pendingExportInternetOnly=true;if(internetItemCount()==0){toast("No internet items to export");return;}startExportFormatFlow();'''
if old not in s:raise SystemExit('3.0.94 target missing: internet export choice')
s=s.replace(old,new,1)

old='''        pendingExportInternetOnly=false;pendingBatchMode=1;pendingBatchNumber=db.nextBatchNumber(sessionId);pendingBatchFirstHistoryId=first;pendingBatchLastHistoryId=through;pendingBatchReplayId=0L;showExportDialog();'''
new='''        pendingExportInternetOnly=false;pendingBatchMode=1;pendingBatchNumber=db.nextBatchNumber(sessionId);pendingBatchFirstHistoryId=first;pendingBatchLastHistoryId=through;pendingBatchReplayId=0L;startExportFormatFlow();'''
if old not in s:raise SystemExit('3.0.94 target missing: new batch export choice')
s=s.replace(old,new,1)

old='''        pendingExportInternetOnly=false;pendingBatchMode=2;pendingBatchNumber=0;long last=db.maxHistoryId(sessionId);pendingBatchFirstHistoryId=db.firstHistoryIdAfter(sessionId,0L,last);pendingBatchLastHistoryId=last;pendingBatchReplayId=0L;showExportDialog();'''
new='''        pendingExportInternetOnly=false;pendingBatchMode=2;pendingBatchNumber=0;long last=db.maxHistoryId(sessionId);pendingBatchFirstHistoryId=db.firstHistoryIdAfter(sessionId,0L,last);pendingBatchLastHistoryId=last;pendingBatchReplayId=0L;startExportFormatFlow();'''
if old not in s:raise SystemExit('3.0.94 target missing: complete export choice')
s=s.replace(old,new,1)

old='''pendingBatchReplayId=b.id;showExportDialog();}).setNegativeButton("Cancel",null).show();'''
new='''pendingBatchReplayId=b.id;startExportFormatFlow();}).setNegativeButton("Cancel",null).show();'''
if old not in s:raise SystemExit('3.0.94 target missing: re-export choice')
s=s.replace(old,new,1)

s=s.replace('Onhand Inventory 3.0.93','Onhand Inventory 3.0.94')
p.write_text(s)

# Advance installable package version.
p=Path('app/build.gradle')
s=p.read_text().replace('versionCode 30093','versionCode 30094',1).replace("versionName '3.0.93'","versionName '3.0.94'",1)
if 'versionCode 30094' not in s or "versionName '3.0.94'" not in s:
    raise SystemExit('3.0.94 target missing: Gradle version')
p.write_text(s)

p=Path('app/src/main/AndroidManifest.xml')
s=p.read_text().replace('iCE Onhand 3.0.93','iCE Onhand 3.0.94')
p.write_text(s)

# Build-time regression checks for the new navigation and preserved safety.
main=Path('app/src/main/java/com/iceinventory/onhand/MainActivity.java').read_text()
checks={
    'Export starts with export choices':'exp.setOnClickListener(v->showExportScopeDialog())' in main,
    'Continue from format goes to destination dialog':'if(requestCode==REQ_EXPORT_FORMAT){\n            showExportDialog();' in main,
    'new batch choice opens format':'pendingBatchMode=1' in main and 'pendingBatchReplayId=0L;startExportFormatFlow();' in main,
    'complete choice opens format':'pendingBatchMode=2' in main and 'pendingBatchLastHistoryId=last;pendingBatchReplayId=0L;startExportFormatFlow();' in main,
    're-export choice opens format':'pendingBatchReplayId=b.id;startExportFormatFlow();' in main,
    'internet choice opens format':'pendingExportInternetOnly=true' in main and 'startExportFormatFlow();' in main,
    'destination dialog still has Downloads':'Save to Downloads' in main,
    'destination dialog still has Drive':'Save to Google Drive' in main,
    '3.0.93 fresh batch reset preserved':'db.resetSessionForReplacementImport(sessionId);' in main,
    '3.0.92 consolidation preserved':'Combine and Verify User Batches' in main,
}
missing=[k for k,v in checks.items() if not v]
if missing:raise SystemExit('3.0.94 verification failed: '+', '.join(missing))
print('Prepared iCE Onhand 3.0.94: Export choice first; Continue to File opens destination choices')
