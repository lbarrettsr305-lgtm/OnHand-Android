from pathlib import Path
import re

# Prepare the complete 3.0.96 master-user / professional report feature first.
base=Path('.github/prepare_3096.py')
exec(compile(base.read_text(),str(base),'exec'),{'__name__':'__main__','__file__':str(base)})

p=Path('app/src/main/java/com/iceinventory/onhand/ProfessionalCombinedXlsxWriter.java')
s=p.read_text()

# Add the third workbook sheet containing line-by-line inventory valuation.
old='''        put(zip,"xl/worksheets/sheet2.xml",combinedSheet(reportName,masterUser,combined,createdAt));\n        zip.finish();'''
new='''        put(zip,"xl/worksheets/sheet2.xml",combinedSheet(reportName,masterUser,combined,createdAt));\n        put(zip,"xl/worksheets/sheet3.xml",valuationSheet(reportName,masterUser,combined,createdAt));\n        zip.finish();'''
if old not in s:raise SystemExit('3.0.96 valuation target missing: sheet2 write')
s=s.replace(old,new,1)

# Insert the professional valuation report before the logo helper.
marker='''    private static byte[] logoPng(Context context){\n'''
valuation='''    private static String valuationSheet(String reportName,String masterUser,List<CombinedRow> rows,Date createdAt){\n        String when=new SimpleDateFormat("yyyy-MM-dd HH:mm:ss",Locale.US).format(createdAt);\n        StringBuilder x=new StringBuilder(Math.max(12000,rows.size()*240));\n        x.append("<?xml version=\\\"1.0\\\" encoding=\\\"UTF-8\\\" standalone=\\\"yes\\\"?>");\n        x.append("<worksheet xmlns=\\\"http://schemas.openxmlformats.org/spreadsheetml/2006/main\\\">");\n        x.append("<sheetViews><sheetView workbookViewId=\\\"0\\\"><pane ySplit=\\\"4\\\" topLeftCell=\\\"A5\\\" activePane=\\\"bottomLeft\\\" state=\\\"frozen\\\"/></sheetView></sheetViews>");\n        x.append("<cols><col min=\\\"1\\\" max=\\\"1\\\" width=\\\"14\\\" customWidth=\\\"1\\\"/><col min=\\\"2\\\" max=\\\"2\\\" width=\\\"22\\\" customWidth=\\\"1\\\"/><col min=\\\"3\\\" max=\\\"3\\\" width=\\\"48\\\" customWidth=\\\"1\\\"/><col min=\\\"4\\\" max=\\\"4\\\" width=\\\"16\\\" customWidth=\\\"1\\\"/><col min=\\\"5\\\" max=\\\"5\\\" width=\\\"20\\\" customWidth=\\\"1\\\"/></cols><sheetData>");\n        rowStart(x,1,26);textCell(x,"A1","Ice Inventory LLC - Total Inventory Valuation",1);rowEnd(x);\n        rowStart(x,2,20);textCell(x,"A2","Report: "+clean(reportName)+"   |   Master Report User: "+clean(masterUser)+"   |   Created: "+when,6);rowEnd(x);\n        rowStart(x,3,20);textCell(x,"A3","Extended Value = Quantity × Price. Missing or non-numeric prices are valued at $0.00 and should be reviewed.",6);rowEnd(x);\n        rowStart(x,4,22);textCell(x,"A4","Quantity",3);textCell(x,"B4","Barcode",3);textCell(x,"C4","Description",3);textCell(x,"D4","Price",3);textCell(x,"E4","Extended Value",3);rowEnd(x);\n        int r=5;double grand=0.0;int missingPrices=0;\n        for(CombinedRow row:rows){\n            double price=parseMoney(row.price);\n            if(clean(row.price).isEmpty()||Double.isNaN(price)){price=0.0;missingPrices++;}\n            double extended=row.quantity*price;grand+=extended;\n            rowStart(x,r,20);numberCell(x,"A"+r,row.quantity,8);textCell(x,"B"+r,clean(row.barcode),0);textCell(x,"C"+r,clean(row.description),0);moneyCell(x,"D"+r,price,10);moneyCell(x,"E"+r,extended,10);rowEnd(x);r++;\n        }\n        int totalRow=r+1;\n        rowStart(x,totalRow,24);textCell(x,"D"+totalRow,"Grand Total Inventory Value",4);moneyCell(x,"E"+totalRow,grand,11);rowEnd(x);\n        int reviewRow=totalRow+1;\n        rowStart(x,reviewRow,20);textCell(x,"D"+reviewRow,"Lines Requiring Price Review",4);numberCell(x,"E"+reviewRow,missingPrices,8);rowEnd(x);\n        x.append("</sheetData><mergeCells count=\\\"3\\\"><mergeCell ref=\\\"A1:E1\\\"/><mergeCell ref=\\\"A2:E2\\\"/><mergeCell ref=\\\"A3:E3\\\"/></mergeCells>");\n        x.append("<autoFilter ref=\\\"A4:E").append(Math.max(4,r-1)).append("\\\"/>");\n        x.append("<pageMargins left=\\\"0.35\\\" right=\\\"0.35\\\" top=\\\"0.5\\\" bottom=\\\"0.5\\\" header=\\\"0.2\\\" footer=\\\"0.2\\\"/>");\n        x.append("<pageSetup orientation=\\\"landscape\\\" fitToWidth=\\\"1\\\" fitToHeight=\\\"0\\\" paperSize=\\\"9\\\"/>");\n        x.append("</worksheet>");\n        return x.toString();\n    }\n\n    private static double parseMoney(String value){\n        String v=clean(value);if(v.isEmpty())return Double.NaN;\n        try{return Double.parseDouble(v.replace("$","").replace(",","").trim());}catch(Exception e){return Double.NaN;}\n    }\n\n'''
if marker not in s:raise SystemExit('3.0.96 valuation target missing: logo helper')
s=s.replace(marker,valuation+marker,1)

