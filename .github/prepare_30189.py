#!/usr/bin/env python3
from pathlib import Path
import runpy

root = Path(__file__).resolve().parents[1]
runpy.run_path(str(root / ".github" / "prepare_30188.py"), run_name="__main__")

gradle = root / "app" / "build.gradle"
s = gradle.read_text().replace("versionCode 30188", "versionCode 30189").replace("versionName '3.0.188'", "versionName '3.0.189'")
gradle.write_text(s)

manifest = root / "app" / "src" / "main" / "AndroidManifest.xml"
manifest.write_text(manifest.read_text().replace("iCE Onhand 3.0.188", "iCE Onhand 3.0.189"))

db = root / "app" / "src" / "main" / "java" / "com" / "iceinventory" / "onhand" / "InventoryDb.java"
s = db.read_text()
s = s.replace("private static final int DB_VERSION = 3;", "private static final int DB_VERSION = 4;")
s = s.replace("        public String price;\n        public double quantity;", "        public String price;\n        public String categoryName;\n        public double quantity;")
s = s.replace("price TEXT NOT NULL DEFAULT '', quantity REAL", "price TEXT NOT NULL DEFAULT '', category_name TEXT NOT NULL DEFAULT '', quantity REAL")
s = s.replace("        if (oldVersion < 3) ensureRecoveryTables(db);", "        if (oldVersion < 3) ensureRecoveryTables(db);\n        if (oldVersion < 4) ensureCategoryColumns(db);")
s = s.replace("            ensurePriceColumn(db);\n            ensureDefaults(db);", "            ensurePriceColumn(db);\n            ensureCategoryColumns(db);\n            ensureDefaults(db);")
anchor = '''    private void ensureRecoveryTables(SQLiteDatabase db) {'''
category_method = '''    private void ensureCategoryColumns(SQLiteDatabase db) {
        boolean itemFound=false;
        try (Cursor c=db.rawQuery("PRAGMA table_info(items)", null)) {
            while(c.moveToNext())if("category_name".equalsIgnoreCase(c.getString(c.getColumnIndexOrThrow("name")))){itemFound=true;break;}
        } catch(Exception ignored) {}
        if(!itemFound)try{db.execSQL("ALTER TABLE items ADD COLUMN category_name TEXT NOT NULL DEFAULT ''");}catch(Exception ignored){}
        boolean recoveryFound=false;
        try (Cursor c=db.rawQuery("PRAGMA table_info(recovery_snapshot_items)", null)) {
            while(c.moveToNext())if("category_name".equalsIgnoreCase(c.getString(c.getColumnIndexOrThrow("name")))){recoveryFound=true;break;}
        } catch(Exception ignored) {}
        if(!recoveryFound)try{db.execSQL("ALTER TABLE recovery_snapshot_items ADD COLUMN category_name TEXT NOT NULL DEFAULT ''");}catch(Exception ignored){}
    }

'''
if s.count(anchor) != 1:
    raise SystemExit("Recovery method anchor not found")
s = s.replace(anchor, category_method + anchor, 1)
s = s.replace("price TEXT NOT NULL DEFAULT '', quantity REAL NOT NULL DEFAULT 0, location TEXT", "price TEXT NOT NULL DEFAULT '', category_name TEXT NOT NULL DEFAULT '', quantity REAL NOT NULL DEFAULT 0, location TEXT")
s = s.replace("ensureRecoveryTables(sql);", "ensureRecoveryTables(sql);ensureCategoryColumns(sql);")
s = s.replace("SELECT id,session_id,barcode,description,price,quantity,location,updated_at FROM items", "SELECT id,session_id,barcode,description,price,quantity,location,updated_at,category_name FROM items")

old_overloads = '''    public void addOrIncrement(long sessionId, String barcode, String description, String price, double quantity, String location) {
        addOrIncrementAt(sessionId,barcode,description,price,quantity,location,System.currentTimeMillis());
    }

    public void addOrIncrementAt(long sessionId, String barcode, String description, String price, double quantity, String location, long updatedAt) {'''
