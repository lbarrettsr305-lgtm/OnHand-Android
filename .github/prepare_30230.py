#!/usr/bin/env python3
"""Build 3.0.230 with readable Options, corrected Fleet Feet, and direct batch audit."""
from pathlib import Path
import runpy
import re

root=Path(__file__).resolve().parent.parent
workflow=root/".github/workflows/build-apk.yml"

w=workflow.read_text()
for new,old,expected in [
    ("Prepare and verify 3.0.230 Fleet Feet preset and direct batch quantity report","Prepare and verify 3.0.229 aligned footer and independent export template editor",1),
    (".github/prepare_30230.py",".github/prepare_30229.py",1),
    ("iCE-Onhand-Inventory-3.0.230","iCE-Onhand-Inventory-3.0.229",4),
]:
    if w.count(new)!=expected:raise SystemExit("3.0.230 workflow marker ambiguous: "+new)
    w=w.replace(new,old)
workflow.write_text(w)

runpy.run_path(str(root/".github/prepare_30229.py"),run_name="__main__")

w=workflow.read_text()
for old,new,expected in [
    ("Prepare and verify 3.0.229 aligned footer and independent export template editor","Prepare and verify 3.0.230 Fleet Feet preset and direct batch quantity report",1),
    (".github/prepare_30229.py",".github/prepare_30230.py",1),
    ("iCE-Onhand-Inventory-3.0.229","iCE-Onhand-Inventory-3.0.230",4),
]:
    if w.count(old)!=expected:raise SystemExit("3.0.229 workflow marker ambiguous: "+old)
    w=w.replace(old,new)
workflow.write_text(w)

gradle=root/"app/build.gradle"
g=gradle.read_text()
if g.count("versionCode 30229")!=1 or g.count("versionName '3.0.229'")!=1:
    raise SystemExit("Prior Gradle version absent")
gradle.write_text(g.replace("versionCode 30229","versionCode 30230",1)
                    .replace("versionName '3.0.229'","versionName '3.0.230'",1))

manifest=root/"app/src/main/AndroidManifest.xml"
m=manifest.read_text()
if m.count("iCE Onhand 3.0.229")!=1:raise SystemExit("Prior manifest version missing")
m=m.replace("iCE Onhand 3.0.229","iCE Onhand 3.0.230",1)
anchor='<activity\n            android:name=".BatchMergeActivity"'
if m.count(anchor)!=1:raise SystemExit("BatchMergeActivity manifest anchor missing")
m=m.replace(anchor,'<activity\n            android:name=".BatchQuantityReportActivity"\n            android:exported="false" />\n        '+anchor,1)
manifest.write_text(m)

main=root/"app/src/main/java/com/iceinventory/onhand/MainActivity.java"
s=main.read_text()
if s.count("Onhand Inventory 3.0.229")!=1:raise SystemExit("Prior visible version missing")
s=s.replace("Onhand Inventory 3.0.229","Onhand Inventory 3.0.230",1)

# Direct button on the Master home screen, visible without opening Export.
anchor="        root.addView(sessionBar);"
home='''        if(isMasterDevice()){
            Button batchTotals=button("BATCH QTY REPORT",2);
            batchTotals.setTextSize(15f);
            batchTotals.setSingleLine(true);
            batchTotals.setContentDescription("Review total quantities in returned user batch files");
            batchTotals.setOnClickListener(v->openBatchQuantityReport());
            LinearLayout.LayoutParams batchLp=new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT,dp(50));
            batchLp.setMargins(0,dp(6),0,dp(6));
            root.addView(batchTotals,batchLp);
        }
'''
if s.count(anchor)!=1:raise SystemExit("Master toolbar insertion point missing")
s=s.replace(anchor,anchor+"\n"+home,1)

# Reuse one method for the home button, Export menu and Options shortcut.
anchor="    private void showOptions()"
method='''    private void openBatchQuantityReport(){
        Intent report=new Intent(this,BatchQuantityReportActivity.class);
        report.putExtra("report_store",sessionName);
        startActivity(report);
    }

'''
if s.count(anchor)!=1:raise SystemExit("Settings method insertion anchor missing")
s=s.replace(anchor,method+anchor,1)

# A top-level entry in Export Reports also leads to the same audit.
export_section='        addExportSection(exportPanel,"INVENTORY EXPORTS");'
if s.count(export_section)!=1:raise SystemExit("Export Reports section anchor missing")
s=s.replace(export_section,'''        addExportSection(exportPanel,"BATCH CONTROL");
        addExportButton(exportPanel,exportDialog,"BATCH QTY REPORT — BY USER / LOCATION",19);
'''+export_section,1)

choice=re.search(r'    private void handleExportChoice\(int which\)\s*\{',s)
if not choice:raise SystemExit("Export choice handler missing")
s=s[:choice.end()]+'\n        if(which==19){openBatchQuantityReport();return;}'+s[choice.end():]

