#!/usr/bin/env python3
from pathlib import Path
import runpy

root = Path(__file__).resolve().parent.parent
workflow = root / ".github/workflows/build-apk.yml"
w = workflow.read_text()
for old, new in [
    ("Prepare and verify 3.0.224 replacement location and export names", "Prepare and verify 3.0.222 clean Fleet Feet batch export"),
    (".github/prepare_30224.py", ".github/prepare_30222.py"),
    ("iCE-Onhand-Inventory-3.0.224", "iCE-Onhand-Inventory-3.0.222"),
]:
    if old not in w:
        raise SystemExit("3.0.224 workflow marker missing: " + old)
    w = w.replace(old, new)
workflow.write_text(w)
runpy.run_path(str(root / ".github/prepare_30222.py"), run_name="__main__")
w = workflow.read_text()
for old, new in [
    ("Prepare and verify 3.0.222 clean Fleet Feet batch export", "Prepare and verify 3.0.224 replacement location and export names"),
    (".github/prepare_30222.py", ".github/prepare_30224.py"),
    ("iCE-Onhand-Inventory-3.0.222", "iCE-Onhand-Inventory-3.0.224"),
]:
    if old not in w:
        raise SystemExit("3.0.222 workflow marker missing: " + old)
    w = w.replace(old, new)
workflow.write_text(w)

main = root / "app/src/main/java/com/iceinventory/onhand/MainActivity.java"
s = main.read_text()

def replace_once(old, new, label):
    global s
    if s.count(old) != 1:
        raise SystemExit(label + " point missing or ambiguous")
    s = s.replace(old, new, 1)

replace_once(
    '    private EditText locationScanInput;\n',
    '    private EditText locationScanInput;\n    private ArrayList<ImportedRow> pendingImportedRows;\n    private String pendingImportedName="";\n',
    "Pending import fields",
)
replace_once(
    '        if(locationDialog!=null){locationDialog.dismiss();locationDialog=null;locationScanInput=null;}\n        barcode.setText("");description.setText("");qty.setText("");\n',
    '        if(locationDialog!=null){locationDialog.dismiss();locationDialog=null;locationScanInput=null;}\n        if(pendingImportedRows!=null){finishPendingImport(n);return;}\n        barcode.setText("");description.setText("");qty.setText("");\n',
    "Import location submission",
)
finish_method = '''    private void finishPendingImport(String startingLocation){
        ArrayList<ImportedRow> rows=pendingImportedRows;
        String importedName=pendingImportedName;
        pendingImportedRows=null;pendingImportedName="";
        if(rows==null||rows.isEmpty())return;
        try {
            db.replaceSession(sessionId,importedName);
            sessionName=importedName;
            if(titleSession!=null)titleSession.setText(sessionName);
            for(ImportedRow row:rows){
                String rowLocation=row.location==null||row.location.trim().isEmpty()?startingLocation:row.location.trim();
                db.addLocation(rowLocation);
                db.addOrIncrementAt(sessionId,row.barcode,row.description,row.itemNumber,row.price,"",row.quantity,rowLocation,System.currentTimeMillis());
            }
            refreshLocations();refreshList();
            toast("Replaced current inventory with "+rows.size()+" rows: "+importedName);
            barcode.setText("");description.setText("");qty.setText("");
            focusBarcodeWithoutKeyboard();
        } catch(Exception e){showError("Import failed. Current inventory may be incomplete.",e);}
    }

'''
anchor = '    private String locationParent(String name){'
if s.count(anchor) != 1:
    raise SystemExit("Import completion insertion point missing or ambiguous")