# Add numeric currency-cell support. Price and extended value remain true Excel numbers.
old='''    private static void numberCell(StringBuilder x,String ref,long value,int style){\n        x.append("<c r=\\\"").append(ref).append("\\\"");if(style>0)x.append(" s=\\\"").append(style).append("\\\"");x.append("><v>").append(value).append("</v></c>");\n    }\n\n'''
new='''    private static void numberCell(StringBuilder x,String ref,long value,int style){\n        x.append("<c r=\\\"").append(ref).append("\\\"");if(style>0)x.append(" s=\\\"").append(style).append("\\\"");x.append("><v>").append(value).append("</v></c>");\n    }\n    private static void moneyCell(StringBuilder x,String ref,double value,int style){\n        x.append("<c r=\\\"").append(ref).append("\\\"");if(style>0)x.append(" s=\\\"").append(style).append("\\\"");x.append("><v>").append(String.format(Locale.US,"%.2f",value)).append("</v></c>");\n    }\n\n'''
if old not in s:raise SystemExit('3.0.96 valuation target missing: number cell helper')
s=s.replace(old,new,1)

# Workbook package now contains three worksheets.
old='''                "<Override PartName=\\\"/xl/worksheets/sheet2.xml\\\" ContentType=\\\"application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml\\\"/>"+\n'''
new=old+'''                "<Override PartName=\\\"/xl/worksheets/sheet3.xml\\\" ContentType=\\\"application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml\\\"/>"+\n'''
if old not in s:raise SystemExit('3.0.96 valuation target missing: content types sheet2')
s=s.replace(old,new,1)

s,n=re.subn(r'''    private static String workbook\(\)\{return .*?;\}\n''','''    private static String workbook(){return "<?xml version=\\\"1.0\\\" encoding=\\\"UTF-8\\\"?><workbook xmlns=\\\"http://schemas.openxmlformats.org/spreadsheetml/2006/main\\\" xmlns:r=\\\"http://schemas.openxmlformats.org/officeDocument/2006/relationships\\\"><sheets><sheet name=\\\"Verification\\\" sheetId=\\\"1\\\" r:id=\\\"rId1\\\"/><sheet name=\\\"Combined Inventory\\\" sheetId=\\\"2\\\" r:id=\\\"rId2\\\"/><sheet name=\\\"Inventory Valuation\\\" sheetId=\\\"3\\\" r:id=\\\"rId3\\\"/></sheets></workbook>";}\n''',s,count=1)
if n!=1:raise SystemExit('3.0.96 valuation target missing: workbook')

