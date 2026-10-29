#!/usr/bin/env python3
"""OnHand 3.0.241: map Victoria location UPC scans to reportable locations."""
from pathlib import Path
import os
import runpy

root = Path(__file__).resolve().parents[1]
workflow = root / ".github/workflows/build-apk.yml"
w = workflow.read_text()
for new, old, expected in [
    ("Prepare and verify 3.0.241 Victoria location UPC map",
     "Prepare and verify 3.0.240 Victoria overhead side location scan", 1),
    (".github/prepare_30241.py", ".github/prepare_30240.py", 1),
    ("iCE-Onhand-Inventory-3.0.241", "iCE-Onhand-Inventory-3.0.240", 4),
]:
    if w.count(new) != expected:
        raise SystemExit("3.0.241 workflow marker missing: " + new)
    w = w.replace(new, old)
workflow.write_text(w)

if os.environ.get("ONHAND_PREPARED_30240") != "1":
    runpy.run_path(str(root / ".github/prepare_30240.py"), run_name="__main__")

main = root / "app/src/main/java/com/iceinventory/onhand/MainActivity.java"
s = main.read_text()

def once(old, new, label):
    global s
    count = s.count(old)
    if count != 1:
        raise SystemExit(label + " anchor mismatch: " + str(count))
    s = s.replace(old, new, 1)

once('''    private java.util.ArrayList<String> victoriaSpecialLocations(){''',
     '''    private String[][] victoriaLocationMappings(){
        return new String[][]{
            {"21100141022","WH-2 TEA UNDER BACK STAIRS"},
            {"21100140022","WH-2 CAPPUCHINO BACK STAIRS"},
            {"21100139022","WH-2 RIGHT WALL UNDER RACK"},
            {"21100138022","WH-2 RIGHT WALL FLOOR DISPLAYS"},
            {"21100137022","WH-2 LEFT WALL UNDER RACK"},
            {"21100136022","WH-2 LEFT WALL SYRUPS"},
            {"21100135022","WH-1 FRONT DISPLAYS"},
            {"21100134022","WH-1 BACK WALL RACK"},
            {"21100133022","WH-1 FLOOR DISPLAYS"},
            {"21100132022","UPSTAIRS"},
            {"21100131022","SHOWROOM"}
        };
    }

    private String victoriaLocationDescription(String upc){
        if(!isVictoriaCoffeeInventory()||upc==null)return "";
        String code=upc.trim();
        for(String[] mapping:victoriaLocationMappings())
            if(mapping[0].equals(code))return mapping[1];
        return "";
    }

    private String victoriaLocationUpc(String description){
        if(!isVictoriaCoffeeInventory()||description==null)return "";
        for(String[] mapping:victoriaLocationMappings())
            if(mapping[1].equalsIgnoreCase(description.trim()))return mapping[0];
        return "";
    }

    private java.util.ArrayList<String> victoriaSpecialLocations(){''', "Victoria location UPC map")

once('''        for(String name:victoriaSpecialLocations())db.addLocation(name);
        String[] walls={"Front-Wall","Left-Wall","Right-Wall","Back-Wall"};''',
     '''        for(String name:victoriaSpecialLocations())db.addLocation(name);
        for(String[] mapping:victoriaLocationMappings())db.addLocation(mapping[1]);
        String[] walls={"Front-Wall","Left-Wall","Right-Wall","Back-Wall"};''', "initialize mapped locations")

once('''    private boolean isMainOnlyLocation(String location){
        if(isVictoriaCoffeeInventory()&&location!=null&&
                (location.equalsIgnoreCase("Overhead-LFT")||location.equalsIgnoreCase("Overhead-RHT")))
            return false;
        return location!=null&&!location.isEmpty()&&location.equalsIgnoreCase(normalizeMainLocation(location));
    }''',
     '''    private boolean isMainOnlyLocation(String location){
        if(isVictoriaCoffeeInventory()&&location!=null&&
                (location.equalsIgnoreCase("Overhead-LFT")||location.equalsIgnoreCase("Overhead-RHT")||
                 !victoriaLocationUpc(location).isEmpty()))return false;
        return location!=null&&!location.isEmpty()&&location.equalsIgnoreCase(normalizeMainLocation(location));
    }''', "mapped location banner")

once('''    private void handleScannedBarcode(String rawCode) {
        if(!ensureCountingLocation())return;''',
     '''    private void handleScannedBarcode(String rawCode) {
        String mappedLocation=victoriaLocationDescription(rawCode);
        if(!mappedLocation.isEmpty()){
            submitCountingLocation(mappedLocation);
            barcode.setText("");description.setText("");qty.setText("");
            return;
        }
        if(!ensureCountingLocation())return;''', "location UPC scan routing")

once('''        if(isVictoriaCoffeeInventory()){
            String exact=canonicalVictoriaSpecialLocation(scanned);''',
     '''        if(isVictoriaCoffeeInventory()){
            String mapped=victoriaLocationDescription(scanned);
            if(!mapped.isEmpty()){
                submitCountingLocation(mapped);return;
            }
            String exact=canonicalVictoriaSpecialLocation(scanned);''', "location UPC scan in location picker")

