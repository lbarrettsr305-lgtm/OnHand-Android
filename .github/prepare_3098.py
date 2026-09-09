from pathlib import Path
import re

# Preserve the complete 3.0.97 package first.
base=Path('.github/prepare_3097.py')
exec(compile(base.read_text(),str(base),'exec'),{'__name__':'__main__','__file__':str(base)})

# -----------------------------------------------------------------------------
# 3.0.98
# 1) Use the verified Ice Inventory master logo (3070) in professional reports.
# 2) Put that logo on Verification, Combined Inventory, and Inventory Valuation.
# 3) Make the entire Combine User Batches screen vertically scrollable so no
#    source/result lines or report buttons are clipped/covered on smaller phones.
# -----------------------------------------------------------------------------

# ----- Combine User Batches: one full-page ScrollView -----
p=Path('app/src/main/java/com/iceinventory/onhand/BatchMergeActivity.java')
m=p.read_text()
new_oncreate=r'''    @Override public void onCreate(Bundle state){
        super.onCreate(state);
        LinearLayout root=new LinearLayout(this);root.setOrientation(LinearLayout.VERTICAL);root.setBackgroundColor(Color.rgb(8,24,27));
        ScrollView pageScroll=new ScrollView(this);pageScroll.setFillViewport(true);
        LinearLayout page=new LinearLayout(this);page.setOrientation(LinearLayout.VERTICAL);page.setPadding(dp(16),dp(16),dp(16),dp(28));page.setBackgroundColor(Color.rgb(8,24,27));
        TextView title=text("Combine User Batches",24,Color.rgb(255,215,0));page.addView(title);
        TextView master=text("MASTER REPORT USER: "+(savedMasterUserName().isEmpty()?"NOT SET":savedMasterUserName()),18,Color.rgb(255,215,0));master.setPadding(0,dp(8),0,dp(4));page.addView(master);
        TextView help=text("Select iCE OnHand batches or compatible external tab-delimited files. Recognizable Barcode and Quantity headers are accepted. Headerless external files are also accepted in Quantity | Barcode | Description | Price order. Filenames, extensions, store names and batch numbers are not required.",15,Color.WHITE);help.setPadding(0,dp(8),0,dp(12));page.addView(help);
        Button choose=button("Select Batch / Source Files");choose.setOnClickListener(v->chooseFiles());page.addView(choose,new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT,dp(54)));
        TextView resultsTitle=text("SELECTED FILES / VERIFICATION RESULTS",16,Color.rgb(255,215,0));resultsTitle.setPadding(0,dp(14),0,dp(4));page.addView(resultsTitle);
        status=text("No batch files selected.",16,Color.WHITE);status.setPadding(dp(2),dp(6),dp(2),dp(14));status.setTextIsSelectable(true);page.addView(status,new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT,ViewGroup.LayoutParams.WRAP_CONTENT));
        TextView reportsTitle=text("REPORT EXPORTS",16,Color.rgb(255,215,0));reportsTitle.setPadding(0,dp(8),0,dp(5));page.addView(reportsTitle);
        save=button("Export Combined Batch — TXT");save.setEnabled(false);save.setOnClickListener(v->saveCombined());page.addView(save,new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT,dp(54)));
        report=button("Export Verification Report — TXT");report.setEnabled(false);report.setOnClickListener(v->saveReport());LinearLayout.LayoutParams rp=new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT,dp(54));rp.setMargins(0,dp(8),0,0);page.addView(report,rp);
        excel=button("Export Professional Combined Report — Excel");excel.setEnabled(false);excel.setOnClickListener(v->saveProfessionalXlsx());LinearLayout.LayoutParams xp=new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT,dp(54));xp.setMargins(0,dp(8),0,0);page.addView(excel,xp);
        Button close=button("Back to Inventory");close.setOnClickListener(v->finish());LinearLayout.LayoutParams cp=new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT,dp(50));cp.setMargins(0,dp(10),0,0);page.addView(close,cp);
        pageScroll.addView(page,new ScrollView.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT,ViewGroup.LayoutParams.WRAP_CONTENT));
        root.addView(pageScroll,new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT,0,1));
        setContentView(root);
    }

'''
pat=r'''    @Override public void onCreate\(Bundle state\)\{.*?\n    \}\n\n(?=    private void chooseFiles\(\))'''
m,n=re.subn(pat,lambda x:new_oncreate,m,count=1,flags=re.S)
if n!=1:raise SystemExit('3.0.98 target missing: BatchMergeActivity onCreate')
p.write_text(m)

