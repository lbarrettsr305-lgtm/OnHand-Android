#!/usr/bin/env python3
from pathlib import Path
import runpy

script_dir = Path(__file__).resolve().parent
root = script_dir.parent if script_dir.name == ".github" else script_dir
workflow = root / ".github/workflows/build-apk.yml"

# Recreate the tested 3.0.214 file-picker handoff, then add format selection
# directly to the Master import menu.
w = workflow.read_text()
for new, old in [
    ("Prepare and verify 3.0.215 import format chooser", "Prepare and verify 3.0.214 import flow fix"),
    (".github/prepare_30215.py", ".github/prepare_30214.py"),
    ("iCE-Onhand-Inventory-3.0.215", "iCE-Onhand-Inventory-3.0.214"),
]:
    if new not in w:
        raise SystemExit("3.0.215 workflow seed missing: " + new)
    w = w.replace(new, old)
workflow.write_text(w)
runpy.run_path(str(root / ".github/prepare_30214.py"), run_name="__main__")

w = workflow.read_text()
for old, new in [
    ("Prepare and verify 3.0.214 import flow fix", "Prepare and verify 3.0.215 import format chooser"),
    (".github/prepare_30214.py", ".github/prepare_30215.py"),
    ("iCE-Onhand-Inventory-3.0.214", "iCE-Onhand-Inventory-3.0.215"),
]:
    if old not in w:
        raise SystemExit("3.0.214 workflow marker missing: " + old)
    w = w.replace(old, new)
workflow.write_text(w)

main = root / "app/src/main/java/com/iceinventory/onhand/MainActivity.java"
s = main.read_text()
start = s.find("    private void showImportMenu() {")
end = s.find("\n    private void startImportFormatFlow()", start)
if start < 0 or end < 0:
    raise SystemExit("Import menu method boundaries missing")
menu = s[start:end]
if menu.count("else importCsv();") != 1:
    raise SystemExit("Shared User import menu action missing or ambiguous")
menu = menu.replace("else importCsv();", "else showStandardImportFormatDialog();", 1)
s = s[:start] + menu + s[end:]

anchor = "    private void startImportFormatFlow() {"
dialog = '''    private void showStandardImportFormatDialog(){
        String[] choices={"Use Saved Format","Fleet Feet — Barcode, Item Number, Description, Size","Victoria — Qty, Barcode, Description, Item Number, Location","Generic POS — Qty, Barcode, Description, Price"};
        new AlertDialog.Builder(this).setTitle("Choose Import File Format")
                .setMessage("Choose the column layout in your file. The file picker opens next.")
                .setItems(choices,(d,which)->{
                    String order=null;
                    if(which==1)order="barcode,item_number,description,size";
                    else if(which==2)order="quantity,barcode,description,item_number,location";
                    else if(which==3)order="quantity,barcode,description,price";
                    if(order!=null)prefs().edit().putString("import_field_order",order).apply();
                    importCsv();
                }).setNegativeButton("Cancel",null).show();
    }

'''
if s.count(anchor) != 1:
    raise SystemExit("Import flow insertion point missing or ambiguous")
s = s.replace(anchor, dialog + anchor, 1)

fmt_path = root / "app/src/main/java/com/iceinventory/onhand/FormatConfigActivity.java"
f = fmt_path.read_text()
old_help = '"Choose and save the preset matching your file here. To import, return Home, tap START / IMPORT, choose Shared User / Standard TXT File, then select the customer file. Fleet Feet uses Barcode, Item Number, Description, Size. CSV and tab-delimited TXT are supported.";'
new_help = '"Choose and save a column setup here, or choose a preset each time you import. To import, return Home, tap START / IMPORT, choose Shared User / Standard TXT File, select the matching format, then choose the customer file. CSV and tab-delimited TXT are supported.";'
if f.count(old_help) != 1:
    raise SystemExit("Import setup directions missing or ambiguous")
f = f.replace(old_help, new_help, 1)
fmt_path.write_text(f)

gradle = root / "app/build.gradle"
g = gradle.read_text()
if "versionCode 30214" not in g or "versionName '3.0.214'" not in g:
    raise SystemExit("3.0.214 Gradle version missing")
gradle.write_text(g.replace("versionCode 30214", "versionCode 30215", 1).replace("versionName '3.0.214'", "versionName '3.0.215'", 1))

manifest = root / "app/src/main/AndroidManifest.xml"
m = manifest.read_text()
if m.count("iCE Onhand 3.0.214") != 1:
    raise SystemExit("3.0.214 app label missing")
manifest.write_text(m.replace("iCE Onhand 3.0.214", "iCE Onhand 3.0.215", 1))

if s.count("Onhand Inventory 3.0.214") != 1:
    raise SystemExit("3.0.214 home label missing")
s = s.replace("Onhand Inventory 3.0.214", "Onhand Inventory 3.0.215", 1)
main.write_text(s)

checks = {
    "import format selection is in the import menu": "else showStandardImportFormatDialog();" in menu,
    "presets map to supported columns": all(x in dialog for x in ["barcode,item_number,description,size", "quantity,barcode,description,item_number,location", "quantity,barcode,description,price"]),
    "file picker opens after format choice": "importCsv();" in dialog,
    "counter imports use saved shared format": "if(!hasAdminAccess()){importCsv();return;}" in menu,
    "Fleet Feet setup remains available": 'String[] fields={"barcode","item_number","description","size"};' in f,
    "version labels": "versionName '3.0.215'" in gradle.read_text() and "iCE Onhand 3.0.215" in manifest.read_text() and "Onhand Inventory 3.0.215" in s,
    "workflow points to release": ".github/prepare_30215.py" in workflow.read_text() and "3.0.215" in workflow.read_text(),
}
failed = [name for name, passed in checks.items() if not passed]
if failed:
    raise SystemExit("3.0.215 validation failed: " + ", ".join(failed))
print("Prepared iCE OnHand 3.0.215: choose import format in the import flow, then open the customer file.")
