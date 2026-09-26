from pathlib import Path

base = Path('.github/prepare_30167.py')
exec(compile(base.read_text(), str(base), 'exec'), {'__name__': '__main__', '__file__': str(base)})


def rep(path, old, new, label):
    p = Path(path); s = p.read_text()
    if s.count(old) != 1: raise SystemExit('3.0.168 target ' + label + ' count ' + str(s.count(old)))
    p.write_text(s.replace(old, new, 1))


rep('app/build.gradle', 'versionCode 30167', 'versionCode 30168', 'code')
rep('app/build.gradle', "versionName '3.0.167'", "versionName '3.0.168'", 'name')
rep('app/src/main/AndroidManifest.xml', 'iCE Onhand 3.0.167', 'iCE Onhand 3.0.168', 'manifest')
rep('app/src/main/java/com/iceinventory/onhand/MainActivity.java', 'Onhand Inventory 3.0.167', 'Onhand Inventory 3.0.168', 'header')

Path('app/src/main/java/com/iceinventory/onhand/MonthlyCombinedInventoryXlsxWriter.java').write_text(r'''package com.iceinventory.onhand;
import java.io.*;import java.nio.charset.StandardCharsets;import java.util.*;import java.util.zip.*;
public final class MonthlyCombinedInventoryXlsxWriter{
 private MonthlyCombinedInventoryXlsxWriter(){}
 public static final class Row{public String upc="",gtin="",retail="",description="";public double quantity;}
 public static void write(OutputStream out,String customer,String date,List<Row> data)throws IOException{
  StringBuilder x=new StringBuilder();int r=1;
  row(x,r++,new String[]{"COMPLETE COMBINED INVENTORY","","","","",""},1);
  row(x,r++,new String[]{"CUSTOMER",customer,"INVENTORY DATE",date,"",""},0);r++;
  row(x,r++,new String[]{"UPC","GTIN","QTY","RETAIL","DESCRIPTION","EXTENDED VALUE"},1);
  int first=r;double totalQty=0;
  for(Row a:data){totalQty+=a.quantity;rowStart(x,r);text(x,0,r,a.upc,0);text(x,1,r,a.gtin,0);number(x,2,r,a.quantity,0);moneyOrBlank(x,3,r,a.retail);text(x,4,r,a.description,0);if(!clean(a.retail).isEmpty())formula(x,5,r,"C"+r+"*D"+r,2);else text(x,5,r,"",0);rowEnd(x);r++;}
  int last=r-1;rowStart(x,r);text(x,0,r,"GRAND TOTAL",1);text(x,1,r,"",1);number(x,2,r,totalQty,1);text(x,3,r,"",1);text(x,4,r,"",1);if(last>=first)formula(x,5,r,"SUM(F"+first+":F"+last+")",3);else number(x,5,r,0,3);rowEnd(x);
  ZipOutputStream z=new ZipOutputStream(out);put(z,"[Content_Types].xml",types());put(z,"_rels/.rels",rels());put(z,"xl/workbook.xml",book());put(z,"xl/_rels/workbook.xml.rels",bookrels());put(z,"xl/styles.xml",styles());
  String sheet="<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"yes\"?><worksheet xmlns=\"http://schemas.openxmlformats.org/spreadsheetml/2006/main\"><sheetViews><sheetView workbookViewId=\"0\"><pane ySplit=\"4\" topLeftCell=\"A5\" activePane=\"bottomLeft\" state=\"frozen\"/></sheetView></sheetViews><cols><col min=\"1\" max=\"1\" width=\"19\" customWidth=\"1\"/><col min=\"2\" max=\"2\" width=\"19\" customWidth=\"1\"/><col min=\"3\" max=\"3\" width=\"12\" customWidth=\"1\"/><col min=\"4\" max=\"4\" width=\"13\" customWidth=\"1\"/><col min=\"5\" max=\"5\" width=\"46\" customWidth=\"1\"/><col min=\"6\" max=\"6\" width=\"18\" customWidth=\"1\"/></cols><sheetData>"+x+"</sheetData><autoFilter ref=\"A4:F"+r+"\"/></worksheet>";put(z,"xl/worksheets/sheet1.xml",sheet);z.finish();z.flush();
 }
 private static void row(StringBuilder x,int r,String[] v,int s){rowStart(x,r);for(int i=0;i<v.length;i++)text(x,i,r,v[i],s);rowEnd(x);}private static void rowStart(StringBuilder x,int r){x.append("<row r=\"").append(r).append("\">");}private static void rowEnd(StringBuilder x){x.append("</row>");}
 private static void text(StringBuilder x,int c,int r,String v,int s){x.append("<c r=\"").append(ref(c,r)).append("\" t=\"inlineStr\"");if(s>0)x.append(" s=\"").append(s).append("\"");x.append("><is><t xml:space=\"preserve\">").append(xml(v)).append("</t></is></c>");}
 private static void number(StringBuilder x,int c,int r,double v,int s){x.append("<c r=\"").append(ref(c,r)).append("\"");if(s>0)x.append(" s=\"").append(s).append("\"");x.append("><v>").append(QuantityMath.format(v)).append("</v></c>");}
 private static void moneyOrBlank(StringBuilder x,int c,int r,String v){try{double n=Double.parseDouble(clean(v).replace("$",""));number(x,c,r,n,2);}catch(Exception e){text(x,c,r,"",0);}}
 private static void formula(StringBuilder x,int c,int r,String f,int s){x.append("<c r=\"").append(ref(c,r)).append("\" s=\"").append(s).append("\"><f>").append(f).append("</f><v>0</v></c>");}
 private static String ref(int c,int r){int n=c+1;StringBuilder b=new StringBuilder();while(n>0){int q=(n-1)%26;b.insert(0,(char)('A'+q));n=(n-1)/26;}return b.toString()+r;}private static String clean(String s){return s==null?"":s.trim();}
 private static String xml(String s){if(s==null)return "";StringBuilder b=new StringBuilder();for(int i=0;i<s.length();i++){char c=s.charAt(i);if(c==9||c==10||c==13||c>=32){if(c=='&')b.append("&amp;");else if(c=='<')b.append("&lt;");else if(c=='>')b.append("&gt;");else if(c=='\"')b.append("&quot;");else if(c=='\'')b.append("&apos;");else b.append(c);}}return b.toString();}
 private static void put(ZipOutputStream z,String n,String v)throws IOException{z.putNextEntry(new ZipEntry(n));z.write(v.getBytes(StandardCharsets.UTF_8));z.closeEntry();}
 private static String types(){return "<?xml version=\"1.0\" encoding=\"UTF-8\"?><Types xmlns=\"http://schemas.openxmlformats.org/package/2006/content-types\"><Default Extension=\"rels\" ContentType=\"application/vnd.openxmlformats-package.relationships+xml\"/><Default Extension=\"xml\" ContentType=\"application/xml\"/><Override PartName=\"/xl/workbook.xml\" ContentType=\"application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml\"/><Override PartName=\"/xl/worksheets/sheet1.xml\" ContentType=\"application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml\"/><Override PartName=\"/xl/styles.xml\" ContentType=\"application/vnd.openxmlformats-officedocument.spreadsheetml.styles+xml\"/></Types>";}private static String rels(){return "<?xml version=\"1.0\" encoding=\"UTF-8\"?><Relationships xmlns=\"http://schemas.openxmlformats.org/package/2006/relationships\"><Relationship Id=\"rId1\" Type=\"http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument\" Target=\"xl/workbook.xml\"/></Relationships>";}
 private static String book(){return "<?xml version=\"1.0\" encoding=\"UTF-8\"?><workbook xmlns=\"http://schemas.openxmlformats.org/spreadsheetml/2006/main\" xmlns:r=\"http://schemas.openxmlformats.org/officeDocument/2006/relationships\"><sheets><sheet name=\"Combined Inventory\" sheetId=\"1\" r:id=\"rId1\"/></sheets><calcPr calcId=\"191029\" fullCalcOnLoad=\"1\" forceFullCalc=\"1\"/></workbook>";}private static String bookrels(){return "<?xml version=\"1.0\" encoding=\"UTF-8\"?><Relationships xmlns=\"http://schemas.openxmlformats.org/package/2006/relationships\"><Relationship Id=\"rId1\" Type=\"http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet\" Target=\"worksheets/sheet1.xml\"/><Relationship Id=\"rId2\" Type=\"http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles\" Target=\"styles.xml\"/></Relationships>";}
 private static String styles(){return "<?xml version=\"1.0\" encoding=\"UTF-8\"?><styleSheet xmlns=\"http://schemas.openxmlformats.org/spreadsheetml/2006/main\"><numFmts count=\"1\"><numFmt numFmtId=\"164\" formatCode=\"$#,##0.00\"/></numFmts><fonts count=\"2\"><font><sz val=\"11\"/><name val=\"Calibri\"/></font><font><b/><color rgb=\"FF000000\"/><sz val=\"11\"/><name val=\"Calibri\"/></font></fonts><fills count=\"3\"><fill><patternFill patternType=\"none\"/></fill><fill><patternFill patternType=\"gray125\"/></fill><fill><patternFill patternType=\"solid\"><fgColor rgb=\"FFFFD700\"/></patternFill></fill></fills><borders count=\"1\"><border><left/><right/><top/><bottom/><diagonal/></border></borders><cellStyleXfs count=\"1\"><xf numFmtId=\"0\" fontId=\"0\" fillId=\"0\" borderId=\"0\"/></cellStyleXfs><cellXfs count=\"4\"><xf numFmtId=\"0\" fontId=\"0\" fillId=\"0\" borderId=\"0\" xfId=\"0\"/><xf numFmtId=\"0\" fontId=\"1\" fillId=\"2\" borderId=\"0\" xfId=\"0\" applyFont=\"1\" applyFill=\"1\"/><xf numFmtId=\"164\" fontId=\"0\" fillId=\"0\" borderId=\"0\" xfId=\"0\" applyNumberFormat=\"1\"/><xf numFmtId=\"164\" fontId=\"1\" fillId=\"2\" borderId=\"0\" xfId=\"0\" applyFont=\"1\" applyFill=\"1\" applyNumberFormat=\"1\"/></cellXfs><cellStyles count=\"1\"><cellStyle name=\"Normal\" xfId=\"0\" builtinId=\"0\"/></cellStyles></styleSheet>";}
}''')

