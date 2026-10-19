#!/usr/bin/env python3
"""OnHand 3.0.237: Walls / Aisles 01-10 and expandable six-slot warehouse Bays."""
from pathlib import Path
import runpy

root=Path(__file__).resolve().parents[1]
workflow=root/".github/workflows/build-apk.yml"
w=workflow.read_text()
markers=[
    ("Prepare and verify 3.0.237 wall aisle and warehouse bay locations",
     "Prepare and verify 3.0.236 Bluetooth location scanning and readable buttons",1),
    (".github/prepare_30237.py",".github/prepare_30236.py",1),
    ("iCE-Onhand-Inventory-3.0.237","iCE-Onhand-Inventory-3.0.236",4),
]
for new,old,expected in markers:
    if w.count(new)!=expected:raise SystemExit("3.0.237 workflow marker missing "+new)
    w=w.replace(new,old)
workflow.write_text(w)
runpy.run_path(str(root/".github/prepare_30236.py"),run_name="__main__")
w=workflow.read_text()
for new,old,expected in markers:
    if w.count(old)!=expected:raise SystemExit("3.0.236 workflow restore missing "+old)
    w=w.replace(old,new)
workflow.write_text(w)

gpath=root/"app/build.gradle"
g=gpath.read_text()
assert g.count("versionCode 30236")==1 and g.count("versionName '3.0.236'")==1
gpath.write_text(g.replace("versionCode 30236","versionCode 30237",1)
                 .replace("versionName '3.0.236'","versionName '3.0.237'",1))
mpath=root/"app/src/main/AndroidManifest.xml"
m=mpath.read_text()
assert m.count("iCE Onhand 3.0.236")==1
mpath.write_text(m.replace("iCE Onhand 3.0.236","iCE Onhand 3.0.237",1))

def replace_once(content,old,new,label):
    hits=content.count(old)
    if hits!=1:raise SystemExit("3.0.237 "+label+" unexpected matches: "+str(hits))
    return content.replace(old,new,1)

dbpath=root/"app/src/main/java/com/iceinventory/onhand/InventoryDb.java"
db=dbpath.read_text()
# Defaults are insert-with-conflict-ignore, so adding these never deletes counts or
# changes a user's previous inventory. No arbitrary number of warehouse bays is assumed.
db=replace_once(db,"        Collections.addAll(frequentLocations,exactLocations);",
'''        Collections.addAll(frequentLocations,exactLocations);
        // Independent main locations: keep existing original legacy Aisle/Wall names.
        String[] walls={"Front-Wall","Left-Wall","Right-Wall","Back-Wall"};
        Collections.addAll(frequentLocations,walls);
        for(int numberedAisle=1;numberedAisle<=10;numberedAisle++){
            frequentLocations.add(String.format(java.util.Locale.US,"Aisle-%02d",numberedAisle));
        }''',"new independent wall/aisle defaults")
dbpath.write_text(db)

mainpath=root/"app/src/main/java/com/iceinventory/onhand/MainActivity.java"
s=mainpath.read_text()
s=replace_once(s,"Onhand Inventory 3.0.236","Onhand Inventory 3.0.237","version")

s=replace_once(s,'    private String locationParent(String name){',
r'''    private String locationParent(String name){''',"location parent presence")  # anchor existence
s=replace_once(s,'        String n=name==null?"":name.trim();\n        if(n.matches("(?i)^Aisle\\\\d+.*"))return "Aisle";',
r'''        String n=name==null?"":name.trim();
        java.util.regex.Matcher bayParent=java.util.regex.Pattern.compile("(?i)^(Bay-\\d{2,3})-T[1-3]-P[1-2]$").matcher(n);
        if(bayParent.matches())return bayParent.group(1);
        if(n.matches("(?i)^Bay-\\d{2,3}$"))return n;
        if(n.matches("(?i)^(Front|Left|Right|Back)-Wall$"))return n;
        if(n.matches("(?i)^Aisle-(0[1-9]|10)$"))return n;
        if(n.matches("(?i)^Aisle\\d+.*"))return "Aisle";''',"warehouse and new standalone location picker groups")