# ----- Professional combined Excel: correct logo on every worksheet -----
p=Path('app/src/main/java/com/iceinventory/onhand/ProfessionalCombinedXlsxWriter.java')
x=p.read_text()

# The old report writer referenced an older/wrong logo. Use only the verified master asset.
old='''            Bitmap b=BitmapFactory.decodeResource(context.getResources(),R.drawable.ice_inventory_logo_3066);\n            if(b==null)b=BitmapFactory.decodeResource(context.getResources(),R.drawable.ice_onhand_approved);\n            if(b==null)b=Bitmap.createBitmap(2,2,Bitmap.Config.ARGB_8888);'''
new='''            Bitmap b=BitmapFactory.decodeResource(context.getResources(),R.drawable.ice_inventory_master_3070);\n            if(b==null)throw new IllegalStateException("Verified Ice Inventory master logo unavailable");'''
if old not in x:raise SystemExit('3.0.98 target missing: old report logo selection')
x=x.replace(old,new,1)

# Package separate drawing relationships for sheet 2 and sheet 3, all sharing the verified image.
old='''        put(zip,"xl/worksheets/sheet2.xml",combinedSheet(reportName,masterUser,combined,createdAt));\n        put(zip,"xl/worksheets/sheet3.xml",valuationSheet(reportName,masterUser,combined,createdAt));\n        zip.finish();'''
new='''        put(zip,"xl/worksheets/sheet2.xml",combinedSheet(reportName,masterUser,combined,createdAt));\n        put(zip,"xl/worksheets/_rels/sheet2.xml.rels",sheetDrawingRels("drawing2.xml"));\n        put(zip,"xl/drawings/drawing2.xml",drawingCompact());\n        put(zip,"xl/drawings/_rels/drawing2.xml.rels",drawingRels());\n        put(zip,"xl/worksheets/sheet3.xml",valuationSheet(reportName,masterUser,combined,createdAt));\n        put(zip,"xl/worksheets/_rels/sheet3.xml.rels",sheetDrawingRels("drawing3.xml"));\n        put(zip,"xl/drawings/drawing3.xml",drawingCompact());\n        put(zip,"xl/drawings/_rels/drawing3.xml.rels",drawingRels());\n        zip.finish();'''
if old not in x:raise SystemExit('3.0.98 target missing: sheet2/sheet3 package block')
x=x.replace(old,new,1)

# Combined Inventory: reserve left side for logo and attach drawing.
x=x.replace('<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">','<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">',1)
x=x.replace('rowStart(x,1,26);textCell(x,"A1","Ice Inventory LLC - Combined Inventory",1);rowEnd(x);','rowStart(x,1,26);textCell(x,"C1","Ice Inventory LLC - Combined Inventory",1);rowEnd(x);',1)
x=x.replace('rowStart(x,2,20);textCell(x,"A2","Report: "+clean(reportName)+"   |   Master Report User: "+clean(masterUser)+"   |   Created: "+when,6);rowEnd(x);','rowStart(x,2,20);textCell(x,"C2","Report: "+clean(reportName)+"   |   Master Report User: "+clean(masterUser)+"   |   Created: "+when,6);rowEnd(x);',1)
x=x.replace('<mergeCells count="2"><mergeCell ref="A1:D1"/><mergeCell ref="A2:D2"/></mergeCells>','<mergeCells count="2"><mergeCell ref="C1:D1"/><mergeCell ref="C2:D2"/></mergeCells>',1)
# Add drawing to the first non-verification worksheet close (combined sheet).
needle='''        x.append("<pageSetup orientation=\\\"landscape\\\" fitToWidth=\\\"1\\\" fitToHeight=\\\"0\\\" paperSize=\\\"9\\\"/>");\n        x.append("</worksheet>");\n        return x.toString();\n    }\n\n    private static String valuationSheet'''
replacement='''        x.append("<pageSetup orientation=\\\"landscape\\\" fitToWidth=\\\"1\\\" fitToHeight=\\\"0\\\" paperSize=\\\"9\\\"/>");\n        x.append("<drawing r:id=\\\"rId1\\\"/>");\n        x.append("</worksheet>");\n        return x.toString();\n    }\n\n    private static String valuationSheet'''
if needle not in x:raise SystemExit('3.0.98 target missing: combined sheet close')
x=x.replace(needle,replacement,1)

