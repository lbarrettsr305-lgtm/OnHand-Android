from pathlib import Path
import re

# Preserve every verified 3.0.93 feature first, including fresh Batch 01 reset.
base=Path('.github/prepare_3093.py')
exec(compile(base.read_text(),str(base),'exec'),{'__name__':'__main__','__file__':str(base)})

# -----------------------------------------------------------------------------
# 3.0.94 export workflow
#
# Default export contract:
#   tab-delimited TXT
#   Quantity | Barcode | Description | Price
#
# Navigation:
#   Export -> choose what to export -> format screen -> CONTINUE TO FILE
#   -> Android/save destination choices.
# -----------------------------------------------------------------------------
p=Path('app/src/main/java/com/iceinventory/onhand/MainActivity.java')
s=p.read_text()

# Export button now asks WHAT to export before opening format configuration.
old='''exp.setTypeface(Typeface.DEFAULT,Typeface.BOLD);exp.setOnClickListener(v->startExportFormatFlow());'''
new='''exp.setTypeface(Typeface.DEFAULT,Typeface.BOLD);exp.setOnClickListener(v->showExportScopeDialog());'''
if old not in s:raise SystemExit('3.0.94 target missing: Export button flow')
s=s.replace(old,new,1)

# Continue from the format screen now advances directly to the filename/destination dialog.
old='''        if(requestCode==REQ_EXPORT_FORMAT){\n            showExportScopeDialog();\n            return;\n        }\n'''
new='''        if(requestCode==REQ_EXPORT_FORMAT){\n            showExportDialog();\n            return;\n        }\n'''
if old not in s:raise SystemExit('3.0.94 target missing: export format result flow')
s=s.replace(old,new,1)

# Replace the whole Export Items menu so standard/new-count export is TXT first/default.
scope='''    private void showExportScopeDialog() {
        int next=db.nextBatchNumber(sessionId);
        String batch=String.format(Locale.US,"%02d",next);
        String[] choices={"Export New Counts Only (Batch "+batch+")","Export Complete Inventory — TXT","Export Complete Inventory — Excel (.xlsx)","Re-export Previous Batch","Internet Items With Pictures","Location Quantity Report"};
        new AlertDialog.Builder(this).setTitle("Export Items").setItems(choices,(d,which)->{
            if(which==0){pendingExportExcel=false;pendingExportInternetOnly=false;pendingExportLocationQuantityReport=false;beginNewBatchExport();return;}
            if(which==1){pendingExportExcel=false;pendingExportInternetOnly=false;pendingExportLocationQuantityReport=false;beginCompleteInventoryExport();return;}
            if(which==2){pendingExportExcel=true;pendingExportInternetOnly=false;pendingExportLocationQuantityReport=false;beginCompleteInventoryExport();return;}
            if(which==3){pendingExportExcel=false;pendingExportInternetOnly=false;pendingExportLocationQuantityReport=false;showBatchReExportDialog();return;}
            resetBatchExportState();
            if(which==4){pendingExportExcel=false;pendingExportInternetOnly=true;pendingExportLocationQuantityReport=false;if(internetItemCount()==0){toast("No internet items to export");return;}startExportFormatFlow();return;}
            pendingExportExcel=false;pendingExportInternetOnly=false;pendingExportLocationQuantityReport=true;startExportFormatFlow();
        }).setNegativeButton("Cancel",null).show();
    }
'''
pat=r'''    private void showExportScopeDialog\(\) \{.*?\n    \}\n(?=\n    private void beginNewBatchExport\(\))'''
s,n=re.subn(pat,lambda m:scope,s,count=1,flags=re.S)
if n!=1:raise SystemExit('3.0.94 target missing: export scope method')

# New-count and complete export selections go to format configuration first.
old='''        pendingExportInternetOnly=false;pendingBatchMode=1;pendingBatchNumber=db.nextBatchNumber(sessionId);pendingBatchFirstHistoryId=first;pendingBatchLastHistoryId=through;pendingBatchReplayId=0L;showExportDialog();'''
new='''        pendingExportInternetOnly=false;pendingBatchMode=1;pendingBatchNumber=db.nextBatchNumber(sessionId);pendingBatchFirstHistoryId=first;pendingBatchLastHistoryId=through;pendingBatchReplayId=0L;startExportFormatFlow();'''
if old not in s:raise SystemExit('3.0.94 target missing: new batch export choice')
s=s.replace(old,new,1)

