#!/usr/bin/env python3
"""OnHand 3.0.233: support monthly Fleet Feet RGIS customer files as delivered."""
from pathlib import Path
import runpy

root=Path(__file__).resolve().parent.parent
workflow=root/".github/workflows/build-apk.yml"
w=workflow.read_text()
for n,o,expected in [
    ("Prepare and verify 3.0.233 recurring Fleet Feet RGIS customer import","Prepare and verify 3.0.232 Victoria item-number alias reconciliation",1),
    (".github/prepare_30233.py",".github/prepare_30232.py",1),
    ("iCE-Onhand-Inventory-3.0.233","iCE-Onhand-Inventory-3.0.232",4)
]:
    if w.count(n)!=expected:raise SystemExit("Workflow 3.0.233 marker mismatch: "+n)
    w=w.replace(n,o)
workflow.write_text(w)
runpy.run_path(str(root/".github/prepare_30232.py"),run_name="__main__")
w=workflow.read_text()
for o,n,expected in [
    ("Prepare and verify 3.0.232 Victoria item-number alias reconciliation","Prepare and verify 3.0.233 recurring Fleet Feet RGIS customer import",1),
    (".github/prepare_30232.py",".github/prepare_30233.py",1),
    ("iCE-Onhand-Inventory-3.0.232","iCE-Onhand-Inventory-3.0.233",4)
]:
    if w.count(o)!=expected:raise SystemExit("Workflow 3.0.232 restoration mismatch: "+o)
    w=w.replace(o,n)
workflow.write_text(w)

gradle=root/"app/build.gradle"
g=gradle.read_text()
if g.count("versionCode 30232")!=1 or g.count("versionName '3.0.232'")!=1:raise SystemExit("Previous version missing")
gradle.write_text(g.replace("versionCode 30232","versionCode 30233",1).replace("versionName '3.0.232'","versionName '3.0.233'",1))
manifest=root/"app/src/main/AndroidManifest.xml"
m=manifest.read_text()
if m.count("iCE Onhand 3.0.232")!=1:raise SystemExit("Previous manifest missing")
manifest.write_text(m.replace("iCE Onhand 3.0.232","iCE Onhand 3.0.233",1))

main=root/"app/src/main/java/com/iceinventory/onhand/MainActivity.java"
s=main.read_text()
if s.count("Onhand Inventory 3.0.232")!=1:raise SystemExit("Previous home version missing")
s=s.replace("Onhand Inventory 3.0.232","Onhand Inventory 3.0.233",1)

def replace_once(old,new,label):
    global s
    if s.count(old)!=1:raise SystemExit(label+": expected one, found "+str(s.count(old)))
    s=s.replace(old,new,1)

# Fleet Feet's ORIGINAL RGIS file columns:
# Barcode, Item Number, Description, Size, [unused blank field].
# No QTY is supplied: new count starts with zero quantity.
replace_once(
    'String[] orders={null,"barcode,description,item_number,size",',
    'String[] orders={null,"barcode,item_number,description,size",',
    "Fleet Feet chooser input mapping")
replace_once(
    'FLEET FEET\\nBarcode • Description • Item Number • Size',
    'FLEET FEET\\nBarcode • Item Number • Description • Size',
    "Fleet Feet chooser caption")

# Undo older migration that incorrectly reversed Item Number/Description.
replace_once('''        if("barcode,item_number,description,size".equals(previouslySaved))
            prefs().edit().putString("import_field_order","barcode,description,item_number,size").apply();''',
'''        if("barcode,description,item_number,size".equals(previouslySaved))
            prefs().edit().putString("import_field_order","barcode,item_number,description,size").apply();''',
"Fleet Feet saved preference correction")

