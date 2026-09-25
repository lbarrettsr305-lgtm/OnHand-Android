from pathlib import Path

base = Path('.github/prepare_30154.py')
exec(compile(base.read_text(), str(base), 'exec'), {'__name__': '__main__', '__file__': str(base)})


def rep(path, old, new):
    target = Path(path)
    source = target.read_text()
    if source.count(old) != 1:
        raise SystemExit('3.0.155 expected one target: ' + old[:140])
    target.write_text(source.replace(old, new, 1))


rep('app/build.gradle', 'versionCode 30154', 'versionCode 30155')
rep('app/build.gradle', "versionName '3.0.154'", "versionName '3.0.155'")
rep('app/src/main/AndroidManifest.xml', 'iCE Onhand 3.0.154', 'iCE Onhand 3.0.155')
m = 'app/src/main/java/com/iceinventory/onhand/MainActivity.java'
db = 'app/src/main/java/com/iceinventory/onhand/InventoryDb.java'
rep(m, 'Onhand Inventory 3.0.154', 'Onhand Inventory 3.0.155')

# Future counts reuse the stored spelling of a location and never split totals by case.
rep(db,
'''        String safeLocation = location == null || location.trim().isEmpty() ? "Main" : location.trim();
        long when=updatedAt>0?updatedAt:System.currentTimeMillis();
        String[] args = { String.valueOf(sessionId), safeBarcode, safeLocation };
        try (Cursor c = db.rawQuery("SELECT id,quantity FROM items WHERE session_id=? AND barcode=? AND location=?", args)) {''',
'''        String safeLocation = canonicalLocation(location);
        long when=updatedAt>0?updatedAt:System.currentTimeMillis();
        String[] args = { String.valueOf(sessionId), safeBarcode, safeLocation };
        try (Cursor c = db.rawQuery("SELECT id,quantity FROM items WHERE session_id=? AND barcode=? AND location=? COLLATE NOCASE", args)) {''')

rep(db,
'''    public int zeroAllQuantities(long sessionId) {''',
'''    private String canonicalLocation(String location) {
        String requested=location==null||location.trim().isEmpty()?"Main":location.trim();
        try(Cursor c=getReadableDatabase().rawQuery("SELECT name FROM locations WHERE name=? COLLATE NOCASE LIMIT 1",new String[]{requested})) {
            if(c.moveToFirst())return c.getString(0);
        }
        return requested;
    }

    /** Moves one selected count line and merges with the same barcode at the destination. */
    public boolean moveItem(long id,String destination) {
        Row source=rowById(id);
        if(source==null||source.quantity==0)return false;
        String target=canonicalLocation(destination);
        if(target.equalsIgnoreCase(source.location==null?"":source.location.trim()))return false;
        SQLiteDatabase sql=getWritableDatabase();
        sql.beginTransaction();
        try {
            long targetId=-1L;int targetQty=0;
            try(Cursor c=sql.rawQuery("SELECT id,quantity FROM items WHERE session_id=? AND barcode=? AND location=? COLLATE NOCASE LIMIT 1",
                    new String[]{String.valueOf(source.sessionId),source.barcode,target})) {
                if(c.moveToFirst()){targetId=c.getLong(0);targetQty=c.getInt(1);}
            }
            if(targetId>0) {
                ContentValues cv=new ContentValues();cv.put("quantity",targetQty+source.quantity);cv.put("updated_at",System.currentTimeMillis());
                if(source.description!=null&&!source.description.trim().isEmpty())cv.put("description",source.description.trim());
                if(source.price!=null&&!source.price.trim().isEmpty())cv.put("price",source.price.trim());
                sql.update("items",cv,"id=?",new String[]{String.valueOf(targetId)});
                sql.delete("items","id=?",new String[]{String.valueOf(source.id)});
            } else {
                ContentValues cv=new ContentValues();cv.put("location",target);cv.put("updated_at",System.currentTimeMillis());
                sql.update("items",cv,"id=?",new String[]{String.valueOf(source.id)});
            }
            recordHistory(source.sessionId,source.barcode,source.description,-source.quantity,source.location,"MOVE_OUT");
            recordHistory(source.sessionId,source.barcode,source.description,source.quantity,target,"MOVE_IN");
            sql.setTransactionSuccessful();
            return true;
        } finally { sql.endTransaction(); }
    }

    public int zeroAllQuantities(long sessionId) {''')

# Count detail means actual counted lines, never the untouched imported zero catalog.
rep(m,
'''        for(InventoryDb.Row r:db.itemsInScanOrder(sessionId)) {
            out.append(user).append('\\t')''',
'''        for(InventoryDb.Row r:db.itemsInScanOrder(sessionId)) {
            if(r.quantity==0)continue;
            out.append(user).append('\\t')''')
