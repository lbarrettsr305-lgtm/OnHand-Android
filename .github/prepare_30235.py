#!/usr/bin/env python3
"""3.0.235: allow a scanned/typed MAIN counting location without an exact side."""
from pathlib import Path
import runpy

root=Path(__file__).resolve().parents[1]
workflow=root/".github/workflows/build-apk.yml"
w=workflow.read_text()
markers=[
    ("Prepare and verify 3.0.235 main-location-only counting","Prepare and verify 3.0.234 Fleet Feet headerless Barcode Qty customer report",1),
    (".github/prepare_30235.py",".github/prepare_30234.py",1),
    ("iCE-Onhand-Inventory-3.0.235","iCE-Onhand-Inventory-3.0.234",4),
]
for new,old,expected in markers:
    if w.count(new)!=expected:raise SystemExit("3.0.235 workflow marker wrong: "+new+" = "+str(w.count(new)))
    w=w.replace(new,old)
workflow.write_text(w)
runpy.run_path(str(root/".github/prepare_30234.py"),run_name="__main__")
w=workflow.read_text()
for new,old,expected in markers:
    if w.count(old)!=expected:raise SystemExit("3.0.234 workflow restore marker wrong: "+old)
    w=w.replace(old,new)
workflow.write_text(w)

gradle=root/"app/build.gradle"
g=gradle.read_text()
if g.count("versionCode 30234")!=1 or g.count("versionName '3.0.234'")!=1:
    raise SystemExit("3.0.234 Gradle version missing")
gradle.write_text(g.replace("versionCode 30234","versionCode 30235",1).replace("versionName '3.0.234'","versionName '3.0.235'",1))
manifest=root/"app/src/main/AndroidManifest.xml"
m=manifest.read_text()
if m.count("iCE Onhand 3.0.234")!=1:raise SystemExit("3.0.234 manifest version missing")
manifest.write_text(m.replace("iCE Onhand 3.0.234","iCE Onhand 3.0.235",1))

main=root/"app/src/main/java/com/iceinventory/onhand/MainActivity.java"
s=main.read_text()
def once(old,new,label):
    global s
    hits=s.count(old)
    if hits!=1:raise SystemExit("3.0.235 "+label+" unexpected source matches: "+str(hits))
    s=s.replace(old,new,1)

once("Onhand Inventory 3.0.234","Onhand Inventory 3.0.235","visible version")

# The existing dispatchKeyEvent routes Bluetooth scanner keys to locationScanInput.
# Add separate main-only focus target, without interfering with exact-location scans.
once("    private EditText locationScanInput;\n",
     "    private EditText locationScanInput;\n    private EditText mainOnlyLocationInput;\n",
     "location scanner state")

# Canonical main parents from existing location names and legacy scanned label codes.
# The aisle number is preserved; the side is deliberately dropped ONLY by the
# explicit main-only action. Exact locations continue through the old submit path.
helpers=r'''    private String normalizeMainLocation(String raw) {
        String value=raw==null?"":raw.trim();
        if(value.isEmpty()||value.matches("(?i)^Aisle\\s*$"))return "";
        if(value.matches("\\d+")){
            String found=null;
            for(String name:db.locations()){
                if(name.endsWith("-"+value)){
                    if(found!=null&&!found.equalsIgnoreCase(name))return "";
                    found=name;
                }
            }
            if(found!=null)value=found;
        }
        java.util.regex.Matcher aisle=java.util.regex.Pattern.compile("(?i)^Aisle\\s*(\\d+).*").matcher(value);
        if(aisle.matches())return "Aisle "+aisle.group(1);
        if(value.equalsIgnoreCase("Cooler Doors"))return "Cooler Doors";
        if(value.equalsIgnoreCase("Cigarette Shelves"))return "Cigarette Shelves";
        String[] grouped=storeMapLocation(value);
        return grouped[0].isEmpty()?value:grouped[0];
    }

    private boolean isMainOnlyLocation(String location){
        return location!=null&&!location.isEmpty()&&location.equalsIgnoreCase(normalizeMainLocation(location));
    }

    private void submitMainOnlyLocation(String scannedOrTyped){
        String main=normalizeMainLocation(scannedOrTyped);
        if(main.isEmpty()){
            toast("Enter or scan a MAIN location. Include the aisle number (for example Aisle 1). If a label code is ambiguous, type the location name.");
            return;
        }
        submitCountingLocation(main);
    }

'''
once("    private String locationParent(String name){",
     helpers+"    private String locationParent(String name){",
     "main-only normalization helpers")