# Customer RGIS .TXT is comma-separated, quoted, headerless, and its
# DESCRIPTION can contain literal inch marks (e.g. 3" SHORT). The normal CSV
# quote parser can shift fields. Anchor from the right to read 5 exact fields.
helper=r'''    private List<String> parseFleetFeetOriginalLine(String line){
        java.util.regex.Matcher rgis=java.util.regex.Pattern.compile(
                "^\"([^\"]*)\",\"([^\"]*)\",\"(.*)\",\"([^\"]*)\",\"([^\"]*)\"$")
                .matcher(line);
        if(!rgis.matches())
            throw new IllegalArgumentException("Unexpected Fleet Feet RGIS row. Check the original customer format.");
        return java.util.Arrays.asList(rgis.group(1),rgis.group(2),
                rgis.group(3).replace("\"\"","\""),rgis.group(4),rgis.group(5));
    }

'''
replace_once("    private void readImport(Uri uri) {",helper+"    private void readImport(Uri uri) {","original RGIS parser")
replace_once('''            String[] order=prefs().getString("import_field_order","barcode,description,quantity,location,price").split(",");''',
'''            String fleetOrder=prefs().getString("import_field_order","barcode,description,quantity,location,price");
            if("barcode,description,item_number,size".equals(fleetOrder)){
                fleetOrder="barcode,item_number,description,size";
                prefs().edit().putString("import_field_order",fleetOrder).apply();
            }
            String[] order=fleetOrder.split(",");''',
"auto-repair previously saved Fleet mapping")
replace_once('''            String line=header?br.readLine():firstLine;
            while(line!=null) {''',
'''            boolean fleetOriginal=!header && delimiter==',' &&
                    "barcode,item_number,description,size".equals(fleetOrder);
            java.util.LinkedHashMap<String,ImportedRow> uniqueFleet=
                    fleetOriginal?new java.util.LinkedHashMap<>():null;
            String line=header?br.readLine():firstLine;
            while(line!=null) {''',
"RGIS detection")
replace_once("                    List<String> fields=CsvUtils.parseLine(line,delimiter);",
"                    List<String> fields=fleetOriginal?parseFleetFeetOriginalLine(line):CsvUtils.parseLine(line,delimiter);",
"original CSV line parser")
replace_once("                        row.barcode=maybeGtin(code);",
"                        row.barcode=fleetOriginal?code:maybeGtin(code);",
"preserve original Fleet barcodes")
replace_once('''                        rows.add(row);''',
'''                        if(fleetOriginal){
                            ImportedRow earlier=uniqueFleet.get(row.barcode);
                            if(earlier==null){uniqueFleet.put(row.barcode,row);rows.add(row);}
                            else {
                                if(!earlier.itemNumber.equalsIgnoreCase(row.itemNumber))
                                    throw new Exception("Conflicting item numbers for Fleet barcode "+row.barcode);
                                if(row.description.length()>earlier.description.length())
                                    earlier.description=row.description;
                            }
                        } else rows.add(row);''',
"dedupe original Fleet catalog by barcode")
main.write_text(s)

fmt=root/"app/src/main/java/com/iceinventory/onhand/FormatConfigActivity.java"
f=fmt.read_text()
old='''?new String[]{"quantity","barcode","description","item_number","size"}
                :new String[]{"barcode","description","item_number","size"};'''
new='''?new String[]{"quantity","barcode","description","item_number","size"}
                :new String[]{"barcode","item_number","description","size"};'''
if f.count(old)!=1:raise SystemExit("Fleet Format preset layout missing")
f=f.replace(old,new,1)
old='''            if("barcode,item_number,description,size".equals(oldFleet))
                prefs().edit().putString(KEY_IMPORT,"barcode,description,item_number,size").apply();'''
new='''            if("barcode,description,item_number,size".equals(oldFleet))
                prefs().edit().putString(KEY_IMPORT,"barcode,item_number,description,size").apply();'''
if f.count(old)!=1:raise SystemExit("Fleet preset migration missing")
f=f.replace(old,new,1)
f=f.replace("Fleet Feet imports BARCODE, DESCRIPTION, ITEM NUMBER, SIZE.",
            "Original Fleet Feet RGIS imports BARCODE, ITEM NUMBER, DESCRIPTION, SIZE. The blank fifth field is ignored.")
fmt.write_text(f)

checks={
    "version": "versionName '3.0.233'" in gradle.read_text() and "Onhand Inventory 3.0.233" in main.read_text(),
    "raw RGIS order": 'String[] orders={null,"barcode,item_number,description,size",' in main.read_text(),
    "format import order": 'new String[]{"barcode","item_number","description","size"}' in fmt.read_text(),
    "Fleet customer export still has Quantity first": 'new String[]{"quantity","barcode","description","item_number","size"}' in fmt.read_text(),
    "malformed inch quotes parser": 'parseFleetFeetOriginalLine(line)' in main.read_text() and 'rgis.group(4)' in main.read_text(),
    "barcode duplicate protection": "uniqueFleet.get(row.barcode)" in main.read_text() and "earlier.description=row.description" in main.read_text(),
    "does not change barcode": "row.barcode=fleetOriginal?code:maybeGtin(code);" in main.read_text(),
    "old wrong mapping migrated": '"barcode,description,item_number,size".equals(fleetOrder)' in main.read_text(),
    "Victoria unaffected": "groupVictoriaByItem()" in (root/"app/src/main/java/com/iceinventory/onhand/BatchMergeActivity.java").read_text(),
    "build release": ".github/prepare_30233.py" in workflow.read_text() and "3.0.233" in workflow.read_text(),
}
failed=[key for key,pass_ in checks.items() if not pass_]
if failed:raise SystemExit("OnHand 3.0.233 checks failed: "+", ".join(failed))
print("Prepared OnHand 3.0.233: direct monthly RGIS imports in original order, QTY zero, barcode duplicate/quote fixes.")
