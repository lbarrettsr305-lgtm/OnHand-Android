from pathlib import Path
import re

base = Path('.github/prepare_30159.py')
exec(compile(base.read_text(), str(base), 'exec'), {'__name__': '__main__', '__file__': str(base)})


def rep(path, old, new, label, count=1):
    target = Path(path)
    source = target.read_text()
    if source.count(old) != count:
        raise SystemExit('3.0.160 expected %d target(s) for %s, found %d' % (count, label, source.count(old)))
    target.write_text(source.replace(old, new, count))


rep('app/build.gradle', 'versionCode 30159', 'versionCode 30160', 'Gradle code')
rep('app/build.gradle', "versionName '3.0.159'", "versionName '3.0.160'", 'Gradle name')
rep('app/src/main/AndroidManifest.xml', 'iCE Onhand 3.0.159', 'iCE Onhand 3.0.160', 'manifest version')
rep('app/src/main/java/com/iceinventory/onhand/MainActivity.java',
    'Onhand Inventory 3.0.159', 'Onhand Inventory 3.0.160', 'visible version')

main_path = Path('app/src/main/java/com/iceinventory/onhand/MainActivity.java')
main = main_path.read_text()

# The location dialog no longer covers the inventory immediately on entry.
# A location remains mandatory when Scan or Add Qty is first used.
main = main.replace('        barcode.postDelayed(this::showLocationStepIfNeeded,650);\n', '', 1)
main = main.replace('refreshLocations();refreshList();showLocationStepIfNeeded();',
                    'refreshLocations();refreshList();', 2)

old_reports = '''        addExportSection(exportPanel,"COMBINE & SPECIAL REPORTS");
        addExportButton(exportPanel,exportDialog,"Combine & Verify User Batches",4);
        addExportButton(exportPanel,exportDialog,"Internet Items With Pictures",5);
        addExportButton(exportPanel,exportDialog,"Location Quantity Report",6);
        addExportButton(exportPanel,exportDialog,"Location Detail — TXT (Scan Order)",7);
        addExportButton(exportPanel,exportDialog,"Location Detail — Excel",8);

        addExportSection(exportPanel,"AUDIT VERIFICATION — COUNTED ITEMS ONLY");
        addExportButton(exportPanel,exportDialog,"Highest Unit Price — Excel",9);
        addExportButton(exportPanel,exportDialog,"Highest Extended Value — Excel",10);
        addExportButton(exportPanel,exportDialog,"Highest Quantity — Excel",11);
'''
new_reports = '''        addExportSection(exportPanel,"LOCATION REPORTS");
        addExportButton(exportPanel,exportDialog,"Location Quantity Report",6);
        addExportButton(exportPanel,exportDialog,"Location Detail — TXT (Scan Order)",7);
        addExportButton(exportPanel,exportDialog,"Location Detail — Excel",8);

        addExportSection(exportPanel,"PETROSOFT MONTHLY REPORTS");
        addExportButton(exportPanel,exportDialog,"Category Description & Quantity — Excel",12);
        addExportButton(exportPanel,exportDialog,"Cigarettes Quantity — Excel",13);

        addExportSection(exportPanel,"AUDIT VERIFICATION — COUNTED ITEMS ONLY");
        addExportButton(exportPanel,exportDialog,"Highest Unit Price — Excel",9);
        addExportButton(exportPanel,exportDialog,"Highest Extended Value — Excel",10);
        addExportButton(exportPanel,exportDialog,"Highest Quantity — Excel",11);

        addExportSection(exportPanel,"COMBINE & OTHER REPORTS");
        addExportButton(exportPanel,exportDialog,"Combine & Verify User Batches",4);
        addExportButton(exportPanel,exportDialog,"Internet Items With Pictures",5);
'''
if old_reports not in main:
    raise SystemExit('3.0.160 export report block target missing')
main = main.replace(old_reports, new_reports, 1)

old_create = '''        exportDialog[0]=new AlertDialog.Builder(this).setTitle("Export Reports")
                .setView(exportScroll).setNegativeButton("Cancel",null).create();
        exportDialog[0].show();'''
new_create = '''        TextView scrollHint=text("SCROLL DOWN FOR ALL REPORTS ↓",13,Color.WHITE,true);
        scrollHint.setGravity(Gravity.CENTER);scrollHint.setPadding(0,dp(5),0,dp(5));
        exportPanel.addView(scrollHint);
        exportDialog[0]=new AlertDialog.Builder(this).setTitle("Export Reports")
                .setView(exportScroll).setNegativeButton("Cancel",null).create();
        exportDialog[0].setOnShowListener(d->{android.view.Window w=exportDialog[0].getWindow();if(w!=null)w.setLayout(ViewGroup.LayoutParams.MATCH_PARENT,ViewGroup.LayoutParams.MATCH_PARENT);});
        exportDialog[0].show();'''
