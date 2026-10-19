#!/usr/bin/env python3
"""OnHand 3.0.238: Victoria Coffee location template and tappable, quantified zone-map."""
from pathlib import Path
import runpy

root=Path(__file__).resolve().parents[1]
workflow=root/".github/workflows/build-apk.yml"
w=workflow.read_text()
markers=[
 ("Prepare and verify 3.0.238 Victoria Coffee locations and floor plan",
  "Prepare and verify 3.0.237 wall aisle and warehouse bay locations",1),
 (".github/prepare_30238.py",".github/prepare_30237.py",1),
 ("iCE-Onhand-Inventory-3.0.238","iCE-Onhand-Inventory-3.0.237",4),
]
for new,old,expected in markers:
    if w.count(new)!=expected:raise SystemExit("3.0.238 workflow anchor mismatch "+new)
    w=w.replace(new,old)
workflow.write_text(w)
runpy.run_path(str(root/".github/prepare_30237.py"),run_name="__main__")
w=workflow.read_text()
for new,old,expected in markers:
    if w.count(old)!=expected:raise SystemExit("3.0.237 workflow restore mismatch "+old)
    w=w.replace(old,new)
workflow.write_text(w)

gradle=root/"app/build.gradle"
g=gradle.read_text()
if g.count("versionCode 30237")!=1 or g.count("versionName '3.0.237'")!=1:raise SystemExit("Gradle version missing")
gradle.write_text(g.replace("versionCode 30237","versionCode 30238",1).replace("versionName '3.0.237'","versionName '3.0.238'",1))
manifest=root/"app/src/main/AndroidManifest.xml"
m=manifest.read_text()
if m.count("iCE Onhand 3.0.237")!=1:raise SystemExit("manifest version missing")
manifest.write_text(m.replace("iCE Onhand 3.0.237","iCE Onhand 3.0.238",1))

path=root/"app/src/main/java/com/iceinventory/onhand/MainActivity.java"
s=path.read_text()
def once(old,new,label):
    global s
    hits=s.count(old)
    if hits!=1:raise SystemExit("3.0.238 "+label+" expected one target; found "+str(hits))
    s=s.replace(old,new,1)
once("Onhand Inventory 3.0.237","Onhand Inventory 3.0.238","app version")

