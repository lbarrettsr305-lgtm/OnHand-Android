package com.iceinventory.onhand;

import android.content.Context;
import android.graphics.Bitmap;
import android.graphics.BitmapFactory;

import java.io.ByteArrayOutputStream;
import java.io.IOException;
import java.io.OutputStream;
import java.nio.charset.StandardCharsets;
import java.text.SimpleDateFormat;
import java.util.Date;
import java.util.List;
import java.util.Locale;
import java.util.zip.ZipEntry;
import java.util.zip.ZipOutputStream;

/** Professional, dependency-free XLSX writer for combined batch reconciliation reports. */
public final class ProfessionalCombinedXlsxWriter {
    private ProfessionalCombinedXlsxWriter(){}

    public static final class SourceRow {
        public final String sourceType,userName,fileName;
        public final int rows;
        public final long quantity;
        public SourceRow(String sourceType,String userName,String fileName,int rows,long quantity){
            this.sourceType=sourceType==null?"":sourceType;
            this.userName=userName==null?"":userName;
            this.fileName=fileName==null?"":fileName;
            this.rows=rows;
            this.quantity=quantity;
        }
    }

    public static final class CombinedRow {
        public final String barcode,description,price;
        public final long quantity;
        public CombinedRow(String barcode,String description,String price,long quantity){
            this.barcode=barcode==null?"":barcode;
            this.description=description==null?"":description;
            this.price=price==null?"":price;
            this.quantity=quantity;
        }
    }

    public static void write(Context context,OutputStream output,String reportName,String masterUser,
                             List<SourceRow> sources,List<CombinedRow> combined,
                             long sourceTotal,long combinedTotal,boolean verified,Date createdAt) throws IOException {
        if(createdAt==null)createdAt=new Date();
        byte[] logo=logoPng(context);
        ZipOutputStream zip=new ZipOutputStream(output);
        put(zip,"[Content_Types].xml",contentTypes());
        put(zip,"_rels/.rels",rootRels());
        put(zip,"xl/workbook.xml",workbook());
        put(zip,"xl/_rels/workbook.xml.rels",workbookRels());
        put(zip,"xl/styles.xml",styles());
        put(zip,"xl/worksheets/sheet1.xml",verificationSheet(reportName,masterUser,sources,combined.size(),sourceTotal,combinedTotal,verified,createdAt));
        put(zip,"xl/worksheets/_rels/sheet1.xml.rels",verificationSheetRels());
        put(zip,"xl/drawings/drawing1.xml",drawing());
        put(zip,"xl/drawings/_rels/drawing1.xml.rels",drawingRels());
        putBytes(zip,"xl/media/image1.png",logo);
        put(zip,"xl/worksheets/sheet2.xml",combinedSheet(reportName,masterUser,combined,createdAt));
        zip.finish();
        zip.flush();
    }

