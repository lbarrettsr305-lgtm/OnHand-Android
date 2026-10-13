#!/usr/bin/env python3
from pathlib import Path
import re
import runpy

root=Path(__file__).resolve().parent.parent
workflow=root/".github/workflows/build-apk.yml"
w=workflow.read_text()
for new,old in [
    ("Prepare and verify 3.0.222 clean Fleet Feet batch export","Prepare and verify 3.0.221 import location prompt"),
    (".github/prepare_30222.py",".github/prepare_30221.py"),
    ("iCE-Onhand-Inventory-3.0.222","iCE-Onhand-Inventory-3.0.221"),
]:
    if new not in w: raise SystemExit("3.0.222 workflow seed missing: "+new)
    w=w.replace(new,old)
workflow.write_text(w)
runpy.run_path(str(root/".github/prepare_30221.py"),run_name="__main__")
w=workflow.read_text()
for old,new in [
    ("Prepare and verify 3.0.221 import location prompt","Prepare and verify 3.0.222 clean Fleet Feet batch export"),
    (".github/prepare_30221.py",".github/prepare_30222.py"),
    ("iCE-Onhand-Inventory-3.0.221","iCE-Onhand-Inventory-3.0.222"),
]:
    if old not in w: raise SystemExit("3.0.221 workflow marker missing: "+old)
    w=w.replace(old,new)
workflow.write_text(w)

dbfile=root/"app/src/main/java/com/iceinventory/onhand/InventoryDb.java"
d=dbfile.read_text()
pat=r'''    public void replaceSession\(long sessionId, String newName\) \{.*?\n    \}\n\n    public long createSession'''
repl='''    public void replaceSession(long sessionId, String newName) {
        if(sessionId<=0)throw new IllegalArgumentException("No active inventory session");
        SQLiteDatabase db=getWritableDatabase();
        db.beginTransaction();
        try {
            String[] args=new String[]{String.valueOf(sessionId)};
            db.delete("items","session_id=?",args);
            db.delete("scan_history","session_id=?",args);
            db.delete("export_batches","session_id=?",args);
            ContentValues cv=new ContentValues();
            cv.put("name",newName==null||newName.trim().isEmpty()?"Imported Inventory":newName.trim());
            db.update("sessions",cv,"id=?",args);
            db.setTransactionSuccessful();
        } finally { db.endTransaction(); }
    }

    public long createSession'''
d,n=re.subn(pat,repl,d,count=1,flags=re.S)
if n!=1: raise SystemExit("Replacement import batch reset point missing or ambiguous")
old='''        String safeCategory=categoryName==null?"":categoryName.trim();
        if(safeCategory.isEmpty())try(Cursor inherited=db.rawQuery("SELECT category_name FROM items WHERE session_id=? AND barcode=? AND category_name<>'' LIMIT 1",new String[]{String.valueOf(sessionId),safeBarcode})){if(inherited.moveToFirst())safeCategory=inherited.getString(0);}catch(Exception ignored){}'''
new='''        String safeCategory=categoryName==null?"":categoryName.trim();
        String safeItemNumber=itemNumber==null?"":itemNumber.trim();
        if(safeItemNumber.isEmpty())try(Cursor inherited=db.rawQuery("SELECT item_number FROM items WHERE session_id=? AND barcode=? AND item_number<>'' LIMIT 1",new String[]{String.valueOf(sessionId),safeBarcode})){if(inherited.moveToFirst())safeItemNumber=inherited.getString(0);}catch(Exception ignored){}
        if(safeCategory.isEmpty())try(Cursor inherited=db.rawQuery("SELECT category_name FROM items WHERE session_id=? AND barcode=? AND category_name<>'' LIMIT 1",new String[]{String.valueOf(sessionId),safeBarcode})){if(inherited.moveToFirst())safeCategory=inherited.getString(0);}catch(Exception ignored){}'''
if d.count(old)!=1: raise SystemExit("Item number inheritance point missing or ambiguous")
d=d.replace(old,new,1)
d=d.replace('if (itemNumber != null && !itemNumber.trim().isEmpty()) cv.put("item_number", itemNumber.trim());','if (!safeItemNumber.isEmpty()) cv.put("item_number", safeItemNumber);',1)
d=d.replace('cv.put("item_number", itemNumber == null ? "" : itemNumber.trim());','cv.put("item_number", safeItemNumber);',1)
dbfile.write_text(d)

main=root/"app/src/main/java/com/iceinventory/onhand/MainActivity.java"
s=main.read_text()
s=s.replace('String barcode,description,price,location;\n        int quantity;','String barcode,description,itemNumber,price,location;\n        int quantity;',1)
old='''                        row.description=joinedDescription(field(fields,itemIndex),field(fields,descriptionIndex),field(fields,sizeIndex));
                        row.price=field(fields,priceIndex).replace("$","").trim();'''
new='''                        row.itemNumber=field(fields,itemIndex);
                        row.description=field(fields,descriptionIndex);
                        String size=field(fields,sizeIndex);
                        if(!size.isEmpty())row.description=(row.description.isEmpty()?"":row.description+" ")+"[Size: "+size+"]";
                        row.price=field(fields,priceIndex).replace("$","").trim();'''
