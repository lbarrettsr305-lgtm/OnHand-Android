package com.iceinventory.onhand;

import java.io.IOException;
import java.io.OutputStream;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.Collections;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Locale;
import java.util.Map;
import java.util.zip.ZipEntry;
import java.util.zip.ZipOutputStream;

/** Petrosoft category quantity reports. The locked customer import workbook remains unchanged. */
public final class MonthlyCategoryXlsxWriter {
    private MonthlyCategoryXlsxWriter(){}

    private static final class CategoryTotal {
        String name;
        long quantity;
        CategoryTotal(String name){this.name=name;}
    }

    public static void writeCategorySummary(OutputStream output,List<MonthlyClientXlsxWriter.ClientRow> rows) throws IOException {
        Map<String,CategoryTotal> totals=new LinkedHashMap<>();
        for(MonthlyClientXlsxWriter.ClientRow row:rows){
            String name=categoryName(row.product);
            String key=name.toUpperCase(Locale.US);
            CategoryTotal total=totals.get(key);
            if(total==null){total=new CategoryTotal(name);totals.put(key,total);}
            total.quantity=Math.addExact(total.quantity,row.quantity);
        }
        List<CategoryTotal> sorted=new ArrayList<>(totals.values());
        Collections.sort(sorted,(a,b)->a.name.compareToIgnoreCase(b.name));
        StringBuilder body=new StringBuilder();int r=1;long grand=0;
        rowStart(body,r);text(body,0,r,"CATEGORY NAME",1);text(body,1,r,"QTY",1);rowEnd(body);r++;
        for(CategoryTotal total:sorted){rowStart(body,r);text(body,0,r,total.name,0);number(body,1,r,total.quantity,0);rowEnd(body);grand=Math.addExact(grand,total.quantity);r++;}
        rowStart(body,r);text(body,0,r,"GRAND TOTAL",1);number(body,1,r,grand,1);rowEnd(body);
        write(output,"CATEGORY REPORT",body.toString(),2,r);
    }

    public static void writeCigarettes(OutputStream output,List<MonthlyClientXlsxWriter.ClientRow> rows) throws IOException {
        List<MonthlyClientXlsxWriter.ClientRow> cigarettes=new ArrayList<>();
        for(MonthlyClientXlsxWriter.ClientRow row:rows)if(categoryName(row.product).toUpperCase(Locale.US).contains("CIGARETTE"))cigarettes.add(row);
        Collections.sort(cigarettes,(a,b)->{int q=Long.compare(b.quantity,a.quantity);return q!=0?q:a.product.description.compareToIgnoreCase(b.product.description);});
        StringBuilder body=new StringBuilder();int r=1;long total=0;
        rowStart(body,r);text(body,0,r,"CATEGORY NAME",1);text(body,1,r,"GTIN",1);text(body,2,r,"DESCRIPTION",1);text(body,3,r,"QTY",1);rowEnd(body);r++;
        for(MonthlyClientXlsxWriter.ClientRow row:cigarettes){MonthlyClientXlsxWriter.Product p=row.product;rowStart(body,r);text(body,0,r,categoryName(p),0);text(body,1,r,p.gtin,0);text(body,2,r,p.description,0);number(body,3,r,row.quantity,0);rowEnd(body);total=Math.addExact(total,row.quantity);r++;}
        rowStart(body,r);text(body,0,r,"TOTAL CIGARETTES QTY",1);number(body,3,r,total,1);rowEnd(body);
        write(output,"CIGARETTES",body.toString(),4,r);
    }

    private static String categoryName(MonthlyClientXlsxWriter.Product p){
        String name=p==null?"":clean(p.categoryName);
        if(!name.isEmpty())return name;
        String id=p==null?"":clean(p.category);
        return id.isEmpty()?"UNCATEGORIZED":"CATEGORY "+id;
    }

    private static void write(OutputStream output,String sheetName,String rows,int columns,int lastRow) throws IOException {
        ZipOutputStream zip=new ZipOutputStream(output);
        put(zip,"[Content_Types].xml",contentTypes());put(zip,"_rels/.rels",rootRels());put(zip,"xl/workbook.xml",workbook(sheetName));put(zip,"xl/_rels/workbook.xml.rels",workbookRels());put(zip,"xl/styles.xml",styles());
        StringBuilder sheet=new StringBuilder(4096+rows.length());
        sheet.append("<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"yes\"?><worksheet xmlns=\"http://schemas.openxmlformats.org/spreadsheetml/2006/main\"><sheetViews><sheetView workbookViewId=\"0\"><pane ySplit=\"1\" topLeftCell=\"A2\" activePane=\"bottomLeft\" state=\"frozen\"/></sheetView></sheetViews><cols>");
        double[] widths={25,20,48,13};for(int i=0;i<columns;i++)sheet.append("<col min=\"").append(i+1).append("\" max=\"").append(i+1).append("\" width=\"").append(widths[i]).append("\" customWidth=\"1\"/>");
        sheet.append("</cols><sheetData>").append(rows).append("</sheetData><autoFilter ref=\"A1:").append(ref(columns-1,Math.max(1,lastRow))).append("\"/></worksheet>");
        put(zip,"xl/worksheets/sheet1.xml",sheet.toString());zip.finish();zip.flush();
    }

