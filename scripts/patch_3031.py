from pathlib import Path

p=Path('app/src/main/java/com/iceinventory/onhand/MainActivity.java')
s=p.read_text()

# Persist list sorting preference. Database currently returns last-updated first.
s=s.replace('private static final String KEY_AUTO_GTIN="auto_gtin14";','private static final String KEY_AUTO_GTIN="auto_gtin14";\n    private static final String KEY_SORT_LAST="sort_last_entry_first";')
s=s.replace('private boolean isAutoGtin(){ return prefs().getBoolean(KEY_AUTO_GTIN,false); }','private boolean isAutoGtin(){ return prefs().getBoolean(KEY_AUTO_GTIN,false); }\n    private boolean isSortLastFirst(){ return prefs().getBoolean(KEY_SORT_LAST,true); }')

# Add sort selector to Options.
old='''        CheckBox auto=new CheckBox(this); auto.setText("Automatically convert valid scans to GTIN-14"); auto.setChecked(isAutoGtin()); box.addView(auto);
        TextView unknown=label("Unknown barcode behavior");'''
new='''        CheckBox auto=new CheckBox(this); auto.setText("Automatically convert valid scans to GTIN-14"); auto.setChecked(isAutoGtin()); box.addView(auto);
        TextView sortLabel=label("Inventory list sort"); sortLabel.setPadding(0,dp(8),0,0); box.addView(sortLabel);
        RadioGroup sortGroup=new RadioGroup(this); RadioButton lastFirst=new RadioButton(this); lastFirst.setText("Last Entry First"); lastFirst.setId(610); RadioButton normalOrder=new RadioButton(this); normalOrder.setText("Normal Order"); normalOrder.setId(611); sortGroup.addView(lastFirst); sortGroup.addView(normalOrder); sortGroup.check(isSortLastFirst()?610:611); box.addView(sortGroup);
        TextView unknown=label("Unknown barcode behavior");'''
if old not in s: raise SystemExit('options insertion point not found')
s=s.replace(old,new,1)
oldsave='''            prefs().edit().putBoolean(KEY_AUTO_GTIN,auto.isChecked()).putString(KEY_UNKNOWN_MODE,selected).apply();
            toast(auto.isChecked()?"Options saved • Auto GTIN on":"Options saved");'''
newsave='''            prefs().edit().putBoolean(KEY_AUTO_GTIN,auto.isChecked()).putBoolean(KEY_SORT_LAST,sortGroup.getCheckedRadioButtonId()==610).putString(KEY_UNKNOWN_MODE,selected).apply();
            refreshList();
            toast(auto.isChecked()?"Options saved • Auto GTIN on":"Options saved");'''
if oldsave not in s: raise SystemExit('options save point not found')
s=s.replace(oldsave,newsave,1)

# Restore fast +1 by tapping the description.
needle='''                row.addView(desc);'''
replacement='''                desc.setOnClickListener(v->{ highlightedRowId=r.id; db.incrementItem(r.id,1); refreshList(); toast("Quantity +1"); });
                row.addView(desc);'''
if needle not in s: raise SystemExit('description row point not found')
s=s.replace(needle,replacement,1)

# Normal order is the reverse of the database's last-updated-first list.
oldrefresh='''        visibleRows.clear(); visibleRows.addAll(db.items(sessionId)); ArrayList<String> lines=new ArrayList<>(); int units=0;'''
newrefresh='''        visibleRows.clear(); visibleRows.addAll(db.items(sessionId)); if(!isSortLastFirst()) java.util.Collections.reverse(visibleRows); ArrayList<String> lines=new ArrayList<>(); int units=0;'''
if oldrefresh not in s: raise SystemExit('refresh sort point not found')
s=s.replace(oldrefresh,newrefresh,1)
p.write_text(s)

b=Path('app/build.gradle')
g=b.read_text().replace('versionCode 30030','versionCode 30031').replace("versionName '3.0.30'","versionName '3.0.31'")
b.write_text(g)
