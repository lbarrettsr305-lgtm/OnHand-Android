from pathlib import Path
import runpy

# Preserve all 3.0.72 behavior first, including safe Replace / Append / Cancel import.
runpy.run_path('.github/prepare_3072.py', run_name='__main__')

p = Path('app/src/main/java/com/iceinventory/onhand/MainActivity.java')
s = p.read_text()

# Track the new dedicated export scope while Android's document picker is open.
old = '''    private boolean pendingExportInternetOnly=false;\n'''
new = '''    private boolean pendingExportInternetOnly=false;\n    private boolean pendingExportLocationQuantityReport=false;\n'''
if old not in s:
    raise SystemExit('3.0.73 target missing: pending export field')
s = s.replace(old, new, 1)

# Add Location Quantity Report as its own export choice.
old = '''        String[] choices={"All inventory items","Internet items only"};\n        new AlertDialog.Builder(this)\n                .setTitle("Export Items")\n                .setItems(choices,(d,which)->{\n                    boolean internetOnly=which==1;\n                    if(internetOnly&&internetItemCount()==0){toast("No internet items to export");return;}\n                    pendingExportInternetOnly=internetOnly;\n                    showExportDialog();\n                })\n'''
new = '''        String[] choices={"All inventory items","Internet items only","Location Quantity Report"};\n        new AlertDialog.Builder(this)\n                .setTitle("Export Items")\n                .setItems(choices,(d,which)->{\n                    boolean internetOnly=which==1;\n                    boolean locationQuantityReport=which==2;\n                    if(internetOnly&&internetItemCount()==0){toast("No internet items to export");return;}\n                    pendingExportInternetOnly=internetOnly;\n                    pendingExportLocationQuantityReport=locationQuantityReport;\n                    showExportDialog();\n                })\n'''
if old not in s:
    raise SystemExit('3.0.73 target missing: export scope choices')
s = s.replace(old, new, 1)

# Add a clear separate filename for the location report.
marker = '''    private void showExportDialog() {\n'''
helper = '''    private String locationQuantityExportFileName(String name) {\n        String n=cleanTextName(name);\n        if(n.toLowerCase(Locale.US).endsWith(".txt"))n=n.substring(0,n.length()-4);\n        if(!n.toLowerCase(Locale.US).endsWith(" - location quantity"))n+=" - Location Quantity";\n        return n+".txt";\n    }\n\n    private String buildLocationQuantityReport(List<InventoryDb.Row> rows) {\n        java.util.TreeMap<String,Integer> totals=new java.util.TreeMap<>(String.CASE_INSENSITIVE_ORDER);\n        for(String loc:db.locations()){\n            String key=loc==null||loc.trim().isEmpty()?"Main":loc.trim();\n            totals.put(key,0);\n        }\n        int grandTotal=0;\n        for(InventoryDb.Row r:rows){\n            String key=r.location==null||r.location.trim().isEmpty()?"Main":r.location.trim();\n            int qty=r.quantity;\n            Integer current=totals.get(key);\n            totals.put(key,(current==null?0:current)+qty);\n            grandTotal+=qty;\n        }\n        StringBuilder out=new StringBuilder();\n        out.append("Location\\tQuantity\\r\\n");\n        for(java.util.Map.Entry<String,Integer> e:totals.entrySet()){\n            out.append(e.getKey().replace("\\t"," ").replace("\\r"," ").replace("\\n"," "))\n                    .append('\\t').append(e.getValue()).append("\\r\\n");\n        }\n        out.append("GRAND TOTAL\\t").append(grandTotal).append("\\r\\n");\n        return out.toString();\n    }\n\n'''
if marker not in s:
    raise SystemExit('3.0.73 target missing: export dialog marker')
s = s.replace(marker, helper + marker, 1)