    private static String verificationSheet(String reportName,String masterUser,List<SourceRow> sources,
                                            int uniqueBarcodes,long sourceTotal,long combinedTotal,
                                            boolean verified,Date createdAt){
        String when=new SimpleDateFormat("yyyy-MM-dd HH:mm:ss",Locale.US).format(createdAt);
        long difference=combinedTotal-sourceTotal;
        StringBuilder x=new StringBuilder(16000);
        x.append("<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"yes\"?>");
        x.append("<worksheet xmlns=\"http://schemas.openxmlformats.org/spreadsheetml/2006/main\" xmlns:r=\"http://schemas.openxmlformats.org/officeDocument/2006/relationships\">");
        x.append("<sheetViews><sheetView workbookViewId=\"0\" showGridLines=\"0\"/></sheetViews>");
        x.append("<cols><col min=\"1\" max=\"1\" width=\"22\" customWidth=\"1\"/><col min=\"2\" max=\"2\" width=\"24\" customWidth=\"1\"/><col min=\"3\" max=\"3\" width=\"34\" customWidth=\"1\"/><col min=\"4\" max=\"4\" width=\"18\" customWidth=\"1\"/><col min=\"5\" max=\"5\" width=\"18\" customWidth=\"1\"/><col min=\"6\" max=\"6\" width=\"18\" customWidth=\"1\"/></cols>");
        x.append("<sheetData>");

        rowStart(x,1,30); textCell(x,"C1","Ice Inventory LLC",1); rowEnd(x);
        rowStart(x,2,24); textCell(x,"C2","Combined Batch Verification & Reconciliation Report",2); rowEnd(x);
        rowStart(x,3,8); rowEnd(x);

        rowStart(x,4,20); textCell(x,"A4","Report / Inventory",4); textCell(x,"B4",clean(reportName),0); rowEnd(x);
        rowStart(x,5,20); textCell(x,"A5","Master Report User",4); textCell(x,"B5",clean(masterUser),7); rowEnd(x);
        rowStart(x,6,20); textCell(x,"A6","Created At",4); textCell(x,"B6",when,0); rowEnd(x);
        rowStart(x,7,20); textCell(x,"A7","Verification Status",4); textCell(x,"B7",verified?"PASS - VERIFIED":"FAIL - NOT VERIFIED",verified?5:9); rowEnd(x);

        rowStart(x,9,22); textCell(x,"A9","Reconciliation Summary",2); rowEnd(x);
        rowStart(x,10,20); textCell(x,"A10","Selected Source Files",4); numberCell(x,"B10",sources.size(),8); rowEnd(x);
        int loaded=0,totalRows=0;for(SourceRow s:sources){loaded++;totalRows+=s.rows;}
        rowStart(x,11,20); textCell(x,"A11","Successfully Loaded Files",4); numberCell(x,"B11",loaded,8); rowEnd(x);
        rowStart(x,12,20); textCell(x,"A12","Source Rows",4); numberCell(x,"B12",totalRows,8); rowEnd(x);
        rowStart(x,13,20); textCell(x,"A13","Combined Unique Barcodes",4); numberCell(x,"B13",uniqueBarcodes,8); rowEnd(x);
        rowStart(x,14,20); textCell(x,"A14","Source Grand Total Quantity",4); numberCell(x,"B14",sourceTotal,8); rowEnd(x);
        rowStart(x,15,20); textCell(x,"A15","Combined Grand Total Quantity",4); numberCell(x,"B15",combinedTotal,8); rowEnd(x);
        rowStart(x,16,20); textCell(x,"A16","Difference",4); numberCell(x,"B16",difference,difference==0?5:9); rowEnd(x);

        rowStart(x,18,22); textCell(x,"A18","Source Batch Audit",2); rowEnd(x);
        rowStart(x,19,22); textCell(x,"A19","Source Type",3); textCell(x,"B19","User / Operator",3); textCell(x,"C19","Source File",3); textCell(x,"D19","Rows",3); textCell(x,"E19","Quantity",3); rowEnd(x);
        int r=20;
        for(SourceRow s:sources){
            rowStart(x,r,20);
            textCell(x,"A"+r,clean(s.sourceType),0);
            textCell(x,"B"+r,clean(s.userName),0);
            textCell(x,"C"+r,clean(s.fileName),0);
            numberCell(x,"D"+r,s.rows,8);
            numberCell(x,"E"+r,s.quantity,8);
            rowEnd(x);r++;
        }

        int noteTitle=r+2,noteRow=r+3,methodTitle=r+6,methodRow=r+7;
        rowStart(x,noteTitle,22);textCell(x,"A"+noteTitle,"Formal Verification Note",2);rowEnd(x);
        String note="Ice Inventory LLC certifies that this report was generated by the designated Master Report User using the source files listed above. The system verified that every selected source file shown as loaded was included in the calculation, matching barcodes were consolidated, and the Source Grand Total Quantity equals the Combined Grand Total Quantity when the report status is PASS. This verification confirms computational reconciliation of the selected electronic source files; it does not independently certify the physical accuracy of the underlying inventory counts.";
        rowStart(x,noteRow,78);textCell(x,"A"+noteRow,note,6);rowEnd(x);

        rowStart(x,methodTitle,22);textCell(x,"A"+methodTitle,"Verification Method",2);rowEnd(x);
        String method="1. Each selected file is validated as tab-delimited inventory data by its headers, not by its filename.  2. Barcode and Quantity columns are required; Description and Price are optional.  3. Every source row quantity is added to the source total.  4. Matching barcodes are summed into one combined quantity.  5. PASS requires all selected files to load successfully and the source and combined grand totals to match exactly.";
        rowStart(x,methodRow,72);textCell(x,"A"+methodRow,method,6);rowEnd(x);

        int finalRow=methodRow+3;
        rowStart(x,finalRow,24);textCell(x,"A"+finalRow,"FINAL RESULT",4);textCell(x,"B"+finalRow,verified?"PASS - ALL SELECTED SOURCE QUANTITIES INCLUDED AND TOTALS MATCH":"FAIL - RECONCILIATION NOT VERIFIED",verified?5:9);rowEnd(x);

        x.append("</sheetData>");
        x.append("<mergeCells count=\"7\">");
        x.append("<mergeCell ref=\"C1:F1\"/><mergeCell ref=\"C2:F2\"/><mergeCell ref=\"A9:F9\"/><mergeCell ref=\"A18:F18\"/>");
        x.append("<mergeCell ref=\"A").append(noteTitle).append(":F").append(noteTitle).append("\"/>");
        x.append("<mergeCell ref=\"A").append(noteRow).append(":F").append(noteRow).append("\"/>");
        x.append("<mergeCell ref=\"A").append(methodTitle).append(":F").append(methodTitle).append("\"/>");
        x.append("</mergeCells>");
        x.append("<pageMargins left=\"0.35\" right=\"0.35\" top=\"0.5\" bottom=\"0.5\" header=\"0.2\" footer=\"0.2\"/>");
        x.append("<pageSetup orientation=\"landscape\" fitToWidth=\"1\" fitToHeight=\"0\" paperSize=\"9\"/>");
        x.append("<drawing r:id=\"rId1\"/>");
        x.append("</worksheet>");
        return x.toString();
    }

