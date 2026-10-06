#!/usr/bin/env python3
from pathlib import Path
import re
import runpy

root = Path(__file__).resolve().parents[1]
workflow = root / ".github/workflows/build-apk.yml"
w = workflow.read_text()
for old, new in [
    ("Prepare and verify 3.0.209 Scanning settings transfer", "Prepare and verify 3.0.208 Count User defaults and maximum quantity setting"),
    (".github/prepare_30209.py", ".github/prepare_30208.py"),
    ("iCE-Onhand-Inventory-3.0.209", "iCE-Onhand-Inventory-3.0.208"),
]:
    if old not in w:
        raise SystemExit("3.0.209 workflow seed missing: " + old)
    w = w.replace(old, new)
workflow.write_text(w)
runpy.run_path(str(root / ".github/prepare_30208.py"), run_name="__main__")

w = workflow.read_text()
for old, new in [
    ("Prepare and verify 3.0.208 Count User defaults and maximum quantity setting", "Prepare and verify 3.0.209 Scanning settings transfer"),
    (".github/prepare_30208.py", ".github/prepare_30209.py"),
    ("iCE-Onhand-Inventory-3.0.208", "iCE-Onhand-Inventory-3.0.209"),
]:
    if old not in w:
        raise SystemExit("3.0.209 workflow marker missing: " + old)
    w = w.replace(old, new)
workflow.write_text(w)

gradle = root / "app/build.gradle"
s = gradle.read_text()
if "versionCode 30208" not in s or "versionName '3.0.208'" not in s:
    raise SystemExit("3.0.208 Gradle version missing")
gradle.write_text(s.replace("versionCode 30208", "versionCode 30209", 1).replace("versionName '3.0.208'", "versionName '3.0.209'", 1))

manifest = root / "app/src/main/AndroidManifest.xml"
s = manifest.read_text()
if "iCE Onhand 3.0.208" not in s:
    raise SystemExit("3.0.208 manifest label missing")
manifest.write_text(s.replace("iCE Onhand 3.0.208", "iCE Onhand 3.0.209", 1))

main = root / "app/src/main/java/com/iceinventory/onhand/MainActivity.java"
s = main.read_text()
if "Onhand Inventory 3.0.208" not in s:
    raise SystemExit("3.0.208 screen version missing")
s = s.replace("Onhand Inventory 3.0.208", "Onhand Inventory 3.0.209", 1)

# Put the Counter User limit in a labeled Scanning group.
old = '''        Button maxQty=button("Maximum Qty per Barcode: "+maximumQuantityLabel(),0);
        maxQty.setOnClickListener(v->showMaximumQuantitySetting());
        box.addView(maxQty,new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT,dp(58)));'''
new = '''        TextView scanSettings=text("SCANNING",16,gold(),true);scanSettings.setPadding(dp(6),dp(16),0,dp(2));box.addView(scanSettings);
        Button maxQty=button("Maximum Qty per Barcode: "+maximumQuantityLabel(),0);
        maxQty.setOnClickListener(v->showMaximumQuantitySetting());
        box.addView(maxQty,new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT,dp(58)));'''
if s.count(old) != 1:
    raise SystemExit("Count User maximum quantity control missing")
s = s.replace(old, new, 1)

# Master Options: keep unknown-barcode behavior and maximum quantity together
# immediately under the Scanning heading.
anchor = '        box.addView(optionSwitch("Vibrate on Scan",KEY_VIBRATE,true));'
controls = '''
        Button unknown=button("Unknown Barcode Behavior: "+friendlyUnknownMode(),0);
        unknown.setOnClickListener(v->showUnknownBarcodeMode());
        box.addView(unknown,new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT,dp(54)));
        Button scanMaximum=button("Maximum Qty per Barcode: "+maximumQuantityLabel(),0);
        scanMaximum.setOnClickListener(v->showMaximumQuantitySetting());
        box.addView(scanMaximum,new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT,dp(54)));'''
if s.count(anchor) != 1:
    raise SystemExit("Master Scanning section insertion point missing")
s = s.replace(anchor, anchor + controls, 1)
unknown_pattern = r'\n        Button unknown=button\("Unknown Barcode Behavior: "\+friendlyUnknownMode\(\),0\);\n        unknown\.setOnClickListener\(v->showUnknownBarcodeMode\(\)\);\n        box\.addView\(unknown,new LinearLayout\.LayoutParams\(ViewGroup\.LayoutParams\.MATCH_PARENT,dp\(\d+\)\)\);'
unknown_matches = list(re.finditer(unknown_pattern, s))
if len(unknown_matches) == 2:
    match = unknown_matches[-1]
    s = s[:match.start()] + s[match.end():]
elif len(unknown_matches) != 1:
    raise SystemExit("Expected one Unknown Barcode control after placement, found " + str(len(unknown_matches)))

