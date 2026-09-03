from pathlib import Path

p=Path('app/src/main/java/com/iceinventory/onhand/MainActivity.java')
s=p.read_text()

# Add configurable import field order/state alongside the existing export format.
field_anchor='''    private final ArrayList<String> exportColumns=new ArrayList<>();
    private final Map<String,Boolean> exportEnabled=new LinkedHashMap<>();
'''
field_repl=field_anchor+'''    private final ArrayList<String> importColumns=new ArrayList<>();
    private final Map<String,Boolean> importEnabled=new LinkedHashMap<>();
'''
if field_anchor not in s:
    raise SystemExit('export field anchor not found')
s=s.replace(field_anchor,field_repl,1)

# Initialize import defaults to match the normal export defaults:
# Barcode, Description, Quantity, Location (Price available but off).
s=s.replace('''        initExportFormat();
        try {''','''        initExportFormat();
        initImportFormat();
        try {''',1)

method_anchor='''    private void initializeApp() {'''
init_import='''    private void initImportFormat() {
        if(!importColumns.isEmpty()) return;
        String[] cols={"Barcode","Description","Price","Quantity","Location"};
        for(String c:cols) importColumns.add(c);
        importEnabled.put("Barcode",true);
        importEnabled.put("Description",true);
        importEnabled.put("Price",false);
        importEnabled.put("Quantity",true);
        importEnabled.put("Location",true);
    }

'''
if method_anchor not in s:
    raise SystemExit('initializeApp anchor not found')
s=s.replace(method_anchor,init_import+method_anchor,1)

# Replace direct file picker with an Import dialog that mirrors Export's format configuration.
old_import='''    private void importCsv(){Intent i=new Intent(Intent.ACTION_OPEN_DOCUMENT);i.addCategory(Intent.CATEGORY_OPENABLE);i.setType("text/*");startActivityForResult(i,REQ_IMPORT);}'''
new_import='''    private void importCsv(){
        LinearLayout content=new LinearLayout(this); content.setOrientation(LinearLayout.VERTICAL); content.setPadding(dp(20),dp(12),dp(20),dp(12));
        TextView intro=new TextView(this); intro.setText("Choose the incoming column order, then select a tab-delimited TXT file. CSV files from older versions are still accepted."); intro.setTextSize(13); content.addView(intro);
        Button configure=button("Configure Import Format"); configure.setOnClickListener(v->showConfigureImportFormat()); content.addView(configure);
        new AlertDialog.Builder(this).setTitle("File Import").setView(content)
                .setPositiveButton("Choose File",(d,w)->{
                    if(!Boolean.TRUE.equals(importEnabled.get("Barcode"))){ toast("Import format must include Barcode"); return; }
                    Intent i=new Intent(Intent.ACTION_OPEN_DOCUMENT); i.addCategory(Intent.CATEGORY_OPENABLE); i.setType("text/*"); startActivityForResult(i,REQ_IMPORT);
                })
                .setNegativeButton("Cancel",null).show();
    }'''
if old_import not in s:
    raise SystemExit('importCsv method not found')
s=s.replace(old_import,new_import,1)

# Add a Configure Import Format dialog that behaves like Configure Output Format.
config_anchor='''    private void confirmZeroQuantities(String loc)'''
config_method='''    private void showConfigureImportFormat() {
        LinearLayout box=new LinearLayout(this); box.setOrientation(LinearLayout.VERTICAL); box.setPadding(dp(14),dp(8),dp(14),0);
        TextView help=new TextView(this); help.setText("Set the incoming file column order. Tap a field to include/exclude it. Barcode must remain included. Use Move Up or Move Down to match the file."); help.setTextSize(13); box.addView(help);
        ListView fields=new ListView(this); fields.setChoiceMode(ListView.CHOICE_MODE_SINGLE);
        ArrayAdapter<String> adapter=new ArrayAdapter<>(this,android.R.layout.simple_list_item_single_choice,new ArrayList<>()); fields.setAdapter(adapter);
        box.addView(fields,new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT,dp(240)));
        final int[] selected={0};
        Runnable refresh=()->{
            ArrayList<String> labels=new ArrayList<>();
            int col=1;
            for(String c:importColumns){
                boolean on=Boolean.TRUE.equals(importEnabled.get(c));
                labels.add((on?("✓  "+col+". "+c):("○     "+c)));
                if(on) col++;
            }
            adapter.clear(); adapter.addAll(labels); adapter.notifyDataSetChanged();
            if(selected[0]>=0&&selected[0]<importColumns.size()) fields.setItemChecked(selected[0],true);
        };
        fields.setOnItemClickListener((p,v,pos,id)->{
            selected[0]=pos; String c=importColumns.get(pos);
            if("Barcode".equals(c)&&Boolean.TRUE.equals(importEnabled.get(c))){ toast("Barcode is required for import"); refresh.run(); return; }
            importEnabled.put(c,!Boolean.TRUE.equals(importEnabled.get(c))); refresh.run();
        });
        LinearLayout move=new LinearLayout(this); move.setOrientation(LinearLayout.HORIZONTAL);
        Button up=button("Move Up"),down=button("Move Down");
        move.addView(up,new LinearLayout.LayoutParams(0,ViewGroup.LayoutParams.WRAP_CONTENT,1));
        move.addView(down,new LinearLayout.LayoutParams(0,ViewGroup.LayoutParams.WRAP_CONTENT,1)); box.addView(move);
        up.setOnClickListener(v->{int pos=selected[0];if(pos>0){String c=importColumns.remove(pos);importColumns.add(pos-1,c);selected[0]=pos-1;refresh.run();}});
        down.setOnClickListener(v->{int pos=selected[0];if(pos>=0&&pos<importColumns.size()-1){String c=importColumns.remove(pos);importColumns.add(pos+1,c);selected[0]=pos+1;refresh.run();}});
        refresh.run();
        new AlertDialog.Builder(this).setTitle("Configure Import Format").setView(box).setPositiveButton("Done",null).setNegativeButton("Cancel",null).show();
    }

'''
if config_anchor not in s:
    raise SystemExit('confirmZeroQuantities anchor not found')
s=s.replace(config_anchor,config_method+config_anchor,1)

# For files without recognizable headers, use the configured import order.
old_no_header='''if(!hasHeader){barcodeIndex=0;descriptionIndex=1;if(first.size()>=5){priceIndex=2;quantityIndex=3;locationIndex=4;}else{quantityIndex=2;locationIndex=3;priceIndex=-1;}}else{if(barcodeIndex<0)barcodeIndex=0;if(descriptionIndex<0)descriptionIndex=1;}'''
new_no_header='''if(!hasHeader){ArrayList<String>activeImport=new ArrayList<>();for(String c:importColumns)if(Boolean.TRUE.equals(importEnabled.get(c)))activeImport.add(c);barcodeIndex=activeImport.indexOf("Barcode");descriptionIndex=activeImport.indexOf("Description");priceIndex=activeImport.indexOf("Price");quantityIndex=activeImport.indexOf("Quantity");locationIndex=activeImport.indexOf("Location");if(barcodeIndex<0){toast("Import format must include Barcode");return;}}else{if(barcodeIndex<0)barcodeIndex=0;if(descriptionIndex<0)descriptionIndex=1;}'''
if old_no_header not in s:
    raise SystemExit('headerless import mapping block not found')
s=s.replace(old_no_header,new_no_header,1)

p.write_text(s)

b=Path('app/build.gradle')
g=b.read_text().replace('versionCode 30040','versionCode 30041').replace("versionName '3.0.40'","versionName '3.0.41'")
b.write_text(g)
