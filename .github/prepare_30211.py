#!/usr/bin/env python3
from pathlib import Path
import runpy

script_dir = Path(__file__).resolve().parent
root = script_dir.parent if script_dir.name == ".github" else script_dir
workflow = root / ".github/workflows/build-apk.yml"

# The previous release preparation script expects the workflow to name 3.0.210.
seed = workflow.read_text()
for new, old in [
    ("Prepare and verify 3.0.211 automatic increment count", "Prepare and verify 3.0.210 bundled barcode scanner"),
    (".github/prepare_30211.py", ".github/prepare_30210.py"),
    ("iCE-Onhand-Inventory-3.0.211", "iCE-Onhand-Inventory-3.0.210"),
]:
    if new not in seed:
        raise SystemExit("3.0.211 workflow seed missing: " + new)
    seed = seed.replace(new, old)
workflow.write_text(seed)
runpy.run_path(str(root / ".github/prepare_30210.py"), run_name="__main__")

w = workflow.read_text()
for old, new in [
    ("Prepare and verify 3.0.210 bundled barcode scanner", "Prepare and verify 3.0.211 automatic increment count"),
    (".github/prepare_30210.py", ".github/prepare_30211.py"),
    ("iCE-Onhand-Inventory-3.0.210", "iCE-Onhand-Inventory-3.0.211"),
]:
    if old not in w:
        raise SystemExit("3.0.210 workflow marker missing: " + old)
    w = w.replace(old, new)
workflow.write_text(w)

gradle = root / "app/build.gradle"
g = gradle.read_text()
if "versionCode 30210" not in g or "versionName '3.0.210'" not in g:
    raise SystemExit("3.0.210 Gradle version missing")
g = g.replace("versionCode 30210", "versionCode 30211", 1).replace("versionName '3.0.210'", "versionName '3.0.211'", 1)
gradle.write_text(g)

manifest = root / "app/src/main/AndroidManifest.xml"
m = manifest.read_text()
if m.count("iCE Onhand 3.0.210") != 1:
    raise SystemExit("3.0.210 app label missing")
m = m.replace("iCE Onhand 3.0.210", "iCE Onhand 3.0.211", 1)
manifest.write_text(m)

main = root / "app/src/main/java/com/iceinventory/onhand/MainActivity.java"
s = main.read_text()
if s.count("Onhand Inventory 3.0.210") != 1:
    raise SystemExit("3.0.210 main screen label missing")
s = s.replace("Onhand Inventory 3.0.210", "Onhand Inventory 3.0.211", 1)

max_key = '    private static final String KEY_MAX_QTY="maximum_quantity_per_barcode";'
auto_key = max_key + '\n    private static final String KEY_AUTO_INCREMENT="auto_increment_count";'
if s.count(max_key) != 1:
    raise SystemExit("Maximum quantity preference declaration missing")
s = s.replace(max_key, auto_key, 1)

# Put the new control with the other scanning switches for both Master and Count User.
scan_switch = '        box.addView(optionSwitch("Vibrate on Scan",KEY_VIBRATE,true));'
if s.count(scan_switch) != 1:
    raise SystemExit("Scanning switch section missing")
s = s.replace(scan_switch, scan_switch + '\n        box.addView(optionSwitch("Automatic Increment Count",KEY_AUTO_INCREMENT,false));', 1)

counter_max = '''        Button maxQty=button("Maximum Qty per Barcode: "+maximumQuantityLabel(),0);
        maxQty.setOnClickListener(v->showMaximumQuantitySetting());
        box.addView(maxQty,new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT,dp(58)));'''
counter_auto = counter_max + '\n        box.addView(optionSwitch("Automatic Increment Count",KEY_AUTO_INCREMENT,false));'
if s.count(counter_max) != 1:
    raise SystemExit("Count User Scanning section missing")
s = s.replace(counter_max, counter_auto, 1)

# When enabled, each scan of an already-known barcode adds one at the active location.
# The existing maximum-quantity warning still governs the total across all locations.
old_existing = '''        InventoryDb.Row existing=db.latestForBarcode(sessionId,code);
        if(existing!=null) {'''
