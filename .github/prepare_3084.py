from pathlib import Path
import re

# Generate the verified 3.0.83 source first, then make Excel the default for
# new batch exports while retaining a separate TXT batch choice.
base = Path('.github/prepare_3083_release.py')
exec(compile(base.read_text(), str(base), 'exec'), {'__name__': '__main__', '__file__': str(base)})

p = Path('app/src/main/java/com/iceinventory/onhand/MainActivity.java')
s = p.read_text()

scope = r'''    private void showExportScopeDialog() {
        int next=db.nextBatchNumber(sessionId);
        String batch=String.format(Locale.US,"%02d",next);
        String[] choices={"Export New Counts Only — Excel (.xlsx) (Batch "+batch+")","Export New Counts Only — TXT (Batch "+batch+")","Export Complete Inventory — TXT","Export Complete Inventory — Excel (.xlsx)","Re-export Previous Batch","Internet Items With Pictures","Location Quantity Report"};
        new AlertDialog.Builder(this).setTitle("Export Items").setItems(choices,(d,which)->{
            if(which==0){pendingExportExcel=true;pendingExportInternetOnly=false;pendingExportLocationQuantityReport=false;beginNewBatchExport();return;}
            if(which==1){pendingExportExcel=false;pendingExportInternetOnly=false;pendingExportLocationQuantityReport=false;beginNewBatchExport();return;}
            if(which==2){pendingExportExcel=false;pendingExportInternetOnly=false;pendingExportLocationQuantityReport=false;beginCompleteInventoryExport();return;}
            if(which==3){pendingExportExcel=true;pendingExportInternetOnly=false;pendingExportLocationQuantityReport=false;beginCompleteInventoryExport();return;}
            if(which==4){pendingExportExcel=false;pendingExportInternetOnly=false;pendingExportLocationQuantityReport=false;showBatchReExportDialog();return;}
            resetBatchExportState();
            if(which==5){pendingExportExcel=false;pendingExportInternetOnly=true;pendingExportLocationQuantityReport=false;if(internetItemCount()==0){toast("No internet items to export");return;}showExportDialog();return;}
            pendingExportExcel=false;pendingExportInternetOnly=false;pendingExportLocationQuantityReport=true;showExportDialog();
        }).setNegativeButton("Cancel",null).show();
    }
'''
pat = r'''    private void showExportScopeDialog\(\) \{.*?\n    \}\n(?=\n    private void beginNewBatchExport\(\))'''
s, n = re.subn(pat, lambda m: scope, s, count=1, flags=re.S)
if n != 1:
    raise SystemExit('3.0.84 target missing: export scope')

s, n = re.subn(
    r'''    private String batchExportFileName\(\)\{.*?\}\n''',
    lambda m: '''    private String batchExportFileName(){String day=new SimpleDateFormat("yyyy-MM-dd_HHmm",Locale.US).format(new Date());String ext=pendingExportExcel?".xlsx":".txt";return safeFileName(sessionName)+"_Batch"+String.format(Locale.US,"%02d",Math.max(1,pendingBatchNumber))+"_Seq"+seqText(pendingBatchFirstHistoryId)+"-"+seqText(pendingBatchLastHistoryId)+"_"+day+ext;}\n''',
    s, count=1, flags=re.S)
if n != 1:
    raise SystemExit('3.0.84 target missing: batch filename')

old = '''new AlertDialog.Builder(this).setTitle("Re-export Previous Batch").setItems(labels,(d,which)->{InventoryDb.ExportBatch b=batches.get(which);pendingExportInternetOnly=false;pendingBatchMode=3;pendingBatchNumber=b.batchNumber;pendingBatchFirstHistoryId=b.firstHistoryId;pendingBatchLastHistoryId=b.lastHistoryId;pendingBatchReplayId=b.id;showExportDialog();}).setNegativeButton("Cancel",null).show();'''
new = '''new AlertDialog.Builder(this).setTitle("Re-export Previous Batch").setItems(labels,(d,which)->{InventoryDb.ExportBatch b=batches.get(which);pendingExportExcel=b.filename!=null&&b.filename.toLowerCase(Locale.US).endsWith(".xlsx");pendingExportInternetOnly=false;pendingBatchMode=3;pendingBatchNumber=b.batchNumber;pendingBatchFirstHistoryId=b.firstHistoryId;pendingBatchLastHistoryId=b.lastHistoryId;pendingBatchReplayId=b.id;showExportDialog();}).setNegativeButton("Cancel",null).show();'''
if old not in s:
    raise SystemExit('3.0.84 target missing: batch replay picker')
s = s.replace(old, new, 1)

old = '''                os.write(BatchExportText.exportRows(rows,prefs()).getBytes(StandardCharsets.UTF_8));'''
new = '''                if(pendingExportExcel)SimpleXlsxWriter.writeBatch(os,rows,prefs());
                else os.write(BatchExportText.exportRows(rows,prefs()).getBytes(StandardCharsets.UTF_8));'''
if old not in s:
    raise SystemExit('3.0.84 target missing: batch writer')
s = s.replace(old, new, 1)

s = s.replace('Onhand Inventory 3.0.83', 'Onhand Inventory 3.0.84')
p.write_text(s)

p = Path('app/build.gradle')
s = p.read_text().replace('versionCode 30083', 'versionCode 30084', 1).replace("versionName '3.0.83'", "versionName '3.0.84'", 1)
if 'versionCode 30084' not in s or "versionName '3.0.84'" not in s:
    raise SystemExit('3.0.84 target missing: Gradle version')
p.write_text(s)

p = Path('app/src/main/AndroidManifest.xml')
s = p.read_text().replace('iCE Onhand 3.0.83', 'iCE Onhand 3.0.84')
if 'iCE Onhand 3.0.84' not in s:
    raise SystemExit('3.0.84 target missing: manifest version')
p.write_text(s)

main = Path('app/src/main/java/com/iceinventory/onhand/MainActivity.java').read_text()
checks = {
    'Excel-first batch choice': 'Export New Counts Only — Excel (.xlsx)',
    'TXT batch choice': 'Export New Counts Only — TXT',
    'XLSX batch filename': 'String ext=pendingExportExcel?".xlsx":".txt"',
    'XLSX batch writer': 'SimpleXlsxWriter.writeBatch(os,rows,prefs())',
    'format-aware replay': 'b.filename.toLowerCase(Locale.US).endsWith(".xlsx")',
}
missing = [label for label, needle in checks.items() if needle not in main]
if missing:
    raise SystemExit('3.0.84 verification failed: ' + ', '.join(missing))
print('Prepared iCE Onhand 3.0.84: Excel-first batch export with TXT fallback and format-safe replay')
