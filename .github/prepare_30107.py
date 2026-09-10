from pathlib import Path

# Preserve the validated 3.0.106 subtraction and older-device search fixes.
base=Path('.github/prepare_30106.py')
exec(compile(base.read_text(),str(base),'exec'),{'__name__':'__main__','__file__':str(base)})

p=Path('app/src/main/java/com/iceinventory/onhand/MainActivity.java')
s=p.read_text()

s=s.replace(
    'private boolean pendingExportLocationQuantityReport=false;',
    'private boolean pendingExportLocationQuantityReport=false;\n    private boolean pendingExportLocationDetailReport=false;',
    1)

old='''        String[] choices={"Export New Counts Only (Batch "+batch+")","Export Complete Inventory — TXT","Export Complete Inventory — Excel (.xlsx)","Re-export Previous Batch","Combine & Verify User Batches — Master User","Internet Items With Pictures","Location Quantity Report"};
        new AlertDialog.Builder(this).setTitle("Export Items").setItems(choices,(d,which)->{
            if(which==0){pendingExportExcel=false;pendingExportInternetOnly=false;pendingExportLocationQuantityReport=false;beginNewBatchExport();return;}
            if(which==1){pendingExportExcel=false;pendingExportInternetOnly=false;pendingExportLocationQuantityReport=false;beginCompleteInventoryExport();return;}
            if(which==2){pendingExportExcel=true;pendingExportInternetOnly=false;pendingExportLocationQuantityReport=false;beginCompleteInventoryExport();return;}
            if(which==3){pendingExportExcel=false;pendingExportInternetOnly=false;pendingExportLocationQuantityReport=false;showBatchReExportDialog();return;}
            if(which==4){resetBatchExportState();openBatchMergeForMaster();return;}
            resetBatchExportState();
            if(which==5){pendingExportExcel=false;pendingExportInternetOnly=true;pendingExportLocationQuantityReport=false;if(internetItemCount()==0){toast("No internet items to export");return;}startExportFormatFlow();return;}
            pendingExportExcel=false;pendingExportInternetOnly=false;pendingExportLocationQuantityReport=true;startExportFormatFlow();
        }).setNegativeButton("Cancel",null).show();
'''
new='''        String[] choices={"Export New Counts Only (Batch "+batch+")","Export Complete Inventory — TXT","Export Complete Inventory — Excel (.xlsx)","Re-export Previous Batch","Combine & Verify User Batches — Master User","Internet Items With Pictures","Location Quantity Report","Location Detail Report — Scan Order"};
        new AlertDialog.Builder(this).setTitle("Export Items").setItems(choices,(d,which)->{
            if(which==0){pendingExportExcel=false;pendingExportInternetOnly=false;pendingExportLocationQuantityReport=false;pendingExportLocationDetailReport=false;beginNewBatchExport();return;}
            if(which==1){pendingExportExcel=false;pendingExportInternetOnly=false;pendingExportLocationQuantityReport=false;pendingExportLocationDetailReport=false;beginCompleteInventoryExport();return;}
            if(which==2){pendingExportExcel=true;pendingExportInternetOnly=false;pendingExportLocationQuantityReport=false;pendingExportLocationDetailReport=false;beginCompleteInventoryExport();return;}
            if(which==3){pendingExportExcel=false;pendingExportInternetOnly=false;pendingExportLocationQuantityReport=false;pendingExportLocationDetailReport=false;showBatchReExportDialog();return;}
            if(which==4){pendingExportLocationDetailReport=false;resetBatchExportState();openBatchMergeForMaster();return;}
            resetBatchExportState();
            if(which==5){pendingExportExcel=false;pendingExportInternetOnly=true;pendingExportLocationQuantityReport=false;pendingExportLocationDetailReport=false;if(internetItemCount()==0){toast("No internet items to export");return;}startExportFormatFlow();return;}
            pendingExportExcel=false;pendingExportInternetOnly=false;
            if(which==6){pendingExportLocationQuantityReport=true;pendingExportLocationDetailReport=false;startExportFormatFlow();return;}
            pendingExportLocationQuantityReport=false;pendingExportLocationDetailReport=true;startExportFormatFlow();
        }).setNegativeButton("Cancel",null).show();
'''
if old not in s: raise SystemExit('3.0.107 target missing: Export Items menu')
s=s.replace(old,new,1)

marker='''    private String buildLocationQuantityReport(List<InventoryDb.Row> rows) {
'''
addition='''    private String locationDetailExportFileName(String name) {
        String n=cleanTextName(name);
        if(n.toLowerCase(Locale.US).endsWith(".txt"))n=n.substring(0,n.length()-4);
        if(!n.toLowerCase(Locale.US).endsWith(" - location detail"))n+=" - Location Detail";
        return n+".txt";
    }

    private String reportField(String value) {
        return (value==null?"":value).replace("\\t"," ").replace("\\r"," ").replace("\\n"," ");
    }

    private String buildLocationDetailReport() {
        String user=reportField(savedUserName());
        StringBuilder out=new StringBuilder("User\\tLocation\\tQuantity\\tBarcode\\tDescription\\tPrice\\r\\n");
        for(InventoryDb.Row r:db.itemsInScanOrder(sessionId)) {
            out.append(user).append('\\t')
                    .append(reportField(r.location==null||r.location.trim().isEmpty()?"Main":r.location.trim())).append('\\t')
                    .append(r.quantity).append('\\t')
                    .append(reportField(r.barcode)).append('\\t')
                    .append(reportField(r.description)).append('\\t')
                    .append(reportField(r.price)).append("\\r\\n");
        }
        return out.toString();
    }

'''+marker
if marker not in s: raise SystemExit('3.0.107 target missing: location report builder')
s=s.replace(marker,addition,1)

