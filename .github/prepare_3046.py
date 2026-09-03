from pathlib import Path
import re
import runpy

# First apply the proven 3.0.45 layout/format-flow patch.
runpy.run_path('.github/prepare_3045.py', run_name='__main__')

# --- MainActivity: preserve 3.0.45 layout, restore correct logo, flexible barcode matching,
# and reuse the import filename as the export filename. ---
p=Path('app/src/main/java/com/iceinventory/onhand/MainActivity.java')
s=p.read_text()

# 3.0.45 temporarily pointed at the wrong bitmap. The vector is the approved stylized C/person logo.
s=s.replace('R.drawable.ice_onhand_approved','R.drawable.ice_onhand_icon')

old='''        InventoryDb.Row existing=db.latestForBarcode(sessionId,code);\n        if(existing!=null) {\n            description.setText(existing.description==null?"":existing.description);\n            currentPrice=existing.price==null?"":existing.price;\n            focusQuantity();\n            return;\n        }\n'''
new='''        InventoryDb.Row existing=db.latestForBarcode(sessionId,code);\n        if(existing!=null) {\n            useSavedBarcodeMatch(existing,false);\n            return;\n        }\n\n        List<InventoryDb.Row> flexible=flexibleBarcodeMatches(code);\n        if(flexible.size()==1) {\n            useSavedBarcodeMatch(flexible.get(0),true);\n            return;\n        }\n        if(flexible.size()>1) {\n            showFlexibleBarcodeChoices(flexible);\n            return;\n        }\n'''
if old not in s: raise SystemExit('3.0.46 target missing: exact barcode block')
s=s.replace(old,new,1)

marker='''    private void scanFeedback() {\n'''
helpers='''    private void useSavedBarcodeMatch(InventoryDb.Row row,boolean flexible) {\n        if(row==null)return;\n        String actual=row.barcode==null?"":row.barcode.trim();\n        barcode.setText(actual);barcode.setSelection(actual.length());\n        description.setText(row.description==null?"":row.description);\n        currentPrice=row.price==null?"":row.price;\n        if(flexible)toast("Matched saved barcode: "+actual);\n        focusQuantity();\n    }\n\n    private List<InventoryDb.Row> flexibleBarcodeMatches(String input) {\n        LinkedHashMap<String,InventoryDb.Row> unique=new LinkedHashMap<>();\n        for(InventoryDb.Row r:allRows) {\n            if(r==null||r.barcode==null||!barcodesFlexibleMatch(input,r.barcode))continue;\n            InventoryDb.Row prior=unique.get(r.barcode);\n            if(prior==null||r.updatedAt>prior.updatedAt)unique.put(r.barcode,r);\n        }\n        return new ArrayList<>(unique.values());\n    }\n\n    private boolean barcodesFlexibleMatch(String a,String b) {\n        if(a==null||b==null)return false;\n        String x=a.trim(),y=b.trim();\n        if(x.equals(y))return true;\n        if(!x.matches("\\\\d+")||!y.matches("\\\\d+"))return false;\n        if(x.length()<8||y.length()<8)return false;\n        List<String> xv=barcodeVariants(x),yv=barcodeVariants(y);\n        for(String p:xv)for(String q:yv)if(p.length()>=8&&p.equals(q))return true;\n        return false;\n    }\n\n    private List<String> barcodeVariants(String raw) {\n        ArrayList<String> v=new ArrayList<>();\n        String s=raw==null?"":raw.trim();\n        addBarcodeVariant(v,s);\n        if(!s.matches("\\\\d+"))return v;\n        addBarcodeVariant(v,stripBarcodeZeros(s));\n        if(s.length()>=9) {\n            String noCheck=s.substring(0,s.length()-1);\n            addBarcodeVariant(v,noCheck);\n            addBarcodeVariant(v,stripBarcodeZeros(noCheck));\n        }\n        return v;\n    }\n\n    private String stripBarcodeZeros(String s) {\n        int i=0;while(i<s.length()-1&&s.charAt(i)=='0')i++;return s.substring(i);\n    }\n\n    private void addBarcodeVariant(List<String> list,String value) {\n        if(value!=null&&!value.isEmpty()&&!list.contains(value))list.add(value);\n    }\n\n    private void showFlexibleBarcodeChoices(List<InventoryDb.Row> matches) {\n        String[] labels=new String[matches.size()];\n        for(int i=0;i<matches.size();i++) {\n            InventoryDb.Row r=matches.get(i);\n            String d=r.description==null?"":r.description.trim();\n            labels[i]=r.barcode+(d.isEmpty()?"":"  •  "+d);\n        }\n        new AlertDialog.Builder(this).setTitle("Choose matching barcode")\n                .setItems(labels,(d,which)->useSavedBarcodeMatch(matches.get(which),true))\n                .setNegativeButton("Cancel",null).show();\n    }\n\n'''
if marker not in s: raise SystemExit('3.0.46 target missing: scanFeedback marker')
s=s.replace(marker,helpers+marker,1)