s=replace_once(s,
'''        String value=full==null||full.trim().isEmpty()?"Main":full.trim();
        String[] legacy=value.split("\\\\s*>\\\\s*",2);''',
r'''        String value=full==null||full.trim().isEmpty()?"Main":full.trim();
        // Each Bay is a separate card; its 6 distinct tier/pallet slots are shown
        // individually, with the exact-sum Bay and inventory grand totals.
        java.util.regex.Matcher baySlot=java.util.regex.Pattern.compile("(?i)^(Bay-\\d{2,3})-T([1-3])-P([1-2])$").matcher(value);
        if(baySlot.matches())
            return new String[]{baySlot.group(1),"Tier "+baySlot.group(2)+" / Pallet "+baySlot.group(3)};
        if(value.matches("(?i)^Bay-\\d{2,3}$"))return new String[]{value,"Main (no exact spot)"};
        if(value.matches("(?i)^(Front|Left|Right|Back)-Wall$"))return new String[]{value,""};
        if(value.matches("(?i)^Aisle-(0[1-9]|10)$"))return new String[]{value,""};
        String[] legacy=value.split("\\s*>\\s*",2);''',
"warehouse map sections and standalone wall/aisle")

s=replace_once(s,
'''    private void submitMainOnlyLocation(String scannedOrTyped){
        String main=normalizeMainLocation(scannedOrTyped);''',
r'''    private void submitMainOnlyLocation(String scannedOrTyped){
        // Hardware scanner starts on the MAIN input. If a pallet-slot label is
        // scanned there, retain its exact Tier and Pallet rather than dropping it.
        String scanned=scannedOrTyped==null?"":scannedOrTyped.trim();
        java.util.regex.Matcher slot=java.util.regex.Pattern.compile("(?i)^Bay-(\\d{1,3})-T([1-3])-P([1-2])$").matcher(scanned);
        if(slot.matches()){
            String exact=String.format(java.util.Locale.US,"Bay-%02d-T%s-P%s",
                Integer.parseInt(slot.group(1)),slot.group(2),slot.group(3));
            submitCountingLocation(exact);
            return;
        }
        String main=normalizeMainLocation(scannedOrTyped);''',
"avoid destroying exact Bay slot on main-only scanner")

# Provide an in-app expandable Bay setup: 1..999, user controls which bays exist.
# Six unique scannable tags are created per Bay; repeat is harmless/duplicate-safe.
helpers=r'''    private String warehouseSlotName(int bay,int tier,int pallet){
        return String.format(java.util.Locale.US,"Bay-%02d-T%d-P%d",bay,tier,pallet);
    }

    private void addWarehouseBayRange(int first,int last){
        for(int bay=first;bay<=last;bay++)
            for(int tier=1;tier<=3;tier++)
                for(int pallet=1;pallet<=2;pallet++)
                    db.addLocation(warehouseSlotName(bay,tier,pallet));
    }

    private void showWarehouseBaySetup(){
        LinearLayout fields=new LinearLayout(this);
        fields.setOrientation(LinearLayout.VERTICAL);
        fields.setPadding(dp(14),dp(8),dp(14),dp(4));
        fields.addView(text("Create 6 unique locations per bay: 3 tiers x 2 pallet spots.\nExample: Bay-01-T1-P1 through Bay-01-T3-P2.\nEach tag can be scanned with your Bluetooth scanner.",15,Color.WHITE,false));
        fields.addView(text("FIRST BAY NUMBER",14,gold(),true));
        EditText first=new EditText(this);
        first.setSingleLine(true);
        first.setInputType(android.text.InputType.TYPE_CLASS_NUMBER);
        first.setText("1");
        first.setTextColor(Color.WHITE);
        fields.addView(first);
        fields.addView(text("LAST BAY NUMBER",14,gold(),true));
        EditText last=new EditText(this);
        last.setSingleLine(true);
        last.setInputType(android.text.InputType.TYPE_CLASS_NUMBER);
        last.setText("1");
        last.setTextColor(Color.WHITE);
        fields.addView(last);
        AlertDialog addDialog=new AlertDialog.Builder(this)
            .setTitle("SET UP WAREHOUSE BAYS")
            .setView(fields)
            .setPositiveButton("ADD BAY LOCATIONS",null)
            .setNegativeButton("CANCEL",null).create();
        addDialog.setOnShowListener(d->addDialog.getButton(AlertDialog.BUTTON_POSITIVE).setOnClickListener(v->{
            int start,end;
            try{
                start=Integer.parseInt(first.getText().toString().trim());
                end=Integer.parseInt(last.getText().toString().trim());
            }catch(Exception ex){toast("Enter both bay numbers (for example 1 and 10).");return;}
            if(start<1||end<start||end>999||end-start>=100){
                toast("Use bays 1-999, in order, up to 100 bays at a time.");return;
            }
            addWarehouseBayRange(start,end);
            addDialog.dismiss();
            if(locationDialog!=null)locationDialog.dismiss();
            locationDialog=null;locationScanInput=null;mainOnlyLocationInput=null;
            toast("Bays "+start+"–"+end+": "+((end-start+1)*6)+" pallet locations ready. Repeating setup never duplicates them.");
            showLocationStep();
        }));
        addDialog.show();
    }

'''
s=replace_once(s,"    private String normalizeMainLocation(String raw) {",
               helpers+"    private String normalizeMainLocation(String raw) {",
               "dynamic warehouse setup helpers")

