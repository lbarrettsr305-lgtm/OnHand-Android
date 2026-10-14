#!/usr/bin/env python3
"""OnHand 3.0.231: add Fleet Feet export template, repair saved import order, and export size/item number in XLSX."""
from pathlib import Path
import runpy

root=Path(__file__).resolve().parent.parent
workflow=root/".github/workflows/build-apk.yml"
w=workflow.read_text()
for new,old,expected in [
    ("Prepare and verify 3.0.231 Fleet Feet import and export formats","Prepare and verify 3.0.230 Fleet Feet preset and direct batch quantity report",1),
    (".github/prepare_30231.py",".github/prepare_30230.py",1),
    ("iCE-Onhand-Inventory-3.0.231","iCE-Onhand-Inventory-3.0.230",4),
]:
    if w.count(new)!=expected:raise SystemExit("3.0.231 workflow seed mismatch: "+new)
    w=w.replace(new,old)
workflow.write_text(w)
runpy.run_path(str(root/".github/prepare_30230.py"),run_name="__main__")
w=workflow.read_text()
for old,new,expected in [
    ("Prepare and verify 3.0.230 Fleet Feet preset and direct batch quantity report","Prepare and verify 3.0.231 Fleet Feet import and export formats",1),
    (".github/prepare_30230.py",".github/prepare_30231.py",1),
    ("iCE-Onhand-Inventory-3.0.230","iCE-Onhand-Inventory-3.0.231",4),
]:
    if w.count(old)!=expected:raise SystemExit("3.0.230 workflow mismatch: "+old)
    w=w.replace(old,new)
workflow.write_text(w)

gradle=root/"app/build.gradle"
g=gradle.read_text()
if g.count("versionCode 30230")!=1 or g.count("versionName '3.0.230'")!=1:raise SystemExit("Previous Android version missing")
gradle.write_text(g.replace("versionCode 30230","versionCode 30231",1).replace("versionName '3.0.230'","versionName '3.0.231'",1))
manifest=root/"app/src/main/AndroidManifest.xml"
m=manifest.read_text()
if m.count("iCE Onhand 3.0.230")!=1:raise SystemExit("Previous manifest label missing")
manifest.write_text(m.replace("iCE Onhand 3.0.230","iCE Onhand 3.0.231",1))
main=root/"app/src/main/java/com/iceinventory/onhand/MainActivity.java"
s=main.read_text()
if s.count("Onhand Inventory 3.0.230")!=1:raise SystemExit("Previous visible version missing")
main.write_text(s.replace("Onhand Inventory 3.0.230","Onhand Inventory 3.0.231",1))

fmt=root/"app/src/main/java/com/iceinventory/onhand/FormatConfigActivity.java"
f=fmt.read_text()

# Always show Fleet Feet next to Victoria/Generic as a reusable format choice.
# Put the third button on a separate row to avoid three squeezed labels.
old='''        if(MODE_IMPORT.equals(mode)){
            victoria.setTextSize(14);generic.setTextSize(14);
            Button fleetFeet=button("Fleet Feet");fleetFeet.setTextSize(14);
            fleetFeet.setOnClickListener(v->applyFleetFeetPreset());
            LinearLayout.LayoutParams fp=new LinearLayout.LayoutParams(0,dp(48),1);fp.setMargins(dp(6),0,0,0);presets.addView(fleetFeet,fp);
        }'''
new='''        victoria.setTextSize(15);generic.setTextSize(15);
        Button fleetFeet=button("Fleet Feet");
        fleetFeet.setTextSize(16);
        fleetFeet.setOnClickListener(v->applyFleetFeetPreset());'''
if f.count(old)!=1:raise SystemExit("Existing import-only Fleet Feet preset button missing")
f=f.replace(old,new,1)
old='        body.addView(presets);'
new='''        body.addView(presets);
        LinearLayout.LayoutParams fleetRow=new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT,dp(48));
        fleetRow.setMargins(0,dp(6),0,dp(3));
        body.addView(fleetFeet,fleetRow);'''
if f.count(old)!=1:raise SystemExit("Format presets row missing")
f=f.replace(old,new,1)