old_export='''        name.setText(safeFileName(sessionName)+"_"+new SimpleDateFormat("yyyy-MM-dd_HHmm",Locale.US).format(new Date())+".txt");\n'''
new_export='''        String defaultName=prefs().getString(importFileNameKey(),"");\n        if(defaultName==null||defaultName.trim().isEmpty())defaultName=safeFileName(sessionName)+".txt";\n        name.setText(cleanTextName(defaultName));\n'''
if old_export not in s: raise SystemExit('3.0.46 target missing: export filename')
s=s.replace(old_export,new_export,1)

old_import='''    private void readImport(Uri uri) {\n        if(uri==null)return;\n        try(InputStream is=getContentResolver().openInputStream(uri);\n            BufferedReader br=new BufferedReader(new InputStreamReader(is,StandardCharsets.UTF_8))) {\n            int imported=TabTextUtils.importRows(br,db,sessionId,prefs(),prefs().getBoolean(KEY_AUTO_GTIN,false));\n            refreshLocations();refreshList();toast("Imported "+imported+" tab-delimited TXT rows");\n        } catch(Exception e){showError("Import failed",e);}\n    }\n'''
new_import='''    private void readImport(Uri uri) {\n        if(uri==null)return;\n        String selectedName=displayNameForImport(uri);\n        if(!selectedName.isEmpty())prefs().edit().putString(importFileNameKey(),selectedName).apply();\n        try(InputStream is=getContentResolver().openInputStream(uri);\n            BufferedReader br=new BufferedReader(new InputStreamReader(is,StandardCharsets.UTF_8))) {\n            int imported=TabTextUtils.importRows(br,db,sessionId,prefs(),prefs().getBoolean(KEY_AUTO_GTIN,false));\n            refreshLocations();refreshList();toast("Imported "+imported+" tab-delimited TXT rows");\n        } catch(Exception e){showError("Import failed",e);}\n    }\n\n    private String importFileNameKey(){return "last_import_filename_"+sessionId;}\n\n    private String displayNameForImport(Uri uri) {\n        String name="";\n        try(android.database.Cursor c=getContentResolver().query(uri,new String[]{android.provider.OpenableColumns.DISPLAY_NAME},null,null,null)) {\n            if(c!=null&&c.moveToFirst())name=c.getString(0);\n        } catch(Exception ignored){}\n        if(name==null||name.trim().isEmpty()) {\n            String p=uri.getLastPathSegment();name=p==null?"":p;\n        }\n        name=name.trim();\n        int slash=Math.max(name.lastIndexOf('/'),name.lastIndexOf('\\\\'));if(slash>=0)name=name.substring(slash+1);\n        int dot=name.lastIndexOf('.');if(dot>0)name=name.substring(0,dot);\n        return name.isEmpty()?"":name+".txt";\n    }\n'''
if old_import not in s: raise SystemExit('3.0.46 target missing: readImport')
s=s.replace(old_import,new_import,1)

