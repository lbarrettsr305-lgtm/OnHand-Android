#!/usr/bin/env python3
from pathlib import Path
import runpy

root = Path(__file__).resolve().parents[1]
workflow = root / ".github/workflows/build-apk.yml"

# Let the previous release validate against its own workflow markers first.
w = workflow.read_text()
w = w.replace("Prepare and verify 3.0.207 Victoria four-column customer report", "Prepare and verify 3.0.206 Victoria reconciliation and import/export templates")
w = w.replace(".github/prepare_30207.py", ".github/prepare_30206.py")
w = w.replace("iCE-Onhand-Inventory-3.0.207", "iCE-Onhand-Inventory-3.0.206")
workflow.write_text(w)
runpy.run_path(str(root / ".github" / "prepare_30206.py"), run_name="__main__")

# Restore this release's workflow markers after 3.0.206 has completed.
w = workflow.read_text()
w = w.replace("Prepare and verify 3.0.206 Victoria reconciliation and import/export templates", "Prepare and verify 3.0.207 Victoria four-column customer report")
w = w.replace("Prepare and verify 3.0.205 Victoria import/export templates", "Prepare and verify 3.0.207 Victoria four-column customer report")
w = w.replace(".github/prepare_30206.py", ".github/prepare_30207.py")
w = w.replace(".github/prepare_30205.py", ".github/prepare_30207.py")
w = w.replace("iCE-Onhand-Inventory-3.0.206", "iCE-Onhand-Inventory-3.0.207")
w = w.replace("iCE-Onhand-Inventory-3.0.205", "iCE-Onhand-Inventory-3.0.207")
workflow.write_text(w)

gradle = root / "app/build.gradle"
s = gradle.read_text()
if "versionName '3.0.206'" not in s or "versionCode 30206" not in s:
    raise SystemExit("3.0.206 version source not found")
gradle.write_text(s.replace("versionCode 30206", "versionCode 30207", 1).replace("versionName '3.0.206'", "versionName '3.0.207'", 1))

manifest = root / "app/src/main/AndroidManifest.xml"
s = manifest.read_text()
if "iCE Onhand 3.0.206" not in s:
    raise SystemExit("3.0.206 app label missing")
manifest.write_text(s.replace("iCE Onhand 3.0.206", "iCE Onhand 3.0.207", 1))

main = root / "app/src/main/java/com/iceinventory/onhand/MainActivity.java"
s = main.read_text()
if "Onhand Inventory 3.0.206" not in s:
    raise SystemExit("3.0.206 screen version missing")
main.write_text(s.replace("Onhand Inventory 3.0.206", "Onhand Inventory 3.0.207", 1))

# Put the Victoria workflow at the top of Export Reports so it is easy to find.
main = root / "app/src/main/java/com/iceinventory/onhand/MainActivity.java"
s = main.read_text()
old_export = '        addExportButton(exportPanel,exportDialog,"Re-export Previous Batch",3);'
new_export = old_export + '\n\n        addExportSection(exportPanel,"VICTORIA INVENTORY WORKFLOW");\n        addExportButton(exportPanel,exportDialog,"Victoria Inventory Workflow",4);'
if s.count(old_export) != 1:
    raise SystemExit("Victoria export menu insertion point missing")
s = s.replace(old_export, new_export, 1)
old_old = '''        addExportSection(exportPanel,"COMBINE & OTHER REPORTS");
        addExportButton(exportPanel,exportDialog,"Combine & Verify User Batches",4);
        addExportButton(exportPanel,exportDialog,"Internet Items With Pictures",5);'''
new_old = '''        addExportSection(exportPanel,"OTHER REPORTS");
        addExportButton(exportPanel,exportDialog,"Internet Items With Pictures",5);'''
if s.count(old_old) != 1:
    raise SystemExit("Victoria duplicate export menu entry missing")
s = s.replace(old_old, new_old, 1)
if 'addExportButton(exportPanel,exportDialog,"Victoria Inventory Workflow",4);' not in s:
    raise SystemExit("Victoria workflow menu verification failed")
main.write_text(s)