s=replace_once(s,
'''        panel.addView(exactHeading);

        List<String> names=db.locations();''',
'''        panel.addView(exactHeading);
        Button setupBays=button("ADD / SET UP WAREHOUSE BAYS",1);
        setupBays.setTextSize(14);
        setupBays.setOnClickListener(v->showWarehouseBaySetup());
        panel.addView(setupBays,new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT,dp(59)));

        List<String> names=db.locations();''',
"warehouse action on location picker")

# Explicitly allow a bare Bay main location when requested. An exact scanned
# Bay slot never loses its tier/position, as handled above.
s=replace_once(s,
'''        if(value.equalsIgnoreCase("Cooler Doors"))return "Cooler Doors";''',
'''        if(value.matches("(?i)^Bay-\\\\d{2,3}$"))return value;
        if(value.equalsIgnoreCase("Cooler Doors"))return "Cooler Doors";''',
"main Bay normalization")

mainpath.write_text(s)
checks={
 "version":"versionName '3.0.237'" in gpath.read_text() and "iCE Onhand 3.0.237" in mpath.read_text() and "Onhand Inventory 3.0.237" in s,
 "4 walls":all(x in db for x in ["Front-Wall","Left-Wall","Right-Wall","Back-Wall"]),
 "10 aisles":'numberedAisle<=10' in db and 'Aisle-%02d' in db,
 "six slots":'tier<=3' in s and 'pallet<=2' in s and 'warehouseSlotName' in s,
 "configurable range":'showWarehouseBaySetup()' in s and 'ADD / SET UP WAREHOUSE BAYS' in s,
 "slot preserved":'submitCountingLocation(exact);' in s,
 "map totals":'Tier "+baySlot.group(2)+" / Pallet "' in s,
 "legacy preserved":'Aisle\\\\d+.*' in s and "Collections.addAll(frequentLocations,exactLocations);" in db,
 "bluetooth kept":'BLUETOOTH SCANNER — MAIN LOCATION' in s,
 "templates kept":'Fleet Feet Client — Barcode + Qty (No Headers)' in s and 'Victoria' in s and 'Petrosoft' in s,
 "workflow":".github/prepare_30237.py" in workflow.read_text()
}
bad=[k for k,v in checks.items() if not v]
if bad:raise SystemExit("3.0.237 verification failed: "+", ".join(bad))
print("Prepared OnHand 3.0.237: four walls, ten standalone aisles, user-configured warehouse Bays with six exact pallet tags each.")
