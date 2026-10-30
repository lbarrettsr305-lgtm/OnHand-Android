#!/usr/bin/env python3
"""OnHand 3.0.244: require verification before quantity subtractions."""
from pathlib import Path
import os
import runpy

root = Path(__file__).resolve().parents[1]
workflow = root / ".github/workflows/build-apk.yml"


def replace_once(path, old, new, label):
    data = path.read_text()
    count = data.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected one anchor, found {count}")
    path.write_text(data.replace(old, new, 1))


# Reapply the validated 3.0.243 preparation chain from its clean release base.
if os.environ.get("ONHAND_PREPARED_30243") != "1":
    w = workflow.read_text()
    for current, previous, expected in [
        ("Prepare and verify 3.0.244 negative quantity safeguards",
         "Prepare and verify 3.0.243 Victoria counted batch workflow", 1),
        (".github/prepare_30244.py", ".github/prepare_30243.py", 1),
        ("iCE-Onhand-Inventory-3.0.244", "iCE-Onhand-Inventory-3.0.243", 4),
    ]:
        if w.count(current) != expected:
            raise SystemExit("3.0.244 workflow marker missing: " + current)
        w = w.replace(current, previous)
    workflow.write_text(w)
    runpy.run_path(str(root / ".github/prepare_30243.py"), run_name="__main__")

for old, new, expected in [
    ("Prepare and verify 3.0.243 Victoria counted batch workflow",
     "Prepare and verify 3.0.244 negative quantity safeguards", 1),
    (".github/prepare_30243.py", ".github/prepare_30244.py", 1),
    ("iCE-Onhand-Inventory-3.0.243", "iCE-Onhand-Inventory-3.0.244", 4),
]:
    w = workflow.read_text()
    if w.count(old) != expected:
        raise SystemExit("3.0.243 workflow restore marker missing: " + old)
    workflow.write_text(w.replace(old, new))

w = workflow.read_text()
branch = "feature/30243-victoria-count-batches"
if w.count(branch) != 2:
    raise SystemExit("Expected release branch in push and pull_request triggers")
workflow.write_text(w.replace(branch, branch + ", feature/30244-negative-quantity-verification"))

gradle = root / "app/build.gradle"
replace_once(gradle, "versionCode 30243", "versionCode 30244", "Gradle version code")
replace_once(gradle, "versionName '3.0.243'", "versionName '3.0.244'", "Gradle version name")
manifest = root / "app/src/main/AndroidManifest.xml"
replace_once(manifest, "iCE Onhand 3.0.243", "iCE Onhand 3.0.244", "Manifest version")
main = root / "app/src/main/java/com/iceinventory/onhand/MainActivity.java"
replace_once(main, "Onhand Inventory 3.0.243", "Onhand Inventory 3.0.244", "Main screen version")

replace_once(
    main,
    '        String loc=confirmedLocation;\n        if(Math.abs(q)>300){',
    '        String loc=confirmedLocation;\n'
    '        if(q<0){\n'
    '            final double subtract=q,existing=current;final String saveCode=code,saveLoc=loc,saveDescription=description.getText().toString(),savePrice=currentPrice;\n'
    '            confirmNegativeAdjustment(saveCode,saveLoc,existing,subtract,()->saveEnteredCount(saveCode,saveDescription,savePrice,subtract,saveLoc));\n'
    '            return;\n'
    '        }\n'
    '        if(Math.abs(q)>300){',
    "Signed count verification",
)