    private static String combinedSheet(String reportName,String masterUser,List<CombinedRow> rows,Date createdAt){
        String when=new SimpleDateFormat("yyyy-MM-dd HH:mm:ss",Locale.US).format(createdAt);
        StringBuilder x=new StringBuilder(Math.max(10000,rows.size()*180));
        x.append("<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"yes\"?>");
        x.append("<worksheet xmlns=\"http://schemas.openxmlformats.org/spreadsheetml/2006/main\">");
        x.append("<sheetViews><sheetView workbookViewId=\"0\"><pane ySplit=\"4\" topLeftCell=\"A5\" activePane=\"bottomLeft\" state=\"frozen\"/></sheetView></sheetViews>");
        x.append("<cols><col min=\"1\" max=\"1\" width=\"14\" customWidth=\"1\"/><col min=\"2\" max=\"2\" width=\"22\" customWidth=\"1\"/><col min=\"3\" max=\"3\" width=\"48\" customWidth=\"1\"/><col min=\"4\" max=\"4\" width=\"16\" customWidth=\"1\"/></cols><sheetData>");
        rowStart(x,1,26);textCell(x,"A1","Ice Inventory LLC - Combined Inventory",1);rowEnd(x);
        rowStart(x,2,20);textCell(x,"A2","Report: "+clean(reportName)+"   |   Master Report User: "+clean(masterUser)+"   |   Created: "+when,6);rowEnd(x);
        rowStart(x,4,22);textCell(x,"A4","Quantity",3);textCell(x,"B4","Barcode",3);textCell(x,"C4","Description",3);textCell(x,"D4","Price",3);rowEnd(x);
        int r=5;
        for(CombinedRow row:rows){
            rowStart(x,r,20);numberCell(x,"A"+r,row.quantity,8);textCell(x,"B"+r,clean(row.barcode),0);textCell(x,"C"+r,clean(row.description),0);textCell(x,"D"+r,clean(row.price),0);rowEnd(x);r++;
        }
        x.append("</sheetData><mergeCells count=\"2\"><mergeCell ref=\"A1:D1\"/><mergeCell ref=\"A2:D2\"/></mergeCells>");
        x.append("<autoFilter ref=\"A4:D").append(Math.max(4,r-1)).append("\"/>");
        x.append("<pageMargins left=\"0.35\" right=\"0.35\" top=\"0.5\" bottom=\"0.5\" header=\"0.2\" footer=\"0.2\"/>");
        x.append("<pageSetup orientation=\"landscape\" fitToWidth=\"1\" fitToHeight=\"0\" paperSize=\"9\"/>");
        x.append("</worksheet>");
        return x.toString();
    }