new_overloads = '''    public void addOrIncrement(long sessionId, String barcode, String description, String price, double quantity, String location) {
        addOrIncrementAt(sessionId,barcode,description,price,"",quantity,location,System.currentTimeMillis());
    }

    public void addOrIncrement(long sessionId, String barcode, String description, String price, String categoryName, double quantity, String location) {
        addOrIncrementAt(sessionId,barcode,description,price,categoryName,quantity,location,System.currentTimeMillis());
    }

    public void addOrIncrementAt(long sessionId, String barcode, String description, String price, double quantity, String location, long updatedAt) {
        addOrIncrementAt(sessionId,barcode,description,price,"",quantity,location,updatedAt);
    }

    public void addOrIncrementAt(long sessionId, String barcode, String description, String price, String categoryName, double quantity, String location, long updatedAt) {'''
if s.count(old_overloads) != 1:
    raise SystemExit("DB add overloads not found")
s = s.replace(old_overloads, new_overloads, 1)
s = s.replace('''        String safeLocation = canonicalLocation(location);
        long when=updatedAt>0?updatedAt:System.currentTimeMillis();''', '''        String safeLocation = canonicalLocation(location);
        String safeCategory=categoryName==null?"":categoryName.trim();
        if(safeCategory.isEmpty())try(Cursor inherited=db.rawQuery("SELECT category_name FROM items WHERE session_id=? AND barcode=? AND category_name<>'' LIMIT 1",new String[]{String.valueOf(sessionId),safeBarcode})){if(inherited.moveToFirst())safeCategory=inherited.getString(0);}catch(Exception ignored){}
        long when=updatedAt>0?updatedAt:System.currentTimeMillis();''', 1)
s = s.replace('''                if (price != null && !price.trim().isEmpty()) cv.put("price", price.trim());
                cv.put("updated_at", when);''', '''                if (price != null && !price.trim().isEmpty()) cv.put("price", price.trim());
                if (!safeCategory.isEmpty()) cv.put("category_name", safeCategory);
                cv.put("updated_at", when);''', 1)
s = s.replace('''        cv.put("price", price == null ? "" : price.trim());
        cv.put("quantity", quantity);''', '''        cv.put("price", price == null ? "" : price.trim());
        cv.put("category_name", safeCategory);
        cv.put("quantity", quantity);''', 1)
s = s.replace('''                if(source.price!=null&&!source.price.trim().isEmpty())cv.put("price",source.price.trim());
                sql.update''', '''                if(source.price!=null&&!source.price.trim().isEmpty())cv.put("price",source.price.trim());
                if(source.categoryName!=null&&!source.categoryName.trim().isEmpty())cv.put("category_name",source.categoryName.trim());
                sql.update''', 1)

old_items_query = '''SELECT i.id,i.session_id,i.barcode,i.description,i.price,i.quantity,i.location,i.updated_at,COALESCE((SELECT MIN(h.id) FROM scan_history h WHERE h.session_id=i.session_id AND h.barcode=i.barcode AND h.location=i.location),i.id) FROM items i'''
new_items_query = '''SELECT i.id,i.session_id,i.barcode,i.description,i.price,i.quantity,i.location,i.updated_at,i.category_name,COALESCE((SELECT MIN(h.id) FROM scan_history h WHERE h.session_id=i.session_id AND h.barcode=i.barcode AND h.location=i.location),i.id) FROM items i'''
if s.count(old_items_query) != 1:
    raise SystemExit("DB items query not found")
s = s.replace(old_items_query, new_items_query, 1)
s = s.replace('''        r.updatedAt=c.getLong(7);
        if(c.getColumnCount()>8)r.scanSequence=c.getLong(8);else r.scanSequence=r.id;''', '''        r.updatedAt=c.getLong(7);
        if(c.getColumnCount()>8)r.categoryName=c.getString(8);else r.categoryName="";
        if(c.getColumnCount()>9)r.scanSequence=c.getLong(9);else r.scanSequence=r.id;''', 1)