# Import: BARCODE, DESCRIPTION, ITEM NUMBER, SIZE
# Export: QTY, BARCODE, DESCRIPTION, ITEM NUMBER, SIZE.
old='        String[] fields={"barcode","description","item_number","size"};'
new='''        String[] fields=MODE_EXPORT.equals(mode)
                ?new String[]{"quantity","barcode","description","item_number","size"}
                :new String[]{"barcode","description","item_number","size"};'''
if f.count(old)!=1:raise SystemExit("Fleet Feet import preset order missing")
f=f.replace(old,new,1)
f=f.replace('toast("Saved Fleet Feet import format");','toast(MODE_EXPORT.equals(mode)?"Saved Fleet Feet export format":"Saved Fleet Feet import format");',1)

# Upgrade stored settings from older versions on opening the import-format screen:
# merely upgrading the code did not reorder previously saved Fleet Feet mappings.
old='''        if(!MODE_EXPORT.equals(mode))mode=MODE_IMPORT;
        load();'''
new='''        if(!MODE_EXPORT.equals(mode))mode=MODE_IMPORT;
        if(MODE_IMPORT.equals(mode)){
            String oldFleet=prefs().getString(KEY_IMPORT,"");
            if("barcode,item_number,description,size".equals(oldFleet))
                prefs().edit().putString(KEY_IMPORT,"barcode,description,item_number,size").apply();
        }
        load();'''
if f.count(old)!=1:raise SystemExit("Format load initialization missing")
f=f.replace(old,new,1)

# Make the help text unambiguous about input vs customer output.
f=f.replace('String helpText=MODE_EXPORT.equals(mode)','String helpText=MODE_EXPORT.equals(mode)',1)
f=f.replace('Use the Generic POS preset for Quantity, Barcode, Description, Price, or Victoria for QTY, BARCODE, DESCRIPTION, ITEM NUMBER, LOCATION.',
'''Choose Generic POS, Victoria, or Fleet Feet. Fleet Feet customer output is QTY, BARCODE, DESCRIPTION, ITEM NUMBER, SIZE (no Location). User batch files still include Location for audit.''')
f=f.replace('Choose and save a column setup here, or choose a preset each time you import.',
'''Fleet Feet imports BARCODE, DESCRIPTION, ITEM NUMBER, SIZE. Choose and save a format here, or choose a preset each time you import.''')
fmt.write_text(f)

tab=root/"app/src/main/java/com/iceinventory/onhand/TabTextUtils.java"
t=tab.read_text()
# Batch source exports must preserve Location. The five-column Fleet Feet
# customer report is different from counter/source exports.
marker='    public static String exportRows('
customer='''    public static List<String> getCustomerOrder(SharedPreferences prefs){
        List<String> fields=new ArrayList<>(getOrder(prefs,true));
        String selected=prefs.getString(KEY_EXPORT,"").trim();
        if("quantity,barcode,description,item_number,size".equals(selected))
            fields.remove("location");
        return fields;
    }

'''
if t.count(marker)!=1:raise SystemExit("Normal TXT exporter insertion point missing")
t=t.replace(marker,customer+marker,1)
start=t.index("    public static String exportRows(")
end=t.find("\n    public static String exportHeader(",start)
if end<0:raise SystemExit("Normal TXT export method end missing")
part=t[start:end]
if part.count("List<String> order=getOrder(prefs,true);")!=1:raise SystemExit("Normal TXT mapping call missing")
part=part.replace("List<String> order=getOrder(prefs,true);","List<String> order=getCustomerOrder(prefs);",1)
t=t[:start]+part+t[end:]
tab.write_text(t)

# Excel customer files must use the same selected columns as TXT, including
# the size in its own cell instead of appended to the description.
xlsx=root/"app/src/main/java/com/iceinventory/onhand/SimpleXlsxWriter.java"
x=xlsx.read_text()
old='        List<String> order=TabTextUtils.getOrder(prefs,true);'
new='''        List<String> order=preserveAdjustments
                ?TabTextUtils.getOrder(prefs,true)
                :TabTextUtils.getCustomerOrder(prefs);'''
