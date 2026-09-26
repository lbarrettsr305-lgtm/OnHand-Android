from pathlib import Path

base = Path('.github/prepare_30166.py')
exec(compile(base.read_text(), str(base), 'exec'), {'__name__': '__main__', '__file__': str(base)})


def rep(path, old, new, label):
    p = Path(path)
    s = p.read_text()
    if s.count(old) != 1:
        raise SystemExit('3.0.167 target ' + label + ' count ' + str(s.count(old)))
    p.write_text(s.replace(old, new, 1))


rep('app/build.gradle', 'versionCode 30166', 'versionCode 30167', 'code')
rep('app/build.gradle', "versionName '3.0.166'", "versionName '3.0.167'", 'name')
rep('app/src/main/AndroidManifest.xml', 'iCE Onhand 3.0.166', 'iCE Onhand 3.0.167', 'manifest')
rep('app/src/main/java/com/iceinventory/onhand/MainActivity.java',
    'Onhand Inventory 3.0.166', 'Onhand Inventory 3.0.167', 'header')

writer = r'''package com.iceinventory.onhand;
import java.io.*;import java.nio.charset.StandardCharsets;import java.util.*;import java.util.zip.*;
public final class MonthlyUnmatchedXlsxWriter{
 private MonthlyUnmatchedXlsxWriter(){}
 public static final class Row{public String barcode="",description="",users="",locations="";public double quantity;}
 public static void write(OutputStream out,String customer,String date,List<Row> data)throws IOException{
  StringBuilder rows=new StringBuilder();int r=1;
  row(rows,r++,new String[]{"MISSING / NEW ITEMS — CLIENT ACTION REQUIRED","","","",""},true);
  row(rows,r++,new String[]{"CUSTOMER",customer,"INVENTORY DATE",date,""},false);r++;
  row(rows,r++,new String[]{"BARCODE","QUANTITY","DESCRIPTION","COUNTER / USER FILE AND QUANTITY","LOCATIONS"},true);
  double total=0;for(Row a:data){total+=a.quantity;rowStart(rows,r);text(rows,0,r,a.barcode,0);number(rows,1,r,a.quantity,0);text(rows,2,r,a.description,0);text(rows,3,r,a.users,0);text(rows,4,r,a.locations,0);rowEnd(rows);r++;}
  rowStart(rows,r);text(rows,0,r,"TOTAL MISSING QUANTITY",1);number(rows,1,r,total,1);text(rows,2,r,"Add or correct these products in Petrosoft after inventory.",1);text(rows,3,r,"",1);text(rows,4,r,"",1);rowEnd(rows);
  ZipOutputStream zip=new ZipOutputStream(out);put(zip,"[Content_Types].xml",types());put(zip,"_rels/.rels",rels());put(zip,"xl/workbook.xml",book());put(zip,"xl/_rels/workbook.xml.rels",bookrels());put(zip,"xl/styles.xml",styles());
  String sheet="<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"yes\"?><worksheet xmlns=\"http://schemas.openxmlformats.org/spreadsheetml/2006/main\"><sheetViews><sheetView workbookViewId=\"0\"><pane ySplit=\"4\" topLeftCell=\"A5\" activePane=\"bottomLeft\" state=\"frozen\"/></sheetView></sheetViews><cols><col min=\"1\" max=\"1\" width=\"20\" customWidth=\"1\"/><col min=\"2\" max=\"2\" width=\"12\" customWidth=\"1\"/><col min=\"3\" max=\"3\" width=\"42\" customWidth=\"1\"/><col min=\"4\" max=\"4\" width=\"55\" customWidth=\"1\"/><col min=\"5\" max=\"5\" width=\"32\" customWidth=\"1\"/></cols><sheetData>"+rows+"</sheetData><autoFilter ref=\"A4:E"+r+"\"/></worksheet>";
  put(zip,"xl/worksheets/sheet1.xml",sheet);zip.finish();zip.flush();
 }
 private static void row(StringBuilder x,int r,String[] v,boolean bold){rowStart(x,r);for(int i=0;i<v.length;i++)text(x,i,r,v[i],bold?1:0);rowEnd(x);}
 private static void rowStart(StringBuilder x,int r){x.append("<row r=\"").append(r).append("\">");}private static void rowEnd(StringBuilder x){x.append("</row>");}
 private static void text(StringBuilder x,int c,int r,String v,int s){x.append("<c r=\"").append(ref(c,r)).append("\" t=\"inlineStr\"");if(s>0)x.append(" s=\"").append(s).append("\"");x.append("><is><t xml:space=\"preserve\">").append(xml(v)).append("</t></is></c>");}
 private static void number(StringBuilder x,int c,int r,double v,int s){x.append("<c r=\"").append(ref(c,r)).append("\"");if(s>0)x.append(" s=\"").append(s).append("\"");x.append("><v>").append(QuantityMath.format(v)).append("</v></c>");}
 private static String ref(int c,int r){int n=c+1;StringBuilder b=new StringBuilder();while(n>0){int q=(n-1)%26;b.insert(0,(char)('A'+q));n=(n-1)/26;}return b.toString()+r;}
 private static String xml(String s){if(s==null)return "";StringBuilder b=new StringBuilder();for(int i=0;i<s.length();i++){char c=s.charAt(i);if(c==9||c==10||c==13||c>=32){if(c=='&')b.append("&amp;");else if(c=='<')b.append("&lt;");else if(c=='>')b.append("&gt;");else if(c=='\"')b.append("&quot;");else if(c=='\'')b.append("&apos;");else b.append(c);}}return b.toString();}
 private static void put(ZipOutputStream z,String n,String v)throws IOException{z.putNextEntry(new ZipEntry(n));z.write(v.getBytes(StandardCharsets.UTF_8));z.closeEntry();}
 private static String types(){return "<?xml version=\"1.0\" encoding=\"UTF-8\"?><Types xmlns=\"http://schemas.openxmlformats.org/package/2006/content-types\"><Default Extension=\"rels\" ContentType=\"application/vnd.openxmlformats-package.relationships+xml\"/><Default Extension=\"xml\" ContentType=\"application/xml\"/><Override PartName=\"/xl/workbook.xml\" ContentType=\"application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml\"/><Override PartName=\"/xl/worksheets/sheet1.xml\" ContentType=\"application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml\"/><Override PartName=\"/xl/styles.xml\" ContentType=\"application/vnd.openxmlformats-officedocument.spreadsheetml.styles+xml\"/></Types>";}
 private static String rels(){return "<?xml version=\"1.0\" encoding=\"UTF-8\"?><Relationships xmlns=\"http://schemas.openxmlformats.org/package/2006/relationships\"><Relationship Id=\"rId1\" Type=\"http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument\" Target=\"xl/workbook.xml\"/></Relationships>";}
 private static String book(){return "<?xml version=\"1.0\" encoding=\"UTF-8\"?><workbook xmlns=\"http://schemas.openxmlformats.org/spreadsheetml/2006/main\" xmlns:r=\"http://schemas.openxmlformats.org/officeDocument/2006/relationships\"><sheets><sheet name=\"Missing New Items\" sheetId=\"1\" r:id=\"rId1\"/></sheets></workbook>";}
 private static String bookrels(){return "<?xml version=\"1.0\" encoding=\"UTF-8\"?><Relationships xmlns=\"http://schemas.openxmlformats.org/package/2006/relationships\"><Relationship Id=\"rId1\" Type=\"http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet\" Target=\"worksheets/sheet1.xml\"/><Relationship Id=\"rId2\" Type=\"http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles\" Target=\"styles.xml\"/></Relationships>";}
 private static String styles(){return "<?xml version=\"1.0\" encoding=\"UTF-8\"?><styleSheet xmlns=\"http://schemas.openxmlformats.org/spreadsheetml/2006/main\"><fonts count=\"2\"><font><sz val=\"11\"/><name val=\"Calibri\"/></font><font><b/><color rgb=\"FF000000\"/><sz val=\"11\"/><name val=\"Calibri\"/></font></fonts><fills count=\"3\"><fill><patternFill patternType=\"none\"/></fill><fill><patternFill patternType=\"gray125\"/></fill><fill><patternFill patternType=\"solid\"><fgColor rgb=\"FFFFD700\"/></patternFill></fill></fills><borders count=\"1\"><border><left/><right/><top/><bottom/><diagonal/></border></borders><cellStyleXfs count=\"1\"><xf numFmtId=\"0\" fontId=\"0\" fillId=\"0\" borderId=\"0\"/></cellStyleXfs><cellXfs count=\"2\"><xf numFmtId=\"0\" fontId=\"0\" fillId=\"0\" borderId=\"0\" xfId=\"0\"/><xf numFmtId=\"0\" fontId=\"1\" fillId=\"2\" borderId=\"0\" xfId=\"0\" applyFont=\"1\" applyFill=\"1\"/></cellXfs><cellStyles count=\"1\"><cellStyle name=\"Normal\" xfId=\"0\" builtinId=\"0\"/></cellStyles></styleSheet>";}
}'''
Path('app/src/main/java/com/iceinventory/onhand/MonthlyUnmatchedXlsxWriter.java').write_text(writer)

s = Path('app/src/main/java/com/iceinventory/onhand/MonthlyUnmatchedXlsxWriter.java').read_text()
checks = {
    'version': "versionName '3.0.167'" in Path('app/build.gradle').read_text(),
    'control characters removed': 'if(c==9||c==10||c==13||c>=32)' in s,
    'normal style declared': '<cellStyles count=' in s,
    'five explicit columns': 'text(rows,4,r,a.locations,0)' in s,
    'standalone worksheet': 'standalone=\\\"yes\\\"' in s,
    'location import retained': 'int qi=0,bi=1,di=2,li=4' in Path('app/src/main/java/com/iceinventory/onhand/MonthlyInventoryActivity.java').read_text()
}
bad = [k for k, v in checks.items() if not v]
if bad: raise SystemExit('3.0.167 checks failed: ' + ', '.join(bad))
print('Prepared iCE OnHand 3.0.167: standards-safe missing-items Excel with fixed columns and locations')