# Counter files and the verification report keep Location. Only the final
# Victoria customer file removes it, because the client's required layout is
# QTY, BARCODE, DESCRIPTION, ITEM NUMBER.
batch = root / "app/src/main/java/com/iceinventory/onhand/BatchMergeActivity.java"
s = batch.read_text()
old_header = 'StringBuilder b=new StringBuilder("QTY\\tBARCODE\\tDESCRIPTION\\tITEM NUMBER\\tLOCATION\\r\\n");'
new_header = 'StringBuilder b=new StringBuilder("QTY\\tBARCODE\\tDESCRIPTION\\tITEM NUMBER\\r\\n");'
if old_header not in s:
    raise SystemExit("Victoria five-column customer header target missing")
s = s.replace(old_header, new_header, 1)
old_row = "b.append(QuantityMath.format(t.quantity)).append('\\t').append(clean(t.barcode)).append('\\t').append(clean(t.description)).append('\\t').append(clean(t.itemNumber)).append('\\t').append(clean(t.location)).append(\"\\r\\n\");"
new_row = "b.append(QuantityMath.format(t.quantity)).append('\\t').append(clean(t.barcode)).append('\\t').append(clean(t.description)).append('\\t').append(clean(t.itemNumber)).append(\"\\r\\n\");"
if old_row not in s:
    raise SystemExit("Victoria five-column customer row target missing")
s = s.replace(old_row, new_row, 1)

# Build the Victoria customer report from two authoritative sources:
# the original customer Excel supplies ITEM NUMBER and DESCRIPTION, while the
# returned counter files supply QTY and LOCATION for internal reconciliation.
s = s.replace(
    "private static final int REQ_FILES=4101,REQ_SAVE=4102,REQ_REPORT=4103,REQ_XLSX=4104,REQ_LOCATION_DETAIL=4105,REQ_LOCATION_TOTALS=4106;",
    "private static final int REQ_FILES=4101,REQ_SAVE=4102,REQ_REPORT=4103,REQ_XLSX=4104,REQ_LOCATION_DETAIL=4105,REQ_LOCATION_TOTALS=4106,REQ_VICTORIA_SOURCE=4107;",
    1)
s = s.replace(
    "    private static final class BatchStat {",
    '''    private static final class VictoriaProduct {
        String description="",itemNumber="";
    }

    private static final class BatchStat {''',
    1)
s = s.replace(
    "    private final LinkedHashMap<String,Total> combined=new LinkedHashMap<>();",
    '''    private final LinkedHashMap<String,Total> combined=new LinkedHashMap<>();
    private final LinkedHashMap<String,VictoriaProduct> victoriaProducts=new LinkedHashMap<>();
    private boolean victoriaSourceLoaded;
    private String victoriaSourceName="";''',
    1)

old_ui = '''        TextView help=text("Select iCE OnHand batches or compatible external tab-delimited files. Recognizable Barcode and Quantity headers are accepted. Headerless external files are also accepted in Quantity | Barcode | Description | Price order. Filenames, extensions, store names and batch numbers are not required. All new combined outputs begin with COMBINED. Any file beginning with COMBINED is automatically identified as a non-source output and skipped to prevent double-counting. Older verification/report filenames are also protected.",15,Color.WHITE);help.setPadding(0,dp(8),0,dp(12));page.addView(help);
        Button choose=button("Select Batch / Source Files");choose.setOnClickListener(v->chooseFiles());page.addView(choose,new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT,dp(54)));'''
new_ui = '''        TextView help=text("VICTORIA WORKFLOW: First select the original Victoria Excel file. It supplies ITEM NUMBER and the official DESCRIPTION. Then select every returned counter file. Counter files supply QTY and LOCATION. Location remains in the verification reports but is excluded from the final four-column Victoria customer Excel.",15,Color.WHITE);help.setPadding(0,dp(8),0,dp(12));page.addView(help);
        Button victoriaSource=button("1. Select Original Victoria Excel");victoriaSource.setOnClickListener(v->chooseVictoriaSource());page.addView(victoriaSource,new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT,dp(58)));
        Button choose=button("2. Select All Counter Files");choose.setOnClickListener(v->chooseFiles());LinearLayout.LayoutParams chooseParams=new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT,dp(58));chooseParams.setMargins(0,dp(8),0,0);page.addView(choose,chooseParams);'''
if old_ui not in s:
    raise SystemExit("Victoria source UI anchor missing")
s = s.replace(old_ui, new_ui, 1)

