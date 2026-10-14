#!/usr/bin/env python3
from pathlib import Path
import runpy

root = Path(__file__).resolve().parent.parent
workflow = root / ".github/workflows/build-apk.yml"

# The preceding release script expects the workflow to name 3.0.226.
w = workflow.read_text()
for new, old, expected in [
    ("Prepare and verify 3.0.227 optional default qty and clean export columns", "Prepare and verify 3.0.226 auto-increment scan feedback", 1),
    (".github/prepare_30227.py", ".github/prepare_30226.py", 1),
    ("iCE-Onhand-Inventory-3.0.227", "iCE-Onhand-Inventory-3.0.226", 4),
]:
    if w.count(new) != expected:
        raise SystemExit("3.0.227 workflow marker missing or ambiguous: " + new)
    w = w.replace(new, old)
workflow.write_text(w)

runpy.run_path(str(root / ".github/prepare_30226.py"), run_name="__main__")

w = workflow.read_text()
for old, new, expected in [
    ("Prepare and verify 3.0.226 auto-increment scan feedback", "Prepare and verify 3.0.227 optional default qty and clean export columns", 1),
    (".github/prepare_30226.py", ".github/prepare_30227.py", 1),
    ("iCE-Onhand-Inventory-3.0.226", "iCE-Onhand-Inventory-3.0.227", 4),
]:
    if w.count(old) != expected:
        raise SystemExit("3.0.226 workflow marker missing or ambiguous: " + old)
    w = w.replace(old, new)
workflow.write_text(w)

gradle = root / "app/build.gradle"
g = gradle.read_text()
if g.count("versionCode 30226") != 1 or g.count("versionName '3.0.226'") != 1:
    raise SystemExit("3.0.226 Gradle version missing or ambiguous")
g = g.replace("versionCode 30226", "versionCode 30227", 1)
g = g.replace("versionName '3.0.226'", "versionName '3.0.227'", 1)
gradle.write_text(g)

manifest = root / "app/src/main/AndroidManifest.xml"
m = manifest.read_text()
if m.count("iCE Onhand 3.0.226") != 1:
    raise SystemExit("3.0.226 manifest label missing or ambiguous")
manifest.write_text(m.replace("iCE Onhand 3.0.226", "iCE Onhand 3.0.227", 1))

main = root / "app/src/main/java/com/iceinventory/onhand/MainActivity.java"
s = main.read_text()
if s.count("Onhand Inventory 3.0.226") != 1:
    raise SystemExit("3.0.226 home version label missing or ambiguous")
s = s.replace("Onhand Inventory 3.0.226", "Onhand Inventory 3.0.227", 1)

# Optional default quantity. 0 means OFF. This only pre-fills the Qty box;
# it does not save automatically, and Automatic Increment Count still takes precedence.
auto_key = '    private static final String KEY_AUTO_INCREMENT="auto_increment_count";'
default_key = auto_key + '\n    private static final String KEY_DEFAULT_QTY="default_scan_quantity";'
if s.count(auto_key) != 1:
    raise SystemExit("Automatic Increment Count preference declaration missing")
s = s.replace(auto_key, default_key, 1)

auto_control = '        box.addView(optionSwitch("Automatic Increment Count",KEY_AUTO_INCREMENT,false));'
if s.count(auto_control) != 2:
    raise SystemExit("Expected Master and Count User Automatic Increment Count controls")
default_control = auto_control + '''
        Button defaultQty=button("Default Qty (Optional): "+defaultQuantityLabel(),0);
        defaultQty.setOnClickListener(v->showDefaultQuantitySetting());
        box.addView(defaultQty,new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT,dp(58)));'''
s = s.replace(auto_control, default_control)

helper_anchor = '    private String friendlyUnknownMode() {'
helpers = '''    private double defaultQuantity(){
        try{
            double value=QuantityMath.parse(prefs().getString(KEY_DEFAULT_QTY,"0"));
            return value>0?value:0;
        }catch(Exception ignored){return 0;}
    }

    private String defaultQuantityLabel(){
        double value=defaultQuantity();
        return value>0?QuantityMath.format(value):"Off";
    }

    private void showDefaultQuantitySetting(){
        final EditText input=new EditText(this);
        input.setSingleLine(true);
        input.setInputType(InputType.TYPE_CLASS_NUMBER|InputType.TYPE_NUMBER_FLAG_DECIMAL);
        double current=defaultQuantity();
        if(current>0){input.setText(QuantityMath.format(current));input.setSelection(input.getText().length());}
        new AlertDialog.Builder(this)
                .setTitle("Default Qty (Optional)")
                .setMessage("When set, every normal barcode scan pre-fills the Qty box with this amount. It does NOT save the count automatically. Automatic Increment Count still works separately. Set 0 or use TURN OFF to leave Qty blank after a scan.")
                .setView(input)
                .setPositiveButton("SAVE",(d,w)->{
                    String raw=input.getText().toString().trim();
                    if(raw.isEmpty()){prefs().edit().putString(KEY_DEFAULT_QTY,"0").apply();toast("Default Qty turned off");return;}
                    try{
                        double value=QuantityMath.parse(raw);
                        if(value<=0){prefs().edit().putString(KEY_DEFAULT_QTY,"0").apply();toast("Default Qty turned off");return;}
                        prefs().edit().putString(KEY_DEFAULT_QTY,QuantityMath.format(value)).apply();
                        toast("Default Qty set to "+QuantityMath.format(value));
                    }catch(Exception e){toast("Default Qty must be a valid number");}
                })
                .setNeutralButton("TURN OFF",(d,w)->{prefs().edit().putString(KEY_DEFAULT_QTY,"0").apply();toast("Default Qty turned off");})
                .setNegativeButton("Cancel",null)
                .show();
    }

    private void applyDefaultQuantityIfEnabled(){
        if(qty==null||prefs().getBoolean(KEY_AUTO_INCREMENT,false))return;
        double value=defaultQuantity();
        if(value<=0)return;
        String text=QuantityMath.format(value);
        qty.setText(text);
        qty.setSelection(text.length());
    }

'''
if s.count(helper_anchor) != 1:
    raise SystemExit("Default Qty helper insertion point missing")
