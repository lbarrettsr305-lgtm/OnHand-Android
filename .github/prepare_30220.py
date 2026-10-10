#!/usr/bin/env python3
from pathlib import Path
import runpy

root=Path(__file__).resolve().parent.parent
workflow=root/".github/workflows/build-apk.yml"
w=workflow.read_text()
for new,old in [
    ("Prepare and verify 3.0.220 external scanner flow","Prepare and verify 3.0.219 replace import instructions"),
    (".github/prepare_30220.py",".github/prepare_30219.py"),
    ("iCE-Onhand-Inventory-3.0.220","iCE-Onhand-Inventory-3.0.219"),
]:
    if new not in w: raise SystemExit("3.0.220 workflow seed missing: "+new)
    w=w.replace(new,old)
workflow.write_text(w)
runpy.run_path(str(root/".github/prepare_30219.py"),run_name="__main__")
w=workflow.read_text()
for old,new in [
    ("Prepare and verify 3.0.219 replace import instructions","Prepare and verify 3.0.220 external scanner flow"),
    (".github/prepare_30219.py",".github/prepare_30220.py"),
    ("iCE-Onhand-Inventory-3.0.219","iCE-Onhand-Inventory-3.0.220"),
]:
    if old not in w: raise SystemExit("3.0.219 workflow marker missing: "+old)
    w=w.replace(old,new)
workflow.write_text(w)

main=root/"app/src/main/java/com/iceinventory/onhand/MainActivity.java"
s=main.read_text()
def once(old,new,label):
    global s
    if s.count(old)!=1: raise SystemExit(label+" anchor missing or ambiguous")
    s=s.replace(old,new,1)

once("import android.widget.ArrayAdapter;","import android.widget.AdapterView;\nimport android.widget.ArrayAdapter;","Spinner import")
once('private static final String KEY_AUTO_GTIN="auto_gtin14";',
     'private static final String KEY_AUTO_GTIN="auto_gtin14";\n    private static final String KEY_AUTO_INCREMENT="auto_increment_scan";\n    private static final String KEY_MAX_QTY="max_qty_per_item";\n    private static final String KEY_LOCATION_PREFIX="last_location_session_";',
     "Scanning preference keys")
once('Button scan=button("📷 Scan",1);scan.setOnClickListener(v->scanBarcode());',
     'Button scan=button("Camera",1);scan.setOnClickListener(v->scanBarcode());',
     "Camera button label")
once('barcode.setHint("Scan or type barcode");',
     'barcode.setHint("External scanner or type barcode");',
     "Barcode field hint")
once('        refreshLocations();\n        refreshList();\n    }',
     '        refreshLocations();\n        refreshList();\n        barcode.post(this::focusBarcodeWithoutKeyboard);\n    }',
     "Startup barcode focus")
once('        TextView display=text("Display",16,gold(),true);',
     '        box.addView(optionSwitch("Auto-increment count on scan",KEY_AUTO_INCREMENT,false));\n        Button unknown=button("Unknown Barcode Behavior: "+friendlyUnknownMode(),0);\n        unknown.setOnClickListener(v->showUnknownBarcodeMode());\n        box.addView(unknown,new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT,dp(50)));\n        Button maxQty=button("Maximum quantity per item: "+getMaxQty(),0);\n        maxQty.setOnClickListener(v->showMaxQtyDialog());\n        box.addView(maxQty,new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT,dp(50)));\n        TextView display=text("Display",16,gold(),true);',
     "Scanning settings controls")
once('        Button unknown=button("Unknown Barcode Behavior: "+friendlyUnknownMode(),0);\n        unknown.setOnClickListener(v->showUnknownBarcodeMode());\n        box.addView(unknown,new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT,dp(50)));\n        new AlertDialog.Builder(this).setTitle("Options")',
     '        new AlertDialog.Builder(this).setTitle("Options")',
     "Old unknown control position")