# Carry the Master-selected scanning defaults in every shared store file.
old_header = '''out.write("#ICE_ONHAND_PROJECT\\tROLE="+(masterCandidate?"MASTER_CANDIDATE":"COUNT_USER")+"\\tMASTER_PIN_HASH="+prefs().getString(KEY_MASTER_PIN_HASH,"")+"\\r\\nQuantity\\tBarcode\\tDescription\\tPrice\\r\\n");'''
new_header = '''out.write("#ICE_ONHAND_PROJECT\\tROLE="+(masterCandidate?"MASTER_CANDIDATE":"COUNT_USER")+"\\tMASTER_PIN_HASH="+prefs().getString(KEY_MASTER_PIN_HASH,"")+"\\tUNKNOWN_BARCODE_MODE="+getUnknownBarcodeMode()+"\\tMAXIMUM_QTY="+prefs().getString(KEY_MAX_QTY,"0")+"\\r\\nQuantity\\tBarcode\\tDescription\\tPrice\\r\\n");'''
if s.count(old_header) != 1:
    at = s.find("MASTER_PIN_HASH=")
    context = s[max(0, at-180):at+500] if at >= 0 else "Master PIN metadata absent"
    raise SystemExit("Shared store metadata header missing; generated source context: " + context)
s = s.replace(old_header, new_header, 1)

# Apply settings carried by a shared store when a Count User imports it.
start = s.find("    private void applySharedProjectRole(Uri uri){")
end = s.find("    private void offerMasterCandidateActivation()", start)
if start < 0 or end < 0:
    raise SystemExit("Shared project role method missing")
method = s[start:end]
if 'String verifier="",role="";' not in method:
    raise SystemExit("Shared role metadata parser declaration missing")
method = method.replace('String verifier="",role="";', 'String verifier="",role="",unknownMode="",maximumQty="";', 1)
old_parse = 'else if(part.startsWith("ROLE="))role=part.substring("ROLE=".length()).trim();'
new_parse = old_parse + 'else if(part.startsWith("UNKNOWN_BARCODE_MODE="))unknownMode=part.substring("UNKNOWN_BARCODE_MODE=".length()).trim();else if(part.startsWith("MAXIMUM_QTY="))maximumQty=part.substring("MAXIMUM_QTY=".length()).trim();'
if method.count(old_parse) != 1:
    raise SystemExit("Shared settings metadata parse point missing")
method = method.replace(old_parse, new_parse, 1)
old_editor = 'if(verifier.matches("[0-9a-fA-F]{64}"))e.putString(KEY_AUTHORIZED_MASTER_PIN_HASH,verifier);e.apply();'
new_editor = '''if(verifier.matches("[0-9a-fA-F]{64}"))e.putString(KEY_AUTHORIZED_MASTER_PIN_HASH,verifier);if("ignore".equals(unknownMode)||"add".equals(unknownMode)||"search".equals(unknownMode))e.putString(KEY_UNKNOWN_MODE,unknownMode);try{double limit=QuantityMath.parse(maximumQty);if(limit>=0)e.putString(KEY_MAX_QTY,QuantityMath.format(limit));}catch(Exception ignored){}e.apply();'''
if method.count(old_editor) != 1:
    raise SystemExit("Shared settings application point missing")
method = method.replace(old_editor, new_editor, 1)
s = s[:start] + method + s[end:]

# Make the setup package label clear: it also delivers Scanning defaults.
old_label = 'Button counter=button("COUNTER PHONE\\nApp + Current Store",1);'
new_label = 'Button counter=button("COUNTER PHONE\\nApp + Store + Scanning Settings",1);'
if s.count(old_label) != 1:
    raise SystemExit("New Counter phone share label missing")
s = s.replace(old_label, new_label, 1)
main.write_text(s)

checks = {
    "version": "versionName '3.0.209'" in gradle.read_text(),
    "Master Scanning has unknown behavior": 'Button unknown=button("Unknown Barcode Behavior: "+friendlyUnknownMode(),0);' in s and 'TextView display=text("Display"' in s,
    "Master Scanning has max quantity": 'Button scanMaximum=button("Maximum Qty per Barcode: "+maximumQuantityLabel(),0);' in s,
    "Count User Scanning has max quantity": 'TextView scanSettings=text("SCANNING"' in s and s.count('Button maxQty=button("Maximum Qty per Barcode: "+maximumQuantityLabel(),0);') == 1,
    "shared store exports defaults": "UNKNOWN_BARCODE_MODE=" in s and "MAXIMUM_QTY=" in s,
    "shared store applies defaults": 'e.putString(KEY_UNKNOWN_MODE,unknownMode)' in s and 'e.putString(KEY_MAX_QTY,QuantityMath.format(limit))' in s,
    "setup package label": "App + Store + Scanning Settings" in s,
}
failed = [name for name, passed in checks.items() if not passed]
if failed:
    raise SystemExit("3.0.209 checks failed: " + ", ".join(failed))
print("Prepared iCE OnHand 3.0.209: Scanning settings are grouped together and shared store files carry Master defaults.")
