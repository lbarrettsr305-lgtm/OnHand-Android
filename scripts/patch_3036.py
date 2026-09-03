from pathlib import Path

p=Path('app/src/main/java/com/iceinventory/onhand/MainActivity.java')
s=p.read_text()

# Main description field: bold black text on a light background for visibility above keyboard.
s=s.replace(
    'description=new EditText(this); description.setSingleLine(true); description.setTextSize(15); description.setHint("Optional item description"); root.addView(description);',
    'description=new EditText(this); description.setSingleLine(true); description.setTextSize(16); description.setHint("Optional item description"); description.setTextColor(Color.BLACK); description.setHintTextColor(Color.rgb(80,80,80)); description.setTypeface(Typeface.create("sans-serif",Typeface.BOLD)); description.setBackgroundColor(Color.rgb(255,248,210)); description.setPadding(dp(10),dp(8),dp(10),dp(8)); root.addView(description);',
    1
)

# List item description: always bold; selected/highlighted item is black for maximum contrast.
desc_marker='desc.setTypeface(Typeface.create("sans-serif",Typeface.BOLD));'
if desc_marker in s and 'desc.setTextColor(r.id==highlightedRowId?Color.BLACK:Color.WHITE);' not in s:
    s=s.replace(desc_marker, desc_marker+' desc.setTextColor(r.id==highlightedRowId?Color.BLACK:Color.WHITE);', 1)

# Yellow Qty control: selected yellow text must be black; non-selected dark box stays white.
qty_marker='qtyBox.setBackgroundColor(r.id==highlightedRowId?Color.rgb(246,197,0):Color.rgb(45,45,45));'
if qty_marker in s and 'qtyBox.setTextColor(r.id==highlightedRowId?Color.BLACK:Color.WHITE);' not in s:
    s=s.replace(qty_marker, qty_marker+' qtyBox.setTextColor(r.id==highlightedRowId?Color.BLACK:Color.WHITE);', 1)

# Quantity dialog: keep item header visible and avoid forcing keyboard open on launch.
dialog_marker='AlertDialog dialog=new AlertDialog.Builder(this).setTitle("Add Quantity").setView(scroll).setPositiveButton("Add",null).setNegativeButton("Cancel",null).create();'
if dialog_marker in s and 'box.setFocusableInTouchMode(true); box.requestFocus();' not in s:
    s=s.replace(dialog_marker, 'box.setFocusableInTouchMode(true); box.requestFocus();\n        '+dialog_marker, 1)

p.write_text(s)

b=Path('app/build.gradle')
g=b.read_text().replace('versionCode 30035','versionCode 30036').replace("versionName '3.0.35'","versionName '3.0.36'")
b.write_text(g)