s,n=re.subn(r'''    private static String workbookRels\(\)\{return .*?;\}\n''','''    private static String workbookRels(){return "<?xml version=\\\"1.0\\\" encoding=\\\"UTF-8\\\"?><Relationships xmlns=\\\"http://schemas.openxmlformats.org/package/2006/relationships\\\"><Relationship Id=\\\"rId1\\\" Type=\\\"http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet\\\" Target=\\\"worksheets/sheet1.xml\\\"/><Relationship Id=\\\"rId2\\\" Type=\\\"http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet\\\" Target=\\\"worksheets/sheet2.xml\\\"/><Relationship Id=\\\"rId3\\\" Type=\\\"http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet\\\" Target=\\\"worksheets/sheet3.xml\\\"/><Relationship Id=\\\"rId4\\\" Type=\\\"http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles\\\" Target=\\\"styles.xml\\\"/></Relationships>";}\n''',s,count=1)
if n!=1:raise SystemExit('3.0.96 valuation target missing: workbook rels')

# Currency formatting: styles 10 and 11 are normal and highlighted currency respectively.
old='''                "<styleSheet xmlns=\\\"http://schemas.openxmlformats.org/spreadsheetml/2006/main\\\">"+\n                "<fonts count=\\\"5\\\">"+\n'''
new='''                "<styleSheet xmlns=\\\"http://schemas.openxmlformats.org/spreadsheetml/2006/main\\\">"+\n                "<numFmts count=\\\"1\\\"><numFmt numFmtId=\\\"164\\\" formatCode=\\\"$#,##0.00\\\"/></numFmts>"+\n                "<fonts count=\\\"5\\\">"+\n'''
if old not in s:raise SystemExit('3.0.96 valuation target missing: style header')
s=s.replace(old,new,1)
s=s.replace('"<cellXfs count=\\\"10\\\">"+','"<cellXfs count=\\\"12\\\">"+',1)
old='''                "<xf numFmtId=\\\"0\\\" fontId=\\\"4\\\" fillId=\\\"3\\\" borderId=\\\"1\\\" xfId=\\\"0\\\" applyFont=\\\"1\\\" applyFill=\\\"1\\\" applyBorder=\\\"1\\\"/>"+\n                "</cellXfs>"+\n'''
new='''                "<xf numFmtId=\\\"0\\\" fontId=\\\"4\\\" fillId=\\\"3\\\" borderId=\\\"1\\\" xfId=\\\"0\\\" applyFont=\\\"1\\\" applyFill=\\\"1\\\" applyBorder=\\\"1\\\"/>"+\n                "<xf numFmtId=\\\"164\\\" fontId=\\\"0\\\" fillId=\\\"0\\\" borderId=\\\"1\\\" xfId=\\\"0\\\" applyNumberFormat=\\\"1\\\" applyBorder=\\\"1\\\"/>"+\n                "<xf numFmtId=\\\"164\\\" fontId=\\\"4\\\" fillId=\\\"3\\\" borderId=\\\"1\\\" xfId=\\\"0\\\" applyNumberFormat=\\\"1\\\" applyFont=\\\"1\\\" applyFill=\\\"1\\\" applyBorder=\\\"1\\\"/>"+\n                "</cellXfs>"+\n'''
if old not in s:raise SystemExit('3.0.96 valuation target missing: cell styles')
s=s.replace(old,new,1)

p.write_text(s)

# Final regression checks.
xlsx=p.read_text()
checks={
    'valuation worksheet packaged':'sheet3.xml' in xlsx and 'valuationSheet(reportName' in xlsx,
    'valuation sheet named':'Inventory Valuation' in xlsx,
    'requested columns':'Quantity' in xlsx and 'Barcode' in xlsx and 'Description' in xlsx and 'Price' in xlsx and 'Extended Value' in xlsx,
    'extended calculation':'double extended=row.quantity*price' in xlsx,
    'grand total':'Grand Total Inventory Value' in xlsx and 'grand+=extended' in xlsx,
    'currency format':'$#,##0.00' in xlsx and 'moneyCell' in xlsx,
    'missing price review':'Missing or non-numeric prices are valued at $0.00' in xlsx and 'Lines Requiring Price Review' in xlsx,
}
missing=[k for k,v in checks.items() if not v]
if missing:raise SystemExit('3.0.96 valuation verification failed: '+', '.join(missing))
print('Prepared iCE Onhand 3.0.96 valuation: Quantity + Barcode + Description + Price + Extended Value + Grand Total Inventory Value')