old='''        pendingExportInternetOnly=false;pendingBatchMode=2;pendingBatchNumber=0;long last=db.maxHistoryId(sessionId);pendingBatchFirstHistoryId=db.firstHistoryIdAfter(sessionId,0L,last);pendingBatchLastHistoryId=last;pendingBatchReplayId=0L;showExportDialog();'''
new='''        pendingExportInternetOnly=false;pendingBatchMode=2;pendingBatchNumber=0;long last=db.maxHistoryId(sessionId);pendingBatchFirstHistoryId=db.firstHistoryIdAfter(sessionId,0L,last);pendingBatchLastHistoryId=last;pendingBatchReplayId=0L;startExportFormatFlow();'''
if old not in s:raise SystemExit('3.0.94 target missing: complete export choice')
s=s.replace(old,new,1)

# Previous-batch selection also goes through format screen before destination.
old='''pendingBatchReplayId=b.id;showExportDialog();}).setNegativeButton("Cancel",null).show();'''
new='''pendingBatchReplayId=b.id;startExportFormatFlow();}).setNegativeButton("Cancel",null).show();'''
if old not in s:raise SystemExit('3.0.94 target missing: re-export choice')
s=s.replace(old,new,1)

s=s.replace('Onhand Inventory 3.0.93','Onhand Inventory 3.0.94')
p.write_text(s)

# Keep exact standard tab-delimited heading/order requested by operator.
p=Path('app/src/main/java/com/iceinventory/onhand/TabTextUtils.java')
tab=p.read_text()
if 'private static final String DEFAULT_STRING="quantity,barcode,description,price";' not in tab:
    raise SystemExit('3.0.94 target missing: standard export field order')
if 'if("quantity".equals(field))return "Quantity";' not in tab:
    raise SystemExit('3.0.94 target missing: Quantity heading')
p.write_text(tab)

# Advance installable package version.
p=Path('app/build.gradle')
g=p.read_text().replace('versionCode 30093','versionCode 30094',1).replace("versionName '3.0.93'","versionName '3.0.94'",1)
if 'versionCode 30094' not in g or "versionName '3.0.94'" not in g:
    raise SystemExit('3.0.94 target missing: Gradle version')
p.write_text(g)

p=Path('app/src/main/AndroidManifest.xml')
m=p.read_text().replace('iCE Onhand 3.0.93','iCE Onhand 3.0.94')
if 'iCE Onhand 3.0.94' not in m:raise SystemExit('3.0.94 target missing: manifest version')
p.write_text(m)

# Regression checks for navigation, default TXT contract, destinations and safety.
main=Path('app/src/main/java/com/iceinventory/onhand/MainActivity.java').read_text()
tab=Path('app/src/main/java/com/iceinventory/onhand/TabTextUtils.java').read_text()
checks={
    'Export starts with export choices':'exp.setOnClickListener(v->showExportScopeDialog())' in main,
    'TXT is standard new-count choice':'String[] choices={"Export New Counts Only (Batch "+batch+")","Export Complete Inventory — TXT"' in main,
    'new-count defaults to TXT':'if(which==0){pendingExportExcel=false' in main,
    'Continue from format goes to destination dialog':'if(requestCode==REQ_EXPORT_FORMAT){\n            showExportDialog();' in main,
    'new batch choice opens format':'pendingBatchMode=1' in main and 'pendingBatchReplayId=0L;startExportFormatFlow();' in main,
    'complete choice opens format':'pendingBatchMode=2' in main and 'pendingBatchLastHistoryId=last;pendingBatchReplayId=0L;startExportFormatFlow();' in main,
    're-export choice opens format':'pendingBatchReplayId=b.id;startExportFormatFlow();' in main,
    'internet choice opens format':'pendingExportInternetOnly=true' in main and 'startExportFormatFlow();return;' in main,
    'destination dialog has Downloads':'Save to Downloads' in main,
    'destination dialog has Drive':'Save to Google Drive' in main,
    'standard four-field order':'DEFAULT_STRING="quantity,barcode,description,price"' in tab,
    'Quantity heading':'if("quantity".equals(field))return "Quantity";' in tab,
    'tab delimiter':"b.append('\\t')" in tab,
    'header always emitted':'b.append("\\r\\n");' in tab,
    'fresh batch reset preserved':'db.resetSessionForReplacementImport(sessionId);' in main,
    'batch consolidation preserved':'Combine and Verify User Batches' in main,
}
missing=[k for k,v in checks.items() if not v]
if missing:raise SystemExit('3.0.94 verification failed: '+', '.join(missing))
print('Prepared iCE Onhand 3.0.94: TXT default + Quantity/Barcode/Description/Price + direct destination flow')
