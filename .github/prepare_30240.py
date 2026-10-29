#!/usr/bin/env python3
"""OnHand 3.0.240: recognize and retain Victoria overhead side barcodes."""
from pathlib import Path
import os
import runpy

root = Path(__file__).resolve().parents[1]
workflow = root / ".github/workflows/build-apk.yml"
w = workflow.read_text()
for new, old, expected in [
    ("Prepare and verify 3.0.240 Victoria overhead side location scan",
     "Prepare and verify 3.0.239 Victoria item-number import and customer export", 1),
    (".github/prepare_30240.py", ".github/prepare_30239.py", 1),
    ("iCE-Onhand-Inventory-3.0.240", "iCE-Onhand-Inventory-3.0.239", 4),
]:
    if w.count(new) != expected:
        raise SystemExit("3.0.240 workflow marker missing: " + new)
    w = w.replace(new, old)
workflow.write_text(w)

if os.environ.get("ONHAND_PREPARED_30239") != "1":
    runpy.run_path(str(root / ".github/prepare_30239.py"), run_name="__main__")

main = root / "app/src/main/java/com/iceinventory/onhand/MainActivity.java"
s = main.read_text()

def once(old, new, label):
    global s
    count = s.count(old)
    if count != 1:
        raise SystemExit(label + " anchor mismatch: " + str(count))
    s = s.replace(old, new, 1)

once('''        // Overhead mapped inventory locations: distinguish the 4-item map from
        // the 6-item map by keeping every exact overhead barcode unique.
        names.add("Overhead");
        for(int index=1;index<=10;index++)
            names.add(String.format(java.util.Locale.US,"Overhead-%02d",index));''',
     '''        // Victoria's printed overhead map uses two scannable exact locations.
        names.add("Overhead");
        names.add("Overhead-LFT");
        names.add("Overhead-RHT");''', "Victoria overhead presets")
once('''    private boolean isVictoriaSpecialLocation(String name){
        if(name==null)return false;
        for(String preset:victoriaSpecialLocations())
            if(preset.equalsIgnoreCase(name.trim()))return true;
        return false;
    }''',
     '''    private boolean isVictoriaSpecialLocation(String name){
        return !canonicalVictoriaSpecialLocation(name).isEmpty();
    }

    private String canonicalVictoriaSpecialLocation(String name){
        if(name==null)return "";
        for(String preset:victoriaSpecialLocations())
            if(preset.equalsIgnoreCase(name.trim()))return preset;
        return "";
    }''', "Victoria location canonicalization")
once('''    private boolean isMainOnlyLocation(String location){
        return location!=null&&!location.isEmpty()&&location.equalsIgnoreCase(normalizeMainLocation(location));
    }''',
     '''    private boolean isMainOnlyLocation(String location){
        if(isVictoriaCoffeeInventory()&&location!=null&&
                (location.equalsIgnoreCase("Overhead-LFT")||location.equalsIgnoreCase("Overhead-RHT")))
            return false;
        return location!=null&&!location.isEmpty()&&location.equalsIgnoreCase(normalizeMainLocation(location));
    }''', "exact overhead banner")
once('''        if(isVictoriaCoffeeInventory()&&isVictoriaSpecialLocation(scanned)){
            submitCountingLocation(scanned);return;
        }''',
     '''        if(isVictoriaCoffeeInventory()){
            String exact=canonicalVictoriaSpecialLocation(scanned);
            if(!exact.isEmpty()){
                submitCountingLocation(exact);return;
            }
        }''', "exact overhead barcode routing")
once('        if(n.startsWith("Overhead"))return "Overhead";',
     '        if(n.toLowerCase(java.util.Locale.US).startsWith("overhead"))return "Overhead";',
     "case-insensitive overhead grouping")
main.write_text(s)

gradle = root / "app/build.gradle"
g = gradle.read_text()
if g.count("versionCode 30239") != 1 or g.count("versionName '3.0.239'") != 1:
    raise SystemExit("Gradle 3.0.239 marker missing")
gradle.write_text(g.replace("versionCode 30239", "versionCode 30240", 1)
                  .replace("versionName '3.0.239'", "versionName '3.0.240'", 1))

manifest = root / "app/src/main/AndroidManifest.xml"
m = manifest.read_text()
if m.count("iCE Onhand 3.0.239") != 1:
    raise SystemExit("manifest 3.0.239 marker missing")
manifest.write_text(m.replace("iCE Onhand 3.0.239", "iCE Onhand 3.0.240", 1))

for path, old, new, label in [
    (main, "Onhand Inventory 3.0.239", "Onhand Inventory 3.0.240", "app version"),
    (root / "app/src/main/java/com/iceinventory/onhand/BatchMergeActivity.java",
     "Onhand Inventory 3.0.239", "Onhand Inventory 3.0.240", "batch merge version"),
]:
    s = path.read_text()
    if path == main and s.count(old) != 1:
        raise SystemExit(label + " marker mismatch")
    if s.count(old) == 1:
        path.write_text(s.replace(old, new, 1))

w = workflow.read_text()
for old, new, expected in [
    ("Prepare and verify 3.0.239 Victoria item-number import and customer export",
     "Prepare and verify 3.0.240 Victoria overhead side location scan", 1),
    (".github/prepare_30239.py", ".github/prepare_30240.py", 1),
    ("iCE-Onhand-Inventory-3.0.239", "iCE-Onhand-Inventory-3.0.240", 4),
]:
    if w.count(old) != expected:
        raise SystemExit("3.0.239 workflow restore marker mismatch: " + old)
    w = w.replace(old, new)
workflow.write_text(w)

if "names.add(\"Overhead-LFT\")" not in main.read_text() or "names.add(\"Overhead-RHT\")" not in main.read_text():
    raise SystemExit("Victoria overhead side locations were not added")
print("Prepared OnHand 3.0.240: Victoria overhead barcode scans retain OVERHEAD-LFT / OVERHEAD-RHT as exact count locations.")