new_existing = '''        InventoryDb.Row existing=db.latestForBarcode(sessionId,code);
        if(existing!=null) {
            if(prefs().getBoolean(KEY_AUTO_INCREMENT,false)) {
                String activeLocation=location==null||location.getSelectedItem()==null?"Main":location.getSelectedItem().toString();
                double projected=db.quantityForBarcode(sessionId,code)+1;
                Runnable increment=()->{
                    db.addOrIncrement(sessionId,code,existing.description,existing.price,1,activeLocation);
                    lastBarcode=code;
                    barcode.setText("");description.setText("");qty.setText("");currentPrice="";
                    refreshList();focusBarcodeWithoutKeyboard();noteCountForSafety();
                    toast("Automatically added 1 to "+code);
                    if(continuousPhoneScan)barcode.postDelayed(this::scanBarcode,180);
                };
                confirmMaximumQuantity(code,projected,increment);
                return;
            }
'''
if s.count(old_existing) != 1:
    raise SystemExit("Known barcode handling block missing")
s = s.replace(old_existing, new_existing, 1)

# Carry this Master preference with shared store files and apply it when Count Users import them.
old_header = r'+"\tMAXIMUM_QTY="+prefs().getString(KEY_MAX_QTY,"0");'
new_header = r'+"\tMAXIMUM_QTY="+prefs().getString(KEY_MAX_QTY,"0")+"\tAUTO_INCREMENT_COUNT="+prefs().getBoolean(KEY_AUTO_INCREMENT,false);'
if s.count(old_header) != 1:
    raise SystemExit("Shared store maximum quantity metadata missing")
s = s.replace(old_header, new_header, 1)

method_start = s.find("    private void applySharedProjectRole(Uri uri){")
method_end = s.find("    private void offerMasterCandidateActivation()", method_start)
if method_start < 0 or method_end < 0:
    raise SystemExit("Shared store settings parser missing")
method = s[method_start:method_end]
decl = 'unknownMode="",maximumQty="",profile='
decl_new = 'unknownMode="",maximumQty="",autoIncrement="",profile='
if method.count(decl) != 1:
    raise SystemExit("Shared store parser metadata declaration missing")
method = method.replace(decl, decl_new, 1)
max_parse = 'else if(part.startsWith("MAXIMUM_QTY="))maximumQty=part.substring("MAXIMUM_QTY=".length()).trim();'
auto_parse = max_parse + '\n                    else if(part.startsWith("AUTO_INCREMENT_COUNT="))autoIncrement=part.substring("AUTO_INCREMENT_COUNT=".length()).trim();'
if method.count(max_parse) != 1:
    raise SystemExit("Shared store maximum quantity parser missing")
method = method.replace(max_parse, auto_parse, 1)
apply_marker = '            try{double limit=QuantityMath.parse(maximumQty);if(limit>=0){defaults.putString(KEY_MAX_QTY,QuantityMath.format(limit));changed=true;}}catch(Exception ignored){}'
apply_auto = apply_marker + '\n            if("true".equalsIgnoreCase(autoIncrement)||"false".equalsIgnoreCase(autoIncrement)){defaults.putBoolean(KEY_AUTO_INCREMENT,Boolean.parseBoolean(autoIncrement));changed=true;}'
if method.count(apply_marker) != 1:
    raise SystemExit("Shared store defaults application block missing")
method = method.replace(apply_marker, apply_auto, 1)
s = s[:method_start] + method + s[method_end:]
main.write_text(s)

checks = {
    "release version": "versionCode 30211" in gradle.read_text() and "versionName '3.0.211'" in gradle.read_text(),
    "visible version labels": "iCE Onhand 3.0.211" in manifest.read_text() and "Onhand Inventory 3.0.211" in s,
    "bundled scanner retained": "com.google.mlkit.vision.barcode.BarcodeScanning" in (root / "app/src/main/java/com/iceinventory/onhand/ScanActivity.java").read_text(),
    "setting under Master Scanning": 'optionSwitch("Automatic Increment Count",KEY_AUTO_INCREMENT,false)' in s,
    "auto increments at active location": 'db.addOrIncrement(sessionId,code,existing.description,existing.price,1,activeLocation)' in s,
    "maximum warning retained": 'confirmMaximumQuantity(code,projected,increment)' in s,
    "shared store sends setting": 'AUTO_INCREMENT_COUNT=' in s,
    "Count User import receives setting": 'defaults.putBoolean(KEY_AUTO_INCREMENT,Boolean.parseBoolean(autoIncrement))' in s,
    "workflow points to this release": ".github/prepare_30211.py" in workflow.read_text() and "3.0.211" in workflow.read_text(),
}
failed = [name for name, passed in checks.items() if not passed]
if failed:
    raise SystemExit("3.0.211 validation failed: " + ", ".join(failed))
print("Prepared iCE OnHand 3.0.211 with optional automatic increment count under Scanning settings.")