once('''        if(n.toLowerCase(java.util.Locale.US).startsWith("overhead"))return "Overhead";''',
     '''        if(n.regionMatches(true,0,"WH-1",0,4))return "WH-1";
        if(n.regionMatches(true,0,"WH-2",0,4))return "WH-2";
        if(n.equalsIgnoreCase("UPSTAIRS"))return "UPSTAIRS";
        if(n.toLowerCase(java.util.Locale.US).startsWith("overhead"))return "Overhead";''', "warehouse location grouping")

once('''        if(loc.startsWith("overhead")||loc.startsWith("over head"))return "OVERHEAD";''',
     '''        if(loc.startsWith("wh-1"))return "WH-1";
        if(loc.startsWith("wh-2"))return "WH-2";
        if(loc.equals("upstairs"))return "UPSTAIRS";
        if(loc.startsWith("overhead")||loc.startsWith("over head"))return "OVERHEAD";''', "warehouse map subtotal grouping")

once('''            {"WAREHOUSE — LOOSE STOCK","FLOOR PALLETS","UNDER STAIR","SUPPLY SHELVES","UTILITY"},''',
     '''            {"WAREHOUSE — LOOSE STOCK","FLOOR PALLETS","UNDER STAIR","SUPPLY SHELVES","UTILITY","WH-1","WH-2","UPSTAIRS"},''', "floor plan Victoria location totals")
main.write_text(s)

doc = root / "VICTORIA-COFFEE-LOCATION-MAP.md"
d = doc.read_text()
if d.count("OnHand 3.0.240") != 1:
    raise SystemExit("location map 3.0.240 title marker missing")
d = d.replace("OnHand 3.0.240", "OnHand 3.0.241", 1)
anchor = "## Schematic map\n"
if d.count(anchor) != 1:
    raise SystemExit("location map insertion anchor mismatch")
section = '''## Victoria location UPCs for reports

Scan a location UPC to select the matching location description. The app saves the description as the count location so batch and location reports use the same readable name.

| LOCATION UPC | LOCATION DESCRIPTION |
| --- | --- |
| 21100141022 | WH-2 TEA UNDER BACK STAIRS |
| 21100140022 | WH-2 CAPPUCHINO BACK STAIRS |
| 21100139022 | WH-2 RIGHT WALL UNDER RACK |
| 21100138022 | WH-2 RIGHT WALL FLOOR DISPLAYS |
| 21100137022 | WH-2 LEFT WALL UNDER RACK |
| 21100136022 | WH-2 LEFT WALL SYRUPS |
| 21100135022 | WH-1 FRONT DISPLAYS |
| 21100134022 | WH-1 BACK WALL RACK |
| 21100133022 | WH-1 FLOOR DISPLAYS |
| 21100132022 | UPSTAIRS |
| 21100131022 | SHOWROOM |

'''
d = d.replace(anchor, section + anchor, 1)
doc.write_text(d)

gradle = root / "app/build.gradle"
g = gradle.read_text()
if g.count("versionCode 30240") != 1 or g.count("versionName '3.0.240'") != 1:
    raise SystemExit("Gradle 3.0.240 markers missing")
gradle.write_text(g.replace("versionCode 30240", "versionCode 30241", 1)
                  .replace("versionName '3.0.240'", "versionName '3.0.241'", 1))

manifest = root / "app/src/main/AndroidManifest.xml"
m = manifest.read_text()
if m.count("iCE Onhand 3.0.240") != 1:
    raise SystemExit("manifest 3.0.240 marker missing")
manifest.write_text(m.replace("iCE Onhand 3.0.240", "iCE Onhand 3.0.241", 1))

for path, label in [(main, "main screen"),
                    (root / "app/src/main/java/com/iceinventory/onhand/BatchMergeActivity.java", "batch merge")]:
    text = path.read_text()
    old = "Onhand Inventory 3.0.240"
    if path == main and text.count(old) != 1:
        raise SystemExit(label + " version marker mismatch")
    if text.count(old) == 1:
        path.write_text(text.replace(old, "Onhand Inventory 3.0.241", 1))

w = workflow.read_text()
for old, new, expected in [
    ("Prepare and verify 3.0.240 Victoria overhead side location scan",
     "Prepare and verify 3.0.241 Victoria location UPC map", 1),
    (".github/prepare_30240.py", ".github/prepare_30241.py", 1),
    ("iCE-Onhand-Inventory-3.0.240", "iCE-Onhand-Inventory-3.0.241", 4),
]:
    if w.count(old) != expected:
        raise SystemExit("3.0.240 workflow restore marker mismatch: " + old)
    w = w.replace(old, new)
workflow.write_text(w)

checks = {
    "11 location UPCs": all(code in main.read_text() for code in [
        "21100141022", "21100140022", "21100139022", "21100138022", "21100137022",
        "21100136022", "21100135022", "21100134022", "21100133022", "21100132022", "21100131022"]),
    "location UPC selects description": "submitCountingLocation(mappedLocation)" in main.read_text(),
    "location labels appear in report docs": "Victoria location UPCs for reports" in doc.read_text(),
    "release version": "versionCode 30241" in gradle.read_text() and "versionName '3.0.241'" in gradle.read_text(),
    "workflow uses current prep": ".github/prepare_30241.py" in workflow.read_text(),
}
failed = [name for name, passed in checks.items() if not passed]
if failed:
    raise SystemExit("3.0.241 validation failed: " + ", ".join(failed))
print("Prepared OnHand 3.0.241: Victoria location UPCs select their matching full descriptions for count and location reports.")