# Put report/template setup near top, not after all Recovery/Inventory settings.
options_start=s.find("    private void showOptions()")
options_end=s.find("    private String friendlyUnknownMode()",options_start)
if options_start<0 or options_end<0:raise SystemExit("Options method boundaries missing")
options=s[options_start:options_end]
begin=options.find('        TextView importExport=text("Import / Export"')
end_marker='        box.addView(exportFormat,new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT,dp(56)));'
end=options.find(end_marker,begin)
if begin<0 or end<0:raise SystemExit("Options import/export group missing")
end+=len(end_marker)
group=options[begin:end]
options=options[:begin]+options[end:]
group=group.replace('TextView importExport=text("Import / Export"','TextView importExport=text("REPORTS & TEMPLATES"',1)
group=group.replace('button("EDIT EXPORT TEMPLATE (NO BATCH NEEDED)",0)','button("EDIT EXPORT TEMPLATE",0)',1)
group=group.replace('exportFormat.setTextSize(15);','exportFormat.setTextSize(15);exportFormat.setSingleLine(true);',1)
group+='''\n        TextView formatNote=text("Templates can be edited before a batch or count exists.",12,Color.WHITE,false);
        formatNote.setPadding(dp(4),dp(4),dp(4),dp(4));
        box.addView(formatNote);
        Button batchQuick=button("BATCH QTY REPORT",1);
        batchQuick.setTextSize(15);batchQuick.setSingleLine(true);
        batchQuick.setOnClickListener(v->openBatchQuantityReport());
        box.addView(batchQuick,new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT,dp(54)));
'''
scan_anchor='        TextView scanning=text("Scanning"'
if options.count(scan_anchor)!=1:raise SystemExit("Scanning group insertion anchor missing")
options=options.replace(scan_anchor,group+'\n        '+scan_anchor.strip(),1)
# Make long settings captions fit on one line at normal and enlarged font sizes.
options=options.replace('Unknown Barcode Behavior:\\nCurrent: ','Unknown Barcode: ')
options=options.replace('Unknown Barcode Behavior: ','Unknown Barcode: ')
options=options.replace('Maximum Qty per Barcode: ','Qty Warning Limit: ')
s=s[:options_start]+options+s[options_end:]

# Fleet Feet's field order is supplied by the customer; this is distinct
# from Victoria and Generic POS. Match headerless files in this exact order.
old_order="barcode,item_number,description,size"
new_order="barcode,description,item_number,size"
if s.count(old_order)<1:raise SystemExit("Fleet Feet chooser order missing")
s=s.replace(old_order,new_order)
s=s.replace("Barcode • Item Number • Description • Size","Barcode • Description • Item Number • Size")
s=s.replace("Barcode, Item Number, Description, Size","Barcode, Description, Item Number, Size")
# Upgrade old saved Fleet Feet preset when the format dialog opens.
chooser='    private void showStandardImportFormatDialog(){'
if s.count(chooser)!=1:raise SystemExit("Fleet Feet dialog method missing")
s=s.replace(chooser,chooser+'''
        String previouslySaved=prefs().getString("import_field_order","");
        if("barcode,item_number,description,size".equals(previouslySaved))
            prefs().edit().putString("import_field_order","barcode,description,item_number,size").apply();
''',1)
main.write_text(s)

fmt=root/"app/src/main/java/com/iceinventory/onhand/FormatConfigActivity.java"
f=fmt.read_text()
old='String[] fields={"barcode","item_number","description","size"};'
new='String[] fields={"barcode","description","item_number","size"};'
if f.count(old)!=1:raise SystemExit("Fleet Feet import preset fields missing")
f=f.replace(old,new,1)
f=f.replace("Barcode, Item Number, Description, Size","Barcode, Description, Item Number, Size")
# Standalone export template editor must clearly say Save, not start an export.
save_anchor='Button save=button("SAVE FORMAT");'
if f.count(save_anchor)!=1:raise SystemExit("Format screen Save Format button missing")
# Existing Save Format already saves locally only, no batch requirement.
fmt.write_text(f)

checks={
    "version": "versionName '3.0.230'" in gradle.read_text(),
    "manifest": "iCE Onhand 3.0.230" in manifest.read_text() and ".BatchQuantityReportActivity" in manifest.read_text(),
    "home version": "Onhand Inventory 3.0.230" in main.read_text(),
    "home access": 'Button batchTotals=button("BATCH QTY REPORT",2);' in main.read_text(),
    "export report link": 'BATCH QTY REPORT — BY USER / LOCATION' in main.read_text() and "if(which==19){openBatchQuantityReport();return;}" in main.read_text(),
    "settings shortcut": 'button("BATCH QTY REPORT",1)' in main.read_text(),
    "short export template": 'button("EDIT EXPORT TEMPLATE",0)' in main.read_text(),
    "correct Fleet Feet importer": "barcode,description,item_number,size" in main.read_text(),
    "correct Fleet Feet preset": 'String[] fields={"barcode","description","item_number","size"};' in fmt.read_text(),
    "read-only audit": "never" in (root/"app/src/main/java/com/iceinventory/onhand/BatchQuantityReportActivity.java").read_text(),
    "workflow": ".github/prepare_30230.py" in workflow.read_text() and "3.0.230" in workflow.read_text(),
}
failed=[key for key,passed in checks.items() if not passed]
if failed:raise SystemExit("3.0.230 validation failed: "+", ".join(failed))
print("Prepared iCE OnHand 3.0.230: visible batch QTY audit, readable Options, corrected Fleet Feet headerless mapping.")