s=s.replace(
    'if(pendingExportLocationQuantityReport)exportName=locationQuantityExportFileName(exportName);',
    'if(pendingExportLocationQuantityReport)exportName=locationQuantityExportFileName(exportName);\n            if(pendingExportLocationDetailReport)exportName=locationDetailExportFileName(exportName);',
    1)
s=s.replace(
    'String exportTitle=pendingExportLocationQuantityReport?"Location Quantity Report":(pendingExportInternetOnly?"Export Internet Items With Pictures":(pendingExportExcel?"Export Excel":"Export TXT"));',
    'String exportTitle=pendingExportLocationDetailReport?"Location Detail Report":(pendingExportLocationQuantityReport?"Location Quantity Report":(pendingExportInternetOnly?"Export Internet Items With Pictures":(pendingExportExcel?"Export Excel":"Export TXT")));',
    1)
s=s.replace(
    'String exportMessage=pendingExportLocationQuantityReport?"Separate TXT report • total quantity for each location plus a grand total.":(pendingExportInternetOnly?"Separate HTML report • internet-added items with associated product pictures.":(pendingExportExcel?"Excel workbook • same inventory columns and headers as TXT.":"All inventory items • tab-delimited TXT file."));',
    'String exportMessage=pendingExportLocationDetailReport?"User, Location, Quantity, Barcode, Description and Price • original scan order.":(pendingExportLocationQuantityReport?"Separate TXT report • total quantity for each location plus a grand total.":(pendingExportInternetOnly?"Separate HTML report • internet-added items with associated product pictures.":(pendingExportExcel?"Excel workbook • same inventory columns and headers as TXT.":"All inventory items • tab-delimited TXT file.")));',
    1)

old='''            if(pendingExportLocationQuantityReport) {
                os.write(buildLocationQuantityReport(db.items(sessionId)).getBytes(StandardCharsets.UTF_8));
                toast("Location quantity report exported");
            } else if(pendingBatchMode==1||pendingBatchMode==3) {
'''
new='''            if(pendingExportLocationDetailReport) {
                os.write(buildLocationDetailReport().getBytes(StandardCharsets.UTF_8));
                toast("Location detail report exported in scan order");
            } else if(pendingExportLocationQuantityReport) {
                os.write(buildLocationQuantityReport(db.items(sessionId)).getBytes(StandardCharsets.UTF_8));
                toast("Location quantity report exported");
            } else if(pendingBatchMode==1||pendingBatchMode==3) {
'''
if old not in s: raise SystemExit('3.0.107 target missing: report write routing')
s=s.replace(old,new,1)
s=s.replace(
    'if(!pendingExportInternetOnly&&!pendingExportLocationQuantityReport)resetBatchExportState();',
    'if(!pendingExportInternetOnly&&!pendingExportLocationQuantityReport&&!pendingExportLocationDetailReport)resetBatchExportState();',
    1)

s=s.replace('Onhand Inventory 3.0.106','Onhand Inventory 3.0.107',1)
if 'Onhand Inventory 3.0.107' not in s: raise SystemExit('3.0.107 visible version target missing')
p.write_text(s)

# Keep the highlighted yellow row at the same readable size on older devices.
p=Path('app/src/main/java/com/iceinventory/onhand/InventoryAdapter.java')
a=p.read_text()
old='''        root.setPadding(dp(compact?6:8),dp(compact?3:6),dp(compact?6:8),dp(compact?3:6));
        root.setBackgroundColor(bg);
'''
new='''        root.setPadding(dp(compact?6:8),dp(compact?3:6),dp(compact?6:8),dp(compact?3:6));
        root.setMinimumHeight(dp(active?58:(compact?48:58)));
        root.setBackgroundColor(bg);
'''
if old not in a: raise SystemExit('3.0.107 target missing: highlighted list row sizing')
a=a.replace(old,new,1)
p.write_text(a)

p=Path('app/build.gradle')
g=p.read_text().replace('versionCode 30106','versionCode 30107',1).replace("versionName '3.0.106'","versionName '3.0.107'",1)
if 'versionCode 30107' not in g or "versionName '3.0.107'" not in g: raise SystemExit('3.0.107 Gradle version target missing')
p.write_text(g)

p=Path('app/src/main/AndroidManifest.xml')
m=p.read_text().replace('iCE Onhand 3.0.106','iCE Onhand 3.0.107',1)
if 'iCE Onhand 3.0.107' not in m: raise SystemExit('3.0.107 manifest version target missing')
p.write_text(m)

main=Path('app/src/main/java/com/iceinventory/onhand/MainActivity.java').read_text()
adapter=Path('app/src/main/java/com/iceinventory/onhand/InventoryAdapter.java').read_text()
checks={
    'separate location detail choice':'Location Detail Report — Scan Order' in main,
    'required report columns':'User\\tLocation\\tQuantity\\tBarcode\\tDescription\\tPrice' in main,
    'original scan order':'db.itemsInScanOrder(sessionId)' in main,
    'saved user on each row':'String user=reportField(savedUserName())' in main,
    'existing location totals retained':'buildLocationQuantityReport' in main,
    'older-device yellow row minimum':'root.setMinimumHeight(dp(active?58:(compact?48:58)))' in adapter,
    'subtraction retained':'if(q<0&&current+q<0)' in main,
    'responsive partial search retained':'finishPartialBarcodeSearch' in main,
}
missing=[k for k,v in checks.items() if not v]
if missing: raise SystemExit('3.0.107 verification failed: '+', '.join(missing))
print('Prepared iCE Onhand 3.0.107: location detail scan-order report + consistent highlighted-row size')
