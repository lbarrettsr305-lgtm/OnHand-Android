#!/usr/bin/env python3
from pathlib import Path
import runpy

script_dir = Path(__file__).resolve().parent
root = script_dir.parent if script_dir.name == ".github" else script_dir
workflow = root / ".github/workflows/build-apk.yml"

# Seed the prior release preparation, then advance the release to 3.0.213.
w = workflow.read_text()
for new, old in [
    ("Prepare and verify 3.0.213 import template fixes", "Prepare and verify 3.0.212 Fleet Feet import format"),
    (".github/prepare_30213.py", ".github/prepare_30212.py"),
    ("iCE-Onhand-Inventory-3.0.213", "iCE-Onhand-Inventory-3.0.212"),
]:
    if new not in w:
        raise SystemExit("3.0.213 workflow seed missing: " + new)
    w = w.replace(new, old)
workflow.write_text(w)
runpy.run_path(str(root / ".github/prepare_30212.py"), run_name="__main__")

w = workflow.read_text()
for old, new in [
    ("Prepare and verify 3.0.212 Fleet Feet import format", "Prepare and verify 3.0.213 import template fixes"),
    (".github/prepare_30212.py", ".github/prepare_30213.py"),
    ("iCE-Onhand-Inventory-3.0.212", "iCE-Onhand-Inventory-3.0.213"),
]:
    if old not in w:
        raise SystemExit("3.0.212 workflow marker missing: " + old)
    w = w.replace(old, new)
workflow.write_text(w)

gradle = root / "app/build.gradle"
g = gradle.read_text()
if "versionCode 30212" not in g or "versionName '3.0.212'" not in g:
    raise SystemExit("3.0.212 Gradle version missing")
gradle.write_text(g.replace("versionCode 30212", "versionCode 30213", 1).replace("versionName '3.0.212'", "versionName '3.0.213'", 1))

manifest = root / "app/src/main/AndroidManifest.xml"
m = manifest.read_text()
if m.count("iCE Onhand 3.0.212") != 1:
    raise SystemExit("3.0.212 app label missing")
manifest.write_text(m.replace("iCE Onhand 3.0.212", "iCE Onhand 3.0.213", 1))

main = root / "app/src/main/java/com/iceinventory/onhand/MainActivity.java"
s = main.read_text()
if s.count("Onhand Inventory 3.0.212") != 1:
    raise SystemExit("3.0.212 main screen label missing")
main.write_text(s.replace("Onhand Inventory 3.0.212", "Onhand Inventory 3.0.213", 1))

fmt_path = root / "app/src/main/java/com/iceinventory/onhand/FormatConfigActivity.java"
f = fmt_path.read_text()
old_fleet = '''    private void applyFleetFeetPreset(){
        order.clear();enabled.clear();
        String[] fields={"barcode","item_number","description","size"};
        for(String f:ALL){order.add(f);enabled.put(f,false);}
        for(String f:fields)enabled.put(f,true);
        selectedIndex=Math.max(0,order.indexOf("barcode"));renderRows();
    }
'''.replace("+", "")
new_fleet = '''    private void applyFleetFeetPreset(){
        order.clear();enabled.clear();
        String[] fields={"barcode","item_number","description","size"};
        for(String field:fields){order.add(field);enabled.put(field,true);}
        for(String field:ALL)if(!order.contains(field)){order.add(field);enabled.put(field,false);}
        selectedIndex=0;renderRows();saveCurrentOrder();
        toast("Saved Fleet Feet import format");
    }
'''.replace("+", "")
if f.count(old_fleet) != 1:
    raise SystemExit("Fleet Feet preset method missing or unexpected")
f = f.replace(old_fleet, new_fleet, 1)

old_preset = '''    private void applyPreset(boolean victoria){
        order.clear();enabled.clear();
        String[] fields=victoria
                ?new String[]{"quantity","barcode","description","item_number","location"}
                :new String[]{"quantity","barcode","description","price"};
        for(String f:ALL){order.add(f);enabled.put(f,false);}
        for(String f:fields)enabled.put(f,true);
        selectedIndex=0;renderRows();
    }

'''.replace("+", "")
new_preset = '''    private void applyPreset(boolean victoria){
        order.clear();enabled.clear();
        String[] fields=victoria
                ?new String[]{"quantity","barcode","description","item_number","location"}
                :new String[]{"quantity","barcode","description","price"};
        for(String f:ALL){order.add(f);enabled.put(f,false);}
        for(String f:fields)enabled.put(f,true);
        selectedIndex=0;renderRows();saveCurrentOrder();
        toast(victoria?"Saved Victoria format":"Saved Generic POS format");
    }

'''.replace("+", "")
if f.count(old_preset) != 1:
    raise SystemExit("Victoria/Generic preset ending missing or ambiguous")
