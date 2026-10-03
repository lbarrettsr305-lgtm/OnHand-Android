#!/usr/bin/env python3
from pathlib import Path
import re
import subprocess
import sys

root = Path(__file__).resolve().parents[1]
subprocess.run([sys.executable, str(root / ".github" / "prepare_30204.py")], check=True)

print("3.0.205: previous release patches completed")
gradle = root / "app/build.gradle"
s = gradle.read_text()
if "versionName '3.0.204'" not in s or "versionCode 30204" not in s:
    raise SystemExit("3.0.204 version source not found")
gradle.write_text(s.replace("versionCode 30204", "versionCode 30205", 1).replace("versionName '3.0.204'", "versionName '3.0.205'", 1))

manifest = root / "app/src/main/AndroidManifest.xml"
s = manifest.read_text()
if "iCE Onhand 3.0.204" not in s: raise SystemExit("app label target missing")
manifest.write_text(s.replace("iCE Onhand 3.0.204", "iCE Onhand 3.0.205", 1))

main = root / "app/src/main/java/com/iceinventory/onhand/MainActivity.java"
s = main.read_text()
if "Onhand Inventory 3.0.204" not in s: raise SystemExit("screen version target missing")
main.write_text(s.replace("Onhand Inventory 3.0.204", "Onhand Inventory 3.0.205", 1))

# Store Victoria's item number as a real inventory field so it survives import, merge, and export.
print("3.0.205: version labels updated")
dbp = root / "app/src/main/java/com/iceinventory/onhand/InventoryDb.java"
s = dbp.read_text()
m = re.search(r"private static final int DB_VERSION = (\d+);", s)
if not m: raise SystemExit("DB version declaration missing")
old_db_version=int(m.group(1))
s = s[:m.start()] + "private static final int DB_VERSION = " + str(old_db_version+1) + ";" + s[m.end():]
s = s.replace("public String description;\n        public String price;", "public String description;\n        public String itemNumber;\n        public String price;", 1)
s = s.replace("description TEXT NOT NULL DEFAULT '', price TEXT", "description TEXT NOT NULL DEFAULT '', item_number TEXT NOT NULL DEFAULT '', price TEXT", 1)
s = s.replace("if (oldVersion < 2) ensurePriceColumn(db);", "if (oldVersion < 2) ensurePriceColumn(db);\n        if (oldVersion < 3) ensureItemNumberColumn(db);", 1)
s = s.replace("ensurePriceColumn(db);\n            ensureDefaults(db);", "ensurePriceColumn(db);\n            ensureItemNumberColumn(db);\n            ensureDefaults(db);", 1)
s = s.replace("ensurePriceColumn(db);\n        ensureDefaults(db);", "ensurePriceColumn(db);\n        ensureItemNumberColumn(db);\n        ensureDefaults(db);", 1)
marker = "    private void ensureDefaults(SQLiteDatabase db) {"
method = '''    private void ensureItemNumberColumn(SQLiteDatabase db) {
        boolean found=false;
        try (Cursor c=db.rawQuery("PRAGMA table_info(items)", null)) {
            while(c.moveToNext()) if ("item_number".equalsIgnoreCase(c.getString(c.getColumnIndexOrThrow("name")))) { found=true; break; }
        } catch (Exception ignored) {}
        if (!found) try { db.execSQL("ALTER TABLE items ADD COLUMN item_number TEXT NOT NULL DEFAULT ''"); } catch (Exception ignored) {}
    }

'''
if marker not in s: raise SystemExit("DB migration insertion point missing")
s = s.replace(marker, method + marker, 1)

