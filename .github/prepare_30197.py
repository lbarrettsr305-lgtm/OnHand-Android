#!/usr/bin/env python3
from pathlib import Path
import runpy

root = Path(__file__).resolve().parents[1]
runpy.run_path(str(root / ".github" / "prepare_30196.py"), run_name="__main__")

def replace(path, old, new, label):
    p = root / path
    s = p.read_text()
    if s.count(old) != 1:
        raise SystemExit(f"3.0.197 target missing or ambiguous: {label}")
    p.write_text(s.replace(old, new, 1))

gradle = root / "app" / "build.gradle"
s = gradle.read_text()
if "versionName '3.0.196'" not in s:
    raise SystemExit("3.0.196 version source not found")
gradle.write_text(s.replace("versionCode 30196", "versionCode 30197", 1).replace("versionName '3.0.196'", "versionName '3.0.197'", 1))

manifest = root / "app" / "src" / "main" / "AndroidManifest.xml"
s = manifest.read_text()
if "iCE Onhand 3.0.196" not in s:
    raise SystemExit("3.0.196 app label not found")
manifest.write_text(s.replace("iCE Onhand 3.0.196", "iCE Onhand 3.0.197", 1))

main_path = "app/src/main/java/com/iceinventory/onhand/MainActivity.java"
p = root / main_path
s = p.read_text().replace("Onhand Inventory 3.0.196", "Onhand Inventory 3.0.197", 1)

old = '''        cigaretteSummary=text("🚬 CIGARETTES QTY: 0",16,Color.BLACK,true);
        cigaretteSummary.setGravity(Gravity.CENTER);cigaretteSummary.setPadding(dp(5),dp(5),dp(5),dp(5));cigaretteSummary.setBackgroundColor(gold());
        root.addView(cigaretteSummary,new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT,dp(38)));'''
new = '''        cigaretteSummary=text("🚬 CIGARETTES QTY: 0",22,Color.WHITE,true);
        cigaretteSummary.setTypeface(Typeface.DEFAULT,Typeface.BOLD);
        cigaretteSummary.setGravity(Gravity.CENTER);cigaretteSummary.setPadding(dp(6),dp(7),dp(6),dp(7));cigaretteSummary.setBackgroundColor(green());
        root.addView(cigaretteSummary,new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT,dp(52)));'''
if s.count(old) != 1:
    raise SystemExit("3.0.197 target missing: cigarette total style")
s = s.replace(old, new, 1)

# Put a remembered tab-delimited inventory shortcut on the count screen.
field = '    private String pendingExportFileName="";'
if s.count(field) != 1:
    raise SystemExit("3.0.197 target missing: resume button field")
s = s.replace(field, field + '\n    private Button tabDelimitedResumeButton;', 1)

anchor = '        root.addView(sessionBar);'
resume_ui = '''        root.addView(sessionBar);
        tabDelimitedResumeButton=button("↩ RESUME INVENTORY",1);
        tabDelimitedResumeButton.setTypeface(Typeface.DEFAULT,Typeface.BOLD);
        tabDelimitedResumeButton.setTextSize(17);
        tabDelimitedResumeButton.setVisibility(prefs().getBoolean("tab_delimited_resume_active",false)?View.VISIBLE:View.GONE);
        tabDelimitedResumeButton.setOnClickListener(v->resumeTabDelimitedInventory());
        LinearLayout.LayoutParams resumeLp=new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT,dp(52));
        resumeLp.setMargins(0,dp(5),0,dp(4));
        root.addView(tabDelimitedResumeButton,resumeLp);'''
if s.count(anchor) != 1:
    raise SystemExit("3.0.197 target missing: inventory resume placement")
s = s.replace(anchor, resume_ui, 1)

# On every successful tab-delimited import, remember which database inventory to reopen.
old = '''        toast((replaceCurrent?"Replaced current data • ":"Appended • ")+"Imported "+imported+" tab-delimited TXT rows");
        if(replaceCurrent)offerMasterCandidateActivation();'''
new = '''        toast((replaceCurrent?"Replaced current data • ":"Appended • ")+"Imported "+imported+" tab-delimited TXT rows");
        prefs().edit().putBoolean("tab_delimited_resume_active",true).putLong("tab_delimited_resume_session_id",sessionId).putString("tab_delimited_resume_session_name",sessionName).apply();
        if(tabDelimitedResumeButton!=null)tabDelimitedResumeButton.setVisibility(View.VISIBLE);
        if(replaceCurrent)offerMasterCandidateActivation();
        if(replaceCurrent)showImportNextSteps(imported);'''
if s.count(old) != 1:
    raise SystemExit("3.0.197 target missing: successful import follow-up")
s = s.replace(old, new, 1)

