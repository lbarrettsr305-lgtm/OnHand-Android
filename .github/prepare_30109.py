from pathlib import Path

# Preserve the validated 3.0.108 Location Detail TXT and Excel exports.
base=Path('.github/prepare_30108.py')
exec(compile(base.read_text(),str(base),'exec'),{'__name__':'__main__','__file__':str(base)})

p=Path('app/src/main/java/com/iceinventory/onhand/MainActivity.java')
s=p.read_text()

s=s.replace(
    'private boolean pendingExportLocationDetailReport=false;',
    'private boolean pendingExportLocationDetailReport=false;\n    private int pendingAuditSort=0;',
    1)

old='''        String[] choices={"Export New Counts Only (Batch "+batch+")","Export Complete Inventory — TXT","Export Complete Inventory — Excel (.xlsx)","Re-export Previous Batch","Combine & Verify User Batches — Master User","Internet Items With Pictures","Location Quantity Report","Location Detail Report — TXT (Scan Order)","Location Detail Report — Excel (.xlsx)"};'''
new='''        String[] choices={"Export New Counts Only (Batch "+batch+")","Export Complete Inventory — TXT","Export Complete Inventory — Excel (.xlsx)","Re-export Previous Batch","Combine & Verify User Batches — Master User","Internet Items With Pictures","Location Quantity Report","Location Detail Report — TXT (Scan Order)","Location Detail Report — Excel (.xlsx)","Audit — Highest Unit Price (Excel)","Audit — Highest Extended Value (Excel)","Audit — Highest Quantity (Excel)"};'''
if old not in s: raise SystemExit('3.0.109 target missing: export choices')
s=s.replace(old,new,1)

old='''        new AlertDialog.Builder(this).setTitle("Export Items").setItems(choices,(d,which)->{
            if(which==0){'''
new='''        new AlertDialog.Builder(this).setTitle("Export Items").setItems(choices,(d,which)->{
            pendingAuditSort=0;
            if(which==0){'''
if old not in s: raise SystemExit('3.0.109 target missing: export handler start')
s=s.replace(old,new,1)

old='''            pendingExportExcel=false;pendingExportInternetOnly=false;
            if(which==6){pendingExportLocationQuantityReport=true;pendingExportLocationDetailReport=false;startExportFormatFlow();return;}
            pendingExportLocationQuantityReport=false;pendingExportLocationDetailReport=true;pendingExportExcel=(which==8);startExportFormatFlow();'''
new='''            pendingExportExcel=false;pendingExportInternetOnly=false;
            if(which==6){pendingExportLocationQuantityReport=true;pendingExportLocationDetailReport=false;startExportFormatFlow();return;}
            if(which==7||which==8){pendingExportLocationQuantityReport=false;pendingExportLocationDetailReport=true;pendingExportExcel=(which==8);startExportFormatFlow();return;}
            pendingExportLocationQuantityReport=false;pendingExportLocationDetailReport=false;pendingExportExcel=true;
            pendingAuditSort=which==9?1:(which==10?2:3);startExportFormatFlow();'''
if old not in s: raise SystemExit('3.0.109 target missing: report routing')
s=s.replace(old,new,1)

marker='''    private String locationDetailExportFileName(String name) {'''
addition='''    private String auditExportFileName(String name) {
        String n=name==null?"":name.trim();
        String lower=n.toLowerCase(Locale.US);
        if(lower.endsWith(".xlsx"))n=n.substring(0,n.length()-5);
        else if(lower.endsWith(".txt"))n=n.substring(0,n.length()-4);
        String suffix=pendingAuditSort==1?" - Audit Highest Unit Price":(pendingAuditSort==2?" - Audit Highest Extended Value":" - Audit Highest Quantity");
        return cleanExcelName(n+suffix+".xlsx");
    }

'''+marker
if marker not in s: raise SystemExit('3.0.109 target missing: filename marker')
s=s.replace(marker,addition,1)

s=s.replace(
    'if(pendingExportLocationDetailReport)exportName=locationDetailExportFileName(exportName);',
    'if(pendingExportLocationDetailReport)exportName=locationDetailExportFileName(exportName);\n            if(pendingAuditSort>0)exportName=auditExportFileName(exportName);',
    1)
s=s.replace(
    'String exportTitle=pendingExportLocationDetailReport?(pendingExportExcel?"Location Detail Excel Report":"Location Detail TXT Report"):',
    'String exportTitle=pendingAuditSort>0?"Audit Verification Excel Report":(pendingExportLocationDetailReport?(pendingExportExcel?"Location Detail Excel Report":"Location Detail TXT Report"):',
    1)