if x.count(old)!=1:raise SystemExit("XLSX export column-order call missing")
x=x.replace(old,new,1)
old='value(field,row,when,dateFmt,timeFmt)'
new='value(field,row,when,dateFmt,timeFmt,order.contains("size"))'
if x.count(old)!=1:raise SystemExit("XLSX value invocation missing")
x=x.replace(old,new,1)
old='''    private static String value(String field,InventoryDb.Row r,Date when,SimpleDateFormat dateFmt,SimpleDateFormat timeFmt){
        if("barcode".equals(field))return clean(r.barcode);
        if("description".equals(field))return clean(r.description);
        if("price".equals(field))return clean(r.price);'''
new='''    private static String value(String field,InventoryDb.Row r,Date when,SimpleDateFormat dateFmt,SimpleDateFormat timeFmt,boolean sizeColumn){
        if("barcode".equals(field))return clean(r.barcode);
        if("description".equals(field))return clean(sizeColumn?descriptionWithoutSize(r.description):r.description);
        if("item_number".equals(field))return clean(r.itemNumber);
        if("size".equals(field))return clean(sizeFromDescription(r.description));
        if("price".equals(field))return clean(r.price);'''
if x.count(old)!=1:raise SystemExit("XLSX values mapping missing")
x=x.replace(old,new,1)
old='        if("description".equals(field))return 46;'
new='''        if("description".equals(field))return 46;
        if("item_number".equals(field))return 24;
        if("size".equals(field))return 16;'''
if x.count(old)!=1:raise SystemExit("XLSX width mapping missing")
x=x.replace(old,new,1)
marker='    private static String clean(String s){'
helpers='''    private static int sizeSuffixStart(String description){
        if(description==null||!description.endsWith("]"))return -1;
        int start=description.lastIndexOf("[Size: ");
        if(start<0||(start>0&&description.charAt(start-1)!=' '))return -1;
        return start;
    }
    private static String sizeFromDescription(String description){
        int start=sizeSuffixStart(description);
        return start<0?"":description.substring(start+7,description.length()-1).trim();
    }
    private static String descriptionWithoutSize(String description){
        int start=sizeSuffixStart(description);
        return start<0?(description==null?"":description):description.substring(0,start).trim();
    }

'''
if x.count(marker)!=1:raise SystemExit("XLSX helper anchor missing")
x=x.replace(marker,helpers+marker,1)
xlsx.write_text(x)

checks={
    "version": "versionName '3.0.231'" in gradle.read_text() and "iCE Onhand 3.0.231" in manifest.read_text() and "Onhand Inventory 3.0.231" in main.read_text(),
    "Fleet export button": f.count('Button fleetFeet=button("Fleet Feet")')==1 and 'body.addView(fleetFeet,fleetRow);' in f,
    "correct Fleet import order": 'new String[]{"barcode","description","item_number","size"}' in f,
    "correct Fleet export order": 'new String[]{"quantity","barcode","description","item_number","size"}' in f,
    "old saved order migration": 'prefs().edit().putString(KEY_IMPORT,"barcode,description,item_number,size").apply();' in f,
    "saved preset labels": "Saved Fleet Feet export format" in f,
    "customer-only location removal": '"quantity,barcode,description,item_number,size".equals(selected)' in t and 'fields.remove("location");' in t,
    "batch source location retained": 'if(export&&!out.contains("location"))out.add("location")' in t,
    "TXT customer format": 'List<String> order=getCustomerOrder(prefs);' in t,
    "Excel customer format": 'TabTextUtils.getCustomerOrder(prefs)' in x,
    "Excel separate size and item": 'if("size".equals(field))return clean(sizeFromDescription(r.description));' in x and 'if("item_number".equals(field))return clean(r.itemNumber);' in x,
    "workflow": ".github/prepare_30231.py" in workflow.read_text() and "3.0.231" in workflow.read_text(),
}
failed=[key for key,passed in checks.items() if not passed]
if failed:raise SystemExit("3.0.231 validation failed: "+", ".join(failed))
print("Prepared OnHand 3.0.231: Fleet Feet export preset in TXT/Excel, input order migration, unchanged source batch locations.")
