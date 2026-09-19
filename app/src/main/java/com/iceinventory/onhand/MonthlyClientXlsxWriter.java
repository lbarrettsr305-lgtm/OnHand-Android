package com.iceinventory.onhand;

import java.io.IOException;
import java.io.OutputStream;
import java.nio.charset.StandardCharsets;
import java.util.List;
import java.util.zip.ZipEntry;
import java.util.zip.ZipOutputStream;

/** Writes the locked CHEV2620 master and nine-column client workbooks. */
public final class MonthlyClientXlsxWriter {
    private MonthlyClientXlsxWriter(){}

    public static final String[] CLIENT_HEADERS={"GTIN","QUANTITY","CATEGORY_ID","RETAIL","DESCRIPTION","COST","DATE","TIME","SECTION"};
    public static final String[] MASTER_HEADERS={"UPC","GTIN","CATEGORY_ID","RETAIL","DESCRIPTION","COST","DATE","TIME","SECTION","CATEGORY_NAME"};

    public static final class Product {
        public String upc="",gtin="",category="",retail="",description="",cost="",date="",time="10:00 AM",section="FLOOR",categoryName="";
    }
    public static final class ClientRow {
        public Product product;public long quantity;
        public ClientRow(Product product,long quantity){this.product=product;this.quantity=quantity;}
    }

    public static void writeMaster(OutputStream output,List<Product> products) throws IOException {
        StringBuilder rows=new StringBuilder();int r=1;
        headerRow(rows,MASTER_HEADERS,r++);
        for(Product p:products){
            rowStart(rows,r);text(rows,0,r,p.upc,0);text(rows,1,r,p.gtin,0);numberOrText(rows,2,r,p.category,0);numberOrText(rows,3,r,p.retail,2);text(rows,4,r,p.description,0);numberOrText(rows,5,r,p.cost,3);text(rows,6,r,p.date,0);text(rows,7,r,p.time,0);text(rows,8,r,p.section,0);text(rows,9,r,p.categoryName,0);rowEnd(rows);r++;
        }
        write(output,"CHEV2620 MASTER",rows.toString(),MASTER_HEADERS.length,r-1);
    }

    public static void writeClient(OutputStream output,List<ClientRow> clientRows) throws IOException {
        StringBuilder rows=new StringBuilder();int r=1;
        headerRow(rows,CLIENT_HEADERS,r++);
        for(ClientRow item:clientRows){Product p=item.product;
            rowStart(rows,r);text(rows,0,r,p.gtin,0);number(rows,1,r,item.quantity,0);numberOrText(rows,2,r,p.category,0);numberOrText(rows,3,r,p.retail,2);text(rows,4,r,p.description,0);numberOrText(rows,5,r,p.cost,3);text(rows,6,r,p.date,0);text(rows,7,r,p.time,0);text(rows,8,r,p.section,0);rowEnd(rows);r++;
        }
        write(output,"CHEV2620 INVENTORY",rows.toString(),CLIENT_HEADERS.length,r-1);
    }

    private static void write(OutputStream output,String sheetName,String rows,int columns,int lastRow) throws IOException {
        ZipOutputStream zip=new ZipOutputStream(output);
        put(zip,"[Content_Types].xml",contentTypes());put(zip,"_rels/.rels",rootRels());put(zip,"xl/workbook.xml",workbook(sheetName));put(zip,"xl/_rels/workbook.xml.rels",workbookRels());put(zip,"xl/styles.xml",styles());
        StringBuilder s=new StringBuilder(4096+rows.length());
        s.append("<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"yes\"?><worksheet xmlns=\"http://schemas.openxmlformats.org/spreadsheetml/2006/main\"><sheetViews><sheetView workbookViewId=\"0\"><pane ySplit=\"1\" topLeftCell=\"A2\" activePane=\"bottomLeft\" state=\"frozen\"/></sheetView></sheetViews><cols>");
        double[] widths={20,13,14,13,42,13,14,13,13,24};for(int i=0;i<columns;i++)s.append("<col min=\"").append(i+1).append("\" max=\"").append(i+1).append("\" width=\"").append(widths[i]).append("\" customWidth=\"1\"/>");
        s.append("</cols><sheetData>").append(rows).append("</sheetData><autoFilter ref=\"A1:").append(ref(columns-1,Math.max(1,lastRow))).append("\"/></worksheet>");
        put(zip,"xl/worksheets/sheet1.xml",s.toString());zip.finish();zip.flush();
    }