s = s.replace(anchor, finish_method + anchor, 1)
replace_once(
    '        boolean changingLocation=confirmedLocationSession==sessionId&&!confirmedLocation.isEmpty();\n',
    '        boolean changingLocation=pendingImportedRows==null&&confirmedLocationSession==sessionId&&!confirmedLocation.isEmpty();\n',
    "Starting location prompt state",
)
replace_once(
    '        String title=confirmedLocationSession==sessionId&&!confirmedLocation.isEmpty()?"CHANGE COUNTING LOCATION":"1  SET COUNTING LOCATION";\n',
    '        String title=pendingImportedRows!=null?"SET STARTING LOCATION":(confirmedLocationSession==sessionId&&!confirmedLocation.isEmpty()?"CHANGE COUNTING LOCATION":"1  SET COUNTING LOCATION");\n',
    "Starting location prompt title",
)
replace_once(
    '            .setNegativeButton("Cancel",(d,w)->{locationDialog=null;locationScanInput=null;}).create();\n',
    '            .setNegativeButton("Cancel",(d,w)->{locationDialog=null;locationScanInput=null;if(pendingImportedRows!=null){pendingImportedRows=null;pendingImportedName="";}}).create();\n',
    "Cancel pending import",
)
replace_once(
    '                        row.location=field(fields,locationIndex);\n                        if(row.location.isEmpty())row.location="Main";\n',
    '                        row.location=field(fields,locationIndex);\n',
    "Preserve blank imported location",
)
old = '''            String importedName=importFileName(uri);
            db.replaceSession(sessionId,importedName);
            // A replacement import begins a new count: require the operator to
            // confirm its starting location instead of carrying the old one over.
            prefs().edit().remove(confirmedLocationKey(sessionId)).apply();
            confirmedLocation="";
            confirmedLocationSession=-1L;
            sessionName=importedName;
            if(titleSession!=null)titleSession.setText(sessionName);
            for(ImportedRow row:rows) {
                db.addLocation(row.location);
                db.addOrIncrementAt(sessionId,row.barcode,row.description,row.itemNumber,row.price,"",row.quantity,row.location,System.currentTimeMillis());
            }
            refreshLocations();refreshList();
            toast("Replaced current inventory with "+rows.size()+" rows: "+importedName);
            showLocationStep();
'''
new = '''            pendingImportedRows=rows;
            pendingImportedName=importFileName(uri);
            toast("Choose the starting location for this imported inventory.");
            showLocationStep();
'''
replace_once(old, new, "Delay replacement until location confirmation")
main.write_text(s)

replace_once(
    '    private String batchExportFileName(){String ext=pendingExportExcel?".xlsx":".txt";String user=safeFilePart(savedUserName());if(user.isEmpty())user="Counter";return "count"+user+"-Batch"+Math.max(1,pendingBatchNumber)+ext;}\n',
    '    private String batchExportFileName(){String ext=pendingExportExcel?".xlsx":".txt";String store=safeFilePart(sessionName);String user=safeFilePart(savedUserName());if(store.isEmpty())store="Inventory";if(user.isEmpty())user="Counter";return store+"-"+user+"-Batch"+String.format(Locale.US,"%02d",Math.max(1,pendingBatchNumber))+ext;}\n',
    "Store-user batch export filename",
)
replace_once(
    '    private String completeExportFileName(){String ext=pendingExportExcel?".xlsx":".txt";String store=safeFilePart(sessionName);String user=safeFilePart(savedUserName());if(store.isEmpty())store="Inventory";if(user.isEmpty())user="Counter";return "COMPLETED INVENTORY - "+user+" - "+store+"-"+String.format(Locale.US,"%02d",Math.max(1,pendingBatchNumber))+ext;}\n',
    '    private String completeExportFileName(){String ext=pendingExportExcel?".xlsx":".txt";String store=safeFilePart(sessionName);String user=safeFilePart(savedUserName());if(store.isEmpty())store="Inventory";if(user.isEmpty())user="Counter";return store+"-"+user+"-"+String.format(Locale.US,"%02d",Math.max(1,pendingBatchNumber))+ext;}\n',
    "Store-user complete export filename",
)
main.write_text(s)

gradle = root / "app/build.gradle"
g = gradle.read_text()
if "versionCode 30222" not in g or "versionName '3.0.222'" not in g:
    raise SystemExit("3.0.222 Gradle version missing")
gradle.write_text(g.replace("versionCode 30222", "versionCode 30224", 1).replace("versionName '3.0.222'", "versionName '3.0.224'", 1))

manifest = root / "app/src/main/AndroidManifest.xml"
m = manifest.read_text()
if m.count("iCE Onhand 3.0.222") != 1:
    raise SystemExit("3.0.222 manifest label missing or ambiguous")
manifest.write_text(m.replace("iCE Onhand 3.0.222", "iCE Onhand 3.0.224", 1))

s = main.read_text()
if s.count("Onhand Inventory 3.0.222") != 1:
    raise SystemExit("3.0.222 home label missing or ambiguous")
main.write_text(s.replace("Onhand Inventory 3.0.222", "Onhand Inventory 3.0.224", 1))

print("Prepared iCE OnHand 3.0.224: replacement imports wait for a starting location; blank-location rows use it; exports use store-user-batch filenames.")
