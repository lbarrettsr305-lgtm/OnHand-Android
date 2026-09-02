from pathlib import Path

p=Path('app/src/main/java/com/iceinventory/onhand/MainActivity.java')
s=p.read_text()

# Hardware barcode scanners should work no matter which control currently has focus.
field_anchor='    private final ArrayList<InventoryDb.Row> visibleRows=new ArrayList<>();\n'
fields='''    private final StringBuilder hardwareScanBuffer=new StringBuilder();\n    private long hardwareScanLastMs=0L;\n'''
if fields not in s:
    if field_anchor not in s: raise SystemExit('scanner field anchor not found')
    s=s.replace(field_anchor, field_anchor+fields)

method_anchor='    private void showGtinConversion() {'
method='''    @Override public boolean dispatchKeyEvent(KeyEvent event) {\n        // Bluetooth/USB barcode scanners behave like physical keyboards. Capture their\n        // keystrokes at the Activity level so the barcode field never needs focus.\n        if(event!=null && event.getAction()==KeyEvent.ACTION_DOWN && event.getDeviceId()!=-1){\n            int key=event.getKeyCode();\n            if(key==KeyEvent.KEYCODE_ENTER || key==KeyEvent.KEYCODE_NUMPAD_ENTER || key==KeyEvent.KEYCODE_TAB){\n                if(hardwareScanBuffer.length()>0){\n                    String scanned=hardwareScanBuffer.toString();\n                    hardwareScanBuffer.setLength(0);\n                    hardwareScanLastMs=0L;\n                    handleScannedBarcode(scanned);\n                    return true;\n                }\n            }\n            int unicode=event.getUnicodeChar();\n            if(unicode>=32 && unicode!=127){\n                long now=System.currentTimeMillis();\n                if(hardwareScanLastMs==0L || now-hardwareScanLastMs>350L){\n                    hardwareScanBuffer.setLength(0);\n                    // A new hardware scan always replaces anything left in the scan box.\n                    if(barcode!=null) barcode.setText(\"\");\n                }\n                hardwareScanBuffer.append((char)unicode);\n                hardwareScanLastMs=now;\n                if(barcode!=null){\n                    barcode.setText(hardwareScanBuffer.toString());\n                    barcode.setSelection(barcode.length());\n                }\n                return true;\n            }\n        }\n        return super.dispatchKeyEvent(event);\n    }\n\n'''
if method not in s:
    if method_anchor not in s: raise SystemExit('GTIN method anchor not found')
    s=s.replace(method_anchor, method+method_anchor)

# Make the entire item row a large +1 target. Long press still opens Edit Count.
old='''                row.setOnLongClickListener(v->{editRow(position);return true;});\n                return row;\n'''
new='''                row.setOnClickListener(v->{ highlightedRowId=r.id; db.incrementItem(r.id,1); refreshList(); toast(\"Quantity +1\"); });\n                row.setOnLongClickListener(v->{editRow(position);return true;});\n                return row;\n'''
if old not in s: raise SystemExit('row click anchor not found')
s=s.replace(old,new,1)

old_list='list.setAdapter(listAdapter); list.setOnItemClickListener((p,v,pos,id)->editRow(pos));'
new_list='list.setAdapter(listAdapter); list.setOnItemClickListener((p,v,pos,id)->{ if(pos>=0&&pos<visibleRows.size()){ InventoryDb.Row r=visibleRows.get(pos); highlightedRowId=r.id; db.incrementItem(r.id,1); refreshList(); toast("Quantity +1"); }});'
if old_list not in s: raise SystemExit('list click anchor not found')
s=s.replace(old_list,new_list,1)

p.write_text(s)

b=Path('app/build.gradle')
g=b.read_text().replace('versionCode 30025','versionCode 30026').replace("versionName '3.0.25'","versionName '3.0.26'")
g=g.replace('versionCode 30024','versionCode 30026').replace("versionName '3.0.24'","versionName '3.0.26'")
g=g.replace('versionCode 30023','versionCode 30026').replace("versionName '3.0.23'","versionName '3.0.26'")
b.write_text(g)