once('    private String getUnknownBarcodeMode(){return prefs().getString(KEY_UNKNOWN_MODE,"add");}',
     '''    private String getUnknownBarcodeMode(){return prefs().getString(KEY_UNKNOWN_MODE,"ignore");}

    private int getMaxQty(){return Math.max(1,prefs().getInt(KEY_MAX_QTY,9999));}

    private void showMaxQtyDialog() {
        EditText input=new EditText(this);
        input.setInputType(InputType.TYPE_CLASS_NUMBER);
        input.setText(String.valueOf(getMaxQty()));
        input.setSelection(input.getText().length());
        new AlertDialog.Builder(this).setTitle("Maximum quantity per item")
                .setMessage("Counts cannot exceed this quantity at one location.")
                .setView(input).setPositiveButton("Save",(d,w)->{
                    try {
                        int value=Integer.parseInt(input.getText().toString().trim());
                        if(value<1)throw new NumberFormatException();
                        prefs().edit().putInt(KEY_MAX_QTY,value).apply();
                        toast("Maximum quantity saved");
                    } catch(Exception e) { toast("Enter a maximum quantity of at least 1"); }
                }).setNegativeButton("Cancel",null).show();
    }''',
     "Unknown barcode default and max quantity")
once('        description.setText(existing.description==null?"":existing.description);\n            currentPrice=existing.price==null?"":existing.price;\n            focusQuantity();\n            return;',
     '''        description.setText(existing.description==null?"":existing.description);
            currentPrice=existing.price==null?"":existing.price;
            lastBarcode=code;
            applyFilter();
            scrollToLastBarcode();
            if(prefs().getBoolean(KEY_AUTO_INCREMENT,false)) {
                String loc=location.getSelectedItem()==null?"Main":location.getSelectedItem().toString();
                int current=db.quantityForBarcodeAtLocation(sessionId,code,loc);
                if(current>=getMaxQty()) {
                    toast("Maximum quantity reached for "+loc);
                    focusBarcodeWithoutKeyboard();
                    return;
                }
                db.addLocation(loc);
                db.addOrIncrement(sessionId,code,description.getText().toString(),currentPrice,1,loc);
                barcode.setText("");description.setText("");qty.setText("");currentPrice="";
                refreshList();
                focusBarcodeWithoutKeyboard();
                return;
            }
            focusQuantity();
            return;''',
     "Existing barcode scan behavior")
once('        if(q<=0){toast("Quantity must be greater than zero");focusQuantity();return;}',
     '        if(q<=0){toast("Quantity must be greater than zero");focusQuantity();return;}\n        if(q>getMaxQty()){toast("Maximum quantity is "+getMaxQty());focusQuantity();return;}',
     "Maximum quantity validation")
once('        q=Math.max(0,q+delta);',
     '        q=Math.max(0,Math.min(getMaxQty(),q+delta));',
     "Quantity button cap")
once('    @Override public void onAddOne(InventoryDb.Row row) {\n        db.incrementQuantity(row.id,1);lastBarcode=row.barcode;refreshList();\n    }',
     '    @Override public void onAddOne(InventoryDb.Row row) {\n        if(row.quantity>=getMaxQty()){toast("Maximum quantity is "+getMaxQty());return;}\n        db.incrementQuantity(row.id,1);lastBarcode=row.barcode;refreshList();\n    }',
     "List increment cap")
once('        adapter.setRows(visibleRows);',
     '        adapter.setRows(visibleRows);\n        scrollToLastBarcode();',
     "Scroll to highlighted scan")
once('    private void applyFilter() {',
     '''    private void scrollToLastBarcode() {
        if(list==null||lastBarcode==null||lastBarcode.isEmpty())return;
        list.post(()->{
            for(int i=0;i<visibleRows.size();i++) {
                InventoryDb.Row row=visibleRows.get(i);
                if(lastBarcode.equals(row.barcode)){list.setSelection(i);return;}
            }
        });
    }

    private void applyFilter() {''',
     "Highlight scroll helper")