# All new preset names are scoped to Victoria Coffee projects. The existing
# shared location table is untouched: no destructive migration, no inventory
# clearing, and other clients never auto-create the Victoria-specific sites.
methods=r'''    private boolean isVictoriaCoffeeInventory(){
        return sessionName!=null&&sessionName.toLowerCase(java.util.Locale.US).contains("victoria");
    }

    private java.util.ArrayList<String> victoriaSpecialLocations(){
        java.util.ArrayList<String> names=new java.util.ArrayList<>();
        // Overhead mapped inventory locations: distinguish the 4-item map from
        // the 6-item map by keeping every exact overhead barcode unique.
        names.add("Overhead");
        for(int index=1;index<=10;index++)
            names.add(String.format(java.util.Locale.US,"Overhead-%02d",index));

        java.util.Collections.addAll(names,
            "Under-Stair","Under-Stair-Left","Under-Stair-Center","Under-Stair-Right",
            "Under-Stair-Pallet-01","Under-Stair-Pallet-02","Under-Stair-Shelf",
            "Supply-Shelves","Supply-Shelves-White","Supply-Shelves-Metal-01",
            "Supply-Shelves-Metal-02","Supply-Shelves-Top","Supply-Shelves-Bottom",
            "Utility-Area","Utility-Fridge","Utility-Table","Utility-Boxes","Utility-Floor",
            "Floor-Pallets","Equipment-Rack","Equipment-Rack-Bottom",
            "Equipment-Rack-Middle","Equipment-Rack-Top","Equipment-Rack-Front",
            "Equipment-Rack-Side","Equipment-Staging",
            "Equipment-Staging-Cart-01","Equipment-Staging-Cart-02",
            "Equipment-Staging-Floor-01","Equipment-Staging-Floor-02",
            "Showroom","Showroom-Front","Showroom-Back","Showroom-Left",
            "Showroom-Right","Showroom-Center",
            "Display-Shelves","Display-Shelves-Left","Display-Shelves-Center",
            "Display-Shelves-Right","Display-Shelves-Top","Display-Shelves-Bottom",
            "Demo-Floor","Demo-Floor-01","Demo-Floor-02",
            "Demo-Floor-03","Demo-Floor-04","Demo-Floor-05");
        for(int n=1;n<=5;n++)
            names.add(String.format(java.util.Locale.US,"Floor-Pallet-%02d",n));
        return names;
    }

    private boolean isVictoriaSpecialLocation(String name){
        if(name==null)return false;
        for(String preset:victoriaSpecialLocations())
            if(preset.equalsIgnoreCase(name.trim()))return true;
        return false;
    }

    private void ensureVictoriaCoffeeLocations(){
        if(!isVictoriaCoffeeInventory())return;
        // Idempotent; a location name is unique in DB, so upgrading or
        // revisiting a Victoria inventory cannot create duplicate tags.
        for(String name:victoriaSpecialLocations())db.addLocation(name);
        String[] walls={"Front-Wall","Left-Wall","Right-Wall","Back-Wall"};
        for(String wall:walls)db.addLocation(wall);
        for(int n=1;n<=10;n++)
            db.addLocation(String.format(java.util.Locale.US,"Aisle-%02d",n));
        // Rack Bays remain explicitly configurable via the existing Bay Setup
        // control, because the number of bays has not been verified in photos.
    }

    private String victoriaZone(String name){
        String loc=name==null?"":name.trim().toLowerCase(java.util.Locale.US);
        if(loc.startsWith("bay-"))return "RACK BAYS";
        if(loc.startsWith("aisle"))return "AISLES";
        if(loc.matches("^(front|left|right|back)-wall$")||loc.startsWith("walls"))return "WALLS";
        if(loc.startsWith("overhead")||loc.startsWith("over head"))return "OVERHEAD";
        if(loc.startsWith("under-stair"))return "UNDER STAIR";
        if(loc.startsWith("supply-shel"))return "SUPPLY SHELVES";
        if(loc.startsWith("utility-"))return "UTILITY";
        if(loc.startsWith("floor-pallet"))return "FLOOR PALLETS";
        if(loc.startsWith("equipment-rack"))return "EQUIPMENT RACK";
        if(loc.startsWith("equipment-staging"))return "STAGING";
        if(loc.startsWith("display-shelves"))return "DISPLAY SHELVES";
        if(loc.startsWith("demo-floor"))return "DEMO FLOOR";
        if(loc.startsWith("showroom"))return "SHOWROOM";
        return "OTHER / UNMAPPED";
    }

    private int victoriaZoneTotal(String zone){
        int sum=0;
        for(InventoryDb.Row item:db.items(sessionId))
            if(zone.equals(victoriaZone(item.location)))sum+=item.quantity;
        return sum;
    }

    private void showVictoriaZoneDetails(String zone){
        if(!isVictoriaCoffeeInventory())return;
        ScrollView scroller=new ScrollView(this);
        LinearLayout layout=new LinearLayout(this);
        layout.setOrientation(LinearLayout.VERTICAL);
        layout.setPadding(dp(12),dp(8),dp(12),dp(10));
        scroller.addView(layout);
        TextView info=text("ZONE QUANTITY: "+victoriaZoneTotal(zone)+
           "\nSelect the exact location to begin counting. Existing counts are retained.",15,gold(),true);
        info.setPadding(0,0,0,dp(8));
        layout.addView(info);
        java.util.LinkedHashMap<String,Integer> quantities=new java.util.LinkedHashMap<>();
        for(InventoryDb.Row item:db.items(sessionId)){
            String k=item.location==null?"Main":item.location.trim();
            quantities.put(k,quantities.getOrDefault(k,0)+item.quantity);
        }
        java.util.ArrayList<String> locations=new java.util.ArrayList<>();
        for(String name:db.locations())
            if(zone.equals(victoriaZone(name)))locations.add(name);
        for(String name:quantities.keySet())
            if(zone.equals(victoriaZone(name))&&!locations.contains(name))locations.add(name);
        if(locations.isEmpty()){
            TextView empty=text("No configured locations in this area yet. Add bays using Set Up Warehouse Bays.",14,Color.WHITE,false);
            layout.addView(empty);
        }
        final AlertDialog[] popup=new AlertDialog[1];
        for(String loc:locations){
            int quantity=quantities.getOrDefault(loc,0);
            Button pick=button(loc+"\nQTY "+quantity+"   •   SELECT LOCATION",1);
            pick.setSingleLine(false);pick.setMaxLines(2);
            pick.setTextSize(13);pick.setGravity(android.view.Gravity.CENTER);
            LinearLayout.LayoutParams lp=new LinearLayout.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT,dp(64));
            lp.setMargins(0,0,0,dp(5));layout.addView(pick,lp);
            pick.setOnClickListener(v->{
                if(popup[0]!=null)popup[0].dismiss();
                submitCountingLocation(loc);
            });
        }
        popup[0]=new AlertDialog.Builder(this)
            .setTitle(zone+" • VICTORIA COFFEE")
            .setView(scroller).setNegativeButton("BACK",null).create();
        popup[0].show();
    }

    private void showVictoriaFloorPlan(){
        if(!isVictoriaCoffeeInventory()){toast("Victoria Coffee inventory only");return;}
        ensureVictoriaCoffeeLocations();
        ScrollView scroll=new ScrollView(this);
        LinearLayout map=new LinearLayout(this);
        map.setOrientation(LinearLayout.VERTICAL);
        map.setPadding(dp(10),dp(10),dp(10),dp(12));
        scroll.addView(map);
        int grand=0;for(InventoryDb.Row item:db.items(sessionId))grand+=item.quantity;
        TextView banner=text("VICTORIA COFFEE\nWAREHOUSE & SHOWROOM LOCATION MAP",18,gold(),true);
        banner.setGravity(Gravity.CENTER);banner.setPadding(0,dp(6),0,dp(6));map.addView(banner);
        TextView accuracy=text("SCHEMATIC / NOT TO SCALE — verify physical positions before attaching rack labels.",13,Color.WHITE,false);
        accuracy.setGravity(Gravity.CENTER);map.addView(accuracy);
        TextView total=text("ALL LOCATIONS • GRAND QTY "+grand,19,gold(),true);
        total.setGravity(Gravity.CENTER);total.setPadding(0,dp(10),0,dp(10));map.addView(total);

        String[][] blocks={
            {"WAREHOUSE — STRUCTURE","WALLS","AISLES","RACK BAYS","OVERHEAD"},
            {"WAREHOUSE — LOOSE STOCK","FLOOR PALLETS","UNDER STAIR","SUPPLY SHELVES","UTILITY"},
            {"WAREHOUSE — EQUIPMENT","EQUIPMENT RACK","STAGING"},
            {"SHOWROOM / OFFICE","SHOWROOM","DISPLAY SHELVES","DEMO FLOOR"},
            {"RECONCILIATION","OTHER / UNMAPPED"}
        };
        for(String[] group:blocks){
            TextView heading=text(group[0],15,gold(),true);
            heading.setPadding(0,dp(8),0,dp(6));
            map.addView(heading);
            for(int i=1;i<group.length;i+=2){
                LinearLayout row=new LinearLayout(this);
                row.setOrientation(LinearLayout.HORIZONTAL);
                for(int j=i;j<Math.min(i+2,group.length);j++){
                    final String zone=group[j];
                    Button tile=button(zone+"\nQTY "+victoriaZoneTotal(zone),1);
                    tile.setTextSize(13);tile.setSingleLine(false);tile.setMaxLines(3);
                    tile.setGravity(Gravity.CENTER);
                    LinearLayout.LayoutParams lp=new LinearLayout.LayoutParams(0,dp(86),1f);
                    lp.setMargins(dp(2),dp(2),dp(2),dp(2));
                    row.addView(tile,lp);
                    tile.setOnClickListener(v->showVictoriaZoneDetails(zone));
                }
                if(group.length>2&&i+1>=group.length){
                    android.widget.Space placeholder=new android.widget.Space(this);
                    row.addView(placeholder,new LinearLayout.LayoutParams(0,dp(86),1f));
                }
                map.addView(row);
            }
        }
        new AlertDialog.Builder(this).setTitle("Victoria Coffee • Floor Plan")
            .setView(scroll).setPositiveButton("CLOSE",null).show();
    }

'''
once("    private String warehouseSlotName(int bay,int tier,int pallet){",methods+
    "    private String warehouseSlotName(int bay,int tier,int pallet){","Victoria scoped template/map helpers")

