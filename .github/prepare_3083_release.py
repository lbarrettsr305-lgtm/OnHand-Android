from pathlib import Path
import re

# 3.0.83 is layered on the verified 3.0.82 release.  The generated 3.0.82
# source also contains newer export modes (Excel + Location Quantity Report),
# so make the one older filename anchor tolerant before executing 3.0.83.
source_path=Path('.github/prepare_3083.py')
src=source_path.read_text()
old="elif 'pendingBatchMode==1||pendingBatchMode==3' not in s:raise SystemExit('3.0.83 Main target missing: export filename block')"
new="""elif 'pendingBatchMode==1||pendingBatchMode==3' not in s:\n    anchor='        String exportName=userExportFileName(exportUser,defaultName);\\n'\n    if anchor not in s:raise SystemExit('3.0.83 Main target missing: export filename anchor')\n    s=s.replace(anchor,anchor+'        if(pendingBatchMode==1||pendingBatchMode==3)exportName=batchExportFileName();\\n        else if(pendingBatchMode==2)exportName=completeExportFileName();\\n',1)"""
if old not in src:
    raise SystemExit('3.0.83 release wrapper target missing: compatibility clause')
src=src.replace(old,new,1)
exec(compile(src,str(source_path),'exec'),{'__name__':'__main__','__file__':str(source_path)})

# Preserve all pre-existing export modes while adding the three batch choices.
p=Path('app/src/main/java/com/iceinventory/onhand/MainActivity.java')
s=p.read_text()

scope=r'''    private void showExportScopeDialog() {
        int next=db.nextBatchNumber(sessionId);
        String[] choices={"Export New Counts Only (Batch "+String.format(Locale.US,"%02d",next)+")","Export Complete Inventory — TXT","Export Complete Inventory — Excel (.xlsx)","Re-export Previous Batch","Internet Items With Pictures","Location Quantity Report"};
        new AlertDialog.Builder(this).setTitle("Export Items").setItems(choices,(d,which)->{
            if(which==0){pendingExportExcel=false;pendingExportInternetOnly=false;pendingExportLocationQuantityReport=false;beginNewBatchExport();return;}
            if(which==1){pendingExportExcel=false;pendingExportInternetOnly=false;pendingExportLocationQuantityReport=false;beginCompleteInventoryExport();return;}
            if(which==2){pendingExportExcel=true;pendingExportInternetOnly=false;pendingExportLocationQuantityReport=false;beginCompleteInventoryExport();return;}
            if(which==3){pendingExportExcel=false;pendingExportInternetOnly=false;pendingExportLocationQuantityReport=false;showBatchReExportDialog();return;}
            resetBatchExportState();
            if(which==4){pendingExportExcel=false;pendingExportInternetOnly=true;pendingExportLocationQuantityReport=false;if(internetItemCount()==0){toast("No internet items to export");return;}showExportDialog();return;}
            pendingExportExcel=false;pendingExportInternetOnly=false;pendingExportLocationQuantityReport=true;showExportDialog();
        }).setNegativeButton("Cancel",null).show();
    }
'''
pat=r'''    private void showExportScopeDialog\(\) \{.*?\n    \}\n(?=\n    private void beginNewBatchExport\(\))'''
s2,n=re.subn(pat,lambda m:scope,s,count=1,flags=re.S)
if n!=1:raise SystemExit('3.0.83 release target missing: generated export scope')
s=s2

# Batch filenames always identify the immutable sequence range. Complete Excel
# gets .xlsx; batch delta/replay stays tab-delimited TXT so corrections can be
# represented exactly and imported by downstream inventory systems.
pat=r'''    private String completeExportFileName\(\)\{.*?\}\n'''
repl='''    private String completeExportFileName(){String day=new SimpleDateFormat("yyyy-MM-dd_HHmm",Locale.US).format(new Date());String ext=pendingExportExcel?".xlsx":".txt";return safeFileName(sessionName)+"_COMPLETE_Seq"+seqText(pendingBatchFirstHistoryId)+"-"+seqText(pendingBatchLastHistoryId)+"_"+day+ext;}\n'''
s2,n=re.subn(pat,lambda m:repl,s,count=1,flags=re.S)
if n!=1:raise SystemExit('3.0.83 release target missing: complete filename helper')
s=s2

# Give batch/complete naming priority over the legacy format-specific helpers.
start='        String exportName=userExportFileName(exportUser,defaultName);\n'
pos=s.find(start)
if pos<0:raise SystemExit('3.0.83 release target missing: generated exportName')
name_end=s.find('        name.setText(exportName);\n',pos)
if name_end<0:raise SystemExit('3.0.83 release target missing: generated name.setText')
name_block='''        String exportName=userExportFileName(exportUser,defaultName);\n        if(pendingBatchMode==1||pendingBatchMode==3)exportName=batchExportFileName();\n        else if(pendingBatchMode==2)exportName=completeExportFileName();\n        else {\n            if(pendingExportExcel)exportName=excelExportFileName(exportName);\n            if(pendingExportInternetOnly)exportName=internetExportFileName(exportName);\n            if(pendingExportLocationQuantityReport)exportName=locationQuantityExportFileName(exportName);\n        }\n'''
s=s[:pos]+name_block+s[name_end:]