s=s.replace(
    '(pendingExportLocationQuantityReport?"Location Quantity Report":(pendingExportInternetOnly?"Export Internet Items With Pictures":(pendingExportExcel?"Export Excel":"Export TXT")));',
    '(pendingExportLocationQuantityReport?"Location Quantity Report":(pendingExportInternetOnly?"Export Internet Items With Pictures":(pendingExportExcel?"Export Excel":"Export TXT"))));',
    1)
s=s.replace(
    'String exportMessage=pendingExportLocationDetailReport?(pendingExportExcel?"Excel workbook • User, Location, Quantity, Barcode, Description and Price • original scan order.":"Tab-delimited TXT • User, Location, Quantity, Barcode, Description and Price • original scan order."):',
    'String exportMessage=pendingAuditSort>0?"Excel audit workbook • sorted highest to lowest • Quantity, Barcode, Description, Price and Extended Value.":(pendingExportLocationDetailReport?(pendingExportExcel?"Excel workbook • User, Location, Quantity, Barcode, Description and Price • original scan order.":"Tab-delimited TXT • User, Location, Quantity, Barcode, Description and Price • original scan order."):',
    1)
s=s.replace(
    '(pendingExportLocationQuantityReport?"Separate TXT report • total quantity for each location plus a grand total.":(pendingExportInternetOnly?"Separate HTML report • internet-added items with associated product pictures.":(pendingExportExcel?"Excel workbook • same inventory columns and headers as TXT.":"All inventory items • tab-delimited TXT file.")));',
    '(pendingExportLocationQuantityReport?"Separate TXT report • total quantity for each location plus a grand total.":(pendingExportInternetOnly?"Separate HTML report • internet-added items with associated product pictures.":(pendingExportExcel?"Excel workbook • same inventory columns and headers as TXT.":"All inventory items • tab-delimited TXT file."))));',
    1)

old='''            if(pendingExportLocationDetailReport) {
                if(pendingExportExcel)SimpleXlsxWriter.writeLocationDetail(os,db.itemsInScanOrder(sessionId),savedUserName());'''
new='''            if(pendingAuditSort>0) {
                SimpleXlsxWriter.writeAudit(os,db.items(sessionId),pendingAuditSort);
                toast("Audit verification Excel report exported");
            } else if(pendingExportLocationDetailReport) {
                if(pendingExportExcel)SimpleXlsxWriter.writeLocationDetail(os,db.itemsInScanOrder(sessionId),savedUserName());'''
if old not in s: raise SystemExit('3.0.109 target missing: writer routing')
s=s.replace(old,new,1)

s=s.replace('Onhand Inventory 3.0.108','Onhand Inventory 3.0.109',1)
if 'Onhand Inventory 3.0.109' not in s: raise SystemExit('3.0.109 visible version target missing')
p.write_text(s)

p=Path('app/src/main/java/com/iceinventory/onhand/SimpleXlsxWriter.java')
x=p.read_text()
x=x.replace('import java.util.Date;','import java.util.ArrayList;\nimport java.util.Collections;\nimport java.util.Comparator;\nimport java.util.Date;',1)

