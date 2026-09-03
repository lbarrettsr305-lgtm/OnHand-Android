from pathlib import Path

p=Path('app/src/main/java/com/iceinventory/onhand/MainActivity.java')
s=p.read_text()

# Keep the active/scanned item description readable above the keyboard.
old='''        description=new EditText(this); description.setSingleLine(true); description.setTextSize(15); description.setHint("Optional item description"); root.addView(description);'''
new='''        description=new EditText(this); description.setSingleLine(true); description.setTextSize(16); description.setHint("Optional item description"); description.setTextColor(Color.BLACK); description.setHintTextColor(Color.rgb(80,80,80)); description.setTypeface(Typeface.create("sans-serif",Typeface.BOLD)); description.setBackgroundColor(Color.rgb(255,248,210)); description.setPadding(dp(10),dp(8),dp(10),dp(8)); root.addView(description);'''
if old not in s: raise SystemExit('main description field block not found')
s=s.replace(old,new,1)

# Highlighted/edited item description should be bold black on the highlighted row.
old='''                TextView desc=new TextView(MainActivity.this); desc.setText(descText); desc.setTextSize(14); desc.setTypeface(Typeface.create("sans-serif",Typeface.BOLD)); desc.setPadding(0,0,0,dp(1));'''
new='''                TextView desc=new TextView(MainActivity.this); desc.setText(descText); desc.setTextSize(14); desc.setTypeface(Typeface.create("sans-serif",Typeface.BOLD)); desc.setTextColor(r.id==highlightedRowId?Color.BLACK:Color.WHITE); desc.setPadding(0,0,0,dp(1));'''
if old not in s: raise SystemExit('list description block not found')
s=s.replace(old,new,1)

# Quantity text on the yellow quantity control must be black for contrast.
old='''                TextView qtyBox=new TextView(MainActivity.this); qtyBox.setText("Qty  "+r.quantity); qtyBox.setTextSize(16); qtyBox.setTypeface(Typeface.create("sans-serif",Typeface.BOLD)); qtyBox.setGravity(Gravity.CENTER); qtyBox.setPadding(dp(14),dp(8),dp(14),dp(8)); qtyBox.setBackgroundColor(r.id==highlightedRowId?Color.rgb(246,197,0):Color.rgb(45,45,45));'''
new='''                TextView qtyBox=new TextView(MainActivity.this); qtyBox.setText("Qty  "+r.quantity); qtyBox.setTextSize(16); qtyBox.setTypeface(Typeface.create("sans-serif",Typeface.BOLD)); qtyBox.setGravity(Gravity.CENTER); qtyBox.setPadding(dp(14),dp(8),dp(14),dp(8)); qtyBox.setBackgroundColor(r.id==highlightedRowId?Color.rgb(246,197,0):Color.rgb(45,45,45)); qtyBox.setTextColor(r.id==highlightedRowId?Color.BLACK:Color.WHITE);'''
if old not in s: raise SystemExit('quantity box block not found')
s=s.replace(old,new,1)

# Keep the quantity dialog's item information visible and do not force the keyboard open.
old='''        AlertDialog dialog=new AlertDialog.Builder(this).setTitle("Add Quantity").setView(scroll).setPositiveButton("Add",null).setNegativeButton("Cancel",null).create();'''
new='''        box.setFocusableInTouchMode(true); box.requestFocus();
        AlertDialog dialog=new AlertDialog.Builder(this).setTitle("Add Quantity").setView(scroll).setPositiveButton("Add",null).setNegativeButton("Cancel",null).create();'''
if old not in s: raise SystemExit('Add Quantity dialog create block not found')
s=s.replace(old,new,1)

p.write_text(s)

b=Path('app/build.gradle')
g=b.read_text().replace('versionCode 30035','versionCode 30036').replace("versionName '3.0.35'","versionName '3.0.36'")
b.write_text(g)
