#!/usr/bin/env python3
from pathlib import Path
import runpy

root = Path(__file__).resolve().parents[1]
workflow = root / ".github/workflows/build-apk.yml"
w = workflow.read_text()
seed = [
    ("Prepare and verify 3.0.208 Count User defaults and maximum quantity setting",
     "Prepare and verify 3.0.207 Victoria four-column customer report"),
    (".github/prepare_30208.py", ".github/prepare_30207.py"),
    ("iCE-Onhand-Inventory-3.0.208", "iCE-Onhand-Inventory-3.0.207"),
]
for old, new in seed:
    if old not in w:
        raise SystemExit(f"Initial workflow marker missing: {old}")
    w = w.replace(old, new)
workflow.write_text(w)

runpy.run_path(str(root / ".github" / "prepare_30207.py"), run_name="__main__")

w = workflow.read_text()
replacements = [
    ("Prepare and verify 3.0.207 Victoria four-column customer report",
     "Prepare and verify 3.0.208 Count User defaults and maximum quantity setting"),
    (".github/prepare_30207.py", ".github/prepare_30208.py"),
    ("iCE-Onhand-Inventory-3.0.207", "iCE-Onhand-Inventory-3.0.208"),
]
for old, new in replacements:
    if old not in w:
        raise SystemExit(f"Workflow marker missing: {old}")
    w = w.replace(old, new)
workflow.write_text(w)

gradle = root / "app/build.gradle"
s = gradle.read_text()
if "versionCode 30207" not in s or "versionName '3.0.207'" not in s:
    raise SystemExit("3.0.207 version source not found")
gradle.write_text(s.replace("versionCode 30207", "versionCode 30208", 1)
                     .replace("versionName '3.0.207'", "versionName '3.0.208'", 1))

manifest = root / "app/src/main/AndroidManifest.xml"
s = manifest.read_text()
if "iCE Onhand 3.0.207" not in s:
    raise SystemExit("3.0.207 app label missing")
manifest.write_text(s.replace("iCE Onhand 3.0.207", "iCE Onhand 3.0.208", 1))

main = root / "app/src/main/java/com/iceinventory/onhand/MainActivity.java"
s = main.read_text()
if "Onhand Inventory 3.0.207" not in s:
    raise SystemExit("3.0.207 screen version missing")
s = s.replace("Onhand Inventory 3.0.207", "Onhand Inventory 3.0.208", 1)

old = '    private static final String KEY_UNKNOWN_MODE="unknown_barcode_mode";'
new = old + '\n    private static final String KEY_MAX_QTY="maximum_quantity_per_barcode";'
if s.count(old) != 1:
    raise SystemExit("Unknown barcode preference declaration missing")
s = s.replace(old, new, 1)

old = '    private String getUnknownBarcodeMode(){return prefs().getString(KEY_UNKNOWN_MODE,"add");}'
new = '''    private String getUnknownBarcodeMode(){return prefs().getString(KEY_UNKNOWN_MODE,isMasterDevice()?"add":"ignore");}

    private int maximumQuantityPerBarcode(){return Math.max(0,prefs().getInt(KEY_MAX_QTY,0));}

    private String maximumQuantityLabel(){int limit=maximumQuantityPerBarcode();return limit==0?"No limit":String.valueOf(limit);}

    private void showMaximumQuantitySetting(){
        EditText input=new EditText(this);input.setSingleLine(true);input.setInputType(InputType.TYPE_CLASS_NUMBER);
        input.setHint("0 = no limit");int current=maximumQuantityPerBarcode();if(current>0)input.setText(String.valueOf(current));
        new AlertDialog.Builder(this).setTitle("Maximum Quantity Per Barcode")
                .setMessage("Set a maximum total quantity for each barcode across all locations. If a count goes over this number, OnHand will warn and let you confirm. Enter 0 for no limit.")
                .setView(input).setPositiveButton("Save",(d,w)->{
                    String value=input.getText().toString().trim();int limit=0;
                    try{if(!value.isEmpty())limit=Integer.parseInt(value);}catch(Exception e){toast("Enter a whole number from 0 to 2147483647");return;}
                    if(limit<0){toast("Maximum quantity cannot be negative");return;}
                    prefs().edit().putInt(KEY_MAX_QTY,limit).apply();
                    toast("Maximum quantity set to "+(limit==0?"No limit":String.valueOf(limit)));
                }).setNegativeButton("Cancel",null).show();
    }

    private void confirmMaximumQuantity(String barcodeCode,int projectedTotal,Runnable continueCount){
        int limit=maximumQuantityPerBarcode();
        if(limit<=0||projectedTotal<=limit){continueCount.run();return;}
        new AlertDialog.Builder(this).setTitle("Maximum Quantity Exceeded")
                .setMessage("Barcode "+barcodeCode+" would total "+projectedTotal+" across all locations. The maximum is "+limit+". Continue with this count?")
                .setPositiveButton("Continue",(d,w)->continueCount.run())
                .setNegativeButton("Cancel",null).show();
    }'''
if s.count(old) != 1:
    raise SystemExit("Unknown barcode default method missing")
s = s.replace(old, new, 1)

old = '''        box.addView(unknown,new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT,dp(50)));
        new AlertDialog.Builder(this).setTitle("Options").setView(box).setPositiveButton("Done",null).show();'''
new = '''        box.addView(unknown,new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT,dp(50)));
        Button maxQty=button("Maximum Qty per Barcode: "+maximumQuantityLabel(),0);
        maxQty.setOnClickListener(v->showMaximumQuantitySetting());
        box.addView(maxQty,new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT,dp(50)));
        new AlertDialog.Builder(this).setTitle("Options").setView(box).setPositiveButton("Done",null).show();'''
