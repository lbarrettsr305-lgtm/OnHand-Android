#!/usr/bin/env python3
from pathlib import Path
import runpy

root = Path(__file__).resolve().parents[1]
runpy.run_path(str(root / ".github" / "prepare_30186.py"), run_name="__main__")

gradle = root / "app" / "build.gradle"
s = gradle.read_text().replace("versionCode 30186", "versionCode 30187").replace("versionName '3.0.186'", "versionName '3.0.187'")
gradle.write_text(s)

manifest = root / "app" / "src" / "main" / "AndroidManifest.xml"
manifest.write_text(manifest.read_text().replace("iCE Onhand 3.0.186", "iCE Onhand 3.0.187"))

main = root / "app" / "src" / "main" / "java" / "com" / "iceinventory" / "onhand" / "MainActivity.java"
s = main.read_text().replace("Onhand Inventory 3.0.186", "Onhand Inventory 3.0.187")

old_adapter_call = '''        adapter.setDisplayOptions(p.getBoolean(KEY_COMPACT,true),p.getBoolean(KEY_SHOW_IMAGES,true),p.getBoolean(KEY_HIGHLIGHT,true),lastBarcode);'''
new_adapter_call = '''        adapter.setDisplayOptions(p.getBoolean(KEY_COMPACT,true),p.getBoolean(KEY_SHOW_IMAGES,true),p.getBoolean(KEY_HIGHLIGHT,true),lastBarcode,confirmedLocationSession==sessionId?confirmedLocation:"");'''
if s.count(old_adapter_call) != 1:
    raise SystemExit("Adapter display options source not found")
s = s.replace(old_adapter_call, new_adapter_call, 1)

old_actions = '''    @Override public void onAddOne(InventoryDb.Row row) {
        if(!requireCurrentCount())return;
        db.incrementQuantity(row.id,1);lastBarcode=row.barcode;refreshList();noteCountForSafety();
    }

    @Override public void onSubtractOne(InventoryDb.Row row) {
        if(!requireCurrentCount())return;
        if(row.quantity<=0)return;
        db.incrementQuantity(row.id,-1);lastBarcode=row.barcode;refreshList();noteCountForSafety();
    }

    @Override public void onEdit(InventoryDb.Row r) {
        if(!requireCurrentCount())return;'''
new_actions = '''    private boolean rowIsAtCurrentLocation(InventoryDb.Row row){
        if(row==null||confirmedLocationSession!=sessionId||confirmedLocation.isEmpty())return false;
        String rowLocation=row.location==null||row.location.trim().isEmpty()?"Main":row.location.trim();
        return rowLocation.equalsIgnoreCase(confirmedLocation);
    }

    private boolean requireRowAtCurrentLocation(InventoryDb.Row row){
        if(rowIsAtCurrentLocation(row))return true;
        String rowLocation=row==null||row.location==null||row.location.trim().isEmpty()?"Main":row.location.trim();
        new AlertDialog.Builder(this).setTitle("PREVIOUS LOCATION — READ ONLY")
            .setMessage("This quantity belongs to "+rowLocation+".\\n\\nYour current counting location is "+(confirmedLocation.isEmpty()?"NOT SET":confirmedLocation)+".\\n\\nTo change this row, first use Change Location and select "+rowLocation+". New counts will remain in the current location.")
            .setPositiveButton("OK",null).show();
        return false;
    }

    @Override public void onAddOne(InventoryDb.Row row) {
        if(!requireCurrentCount()||!requireRowAtCurrentLocation(row))return;
        db.incrementQuantity(row.id,1);lastBarcode=row.barcode;refreshList();noteCountForSafety();
    }

    @Override public void onSubtractOne(InventoryDb.Row row) {
        if(!requireCurrentCount()||!requireRowAtCurrentLocation(row))return;
        if(row.quantity<=0)return;
        db.incrementQuantity(row.id,-1);lastBarcode=row.barcode;refreshList();noteCountForSafety();
    }

    @Override public void onEdit(InventoryDb.Row r) {
        if(!requireCurrentCount()||!requireRowAtCurrentLocation(r))return;'''
if s.count(old_actions) != 1:
    raise SystemExit("Row quantity actions source not found")
s = s.replace(old_actions, new_actions, 1)

old_launch = '''    private void launchQuantity(InventoryDb.Row r) {
        if(!requireCurrentCount())return;'''
new_launch = '''    private void launchQuantity(InventoryDb.Row r) {
        if(!requireCurrentCount()||!requireRowAtCurrentLocation(r))return;'''
if s.count(old_launch) != 1:
    raise SystemExit("Row quantity launcher source not found")
s = s.replace(old_launch, new_launch, 1)
main.write_text(s)

adapter = root / "app" / "src" / "main" / "java" / "com" / "iceinventory" / "onhand" / "InventoryAdapter.java"
a = adapter.read_text()
a = a.replace('''    private String lastBarcode = "";''','''    private String lastBarcode = "";
    private String currentLocation = "";''',1)
old_display = '''    public void setDisplayOptions(boolean compact, boolean showImages, boolean highlightLast, String lastBarcode) {
        this.compact=compact;
        this.showImages=showImages;
        this.highlightLast=highlightLast;
        this.lastBarcode=lastBarcode==null?"":lastBarcode;
        notifyDataSetChanged();
    }'''
new_display = '''    public void setDisplayOptions(boolean compact, boolean showImages, boolean highlightLast, String lastBarcode, String currentLocation) {
        this.compact=compact;
        this.showImages=showImages;
        this.highlightLast=highlightLast;
        this.lastBarcode=lastBarcode==null?"":lastBarcode;
        this.currentLocation=currentLocation==null?"":currentLocation.trim();
        notifyDataSetChanged();
    }'''
if a.count(old_display) != 1:
    raise SystemExit("Inventory adapter options source not found")
a = a.replace(old_display, new_display, 1)
old_active = '''        boolean active=highlightLast && r.barcode!=null && r.barcode.equals(lastBarcode);'''
new_active = '''        String rowLocation=r.location==null||r.location.trim().isEmpty()?"Main":r.location.trim();
        boolean active=highlightLast && r.barcode!=null && r.barcode.equals(lastBarcode) && !currentLocation.isEmpty() && rowLocation.equalsIgnoreCase(currentLocation);'''
if a.count(old_active) != 1:
    raise SystemExit("Inventory active-row source not found")
a = a.replace(old_active, new_active, 1)
adapter.write_text(a)

checks = {
    "version": "versionName '3.0.187'" in gradle.read_text(),
    "row lock": "PREVIOUS LOCATION — READ ONLY" in s and "requireRowAtCurrentLocation" in s,
    "plus protected": "onAddOne(InventoryDb.Row row)" in s and "!requireRowAtCurrentLocation(row)" in s,
    "edit protected": "!requireRowAtCurrentLocation(r)" in s,
    "location highlight": "rowLocation.equalsIgnoreCase(currentLocation)" in a,
}
failed = [name for name, ok in checks.items() if not ok]
if failed:
    raise SystemExit("3.0.187 verification failed: " + ", ".join(failed))
print("Prepared iCE OnHand 3.0.187: prevent previous-location quantity edits while counting elsewhere")
