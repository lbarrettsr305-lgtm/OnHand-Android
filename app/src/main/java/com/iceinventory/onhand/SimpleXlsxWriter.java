package com.iceinventory.onhand;

import android.content.SharedPreferences;

import java.io.IOException;
import java.io.OutputStream;
import java.nio.charset.StandardCharsets;
import java.text.SimpleDateFormat;
import java.util.Date;
import java.util.List;
import java.util.Locale;
import java.util.zip.ZipEntry;
import java.util.zip.ZipOutputStream;

/** Minimal dependency-free XLSX writer for the inventory export. */
public final class SimpleXlsxWriter {
    private SimpleXlsxWriter(){}

    public static void write(OutputStream output,List<InventoryDb.Row> rows,SharedPreferences prefs) throws IOException {
        ZipOutputStream zip=new ZipOutputStream(output);
        put(zip,"[Content_Types].xml",contentTypes());
        put(zip,"_rels/.rels",rootRels());
        put(zip,"xl/workbook.xml",workbook());
        put(zip,"xl/_rels/workbook.xml.rels",workbookRels());
        put(zip,"xl/styles.xml",styles());
        put(zip,"xl/worksheets/sheet1.xml",worksheet(rows,prefs));
        zip.finish();
        zip.flush();
    }

    private static String worksheet(List<InventoryDb.Row> rows,SharedPreferences prefs){
        List<String> order=TabTextUtils.getOrder(prefs,true);
        boolean positiveOnly=prefs.getBoolean("export_quantity_above_zero_only",false);
        SimpleDateFormat dateFmt=new SimpleDateFormat("yyyy-MM-dd",Locale.US);
        SimpleDateFormat timeFmt=new SimpleDateFormat("HH:mm:ss",Locale.US);
        StringBuilder x=new StringBuilder(8192);
        x.append("<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"yes\"?>");
        x.append("<worksheet xmlns=\"http://schemas.openxmlformats.org/spreadsheetml/2006/main\">");
        x.append("<sheetViews><sheetView workbookViewId=\"0\"><pane ySplit=\"1\" topLeftCell=\"A2\" activePane=\"bottomLeft\" state=\"frozen\"/></sheetView></sheetViews>");
        x.append("<cols>");
        for(int i=0;i<order.size();i++){
            double width=columnWidth(order.get(i));
            int col=i+1;
            x.append("<col min=\"").append(col).append("\" max=\"").append(col).append("\" width=\"").append(width).append("\" customWidth=\"1\"/>");
        }
        x.append("</cols><sheetData>");

        int rowNum=1;
        x.append("<row r=\"1\">");
        for(int i=0;i<order.size();i++)textCell(x,cellRef(i,rowNum),TabTextUtils.exportHeader(order.get(i)),1);
        x.append("</row>");

        for(InventoryDb.Row row:rows){
            if(positiveOnly&&row.quantity<=0)continue;
            rowNum++;
            x.append("<row r=\"").append(rowNum).append("\">");
            Date when=new Date(row.updatedAt>0?row.updatedAt:System.currentTimeMillis());
            for(int i=0;i<order.size();i++){
                String field=order.get(i);
                String ref=cellRef(i,rowNum);
                if("quantity".equals(field))numberCell(x,ref,row.quantity);
                else textCell(x,ref,value(field,row,when,dateFmt,timeFmt),0);
            }
            x.append("</row>");
        }
        x.append("</sheetData><autoFilter ref=\"A1:").append(cellRef(Math.max(0,order.size()-1),Math.max(1,rowNum))).append("\"/>");
        x.append("</worksheet>");
        return x.toString();
    }

    private static String value(String field,InventoryDb.Row r,Date when,SimpleDateFormat dateFmt,SimpleDateFormat timeFmt){
        if("barcode".equals(field))return clean(r.barcode);
        if("description".equals(field))return clean(r.description);
        if("price".equals(field))return clean(r.price);
        if("location".equals(field))return clean(r.location);
        if("scan_date".equals(field))return dateFmt.format(when);
        if("scan_time".equals(field))return timeFmt.format(when);
        return "";
    }

    private static double columnWidth(String field){
        if("quantity".equals(field))return 12;
        if("barcode".equals(field))return 20;
        if("description".equals(field))return 46;
        if("price".equals(field))return 14;
        if("location".equals(field))return 20;
        return 18;
    }

    private static void textCell(StringBuilder x,String ref,String value,int style){
        x.append("<c r=\"").append(ref).append("\" t=\"inlineStr\"");
        if(style>0)x.append(" s=\"").append(style).append("\"");
        x.append("><is><t xml:space=\"preserve\">").append(xml(value)).append("</t></is></c>");
    }

