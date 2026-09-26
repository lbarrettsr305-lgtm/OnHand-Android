from pathlib import Path
import re

base = Path('.github/prepare_30158.py')
exec(compile(base.read_text(), str(base), 'exec'), {'__name__': '__main__', '__file__': str(base)})


def rep(path, old, new, label):
    target = Path(path)
    source = target.read_text()
    if source.count(old) != 1:
        raise SystemExit('3.0.159 expected one target for ' + label)
    target.write_text(source.replace(old, new, 1))


rep('app/build.gradle', 'versionCode 30158', 'versionCode 30159', 'Gradle code')
rep('app/build.gradle', "versionName '3.0.158'", "versionName '3.0.159'", 'Gradle name')
rep('app/src/main/AndroidManifest.xml', 'iCE Onhand 3.0.158', 'iCE Onhand 3.0.159', 'manifest version')
rep('app/src/main/java/com/iceinventory/onhand/MainActivity.java',
    'Onhand Inventory 3.0.158', 'Onhand Inventory 3.0.159', 'visible version')

# Replace the shortened 3.0.157 locations with the exact approved Location-Scan
# names. Existing item counts are not changed or deleted.
db_path = Path('app/src/main/java/com/iceinventory/onhand/InventoryDb.java')
db = db_path.read_text()
pattern = r'''        boolean installLocationMaster=true;.*?if\(installLocationMaster\)\{ContentValues marker=new ContentValues\(\);marker\.put\("key","location_master"\);marker\.put\("value","30157"\);db\.insertWithOnConflict\("app_meta",null,marker,SQLiteDatabase\.CONFLICT_REPLACE\);\}'''
replacement = '''        boolean installLocationMaster=true;
        try(Cursor marker=db.rawQuery("SELECT value FROM app_meta WHERE key='location_master' LIMIT 1",null)){
            installLocationMaster=!marker.moveToFirst()||!"30159".equals(marker.getString(0));
        }
        if(installLocationMaster){
            // Remove only the known shortened template rows. Keep user-created locations.
            String[] legacyLocations={
                "FloorDisplay-3010","Backroom-441","Backroom-4444",
                "Wall1-451","Wall2-452","Wall3-453","Wall4-454",
                "Deli-463","Deli-4610","GlassDisplay-4710","Display-5050",
                "Display1-5110","Display2-5210","Display3-5310","Display4-5410","Display5-5510",
                "Display6-5610","Display7-5710","Display8-5810","Display9-5910",
                "Location-6010","Location-7070","Checkout-911","Checkout-913","Checkout-9111",
                "Office-9210","Location-9595","CoolerInside","CoolerDoors","Outside","Fountain"
            };
            for(String legacy:legacyLocations)db.delete("locations","name=? COLLATE NOCASE",new String[]{legacy});
        }
        ArrayList<String> frequentLocations=new ArrayList<>();
        frequentLocations.add("Main");
        for(int aisle=1;aisle<=20;aisle++){
            frequentLocations.add("Aisle"+aisle+"Front-"+aisle+"1");
            frequentLocations.add("Aisle"+aisle+"Left-"+aisle+"2");
            frequentLocations.add("Aisle"+aisle+"Back-"+aisle+"3");
            frequentLocations.add("Aisle"+aisle+"Right-"+aisle+"4");
            frequentLocations.add("Aisle"+aisle+"All-"+aisle+"10");
        }
        String[] exactLocations={
            "Floor DisplAll-3010","Cig Shelf-221","Cig Shelf-222","Cig Shelf-223",
            "BackroomFront-441","BackroomLeft-442","BackroomBack-443","BackroomRight-444","BackroomCenter-445","BackroomALL-4444",
            "WallsFront-451","WallsLeft-452","WallsBack-453","WallsRight-454",
            "Deli AreaFront-461","Deli AreaLeft-462","Deli AreaBack-463","Deli AreaRight-464","Deli AreaCenter-465","Deli AreaALL-4610",
            "Glass DisplaysFront-471","Glass DisplaysLeft-472","Glass DisplaysBack-473","Glass DisplaysRight-474","Glass DisplaysCenter-475","Glass DisplaysALL-4710",
            "PharmacyFront-481","PharmacyLeft-482","PharmacyBack-483","PharmacyRight-484","PharmacyCenter-485",
            "PharmacyMain Location-4810","PharmacyOver Head-4811","PharmacyUnder Stock-4813","PharmacyExtra Location-4814","PharmacyUnder Stock2-4815","PharmacyTop-4816","PharmacyDrawers-4817",
            "Display-5110","Display-5210","Display-5310","Display-5410","Display-5510","Display-5610","Display-5710","Display-5810","Display-5910",
            "Other Location-6010","Cooler InsideALL-7070","Fountain Area-7110","Cooler Door1ALL-5050",
            "Cooler Door-272","Cooler Door-373","Cooler Door-474","Cooler Door-575","Cooler Door-676","Cooler Door-777","Cooler Door-878","Cooler Door-979","Cooler Door-1080","Cooler Door-1181","Cooler Door-1282","Cooler Door-1383","Cooler Door-1484","Cooler Door-1585","Cooler Door-1686","Cooler Door-1787","Cooler Door-1888","Cooler Door-1989",
            "CheckoutFront-911","CheckoutLeft-912","CheckoutBack-913","CheckoutRight-914","CheckoutCenter-915",
            "CheckoutMain Loc-9110","CheckoutOver Head-9111","CheckoutUnder Stock-9113","CheckoutExtra Loc-9114","CheckoutUnder Stock2-9115","CheckoutTop-9116",
            "OfficeFront-921","OfficeLeft-922","OfficeBack-923","OfficeRight-924","Understock-9310","Over Head-9410","Outside-9595","CREDITS-9610","Purch/Delivery-9710","Sales-9999"
        };
        Collections.addAll(frequentLocations,exactLocations);
        for(String name:frequentLocations){
            ContentValues loc=new ContentValues();loc.put("name",name);
            db.insertWithOnConflict("locations",null,loc,SQLiteDatabase.CONFLICT_IGNORE);
        }
        if(installLocationMaster){ContentValues marker=new ContentValues();marker.put("key","location_master");marker.put("value","30159");db.insertWithOnConflict("app_meta",null,marker,SQLiteDatabase.CONFLICT_REPLACE);}'''
