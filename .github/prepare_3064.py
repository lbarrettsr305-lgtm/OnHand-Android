from pathlib import Path
import runpy

# Preserve every working 3.0.63 feature first.
runpy.run_path('.github/prepare_3063.py', run_name='__main__')

p = Path('app/src/main/java/com/iceinventory/onhand/MainActivity.java')
s = p.read_text()

# Advance the visible version number.
s = s.replace('TextView app=text("Onhand Inventory 3.0.63",19,Color.WHITE,true);',
              'TextView app=text("Onhand Inventory 3.0.64",19,Color.WHITE,true);', 1)

# Use the professional black/green/gold iCE barcode-scanner logo.
s = s.replace('logo.setImageResource(R.drawable.ice_onhand_icon);',
              'logo.setImageResource(R.drawable.ice_onhand_logo_3064);', 1)

# Add persistent sort state beside the existing filter state.
old = '    private int filterMode=0;\n'
new = '    private int filterMode=0;\n    private int sortMode=0;\n'
if old not in s:
    raise SystemExit('3.0.64 target missing: filterMode')
s = s.replace(old, new, 1)

# Put a clearly visible Sort control beside Search and Filter.
old = '''        Button filter=button("▼",1);filter.setOnClickListener(v->showFilter());
        searchBar.addView(search,new LinearLayout.LayoutParams(0,dp(46),1));
        LinearLayout.LayoutParams flp=new LinearLayout.LayoutParams(dp(55),dp(46));flp.setMargins(dp(5),0,0,0);
        searchBar.addView(filter,flp);
        root.addView(searchBar);
'''
new = '''        Button sort=button("⇅ Sort",0);sort.setTextSize(12);sort.setOnClickListener(v->showSort());
        Button filter=button("▼",1);filter.setOnClickListener(v->showFilter());
        searchBar.addView(search,new LinearLayout.LayoutParams(0,dp(46),1));
        LinearLayout.LayoutParams slp=new LinearLayout.LayoutParams(dp(78),dp(46));slp.setMargins(dp(5),0,0,0);
        searchBar.addView(sort,slp);
        LinearLayout.LayoutParams flp=new LinearLayout.LayoutParams(dp(50),dp(46));flp.setMargins(dp(4),0,0,0);
        searchBar.addView(filter,flp);
        root.addView(searchBar);
'''
if old not in s:
    raise SystemExit('3.0.64 target missing: search/filter bar')
s = s.replace(old, new, 1)

# Apply sorting after search/filter selection but before handing rows to the adapter.
old = '''        SharedPreferences p=prefs();
        adapter.setDisplayOptions(p.getBoolean(KEY_COMPACT,true),p.getBoolean(KEY_SHOW_IMAGES,true),p.getBoolean(KEY_HIGHLIGHT,true),lastBarcode);
        adapter.setRows(visibleRows);
    }

    private void showFilter() {
'''
new = '''        sortVisibleRows();
        SharedPreferences p=prefs();
        adapter.setDisplayOptions(p.getBoolean(KEY_COMPACT,true),p.getBoolean(KEY_SHOW_IMAGES,true),p.getBoolean(KEY_HIGHLIGHT,true),lastBarcode);
        adapter.setRows(visibleRows);
    }

    private String sortText(String value) {
        return value==null?"":value.trim().toLowerCase(Locale.US);
    }

    private void sortVisibleRows() {
        if(sortMode==0||visibleRows.size()<2)return;
        java.util.Comparator<InventoryDb.Row> c=null;
        if(sortMode==1)c=(a,b)->sortText(a.description).compareTo(sortText(b.description));
        else if(sortMode==2)c=(a,b)->sortText(b.description).compareTo(sortText(a.description));
        else if(sortMode==3)c=(a,b)->sortText(a.barcode).compareTo(sortText(b.barcode));
        else if(sortMode==4)c=(a,b)->Integer.compare(b.quantity,a.quantity);
        else if(sortMode==5)c=(a,b)->Integer.compare(a.quantity,b.quantity);
        else if(sortMode==6)c=(a,b)->{
            int x=sortText(a.location).compareTo(sortText(b.location));
            return x!=0?x:sortText(a.description).compareTo(sortText(b.description));
        };
        else if(sortMode==7)c=(a,b)->Long.compare(b.updatedAt,a.updatedAt);
        if(c!=null)java.util.Collections.sort(visibleRows,c);
    }

    private void showSort() {
        String[] choices={"Default order","Description A–Z","Description Z–A","Barcode","Quantity high to low","Quantity low to high","Location A–Z","Last scanned first"};
        new AlertDialog.Builder(this).setTitle("Sort Items")
                .setSingleChoiceItems(choices,sortMode,(d,w)->{sortMode=w;d.dismiss();applyFilter();})
                .setNegativeButton("Cancel",null).show();
    }

    private void showFilter() {
'''
if old not in s:
    raise SystemExit('3.0.64 target missing: applyFilter adapter block')
s = s.replace(old, new, 1)

p.write_text(s)

# Keep launcher/app-list label and icon synchronized with the visible in-app version.
p = Path('app/src/main/AndroidManifest.xml')
s = p.read_text()
s = s.replace('android:label="iCE Onhand 3.0.63"','android:label="iCE Onhand 3.0.64"',1)
s = s.replace('android:icon="@drawable/ice_onhand_icon"','android:icon="@drawable/ice_onhand_logo_3064"',1)
p.write_text(s)

print('Prepared iCE Onhand 3.0.64: visible version + Sort menu + professional iCE logo')