# Make sure location is initialized when entering the Victoria count; no new
# custom locations get created for Petrosoft, Fleet Feet or generic shops.
once('''        if(!requireCurrentCount())return;
        if(locationDialog!=null&&locationDialog.isShowing())return;
        LinearLayout panel=new LinearLayout(this);''',
'''        if(!requireCurrentCount())return;
        if(locationDialog!=null&&locationDialog.isShowing())return;
        ensureVictoriaCoffeeLocations();
        LinearLayout panel=new LinearLayout(this);''',
"Victoria location initialize")

# Use the existing hierarchical parent/child picker for Victoria's new places.
once('''        if(n.matches("(?i)^Aisle-(0[1-9]|10)$"))return n;''',
'''        if(n.matches("(?i)^Aisle-(0[1-9]|10)$"))return n;
        if(n.startsWith("Overhead"))return "Overhead";
        if(n.startsWith("Under-Stair"))return "Under-Stair";
        if(n.startsWith("Supply-Shelves"))return "Supply-Shelves";
        if(n.startsWith("Utility-"))return "Utility-Area";
        if(n.startsWith("Floor-Pallet"))return "Floor-Pallets";
        if(n.startsWith("Equipment-Rack"))return "Equipment-Rack";
        if(n.startsWith("Equipment-Staging"))return "Equipment-Staging";
        if(n.startsWith("Showroom"))return "Showroom";
        if(n.startsWith("Display-Shelves"))return "Display-Shelves";
        if(n.startsWith("Demo-Floor"))return "Demo-Floor";''',
"Victoria parent grouping")

