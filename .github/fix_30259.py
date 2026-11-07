"""Apply the 3.0.259 price-book dialog fix to the prepared 3.0.258 source."""
from pathlib import Path

path = Path("app/src/main/java/com/iceinventory/onhand/MainActivity.java")
source = path.read_text()
start = source.index("    private void showStorePriceBookFormatChoice(){")
end = source.index("    private void confirmStartPetrosoftWorkflow(){", start)
replacement = '''    private void showStorePriceBookFormatChoice(){
        String[] choices={
                "BARCODE • DESCRIPTION • RETAIL PRICE • ITEM NUMBER",
                "BARCODE • ITEM NUMBER • DESCRIPTION • RETAIL PRICE",
                "QTY • BARCODE • DESCRIPTION • PRICE",
                "USE COLUMN HEADINGS FROM THE FILE"
        };
        String[] orders={"barcode,description,price,item_number","barcode,item_number,description,price","quantity,barcode,description,price","barcode,description,price,item_number"};
        LinearLayout panel=new LinearLayout(this);
        panel.setOrientation(LinearLayout.VERTICAL);
        panel.setPadding(dp(16),dp(8),dp(16),dp(8));
        TextView instruction=text("Select the column order if the file has no headings. Imported quantities start at zero. Your saved counts stay intact.",15,Color.WHITE,false);
        instruction.setPadding(0,0,0,dp(12));
        panel.addView(instruction);
        ScrollView scroll=new ScrollView(this);
        scroll.addView(panel,new ScrollView.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT,ViewGroup.LayoutParams.WRAP_CONTENT));
        AlertDialog dialog=new AlertDialog.Builder(this).setTitle("Existing Price Book Format")
                .setView(scroll)
                .setNegativeButton("CANCEL",(d,w)->prefs().edit().putBoolean(KEY_STORE_SETUP_CATALOG_IMPORT,false).apply()).create();
        for(int i=0;i<choices.length;i++){
            final int selected=i;
            Button choice=button(choices[i],1);
            choice.setAllCaps(false);
            choice.setTextSize(15);
            choice.setSingleLine(false);
            choice.setMinHeight(dp(64));
            choice.setPadding(dp(12),dp(12),dp(12),dp(12));
            LinearLayout.LayoutParams lp=new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT,ViewGroup.LayoutParams.WRAP_CONTENT);
            lp.setMargins(0,0,0,dp(8));
            panel.addView(choice,lp);
            choice.setOnClickListener(v->{
                prefs().edit().putString(KEY_STORE_SETUP_IMPORT_ORDER,orders[selected]).putBoolean(KEY_STORE_SETUP_CATALOG_IMPORT,true).apply();
                dialog.dismiss();
                Intent picker=new Intent(Intent.ACTION_OPEN_DOCUMENT);
                picker.addCategory(Intent.CATEGORY_OPENABLE);
                picker.setType("*/*");
                picker.putExtra(Intent.EXTRA_MIME_TYPES,new String[]{"text/*","application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"});
                startActivityForResult(picker,REQ_IMPORT);
            });
        }
        dialog.show();
    }

'''
old = source[start:end]
assert '.setMessage("Select the column order' in old, "Unexpected price-book dialog source"
path.write_text(source[:start] + replacement + source[end:])
build = Path("app/build.gradle")
config = build.read_text()
assert "versionCode 30258" in config and "versionName '3.0.258'" in config
build.write_text(config.replace("versionCode 30258","versionCode 30259").replace("versionName '3.0.258'","versionName '3.0.259'"))
print("Applied 3.0.259: scrollable price-book format buttons; counting and batch code unchanged.")
