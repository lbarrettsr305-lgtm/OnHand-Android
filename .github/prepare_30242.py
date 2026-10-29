#!/usr/bin/env python3
"""OnHand 3.0.242: map Victoria location UPCs in uploaded count batches."""
from pathlib import Path
import os
import runpy

root = Path(__file__).resolve().parents[1]
workflow = root / ".github/workflows/build-apk.yml"
w = workflow.read_text()
for new, old, expected in [
    ("Prepare and verify 3.0.242 Victoria batch location UPC reports",
     "Prepare and verify 3.0.241 Victoria location UPC map", 1),
    (".github/prepare_30242.py", ".github/prepare_30241.py", 1),
    ("iCE-Onhand-Inventory-3.0.242", "iCE-Onhand-Inventory-3.0.241", 4),
]:
    if w.count(new) != expected:
        raise SystemExit("3.0.242 workflow marker missing: " + new)
    w = w.replace(new, old)
workflow.write_text(w)

if os.environ.get("ONHAND_PREPARED_30241") != "1":
    runpy.run_path(str(root / ".github/prepare_30241.py"), run_name="__main__")

merge = root / "app/src/main/java/com/iceinventory/onhand/BatchMergeActivity.java"
s = merge.read_text()
old = '''    private void addBatchRow(BatchStat stat,String[] v,int bi,int qi,int di,int pi,int ii,int li,double q)throws Exception{
        String code=v[bi].trim(),location=clean(v[li]);'''
new = '''    private String mapVictoriaLocationUpc(String location){
        if(location==null)return "";
        String code=location.trim();
        switch(code){
            case "21100141022":return "WH-2 TEA UNDER BACK STAIRS";
            case "21100140022":return "WH-2 CAPPUCHINO BACK STAIRS";
            case "21100139022":return "WH-2 RIGHT WALL UNDER RACK";
            case "21100138022":return "WH-2 RIGHT WALL FLOOR DISPLAYS";
            case "21100137022":return "WH-2 LEFT WALL UNDER RACK";
            case "21100136022":return "WH-2 LEFT WALL SYRUPS";
            case "21100135022":return "WH-1 FRONT DISPLAYS";
            case "21100134022":return "WH-1 BACK WALL RACK";
            case "21100133022":return "WH-1 FLOOR DISPLAYS";
            case "21100132022":return "UPSTAIRS";
            case "21100131022":return "SHOWROOM";
            default:return location;
        }
    }

    private void addBatchRow(BatchStat stat,String[] v,int bi,int qi,int di,int pi,int ii,int li,double q)throws Exception{
        String code=v[bi].trim(),location=mapVictoriaLocationUpc(clean(v[li]));'''
if s.count(old) != 1:
    raise SystemExit("BatchMerge location import anchor mismatch: " + str(s.count(old)))
merge.write_text(s.replace(old, new, 1))

doc = root / "VICTORIA-COFFEE-LOCATION-MAP.md"
d = doc.read_text()
if d.count("OnHand 3.0.241") != 1:
    raise SystemExit("location map 3.0.241 title marker missing")
d = d.replace("OnHand 3.0.241", "OnHand 3.0.242", 1)
anchor = "## Counting and audit flow\n"
note = "## Counting and audit flow\n\nUploaded Victoria batches also translate a listed LOCATION UPC into its matching LOCATION DESCRIPTION before the user totals and location reports are calculated. Rows already saved under a generic location such as `OVERHEAD` remain generic until corrected.\n\n"
if d.count(anchor) != 1:
    raise SystemExit("location workflow documentation anchor mismatch")
d = d.replace(anchor, note, 1)
doc.write_text(d)

gradle = root / "app/build.gradle"
g = gradle.read_text()
if g.count("versionCode 30241") != 1 or g.count("versionName '3.0.241'") != 1:
    raise SystemExit("Gradle 3.0.241 markers missing")
gradle.write_text(g.replace("versionCode 30241", "versionCode 30242", 1)
                  .replace("versionName '3.0.241'", "versionName '3.0.242'", 1))

manifest = root / "app/src/main/AndroidManifest.xml"
m = manifest.read_text()
if m.count("iCE Onhand 3.0.241") != 1:
    raise SystemExit("manifest 3.0.241 marker missing")
manifest.write_text(m.replace("iCE Onhand 3.0.241", "iCE Onhand 3.0.242", 1))

main = root / "app/src/main/java/com/iceinventory/onhand/MainActivity.java"
s = main.read_text()
if s.count("Onhand Inventory 3.0.241") != 1:
    raise SystemExit("main screen 3.0.241 marker missing")
main.write_text(s.replace("Onhand Inventory 3.0.241", "Onhand Inventory 3.0.242", 1))

w = workflow.read_text()
for old, new, expected in [
    ("Prepare and verify 3.0.241 Victoria location UPC map",
     "Prepare and verify 3.0.242 Victoria batch location UPC reports", 1),
    (".github/prepare_30241.py", ".github/prepare_30242.py", 1),
    ("iCE-Onhand-Inventory-3.0.241", "iCE-Onhand-Inventory-3.0.242", 4),
]:
    if w.count(old) != expected:
        raise SystemExit("3.0.241 workflow restore marker mismatch: " + old)
    w = w.replace(old, new)
workflow.write_text(w)

checks = {
    "batch mapping": "mapVictoriaLocationUpc(clean(v[li]))" in merge.read_text(),
    "all 11 UPCs mapped": all(code in merge.read_text() for code in [
        "21100141022", "21100140022", "21100139022", "21100138022", "21100137022",
        "21100136022", "21100135022", "21100134022", "21100133022", "21100132022", "21100131022"]),
    "location audit note": "Uploaded Victoria batches also translate a listed LOCATION UPC" in doc.read_text(),
    "release version": "versionCode 30242" in gradle.read_text() and "versionName '3.0.242'" in gradle.read_text(),
    "workflow uses current prep": ".github/prepare_30242.py" in workflow.read_text(),
}
failed = [name for name, passed in checks.items() if not passed]
if failed:
    raise SystemExit("3.0.242 validation failed: " + ", ".join(failed))
print("Prepared OnHand 3.0.242: imported Victoria batch LOCATION UPCs are translated to descriptions before location totals and reports.")