# Save a location per inventory and refresh the visible location filter immediately.
once('        ArrayAdapter<String> a=new ArrayAdapter<>(this,android.R.layout.simple_spinner_dropdown_item,locs);\n        location.setAdapter(a);',
     '''        ArrayAdapter<String> a=new ArrayAdapter<>(this,android.R.layout.simple_spinner_dropdown_item,locs);
        location.setAdapter(a);
        String key=KEY_LOCATION_PREFIX+sessionId;
        String preferred=prefs().getString(key,"");
        int index=locs.indexOf(preferred);
        if(index<0)index=locs.indexOf("Main");
        if(index>=0)location.setSelection(index);
        location.setOnItemSelectedListener(new AdapterView.OnItemSelectedListener(){
            @Override public void onItemSelected(AdapterView<?> parent,View view,int position,long id) {
                Object selected=parent.getItemAtPosition(position);
                if(selected!=null)prefs().edit().putString(key,selected.toString()).apply();
                applyFilter();
            }
            @Override public void onNothingSelected(AdapterView<?> parent){}
        });''',
     "Remember selected location")
# Cap one-at-a-time scan increments at the selected location.
db=root/"app/src/main/java/com/iceinventory/onhand/InventoryDb.java"
d=db.read_text()
needle='    public void incrementQuantity(long id, int delta) {'
if d.count(needle)!=1: raise SystemExit("quantity update method anchor missing or ambiguous")
d=d.replace(needle,'''    public int quantityForBarcodeAtLocation(long sessionId,String barcode,String location) {
        SQLiteDatabase r=getReadableDatabase();
        try(Cursor c=r.rawQuery("SELECT COALESCE(SUM(quantity),0) FROM items WHERE session_id=? AND barcode=? AND location=?",
                new String[]{String.valueOf(sessionId),barcode,location})) {
            return c.moveToFirst()?c.getInt(0):0;
        }
    }

'''+needle,1)
db.write_text(d)

gradle=root/"app/build.gradle"
g=gradle.read_text()
if "versionCode 30219" not in g or "versionName '3.0.219'" not in g:raise SystemExit("3.0.219 Gradle version missing")
gradle.write_text(g.replace("versionCode 30219","versionCode 30220",1).replace("versionName '3.0.219'","versionName '3.0.220'",1))
manifest=root/"app/src/main/AndroidManifest.xml"
m=manifest.read_text()
if m.count("iCE Onhand 3.0.219")!=1:raise SystemExit("3.0.219 manifest label missing")
manifest.write_text(m.replace("iCE Onhand 3.0.219","iCE Onhand 3.0.220",1))
s=main.read_text()
if s.count("Onhand Inventory 3.0.219")!=1:raise SystemExit("3.0.219 home label missing")
main.write_text(s.replace("Onhand Inventory 3.0.219","Onhand Inventory 3.0.220",1))

checks={
    "hardware scanner hint and distinct camera button": "External scanner or type barcode" in main.read_text() and 'button("Camera",1)' in main.read_text(),
    "unknown barcode defaults to ignore": 'getString(KEY_UNKNOWN_MODE,"ignore")' in main.read_text(),
    "auto increment and max quantity in Scanning options": 'optionSwitch("Auto-increment count on scan"' in main.read_text() and 'Maximum quantity per item:' in main.read_text(),
    "selected location remembered per inventory": "KEY_LOCATION_PREFIX+sessionId" in main.read_text(),
    "scanned barcode highlighted and scrolled": "lastBarcode=code;\n            applyFilter();\n            scrollToLastBarcode();" in main.read_text(),
    "quantity max enforced": "if(q>getMaxQty())" in main.read_text(),
    "scan increment checks current location quantity": "quantityForBarcodeAtLocation(sessionId,code,loc)" in main.read_text(),
    "version labels": "versionName '3.0.220'" in gradle.read_text() and "iCE Onhand 3.0.220" in manifest.read_text() and "Onhand Inventory 3.0.220" in main.read_text(),
    "workflow release markers": ".github/prepare_30220.py" in workflow.read_text() and "3.0.220" in workflow.read_text(),
}
failed=[k for k,v in checks.items() if not v]
if failed:raise SystemExit("3.0.220 validation failed: "+", ".join(failed))
print("Prepared iCE OnHand 3.0.220 with external scanner, location, count highlighting, and scan settings fixes.")
