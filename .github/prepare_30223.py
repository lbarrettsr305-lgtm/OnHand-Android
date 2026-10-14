#!/usr/bin/env python3
from pathlib import Path
import re
import runpy

root = Path(__file__).resolve().parent.parent
workflow = root / ".github/workflows/build-apk.yml"

# Re-run the validated 3.0.222 preparation from its expected workflow markers.
w = workflow.read_text()
for new, old in [
    ("Prepare and verify 3.0.223 store-user-match report filenames", "Prepare and verify 3.0.222 clean Fleet Feet batch export"),
    (".github/prepare_30223.py", ".github/prepare_30222.py"),
    ("iCE-Onhand-Inventory-3.0.223", "iCE-Onhand-Inventory-3.0.222"),
]:
    if new not in w:
        raise SystemExit("3.0.223 workflow seed missing: " + new)
    w = w.replace(new, old)
workflow.write_text(w)
runpy.run_path(str(root / ".github/prepare_30222.py"), run_name="__main__")

# Advance the build to 3.0.223 after the previous release's checks have passed.
w = workflow.read_text()
for old, new in [
    ("Prepare and verify 3.0.222 clean Fleet Feet batch export", "Prepare and verify 3.0.223 store-user-match report filenames"),
    (".github/prepare_30222.py", ".github/prepare_30223.py"),
    ("iCE-Onhand-Inventory-3.0.222", "iCE-Onhand-Inventory-3.0.223"),
]:
    if old not in w:
        raise SystemExit("3.0.222 workflow marker missing: " + old)
    w = w.replace(old, new)
workflow.write_text(w)

main = root / "app/src/main/java/com/iceinventory/onhand/MainActivity.java"
s = main.read_text()

# Every filename offered by the counting/report screen gets a store, user, and
# match number first. Keep its existing report label and extension after that.
anchor = "    private String safeFileName(String s){"
helper = '''    private String storeUserMatchPrefix(){
        String store=sessionName==null?"":sessionName.trim();
        String user=savedUserName()==null?"":savedUserName().trim();
        if(store.isEmpty())store="Inventory";
        if(user.isEmpty())user="Counter";
        int number=pendingBatchNumber>0?pendingBatchNumber:db.nextBatchNumber(sessionId);
        return safeFileName(store)+"-"+safeFileName(user)+"-"+String.format(Locale.US,"%02d",Math.max(1,number));
    }

    private String withStoreUserMatchPrefix(String filename){
        String name=filename==null?"":filename.trim();
        if(name.isEmpty())name="Report";
        String prefix=storeUserMatchPrefix();
        return name.startsWith(prefix+"-")?name:prefix+"-"+name;
    }

'''
if s.count(anchor) != 1:
    raise SystemExit("3.0.223 MainActivity filename helper anchor missing or ambiguous")
s = s.replace(anchor, helper + anchor, 1)

# Catch every report/count document picker, including paths that don't use the
# usual batch filename helper.
pattern = r'([A-Za-z_]\w*)\.putExtra\(Intent\.EXTRA_TITLE,(.*?)\);'
s, title_count = re.subn(pattern, lambda m: m.group(1) + ".putExtra(Intent.EXTRA_TITLE,withStoreUserMatchPrefix(" + m.group(2) + "));", s, flags=re.S)
if title_count < 1:
    raise SystemExit("3.0.223 MainActivity document titles were not found")

# Keep batch and complete exports concise while retaining the report identity.
batch = '''    private String batchExportFileName(){String ext=pendingExportExcel?".xlsx":".txt";return storeUserMatchPrefix()+"-Batch Count"+ext;}'''
s, batch_count = re.subn(r'    private String batchExportFileName\(\)\{.*?\}', batch, s, count=1, flags=re.S)
complete = '''    private String completeExportFileName(){String ext=pendingExportExcel?".xlsx":".txt";return storeUserMatchPrefix()+"-Complete Inventory"+ext;}'''
s, complete_count = re.subn(r'    private String completeExportFileName\(\)\{.*?\}', complete, s, count=1, flags=re.S)
if batch_count != 1 or complete_count != 1:
    raise SystemExit("3.0.223 batch filename helpers missing or ambiguous")

# Audit reports carry their name after the common prefix.
audit = '''    private String auditExportFileName(String ignored) {
        String report=pendingAuditSort==1?"Highest Unit Price":(pendingAuditSort==2?"Highest Extended Value":"Highest Quantity");
        return storeUserMatchPrefix()+"-"+report+".xlsx";
    }'''
s, audit_count = re.subn(r'    private String auditExportFileName\(String ignored\) \{.*?\n    \}', audit, s, count=1, flags=re.S)
if audit_count != 1:
    raise SystemExit("3.0.223 audit filename helper missing or ambiguous")
main.write_text(s)

# Combined master reports use the selected store and Master user. Where source
# filenames already carry a match number, keep that same number on the outputs.
merge = root / "app/src/main/java/com/iceinventory/onhand/BatchMergeActivity.java"
b = merge.read_text()
imports = "import java.util.regex.Matcher;\nimport java.util.regex.Pattern;\n"
if "import java.util.regex.Matcher;" not in b:
    b = b.replace("import java.util.Map;\n", "import java.util.Map;\n" + imports, 1)
