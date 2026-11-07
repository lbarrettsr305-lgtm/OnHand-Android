"""Apply 3.0.260 scan-entry and text-selection fixes after fix_30259.py."""
from pathlib import Path

path=Path("app/src/main/java/com/iceinventory/onhand/MainActivity.java")
source=path.read_text()
def replace_once(old,new):
    global source
    assert source.count(old)==1, "Unexpected source: "+old[:100]
    source=source.replace(old,new,1)

replace_once('text("Onhand Inventory 3.0.256",19,Color.WHITE,true)',
             'text("Onhand Inventory "+installedVersion(),19,Color.WHITE,true)')
replace_once('String mode=isStoreSetupMode()?"search":getUnknownBarcodeMode();',
             'String mode=isStoreSetupMode()?"manual":getUnknownBarcodeMode();')
replace_once('''        description.setText("");
        if(!"search".equals(mode)) {''','''        description.setText("");
        qty.setText("");
        currentPrice="";
        updatePricePreview();
        if(!"search".equals(mode)) {''')
replace_once('''        toast("Searching internet for item...");
        final String lookupCode=code;''','''        lookupScannedBarcodeOnline(code);
    }

    private void lookupScannedBarcodeOnline(String code) {
        if(code==null||code.trim().isEmpty()){toast("Scan or enter a barcode first");focusBarcodeWithoutKeyboard();return;}
        toast("Searching internet for item...");
        final String lookupCode=code.trim();''')
replace_once('''        final String c=code==null?"":code.trim();
        if(c.isEmpty()){focusDescription();return;}
        new AlertDialog.Builder(this)''','''        final String c=code==null?"":code.trim();
        if(c.isEmpty()){focusDescription();return;}
        if(isStoreSetupMode()){focusDescription();return;}
        new AlertDialog.Builder(this)''')
replace_once('''        root.addView(manualDescriptionActions);

        manualItemPhotoButton''','''        root.addView(manualDescriptionActions);
        Button searchBarcodeOnline=button("Search Barcode Online",0);
        searchBarcodeOnline.setTextSize(14);
        searchBarcodeOnline.setOnClickListener(v->lookupScannedBarcodeOnline(barcode.getText().toString()));
        root.addView(searchBarcodeOnline,new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT,dp(44)));

        manualItemPhotoButton''')
path.write_text(source)

path=Path("app/src/main/java/com/iceinventory/onhand/DescriptionScanActivity.java")
source=path.read_text()
start=source.index("    private void showTextAreaPicker(){")
end=source.index("    private String cleanLine(",start)
replacement='''    private void showTextAreaPicker(){
        java.util.ArrayList<String> lines=new java.util.ArrayList<>(latestLines);
        if(lines.isEmpty()){Toast.makeText(this,"No readable text areas yet",Toast.LENGTH_SHORT).show();return;}
        // Freeze the recognized lines for this picker while the camera continues.
        boolean[] checked=new boolean[lines.size()];
        LinearLayout panel=new LinearLayout(this);
        panel.setOrientation(LinearLayout.VERTICAL);
        panel.setPadding(dp(16),dp(8),dp(16),dp(8));
        TextView instruction=new TextView(this);
        instruction.setText("Check the product name, size, or other lines you want. They will be combined in reading order.");
        instruction.setTextSize(16);
        instruction.setTextColor(Color.WHITE);
        instruction.setPadding(0,0,0,dp(12));
        panel.addView(instruction);
        for(int i=0;i<lines.size();i++){
            final int selected=i;
            android.widget.CheckBox choice=new android.widget.CheckBox(this);
            choice.setText(lines.get(i));
            choice.setTextSize(25);
            choice.setTextColor(Color.WHITE);
            choice.setMinHeight(dp(56));
            choice.setPadding(dp(4),dp(8),dp(4),dp(8));
            choice.setOnCheckedChangeListener((button,isChecked)->checked[selected]=isChecked);
            panel.addView(choice,new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT,ViewGroup.LayoutParams.WRAP_CONTENT));
        }
        android.widget.ScrollView scroll=new android.widget.ScrollView(this);
        scroll.addView(panel);
        AlertDialog dialog=new AlertDialog.Builder(this)
            .setTitle("Choose text to combine")
            .setView(scroll)
            .setNegativeButton("CANCEL",null)
            .setPositiveButton("USE SELECTED",null)
            .create();
        dialog.setOnShowListener(ignored->dialog.getButton(AlertDialog.BUTTON_POSITIVE).setOnClickListener(v->{
            java.util.ArrayList<String> selected=new java.util.ArrayList<>();
            for(int i=0;i<lines.size();i++)if(checked[i])selected.add(lines.get(i));
            String combined=DescriptionSuggestion.combineSelected(selected);
            if(combined.isEmpty()){
                Toast.makeText(this,"Select at least one text line",Toast.LENGTH_SHORT).show();
                return;
            }
            dialog.dismiss();
            returnText(combined);
        }));
        dialog.show();
    }

'''
assert '.setMultiChoiceItems(' in source[start:end]
path.write_text(source[:start]+replacement+source[end:])
build=Path("app/build.gradle")
config=build.read_text()
assert "versionCode 30259" in config and "versionName '3.0.259'" in config
build.write_text(config.replace("versionCode 30259","versionCode 30260").replace("versionName '3.0.259'","versionName '3.0.260'"))
print("Applied 3.0.260: description-first setup, optional online lookup, visible 25sp text choices, installed version label.")