# Valuation sheet: r namespace, logo space, and drawing.
# This is the second worksheet literal without r namespace after the combined replacement above.
x=x.replace('<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">','<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">',1)
x=x.replace('rowStart(x,1,26);textCell(x,"A1","Ice Inventory LLC - Total Inventory Valuation",1);rowEnd(x);','rowStart(x,1,26);textCell(x,"C1","Ice Inventory LLC - Total Inventory Valuation",1);rowEnd(x);',1)
x=x.replace('rowStart(x,2,20);textCell(x,"A2","Report: "+clean(reportName)+"   |   Master Report User: "+clean(masterUser)+"   |   Created: "+when,6);rowEnd(x);','rowStart(x,2,20);textCell(x,"C2","Report: "+clean(reportName)+"   |   Master Report User: "+clean(masterUser)+"   |   Created: "+when,6);rowEnd(x);',1)
x=x.replace('<mergeCells count="3"><mergeCell ref="A1:E1"/><mergeCell ref="A2:E2"/><mergeCell ref="A3:E3"/></mergeCells>','<mergeCells count="3"><mergeCell ref="C1:E1"/><mergeCell ref="C2:E2"/><mergeCell ref="A3:E3"/></mergeCells>',1)
# Add drawing before valuation worksheet closes; use the last matching pageSetup/close block.
old_close='''        x.append("<pageSetup orientation=\\\"landscape\\\" fitToWidth=\\\"1\\\" fitToHeight=\\\"0\\\" paperSize=\\\"9\\\"/>");\n        x.append("</worksheet>");\n        return x.toString();\n    }\n\n    private static double parseMoney'''
new_close='''        x.append("<pageSetup orientation=\\\"landscape\\\" fitToWidth=\\\"1\\\" fitToHeight=\\\"0\\\" paperSize=\\\"9\\\"/>");\n        x.append("<drawing r:id=\\\"rId1\\\"/>");\n        x.append("</worksheet>");\n        return x.toString();\n    }\n\n    private static double parseMoney'''
if old_close not in x:raise SystemExit('3.0.98 target missing: valuation sheet close')
x=x.replace(old_close,new_close,1)

# Content types must know all drawing parts.
old='''                "<Override PartName=\\\"/xl/drawings/drawing1.xml\\\" ContentType=\\\"application/vnd.openxmlformats-officedocument.drawing+xml\\\"/>"+\n'''
new=old+'''                "<Override PartName=\\\"/xl/drawings/drawing2.xml\\\" ContentType=\\\"application/vnd.openxmlformats-officedocument.drawing+xml\\\"/>"+\n                "<Override PartName=\\\"/xl/drawings/drawing3.xml\\\" ContentType=\\\"application/vnd.openxmlformats-officedocument.drawing+xml\\\"/>"+\n'''
if old not in x:raise SystemExit('3.0.98 target missing: drawing1 content type')
x=x.replace(old,new,1)