    private static byte[] logoPng(Context context){
        try{
            Bitmap b=BitmapFactory.decodeResource(context.getResources(),R.drawable.ice_inventory_logo_3066);
            if(b==null)b=BitmapFactory.decodeResource(context.getResources(),R.drawable.ice_onhand_approved);
            if(b==null)b=Bitmap.createBitmap(2,2,Bitmap.Config.ARGB_8888);
            ByteArrayOutputStream out=new ByteArrayOutputStream();
            b.compress(Bitmap.CompressFormat.PNG,100,out);
            return out.toByteArray();
        }catch(Exception e){
            return new byte[]{(byte)0x89,0x50,0x4E,0x47,0x0D,0x0A,0x1A,0x0A};
        }
    }

    private static void rowStart(StringBuilder x,int row,int height){x.append("<row r=\"").append(row).append("\" ht=\"").append(height).append("\" customHeight=\"1\">");}
    private static void rowEnd(StringBuilder x){x.append("</row>");}

    private static void textCell(StringBuilder x,String ref,String value,int style){
        x.append("<c r=\"").append(ref).append("\" t=\"inlineStr\"");if(style>0)x.append(" s=\"").append(style).append("\"");x.append("><is><t xml:space=\"preserve\">").append(xml(value)).append("</t></is></c>");
    }
    private static void numberCell(StringBuilder x,String ref,long value,int style){
        x.append("<c r=\"").append(ref).append("\"");if(style>0)x.append(" s=\"").append(style).append("\"");x.append("><v>").append(value).append("</v></c>");
    }

    private static String clean(String s){return s==null?"":s.replace('\t',' ').replace('\r',' ').replace('\n',' ').trim();}
    private static String xml(String s){String v=s==null?"":s;return v.replace("&","&amp;").replace("<","&lt;").replace(">","&gt;").replace("\"","&quot;").replace("'","&apos;");}

    private static void put(ZipOutputStream zip,String name,String content) throws IOException {putBytes(zip,name,content.getBytes(StandardCharsets.UTF_8));}
    private static void putBytes(ZipOutputStream zip,String name,byte[] bytes) throws IOException {zip.putNextEntry(new ZipEntry(name));zip.write(bytes);zip.closeEntry();}

    private static String contentTypes(){
        return "<?xml version=\"1.0\" encoding=\"UTF-8\"?>"+
                "<Types xmlns=\"http://schemas.openxmlformats.org/package/2006/content-types\">"+
                "<Default Extension=\"rels\" ContentType=\"application/vnd.openxmlformats-package.relationships+xml\"/>"+
                "<Default Extension=\"xml\" ContentType=\"application/xml\"/>"+
                "<Default Extension=\"png\" ContentType=\"image/png\"/>"+
                "<Override PartName=\"/xl/workbook.xml\" ContentType=\"application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml\"/>"+
                "<Override PartName=\"/xl/worksheets/sheet1.xml\" ContentType=\"application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml\"/>"+
                "<Override PartName=\"/xl/worksheets/sheet2.xml\" ContentType=\"application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml\"/>"+
                "<Override PartName=\"/xl/styles.xml\" ContentType=\"application/vnd.openxmlformats-officedocument.spreadsheetml.styles+xml\"/>"+
                "<Override PartName=\"/xl/drawings/drawing1.xml\" ContentType=\"application/vnd.openxmlformats-officedocument.drawing+xml\"/>"+
                "</Types>";
    }

    private static String rootRels(){return "<?xml version=\"1.0\" encoding=\"UTF-8\"?><Relationships xmlns=\"http://schemas.openxmlformats.org/package/2006/relationships\"><Relationship Id=\"rId1\" Type=\"http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument\" Target=\"xl/workbook.xml\"/></Relationships>";}