s = s.replace("INSERT INTO recovery_snapshot_items(snapshot_id,barcode,description,price,quantity,location,updated_at) SELECT ?,barcode,description,price,quantity,location,updated_at", "INSERT INTO recovery_snapshot_items(snapshot_id,barcode,description,price,category_name,quantity,location,updated_at) SELECT ?,barcode,description,price,category_name,quantity,location,updated_at")
s = s.replace("INSERT INTO items(session_id,barcode,description,price,quantity,location,updated_at) SELECT ?,barcode,description,price,quantity,location,updated_at", "INSERT INTO items(session_id,barcode,description,price,category_name,quantity,location,updated_at) SELECT ?,barcode,description,price,category_name,quantity,location,updated_at")
s = s.replace('''                    Row now=current.get(key);r.price=now==null||now.price==null?"":now.price;grouped.put(key,r);''', '''                    Row now=current.get(key);r.price=now==null||now.price==null?"":now.price;r.categoryName=now==null||now.categoryName==null?"":now.categoryName;grouped.put(key,r);''', 1)
db.write_text(s)

tab = root / "app" / "src" / "main" / "java" / "com" / "iceinventory" / "onhand" / "TabTextUtils.java"
s = tab.read_text()
s = s.replace('''        if(!out.contains("barcode"))out.add(Math.min(1,out.size()),"barcode");
        if(out.isEmpty())out.addAll(DEFAULT);''', '''        if(!out.contains("barcode"))out.add(Math.min(1,out.size()),"barcode");
        if(!out.contains("category_description"))out.add("category_description");
        if(out.isEmpty())out.addAll(DEFAULT);''', 1)
s = s.replace('''                else if("price".equals(f))b.append(clean(r.price));
                else if("quantity".equals(f))''', '''                else if("price".equals(f))b.append(clean(r.price));
                else if("category_description".equals(f))b.append(clean(r.categoryName));
                else if("quantity".equals(f))''', 1)
s = s.replace('''        if("price".equals(field))return "Price";
        if("location".equals(field))''', '''        if("price".equals(field))return "Price";
        if("category_description".equals(field))return "Category Description";
        if("location".equals(field))''', 1)
s = s.replace('''        String price=value(m,"price").replace("$","").trim();
        String loc=value(m,"location");''', '''        String price=value(m,"price").replace("$","").trim();
        String category=value(m,"category_description");
        String loc=value(m,"location");''', 1)
s = s.replace("db.addOrIncrementAt(sessionId,code,desc,price,qty,loc,scannedAt);", "db.addOrIncrementAt(sessionId,code,desc,price,category,qty,loc,scannedAt);")
s = s.replace('''        if(f.equals("description")||f.equals("item description")||f.equals("name")||f.contains("description"))return "description";''', '''        if(f.equals("category description")||f.equals("category name")||f.equals("category"))return "category_description";
        if(f.equals("description")||f.equals("item description")||f.equals("name")||f.contains("description"))return "description";''', 1)
tab.write_text(s)

batch = root / "app" / "src" / "main" / "java" / "com" / "iceinventory" / "onhand" / "BatchExportText.java"
s = batch.read_text().replace('''                else if("price".equals(f))b.append(clean(r.price));
                else if("quantity".equals(f))''', '''                else if("price".equals(f))b.append(clean(r.price));
                else if("category_description".equals(f))b.append(clean(r.categoryName));
                else if("quantity".equals(f))''')
batch.write_text(s)

adapter = root / "app" / "src" / "main" / "java" / "com" / "iceinventory" / "onhand" / "InventoryAdapter.java"
s = adapter.read_text()
old_qty = '''        TextView q=text("Qty: "+QuantityMath.format(r.quantity),compact?12:14,primary,true);
        q.setGravity(Gravity.END);
        right.addView(q);'''
new_qty = '''        LinearLayout quantityLine=new LinearLayout(context);quantityLine.setOrientation(LinearLayout.HORIZONTAL);quantityLine.setGravity(Gravity.END|Gravity.CENTER_VERTICAL);
        TextView qtyLabel=text("Qty: ",compact?12:14,primary,true);
        TextView qtyValue=text(QuantityMath.format(r.quantity),active?(compact?20:22):(compact?13:15),active?Color.rgb(0,120,45):primary,true);
        quantityLine.addView(qtyLabel);quantityLine.addView(qtyValue);right.addView(quantityLine);'''
if s.count(old_qty) != 1:
    raise SystemExit("Inventory quantity display not found")
s = s.replace(old_qty, new_qty, 1)
adapter.write_text(s)