db2, count = re.subn(pattern, replacement, db, count=1, flags=re.S)
if count != 1:
    raise SystemExit('3.0.159 location template target missing')
db_path.write_text(db2)

main_path = Path('app/src/main/java/com/iceinventory/onhand/MainActivity.java')
main = main_path.read_text()

# Make the location control explicitly available throughout counting.
main = main.replace('Button addLoc=button("Set\\nLocation",0);',
                    'Button addLoc=button("Change\\nLocation",0);', 1)
if 'Button addLoc=button("Change\\nLocation",0);' not in main:
    raise SystemExit('3.0.159 Change Location button target missing')
main = main.replace('currentLocationBanner.setBackgroundColor(darkGreen());',
                    'currentLocationBanner.setBackgroundColor(darkGreen());\n        currentLocationBanner.setOnClickListener(v->showLocationStep());', 1)

# Replace the flat location selector with parent-first hierarchy. Single-location
# parents auto-select their only exact location.
location_methods = r'''    private String locationParent(String name){
        String n=name==null?"":name.trim();
        if(n.matches("(?i)^Aisle\\d+.*"))return "Aisle";
        if(n.startsWith("Checkout"))return "Checkout";
        if(n.startsWith("Cooler Door"))return "Cooler Doors";
        if(n.startsWith("Cooler Inside"))return "Cooler Inside";
        if(n.startsWith("Backroom"))return "Backroom";
        if(n.startsWith("Walls"))return "Walls";
        if(n.startsWith("Deli Area"))return "Deli Area";
        if(n.startsWith("Glass Displays"))return "Glass Displays";
        if(n.startsWith("Pharmacy"))return "Pharmacy";
        if(n.startsWith("Display-"))return "Display";
        if(n.startsWith("Cig Shelf"))return "Cigarette Shelves";
        if(n.startsWith("Office"))return "Office";
        if(n.startsWith("Floor Displ"))return "Floor Display";
        if(n.startsWith("Fountain Area"))return "Fountain Area";
        if(n.startsWith("Other Location"))return "Other Location";
        if(n.startsWith("Understock"))return "Understock";
        if(n.startsWith("Over Head"))return "Over Head";
        if(n.startsWith("Outside"))return "Outside";
        if(n.startsWith("CREDITS"))return "Credits";
        if(n.startsWith("Purch/Delivery"))return "Purchases / Delivery";
        if(n.startsWith("Sales"))return "Sales";
        return n;
    }

    private void showLocationStep(){
        if(!requireCurrentCount())return;
        if(locationDialog!=null&&locationDialog.isShowing())return;
        LinearLayout panel=new LinearLayout(this);panel.setOrientation(LinearLayout.VERTICAL);
        panel.setPadding(dp(16),dp(8),dp(16),dp(4));
        TextView instructions=text("First choose the MAIN LOCATION. Then choose the exact aisle side or subsection. A location with only one choice is selected automatically.",16,Color.WHITE,false);
        panel.addView(instructions);

        List<String> names=db.locations();
        LinkedHashMap<String,ArrayList<String>> grouped=new LinkedHashMap<>();
        for(String name:names){String parent=locationParent(name);ArrayList<String> children=grouped.get(parent);if(children==null){children=new ArrayList<>();grouped.put(parent,children);}children.add(name);}
        ArrayList<String> parents=new ArrayList<>();parents.add("1. Choose main location");parents.addAll(grouped.keySet());
        Spinner parentChoice=new Spinner(this);
        parentChoice.setAdapter(new ArrayAdapter<>(this,android.R.layout.simple_spinner_dropdown_item,parents));
        panel.addView(parentChoice,new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT,dp(54)));

        ArrayList<String> children=new ArrayList<>();children.add("2. Choose exact location");
        ArrayAdapter<String> childAdapter=new ArrayAdapter<>(this,android.R.layout.simple_spinner_dropdown_item,children);
        Spinner childChoice=new Spinner(this);childChoice.setAdapter(childAdapter);
        panel.addView(childChoice,new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT,dp(54)));

        EditText entry=new EditText(this);entry.setSingleLine(true);entry.setHint("Exact location or scanned location label");
        entry.setTextColor(Color.WHITE);entry.setHintTextColor(Color.LTGRAY);
        panel.addView(entry,new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT,dp(56)));
        locationScanInput=entry;

        parentChoice.setOnItemSelectedListener(new android.widget.AdapterView.OnItemSelectedListener(){
            public void onNothingSelected(android.widget.AdapterView<?> parent){}
            public void onItemSelected(android.widget.AdapterView<?> parent,android.view.View view,int pos,long id){
                children.clear();children.add("2. Choose exact location");
                if(pos>0){ArrayList<String> found=grouped.get(parents.get(pos));if(found!=null)children.addAll(found);}
                childAdapter.notifyDataSetChanged();childChoice.setSelection(0);
                if(children.size()==2){entry.setText(children.get(1));childChoice.setVisibility(View.GONE);}
                else{entry.setText("");childChoice.setVisibility(View.VISIBLE);}
            }
        });
        childChoice.setOnItemSelectedListener(new android.widget.AdapterView.OnItemSelectedListener(){
            public void onNothingSelected(android.widget.AdapterView<?> parent){}
            public void onItemSelected(android.widget.AdapterView<?> parent,android.view.View view,int pos,long id){if(pos>0)entry.setText(children.get(pos));}
        });

        Button camera=button("Scan Location Label",1);
        camera.setOnClickListener(v->GmsBarcodeScanning.getClient(this).startScan()
            .addOnSuccessListener(result->{String value=result.getRawValue();if(value!=null)entry.setText(value.trim());})
            .addOnFailureListener(e->showError("Location scanner error",e)));
        panel.addView(camera,new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT,dp(52)));
        String title=confirmedLocationSession==sessionId&&!confirmedLocation.isEmpty()?"CHANGE COUNTING LOCATION":"1  SET COUNTING LOCATION";
        locationDialog=new AlertDialog.Builder(this).setTitle(title)
            .setView(panel).setPositiveButton("USE THIS LOCATION",null)
            .setNegativeButton("Cancel",(d,w)->{locationDialog=null;locationScanInput=null;}).create();
        locationDialog.setOnShowListener(x->locationDialog.getButton(AlertDialog.BUTTON_POSITIVE)
            .setOnClickListener(v->submitCountingLocation(entry.getText().toString().trim())));
        locationDialog.show();
    }
'''
method_pattern = r'''    private void showLocationStep\(\)\{.*?\n    \}\n(?=\n    private void refreshList\(\))'''
main2, count = re.subn(method_pattern, lambda match: location_methods, main, count=1, flags=re.S)
if count != 1:
    raise SystemExit('3.0.159 location dialog target missing')
