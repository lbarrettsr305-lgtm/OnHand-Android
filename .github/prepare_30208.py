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

    private double maximumQuantityPerBarcode(){try{return Math.max(0,QuantityMath.parse(prefs().getString(KEY_MAX_QTY,"0")));}catch(Exception ignored){return 0;}}

    private String maximumQuantityLabel(){double limit=maximumQuantityPerBarcode();return limit==0?"No limit":QuantityMath.format(limit);}

    private void showMaximumQuantitySetting(){
        EditText input=new EditText(this);input.setSingleLine(true);input.setInputType(InputType.TYPE_CLASS_NUMBER|InputType.TYPE_NUMBER_FLAG_DECIMAL);
        input.setHint("0 = no limit");String current=prefs().getString(KEY_MAX_QTY,"0");if(!"0".equals(current))input.setText(current);
        new AlertDialog.Builder(this).setTitle("Maximum Quantity Per Barcode")
                .setMessage("Set a maximum total quantity for each barcode across all locations. If a count goes over this number, OnHand will warn and let you confirm. Enter 0 for no limit.")
                .setView(input).setPositiveButton("Save",(d,w)->{
                    String value=input.getText().toString().trim();double limit=0;
                    try{if(!value.isEmpty())limit=QuantityMath.parse(value);}catch(Exception e){toast("Enter a valid quantity");return;}
                    if(limit<0){toast("Maximum quantity cannot be negative");return;}
                    String saved=QuantityMath.format(limit);prefs().edit().putString(KEY_MAX_QTY,saved).apply();
                    toast("Maximum quantity set to "+(limit==0?"No limit":saved));
                }).setNegativeButton("Cancel",null).show();
    }

    private void confirmMaximumQuantity(String barcodeCode,double projectedTotal,Runnable continueCount){
        double limit=maximumQuantityPerBarcode();
        if(limit<=0||projectedTotal<=limit){continueCount.run();return;}
        new AlertDialog.Builder(this).setTitle("Maximum Quantity Exceeded")
                .setMessage("Barcode "+barcodeCode+" would total "+QuantityMath.format(projectedTotal)+" across all locations. The maximum is "+QuantityMath.format(limit)+". Continue with this count?")
                .setPositiveButton("Continue",(d,w)->continueCount.run())
                .setNegativeButton("Cancel",null).show();
    }'''
if s.count(old) != 1:
    raise SystemExit("Unknown barcode default method missing")
s = s.replace(old, new, 1)

old = '''        Button selectCounter=button("CHANGE / SELECT COUNTER NAME",1);selectCounter.setTypeface(Typeface.DEFAULT,Typeface.BOLD);selectCounter.setTextSize(16);
        box.addView(selectCounter,new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT,dp(64)));
        TextView protectedMessage=text("Scan, display, inventory, and administrative settings are protected. A Master can temporarily unlock them with the Master PIN.",13,Color.LTGRAY,false);'''
new = '''        Button selectCounter=button("CHANGE / SELECT COUNTER NAME",1);selectCounter.setTypeface(Typeface.DEFAULT,Typeface.BOLD);selectCounter.setTextSize(16);
        box.addView(selectCounter,new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT,dp(64)));
        Button maxQty=button("Maximum Qty per Barcode: "+maximumQuantityLabel(),0);
        maxQty.setOnClickListener(v->showMaximumQuantitySetting());
        box.addView(maxQty,new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT,dp(58)));
        TextView protectedMessage=text("Scan, display, inventory, and administrative settings are protected. A Master can temporarily unlock them with the Master PIN.",13,Color.LTGRAY,false);'''
if s.count(old) != 1:
    raise SystemExit("Count User Options insertion point missing")
s = s.replace(old, new, 1)

old = '''    private void saveEnteredCount(String code,String desc,String price,double amount,String loc){
        db.addLocation(loc);db.addOrIncrement(sessionId,code,desc,price,amount,loc);lastBarcode=code;
        barcode.setText("");description.setText("");qty.setText("");currentPrice="";updatePricePreview();refreshList();
        if(continuousPhoneScan){hideKeyboard();barcode.postDelayed(this::scanBarcode,180);}else focusBarcodeWithoutKeyboard();
        noteCountForSafety();setCountingKeyboardMode(false);
    }'''
new = '''    private void saveEnteredCount(String code,String desc,String price,double amount,String loc){saveEnteredCount(code,desc,price,amount,loc,false);}

    private void saveEnteredCount(String code,String desc,String price,double amount,String loc,boolean confirmedAboveMaximum){
        double projected=db.quantityForBarcode(sessionId,code)+amount;
        if(!confirmedAboveMaximum&&maximumQuantityPerBarcode()>0&&projected>maximumQuantityPerBarcode()){
            confirmMaximumQuantity(code,projected,()->saveEnteredCount(code,desc,price,amount,loc,true));return;
        }
        db.addLocation(loc);db.addOrIncrement(sessionId,code,desc,price,amount,loc);lastBarcode=code;
        barcode.setText("");description.setText("");qty.setText("");currentPrice="";updatePricePreview();refreshList();
        if(continuousPhoneScan){hideKeyboard();barcode.postDelayed(this::scanBarcode,180);}else focusBarcodeWithoutKeyboard();
        noteCountForSafety();setCountingKeyboardMode(false);
    }'''
if s.count(old) != 1:
    at = s.find("saveEnteredCount")
    context = s[max(0, at-400):at+1200] if at >= 0 else "saveEnteredCount is absent"
    raise SystemExit("Count save method missing; generated source context: " + context)
s = s.replace(old, new, 1)

old = '''    @Override public void onAddOne(InventoryDb.Row row) {
        if(!requireCurrentCount()||!requireRowAtCurrentLocation(row))return;
        db.incrementQuantity(row.id,1);lastBarcode=row.barcode;refreshList();noteCountForSafety();
    }'''
new = '''    @Override public void onAddOne(InventoryDb.Row row) {
        if(!requireCurrentCount()||!requireRowAtCurrentLocation(row))return;
        double projected=db.quantityForBarcode(sessionId,row.barcode)+1;
        confirmMaximumQuantity(row.barcode,projected,()->{db.incrementQuantity(row.id,1);lastBarcode=row.barcode;refreshList();noteCountForSafety();});
    }'''
if s.count(old) != 1:
    raise SystemExit("Existing-item plus action missing")
s = s.replace(old, new, 1)

old = '''            double amount=data.getDoubleExtra(QuantityActivity.EXTRA_QUANTITY,0);
            if(amount>0&&pendingQuantityRowId>0) {
                db.incrementQuantity(pendingQuantityRowId,amount);lastBarcode=pendingQuantityBarcode;refreshList();
            }
            pendingQuantityRowId=-1;pendingQuantityBarcode="";'''
new = '''            double amount=data.getDoubleExtra(QuantityActivity.EXTRA_QUANTITY,0);
            if(amount>0&&pendingQuantityRowId>0) {
                final long rowId=pendingQuantityRowId;final String code=pendingQuantityBarcode;
                double projected=db.quantityForBarcode(sessionId,code)+amount;
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
    "new count protected": "maximumQuantityPerBarcode()>0&&projected>maximumQuantityPerBarcode()" in s and "saveEnteredCount(code,desc,price,amount,loc,true)" in s,
    "plus-one protected": "db.quantityForBarcode(sessionId,row.barcode)+1" in s,
    "add quantity protected": "db.quantityForBarcode(sessionId,code)+amount" in s and "confirmMaximumQuantity(code,projected" in s,
    "workflow uses this release": "prepare_30208.py" in workflow.read_text() and "3.0.208" in workflow.read_text(),
}
failed = [name for name, passed in checks.items() if not passed]
if failed:
    raise SystemExit("3.0.208 checks failed: " + ", ".join(failed))
print("Prepared iCE OnHand 3.0.208: Count Users default to Ignore and configurable per-barcode quantity warning added.")
