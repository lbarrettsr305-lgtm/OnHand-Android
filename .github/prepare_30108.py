from pathlib import Path

# Preserve the complete validated 3.0.107 report and older-device layout update.
base=Path('.github/prepare_30107.py')
exec(compile(base.read_text(),str(base),'exec'),{'__name__':'__main__','__file__':str(base)})

p=Path('app/src/main/java/com/iceinventory/onhand/MainActivity.java')
s=p.read_text()

old='''        String[] choices={"Export New Counts Only (Batch "+batch+")","Export Complete Inventory — TXT","Export Complete Inventory — Excel (.xlsx)","Re-export Previous Batch","Combine & Verify User Batches — Master User","Internet Items With Pictures","Location Quantity Report","Location Detail Report — Scan Order"};'''
new='''        String[] choices={"Export New Counts Only (Batch "+batch+")","Export Complete Inventory — TXT","Export Complete Inventory — Excel (.xlsx)","Re-export Previous Batch","Combine & Verify User Batches — Master User","Internet Items With Pictures","Location Quantity Report","Location Detail Report — TXT (Scan Order)","Location Detail Report — Excel (.xlsx)"};'''
if old not in s: raise SystemExit('3.0.108 target missing: export choices')
s=s.replace(old,new,1)

old='''            pendingExportLocationQuantityReport=false;pendingExportLocationDetailReport=true;startExportFormatFlow();'''
new='''            pendingExportLocationQuantityReport=false;pendingExportLocationDetailReport=true;pendingExportExcel=(which==8);startExportFormatFlow();'''
if old not in s: raise SystemExit('3.0.108 target missing: detail report routing')
s=s.replace(old,new,1)

old='''    private String locationDetailExportFileName(String name) {
        String n=cleanTextName(name);
        if(n.toLowerCase(Locale.US).endsWith(".txt"))n=n.substring(0,n.length()-4);
        if(!n.toLowerCase(Locale.US).endsWith(" - location detail"))n+=" - Location Detail";
        return n+".txt";
    }
'''
new='''    private String locationDetailExportFileName(String name) {
        String n=name==null?"":name.trim();
        String lower=n.toLowerCase(Locale.US);
        if(lower.endsWith(".xlsx"))n=n.substring(0,n.length()-5);
        else if(lower.endsWith(".txt"))n=n.substring(0,n.length()-4);
        if(!n.toLowerCase(Locale.US).endsWith(" - location detail"))n+=" - Location Detail";
        return pendingExportExcel?cleanExcelName(n+".xlsx"):cleanTextName(n+".txt");
    }
'''
if old not in s: raise SystemExit('3.0.108 target missing: location detail filename')
s=s.replace(old,new,1)

old='''            if(pendingExportLocationDetailReport) {
                os.write(buildLocationDetailReport().getBytes(StandardCharsets.UTF_8));
                toast("Location detail report exported in scan order");
            } else if(pendingExportLocationQuantityReport) {'''
new='''            if(pendingExportLocationDetailReport) {
                if(pendingExportExcel)SimpleXlsxWriter.writeLocationDetail(os,db.itemsInScanOrder(sessionId),savedUserName());
                else os.write(buildLocationDetailReport().getBytes(StandardCharsets.UTF_8));
                toast(pendingExportExcel?"Location detail Excel report exported in scan order":"Location detail TXT report exported in scan order");
            } else if(pendingExportLocationQuantityReport) {'''
if old not in s: raise SystemExit('3.0.108 target missing: report writer routing')
s=s.replace(old,new,1)

s=s.replace(
    'String exportTitle=pendingExportLocationDetailReport?"Location Detail Report":',
    'String exportTitle=pendingExportLocationDetailReport?(pendingExportExcel?"Location Detail Excel Report":"Location Detail TXT Report"):',
    1)
s=s.replace(
    'String exportMessage=pendingExportLocationDetailReport?"User, Location, Quantity, Barcode, Description and Price • original scan order.":',
    'String exportMessage=pendingExportLocationDetailReport?(pendingExportExcel?"Excel workbook • User, Location, Quantity, Barcode, Description and Price • original scan order.":"Tab-delimited TXT • User, Location, Quantity, Barcode, Description and Price • original scan order."):',
    1)

s=s.replace('Onhand Inventory 3.0.107','Onhand Inventory 3.0.108',1)
if 'Onhand Inventory 3.0.108' not in s: raise SystemExit('3.0.108 visible version target missing')
p.write_text(s)

p=Path('app/src/main/java/com/iceinventory/onhand/SimpleXlsxWriter.java')
x=p.read_text()
marker='''    /** Batch exports must retain zero and negative adjustments for reconciliation. */'''
addition='''    /** Location detail report with fixed columns in original scan order. */
    public static void writeLocationDetail(OutputStream output,List<InventoryDb.Row> rows,String user) throws IOException {
        ZipOutputStream zip=new ZipOutputStream(output);
        put(zip,"[Content_Types].xml",contentTypes());
        put(zip,"_rels/.rels",rootRels());
        put(zip,"xl/workbook.xml",workbook("Location Detail"));
        put(zip,"xl/_rels/workbook.xml.rels",workbookRels());
        put(zip,"xl/styles.xml",styles());
        put(zip,"xl/worksheets/sheet1.xml",locationDetailWorksheet(rows,user));
        zip.finish();
        zip.flush();
    }

'''+marker
if marker not in x: raise SystemExit('3.0.108 target missing: xlsx public writer marker')
x=x.replace(marker,addition,1)

