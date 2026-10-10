#!/usr/bin/env python3
from pathlib import Path
import runpy
import re

script_dir = Path(__file__).resolve().parent
root = script_dir.parent if script_dir.name == ".github" else script_dir
workflow = root / ".github/workflows/build-apk.yml"

# Start from the signed 3.0.217 chooser release.
w = workflow.read_text()
for new, old in [
    ("Prepare and verify 3.0.218 import replacement behavior", "Prepare and verify 3.0.217 import format buttons"),
    (".github/prepare_30218.py", ".github/prepare_30217.py"),
    ("iCE-Onhand-Inventory-3.0.218", "iCE-Onhand-Inventory-3.0.217"),
]:
    if new not in w:
        raise SystemExit("3.0.218 workflow seed missing: " + new)
    w = w.replace(new, old)
workflow.write_text(w)
runpy.run_path(str(root / ".github/prepare_30217.py"), run_name="__main__")

w = workflow.read_text()
for old, new in [
    ("Prepare and verify 3.0.217 import format buttons", "Prepare and verify 3.0.218 import replacement behavior"),
    (".github/prepare_30217.py", ".github/prepare_30218.py"),
    ("iCE-Onhand-Inventory-3.0.217", "iCE-Onhand-Inventory-3.0.218"),
]:
    if old not in w:
        raise SystemExit("3.0.217 workflow marker missing: " + old)
    w = w.replace(old, new)
workflow.write_text(w)

main = root / "app/src/main/java/com/iceinventory/onhand/MainActivity.java"
s = main.read_text()
if "import android.provider.OpenableColumns;" not in s:
    s = s.replace("import android.provider.MediaStore;", "import android.provider.MediaStore;\nimport android.provider.OpenableColumns;", 1)
if "import android.database.Cursor;" not in s:
    s = s.replace("import android.content.SharedPreferences;", "import android.content.SharedPreferences;\nimport android.database.Cursor;", 1)

match = re.search(r"    private void readImport\s*\(Uri uri\)\s*\{", s)
start = match.start() if match else -1
end_match = re.search(r"^\s*private\s+void\s+showError\s*\(", s[start:] if start >= 0 else "", re.MULTILINE)
end = start + end_match.start() if start >= 0 and end_match else -1
if start < 0 or end < 0:
    raise SystemExit("Import parser boundaries missing (readImport="+str(start)+", showError="+str(end)+")")