# Rebuild the writer so no established export format is lost. Only a successful
# NEW batch advances the export ledger. Cancelled/failed exports remain pending.
writer=r'''    private void writeExport(Uri uri) {
        if(uri==null)return;
        try(OutputStream os=getContentResolver().openOutputStream(uri)) {
            if(os==null)throw new Exception("No output stream");
            if(pendingExportLocationQuantityReport) {
                os.write(buildLocationQuantityReport(db.items(sessionId)).getBytes(StandardCharsets.UTF_8));
                toast("Location quantity report exported");
            } else if(pendingBatchMode==1||pendingBatchMode==3) {
                long after=pendingBatchFirstHistoryId>0?pendingBatchFirstHistoryId-1:0L;
                List<InventoryDb.Row> rows=db.batchRows(sessionId,after,pendingBatchLastHistoryId);
                os.write(BatchExportText.exportRows(rows,prefs()).getBytes(StandardCharsets.UTF_8));
                if(pendingBatchMode==1) {
                    int units=0;for(InventoryDb.Row r:rows)units+=r.quantity;
                    db.recordExportBatch(sessionId,pendingBatchNumber,"NEW",pendingBatchFirstHistoryId,pendingBatchLastHistoryId,rows.size(),units,pendingExportFileName);
                    safetyCheckpoint("After Batch "+pendingBatchNumber,true);
                    toast("Batch "+String.format(Locale.US,"%02d",pendingBatchNumber)+" exported • "+rows.size()+" lines");
                } else toast("Batch "+String.format(Locale.US,"%02d",pendingBatchNumber)+" re-exported");
            } else if(pendingBatchMode==2) {
                List<InventoryDb.Row> rows=db.itemsInScanOrder(sessionId);
                if(pendingExportExcel)SimpleXlsxWriter.write(os,rows,prefs());
                else os.write(TabTextUtils.exportRows(rows,prefs()).getBytes(StandardCharsets.UTF_8));
                int units=0;for(InventoryDb.Row r:rows)units+=r.quantity;
                db.recordExportBatch(sessionId,0,"COMPLETE",pendingBatchFirstHistoryId,pendingBatchLastHistoryId,rows.size(),units,pendingExportFileName);
                safetyCheckpoint("After Complete Export",true);
                toast(pendingExportExcel?"Complete inventory Excel exported • "+rows.size()+" lines":"Complete inventory exported • "+rows.size()+" lines");
            } else if(pendingExportExcel) {
                SimpleXlsxWriter.write(os,db.items(sessionId),prefs());
                toast("Excel workbook exported");
            } else if(pendingExportInternetOnly) {
                os.write(buildInternetItemsHtml().getBytes(StandardCharsets.UTF_8));
                toast("Internet items with pictures exported");
            } else {
                os.write(TabTextUtils.exportRows(db.items(sessionId),prefs()).getBytes(StandardCharsets.UTF_8));
                toast("Tab-delimited TXT exported");
            }
            if(!pendingExportInternetOnly&&!pendingExportLocationQuantityReport)resetBatchExportState();
        } catch(Exception e){showError("Export failed",e);}
    }
'''
pat=r'''    private void writeExport\(Uri uri\) \{.*?\n    \}\n(?=\n    private void readImport)'''
s2,n=re.subn(pat,lambda m:writer,s,count=1,flags=re.S)
if n!=1:raise SystemExit('3.0.83 release target missing: generated writer')
s=s2

# Hard verification of coexistence: batch modes plus every prior export mode.
required={
    'new batch choice':'Export New Counts Only (Batch ',
    'complete TXT choice':'Export Complete Inventory — TXT',
    'complete Excel choice':'Export Complete Inventory — Excel (.xlsx)',
    're-export choice':'Re-export Previous Batch',
    'internet report choice':'Internet Items With Pictures',
    'location report choice':'Location Quantity Report',
    'batch-safe writer':'BatchExportText.exportRows(rows,prefs())',
    'complete Excel writer':'SimpleXlsxWriter.write(os,rows,prefs())',
    'legacy Excel writer':'SimpleXlsxWriter.write(os,db.items(sessionId),prefs())',
    'location report writer':'buildLocationQuantityReport(db.items(sessionId))',
    'batch ledger':'recordExportBatch(sessionId,pendingBatchNumber,"NEW"',
    'original scan order':'Original scan order'
}
missing=[label for label,needle in required.items() if needle not in s]
if missing:raise SystemExit('3.0.83 release coexistence verification failed: '+', '.join(missing))
p.write_text(s)
print('Prepared iCE Onhand 3.0.83 release: batch ledger, safe replay, complete TXT/Excel, original scan order, and all prior report exports preserved')
