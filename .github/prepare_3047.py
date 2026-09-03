from pathlib import Path
import runpy

# Preserve every approved 3.0.46 behavior first.
runpy.run_path('.github/prepare_3046.py', run_name='__main__')

# Add a safe current-inventory Zero All Quantities command under Options.
p=Path('app/src/main/java/com/iceinventory/onhand/MainActivity.java')
s=p.read_text()

old='''        box.addView(optionSwitch("Compact List View",KEY_COMPACT,true));\n        Button unknown=button("Unknown Barcode Behavior: "+friendlyUnknownMode(),0);\n'''
new='''        box.addView(optionSwitch("Compact List View",KEY_COMPACT,true));\n        TextView inventory=text("Inventory",16,gold(),true);inventory.setPadding(dp(6),dp(8),0,dp(2));box.addView(inventory);\n        Button zero=button("Zero All Quantities",0);\n        zero.setOnClickListener(v->confirmZeroAllQuantities());\n        box.addView(zero,new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT,dp(50)));\n        Button unknown=button("Unknown Barcode Behavior: "+friendlyUnknownMode(),0);\n'''
if old not in s: raise SystemExit('3.0.47 target missing: Options controls')
s=s.replace(old,new,1)

marker='''    private String friendlyUnknownMode() {\n'''
method='''    private void confirmZeroAllQuantities() {\n        new AlertDialog.Builder(this)\n                .setTitle("Zero All Quantities?")\n                .setMessage("This sets every quantity in the current inventory to 0. Barcodes, descriptions, prices and locations will remain unchanged.")\n                .setPositiveButton("ZERO ALL",(d,w)->{\n                    int changed=db.zeroAllQuantities(sessionId);\n                    refreshList();\n                    toast("Zeroed quantities for "+changed+" item lines");\n                })\n                .setNegativeButton("Cancel",null)\n                .show();\n    }\n\n'''
if marker not in s: raise SystemExit('3.0.47 target missing: friendlyUnknownMode marker')
s=s.replace(marker,method+marker,1)
p.write_text(s)

# Database helper: zero only quantities in the current inventory session.
p=Path('app/src/main/java/com/iceinventory/onhand/InventoryDb.java')
s=p.read_text()
marker='''    public void setQuantity'''
method='''    public int zeroAllQuantities(long sessionId) {\n        ContentValues cv=new ContentValues();\n        cv.put("quantity",0);\n        return getWritableDatabase().update("items",cv,"session_id=?",new String[]{String.valueOf(sessionId)});\n    }\n\n'''
if marker not in s: raise SystemExit('3.0.47 target missing: setQuantity marker')
s=s.replace(marker,method+marker,1)
p.write_text(s)

print('Prepared iCE Onhand 3.0.47: locked layout + Zero All Quantities + Qty > 0 export option')