monthly = root / "app" / "src" / "main" / "java" / "com" / "iceinventory" / "onhand" / "MonthlyInventoryActivity.java"
s = monthly.read_text()
old_onhand = '''    private String onHandText(){StringBuilder b=new StringBuilder(projectMetadata());for(MonthlyClientXlsxWriter.Product p:products.values())b.append("0\\t").append(tab(p.upc)).append('\\t').append(tab(p.description)).append("\\t$").append(money(p.retail)).append("\\r\\n");return b.toString();}'''
new_onhand = '''    private String onHandText(){StringBuilder b=new StringBuilder(projectMetadata()).append("Quantity\\tBarcode\\tDescription\\tPrice\\tCategory Description\\r\\n");for(MonthlyClientXlsxWriter.Product p:products.values())b.append("0\\t").append(tab(p.upc)).append('\\t').append(tab(p.description)).append("\\t$").append(money(p.retail)).append('\\t').append(tab(p.categoryName)).append("\\r\\n");return b.toString();}'''
if s.count(old_onhand) != 1:
    raise SystemExit("Monthly OnHand writer not found")
s = s.replace(old_onhand, new_onhand, 1)
monthly.write_text(s)

main = root / "app" / "src" / "main" / "java" / "com" / "iceinventory" / "onhand" / "MainActivity.java"
s = main.read_text().replace("Onhand Inventory 3.0.188", "Onhand Inventory 3.0.189")
s = s.replace("    private TextView summary;\n", "    private TextView summary;\n    private TextView cigaretteSummary;\n", 1)
old_summary_ui = '''        summary=text("",13,Color.WHITE,true);summary.setPadding(dp(2),dp(5),0,dp(3));root.addView(summary);

        LinearLayout reportBar='''
new_summary_ui = '''        summary=text("",13,Color.WHITE,true);summary.setPadding(dp(2),dp(5),0,dp(3));root.addView(summary);
        cigaretteSummary=text("🚬 CIGARETTES QTY: 0",16,Color.BLACK,true);
        cigaretteSummary.setGravity(Gravity.CENTER);cigaretteSummary.setPadding(dp(5),dp(5),dp(5),dp(5));cigaretteSummary.setBackgroundColor(gold());
        root.addView(cigaretteSummary,new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT,dp(38)));

        LinearLayout reportBar='''
if s.count(old_summary_ui) != 1:
    raise SystemExit("Main summary UI not found")
s = s.replace(old_summary_ui, new_summary_ui, 1)
old_refresh = '''        double units=0;for(InventoryDb.Row r:allRows)units+=r.quantity;
        summary.setText(allRows.size()+" item lines  •  "+QuantityMath.format(units)+" total units");'''
new_refresh = '''        double units=0,cigarettes=0;for(InventoryDb.Row r:allRows){units+=r.quantity;String category=r.categoryName==null?"":r.categoryName.trim().toUpperCase(Locale.US);String rowLocation=r.location==null?"":r.location.trim().toUpperCase(Locale.US);if(category.contains("CIGARETTE")||(category.isEmpty()&&rowLocation.startsWith("CIG SHELF")))cigarettes+=r.quantity;}
        summary.setText(allRows.size()+" item lines  •  "+QuantityMath.format(units)+" total units");
        if(cigaretteSummary!=null)cigaretteSummary.setText("🚬 CIGARETTES QTY: "+QuantityMath.format(cigarettes));'''
if s.count(old_refresh) != 1:
    raise SystemExit("Main refresh summary not found")
s = s.replace(old_refresh, new_refresh, 1)
main.write_text(s)

checks = {
    "version": "versionName '3.0.189'" in gradle.read_text(),
    "db category": "public String categoryName;" in db.read_text() and "DB_VERSION = 4" in db.read_text(),
    "count file category": "Category Description" in monthly.read_text(),
    "import category": "category_description" in tab.read_text(),
    "live cigarette total": "CIGARETTES QTY:" in main.read_text() and "category.contains(\"CIGARETTE\")" in main.read_text(),
    "legacy location fallback": "rowLocation.startsWith(\"CIG SHELF\")" in main.read_text(),
    "active quantity emphasis": "active?(compact?20:22)" in adapter.read_text() and "Color.rgb(0,120,45)" in adapter.read_text(),
}
failed = [name for name, ok in checks.items() if not ok]
if failed:
    raise SystemExit("3.0.189 verification failed: " + ", ".join(failed))
print("Prepared iCE OnHand 3.0.189: live main-screen cigarette quantity with category-aware count files")