s = s.replace(
    "    private void chooseFiles(){",
    '''    private void chooseVictoriaSource(){
        Intent i=new Intent(Intent.ACTION_OPEN_DOCUMENT);i.addCategory(Intent.CATEGORY_OPENABLE);i.setType("application/vnd.openxmlformats-officedocument.spreadsheetml.sheet");startActivityForResult(i,REQ_VICTORIA_SOURCE);
    }

    private void loadVictoriaSource(Uri uri){
        victoriaProducts.clear();victoriaSourceLoaded=false;victoriaSourceName=displayName(uri);
        try(InputStream is=getContentResolver().openInputStream(uri)){
            if(is==null)throw new Exception("Could not open the Victoria Excel file");
            java.util.List<java.util.Map<Integer,String>> rows=XlsxTableReader.readFirstSheet(is);
            if(rows.isEmpty())throw new Exception("The Victoria Excel file is empty");
            java.util.Map<Integer,String> headers=rows.get(0);
            int barcodeColumn=findExcel(headers,"upc","barcode","bar code","gtin");
            int itemColumn=findExcel(headers,"new item number","item number","item-number","itemnumber","sku");
            int descriptionColumn=findExcelExact(headers,"description");
            if(descriptionColumn<0)descriptionColumn=findExcel(headers,"description","des");
            if(barcodeColumn<0||itemColumn<0)throw new Exception("The original Victoria Excel must contain UPC/BARCODE and ITEM NUMBER columns");
            for(int row=1;row<rows.size();row++){
                java.util.Map<Integer,String> values=rows.get(row);
                String barcode=normalizeBarcode(cell(values,barcodeColumn));if(barcode.isEmpty())continue;
                String item=clean(cell(values,itemColumn));if(item.isEmpty())continue;
                VictoriaProduct product=victoriaProducts.get(barcode);
                if(product==null){product=new VictoriaProduct();victoriaProducts.put(barcode,product);}
                if(product.itemNumber.isEmpty())product.itemNumber=item;
                String description=descriptionColumn<0?"":clean(cell(values,descriptionColumn));
                if(product.description.isEmpty()&&!description.isEmpty())product.description=description;
            }
            if(victoriaProducts.isEmpty())throw new Exception("No usable UPC and item-number rows were found in the Victoria Excel file");
            victoriaSourceLoaded=true;
            status.setText("Original Victoria Excel loaded: "+victoriaSourceName+"\\nProducts available for matching: "+victoriaProducts.size()+"\\n\\nNext: tap 2. Select All Counter Files.");
            status.setTextColor(Color.rgb(120,255,140));
        }catch(Exception e){status.setText("Victoria Excel import failed: "+e.getMessage());status.setTextColor(Color.rgb(255,130,130));}
    }

    private int findExcel(java.util.Map<Integer,String> headers,String... names){for(java.util.Map.Entry<Integer,String> entry:headers.entrySet()){String h=clean(entry.getValue()).toLowerCase(Locale.US).replace('_',' ').replace('-',' ');for(String name:names){String n=name.toLowerCase(Locale.US).replace('-',' ');if(h.equals(n)||h.contains(n))return entry.getKey();}}return -1;}
    private int findExcelExact(java.util.Map<Integer,String> headers,String name){for(java.util.Map.Entry<Integer,String> entry:headers.entrySet())if(clean(entry.getValue()).equalsIgnoreCase(name))return entry.getKey();return -1;}
    private String cell(java.util.Map<Integer,String> row,int column){String value=row.get(column);return value==null?"":value;}
    private String normalizeBarcode(String value){String s=clean(value).replace(" ","");if(s.matches("[0-9]+\\\\.0"))s=s.substring(0,s.length()-2);return s;}

    private void chooseFiles(){''',
    1)

s = s.replace(
    '''        if(request==REQ_FILES)loadFiles(data);else if(request==REQ_SAVE)writeCombined(data.getData());''',
    '''        if(request==REQ_VICTORIA_SOURCE)loadVictoriaSource(data.getData());else if(request==REQ_FILES)loadFiles(data);else if(request==REQ_SAVE)writeCombined(data.getData());''',
    1)
s = s.replace(
    "    private void loadFiles(Intent data){\n        combined.clear();",
    '''    private void loadFiles(Intent data){
        if(!victoriaSourceLoaded){status.setText("STEP 1 REQUIRED: Select the original Victoria Excel file before selecting counter files.");status.setTextColor(Color.rgb(255,130,130));return;}
        combined.clear();''',
    1)