rep('app/src/main/java/com/iceinventory/onhand/SimpleXlsxWriter.java',
'''        for(InventoryDb.Row r:rows){
            n++; x.append("<row r=\\\"").append(n).append("\\\">");''',
'''        for(InventoryDb.Row r:rows){
            if(r.quantity==0)continue;
            n++; x.append("<row r=\\\"").append(n).append("\\\">");''')

rep(m,
'''        for(String loc:db.locations()) {
            String key=loc==null||loc.trim().isEmpty()?"Main":loc.trim();
            totals.put(key,0);
        }
        int grandTotal=0;''',
'''        int grandTotal=0;''')
rep(m,
'''            int qty=r.quantity;
            Integer current=totals.get(key);''',
'''            int qty=r.quantity;
            if(qty==0)continue;
            Integer current=totals.get(key);''')

# Let a location be entered as Parent plus an optional side/subsection.
rep(m,
'''        TextView instructions=text("Choose an existing short location name, type a new one, or scan its label. Submit the location before counting barcodes.",16,Color.WHITE,false);''',
'''        TextView instructions=text("Choose an existing location, or enter a parent area and optional side/subsection. Examples: Aisle 1 + Front, Checkout + Understock, Cooler Doors + Door 3.",16,Color.WHITE,false);''')
rep(m,
'''        EditText entry=new EditText(this);entry.setSingleLine(true);entry.setHint("Short location name / scanned label");
        entry.setTextColor(Color.WHITE);entry.setHintTextColor(Color.LTGRAY);
        panel.addView(entry,new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT,dp(56)));
        locationScanInput=entry;''',
'''        EditText entry=new EditText(this);entry.setSingleLine(true);entry.setHint("Parent location / scanned label");
        entry.setTextColor(Color.WHITE);entry.setHintTextColor(Color.LTGRAY);
        panel.addView(entry,new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT,dp(56)));
        EditText subsection=new EditText(this);subsection.setSingleLine(true);subsection.setHint("Side / subsection (optional)");
        subsection.setTextColor(Color.WHITE);subsection.setHintTextColor(Color.LTGRAY);
        panel.addView(subsection,new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT,dp(56)));
        locationScanInput=entry;''')
rep(m,
'''                if(pos>0)entry.setText(options.get(pos));''',
'''                if(pos>0){entry.setText(options.get(pos));subsection.setText("");}''')
rep(m,
'''            .setOnClickListener(v->submitCountingLocation(entry.getText().toString())));''',
'''            .setOnClickListener(v->{
                String parent=entry.getText().toString().trim();String side=subsection.getText().toString().trim();
                submitCountingLocation(side.isEmpty()||parent.contains(" > ")?parent:parent+" > "+side);
            }));''')

# Replace the flat totals popup with a hierarchical store map.
rep(m, 'Button totals=button("▥ Location Totals",0);totals.setOnClickListener(v->showLocationTotals());',
       'Button totals=button("▥ Store Map",0);totals.setOnClickListener(v->showLocationTotals());')
old = '''    private void showLocationTotals() {
        Map<String,Integer> totals=new LinkedHashMap<>();int grand=0;
        for(InventoryDb.Row r:allRows) {
            String loc=r.location==null||r.location.trim().isEmpty()?"Main":r.location.trim();
            totals.put(loc,totals.getOrDefault(loc,0)+r.quantity);grand+=r.quantity;
        }
        if(totals.isEmpty()){toast("No counts to total yet");return;}
        StringBuilder m=new StringBuilder();
        for(Map.Entry<String,Integer> e:totals.entrySet())m.append(e.getKey()).append(": ").append(e.getValue()).append("\\n");
        m.append("\\nGrand Total: ").append(grand);
        new AlertDialog.Builder(this).setTitle("Quantity Totals by Location").setMessage(m.toString()).setPositiveButton("OK",null).show();
    }'''
new = '''    private void showLocationTotals() {
        class Area {String name;int total;LinkedHashMap<String,Integer> parts=new LinkedHashMap<>();Area(String n){name=n;}}
        LinkedHashMap<String,Area> areas=new LinkedHashMap<>();int grand=0;
        for(InventoryDb.Row r:allRows) {
            if(r.quantity==0)continue;
            String full=r.location==null||r.location.trim().isEmpty()?"Main":r.location.trim();
            String[] pair=full.split("\\\\s*>\\\\s*",2);String parent=pair[0].trim();String key=parent.toLowerCase(Locale.US);
            Area area=areas.get(key);if(area==null){area=new Area(parent);areas.put(key,area);}
            area.total+=r.quantity;grand+=r.quantity;
            if(pair.length>1&&!pair[1].trim().isEmpty()){
                String part=pair[1].trim(),partKey=part.toLowerCase(Locale.US),display=part;
                for(String existing:area.parts.keySet())if(existing.equalsIgnoreCase(part)){display=existing;break;}
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
                StringBuilder sides=new StringBuilder();
                for(Map.Entry<String,Integer> p:area.parts.entrySet())sides.append(p.getKey()).append(": ").append(p.getValue()).append("\\n");
                TextView detail=text(sides.toString().trim(),17,Color.WHITE,false);detail.setPadding(dp(8),dp(7),dp(8),dp(7));card.addView(detail);
                TextView center=text("CENTER / SECTION TOTAL: "+area.total,19,gold(),true);center.setGravity(Gravity.CENTER);center.setPadding(0,dp(7),0,dp(5));card.addView(center);
            }
            LinearLayout.LayoutParams cp=new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT,ViewGroup.LayoutParams.WRAP_CONTENT);cp.setMargins(0,0,0,dp(10));map.addView(card,cp);
        }
        new AlertDialog.Builder(this).setTitle("Store Map • Counted Locations").setView(scroll).setPositiveButton("Close",null).show();
    }'''