f = f.replace(old_preset, new_preset, 1)

old_save = '''    private void saveAndFinish(){
        StringBuilder b=new StringBuilder();
        for(String f:order){
            boolean use="barcode".equals(f)||Boolean.TRUE.equals(enabled.get(f));
            if(!use)continue;
            if(b.length()>0)b.append(',');b.append(f);
        }
        if(b.indexOf("barcode")<0){if(b.length()>0)b.insert(0,',');b.insert(0,"barcode");}
        String key=MODE_EXPORT.equals(mode)?KEY_EXPORT:KEY_IMPORT;
        SharedPreferences.Editor editor=prefs().edit().putString(key,b.toString());
        if(MODE_EXPORT.equals(mode)&&positiveOnly!=null)editor.putBoolean(KEY_EXPORT_POSITIVE_ONLY,positiveOnly.isChecked());
        editor.apply();
        setResult(RESULT_OK);
        finish();
    }
'''.replace("+", "")
new_save = '''    private void saveCurrentOrder(){
        StringBuilder b=new StringBuilder();
        for(String f:order){
            boolean use="barcode".equals(f)||Boolean.TRUE.equals(enabled.get(f));
            if(!use)continue;
            if(b.length()>0)b.append(',');b.append(f);
        }
        if(b.indexOf("barcode")<0){if(b.length()>0)b.insert(0,',');b.insert(0,"barcode");}
        String key=MODE_EXPORT.equals(mode)?KEY_EXPORT:KEY_IMPORT;
        SharedPreferences.Editor editor=prefs().edit().putString(key,b.toString());
        if(MODE_EXPORT.equals(mode)&&positiveOnly!=null)editor.putBoolean(KEY_EXPORT_POSITIVE_ONLY,positiveOnly.isChecked());
        editor.apply();
    }

    private void saveAndFinish(){
        saveCurrentOrder();
        setResult(RESULT_OK);
        finish();
    }
'''.replace("+", "")
if f.count(old_save) != 1:
    raise SystemExit("Format save method missing or unexpected")
f = f.replace(old_save, new_save, 1)

for old, new, label in [
    ('body.addView(text("TXT file • TAB delimited",18,gold(),true));', 'body.addView(text("CSV or TXT • comma or tab delimited",18,gold(),true));', "CSV/TXT label"),
    ('"Standard incoming order is Quantity, Barcode, Description, Price. Check optional fields only when they exist in the file, then use Move Up / Move Down to match the file. Barcode must remain included.";', '"Choose the preset matching your file. Fleet Feet uses Barcode, Item Number, Description, Size, with no quantity column. CSV and tab-delimited text files are supported; barcode must remain included.";', "import help text"),
    ('"Column setup is LOCKED. You can continue using the saved setup."', '"Column setup is locked for manual edits. Select a preset to save its column order."', "locked setup guidance"),
    ('"CONTINUE TO FILE"', '"SAVE IMPORT FORMAT"', "save button label"),
]:
    if f.count(old) != 1:
        raise SystemExit(label + " missing or ambiguous")
    f = f.replace(old, new, 1)

fmt_path.write_text(f)

checks = {
    "release version": "versionName '3.0.213'" in gradle.read_text() and "iCE Onhand 3.0.213" in manifest.read_text() and "Onhand Inventory 3.0.213" in main.read_text(),
    "Fleet Feet source order": 'String[] fields={"barcode","item_number","description","size"};' in f and 'for(String field:fields){order.add(field);enabled.put(field,true);}' in f,
    "all preset buttons save immediately": f.count("saveCurrentOrder();") >= 3,
    "clear save action": '"SAVE IMPORT FORMAT"' in f,
    "CSV and tab formats explained": 'CSV or TXT • comma or tab delimited' in f,
    "Fleet Feet import guidance": "Fleet Feet uses Barcode, Item Number, Description, Size" in f,
    "lock guidance explains presets": "Select a preset to save its column order" in f,
    "workflow updated": ".github/prepare_30213.py" in workflow.read_text() and "3.0.213" in workflow.read_text(),
}
failed=[name for name,passed in checks.items() if not passed]
if failed:
    raise SystemExit("3.0.213 validation failed: "+", ".join(failed))
print("Prepared iCE OnHand 3.0.213 with corrected and immediately saved import presets.")