new_parser = '''    private static final class ImportedRow {
        String barcode,description,price,location;
        int quantity;
    }

    private String importFileNameKey() { return "import_file_name"; }

    private int findHeader(List<String> fields,String... names) {
        for(int i=0;i<fields.size();i++) {
            String f=fields.get(i).trim().toLowerCase(Locale.US).replace("_"," ").replace("-"," ");
            for(String n:names)if(f.equals(n)||f.contains(n))return i;
        }
        return -1;
    }

    private String field(List<String> fields,int index) {
        return index>=0&&index<fields.size()?fields.get(index).trim():"";
    }

    private String importFileName(Uri uri) {
        String name="";
        try(Cursor c=getContentResolver().query(uri,new String[]{OpenableColumns.DISPLAY_NAME},null,null,null)) {
            if(c!=null&&c.moveToFirst())name=c.getString(0);
        } catch(Exception ignored) {}
        if(name==null||name.trim().isEmpty())name=uri.getLastPathSegment();
        if(name==null||name.trim().isEmpty())name="Imported Inventory";
        name=name.trim();
        int dot=name.lastIndexOf('.');
        if(dot>0)name=name.substring(0,dot);
        return name;
    }

    private int orderIndex(String[] order,String key) {
        for(int i=0;i<order.length;i++)if(order[i].trim().equalsIgnoreCase(key))return i;
        return -1;
    }

    private String joinedDescription(String itemNumber,String description,String size) {
        StringBuilder out=new StringBuilder();
        if(itemNumber!=null&&!itemNumber.trim().isEmpty())out.append(itemNumber.trim());
        if(description!=null&&!description.trim().isEmpty()) {
            if(out.length()>0)out.append(" | ");
            out.append(description.trim());
        }
        if(size!=null&&!size.trim().isEmpty()) {
            if(out.length()>0)out.append(" | ");
            out.append("Size: ").append(size.trim());
        }
        return out.toString();
    }

    private void readImport(Uri uri) {
        if(uri==null)return;
        ArrayList<ImportedRow> rows=new ArrayList<>();
        try(InputStream is=getContentResolver().openInputStream(uri);
            BufferedReader br=new BufferedReader(new InputStreamReader(is,StandardCharsets.UTF_8))) {
            String firstLine=null;
            while((firstLine=br.readLine())!=null&&firstLine.trim().isEmpty()){}
            if(firstLine==null){toast("The selected file is empty. Current inventory was not changed.");return;}
            char delimiter=firstLine.indexOf('\\t')>=0?'\\t':',';
            List<String> first=CsvUtils.parseLine(firstLine,delimiter);
            String[] order=prefs().getString("import_field_order","barcode,description,quantity,location,price").split(",");
            int barcodeIndex=findHeader(first,"barcode","upc","gtin");
            boolean header=barcodeIndex>=0;
            int itemIndex,descriptionIndex,sizeIndex,quantityIndex,locationIndex,priceIndex;
            if(header) {
                itemIndex=findHeader(first,"item number","item no","item #","sku");
                descriptionIndex=findHeader(first,"description","item description","name");
                sizeIndex=findHeader(first,"size","sizing");
                quantityIndex=findHeader(first,"quantity","qty","onhand","on hand","count");
                locationIndex=findHeader(first,"location","loc","area");
                priceIndex=findHeader(first,"price","retail","cost");
            } else {
                barcodeIndex=orderIndex(order,"barcode");
                if(barcodeIndex<0)barcodeIndex=0;
                itemIndex=orderIndex(order,"item_number");
                descriptionIndex=orderIndex(order,"description");
                sizeIndex=orderIndex(order,"size");
                quantityIndex=orderIndex(order,"quantity");
                locationIndex=orderIndex(order,"location");
                priceIndex=orderIndex(order,"price");
            }
            String line=header?br.readLine():firstLine;
            while(line!=null) {
                if(!line.trim().isEmpty()) {
                    List<String> fields=CsvUtils.parseLine(line,delimiter);
                    String code=field(fields,barcodeIndex);
                    if(!code.isEmpty()) {
                        ImportedRow row=new ImportedRow();
                        row.barcode=maybeGtin(code);
                        row.description=joinedDescription(field(fields,itemIndex),field(fields,descriptionIndex),field(fields,sizeIndex));
                        row.price=field(fields,priceIndex).replace("$","").trim();
                        row.location=field(fields,locationIndex);
                        if(row.location.isEmpty())row.location="Main";
                        try{String q=field(fields,quantityIndex);row.quantity=q.isEmpty()?0:Integer.parseInt(q);}catch(Exception ignored){row.quantity=0;}
                        rows.add(row);
                    }
                }
                line=br.readLine();
            }
            if(rows.isEmpty()){toast("No barcode rows were found. Current inventory was not changed.");return;}
            String importedName=importFileName(uri);
            db.replaceSession(sessionId,importedName);
            sessionName=importedName;
            if(titleSession!=null)titleSession.setText(sessionName);
            for(ImportedRow row:rows) {
                db.addLocation(row.location);
                db.addOrIncrement(sessionId,row.barcode,row.description,row.price,row.quantity,row.location);
            }
            refreshLocations();refreshList();
            toast("Replaced current inventory with "+rows.size()+" rows: "+importedName);
        } catch(Exception e){showError("Import failed. Current inventory was not changed.",e);}
    }
'''
s = s[:start] + new_parser + s[end:]
main.write_text(s)