# Give grouped reports readable exact sub-location labels and retain one-count
# per row regardless of parent, like the existing warehouse Bay totals.
once('''        if(value.matches("(?i)^Aisle-(0[1-9]|10)$"))return new String[]{value,""};''',
'''        if(value.matches("(?i)^Aisle-(0[1-9]|10)$"))return new String[]{value,""};
        String[] vcPrefixes={"Overhead","Under-Stair","Supply-Shelves","Utility-",
            "Floor-Pallet","Equipment-Rack","Equipment-Staging",
            "Showroom","Display-Shelves","Demo-Floor"};
        String[] vcParents={"Overhead","Under-Stair","Supply-Shelves","Utility-Area",
            "Floor-Pallets","Equipment-Rack","Equipment-Staging",
            "Showroom","Display-Shelves","Demo-Floor"};
        for(int index=0;index<vcPrefixes.length;index++){
            String prefix=vcPrefixes[index];
            if(value.equalsIgnoreCase(vcParents[index]))
                return new String[]{vcParents[index],"Main (no exact spot)"};
            if(value.startsWith(prefix)){
                String suffix=value.substring(prefix.length());
                while(suffix.startsWith("-"))suffix=suffix.substring(1);
                return new String[]{vcParents[index],suffix.isEmpty()?"Main (no exact spot)":suffix};
            }
        }''',
"Victoria Store Map grouped subtotals")

# A scanned special shelf/overhead barcode is already an exact location label.
# Do not transform Overhead-03 into Overhead, or Under-Stair-Left into Under.
once('''        String scanned=scannedOrTyped==null?"":scannedOrTyped.trim();
        java.util.regex.Matcher slot=''', 
'''        String scanned=scannedOrTyped==null?"":scannedOrTyped.trim();
        if(isVictoriaCoffeeInventory()&&isVictoriaSpecialLocation(scanned)){
            submitCountingLocation(scanned);return;
        }
        java.util.regex.Matcher slot=''',
"exact Victoria scanner tags")

# Scope map and Victoria templates to Victoria Coffee even though the older
# versions store their global names in a shared location lookup table.
once('''        List<String> names=db.locations();
        LinkedHashMap<String,ArrayList<String>> grouped=new LinkedHashMap<>();''',
'''        List<String> names=db.locations();
        if(!isVictoriaCoffeeInventory())
            names.removeIf(this::isVictoriaSpecialLocation);
        LinkedHashMap<String,ArrayList<String>> grouped=new LinkedHashMap<>();''',
"only display Victoria specialty names in Victoria")

once('''        panel.addView(setupBays,new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT,dp(59)));

        List<String> names=db.locations();''',
'''        panel.addView(setupBays,new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT,dp(59)));
        if(isVictoriaCoffeeInventory()){
            Button visualMap=button("VICTORIA COFFEE — VISUAL FLOOR PLAN",2);
            visualMap.setTextSize(14);
            visualMap.setOnClickListener(v->showVictoriaFloorPlan());
            panel.addView(visualMap,new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT,dp(60)));
        }

        List<String> names=db.locations();''',
"Victoria-only visual map entrypoint")

path.write_text(s)

checks={
 "version": "versionName '3.0.238'" in gradle.read_text() and "iCE Onhand 3.0.238" in manifest.read_text() and "Onhand Inventory 3.0.238" in s,
 "Victoria only": 'sessionName.toLowerCase(java.util.Locale.US).contains("victoria")' in s and 'if(isVictoriaCoffeeInventory()){' in s,
 "all areas":all(x in s for x in ["Under-Stair-Center","Supply-Shelves-White","Utility-Fridge","Equipment-Staging-Cart-01","Display-Shelves-Right","Demo-Floor-05"]),
 "overhead":'index<=10' in s and '"Overhead-%02d"' in s,
 "floor map":'VICTORIA COFFEE — VISUAL FLOOR PLAN' in s and 'SCHEMATIC / NOT TO SCALE' in s,
 "count reconciliation":'OTHER / UNMAPPED' in s and 'int grand=0;for(InventoryDb.Row item:db.items(sessionId))grand+=item.quantity;' in s,
 "physical scanner preserves exact labels":'isVictoriaSpecialLocation(scanned)' in s,
 "rack bays preserved":'warehouseSlotName(bay,tier,pallet)' in s and 'showWarehouseBaySetup()' in s,
 "other workflows":'Fleet Feet Client — Barcode + Qty (No Headers)' in s and 'Petrosoft' in s and 'Victoria' in s,
 "workflow":'.github/prepare_30238.py' in workflow.read_text()
}
failed=[k for k,v in checks.items() if not v]
if failed:raise SystemExit("3.0.238 validation failed: "+", ".join(failed))
print("OnHand 3.0.238: Victoria-only area template and schematic interactive floor plan with live quantity reconciliation.")