if old_create not in main:
    raise SystemExit('3.0.160 export dialog target missing')
main = main.replace(old_create, new_create, 1)

old_handler = '''        if(which==4){pendingExportLocationDetailReport=false;resetBatchExportState();openBatchMergeForMaster();return;}
        resetBatchExportState();'''
new_handler = '''        if(which==4){pendingExportLocationDetailReport=false;resetBatchExportState();openBatchMergeForMaster();return;}
        if(which==12||which==13){
            Intent reports=new Intent(this,MonthlyInventoryActivity.class);
            reports.putExtra(MonthlyInventoryActivity.EXTRA_REPORT_TARGET,which==12?"category":"cigarettes");
            startActivity(reports);return;
        }
        resetBatchExportState();'''
if old_handler not in main:
    raise SystemExit('3.0.160 export handler target missing')
main = main.replace(old_handler, new_handler, 1)

# Build the Store Map from the exact approved Location-Scan labels. Aisle 1
# Front/Left/Back/Right/All must be one area card, not five unrelated cards.
map_methods = r'''    private String[] storeMapLocation(String full){
        String value=full==null||full.trim().isEmpty()?"Main":full.trim();
        String[] legacy=value.split("\\s*>\\s*",2);
        if(legacy.length>1)return new String[]{legacy[0].trim(),legacy[1].trim()};
        java.util.regex.Matcher aisle=java.util.regex.Pattern.compile("(?i)^Aisle(\\d+)(Front|Left|Back|Right|All)-.*$").matcher(value);
        if(aisle.matches())return new String[]{"Aisle "+aisle.group(1),aisle.group(2)};
        String[] parents={"Checkout","Backroom","Walls","Deli Area","Glass Displays","Pharmacy","Office"};
        for(String parent:parents)if(value.startsWith(parent)){
            String part=value.substring(parent.length());int dash=part.lastIndexOf('-');if(dash>0)part=part.substring(0,dash);
            part=part.trim();return new String[]{parent,part.isEmpty()?"All":part};
        }
        if(value.startsWith("Cooler Door")){
            String part=value.substring("Cooler ".length());int dash=part.lastIndexOf('-');if(dash>0)part=part.substring(0,dash);
            return new String[]{"Cooler Doors",part.trim()};
        }
        if(value.startsWith("Display-"))return new String[]{"Displays",value.substring(value.lastIndexOf('-')+1)};
        if(value.startsWith("Cig Shelf-"))return new String[]{"Cigarette Shelves",value.substring(value.lastIndexOf('-')+1)};
        int dash=value.lastIndexOf('-');String label=dash>0?value.substring(0,dash):value;
        return new String[]{label.trim(),""};
    }

    private void showLocationTotals() {
        class Area {String name;int total;LinkedHashMap<String,Integer> parts=new LinkedHashMap<>();Area(String n){name=n;}}
        LinkedHashMap<String,Area> areas=new LinkedHashMap<>();int grand=0;
        for(InventoryDb.Row r:allRows) {
            if(r.quantity==0)continue;
            String[] pair=storeMapLocation(r.location);String parent=pair[0],part=pair[1],key=parent.toLowerCase(Locale.US);
            Area area=areas.get(key);if(area==null){area=new Area(parent);areas.put(key,area);}
            area.total+=r.quantity;grand+=r.quantity;
            if(!part.isEmpty()){
                String display=part;for(String existing:area.parts.keySet())if(existing.equalsIgnoreCase(part)){display=existing;break;}
                area.parts.put(display,area.parts.getOrDefault(display,0)+r.quantity);
            }
        }
        if(areas.isEmpty()){toast("No counted locations yet");return;}
        ScrollView scroll=new ScrollView(this);LinearLayout map=new LinearLayout(this);map.setOrientation(LinearLayout.VERTICAL);map.setPadding(dp(12),dp(8),dp(12),dp(8));scroll.addView(map);
        TextView grandView=text("STORE GRAND TOTAL: "+grand,20,gold(),true);grandView.setGravity(Gravity.CENTER);grandView.setPadding(0,dp(8),0,dp(12));map.addView(grandView);
        for(Area area:areas.values()){
            LinearLayout card=new LinearLayout(this);card.setOrientation(LinearLayout.VERTICAL);card.setPadding(dp(10),dp(8),dp(10),dp(8));card.setBackgroundColor(Color.rgb(4,55,34));
            TextView heading=text(area.name.toUpperCase(Locale.US),18,Color.WHITE,true);heading.setGravity(Gravity.CENTER);card.addView(heading);
            if(area.parts.isEmpty()){
                TextView only=text("TOTAL\\n"+area.total,24,gold(),true);only.setGravity(Gravity.CENTER);only.setPadding(0,dp(10),0,dp(10));card.addView(only);
            } else {
                StringBuilder sides=new StringBuilder();for(Map.Entry<String,Integer> p:area.parts.entrySet())sides.append(p.getKey()).append(": ").append(p.getValue()).append("\\n");
                TextView detail=text(sides.toString().trim(),17,Color.WHITE,false);detail.setGravity(Gravity.CENTER);detail.setPadding(dp(8),dp(7),dp(8),dp(7));card.addView(detail);
                TextView center=text("CENTER / SECTION TOTAL: "+area.total,19,gold(),true);center.setGravity(Gravity.CENTER);center.setPadding(0,dp(7),0,dp(5));card.addView(center);
            }
            LinearLayout.LayoutParams cp=new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT,ViewGroup.LayoutParams.WRAP_CONTENT);cp.setMargins(0,0,0,dp(10));map.addView(card,cp);
        }
        new AlertDialog.Builder(this).setTitle("Store Map • Counted Locations").setView(scroll).setPositiveButton("Close",null).show();
    }
'''
main, map_count = re.subn(r'''    private void showLocationTotals\(\) \{.*?\n    \}\n(?=\n    private void showInternetItems\(\))''',
                          lambda match: map_methods, main, count=1, flags=re.S)