csvfile=root/"app/src/main/java/com/iceinventory/onhand/CsvUtils.java"
c=csvfile.read_text()
signature="    public static List<String> parseLine(String line) {"
if c.count(signature)!=1:
    raise SystemExit("CSV parser signature missing or ambiguous")
c=c.replace(signature,"    public static List<String> parseLine(String line) {\n        return parseLine(line, ',');\n    }\n\n    public static List<String> parseLine(String line, char delimiter) {",1)
branch="} else if (ch==',' && !quoted) {"
if c.count(branch)!=1:
    raise SystemExit("CSV delimiter branch missing or ambiguous")
csvfile.write_text(c.replace(branch,"} else if (ch==delimiter && !quoted) {",1))

dbfile = root / "app/src/main/java/com/iceinventory/onhand/InventoryDb.java"
d = dbfile.read_text()
anchor = "    public long createSession(String name) {"
method = '''    public void replaceSession(long sessionId, String newName) {
        if(sessionId<=0)throw new IllegalArgumentException("No active inventory session");
        SQLiteDatabase db=getWritableDatabase();
        db.beginTransaction();
        try {
            db.delete("items","session_id=?",new String[]{String.valueOf(sessionId)});
            ContentValues cv=new ContentValues();
            cv.put("name",newName==null||newName.trim().isEmpty()?"Imported Inventory":newName.trim());
            db.update("sessions",cv,"id=?",new String[]{String.valueOf(sessionId)});
            db.setTransactionSuccessful();
        } finally { db.endTransaction(); }
    }

'''
if d.count(anchor)!=1:
    raise SystemExit("InventoryDb session insertion point missing or ambiguous")
d=d.replace(anchor,method+anchor,1)
dbfile.write_text(d)

gradle=root/"app/build.gradle"
g=gradle.read_text()
if "versionCode 30217" not in g or "versionName '3.0.217'" not in g:
    raise SystemExit("3.0.217 Gradle version missing")
gradle.write_text(g.replace("versionCode 30217","versionCode 30218",1).replace("versionName '3.0.217'","versionName '3.0.218'",1))

manifest=root/"app/src/main/AndroidManifest.xml"
m=manifest.read_text()
if m.count("iCE Onhand 3.0.217")!=1:
    raise SystemExit("3.0.217 manifest label missing")
manifest.write_text(m.replace("iCE Onhand 3.0.217","iCE Onhand 3.0.218",1))

s=main.read_text()
if s.count("Onhand Inventory 3.0.217")!=1:
    raise SystemExit("3.0.217 home label missing")
main.write_text(s.replace("Onhand Inventory 3.0.217","Onhand Inventory 3.0.218",1))

checks={
    "format mapping used": "orderIndex(order,\"item_number\")" in new_parser and "findHeader(first,\"item number\"" in new_parser,
    "CSV and tab-delimited files supported": "char delimiter=firstLine.indexOf('\\t')>=0?'\\t':',';" in new_parser and "parseLine(String line, char delimiter)" in csvfile.read_text(),
    "only replaces after valid barcode rows": new_parser.index("if(rows.isEmpty())") < new_parser.index("db.replaceSession(sessionId,importedName)"),
    "session renamed from selected file": "String importedName=importFileName(uri);" in new_parser and "db.replaceSession(sessionId,importedName);" in new_parser,
    "all catalog columns retained": all(x in new_parser for x in ["itemIndex", "descriptionIndex", "sizeIndex", "quantityIndex", "locationIndex", "priceIndex"]),
    "release labels": "versionName '3.0.218'" in gradle.read_text() and "iCE Onhand 3.0.218" in manifest.read_text() and "Onhand Inventory 3.0.218" in main.read_text(),
    "workflow points to release": ".github/prepare_30218.py" in workflow.read_text() and "3.0.218" in workflow.read_text(),
}
failed=[name for name,passed in checks.items() if not passed]
if failed:raise SystemExit("3.0.218 validation failed: "+", ".join(failed))
print("Prepared iCE OnHand 3.0.218: imports replace and rename the active inventory, with the selected template's columns applied.")