rep(m, old, new)

# Add an explicit move action to the selected count line.
rep(m,
'''        AlertDialog dialog=new AlertDialog.Builder(this).setTitle("Adjust Quantity").setView(box)
                .setPositiveButton("Apply",null).setNegativeButton("Cancel",null).create();''',
'''        AlertDialog dialog=new AlertDialog.Builder(this).setTitle("Adjust Quantity").setView(box)
                .setPositiveButton("Apply",null).setNeutralButton("Move Location",null).setNegativeButton("Cancel",null).create();''')
rep(m,
'''            adjustment.requestFocus();adjustment.postDelayed(()->showKeyboard(adjustment),100);
        });''',
'''            dialog.getButton(AlertDialog.BUTTON_NEUTRAL).setOnClickListener(v->{dialog.dismiss();showMoveLocation(r);});
            adjustment.requestFocus();adjustment.postDelayed(()->showKeyboard(adjustment),100);
        });''')
rep(m,
'''    @Override public void onHighlight(InventoryDb.Row r) {''',
'''    private void showMoveLocation(InventoryDb.Row row) {
        if(row==null||row.quantity==0){toast("Only a counted quantity can be moved");return;}
        LinearLayout panel=new LinearLayout(this);panel.setOrientation(LinearLayout.VERTICAL);panel.setPadding(dp(16),dp(8),dp(16),0);
        panel.addView(text("Move "+row.quantity+" units of\\n"+row.barcode+"\\nfrom "+row.location,16,Color.WHITE,true));
        Spinner choices=new Spinner(this);ArrayList<String> names=new ArrayList<>();names.add("Choose destination");
        for(String n:db.locations())if(!n.equalsIgnoreCase(row.location))names.add(n);
        choices.setAdapter(new ArrayAdapter<>(this,android.R.layout.simple_spinner_dropdown_item,names));panel.addView(choices,new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT,dp(52)));
        EditText destination=new EditText(this);destination.setSingleLine(true);destination.setHint("Or type destination location");destination.setTextColor(Color.WHITE);destination.setHintTextColor(Color.LTGRAY);panel.addView(destination,new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT,dp(56)));
        choices.setOnItemSelectedListener(new android.widget.AdapterView.OnItemSelectedListener(){public void onNothingSelected(android.widget.AdapterView<?> p){}public void onItemSelected(android.widget.AdapterView<?> p,View v,int pos,long id){if(pos>0)destination.setText(names.get(pos));}});
        AlertDialog confirm=new AlertDialog.Builder(this).setTitle("Move to Another Location").setView(panel).setPositiveButton("Review Move",null).setNegativeButton("Cancel",null).create();
        confirm.setOnShowListener(x->confirm.getButton(AlertDialog.BUTTON_POSITIVE).setOnClickListener(v->{
            String target=destination.getText().toString().trim();if(target.isEmpty()){toast("Choose or type the destination");return;}if(target.equalsIgnoreCase(row.location)){toast("Choose a different location");return;}
            new AlertDialog.Builder(this).setTitle("Confirm Location Move").setMessage("Move "+row.quantity+" units from\\n"+row.location+"\\nto\\n"+target+"?\\n\\nThe inventory grand total will not change.")
                    .setPositiveButton("MOVE",(d,w)->{db.addLocation(target);if(db.moveItem(row.id,target)){confirmedLocation=target;confirmedLocationSession=sessionId;refreshLocations();refreshList();safetyCheckpoint("After location move",true);toast("Moved "+row.quantity+" units to "+target);}else toast("Move could not be completed");confirm.dismiss();})
                    .setNegativeButton("Cancel",null).show();
        }));confirm.show();
    }

    @Override public void onHighlight(InventoryDb.Row r) {''')

print('Prepared iCE OnHand 3.0.155: counted-only reports, case-insensitive locations, move workflow, and hierarchical store map')