marker='''    private static String worksheet(List<InventoryDb.Row> rows,SharedPreferences prefs,boolean preserveAdjustments){'''
addition='''    private static String locationDetailWorksheet(List<InventoryDb.Row> rows,String user){
        StringBuilder x=new StringBuilder(8192);
        x.append("<?xml version=\\"1.0\\" encoding=\\"UTF-8\\" standalone=\\"yes\\"?>");
        x.append("<worksheet xmlns=\\"http://schemas.openxmlformats.org/spreadsheetml/2006/main\\">");
        x.append("<sheetViews><sheetView workbookViewId=\\"0\\"><pane ySplit=\\"1\\" topLeftCell=\\"A2\\" activePane=\\"bottomLeft\\" state=\\"frozen\\"/></sheetView></sheetViews>");
        x.append("<cols><col min=\\"1\\" max=\\"1\\" width=\\"18\\" customWidth=\\"1\\"/><col min=\\"2\\" max=\\"2\\" width=\\"20\\" customWidth=\\"1\\"/><col min=\\"3\\" max=\\"3\\" width=\\"12\\" customWidth=\\"1\\"/><col min=\\"4\\" max=\\"4\\" width=\\"20\\" customWidth=\\"1\\"/><col min=\\"5\\" max=\\"5\\" width=\\"46\\" customWidth=\\"1\\"/><col min=\\"6\\" max=\\"6\\" width=\\"14\\" customWidth=\\"1\\"/></cols><sheetData>");
        String[] headers={"User","Location","Quantity","Barcode","Description","Price"};
        x.append("<row r=\\"1\\">"); for(int i=0;i<headers.length;i++)textCell(x,cellRef(i,1),headers[i],1); x.append("</row>");
        int n=1;
        for(InventoryDb.Row r:rows){
            n++; x.append("<row r=\\"").append(n).append("\\">");
            textCell(x,"A"+n,clean(user),0);
            textCell(x,"B"+n,clean(r.location==null||r.location.trim().isEmpty()?"Main":r.location),0);
            numberCell(x,"C"+n,r.quantity);
            textCell(x,"D"+n,clean(r.barcode),0);
            textCell(x,"E"+n,clean(r.description),0);
            textCell(x,"F"+n,clean(r.price),0);
            x.append("</row>");
        }
        x.append("</sheetData><autoFilter ref=\\"A1:F").append(Math.max(1,n)).append("\\"/></worksheet>");
        return x.toString();
    }

'''+marker
if marker not in x: raise SystemExit('3.0.108 target missing: worksheet marker')
x=x.replace(marker,addition,1)

old='''    private static String workbook(){
        return "<?xml version=\\"1.0\\" encoding=\\"UTF-8\\"?>"+
                "<workbook xmlns=\\"http://schemas.openxmlformats.org/spreadsheetml/2006/main\\" xmlns:r=\\"http://schemas.openxmlformats.org/officeDocument/2006/relationships\\">"+
                "<sheets><sheet name=\\"Inventory\\" sheetId=\\"1\\" r:id=\\"rId1\\"/></sheets></workbook>";
    }
'''
new='''    private static String workbook(){return workbook("Inventory");}
    private static String workbook(String sheetName){
        return "<?xml version=\\"1.0\\" encoding=\\"UTF-8\\"?>"+
                "<workbook xmlns=\\"http://schemas.openxmlformats.org/spreadsheetml/2006/main\\" xmlns:r=\\"http://schemas.openxmlformats.org/officeDocument/2006/relationships\\">"+
                "<sheets><sheet name=\\""+xml(sheetName)+"\\" sheetId=\\"1\\" r:id=\\"rId1\\"/></sheets></workbook>";
    }
'''
if old not in x: raise SystemExit('3.0.108 target missing: workbook name')
x=x.replace(old,new,1)
p.write_text(x)

p=Path('app/build.gradle')
g=p.read_text().replace('versionCode 30107','versionCode 30108',1).replace("versionName '3.0.107'","versionName '3.0.108'",1)
if 'versionCode 30108' not in g or "versionName '3.0.108'" not in g: raise SystemExit('3.0.108 Gradle version target missing')
p.write_text(g)

p=Path('app/src/main/AndroidManifest.xml')
m=p.read_text().replace('iCE Onhand 3.0.107','iCE Onhand 3.0.108',1)
if 'iCE Onhand 3.0.108' not in m: raise SystemExit('3.0.108 manifest version target missing')
p.write_text(m)

main=Path('app/src/main/java/com/iceinventory/onhand/MainActivity.java').read_text()
xlsx=Path('app/src/main/java/com/iceinventory/onhand/SimpleXlsxWriter.java').read_text()
checks={
    'TXT and Excel choices':all(v in main for v in ['Location Detail Report — TXT (Scan Order)','Location Detail Report — Excel (.xlsx)']),
    'Excel MIME and filename':'pendingExportExcel?cleanExcelName' in main and 'locationDetailExportFileName' in main,
    'scan-order data':'writeLocationDetail(os,db.itemsInScanOrder(sessionId),savedUserName())' in main,
    'fixed Excel columns':all(v in xlsx for v in ['"User"','"Location"','"Quantity"','"Barcode"','"Description"','"Price"']),
    'frozen header and filter':'ySplit=\\"1\\"' in xlsx and 'A1:F' in xlsx,
    'previous TXT report retained':'buildLocationDetailReport()' in main,
    'older device sizing retained':'root.setMinimumHeight(dp(active?58:(compact?48:58)))' in Path('app/src/main/java/com/iceinventory/onhand/InventoryAdapter.java').read_text(),
}
missing=[k for k,v in checks.items() if not v]
if missing: raise SystemExit('3.0.108 verification failed: '+', '.join(missing))
print('Prepared iCE Onhand 3.0.108: Location Detail TXT and Excel exports in original scan order')
