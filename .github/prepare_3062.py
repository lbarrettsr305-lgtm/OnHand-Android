from pathlib import Path
import runpy

# Preserve 3.0.61, including the visible New Location button and scrollable Options.
runpy.run_path('.github/prepare_3061.py', run_name='__main__')

p = Path('app/src/main/java/com/iceinventory/onhand/MainActivity.java')
s = p.read_text()

# Remember which export scope the user chose while Android's document picker is open.
old = '''    private String pendingExportFileName="";\n'''
new = '''    private String pendingExportFileName="";\n    private boolean pendingExportInternetOnly=false;\n'''
if old not in s:
    raise SystemExit('3.0.62 target missing: pending export field')
s = s.replace(old, new, 1)

# After export-format setup, let the user choose all items or internet-added items only.
old = '''        if(requestCode==REQ_EXPORT_FORMAT){\n            showExportDialog();\n            return;\n        }\n'''
new = '''        if(requestCode==REQ_EXPORT_FORMAT){\n            showExportScopeDialog();\n            return;\n        }\n'''
if old not in s:
    raise SystemExit('3.0.62 target missing: export format result')
s = s.replace(old, new, 1)

marker = '''    private void showExportDialog() {\n'''
method = '''    private void showExportScopeDialog() {\n        String[] choices={"All inventory items","Internet items only"};\n        new AlertDialog.Builder(this)\n                .setTitle("Export Items")\n                .setItems(choices,(d,which)->{\n                    boolean internetOnly=which==1;\n                    if(internetOnly&&internetItemCount()==0){toast("No internet items to export");return;}\n                    pendingExportInternetOnly=internetOnly;\n                    showExportDialog();\n                })\n                .setNegativeButton("Cancel",null)\n                .show();\n    }\n\n    private int internetItemCount() {\n        int count=0;\n        for(InventoryDb.Row r:db.items(sessionId)){\n            String d=r.description==null?"":r.description.trim();\n            if(d.startsWith(INTERNET_PREFIX))count++;\n        }\n        return count;\n    }\n\n    private String internetExportFileName(String name) {\n        String n=cleanTextName(name);\n        if(n.toLowerCase(Locale.US).endsWith(".txt"))n=n.substring(0,n.length()-4);\n        if(!n.toLowerCase(Locale.US).endsWith(" - internet items"))n+=" - Internet Items";\n        return n+".txt";\n    }\n\n'''
if marker not in s:
    raise SystemExit('3.0.62 target missing: export dialog marker')
s = s.replace(marker, method + marker, 1)

old = '''        name.setText(userExportFileName(exportUser,defaultName));\n        name.setSelection(name.getText().length());\n        new AlertDialog.Builder(this).setTitle("Export TXT").setMessage("Tab-delimited text file • choose where to save it.").setView(name)\n'''
new = '''        String exportName=userExportFileName(exportUser,defaultName);\n        if(pendingExportInternetOnly)exportName=internetExportFileName(exportName);\n        name.setText(exportName);\n        name.setSelection(name.getText().length());\n        String exportTitle=pendingExportInternetOnly?"Export Internet Items":"Export TXT";\n        String exportMessage=pendingExportInternetOnly?"Internet-added items only • tab-delimited TXT file.":"All inventory items • tab-delimited TXT file.";\n        new AlertDialog.Builder(this).setTitle(exportTitle).setMessage(exportMessage).setView(name)\n'''
if old not in s:
    raise SystemExit('3.0.62 target missing: export dialog filename/title')
s = s.replace(old, new, 1)

old = '''            os.write(TabTextUtils.exportRows(db.items(sessionId),prefs()).getBytes(StandardCharsets.UTF_8));\n            toast("Tab-delimited TXT exported");\n'''
new = '''            List<InventoryDb.Row> rows=db.items(sessionId);\n            if(pendingExportInternetOnly){\n                ArrayList<InventoryDb.Row> internetRows=new ArrayList<>();\n                for(InventoryDb.Row r:rows){\n                    String d=r.description==null?"":r.description.trim();\n                    if(d.startsWith(INTERNET_PREFIX))internetRows.add(r);\n                }\n                rows=internetRows;\n            }\n            os.write(TabTextUtils.exportRows(rows,prefs()).getBytes(StandardCharsets.UTF_8));\n            toast(pendingExportInternetOnly?"Internet items exported":"Tab-delimited TXT exported");\n'''
if old not in s:
    raise SystemExit('3.0.62 target missing: write export rows')
s = s.replace(old, new, 1)

p.write_text(s)
print('Prepared iCE Onhand 3.0.62: separate Internet Items export + 3.0.61 responsive UI fixes')