marker='''    /** Batch exports must retain zero and negative adjustments for reconciliation. */'''
addition='''    /** Audit verification workbook sorted highest-to-lowest by unit price, extended value, or quantity. */
    public static void writeAudit(OutputStream output,List<InventoryDb.Row> rows,final int sortMode) throws IOException {
        List<InventoryDb.Row> sorted=new ArrayList<>(rows);
        Collections.sort(sorted,new Comparator<InventoryDb.Row>(){
            @Override public int compare(InventoryDb.Row a,InventoryDb.Row b){
                double av=sortMode==1?auditPrice(a.price):(sortMode==2?a.quantity*auditPrice(a.price):a.quantity);
                double bv=sortMode==1?auditPrice(b.price):(sortMode==2?b.quantity*auditPrice(b.price):b.quantity);
                int primary=Double.compare(bv,av);
                if(primary!=0)return primary;
                return clean(a.barcode).compareTo(clean(b.barcode));
            }
        });
        ZipOutputStream zip=new ZipOutputStream(output);
        put(zip,"[Content_Types].xml",contentTypes());
        put(zip,"_rels/.rels",rootRels());
        String title=sortMode==1?"Highest Unit Price":(sortMode==2?"Highest Extended Value":"Highest Quantity");
        put(zip,"xl/workbook.xml",workbook(title));
        put(zip,"xl/_rels/workbook.xml.rels",workbookRels());
        put(zip,"xl/styles.xml",styles());
        put(zip,"xl/worksheets/sheet1.xml",auditWorksheet(sorted));
        zip.finish();
        zip.flush();
    }

    private static double auditPrice(String value){
        if(value==null)return 0d;
        String v=value.trim().replace("$","").replace(",","");
        if(v.startsWith("(")&&v.endsWith(")"))v="-"+v.substring(1,v.length()-1);
        try{return Double.parseDouble(v);}catch(Exception ignored){return 0d;}
    }

    private static String auditWorksheet(List<InventoryDb.Row> rows){
        StringBuilder x=new StringBuilder(8192);
        x.append("<?xml version=\\"1.0\\" encoding=\\"UTF-8\\" standalone=\\"yes\\"?>");
        x.append("<worksheet xmlns=\\"http://schemas.openxmlformats.org/spreadsheetml/2006/main\\">");
        x.append("<sheetViews><sheetView workbookViewId=\\"0\\"><pane ySplit=\\"1\\" topLeftCell=\\"A2\\" activePane=\\"bottomLeft\\" state=\\"frozen\\"/></sheetView></sheetViews>");
        x.append("<cols><col min=\\"1\\" max=\\"1\\" width=\\"12\\" customWidth=\\"1\\"/><col min=\\"2\\" max=\\"2\\" width=\\"20\\" customWidth=\\"1\\"/><col min=\\"3\\" max=\\"3\\" width=\\"46\\" customWidth=\\"1\\"/><col min=\\"4\\" max=\\"5\\" width=\\"16\\" customWidth=\\"1\\"/></cols><sheetData>");
        String[] headers={"Quantity","Barcode","Description","Price","Extended Value"};
        x.append("<row r=\\"1\\">");for(int i=0;i<headers.length;i++)textCell(x,cellRef(i,1),headers[i],1);x.append("</row>");
        int n=1;
        for(InventoryDb.Row r:rows){
            n++;x.append("<row r=\\"").append(n).append("\\">");
            numberCell(x,"A"+n,r.quantity);
            textCell(x,"B"+n,clean(r.barcode),0);
            textCell(x,"C"+n,clean(r.description),0);
            numberCell(x,"D"+n,auditPrice(r.price));
            numberCell(x,"E"+n,r.quantity*auditPrice(r.price));
            x.append("</row>");
        }
        x.append("</sheetData><autoFilter ref=\\"A1:E").append(Math.max(1,n)).append("\\"/></worksheet>");
        return x.toString();
    }

'''+marker
if marker not in x: raise SystemExit('3.0.109 target missing: audit writer marker')
x=x.replace(marker,addition,1)
p.write_text(x)

p=Path('app/build.gradle')
g=p.read_text().replace('versionCode 30108','versionCode 30109',1).replace("versionName '3.0.108'","versionName '3.0.109'",1)
if 'versionCode 30109' not in g or "versionName '3.0.109'" not in g: raise SystemExit('3.0.109 Gradle version target missing')
p.write_text(g)

p=Path('app/src/main/AndroidManifest.xml')
m=p.read_text().replace('iCE Onhand 3.0.108','iCE Onhand 3.0.109',1)
if 'iCE Onhand 3.0.109' not in m: raise SystemExit('3.0.109 manifest version target missing')
p.write_text(m)

main=Path('app/src/main/java/com/iceinventory/onhand/MainActivity.java').read_text()
xlsx=Path('app/src/main/java/com/iceinventory/onhand/SimpleXlsxWriter.java').read_text()
checks={
    'three audit choices':all(v in main for v in ['Audit — Highest Unit Price (Excel)','Audit — Highest Extended Value (Excel)','Audit — Highest Quantity (Excel)']),
    'descending comparison':'Double.compare(bv,av)' in xlsx,
    'extended calculation':'r.quantity*auditPrice(r.price)' in xlsx,
    'audit columns':all(v in xlsx for v in ['"Quantity"','"Barcode"','"Description"','"Price"','"Extended Value"']),
    'existing location exports retained':all(v in main for v in ['Location Detail Report — TXT (Scan Order)','Location Detail Report — Excel (.xlsx)']),
}
missing=[k for k,v in checks.items() if not v]
if missing: raise SystemExit('3.0.109 verification failed: '+', '.join(missing))
print('Prepared iCE Onhand 3.0.109: three highest-to-lowest Excel audit reports')