if map_count != 1:
    raise SystemExit('3.0.160 Store Map target missing')
main_path.write_text(main)

monthly_path = Path('app/src/main/java/com/iceinventory/onhand/MonthlyInventoryActivity.java')
monthly = monthly_path.read_text()
monthly = monthly.replace('EXTRA_START_NEW="monthly_start_new";',
                          'EXTRA_START_NEW="monthly_start_new",EXTRA_REPORT_TARGET="monthly_report_target";', 1)

old_end = '''else if(pendingSourceUri==null)restoreMonthlyWorkflow();
    }'''
new_end = '''else if(pendingSourceUri==null)restoreMonthlyWorkflow();
        String reportTarget=getIntent()==null?"":getIntent().getStringExtra(EXTRA_REPORT_TARGET);
        if(reportTarget!=null&&!reportTarget.isEmpty()){
            Button target="cigarettes".equals(reportTarget)?saveCigarettes:saveCategory;
            target.setBackgroundTintList(android.content.res.ColorStateList.valueOf(Color.rgb(255,215,0)));
            target.setTextColor(Color.BLACK);
            scroll.postDelayed(()->{scroll.smoothScrollTo(0,Math.max(0,target.getTop()-dp(90)));Toast.makeText(this,"Select all user count files at Step 5, then export the highlighted report.",Toast.LENGTH_LONG).show();},250);
        }
    }'''
if old_end not in monthly:
    raise SystemExit('3.0.160 monthly report navigation target missing')
monthly = monthly.replace(old_end, new_end, 1)
monthly_path.write_text(monthly)

checks = {
    'version': "versionName '3.0.160'" in Path('app/build.gradle').read_text(),
    'no forced startup location': 'barcode.postDelayed(this::showLocationStepIfNeeded,650)' not in main,
    'location still mandatory': 'if(!requireCurrentCount()||!ensureCountingLocation())return;' in main,
    'location reports promoted': 'addExportSection(exportPanel,"LOCATION REPORTS")' in main,
    'category report entry': 'Category Description & Quantity — Excel' in main,
    'cigarettes report entry': 'Cigarettes Quantity — Excel' in main,
    'category description source': 'get(r,columns,"CATEGORYNAME")' in monthly,
    'full-height report dialog': 'ViewGroup.LayoutParams.MATCH_PARENT,ViewGroup.LayoutParams.MATCH_PARENT' in main,
    'monthly report navigation': 'EXTRA_REPORT_TARGET' in monthly and 'target.getTop()' in monthly,
    'CHEV2620 map grouping': '"Aisle "+aisle.group(1)' in main and '"Cooler Doors"' in main,
}
missing = [name for name, ok in checks.items() if not ok]
if missing:
    raise SystemExit('3.0.160 verification failed: ' + ', '.join(missing))

print('Prepared iCE OnHand 3.0.160: optional startup location prompt and visible location/category/cigarettes reports')