    private static String workbook(){return "<?xml version=\"1.0\" encoding=\"UTF-8\"?><workbook xmlns=\"http://schemas.openxmlformats.org/spreadsheetml/2006/main\" xmlns:r=\"http://schemas.openxmlformats.org/officeDocument/2006/relationships\"><sheets><sheet name=\"Verification\" sheetId=\"1\" r:id=\"rId1\"/><sheet name=\"Combined Inventory\" sheetId=\"2\" r:id=\"rId2\"/></sheets></workbook>";}

    private static String workbookRels(){return "<?xml version=\"1.0\" encoding=\"UTF-8\"?><Relationships xmlns=\"http://schemas.openxmlformats.org/package/2006/relationships\"><Relationship Id=\"rId1\" Type=\"http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet\" Target=\"worksheets/sheet1.xml\"/><Relationship Id=\"rId2\" Type=\"http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet\" Target=\"worksheets/sheet2.xml\"/><Relationship Id=\"rId3\" Type=\"http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles\" Target=\"styles.xml\"/></Relationships>";}

    private static String verificationSheetRels(){return "<?xml version=\"1.0\" encoding=\"UTF-8\"?><Relationships xmlns=\"http://schemas.openxmlformats.org/package/2006/relationships\"><Relationship Id=\"rId1\" Type=\"http://schemas.openxmlformats.org/officeDocument/2006/relationships/drawing\" Target=\"../drawings/drawing1.xml\"/></Relationships>";}

    private static String drawingRels(){return "<?xml version=\"1.0\" encoding=\"UTF-8\"?><Relationships xmlns=\"http://schemas.openxmlformats.org/package/2006/relationships\"><Relationship Id=\"rId1\" Type=\"http://schemas.openxmlformats.org/officeDocument/2006/relationships/image\" Target=\"../media/image1.png\"/></Relationships>";}

    private static String drawing(){
        return "<?xml version=\"1.0\" encoding=\"UTF-8\"?>"+
                "<xdr:wsDr xmlns:xdr=\"http://schemas.openxmlformats.org/drawingml/2006/spreadsheetDrawing\" xmlns:a=\"http://schemas.openxmlformats.org/drawingml/2006/main\" xmlns:r=\"http://schemas.openxmlformats.org/officeDocument/2006/relationships\">"+
                "<xdr:twoCellAnchor editAs=\"oneCell\"><xdr:from><xdr:col>0</xdr:col><xdr:colOff>0</xdr:colOff><xdr:row>0</xdr:row><xdr:rowOff>0</xdr:rowOff></xdr:from><xdr:to><xdr:col>2</xdr:col><xdr:colOff>0</xdr:colOff><xdr:row>3</xdr:row><xdr:rowOff>0</xdr:rowOff></xdr:to>"+
                "<xdr:pic><xdr:nvPicPr><xdr:cNvPr id=\"1\" name=\"Ice Inventory Logo\"/><xdr:cNvPicPr/></xdr:nvPicPr><xdr:blipFill><a:blip r:embed=\"rId1\"/><a:stretch><a:fillRect/></a:stretch></xdr:blipFill><xdr:spPr><a:xfrm/><a:prstGeom prst=\"rect\"><a:avLst/></a:prstGeom></xdr:spPr></xdr:pic><xdr:clientData/></xdr:twoCellAnchor></xdr:wsDr>";
    }