# Make the dialog scroll rather than truncating extra controls on older phones.
once('        panel.addView(instructions);\n',
     '''        panel.addView(instructions);
        TextView mainHeading=text("MAIN LOCATION ONLY — SCAN OR TYPE",16,gold(),true);
        panel.addView(mainHeading);
        EditText mainOnlyInput=new EditText(this);
        mainOnlyInput.setSingleLine(true);
        mainOnlyInput.setHint("Example: Aisle 1, Backroom, Checkout");
        mainOnlyInput.setTextColor(Color.WHITE);
        mainOnlyInput.setHintTextColor(Color.LTGRAY);
        panel.addView(mainOnlyInput,new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT,dp(55)));
        mainOnlyLocationInput=mainOnlyInput;
        mainOnlyInput.setOnFocusChangeListener((v,focused)->{if(focused)locationScanInput=mainOnlyInput;});
        mainOnlyInput.setOnEditorActionListener((v,action,event)->{
            if((event!=null&&(event.getKeyCode()==KeyEvent.KEYCODE_ENTER||event.getKeyCode()==KeyEvent.KEYCODE_NUMPAD_ENTER))||action==6||action==5){
                submitMainOnlyLocation(mainOnlyInput.getText().toString());return true;
            }
            return false;
        });
        Button scanMain=button("SCAN MAIN LOCATION LABEL",1);
        scanMain.setOnClickListener(v->{
            locationScanInput=mainOnlyInput;
            pendingLocationScanEntry=mainOnlyInput;
            startActivityForResult(new Intent(this,ScanActivity.class),REQ_SCAN_LOCATION);
        });
        panel.addView(scanMain,new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT,dp(48)));
        Button useMain=button("USE MAIN LOCATION ONLY — START COUNTING",1);
        useMain.setOnClickListener(v->submitMainOnlyLocation(mainOnlyInput.getText().toString()));
        panel.addView(useMain,new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT,dp(56)));
        TextView exactHeading=text("OR SELECT AN EXACT SIDE / SUBLOCATION BELOW",15,Color.WHITE,true);
        exactHeading.setPadding(0,dp(8),0,dp(5));
        panel.addView(exactHeading);
''',
     "main-only field and action")

# External scanners now default to the main location field; choosing the exact
# field restores exact input, and the current exact-location button still works.
once("        locationScanInput=entry;\n",
     '''        locationScanInput=mainOnlyInput;
        entry.setOnFocusChangeListener((v,focused)->{if(focused)locationScanInput=entry;});
''',
     "external scanner main target")
once("                submitCountingLocation(locationScanInput.getText().toString());return true;",
     "                if(locationScanInput==mainOnlyLocationInput)submitMainOnlyLocation(locationScanInput.getText().toString());\n                else submitCountingLocation(locationScanInput.getText().toString());\n                return true;",
     "external scanner Enter/Tab completion")
once('            .setView(panel).setPositiveButton("USE THIS LOCATION",null)',
     '            .setView(new ScrollView(this){{addView(panel);}}).setPositiveButton("USE THIS LOCATION",null)',
     "small-screen dialog scrolling")

# A scan into the main field should never be processed as a product barcode.
# Existing camera callback fills pendingLocationScanEntry and leaves the user
# a clear one-tap main-only confirmation.
# The exact scanner path stays available in the second half of the picker.

# Store map: a main-only count is its OWN subsection and rolls into the main
# subtotal exactly once. The exact-side rows remain untouched.
once('return new String[]{parent,part.isEmpty()?"All":part};',
     'return new String[]{parent,part.isEmpty()?"Main (no exact side)":part};',
     "parent-only section")
once('        if(value.startsWith("Cooler Door")){',
     '        if(value.equalsIgnoreCase("Cooler Doors"))return new String[]{"Cooler Doors","Main (no exact side)"};\n        if(value.startsWith("Cooler Door")){',
     "cooler main grouping")
once('            String[] pair=storeMapLocation(r.location);String parent=pair[0],part=pair[1],key=parent.toLowerCase(Locale.US);',
     '''            String[] pair=storeMapLocation(r.location);
            String parent=pair[0],part=pair[1].isEmpty()?"Main (no exact side)":pair[1],key=parent.toLowerCase(Locale.US);''',
     "map main-only subtotal")
once('confirmedLocation.toUpperCase(java.util.Locale.US):"NOT SET"));',
     '(isMainOnlyLocation(confirmedLocation)?"MAIN ONLY — ":"")+confirmedLocation.toUpperCase(java.util.Locale.US):"NOT SET"));',
     "current location banner")

# Clean up main scanner reference after dialog dismissal to avoid a stale view.
s=s.replace("locationDialog=null;locationScanInput=null;",
            "locationDialog=null;locationScanInput=null;mainOnlyLocationInput=null;")

main.write_text(s)

checks={
    "version": "versionName '3.0.235'" in gradle.read_text() and "iCE Onhand 3.0.235" in manifest.read_text() and "Onhand Inventory 3.0.235" in s,
    "main entry": 'USE MAIN LOCATION ONLY — START COUNTING' in s and 'SCAN MAIN LOCATION LABEL' in s,
    "physical scanner": 'if(locationScanInput==mainOnlyLocationInput)submitMainOnlyLocation' in s,
    "camera scanner": 'pendingLocationScanEntry=mainOnlyInput' in s,
    "exact remains": 'setPositiveButton("USE THIS LOCATION",null)' in s and 'submitCountingLocation(entry.getText().toString().trim())' in s,
    "post import remains": 'pendingImportedRows' in s and 'finishPendingImport(n)' in s,
    "location persistence": 'rememberConfirmedLocation(n)' in s,
    "main aisle canonical": 'return "Aisle "+aisle.group(1);' in s,
    "store map": 'part=pair[1].isEmpty()?"Main (no exact side)":pair[1]' in s,
    "Fleet Feet preserved": 'Fleet Feet Client — Barcode + Qty (No Headers)' in s,
    "Victoria preserved": 'Victoria' in s,
    "workflow": ".github/prepare_30235.py" in workflow.read_text() and "3.0.235" in workflow.read_text(),
}
failed=[k for k,v in checks.items() if not v]
if failed:raise SystemExit("3.0.235 checks failed: "+", ".join(failed))
print("Prepared iCE OnHand 3.0.235: main-only location scan/type, exact-side option, location retention and Store Map subtotal.")