method_anchor = '    private void importCsv() {'
methods = '''    private void resumeTabDelimitedInventory() {
        long savedId=prefs().getLong("tab_delimited_resume_session_id",-1L);
        for(InventoryDb.Session saved:db.sessions()) {
            if(saved.id==savedId) {
                sessionId=saved.id;
                sessionName=saved.name;
                lastBarcode="";
                refreshLocations();
                refreshList();
                focusBarcodeWithoutKeyboard();
                toast("Resumed "+sessionName);
                return;
            }
        }
        toast("The saved inventory is no longer available. Choose it from Inventories.");
    }

    private void showImportNextSteps(int imported) {
        new AlertDialog.Builder(this)
            .setTitle("Inventory Ready")
            .setMessage("Replaced the current inventory and imported "+imported+" rows.\\n\\nBefore counting:\\n1. Confirm the inventory name at the top.\\n2. Open Options and check Unknown Barcode Behavior.\\n3. Choose the current location.\\n4. Test one barcode with your Bluetooth scanner and confirm the item before counting.")
            .setPositiveButton("START COUNTING",(d,w)->focusBarcodeWithoutKeyboard())
            .setNegativeButton("OK",null)
            .show();
    }

'''
if s.count(method_anchor) != 1:
    raise SystemExit("3.0.197 target missing: import helpers placement")
s = s.replace(method_anchor, methods + method_anchor, 1)

# The scan behavior is the first setting to check: move it above Inventory and style it as a clear green control.
lines = s.splitlines(keepends=True)
start = [i for i,line in enumerate(lines) if 'Button unknown=button(' in line]
if len(start) != 1:
    raise SystemExit("3.0.197 target missing or ambiguous: Unknown Barcode Behavior control")
a = start[0]
end = None
for i in range(a, len(lines)):
    if 'box.addView(unknown,' in lines[i]:
        end = i + 1
        if end < len(lines) and 'View optionsBottomSpacer' in lines[end]:
            end += 1
            if end < len(lines) and 'box.addView(optionsBottomSpacer' in lines[end]:
                end += 1
        break
if end is None:
    raise SystemExit("3.0.197 target missing: Unknown Barcode Behavior layout end")
del lines[a:end]
insert = [i for i,line in enumerate(lines) if 'TextView inventory=text("Inventory"' in line]
if len(insert) != 1:
    raise SystemExit("3.0.197 target missing or ambiguous: Options Inventory section")
i = insert[0]
green_unknown = '''        Button unknown=button("Unknown Barcode Behavior\\\\nCurrent: "+friendlyUnknownMode(),1);
        unknown.setTypeface(Typeface.DEFAULT,Typeface.BOLD);
        unknown.setTextSize(18);
        unknown.setSingleLine(false);
        unknown.setMaxLines(2);
        unknown.setGravity(Gravity.CENTER);
        unknown.setOnClickListener(v->showUnknownBarcodeMode());
        box.addView(unknown,new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT,dp(72)));
'''
lines[i:i] = [green_unknown]
s = "".join(lines)
p.write_text(s)

# Make every item quantity badge larger, bold, green, and high contrast.
adapter_path = "app/src/main/java/com/iceinventory/onhand/InventoryAdapter.java"
replace(adapter_path,
    'TextView q=text("QTY: "+QuantityMath.format(r.quantity),compact?15:18,Color.BLACK,true);',
    'TextView q=text("QTY: "+QuantityMath.format(r.quantity),compact?19:22,Color.WHITE,true);',
    "item quantity size and color")
replace(adapter_path,
    'quantityBadge.setColor(Color.rgb(255,215,0));',
    'quantityBadge.setColor(Color.rgb(0,180,45));',
    "item quantity green badge")

main = p.read_text()
adapter = (root / adapter_path).read_text()
checks = {
    "version": "versionName '3.0.197'" in gradle.read_text(),
    "green cigarette quantity": 'cigaretteSummary.setBackgroundColor(green())' in main and 'text("🚬 CIGARETTES QTY: 0",22,Color.WHITE,true)' in main,
    "tab-delimited resume": 'tab_delimited_resume_session_id' in main and 'RESUME INVENTORY' in main,
    "replace guidance": 'Before counting:' in main and 'Bluetooth scanner' in main,
    "unknown setting first": main.index('Button unknown=button("Unknown Barcode Behavior') < main.index('TextView inventory=text("Inventory"'),
    "green bold unknown setting": 'Button unknown=button("Unknown Barcode Behavior\\\\nCurrent: "+friendlyUnknownMode(),1);' in main and 'unknown.setTextSize(18);' in main,
    "green large item quantities": "compact?19:22,Color.WHITE,true" in adapter and "quantityBadge.setColor(Color.rgb(0,180,45))" in adapter,
}
failed = [name for name,ok in checks.items() if not ok]
if failed:
    raise SystemExit("3.0.197 verification failed: " + ", ".join(failed))
print("Prepared iCE Onhand 3.0.197: tab-delimited resume, import next steps, and prominent green scan/quantity controls")