if s.count(old)!=1: raise SystemExit("Fleet Feet import field mapping point missing or ambiguous")
s=s.replace(old,new,1)
old='db.addOrIncrement(sessionId,row.barcode,row.description,row.price,row.quantity,row.location);'
new='db.addOrIncrementAt(sessionId,row.barcode,row.description,row.itemNumber,row.price,"",row.quantity,row.location,System.currentTimeMillis());'
if s.count(old)!=1: raise SystemExit("Imported row database insert point missing or ambiguous")
s=s.replace(old,new,1)
main.write_text(s)

tab=root/"app/src/main/java/com/iceinventory/onhand/TabTextUtils.java"
t=tab.read_text()
old='db.addOrIncrementAt(sessionId,code,desc,price,category,qty,loc,scannedAt);'
new='db.addOrIncrementAt(sessionId,code,desc,itemNumber,price,category,qty,loc,scannedAt);'
if t.count(old)!=1: raise SystemExit("Mapped import item-number write point missing or ambiguous")
tab.write_text(t.replace(old,new,1))

batch=root/"app/src/main/java/com/iceinventory/onhand/BatchExportText.java"
b=batch.read_text()
old='''                else if("description".equals(f))b.append(clean(r.description));
                else if("price".equals(f))b.append(clean(r.price));'''
new='''                else if("description".equals(f))b.append(clean(order.contains("size")?descriptionWithoutSize(r.description):r.description));
                else if("item_number".equals(f))b.append(clean(r.itemNumber));
                else if("size".equals(f))b.append(clean(sizeFromDescription(r.description)));
                else if("price".equals(f))b.append(clean(r.price));'''
if b.count(old)!=1: raise SystemExit("Batch TXT field mapping point missing or ambiguous")
b=b.replace(old,new,1)
marker='''    private static String clean(String s) {'''
helpers='''    private static String sizeFromDescription(String description) {
        if(description==null)return "";
        int start=description.lastIndexOf(" [Size: ");
        if(start<0||!description.endsWith("]"))return "";
        return description.substring(start+8,description.length()-1).trim();
    }

    private static String descriptionWithoutSize(String description) {
        if(description==null)return "";
        int start=description.lastIndexOf(" [Size: ");
        if(start<0||!description.endsWith("]"))return description;
        return description.substring(0,start).trim();
    }

'''
if marker not in b: raise SystemExit("Batch exporter helper insertion point missing")
b=b.replace(marker,helpers+marker,1)
batch.write_text(b)

gradle=root/"app/build.gradle"
g=gradle.read_text()
if "versionCode 30221" not in g or "versionName '3.0.221'" not in g: raise SystemExit("3.0.221 Gradle version missing")
gradle.write_text(g.replace("versionCode 30221","versionCode 30222",1).replace("versionName '3.0.221'","versionName '3.0.222'",1))
manifest=root/"app/src/main/AndroidManifest.xml"
m=manifest.read_text()
if m.count("iCE Onhand 3.0.221")!=1: raise SystemExit("3.0.221 manifest label missing")
manifest.write_text(m.replace("iCE Onhand 3.0.221","iCE Onhand 3.0.222",1))
s=main.read_text()
if s.count("Onhand Inventory 3.0.221")!=1: raise SystemExit("3.0.221 home label missing")
main.write_text(s.replace("Onhand Inventory 3.0.221","Onhand Inventory 3.0.222",1))

s=main.read_text();d=dbfile.read_text();t=tab.read_text();b=batch.read_text()
checks={
    "replacement starts a fresh batch and clears old scan history": 'db.delete("scan_history","session_id=?",args);' in d and 'db.delete("export_batches","session_id=?",args);' in d,
    "Fleet Feet item number is stored": 'row.itemNumber=field(fields,itemIndex);' in s and 'row.itemNumber,row.price' in s,
    "Fleet Feet size survives import": '"[Size: "+size+"]"' in s,
    "mapped imports persist item numbers": 'code,desc,itemNumber,price,category,qty,loc,scannedAt' in t,
    "batch export includes item number and size": '"item_number".equals(f)' in b and '"size".equals(f)' in b,
    "counted rows inherit catalog item number": 'SELECT item_number FROM items WHERE session_id=? AND barcode=?' in d,
    "post-import location prompt retained": 'showLocationStep();' in s and 'remove(confirmedLocationKey(sessionId))' in s,
    "release labels": "versionName '3.0.222'" in gradle.read_text() and "iCE Onhand 3.0.222" in manifest.read_text() and "Onhand Inventory 3.0.222" in s,
    "workflow points to release": ".github/prepare_30222.py" in workflow.read_text() and "3.0.222" in workflow.read_text(),
}
failed=[name for name,passed in checks.items() if not passed]
if failed: raise SystemExit("3.0.222 validation failed: "+", ".join(failed))
print("Prepared iCE OnHand 3.0.222: replacement imports start a fresh batch ledger and Fleet Feet item numbers and sizes export in their own columns.")