old_verify = '''        String masterName=savedMasterUserName();
        boolean masterIncluded=false;
        if(!masterName.isEmpty())for(BatchStat stat:sourceStats)if(stat.userName.equalsIgnoreCase(masterName)){masterIncluded=true;break;}
        verified=errors.isEmpty()&&sourceFiles==candidateFiles&&candidateFiles>0&&masterIncluded&&QuantityMath.equal(sourceGrandTotal,outputTotal)&&QuantityMath.equal(sourceGrandTotal,locationGrandTotal);
        StringBuilder s=new StringBuilder();s.append("Master batch included: ").append(masterIncluded?"YES":"NO - select the Master batch").append("\\n");'''
new_verify = '''        int unmatched=0;java.util.ArrayList<String> unmatchedBarcodes=new java.util.ArrayList<>();
        for(Total total:combined.values()){
            VictoriaProduct product=victoriaProducts.get(normalizeBarcode(total.barcode));
            if(product==null||product.itemNumber.isEmpty()){unmatched++;if(unmatchedBarcodes.size()<20)unmatchedBarcodes.add(total.barcode);continue;}
            total.itemNumber=product.itemNumber;
            if(!product.description.isEmpty())total.description=product.description;
        }
        if(unmatched>0)errors.add(unmatched+" counted barcode(s) were not found with an item number in the original Victoria Excel: "+android.text.TextUtils.join(", ",unmatchedBarcodes)+(unmatched>unmatchedBarcodes.size()?" ...":""));
        String masterName=savedMasterUserName();
        boolean masterIncluded=false;
        if(!masterName.isEmpty())for(BatchStat stat:sourceStats)if(stat.userName.equalsIgnoreCase(masterName)){masterIncluded=true;break;}
        verified=errors.isEmpty()&&victoriaSourceLoaded&&sourceFiles==candidateFiles&&candidateFiles>0&&QuantityMath.equal(sourceGrandTotal,outputTotal)&&QuantityMath.equal(sourceGrandTotal,locationGrandTotal);
        StringBuilder s=new StringBuilder();s.append("Original Victoria Excel: ").append(victoriaSourceName).append(" — ").append(victoriaProducts.size()).append(" products\\n");s.append("Master batch selected: ").append(masterIncluded?"YES":"NO — allowed when the Master did not count").append("\\n");'''
if old_verify not in s:
    raise SystemExit("Victoria verification gate anchor missing")
s = s.replace(old_verify, new_verify, 1)

s = s.replace(
    '''    private void saveCombined(){if(!verified)return;Intent i=new Intent(Intent.ACTION_CREATE_DOCUMENT);i.addCategory(Intent.CATEGORY_OPENABLE);i.setType("text/plain");i.putExtra(Intent.EXTRA_TITLE,combinedOutputName("VERIFIED BATCH",sourceInventoryName()+".txt"));startActivityForResult(i,REQ_SAVE);}''',
    '''    private void saveCombined(){if(!verified)return;Intent i=new Intent(Intent.ACTION_CREATE_DOCUMENT);i.addCategory(Intent.CATEGORY_OPENABLE);i.setType("application/vnd.openxmlformats-officedocument.spreadsheetml.sheet");i.putExtra(Intent.EXTRA_TITLE,combinedOutputName("VICTORIA CUSTOMER REPORT",sourceInventoryName()+".xlsx"));startActivityForResult(i,REQ_SAVE);}''',
    1)
s = s.replace('save=button("Export Combined Batch — TXT")', 'save=button("Export Victoria Customer Report — Excel")', 1)

old_write = '''            StringBuilder b=new StringBuilder("QTY\\tBARCODE\\tDESCRIPTION\\tITEM NUMBER\\r\\n");
            for(Map.Entry<String,Total> e:combined.entrySet()){
                Total t=e.getValue();
                b.append(QuantityMath.format(t.quantity)).append('\\t').append(clean(t.barcode)).append('\\t').append(clean(t.description)).append('\\t').append(clean(t.itemNumber)).append("\\r\\n");
            }
            os.write(b.toString().getBytes(StandardCharsets.UTF_8));'''