    private static void headerRow(StringBuilder x,String[] h,int r){rowStart(x,r);for(int i=0;i<h.length;i++)text(x,i,r,h[i],1);rowEnd(x);}
    private static void rowStart(StringBuilder x,int r){x.append("<row r=\"").append(r).append("\">");}
    private static void rowEnd(StringBuilder x){x.append("</row>");}
    private static void text(StringBuilder x,int c,int r,String v,int style){x.append("<c r=\"").append(ref(c,r)).append("\" t=\"inlineStr\"");if(style>0)x.append(" s=\"").append(style).append("\"");x.append("><is><t xml:space=\"preserve\">").append(xml(v)).append("</t></is></c>");}
    private static void number(StringBuilder x,int c,int r,long v,int style){x.append("<c r=\"").append(ref(c,r)).append("\"");if(style>0)x.append(" s=\"").append(style).append("\"");x.append("><v>").append(v).append("</v></c>");}
    private static void numberOrText(StringBuilder x,int c,int r,String v,int style){try{double d=Double.parseDouble(v==null?"":v.trim());x.append("<c r=\"").append(ref(c,r)).append("\"");if(style>0)x.append(" s=\"").append(style).append("\"");x.append("><v>").append(d).append("</v></c>");}catch(Exception e){text(x,c,r,v,0);}}
    private static String ref(int c,int r){int n=c+1;StringBuilder b=new StringBuilder();while(n>0){int q=(n-1)%26;b.insert(0,(char)('A'+q));n=(n-1)/26;}return b.toString()+r;}
    private static String xml(String s){if(s==null)return "";StringBuilder b=new StringBuilder();for(int i=0;i<s.length();i++){char c=s.charAt(i);if(c==9||c==10||c==13||c>=32){if(c=='&')b.append("&amp;");else if(c=='<')b.append("&lt;");else if(c=='>')b.append("&gt;");else if(c=='\"')b.append("&quot;");else if(c=='\'')b.append("&apos;");else b.append(c);}}return b.toString();}
    private static void put(ZipOutputStream z,String n,String v)throws IOException{z.putNextEntry(new ZipEntry(n));z.write(v.getBytes(StandardCharsets.UTF_8));z.closeEntry();}
    private static String contentTypes(){return "<?xml version=\"1.0\" encoding=\"UTF-8\"?><Types xmlns=\"http://schemas.openxmlformats.org/package/2006/content-types\"><Default Extension=\"rels\" ContentType=\"application/vnd.openxmlformats-package.relationships+xml\"/><Default Extension=\"xml\" ContentType=\"application/xml\"/><Override PartName=\"/xl/workbook.xml\" ContentType=\"application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml\"/><Override PartName=\"/xl/worksheets/sheet1.xml\" ContentType=\"application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml\"/><Override PartName=\"/xl/styles.xml\" ContentType=\"application/vnd.openxmlformats-officedocument.spreadsheetml.styles+xml\"/></Types>";}
    private static String rootRels(){return "<?xml version=\"1.0\" encoding=\"UTF-8\"?><Relationships xmlns=\"http://schemas.openxmlformats.org/package/2006/relationships\"><Relationship Id=\"rId1\" Type=\"http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument\" Target=\"xl/workbook.xml\"/></Relationships>";}
    private static String workbook(String n){return "<?xml version=\"1.0\" encoding=\"UTF-8\"?><workbook xmlns=\"http://schemas.openxmlformats.org/spreadsheetml/2006/main\" xmlns:r=\"http://schemas.openxmlformats.org/officeDocument/2006/relationships\"><sheets><sheet name=\""+xml(n)+"\" sheetId=\"1\" r:id=\"rId1\"/></sheets></workbook>";}
    private static String workbookRels(){return "<?xml version=\"1.0\" encoding=\"UTF-8\"?><Relationships xmlns=\"http://schemas.openxmlformats.org/package/2006/relationships\"><Relationship Id=\"rId1\" Type=\"http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet\" Target=\"worksheets/sheet1.xml\"/><Relationship Id=\"rId2\" Type=\"http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles\" Target=\"styles.xml\"/></Relationships>";}
    private static String styles(){return "<?xml version=\"1.0\" encoding=\"UTF-8\"?><styleSheet xmlns=\"http://schemas.openxmlformats.org/spreadsheetml/2006/main\"><numFmts count=\"2\"><numFmt numFmtId=\"164\" formatCode=\"0.00\"/><numFmt numFmtId=\"165\" formatCode=\"0.0000\"/></numFmts><fonts count=\"2\"><font><sz val=\"11\"/><name val=\"Calibri\"/></font><font><b/><color rgb=\"FFFFFFFF\"/><sz val=\"11\"/><name val=\"Calibri\"/></font></fonts><fills count=\"3\"><fill><patternFill patternType=\"none\"/></fill><fill><patternFill patternType=\"gray125\"/></fill><fill><patternFill patternType=\"solid\"><fgColor rgb=\"FF0B302B\"/></patternFill></fill></fills><borders count=\"1\"><border><left/><right/><top/><bottom/><diagonal/></border></borders><cellStyleXfs count=\"1\"><xf numFmtId=\"0\" fontId=\"0\" fillId=\"0\" borderId=\"0\"/></cellStyleXfs><cellXfs count=\"4\"><xf numFmtId=\"0\" fontId=\"0\" fillId=\"0\" borderId=\"0\" xfId=\"0\"/><xf numFmtId=\"0\" fontId=\"1\" fillId=\"2\" borderId=\"0\" xfId=\"0\" applyFont=\"1\" applyFill=\"1\"/><xf numFmtId=\"164\" fontId=\"0\" fillId=\"0\" borderId=\"0\" xfId=\"0\" applyNumberFormat=\"1\"/><xf numFmtId=\"165\" fontId=\"0\" fillId=\"0\" borderId=\"0\" xfId=\"0\" applyNumberFormat=\"1\"/></cellXfs><cellStyles count=\"1\"><cellStyle name=\"Normal\" xfId=\"0\" builtinId=\"0\"/></cellStyles></styleSheet>";}
}