if s.count(old) != 1:
    raise SystemExit("Options insertion point missing")
s = s.replace(old, new, 1)

old = '''    private void addItem() {
        String code=maybeGtin(barcode.getText().toString().trim());'''
new = '''    private void addItem(){addItem(false);}

    private void addItem(boolean confirmedAboveMaximum) {
        String code=maybeGtin(barcode.getText().toString().trim());'''
if s.count(old) != 1:
    raise SystemExit("Add Count method declaration missing")
s = s.replace(old, new, 1)

old = '''        if(q<=0){toast("Quantity must be greater than zero");focusQuantity();return;}
        String loc=location.getSelectedItem()==null?"Main":location.getSelectedItem().toString();'''
new = '''        if(q<=0){toast("Quantity must be greater than zero");focusQuantity();return;}
        int limit=maximumQuantityPerBarcode();
        int projected=db.quantityForBarcode(sessionId,code)+q;
        if(!confirmedAboveMaximum&&limit>0&&projected>limit){
            confirmMaximumQuantity(code,projected,()->addItem(true));return;
        }
        String loc=location.getSelectedItem()==null?"Main":location.getSelectedItem().toString();'''
if s.count(old) != 1:
    raise SystemExit("Add Count maximum check insertion point missing")
s = s.replace(old, new, 1)

old = '''    @Override public void onAddOne(InventoryDb.Row row) {
        db.incrementQuantity(row.id,1);lastBarcode=row.barcode;refreshList();
    }'''
new = '''    @Override public void onAddOne(InventoryDb.Row row) {
        int projected=db.quantityForBarcode(sessionId,row.barcode)+1;
        confirmMaximumQuantity(row.barcode,projected,()->{db.incrementQuantity(row.id,1);lastBarcode=row.barcode;refreshList();});
    }'''
if s.count(old) != 1:
    raise SystemExit("Existing-item plus action missing")
s = s.replace(old, new, 1)

old = '''                .setPositiveButton("Save",(dd,w)->{
                    int nq=r.quantity;try{nq=Integer.parseInt(q.getText().toString().trim());}catch(Exception ignored){}
                    String nl=loc.getSelectedItem()==null?"Main":loc.getSelectedItem().toString();
                    db.addLocation(nl);db.updateItem(r.id,d.getText().toString(),price.getText().toString().replace("$","").trim(),nq,nl);refreshList();
                })'''
new = '''                .setPositiveButton("Save",(dd,w)->{
                    int nq=r.quantity;try{nq=Integer.parseInt(q.getText().toString().trim());}catch(Exception ignored){}
                    String nl=loc.getSelectedItem()==null?"Main":loc.getSelectedItem().toString();
                    int projected=db.quantityForBarcode(sessionId,r.barcode)-r.quantity+nq;
                    confirmMaximumQuantity(r.barcode,projected,()->{db.addLocation(nl);db.updateItem(r.id,d.getText().toString(),price.getText().toString().replace("$","").trim(),nq,nl);refreshList();});
                })'''
if s.count(old) != 1:
    raise SystemExit("Edit Count save action missing")
s = s.replace(old, new, 1)

old = '''            int amount=data.getIntExtra(QuantityActivity.EXTRA_QUANTITY,0);
            if(amount>0&&pendingQuantityRowId>0) {
                db.incrementQuantity(pendingQuantityRowId,amount);lastBarcode=pendingQuantityBarcode;refreshList();
            }
            pendingQuantityRowId=-1;pendingQuantityBarcode="";'''
new = '''            int amount=data.getIntExtra(QuantityActivity.EXTRA_QUANTITY,0);
            if(amount>0&&pendingQuantityRowId>0) {
                final long rowId=pendingQuantityRowId;final String code=pendingQuantityBarcode;
                int projected=db.quantityForBarcode(sessionId,code)+amount;
                confirmMaximumQuantity(code,projected,()->{db.incrementQuantity(rowId,amount);lastBarcode=code;refreshList();});
            }
            pendingQuantityRowId=-1;pendingQuantityBarcode="";'''
if s.count(old) != 1:
    raise SystemExit("Add Quantity result action missing")
s = s.replace(old, new, 1)

main.write_text(s)

checks = {
    "release version": "versionName '3.0.208'" in gradle.read_text(),
    "Count User Ignore default": 'prefs().getString(KEY_UNKNOWN_MODE,isMasterDevice()?"add":"ignore")' in s,
    "Master saved behavior preserved": 'getString(KEY_UNKNOWN_MODE,isMasterDevice()?"add":"ignore")' in s,
    "maximum quantity setting visible": "Maximum Qty per Barcode:" in s,
    "zero means no limit": "Enter 0 for no limit" in s,
    "warning allows confirmation": 'setPositiveButton("Continue"' in s and 'setNegativeButton("Cancel"' in s,
    "new count protected": "db.quantityForBarcode(sessionId,code)+q" in s,
    "plus-one protected": "db.quantityForBarcode(sessionId,row.barcode)+1" in s,
    "add quantity protected": "db.quantityForBarcode(sessionId,code)+amount" in s,
    "workflow uses this release": "prepare_30208.py" in workflow.read_text() and "3.0.208" in workflow.read_text(),
}
failed = [name for name, passed in checks.items() if not passed]
if failed:
    raise SystemExit("3.0.208 checks failed: " + ", ".join(failed))
print("Prepared iCE OnHand 3.0.208: Count Users default to Ignore and configurable per-barcode quantity warning added.")