pattern = r"    public void addOrIncrementAt\(long sessionId, String barcode, String description, String price, String categoryName, double quantity, String location, long updatedAt\) \{.*?^    \}"
replacement = '''    public void addOrIncrementAt(long sessionId, String barcode, String description, String price, double quantity, String location, long updatedAt) {
        addOrIncrementAt(sessionId,barcode,description,"",price,"",quantity,location,updatedAt);
    }

    public void addOrIncrementAt(long sessionId, String barcode, String description, String price, String categoryName, double quantity, String location, long updatedAt) {
        addOrIncrementAt(sessionId,barcode,description,"",price,categoryName,quantity,location,updatedAt);
    }

    public void addOrIncrementAt(long sessionId, String barcode, String description, String itemNumber, String price, double quantity, String location, long updatedAt) {
        addOrIncrementAt(sessionId,barcode,description,itemNumber,price,"",quantity,location,updatedAt);
    }

    public void addOrIncrementAt(long sessionId, String barcode, String description, String itemNumber, String price, String categoryName, double quantity, String location, long updatedAt) {
        if (sessionId <= 0) throw new IllegalStateException("No active inventory session");
        SQLiteDatabase db = getWritableDatabase();
        String safeBarcode = barcode == null ? "" : barcode.trim();
        String safeLocation = canonicalLocation(location);
        String safeCategory=categoryName==null?"":categoryName.trim();
        if(safeCategory.isEmpty())try(Cursor inherited=db.rawQuery("SELECT category_name FROM items WHERE session_id=? AND barcode=? AND category_name<>'' LIMIT 1",new String[]{String.valueOf(sessionId),safeBarcode})){if(inherited.moveToFirst())safeCategory=inherited.getString(0);}catch(Exception ignored){}
        long when=updatedAt>0?updatedAt:System.currentTimeMillis();
        String[] args = { String.valueOf(sessionId), safeBarcode, safeLocation };
        try (Cursor c = db.rawQuery("SELECT id,quantity FROM items WHERE session_id=? AND barcode=? AND location=? COLLATE NOCASE", args)) {
            if (c.moveToFirst()) {
                ContentValues cv = new ContentValues();
                cv.put("quantity", c.getDouble(1) + quantity);
                if (description != null && !description.trim().isEmpty()) cv.put("description", description.trim());
                if (itemNumber != null && !itemNumber.trim().isEmpty()) cv.put("item_number", itemNumber.trim());
                if (price != null && !price.trim().isEmpty()) cv.put("price", price.trim());
                if (!safeCategory.isEmpty()) cv.put("category_name", safeCategory);
                cv.put("updated_at", when);
                db.update("items", cv, "id=?", new String[]{String.valueOf(c.getLong(0))});
                return;
            }
        }
        ContentValues cv = new ContentValues();
        cv.put("session_id", sessionId); cv.put("barcode", safeBarcode);
        cv.put("description", description == null ? "" : description.trim());
        cv.put("item_number", itemNumber == null ? "" : itemNumber.trim());
        cv.put("price", price == null ? "" : price.trim());
        cv.put("category_name", safeCategory);
        cv.put("quantity", quantity); cv.put("location", safeLocation); cv.put("updated_at", when);
        db.insertOrThrow("items", null, cv);
    }'''
s, n = re.subn(pattern, replacement, s, count=1, flags=re.S | re.M)
if n != 1: raise SystemExit("category-aware add/merge method target missing")
s = s.replace("SELECT id,session_id,barcode,description,price,quantity,location,updated_at", "SELECT id,session_id,barcode,description,item_number,price,quantity,location,updated_at")
s = s.replace("i.barcode,i.description,i.price,i.quantity,i.location,i.updated_at,i.category_name", "i.barcode,i.description,i.item_number,i.price,i.quantity,i.location,i.updated_at,i.category_name")
row_pattern = r"        r\.description=c\.getString\(3\);.*?if\(c\.getColumnCount\(\)>9\)r\.scanSequence=c\.getLong\(9\);else r\.scanSequence=r\.id;"
row_replacement = '''        r.description=c.getString(3);
        r.itemNumber=c.getString(4);
        r.price=c.getString(5);
        r.quantity=c.getDouble(6);
        r.location=c.getString(7);
        r.updatedAt=c.getLong(8);
        if(c.getColumnCount()>9)r.categoryName=c.getString(9);else r.categoryName="";
        if(c.getColumnCount()>10)r.scanSequence=c.getLong(10);else r.scanSequence=r.id;'''
s, n = re.subn(row_pattern, row_replacement, s, count=1, flags=re.S)
if n != 1: raise SystemExit("row cursor mapping target missing")
dbp.write_text(s)
print("3.0.205: item number database migration updated")

# Add ITEM NUMBER header recognition and export in the generic configurable text engine.
tp = root / "app/src/main/java/com/iceinventory/onhand/TabTextUtils.java"
s = tp.read_text()
s = s.replace('else if("description".equals(f))b.append(clean(r.description));', 'else if("description".equals(f))b.append(clean(r.description));\n                else if("item_number".equals(f))b.append(clean(r.itemNumber));')
s = s.replace('if("description".equals(field))return "Description";', 'if("description".equals(field))return "Description";\n        if("item_number".equals(field))return "ITEM NUMBER";')
s = s.replace('String price=value(m,"price").replace("$","").trim();', 'String itemNumber=value(m,"item_number");\n        String price=value(m,"price").replace("$","").trim();')
s = s.replace('db.addOrIncrementAt(sessionId,code,desc,price,qty,loc,scannedAt);', 'db.addOrIncrementAt(sessionId,code,desc,itemNumber,price,qty,loc,scannedAt);')
s = s.replace('if(f.equals("description")||f.equals("item description")||f.equals("name")||f.contains("description"))return "description";', 'if(f.equals("description")||f.equals("item description")||f.equals("name")||f.contains("description"))return "description";\n        if(f.equals("item number")||f.equals("item no")||f.equals("item #")||f.equals("itemnumber"))return "item_number";')
if '"item_number".equals(f)' not in s: raise SystemExit("Tab export item number target missing")
tp.write_text(s)
print("3.0.205: text import/export updated")