    private static String styles(){
        return "<?xml version=\"1.0\" encoding=\"UTF-8\"?>"+
                "<styleSheet xmlns=\"http://schemas.openxmlformats.org/spreadsheetml/2006/main\">"+
                "<fonts count=\"5\">"+
                "<font><sz val=\"11\"/><name val=\"Calibri\"/></font>"+
                "<font><b/><color rgb=\"FFFFFFFF\"/><sz val=\"18\"/><name val=\"Calibri\"/></font>"+
                "<font><b/><color rgb=\"FF0B302B\"/><sz val=\"12\"/><name val=\"Calibri\"/></font>"+
                "<font><b/><color rgb=\"FFFFFFFF\"/><sz val=\"11\"/><name val=\"Calibri\"/></font>"+
                "<font><b/><sz val=\"11\"/><name val=\"Calibri\"/></font>"+
                "</fonts>"+
                "<fills count=\"6\"><fill><patternFill patternType=\"none\"/></fill><fill><patternFill patternType=\"gray125\"/></fill><fill><patternFill patternType=\"solid\"><fgColor rgb=\"FF0B302B\"/><bgColor indexed=\"64\"/></patternFill></fill><fill><patternFill patternType=\"solid\"><fgColor rgb=\"FFFFD700\"/><bgColor indexed=\"64\"/></patternFill></fill><fill><patternFill patternType=\"solid\"><fgColor rgb=\"FFF2F2F2\"/><bgColor indexed=\"64\"/></patternFill></fill><fill><patternFill patternType=\"solid\"><fgColor rgb=\"FFE2F0D9\"/><bgColor indexed=\"64\"/></patternFill></fill></fills>"+
                "<borders count=\"2\"><border><left/><right/><top/><bottom/><diagonal/></border><border><left style=\"thin\"><color rgb=\"FFD0D0D0\"/></left><right style=\"thin\"><color rgb=\"FFD0D0D0\"/></right><top style=\"thin\"><color rgb=\"FFD0D0D0\"/></top><bottom style=\"thin\"><color rgb=\"FFD0D0D0\"/></bottom><diagonal/></border></borders>"+
                "<cellStyleXfs count=\"1\"><xf numFmtId=\"0\" fontId=\"0\" fillId=\"0\" borderId=\"0\"/></cellStyleXfs>"+
                "<cellXfs count=\"10\">"+
                "<xf numFmtId=\"0\" fontId=\"0\" fillId=\"0\" borderId=\"0\" xfId=\"0\"/>"+
                "<xf numFmtId=\"0\" fontId=\"1\" fillId=\"2\" borderId=\"0\" xfId=\"0\" applyFont=\"1\" applyFill=\"1\"><alignment horizontal=\"center\" vertical=\"center\"/></xf>"+
                "<xf numFmtId=\"0\" fontId=\"2\" fillId=\"3\" borderId=\"1\" xfId=\"0\" applyFont=\"1\" applyFill=\"1\" applyBorder=\"1\"><alignment vertical=\"center\"/></xf>"+
                "<xf numFmtId=\"0\" fontId=\"3\" fillId=\"2\" borderId=\"1\" xfId=\"0\" applyFont=\"1\" applyFill=\"1\" applyBorder=\"1\"><alignment horizontal=\"center\" vertical=\"center\"/></xf>"+
                "<xf numFmtId=\"0\" fontId=\"4\" fillId=\"4\" borderId=\"1\" xfId=\"0\" applyFont=\"1\" applyFill=\"1\" applyBorder=\"1\"/>"+
                "<xf numFmtId=\"0\" fontId=\"4\" fillId=\"5\" borderId=\"1\" xfId=\"0\" applyFont=\"1\" applyFill=\"1\" applyBorder=\"1\"/>"+
                "<xf numFmtId=\"0\" fontId=\"0\" fillId=\"0\" borderId=\"1\" xfId=\"0\" applyBorder=\"1\"><alignment wrapText=\"1\" vertical=\"top\"/></xf>"+
                "<xf numFmtId=\"0\" fontId=\"4\" fillId=\"0\" borderId=\"0\" xfId=\"0\" applyFont=\"1\"/>"+
                "<xf numFmtId=\"0\" fontId=\"0\" fillId=\"0\" borderId=\"1\" xfId=\"0\" applyBorder=\"1\"><alignment horizontal=\"right\"/></xf>"+
                "<xf numFmtId=\"0\" fontId=\"4\" fillId=\"3\" borderId=\"1\" xfId=\"0\" applyFont=\"1\" applyFill=\"1\" applyBorder=\"1\"/>"+
                "</cellXfs>"+
                "<cellStyles count=\"1\"><cellStyle name=\"Normal\" xfId=\"0\" builtinId=\"0\"/></cellStyles></styleSheet>";
    }
}