old = '''    private String combinedOutputName(String report,String inventory){String u=safeFilePart(savedUserName());String b=safeFilePart(inventory);return report+" - COMBINED"+(u.isEmpty()?"":" - "+u)+" - "+b;}'''
new = '''    private String combinedOutputName(String report,String inventory){String store=safeFilePart(sourceInventoryName());String user=safeFilePart(savedUserName());if(store.isEmpty())store="Inventory";if(user.isEmpty())user="Master";return store+"-"+user+"-"+reportMatchNumber()+"-"+safeFilePart(report)+"-"+safeFilePart(inventory);}\n\n    private String reportMatchNumber(){int number=1;Pattern p=Pattern.compile("-(\\\\d{2})(?:-|\\\\.)");Pattern legacy=Pattern.compile("(?i)Batch(\\\\d+)");for(BatchStat stat:sourceStats){Matcher m=p.matcher(stat.fileName);if(m.find())return String.format(Locale.US,"%02d",Integer.parseInt(m.group(1)));m=legacy.matcher(stat.fileName);if(m.find())return String.format(Locale.US,"%02d",Integer.parseInt(m.group(1)));}return String.format(Locale.US,"%02d",number);}'''
if b.count(old) != 1:
    raise SystemExit("3.0.223 combined report filename helper missing or ambiguous")
b = b.replace(old, new, 1)
merge.write_text(b)

# Monthly/Petrosoft outputs also get the same prefix; the report name, store,
# date, and file extension remain visible after it.
monthly = root / "app/src/main/java/com/iceinventory/onhand/MonthlyInventoryActivity.java"
m = monthly.read_text()
old = '''    private void create(int request,String type,String name){Intent i=new Intent(Intent.ACTION_CREATE_DOCUMENT);i.addCategory(Intent.CATEGORY_OPENABLE);i.setType(type);i.putExtra(Intent.EXTRA_TITLE,name);startActivityForResult(i,request);}'''
new = '''    private void create(int request,String type,String name){Intent i=new Intent(Intent.ACTION_CREATE_DOCUMENT);i.addCategory(Intent.CATEGORY_OPENABLE);i.setType(type);i.putExtra(Intent.EXTRA_TITLE,withStoreUserMatchPrefix(name));startActivityForResult(i,request);}\n\n    private String withStoreUserMatchPrefix(String filename){String name=filename==null?"":filename.trim();if(name.isEmpty())name="Report";String store=base()==null?"":base().trim();if(store.isEmpty())store="Inventory";String user=getSharedPreferences("onhand_settings",MODE_PRIVATE).getString("export_user_name","Master");if(user==null||user.trim().isEmpty())user="Master";int match=1;Pattern p=Pattern.compile("-(\\\\d{2})(?:-|\\\\.)");for(CountFile file:countFiles){Matcher found=p.matcher(file.name);if(found.find()){match=Integer.parseInt(found.group(1));break;}}String prefix=safeMonthlyName(store)+"-"+safeMonthlyName(user)+"-"+String.format(Locale.US,"%02d",match);return name.startsWith(prefix+"-")?name:prefix+"-"+name;}\n\n    private String safeMonthlyName(String value){return value==null?"":value.trim().replaceAll("[^A-Za-z0-9._-]+","_");}'''
if m.count(old) != 1:
    raise SystemExit("3.0.223 monthly filename helper missing or ambiguous")
m = m.replace(old, new, 1)
m = m.replace("import java.util.Map;\n", "import java.util.Map;\nimport java.util.regex.Matcher;\nimport java.util.regex.Pattern;\n", 1)
monthly.write_text(m)

gradle = root / "app/build.gradle"
g = gradle.read_text()
if "versionCode 30222" not in g or "versionName '3.0.222'" not in g:
    raise SystemExit("3.0.222 Gradle version missing")
gradle.write_text(g.replace("versionCode 30222", "versionCode 30223", 1).replace("versionName '3.0.222'", "versionName '3.0.223'", 1))

manifest = root / "app/src/main/AndroidManifest.xml"
text = manifest.read_text()
if text.count("iCE Onhand 3.0.222") != 1:
    raise SystemExit("3.0.222 manifest label missing")
manifest.write_text(text.replace("iCE Onhand 3.0.222", "iCE Onhand 3.0.223", 1))

main_text = main.read_text()
if main_text.count("Onhand Inventory 3.0.222") != 1:
    raise SystemExit("3.0.222 home label missing")
main.write_text(main_text.replace("Onhand Inventory 3.0.222", "Onhand Inventory 3.0.223", 1))

# Build-time guards verify the common prefix reaches all export surfaces.
main_text = main.read_text()
merge_text = merge.read_text()
monthly_text = monthly.read_text()
checks = {
    "count reports use store-user-match prefix": "withStoreUserMatchPrefix" in main_text and "storeUserMatchPrefix()" in main_text,
    "batch export name is concise": "-Batch Count" in main_text,
    "audit report titles follow prefix": "storeUserMatchPrefix()+\"-\"+report+\".xlsx\"" in main_text,
    "combined reports use selected match number": "reportMatchNumber()" in merge_text and "safeFilePart(report)" in merge_text,
    "monthly exports use user and match": "withStoreUserMatchPrefix(name)" in monthly_text and "export_user_name" in monthly_text,
    "version labels": "versionName '3.0.223'" in gradle.read_text() and "iCE Onhand 3.0.223" in manifest.read_text() and "Onhand Inventory 3.0.223" in main_text,
    "workflow points to release": ".github/prepare_30223.py" in workflow.read_text() and "3.0.223" in workflow.read_text(),
}
failed = [name for name, passed in checks.items() if not passed]
if failed:
    raise SystemExit("3.0.223 validation failed: " + ", ".join(failed))
print("Prepared iCE OnHand 3.0.223: count, audit, combined, and monthly export filenames begin with store-user-match number.")