main = main2

# Never silently drop a quantity typed but not yet added when leaving counting.
leave_methods = r'''    private boolean hasPendingCount(){
        return (barcode!=null&&!barcode.getText().toString().trim().isEmpty())||(qty!=null&&!qty.getText().toString().trim().isEmpty());
    }

    private void leaveCountingSafely(Runnable leave){
        hideKeyboard();
        if(!hasPendingCount()){safetyCheckpoint("Leaving counting screen",true);leave.run();return;}
        String code=barcode==null?"":barcode.getText().toString().trim();
        String amount=qty==null?"":qty.getText().toString().trim();
        if(code.isEmpty()||amount.isEmpty()){
            new AlertDialog.Builder(this).setTitle("COUNT NOT SAVED")
                .setMessage("A barcode or quantity is still incomplete. Finish the count or clear the entry before leaving.")
                .setPositiveButton("STAY AND FINISH",null).show();
            return;
        }
        new AlertDialog.Builder(this).setTitle("SAVE COUNT BEFORE LEAVING?")
            .setMessage("Barcode: "+code+"\nQuantity: "+amount+"\nLocation: "+confirmedLocation+"\n\nThis count has not been added yet.")
            .setNegativeButton("STAY",null)
            .setPositiveButton("SAVE COUNT & RETURN",(d,w)->{
                addItem();
                if(barcode.getText().toString().trim().isEmpty()&&qty.getText().toString().trim().isEmpty()){
                    safetyCheckpoint("Saved before leaving counting",true);leave.run();
                }
            }).show();
    }

    @Override public void onBackPressed(){leaveCountingSafely(this::finish);}

'''
anchor = '    private void normalizeNoActiveInventoryName() {'
if anchor not in main:
    raise SystemExit('3.0.159 leave safeguard anchor missing')