new_write = '''            LinkedHashMap<String,VictoriaCustomerXlsxWriter.Row> customer=new LinkedHashMap<>();
            for(Total t:combined.values()){
                String key=normalizeBarcode(t.barcode);VictoriaCustomerXlsxWriter.Row row=customer.get(key);
                if(row==null){row=new VictoriaCustomerXlsxWriter.Row();row.barcode=t.barcode;row.description=t.description;row.itemNumber=t.itemNumber;customer.put(key,row);}
                row.quantity+=t.quantity;
            }
            VictoriaCustomerXlsxWriter.write(os,new java.util.ArrayList<>(customer.values()));'''
if old_write not in s:
    raise SystemExit("Victoria final report writer anchor missing")
s = s.replace(old_write, new_write, 1)
batch.write_text(s)

writer = root / "app/src/main/java/com/iceinventory/onhand/VictoriaCustomerXlsxWriter.java"
writer.write_text(r'''package com.iceinventory.onhand;

import java.io.IOException;
import java.io.OutputStream;
import java.nio.charset.StandardCharsets;
import java.util.List;
import java.util.zip.ZipEntry;
import java.util.zip.ZipOutputStream;

/** Writes Victoria's exact four-column customer inventory workbook. */
public final class VictoriaCustomerXlsxWriter {
    private VictoriaCustomerXlsxWriter(){}
    public static final class Row { public double quantity; public String barcode="",description="",itemNumber=""; }
    public static void write(OutputStream output,List<Row> rows)throws IOException{
        StringBuilder data=new StringBuilder();int r=1;
        data.append("<row r=\"1\">");text(data,"A1","QTY",1);text(data,"B1","BARCODE",1);text(data,"C1","DESCRIPTION",1);text(data,"D1","ITEM NUMBER",1);data.append("</row>");r++;
        for(Row row:rows){data.append("<row r=\"").append(r).append("\">");number(data,"A"+r,row.quantity);text(data,"B"+r,row.barcode,0);text(data,"C"+r,row.description,0);text(data,"D"+r,row.itemNumber,0);data.append("</row>");r++;}
        ZipOutputStream z=new ZipOutputStream(output);put(z,"[Content_Types].xml",types());put(z,"_rels/.rels",rels());put(z,"xl/workbook.xml",book());put(z,"xl/_rels/workbook.xml.rels",bookrels());put(z,"xl/styles.xml",styles());
        put(z,"xl/worksheets/sheet1.xml","<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"yes\"?><worksheet xmlns=\"http://schemas.openxmlformats.org/spreadsheetml/2006/main\"><sheetViews><sheetView workbookViewId=\"0\"><pane ySplit=\"1\" topLeftCell=\"A2\" activePane=\"bottomLeft\" state=\"frozen\"/></sheetView></sheetViews><cols><col min=\"1\" max=\"1\" width=\"12\" customWidth=\"1\"/><col min=\"2\" max=\"2\" width=\"22\" customWidth=\"1\"/><col min=\"3\" max=\"3\" width=\"55\" customWidth=\"1\"/><col min=\"4\" max=\"4\" width=\"20\" customWidth=\"1\"/></cols><sheetData>"+data+"</sheetData><autoFilter ref=\"A1:D"+Math.max(1,r-1)+"\"/></worksheet>");z.finish();z.flush();
    }
    private static void text(StringBuilder b,String ref,String value,int style){b.append("<c r=\"").append(ref).append("\" t=\"inlineStr\"");if(style>0)b.append(" s=\"").append(style).append("\"");b.append("><is><t xml:space=\"preserve\">").append(xml(value)).append("</t></is></c>");}
    private static void number(StringBuilder b,String ref,double value){b.append("<c r=\"").append(ref).append("\"><v>").append(value).append("</v></c>");}
    private static String xml(String s){if(s==null)return "";return s.replace("&","&amp;").replace("<","&lt;").replace(">","&gt;").replace("\"","&quot;").replace("'","&apos;");}
    private static void put(ZipOutputStream z,String name,String value)throws IOException{z.putNextEntry(new ZipEntry(name));z.write(value.getBytes(StandardCharsets.UTF_8));z.closeEntry();}
    private static String types(){return "<?xml version=\"1.0\" encoding=\"UTF-8\"?><Types xmlns=\"http://schemas.openxmlformats.org/package/2006/content-types\"><Default Extension=\"rels\" ContentType=\"application/vnd.openxmlformats-package.relationships+xml\"/><Default Extension=\"xml\" ContentType=\"application/xml\"/><Override PartName=\"/xl/workbook.xml\" ContentType=\"application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml\"/><Override PartName=\"/xl/worksheets/sheet1.xml\" ContentType=\"application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml\"/><Override PartName=\"/xl/styles.xml\" ContentType=\"application/vnd.openxmlformats-officedocument.spreadsheetml.styles+xml\"/></Types>";}
    private static String rels(){return "<?xml version=\"1.0\" encoding=\"UTF-8\"?><Relationships xmlns=\"http://schemas.openxmlformats.org/package/2006/relationships\"><Relationship Id=\"rId1\" Type=\"http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument\" Target=\"xl/workbook.xml\"/></Relationships>";}
    private static String book(){return "<?xml version=\"1.0\" encoding=\"UTF-8\"?><workbook xmlns=\"http://schemas.openxmlformats.org/spreadsheetml/2006/main\" xmlns:r=\"http://schemas.openxmlformats.org/officeDocument/2006/relationships\"><sheets><sheet name=\"Victoria Inventory\" sheetId=\"1\" r:id=\"rId1\"/></sheets></workbook>";}
    private static String bookrels(){return "<?xml version=\"1.0\" encoding=\"UTF-8\"?><Relationships xmlns=\"http://schemas.openxmlformats.org/package/2006/relationships\"><Relationship Id=\"rId1\" Type=\"http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet\" Target=\"worksheets/sheet1.xml\"/><Relationship Id=\"rId2\" Type=\"http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles\" Target=\"styles.xml\"/></Relationships>";}
    private static String styles(){return "<?xml version=\"1.0\" encoding=\"UTF-8\"?><styleSheet xmlns=\"http://schemas.openxmlformats.org/spreadsheetml/2006/main\"><fonts count=\"2\"><font><sz val=\"11\"/><name val=\"Calibri\"/></font><font><b/><color rgb=\"FF000000\"/><sz val=\"11\"/><name val=\"Calibri\"/></font></fonts><fills count=\"3\"><fill><patternFill patternType=\"none\"/></fill><fill><patternFill patternType=\"gray125\"/></fill><fill><patternFill patternType=\"solid\"><fgColor rgb=\"FFFFD700\"/></patternFill></fill></fills><borders count=\"1\"><border><left/><right/><top/><bottom/><diagonal/></border></borders><cellStyleXfs count=\"1\"><xf numFmtId=\"0\" fontId=\"0\" fillId=\"0\" borderId=\"0\"/></cellStyleXfs><cellXfs count=\"2\"><xf numFmtId=\"0\" fontId=\"0\" fillId=\"0\" borderId=\"0\" xfId=\"0\"/><xf numFmtId=\"0\" fontId=\"1\" fillId=\"2\" borderId=\"0\" xfId=\"0\" applyFont=\"1\" applyFill=\"1\"/></cellXfs><cellStyles count=\"1\"><cellStyle name=\"Normal\" xfId=\"0\" builtinId=\"0\"/></cellStyles></styleSheet>";}
}
''')