s = s.replace(helper_anchor, helpers + helper_anchor, 1)

# Apply the default immediately after a scan clears the previous quantity.
handle_start = s.find("    private void handleScannedBarcode(String rawCode)")
handle_end = s.find("    private void scanFeedback()", handle_start)
if handle_start < 0 or handle_end < 0:
    raise SystemExit("Barcode scan method boundaries missing")
handle = s[handle_start:handle_end]
qty_clear = '        qty.setText("");'
if handle.count(qty_clear) < 1:
    raise SystemExit("Barcode scan quantity clear point missing")
handle = handle.replace(qty_clear, qty_clear + '\n        applyDefaultQuantityIfEnabled();', 1)
s = s[:handle_start] + handle + s[handle_end:]

# Carry the Master default quantity to shared Count User setup files.
header_old = r'+"\tAUTO_INCREMENT_COUNT="+prefs().getBoolean(KEY_AUTO_INCREMENT,false);'
header_new = r'+"\tAUTO_INCREMENT_COUNT="+prefs().getBoolean(KEY_AUTO_INCREMENT,false)+"\tDEFAULT_QTY="+prefs().getString(KEY_DEFAULT_QTY,"0");'
if s.count(header_old) != 1:
    raise SystemExit("Shared store auto-increment metadata missing")
s = s.replace(header_old, header_new, 1)

method_start = s.find("    private void applySharedProjectRole(Uri uri){")
method_end = s.find("    private void offerMasterCandidateActivation()", method_start)
if method_start < 0 or method_end < 0:
    raise SystemExit("Shared store settings parser missing")
method = s[method_start:method_end]
decl = 'unknownMode="",maximumQty="",autoIncrement="",profile='
decl_new = 'unknownMode="",maximumQty="",autoIncrement="",defaultQty="",profile='
if method.count(decl) != 1:
    raise SystemExit("Shared store parser metadata declaration missing")
method = method.replace(decl, decl_new, 1)
auto_parse = 'else if(part.startsWith("AUTO_INCREMENT_COUNT="))autoIncrement=part.substring("AUTO_INCREMENT_COUNT=".length()).trim();'
default_parse = auto_parse + '\n                    else if(part.startsWith("DEFAULT_QTY="))defaultQty=part.substring("DEFAULT_QTY=".length()).trim();'
if method.count(auto_parse) != 1:
    raise SystemExit("Shared store auto-increment parser missing")
method = method.replace(auto_parse, default_parse, 1)
apply_auto = '            if("true".equalsIgnoreCase(autoIncrement)||"false".equalsIgnoreCase(autoIncrement)){defaults.putBoolean(KEY_AUTO_INCREMENT,Boolean.parseBoolean(autoIncrement));changed=true;}'
apply_default = apply_auto + '\n            try{double value=QuantityMath.parse(defaultQty);if(value>=0){defaults.putString(KEY_DEFAULT_QTY,QuantityMath.format(value));changed=true;}}catch(Exception ignored){}'
if method.count(apply_auto) != 1:
    raise SystemExit("Shared store auto-increment application missing")
method = method.replace(apply_auto, apply_default, 1)
s = s[:method_start] + method + s[method_end:]
main.write_text(s)

# Category Description stays available internally for category/cigarette reports,
# but it is no longer forced into standard user-facing TXT/Excel count exports.
tab = root / "app/src/main/java/com/iceinventory/onhand/TabTextUtils.java"
t = tab.read_text()
forced_category = '        if(!out.contains("category_description"))out.add("category_description");'
if t.count(forced_category) != 1:
    raise SystemExit("Category Description export injection point missing or ambiguous")
t = t.replace(forced_category, '        if(!export&&!out.contains("category_description"))out.add("category_description");', 1)
tab.write_text(t)

checks = {
    "version": "versionName '3.0.227'" in gradle.read_text(),
    "manifest": "iCE Onhand 3.0.227" in manifest.read_text(),
    "visible version": "Onhand Inventory 3.0.227" in main.read_text(),
    "default qty preference": 'KEY_DEFAULT_QTY="default_scan_quantity"' in main.read_text(),
    "default qty controls": main.read_text().count('Default Qty (Optional):') == 2,
    "default qty prefill": "applyDefaultQuantityIfEnabled();" in main.read_text(),
    "auto increment takes precedence": 'prefs().getBoolean(KEY_AUTO_INCREMENT,false))return;' in main.read_text(),
    "shared default qty": "DEFAULT_QTY=" in main.read_text() and "defaultQty" in main.read_text(),
    "category description not forced on export": 'if(!export&&!out.contains("category_description"))out.add("category_description");' in tab.read_text(),
    "Victoria four-column customer report retained": "VictoriaCustomerXlsxWriter" in (root / "app/src/main/java/com/iceinventory/onhand/BatchMergeActivity.java").read_text(),
    "workflow": ".github/prepare_30227.py" in workflow.read_text() and "3.0.227" in workflow.read_text(),
}
failed = [name for name, passed in checks.items() if not passed]
if failed:
    raise SystemExit("3.0.227 validation failed: " + ", ".join(failed))
print("Prepared iCE OnHand 3.0.227: optional Default Qty in Settings; Category Description removed from standard exports.")