main = main.replace(anchor, leave_methods + anchor, 1)

# Route the yellow Return button through the same unsaved-count safeguard.
old_monthly_click = 'monthly.setOnClickListener(v->{hideKeyboard();if(monthlyWorkflowMode)finish();else{if(archivedMonthly)mw.edit().putBoolean("active",true).putBoolean("archived",false).putInt("stage",5).putBoolean("combined_exported",false).putBoolean("client_exported",false).putBoolean("audit_exported",false).apply();startActivity(new Intent(this,MonthlyInventoryActivity.class));}});'
new_monthly_click = 'monthly.setOnClickListener(v->{if(monthlyWorkflowMode)leaveCountingSafely(this::finish);else{hideKeyboard();if(archivedMonthly)mw.edit().putBoolean("active",true).putBoolean("archived",false).putInt("stage",5).putBoolean("combined_exported",false).putBoolean("client_exported",false).putBoolean("audit_exported",false).apply();startActivity(new Intent(this,MonthlyInventoryActivity.class));}});'
if old_monthly_click not in main:
    raise SystemExit('3.0.159 monthly return target missing')
main = main.replace(old_monthly_click, new_monthly_click, 1)
main_path.write_text(main)

monthly_path = Path('app/src/main/java/com/iceinventory/onhand/MonthlyInventoryActivity.java')
monthly = monthly_path.read_text()
monthly = monthly.replace('nextStep.setVisibility(View.GONE);root.addView(nextStep);',
                          'nextStep.setVisibility(View.GONE);nextStep.setOnClickListener(v->adjustDeviceCount());root.addView(nextStep);', 1)
monthly = monthly.replace('deviceSessionId=w.getLong("device_session_id",-1);combinedExported=',
                          'deviceSessionId=w.getLong("device_session_id",-1);deviceLoaded=deviceSessionId>0;combinedExported=', 1)
monthly = monthly.replace('nextStep.setText("COUNTING STARTED ON THIS MACHINE\\nContinue the physical count here.\\nAfter every user finishes and exports, press 5. Select All User Count Files.");',
                          'nextStep.setText("COUNTING STARTED ON THIS MACHINE\\nTAP HERE TO RETURN TO THE ACTIVE COUNT.\\nAfter every user finishes and exports, press 5. Select All User Count Files.");', 1)
if 'TAP HERE TO RETURN TO THE ACTIVE COUNT' not in monthly or 'deviceLoaded=deviceSessionId>0' not in monthly:
    raise SystemExit('3.0.159 monthly resume targets missing')
monthly_path.write_text(monthly)

checks = {
    'version': "versionName '3.0.159'" in Path('app/build.gradle').read_text(),
    'cooler doors': 'Cooler Door1ALL-5050' in db2,
    'cooler inside': 'Cooler InsideALL-7070' in db2,
    'checkout front': 'CheckoutFront-911' in db2,
    'all aisles': 'aisle<=20' in db2,
    'parent hierarchy': '1. Choose main location' in main,
    'change location': 'CHANGE COUNTING LOCATION' in main,
    'back safeguard': '@Override public void onBackPressed(){leaveCountingSafely(this::finish);}' in main,
    'yellow resume': 'TAP HERE TO RETURN TO THE ACTIVE COUNT' in monthly,
}
missing=[label for label,ok in checks.items() if not ok]
if missing:
    raise SystemExit('3.0.159 verification missing: '+', '.join(missing))

print('Prepared iCE OnHand 3.0.159: exact hierarchical locations, location switching, active-count resume, and unsaved-count protection')