replace_once(
    main,
    '    private void confirmMaximumQuantity(String barcodeCode,double projectedTotal,Runnable continueCount){\n'
    '        double limit=maximumQuantityPerBarcode();\n'
    '        if(limit<=0||projectedTotal<=limit){continueCount.run();return;}\n'
    '        new AlertDialog.Builder(this).setTitle("Maximum Quantity Exceeded")\n'
    '                .setMessage("Barcode "+barcodeCode+" would total "+QuantityMath.format(projectedTotal)+" across all locations. The maximum is "+QuantityMath.format(limit)+". Continue with this count?")\n'
    '                .setPositiveButton("Continue",(d,w)->continueCount.run())\n'
    '                .setNegativeButton("Cancel",null).show();\n'
    '    }',
    '    private void confirmMaximumQuantity(String barcodeCode,double projectedTotal,Runnable continueCount){\n'
    '        double limit=maximumQuantityPerBarcode();\n'
    '        if(limit<=0||projectedTotal<=limit){continueCount.run();return;}\n'
    '        new AlertDialog.Builder(this).setTitle("Maximum Quantity Exceeded")\n'
    '                .setMessage("Barcode "+barcodeCode+" would total "+QuantityMath.format(projectedTotal)+" across all locations. The maximum is "+QuantityMath.format(limit)+". Continue with this count?")\n'
    '                .setPositiveButton("Continue",(d,w)->continueCount.run())\n'
    '                .setNegativeButton("Cancel",null).show();\n'
    '    }\n\n'
    '    private void confirmNegativeAdjustment(String barcodeCode,String locationName,double current,double subtraction,Runnable continueAdjustment){\n'
    '        if(subtraction>=0){continueAdjustment.run();return;}\n'
    '        new AlertDialog.Builder(this).setTitle("VERIFY SUBTRACTION")\n'
    '                .setMessage("You entered "+QuantityMath.format(subtraction)+" units.\\n\\nBarcode: "+barcodeCode+"\\nLocation: "+locationName+"\\nCurrent quantity: "+QuantityMath.format(current)+"\\nNew quantity: "+QuantityMath.format(current+subtraction)+"\\n\\nConfirm that you want to subtract "+QuantityMath.format(Math.abs(subtraction))+" units.")\n'
    '                .setNegativeButton("GO BACK",null).setPositiveButton("VERIFY & SUBTRACT",(d,w)->continueAdjustment.run()).show();\n'
    '    }',
    "Negative verification dialog",
)

replace_once(
    main,
    '        db.incrementQuantity(row.id,-1);lastBarcode=row.barcode;refreshList();noteCountForSafety();',
    '        confirmNegativeAdjustment(row.barcode,row.location,row.quantity,-1,()->{db.incrementQuantity(row.id,-1);lastBarcode=row.barcode;refreshList();noteCountForSafety();});',
    "List minus verification",
)

replace_once(
    main,
    '                db.incrementQuantity(r.id,amount);refreshList();highlightAndRevealBarcode(r.barcode);noteCountForSafety();dialog.dismiss();\n'
    '                barcode.setText("");description.setText("");qty.setText("");currentPrice="";\n'
    '                focusBarcodeWithoutKeyboard();\n'
    '                toast(amount<0?"Subtracted "+Math.abs(amount)+" • New quantity "+next:"Added "+amount+" • New quantity "+next);',
    '                final double verifiedAmount=amount;\n'
    '                Runnable applyAdjustment=()->{\n'
    '                    db.incrementQuantity(r.id,verifiedAmount);refreshList();highlightAndRevealBarcode(r.barcode);noteCountForSafety();dialog.dismiss();\n'
    '                    barcode.setText("");description.setText("");qty.setText("");currentPrice="";\n'
    '                    focusBarcodeWithoutKeyboard();\n'
    '                    toast(verifiedAmount<0?"Subtracted "+Math.abs(verifiedAmount)+" • New quantity "+next:"Added "+verifiedAmount+" • New quantity "+next);\n'
    '                };\n'
    '                if(verifiedAmount<0)confirmNegativeAdjustment(r.barcode,r.location,r.quantity,verifiedAmount,applyAdjustment);else applyAdjustment.run();',
    "Edit adjustment verification",
)

checks = {
    "version": "versionName '3.0.244'" in gradle.read_text(),
    "negative main input confirmation": "confirmNegativeAdjustment(saveCode,saveLoc,existing,subtract" in main.read_text(),
    "minus button confirmation": "confirmNegativeAdjustment(row.barcode,row.location,row.quantity,-1" in main.read_text(),
    "edit adjustment confirmation": "if(verifiedAmount<0)confirmNegativeAdjustment" in main.read_text(),
    "existing below-zero guard retained": 'if(next<0){toast("Quantity cannot go below zero")' in main.read_text(),
}
if not all(checks.values()):
    raise SystemExit("3.0.244 validation failed: " + repr(checks))
print("Prepared OnHand 3.0.244: negative quantity entries, minus controls, and manual subtractions require confirmation; quantity cannot fall below zero.")