# Give the new report its own save filename, title and explanation.
old = '''        String exportName=userExportFileName(exportUser,defaultName);\n        if(pendingExportInternetOnly)exportName=internetExportFileName(exportName);\n        name.setText(exportName);\n        name.setSelection(name.getText().length());\n        String exportTitle=pendingExportInternetOnly?"Export Internet Items":"Export TXT";\n        String exportMessage=pendingExportInternetOnly?"Internet-added items only • tab-delimited TXT file.":"All inventory items • tab-delimited TXT file.";\n'''
new = '''        String exportName=userExportFileName(exportUser,defaultName);\n        if(pendingExportInternetOnly)exportName=internetExportFileName(exportName);\n        if(pendingExportLocationQuantityReport)exportName=locationQuantityExportFileName(exportName);\n        name.setText(exportName);\n        name.setSelection(name.getText().length());\n        String exportTitle=pendingExportLocationQuantityReport?"Location Quantity Report":(pendingExportInternetOnly?"Export Internet Items":"Export TXT");\n        String exportMessage=pendingExportLocationQuantityReport?"Separate report • total quantity for each location plus a grand total.":(pendingExportInternetOnly?"Internet-added items only • tab-delimited TXT file.":"All inventory items • tab-delimited TXT file.");\n'''
if old not in s:
    raise SystemExit('3.0.73 target missing: export filename/title')
s = s.replace(old, new, 1)

# Write the location summary independently instead of the normal item-level export.
old = '''            List<InventoryDb.Row> rows=db.items(sessionId);\n            if(pendingExportInternetOnly){\n                ArrayList<InventoryDb.Row> internetRows=new ArrayList<>();\n                for(InventoryDb.Row r:rows){\n                    String d=r.description==null?"":r.description.trim();\n                    if(d.startsWith(INTERNET_PREFIX))internetRows.add(r);\n                }\n                rows=internetRows;\n            }\n            os.write(TabTextUtils.exportRows(rows,prefs()).getBytes(StandardCharsets.UTF_8));\n            toast(pendingExportInternetOnly?"Internet items exported":"Tab-delimited TXT exported");\n'''
new = '''            List<InventoryDb.Row> rows=db.items(sessionId);\n            if(pendingExportLocationQuantityReport){\n                os.write(buildLocationQuantityReport(rows).getBytes(StandardCharsets.UTF_8));\n                toast("Location quantity report exported");\n            } else {\n                if(pendingExportInternetOnly){\n                    ArrayList<InventoryDb.Row> internetRows=new ArrayList<>();\n                    for(InventoryDb.Row r:rows){\n                        String d=r.description==null?"":r.description.trim();\n                        if(d.startsWith(INTERNET_PREFIX))internetRows.add(r);\n                    }\n                    rows=internetRows;\n                }\n                os.write(TabTextUtils.exportRows(rows,prefs()).getBytes(StandardCharsets.UTF_8));\n                toast(pendingExportInternetOnly?"Internet items exported":"Tab-delimited TXT exported");\n            }\n'''
if old not in s:
    raise SystemExit('3.0.73 target missing: export writer')
s = s.replace(old, new, 1)

# Advance visible and package versions.
oldv = 'TextView app=text("Onhand Inventory 3.0.72",19,Color.WHITE,true);'
newv = 'TextView app=text("Onhand Inventory 3.0.73",19,Color.WHITE,true);'
if oldv not in s:
    raise SystemExit('3.0.73 target missing: visible version')
s = s.replace(oldv,newv,1)
p.write_text(s)

p = Path('app/build.gradle')
s = p.read_text().replace('versionCode 30072','versionCode 30073',1).replace("versionName '3.0.72'","versionName '3.0.73'",1)
if 'versionCode 30073' not in s or "versionName '3.0.73'" not in s:
    raise SystemExit('3.0.73 target missing: Gradle version')
p.write_text(s)

p = Path('app/src/main/AndroidManifest.xml')
s = p.read_text().replace('android:label="iCE Onhand 3.0.72"','android:label="iCE Onhand 3.0.73"',1)
p.write_text(s)

print('Prepared iCE Onhand 3.0.73: separate Location Quantity Report export with per-location totals and grand total')