m='app/src/main/java/com/iceinventory/onhand/MonthlyInventoryActivity.java'
rep(m,'SAVE_CIGARETTES=5110,SAVE_UNMATCHED=5111;','SAVE_CIGARETTES=5110,SAVE_UNMATCHED=5111,SAVE_COMBINED_XLSX=5112;','request code')
rep(m,'saveCategory,saveCigarettes,saveUnmatched,approveExceptions;','saveCategory,saveCigarettes,saveUnmatched,saveCombinedXlsx,approveExceptions;','button field')
anchor='''        saveClient=button("7. CUSTOMER IMPORT REPORT");saveClient.setTypeface(android.graphics.Typeface.DEFAULT,android.graphics.Typeface.BOLD);saveClient.setTextColor(Color.BLACK);saveClient.setBackgroundTintList(android.content.res.ColorStateList.valueOf(Color.rgb(255,215,0)));saveClient.setOnClickListener(v->create(SAVE_CLIENT,"application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",base()+" CUSTOMER IMPORT REPORT-"+day()+".xlsx"));root.addView(saveClient,params(62));'''
new=anchor+'''\n        saveCombinedXlsx=button("COMPLETE COMBINED INVENTORY — EXCEL");saveCombinedXlsx.setTypeface(android.graphics.Typeface.DEFAULT,android.graphics.Typeface.BOLD);saveCombinedXlsx.setTextColor(Color.BLACK);saveCombinedXlsx.setBackgroundTintList(android.content.res.ColorStateList.valueOf(Color.rgb(0,190,90)));saveCombinedXlsx.setSingleLine(false);saveCombinedXlsx.setMaxLines(2);saveCombinedXlsx.setOnClickListener(v->create(SAVE_COMBINED_XLSX,"application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",base()+" COMPLETE COMBINED INVENTORY-"+day()+".xlsx"));root.addView(saveCombinedXlsx,params(70));'''
rep(m,anchor,new,'combined inventory button')
rep(m,'else if(request==SAVE_CATEGORY){if(!validated)throw new Exception("Category report is blocked until validation passes");MonthlyCategoryXlsxWriter.writeCategorySummary(use,clientRows);}', 'else if(request==SAVE_COMBINED_XLSX){if(!validated)throw new Exception("Complete combined report is blocked until validation passes");MonthlyCombinedInventoryXlsxWriter.write(use,base(),clientDate(),combinedInventoryRows());}\n        else if(request==SAVE_CATEGORY){if(!validated)throw new Exception("Category report is blocked until validation passes");MonthlyCategoryXlsxWriter.writeCategorySummary(use,clientRows);}', 'write combined xlsx')
anchor2='    private ArrayList<MonthlyUnmatchedXlsxWriter.Row> missingRows(){'
method='''    private ArrayList<MonthlyCombinedInventoryXlsxWriter.Row> combinedInventoryRows(){ArrayList<MonthlyCombinedInventoryXlsxWriter.Row> rows=new ArrayList<>();for(Map.Entry<String,Double> e:combined.entrySet()){MonthlyClientXlsxWriter.Product p=products.get(e.getKey());UnmatchedDetail d=countDetails.get(e.getKey());MonthlyCombinedInventoryXlsxWriter.Row r=new MonthlyCombinedInventoryXlsxWriter.Row();r.upc=e.getKey();r.quantity=e.getValue();if(p!=null){r.gtin=p.gtin;r.retail=p.retail;r.description=p.description;}else r.description=d==null?"":d.description;rows.add(r);}Collections.sort(rows,(a,b)->a.description.compareToIgnoreCase(b.description));return rows;}\n'''
if anchor2 not in Path(m).read_text():raise SystemExit('combined rows anchor missing')
rep(m,anchor2,method+anchor2,'combined rows')
rep(m,'saveClient.setEnabled(countsReady&&validated);saveCategory.setEnabled', 'saveClient.setEnabled(countsReady&&validated);if(saveCombinedXlsx!=null)saveCombinedXlsx.setEnabled(countsReady&&validated);saveCategory.setEnabled', 'enable combined report')

s=Path(m).read_text();w=Path('app/src/main/java/com/iceinventory/onhand/MonthlyCombinedInventoryXlsxWriter.java').read_text()
checks={'version':"versionName '3.0.168'" in Path('app/build.gradle').read_text(),'button':'COMPLETE COMBINED INVENTORY — EXCEL' in s,'all combined':'for(Map.Entry<String,Double> e:combined.entrySet())' in s,'columns':'"UPC","GTIN","QTY","RETAIL","DESCRIPTION","EXTENDED VALUE"' in w,'row formulas':'"C"+r+"*D"+r' in w,'grand formula':'"SUM(F"+first+":F"+last+")"' in w,'recalculate':'fullCalcOnLoad=\\"1\\"' in w}
bad=[k for k,v in checks.items() if not v]
if bad:raise SystemExit('3.0.168 checks failed: '+', '.join(bad))
print('Prepared iCE OnHand 3.0.168: complete combined multi-user valuation Excel with formulas')