# Add reusable sheet drawing rel + compact logo anchor for data sheets.
marker='''    private static String drawingRels(){return '''
helpers='''    private static String sheetDrawingRels(String drawingName){return "<?xml version=\\\"1.0\\\" encoding=\\\"UTF-8\\\"?><Relationships xmlns=\\\"http://schemas.openxmlformats.org/package/2006/relationships\\\"><Relationship Id=\\\"rId1\\\" Type=\\\"http://schemas.openxmlformats.org/officeDocument/2006/relationships/drawing\\\" Target=\\\"../drawings/"+drawingName+"\\\"/></Relationships>";}\n\n    private static String drawingCompact(){\n        return "<?xml version=\\\"1.0\\\" encoding=\\\"UTF-8\\\"?>"+\n                "<xdr:wsDr xmlns:xdr=\\\"http://schemas.openxmlformats.org/drawingml/2006/spreadsheetDrawing\\\" xmlns:a=\\\"http://schemas.openxmlformats.org/drawingml/2006/main\\\" xmlns:r=\\\"http://schemas.openxmlformats.org/officeDocument/2006/relationships\\\">"+\n                "<xdr:twoCellAnchor editAs=\\\"oneCell\\\"><xdr:from><xdr:col>0</xdr:col><xdr:colOff>0</xdr:colOff><xdr:row>0</xdr:row><xdr:rowOff>0</xdr:rowOff></xdr:from><xdr:to><xdr:col>2</xdr:col><xdr:colOff>0</xdr:colOff><xdr:row>2</xdr:row><xdr:rowOff>0</xdr:rowOff></xdr:to>"+\n                "<xdr:pic><xdr:nvPicPr><xdr:cNvPr id=\\\"1\\\" name=\\\"Ice Inventory Logo\\\"/><xdr:cNvPicPr/></xdr:nvPicPr><xdr:blipFill><a:blip r:embed=\\\"rId1\\\"/><a:stretch><a:fillRect/></a:stretch></xdr:blipFill><xdr:spPr><a:xfrm/><a:prstGeom prst=\\\"rect\\\"><a:avLst/></a:prstGeom></xdr:spPr></xdr:pic><xdr:clientData/></xdr:twoCellAnchor></xdr:wsDr>";\n    }\n\n'''
if marker not in x:raise SystemExit('3.0.98 target missing: drawingRels marker')
x=x.replace(marker,helpers+marker,1)
p.write_text(x)

# Version package and visible labels.
p=Path('app/src/main/java/com/iceinventory/onhand/MainActivity.java')
s=p.read_text().replace('Onhand Inventory 3.0.97','Onhand Inventory 3.0.98')
if 'Onhand Inventory 3.0.98' not in s:raise SystemExit('3.0.98 target missing: visible version')
p.write_text(s)
p=Path('app/build.gradle')
g=p.read_text().replace('versionCode 30097','versionCode 30098',1).replace("versionName '3.0.97'","versionName '3.0.98'",1)
if 'versionCode 30098' not in g or "versionName '3.0.98'" not in g:raise SystemExit('3.0.98 target missing: Gradle version')
p.write_text(g)
p=Path('app/src/main/AndroidManifest.xml')
a=p.read_text().replace('iCE Onhand 3.0.97','iCE Onhand 3.0.98')
if 'iCE Onhand 3.0.98' not in a:raise SystemExit('3.0.98 target missing: manifest version')
p.write_text(a)

# Regression checks.
merge=Path('app/src/main/java/com/iceinventory/onhand/BatchMergeActivity.java').read_text()
xlsx=Path('app/src/main/java/com/iceinventory/onhand/ProfessionalCombinedXlsxWriter.java').read_text()
checks={
    'full page scrolling':'ScrollView pageScroll=new ScrollView(this)' in merge and 'status.setTextIsSelectable(true)' in merge,
    'no nested results weight panel':'new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT,0,1)' not in merge.split('status=text',1)[1].split('save=button',1)[0],
    'report buttons remain reachable':'REPORT EXPORTS' in merge and 'Export Professional Combined Report — Excel' in merge,
    'verified master logo':'R.drawable.ice_inventory_master_3070' in xlsx,
    'old wrong report logo removed':'R.drawable.ice_inventory_logo_3066' not in xlsx,
    'sheet2 logo relationship':'sheet2.xml.rels' in xlsx and 'drawing2.xml' in xlsx,
    'sheet3 logo relationship':'sheet3.xml.rels' in xlsx and 'drawing3.xml' in xlsx,
    'all three worksheet drawings':xlsx.count('<drawing r:id=\\"rId1\\"/>')>=3,
    'valuation preserved':'Grand Total Inventory Value' in xlsx and 'Inventory Valuation' in xlsx,
    'headerless preserved':'looksLikeHeaderlessStandard' in merge,
    'master user preserved':'MASTER REPORT USER:' in merge,
}
missing=[k for k,v in checks.items() if not v]
if missing:raise SystemExit('3.0.98 verification failed: '+', '.join(missing))
print('Prepared iCE Onhand 3.0.98: verified master logo on all combined Excel sheets + fully scrollable combine screen')