# Show separate saved-order controls for import/export, with Victoria and Generic presets.
fp = root / "app/src/main/java/com/iceinventory/onhand/FormatConfigActivity.java"
s = fp.read_text()
s = s.replace('private static final String[] ALL={"quantity","barcode","description","price","location","scan_date","scan_time"};', 'private static final String[] ALL={"quantity","barcode","description","item_number","price","location","scan_date","scan_time"};')
s = s.replace('if("description".equals(f))return "Description";', 'if("description".equals(f))return "Description";\n        if("item_number".equals(f))return "ITEM NUMBER";')
s = s.replace('        rows=new LinearLayout(this);rows.setOrientation(LinearLayout.VERTICAL);body.addView(rows);', '''        LinearLayout presets=new LinearLayout(this);presets.setOrientation(LinearLayout.HORIZONTAL);
        Button victoria=button("Victoria");victoria.setOnClickListener(v->applyPreset(true));
        Button generic=button("Generic POS");generic.setOnClickListener(v->applyPreset(false));
        presets.addView(victoria,new LinearLayout.LayoutParams(0,dp(48),1));
        LinearLayout.LayoutParams gp=new LinearLayout.LayoutParams(0,dp(48),1);gp.setMargins(dp(6),0,0,0);presets.addView(generic,gp);
        body.addView(presets);
        rows=new LinearLayout(this);rows.setOrientation(LinearLayout.VERTICAL);body.addView(rows);''')
anchor = '    private void renderRows(){'
preset = '''    private void applyPreset(boolean victoria){
        order.clear();enabled.clear();
        String[] fields=victoria
                ?new String[]{"quantity","barcode","description","item_number","location"}
                :new String[]{"quantity","barcode","description","price"};
        for(String f:ALL){order.add(f);enabled.put(f,false);}
        for(String f:fields)enabled.put(f,true);
        selectedIndex=0;renderRows();
    }

'''
if anchor not in s: raise SystemExit("Format preset insertion point missing")
s = s.replace(anchor,preset+anchor,1)
s = s.replace('"Standard order is Quantity, Barcode, Description, Price.', '"Use the Generic POS preset for Quantity, Barcode, Description, Price, or Victoria for QTY, BARCODE, DESCRIPTION, ITEM NUMBER, LOCATION.')
s = s.replace('"Standard incoming order is Quantity, Barcode, Description, Price.', '"Use the Generic POS preset for Quantity, Barcode, Description, Price, or Victoria for QTY, BARCODE, DESCRIPTION, ITEM NUMBER, LOCATION.')
fp.write_text(s)
print("3.0.205: template presets updated")

# Keep output/build name aligned with the new app version.
workflow = root / ".github/workflows/build-apk.yml"
s = workflow.read_text()
if "prepare_30205.py" not in s or "3.0.205" not in s: raise SystemExit("workflow 3.0.205 targets missing")
s = s.replace("Prepare and verify 3.0.204 safe Master count import","Prepare and verify 3.0.205 Victoria import/export templates")
s = s.replace("prepare_30204.py","prepare_30205.py")
s = s.replace("3.0.204","3.0.205")
workflow.write_text(s)

checks = {
    "version bumped": "versionName '3.0.205'" in gradle.read_text(),
    "database migration": "ensureItemNumberColumn(db)" in dbp.read_text() and "item_number TEXT" in dbp.read_text(),
    "import/export mapping": '"item_number"' in tp.read_text() and 'ITEM NUMBER' in tp.read_text(),
    "Victoria five-column preset": 'new String[]{"quantity","barcode","description","item_number","location"}' in fp.read_text(),
    "generic four-column preset": 'new String[]{"quantity","barcode","description","price"}' in fp.read_text(),
    "workflow points to this script": "prepare_30205.py" in workflow.read_text(),
}
failed=[k for k,v in checks.items() if not v]
if failed: raise SystemExit("3.0.205 checks failed: "+", ".join(failed))
print("Prepared iCE Onhand 3.0.205 with separate Victoria and Generic POS import/export presets.")