    private static void rowStart(StringBuilder x,int r){x.append("<row r=\"").append(r).append("\">");}
    private static void rowEnd(StringBuilder x){x.append("</row>");}
    private static void text(StringBuilder x,int c,int r,String v,int style){x.append("<c r=\"").append(ref(c,r)).append("\" t=\"inlineStr\"");if(style>0)x.append(" s=\"").append(style).append("\"");x.append("><is><t xml:space=\"preserve\">").append(xml(v)).append("</t></is></c>");}
    private static void number(StringBuilder x,int c,int r,long v,int style){x.append("<c r=\"").append(ref(c,r)).append("\"");if(style>0)x.append(" s=\"").append(style).append("\"");x.append("><v>").append(v).append("</v></c>");}
    private static String ref(int c,int r){int n=c+1;StringBuilder b=new StringBuilder();while(n>0){int q=(n-1)%26;b.insert(0,(char)('A'+q));n=(n-1)/26;}return b.toString()+r;}
    private static String clean(String s){return s==null?"":s.trim();}
    private static String xml(String s){if(s==null)return "";StringBuilder b=new StringBuilder();for(int i=0;i<s.length();i++){char c=s.charAt(i);if(c==9||c==10||c==13||c>=32){if(c=='&')b.append("&amp;");else if(c=='<')b.append("&lt;");else if(c=='>')b.append("&gt;");else if(c=='\"')b.append("&quot;");else if(c=='\'')b.append("&apos;");else b.append(c);}}return b.toString();}
    private static void put(ZipOutputStream z,String n,String v)throws IOException{z.putNextEntry(new ZipEntry(n));z.write(v.getBytes(StandardCharsets.UTF_8));z.closeEntry();}
    private static String contentTypes(){return "<?xml version=\"1.0\" encoding=\"UTF-8\"?><Types xmlns=\"http://schemas.openxmlformats.org/package/2006/content-types\"><Default Extension=\"rels\" ContentType=\"application/vnd.openxmlformats-package.relationships+xml\"/><Default Extension=\"xml\" ContentType=\"application/xml\"/><Override PartName=\"/xl/workbook.xml\" ContentType=\"application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml\"/><Override PartName=\"/xl/worksheets/sheet1.xml\" ContentType=\"application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml\"/><Override PartName=\"/xl/styles.xml\" ContentType=\"application/vnd.openxmlformats-officedocument.spreadsheetml.styles+xml\"/></Types>";}
    private static String rootRels(){return "<?xml version=\"1.0\" encoding=\"UTF-8\"?><Relationships xmlns=\"http://schemas.openxmlformats.org/package/2006/relationships\"><Relationship Id=\"rId1\" Type=\"http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument\" Target=\"xl/workbook.xml\"/></Relationships>";}
    private static String workbook(String n){return "<?xml version=\"1.0\" encoding=\"UTF-8\"?><workbook xmlns=\"http://schemas.openxmlformats.org/spreadsheetml/2006/main\" xmlns:r=\"http://schemas.openxmlformats.org/officeDocument/2006/relationships\"><sheets><sheet name=\""+xml(n)+"\" sheetId=\"1\" r:id=\"rId1\"/></sheets></workbook>";}
    private static String workbookRels(){return "<?xml version=\"1.0\" encoding=\"UTF-8\"?><Relationships xmlns=\"http://schemas.openxmlformats.org/package/2006/relationships\"><Relationship Id=\"rId1\" Type=\"http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet\" Target=\"worksheets/sheet1.xml\"/><Relationship Id=\"rId2\" Type=\"http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles\" Target=\"styles.xml\"/></Relationships>";}
    private static String styles(){return "<?xml version=\"1.0\" encoding=\"UTF-8\"?><styleSheet xmlns=\"http://schemas.openxmlformats.org/spreadsheetml/2006/main\"><fonts count=\"2\"><font><sz val=\"11\"/><name val=\"Calibri\"/></font><font><b/><color rgb=\"FF000000\"/><sz val=\"11\"/><name val=\"Calibri\"/></font></fonts><fills count=\"3\"><fill><patternFill patternType=\"none\"/></fill><fill><patternFill patternType=\"gray125\"/></fill><fill><patternFill patternType=\"solid\"><fgColor rgb=\"FFFFD700\"/></patternFill></fill></fills><borders count=\"1\"><border><left/><right/><top/><bottom/><diagonal/></border></borders><cellStyleXfs count=\"1\"><xf numFmtId=\"0\" fontId=\"0\" fillId=\"0\" borderId=\"0\"/></cellStyleXfs><cellXfs count=\"2\"><xf numFmtId=\"0\" fontId=\"0\" fillId=\"0\" borderId=\"0\" xfId=\"0\"/><xf numFmtId=\"0\" fontId=\"1\" fillId=\"2\" borderId=\"0\" xfId=\"0\" applyFont=\"1\" applyFill=\"1\"/></cellXfs><cellStyles count=\"1\"><cellStyle name=\"Normal\" xfId=\"0\" builtinId=\"0\"/></cellStyles></styleSheet>";}
}