    private static void numberCell(StringBuilder x,String ref,int value){
        x.append("<c r=\"").append(ref).append("\"><v>").append(value).append("</v></c>");
    }

    private static String cellRef(int zeroBasedColumn,int row){
        int n=zeroBasedColumn+1;
        StringBuilder c=new StringBuilder();
        while(n>0){int rem=(n-1)%26;c.insert(0,(char)('A'+rem));n=(n-1)/26;}
        return c.toString()+row;
    }

    private static String clean(String s){return s==null?"":s.replace('\t',' ').replace('\r',' ').replace('\n',' ').trim();}
    private static String xml(String s){
        String v=s==null?"":s;
        return v.replace("&","&amp;").replace("<","&lt;").replace(">","&gt;").replace("\"","&quot;").replace("'","&apos;");
    }

    private static void put(ZipOutputStream zip,String name,String content) throws IOException {
        zip.putNextEntry(new ZipEntry(name));
        zip.write(content.getBytes(StandardCharsets.UTF_8));
        zip.closeEntry();
    }

    private static String contentTypes(){
        return "<?xml version=\"1.0\" encoding=\"UTF-8\"?>"+
                "<Types xmlns=\"http://schemas.openxmlformats.org/package/2006/content-types\">"+
                "<Default Extension=\"rels\" ContentType=\"application/vnd.openxmlformats-package.relationships+xml\"/>"+
                "<Default Extension=\"xml\" ContentType=\"application/xml\"/>"+
                "<Override PartName=\"/xl/workbook.xml\" ContentType=\"application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml\"/>"+
                "<Override PartName=\"/xl/worksheets/sheet1.xml\" ContentType=\"application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml\"/>"+
                "<Override PartName=\"/xl/styles.xml\" ContentType=\"application/vnd.openxmlformats-officedocument.spreadsheetml.styles+xml\"/>"+
                "</Types>";
    }

    private static String rootRels(){
        return "<?xml version=\"1.0\" encoding=\"UTF-8\"?>"+
                "<Relationships xmlns=\"http://schemas.openxmlformats.org/package/2006/relationships\">"+
                "<Relationship Id=\"rId1\" Type=\"http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument\" Target=\"xl/workbook.xml\"/>"+
                "</Relationships>";
    }

    private static String workbook(){
        return "<?xml version=\"1.0\" encoding=\"UTF-8\"?>"+
                "<workbook xmlns=\"http://schemas.openxmlformats.org/spreadsheetml/2006/main\" xmlns:r=\"http://schemas.openxmlformats.org/officeDocument/2006/relationships\">"+
                "<sheets><sheet name=\"Inventory\" sheetId=\"1\" r:id=\"rId1\"/></sheets></workbook>";
    }

    private static String workbookRels(){
        return "<?xml version=\"1.0\" encoding=\"UTF-8\"?>"+
                "<Relationships xmlns=\"http://schemas.openxmlformats.org/package/2006/relationships\">"+
                "<Relationship Id=\"rId1\" Type=\"http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet\" Target=\"worksheets/sheet1.xml\"/>"+
                "<Relationship Id=\"rId2\" Type=\"http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles\" Target=\"styles.xml\"/>"+
                "</Relationships>";
    }

    private static String styles(){
        return "<?xml version=\"1.0\" encoding=\"UTF-8\"?>"+
                "<styleSheet xmlns=\"http://schemas.openxmlformats.org/spreadsheetml/2006/main\">"+
                "<fonts count=\"2\"><font><sz val=\"11\"/><name val=\"Calibri\"/></font><font><b/><sz val=\"11\"/><name val=\"Calibri\"/></font></fonts>"+
                "<fills count=\"2\"><fill><patternFill patternType=\"none\"/></fill><fill><patternFill patternType=\"gray125\"/></fill></fills>"+
                "<borders count=\"1\"><border><left/><right/><top/><bottom/><diagonal/></border></borders>"+
                "<cellStyleXfs count=\"1\"><xf numFmtId=\"0\" fontId=\"0\" fillId=\"0\" borderId=\"0\"/></cellStyleXfs>"+
                "<cellXfs count=\"2\"><xf numFmtId=\"0\" fontId=\"0\" fillId=\"0\" borderId=\"0\" xfId=\"0\"/><xf numFmtId=\"0\" fontId=\"1\" fillId=\"0\" borderId=\"0\" xfId=\"0\" applyFont=\"1\"/></cellXfs>"+
                "<cellStyles count=\"1\"><cellStyle name=\"Normal\" xfId=\"0\" builtinId=\"0\"/></cellStyles>"+
                "</styleSheet>";
    }
}