p.write_text(s)

# --- InventoryDb: allow imported Scan Date / Scan Time to preserve a row's scan timestamp. ---
p=Path('app/src/main/java/com/iceinventory/onhand/InventoryDb.java')
s=p.read_text()
pattern=r'''    public void addOrIncrement\(long sessionId, String barcode, String description, String price, int quantity, String location\) \{.*?\n    \}\n\n    public void setQuantity'''
replacement='''    public void addOrIncrement(long sessionId, String barcode, String description, String price, int quantity, String location) {\n        addOrIncrementAt(sessionId,barcode,description,price,quantity,location,System.currentTimeMillis());\n    }\n\n    public void addOrIncrementAt(long sessionId, String barcode, String description, String price, int quantity, String location, long updatedAt) {\n        if (sessionId <= 0) throw new IllegalStateException("No active inventory session");\n        SQLiteDatabase db = getWritableDatabase();\n        String safeBarcode = barcode == null ? "" : barcode.trim();\n        String safeLocation = location == null || location.trim().isEmpty() ? "Main" : location.trim();\n        long when=updatedAt>0?updatedAt:System.currentTimeMillis();\n        String[] args = { String.valueOf(sessionId), safeBarcode, safeLocation };\n        try (Cursor c = db.rawQuery("SELECT id,quantity FROM items WHERE session_id=? AND barcode=? AND location=?", args)) {\n            if (c.moveToFirst()) {\n                ContentValues cv = new ContentValues();\n                cv.put("quantity", c.getInt(1) + quantity);\n                if (description != null && !description.trim().isEmpty()) cv.put("description", description.trim());\n                if (price != null && !price.trim().isEmpty()) cv.put("price", price.trim());\n                cv.put("updated_at", when);\n                db.update("items", cv, "id=?", new String[]{String.valueOf(c.getLong(0))});\n                return;\n            }\n        }\n        ContentValues cv = new ContentValues();\n        cv.put("session_id", sessionId);\n        cv.put("barcode", safeBarcode);\n        cv.put("description", description == null ? "" : description.trim());\n        cv.put("price", price == null ? "" : price.trim());\n        cv.put("quantity", quantity);\n        cv.put("location", safeLocation);\n        cv.put("updated_at", when);\n        db.insertOrThrow("items", null, cv);\n    }\n\n    public void setQuantity'''
s2,n=re.subn(pattern,replacement,s,count=1,flags=re.S)
if n!=1: raise SystemExit('3.0.46 target missing: InventoryDb addOrIncrement')
p.write_text(s2)

# --- QuantityActivity: prevent a spacer LayoutParams cast crash on the multiplication keypad. ---
p=Path('app/src/main/java/com/iceinventory/onhand/QuantityActivity.java')
s=p.read_text()
old='''                View spacer=new View(this);\n                keypad.addView(spacer,new ViewGroup.LayoutParams(0,0));\n                GridLayout.LayoutParams lp=(GridLayout.LayoutParams)spacer.getLayoutParams();\n                lp.width=0;lp.height=dp(54);lp.columnSpec=GridLayout.spec(GridLayout.UNDEFINED,1f);\n                spacer.setLayoutParams(lp);\n'''
new='''                View spacer=new View(this);\n                GridLayout.LayoutParams lp=new GridLayout.LayoutParams();\n                lp.width=0;lp.height=dp(54);lp.columnSpec=GridLayout.spec(GridLayout.UNDEFINED,1f);\n                keypad.addView(spacer,lp);\n'''
if old not in s: raise SystemExit('3.0.46 target missing: quantity keypad spacer')
p.write_text(s.replace(old,new,1))

print('Prepared iCE Onhand 3.0.46: locked 3.0.45 layout + correct logo + flexible barcode + filename reuse + timestamps')