checks = {
    "version": "versionName '3.0.207'" in gradle.read_text(),
    "four-column customer header": 'text(data,"A1","QTY",1)' in writer.read_text() and 'text(data,"D1","ITEM NUMBER",1)' in writer.read_text(),
    "customer Excel writer": "VictoriaCustomerXlsxWriter.write" in s and writer.exists(),
    "original Excel lookup required": "Select Original Victoria Excel" in s and "victoriaProducts.get" in s,
    "customer rows aggregate locations": "row.quantity+=t.quantity" in s,
    "master batch optional": "allowed when the Master did not count" in s,
    "counter import still requires location": "missing Location header" in s,
    "location audit reconciliation retained": "QuantityMath.equal(sourceGrandTotal,locationGrandTotal)" in s,
    "Petrosoft reports retained": "PETROSOFT MONTHLY REPORTS" in main.read_text(),
    "workflow points to this release": "prepare_30207.py" in workflow.read_text() and "3.0.207" in workflow.read_text(),
}
failed = [name for name, passed in checks.items() if not passed]
if failed:
    raise SystemExit("3.0.207 checks failed: " + ", ".join(failed))

print("Prepared iCE OnHand 3.0.207: Victoria customer report is QTY, BARCODE, DESCRIPTION, ITEM NUMBER; Petrosoft and internal location reports retained.")
