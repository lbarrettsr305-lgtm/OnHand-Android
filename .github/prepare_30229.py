#!/usr/bin/env python3
"""OnHand 3.0.229: align bottom import/export buttons and edit export template without any batch."""
from pathlib import Path
import runpy

root=Path(__file__).resolve().parent.parent
workflow=root / ".github/workflows/build-apk.yml"

w=workflow.read_text()
for new,old,expected in [
    ("Prepare and verify 3.0.229 aligned footer and independent export template editor","Prepare and verify 3.0.228 responsive new inventory import button",1),
    (".github/prepare_30229.py",".github/prepare_30228.py",1),
    ("iCE-Onhand-Inventory-3.0.229","iCE-Onhand-Inventory-3.0.228",4),
]:
    if w.count(new)!=expected: raise SystemExit("3.0.229 workflow seed mismatch: "+new)
    w=w.replace(new,old)
workflow.write_text(w)

runpy.run_path(str(root/".github/prepare_30228.py"),run_name="__main__")

w=workflow.read_text()
for old,new,expected in [
    ("Prepare and verify 3.0.228 responsive new inventory import button","Prepare and verify 3.0.229 aligned footer and independent export template editor",1),
    (".github/prepare_30228.py",".github/prepare_30229.py",1),
    ("iCE-Onhand-Inventory-3.0.228","iCE-Onhand-Inventory-3.0.229",4),
]:
    if w.count(old)!=expected: raise SystemExit("3.0.228 workflow marker mismatch: "+old)
    w=w.replace(old,new)
workflow.write_text(w)

gradle=root/"app/build.gradle"
g=gradle.read_text()
if g.count("versionCode 30228")!=1 or g.count("versionName '3.0.228'")!=1:raise SystemExit("Previous Gradle version missing")
g=g.replace("versionCode 30228","versionCode 30229",1).replace("versionName '3.0.228'","versionName '3.0.229'",1)
gradle.write_text(g)

manifest=root/"app/src/main/AndroidManifest.xml"
m=manifest.read_text()
if m.count("iCE Onhand 3.0.228")!=1:raise SystemExit("Previous manifest version missing")
manifest.write_text(m.replace("iCE Onhand 3.0.228","iCE Onhand 3.0.229",1))

main=root/"app/src/main/java/com/iceinventory/onhand/MainActivity.java"
s=main.read_text()
if s.count("Onhand Inventory 3.0.228")!=1:raise SystemExit("Previous home version missing")
s=s.replace("Onhand Inventory 3.0.228","Onhand Inventory 3.0.229",1)

# The two-line label and manual padding caused the bottom left control to
# appear lower than Export on several Galaxy screen sizes.
old=('Button imp=button("NEW INVENTORY\\n/ IMPORT",1);'
     'imp.setTextSize(12f);imp.setGravity(Gravity.CENTER);'
     'imp.setMaxLines(2);imp.setIncludeFontPadding(false);'
     'imp.setPadding(dp(2),0,dp(2),0);'
     'imp.setContentDescription("New inventory or import store file");')
new=('Button imp=button("NEW / IMPORT",1);'
     'imp.setTextSize(15f);imp.setGravity(Gravity.CENTER);'
     'imp.setSingleLine(true);imp.setMaxLines(1);'
     'imp.setIncludeFontPadding(false);'
     'imp.setContentDescription("New inventory or import store file");')
if s.count(old)!=1:raise SystemExit("Two-line bottom import button not found exactly once")
s=s.replace(old,new,1)

# Main-screen Options exists even for a brand-new project and does not need
# any count files. Insert the editor next to Configure Import Format.
options_start=s.find("    private void showOptions()")
options_end=s.find("    private String friendlyUnknownMode()",options_start)
if options_start<0 or options_end<0:raise SystemExit("Options section not found")
options=s[options_start:options_end]
anchor='        box.addView(importFormat,new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT,dp(52)));'
if options.count(anchor)!=1:raise SystemExit("Settings Configure Import Format anchor missing")
extra='''
        Button exportFormat=button("EDIT EXPORT TEMPLATE (NO BATCH NEEDED)",0);
        exportFormat.setTextSize(15);
        exportFormat.setOnClickListener(v->{
            Intent intent=new Intent(this,FormatConfigActivity.class);
            intent.putExtra(FormatConfigActivity.EXTRA_MODE,FormatConfigActivity.MODE_EXPORT);
            intent.putExtra("template_setup_only",true);
            startActivity(intent);
        });
        box.addView(exportFormat,new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT,dp(56)));'''
options=options.replace(anchor,anchor+extra,1)
s=s[:options_start]+options+s[options_end:]
main.write_text(s)

fmt=root/"app/src/main/java/com/iceinventory/onhand/FormatConfigActivity.java"
f=fmt.read_text()
old_field='    private String mode;'
if f.count(old_field)!=1:raise SystemExit("FormatConfig mode field missing")
f=f.replace(old_field,old_field+'\n    private boolean templateSetupOnly;',1)
init='        mode=getIntent().getStringExtra(EXTRA_MODE);'
if f.count(init)!=1:raise SystemExit("FormatConfig mode initialization missing")
f=f.replace(init,init+'\n        templateSetupOnly=getIntent().getBooleanExtra("template_setup_only",false);',1)

old_save='"CONTINUE TO SAVE"'
new_save='(templateSetupOnly?"SAVE EXPORT TEMPLATE":"CONTINUE TO SAVE")'
if f.count(old_save)!=1:raise SystemExit("Export template button caption missing (found "+str(f.count(old_save))+")")
f=f.replace(old_save,new_save,1)
fmt.write_text(f)

checks={
    "version": "versionName '3.0.229'" in gradle.read_text() and "iCE Onhand 3.0.229" in manifest.read_text(),
    "home version": "Onhand Inventory 3.0.229" in main.read_text(),
    "one-line bottom import": 'Button imp=button("NEW / IMPORT",1);' in main.read_text() and "imp.setSingleLine(true)" in main.read_text(),
    "bottom import click unchanged": 'imp.setOnClickListener(' in main.read_text(),
    "no batch setup via settings": "EDIT EXPORT TEMPLATE (NO BATCH NEEDED)" in main.read_text() and 'intent.putExtra("template_setup_only",true)' in main.read_text(),
    "export mode": "FormatConfigActivity.MODE_EXPORT" in main.read_text(),
    "format saves": "private void saveCurrentOrder()" in fmt.read_text(),
    "independent save button": '"SAVE EXPORT TEMPLATE"' in fmt.read_text(),
    "workflow": ".github/prepare_30229.py" in workflow.read_text() and "3.0.229" in workflow.read_text(),
}
failed=[k for k,v in checks.items() if not v]
if failed:raise SystemExit("3.0.229 validation failed: "+", ".join(failed))
print("Prepared OnHand 3.0.229: aligned single-line NEW / IMPORT footer and independent export-template editor under Settings.")
