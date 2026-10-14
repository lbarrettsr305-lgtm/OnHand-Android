#!/usr/bin/env python3
"""3.0.234: independent Fleet Feet customer import file, BARCODE,QTY without headers."""
from pathlib import Path
import runpy,re
root=Path(__file__).resolve().parent.parent
workflow=root/".github/workflows/build-apk.yml"
w=workflow.read_text()
for new,old,count in [
 ("Prepare and verify 3.0.234 Fleet Feet headerless Barcode Qty customer report","Prepare and verify 3.0.233 recurring Fleet Feet RGIS customer import",1),
 (".github/prepare_30234.py",".github/prepare_30233.py",1),
 ("iCE-Onhand-Inventory-3.0.234","iCE-Onhand-Inventory-3.0.233",4)
]:
    if w.count(new)!=count:raise SystemExit("Workflow 3.0.234 marker absent: "+new)
    w=w.replace(new,old)
workflow.write_text(w)
runpy.run_path(str(root/".github/prepare_30233.py"),run_name="__main__")
w=workflow.read_text()
for old,new,count in [
 ("Prepare and verify 3.0.233 recurring Fleet Feet RGIS customer import","Prepare and verify 3.0.234 Fleet Feet headerless Barcode Qty customer report",1),
 (".github/prepare_30233.py",".github/prepare_30234.py",1),
 ("iCE-Onhand-Inventory-3.0.233","iCE-Onhand-Inventory-3.0.234",4)
]:
    if w.count(old)!=count:raise SystemExit("Workflow 3.0.233 restoration error: "+old)
    w=w.replace(old,new)
workflow.write_text(w)
g=root/"app/build.gradle";gradle=g.read_text()
if gradle.count("versionCode 30233")!=1 or gradle.count("versionName '3.0.233'")!=1:raise SystemExit("Gradle prior version missing")
g.write_text(gradle.replace("versionCode 30233","versionCode 30234",1).replace("versionName '3.0.233'","versionName '3.0.234'",1))
manifest=root/"app/src/main/AndroidManifest.xml";m=manifest.read_text()
if m.count("iCE Onhand 3.0.233")!=1:raise SystemExit("Manifest prior version missing")
manifest.write_text(m.replace("iCE Onhand 3.0.233","iCE Onhand 3.0.234",1))
main=root/"app/src/main/java/com/iceinventory/onhand/MainActivity.java"
s=main.read_text()
if s.count("Onhand Inventory 3.0.233")!=1:raise SystemExit("Main version missing")
s=s.replace("Onhand Inventory 3.0.233","Onhand Inventory 3.0.234",1)

old='        addExportSection(exportPanel,"INVENTORY EXPORTS");'
new='''        addExportSection(exportPanel,"FLEET FEET — CLIENT IMPORT");
        addExportButton(exportPanel,exportDialog,"Fleet Feet Client — Barcode + Qty (No Headers)",20);
        addExportSection(exportPanel,"INVENTORY EXPORTS");'''
if s.count(old)!=1:raise SystemExit("Export section anchor missing")
s=s.replace(old,new,1)
match=re.search(r'    private void handleExportChoice\(int which\)\s*\{',s)
if not match:raise SystemExit("Export choice method missing")
s=s[:match.end()]+'\n        if(which==20){showFleetFeetClientExportOptions();return;}'+s[match.end():]

extra=r'''    private boolean fleetFeetIncludeZeroQty=false;
    private void showFleetFeetClientExportOptions(){
        if(allRows==null||allRows.isEmpty()){
            toast("No active inventory. Import the Fleet Feet file and count first.");return;
        }
        new AlertDialog.Builder(this)
            .setTitle("Fleet Feet — Client Import")
            .setMessage("The client receives BARCODE,QTY ONLY: comma-separated TXT with NO HEADERS. All locations are added by barcode. Upload/merge every user's counts before final export. All regular Batch, Location, TXT, and Excel reports remain available.\n\nSelect whether to include products with zero quantity.")
            .setPositiveButton("COUNTED ITEMS ONLY",(d,w)->startFleetFeetClientExport(false))
            .setNeutralButton("INCLUDE ZERO-QTY ITEMS",(d,w)->startFleetFeetClientExport(true))
            .setNegativeButton("CANCEL",null).show();
    }

    private void startFleetFeetClientExport(boolean includeZeroQty){
        fleetFeetIncludeZeroQty=includeZeroQty;
        Intent i=new Intent(Intent.ACTION_CREATE_DOCUMENT);
        i.addCategory(Intent.CATEGORY_OPENABLE);
        i.setType("text/plain");
        i.putExtra(Intent.EXTRA_TITLE,safeFilePart(sessionName)+"-FLEETFEET-BARCODE-QTY.txt");
        startActivityForResult(i,7985);
    }

    private void writeFleetFeetClientExport(Uri uri){
        if(uri==null)return;
        try{
            java.util.LinkedHashMap<String,Double> byBarcode=new java.util.LinkedHashMap<>();
            double sourceQty=0;
            for(InventoryDb.Row row:allRows){
                String barcode=row.barcode==null?"":row.barcode.trim();
                if(barcode.isEmpty())continue;
                if(barcode.indexOf(',')>=0||barcode.indexOf('\t')>=0||barcode.indexOf('\n')>=0)
                    throw new IllegalArgumentException("Customer barcode contains invalid separator: "+barcode);
                byBarcode.put(barcode,byBarcode.getOrDefault(barcode,0d)+row.quantity);
                sourceQty+=row.quantity;
            }
            if(byBarcode.isEmpty())throw new IllegalStateException("No barcodes in active inventory.");
            StringBuilder text=new StringBuilder(byBarcode.size()*20);
            double outputQty=0;int count=0;
            for(java.util.Map.Entry<String,Double> entry:byBarcode.entrySet()){
                double quantity=entry.getValue();
                if(quantity < -0.0000001)
                    throw new IllegalStateException("Negative inventory QTY for "+entry.getKey()+". Fix the count before client export.");
                if(!fleetFeetIncludeZeroQty && quantity<=0)continue;
                text.append(entry.getKey()).append(',').append(QuantityMath.format(quantity)).append("\r\n");
                outputQty+=quantity;count++;
            }
            if(count==0)throw new IllegalStateException("There are no counted products; select Include Zero-Qty Items if required.");
            if(Math.abs(sourceQty-outputQty)>0.000001)
                throw new IllegalStateException("Customer barcode quantities do not match the active inventory.");
            try(java.io.OutputStream out=getContentResolver().openOutputStream(uri)){
                if(out==null)throw new IllegalStateException("Cannot create customer file.");
                out.write(text.toString().getBytes(java.nio.charset.StandardCharsets.UTF_8));
            }
            new AlertDialog.Builder(this).setTitle("Fleet Feet customer file saved")
                .setMessage(count+" BARCODE rows saved, total QTY: "+QuantityMath.format(outputQty)+
                    "\n\nExactly 2 columns: BARCODE,QTY. NO HEADERS. Location counts are combined. Other reports remain unchanged.")
                .setPositiveButton("OK",null).show();
        }catch(Exception e){showError("Fleet Feet customer export failed",e);}
    }

'''
anchor='    private void showOptions()'
if s.count(anchor)!=1:raise SystemExit("Options method anchor missing")
s=s.replace(anchor,extra+anchor,1)
match=re.search(r'@Override\s+protected void onActivityResult\([^)]*\)\s*\{',s)
if not match:raise SystemExit("onActivityResult insertion anchor missing")
s=s[:match.end()]+'''
        if(requestCode==7985){
            if(resultCode==RESULT_OK && data!=null)writeFleetFeetClientExport(data.getData());
            return;
        }
'''+s[match.end():]
main.write_text(s)
checks={
    "version": "versionName '3.0.234'" in g.read_text() and "iCE Onhand 3.0.234" in manifest.read_text() and "Onhand Inventory 3.0.234" in main.read_text(),
    "Fleet import unchanged": "parseFleetFeetOriginalLine" in main.read_text(),
    "two-column headerless": 'text.append(entry.getKey()).append(\\',\\').append(QuantityMath.format(quantity))' in main.read_text(),
    "totals by barcode": "byBarcode.put(barcode,byBarcode.getOrDefault(barcode,0d)+row.quantity)" in main.read_text(),
    "counted vs zeros choice": "COUNTED ITEMS ONLY" in main.read_text() and "INCLUDE ZERO-QTY ITEMS" in main.read_text(),
    "no effect on detailed reports": "Fleet Feet Client — Barcode + Qty (No Headers)" in main.read_text() and "Export New Counts" in main.read_text(),
    "workflow": ".github/prepare_30234.py" in workflow.read_text() and "3.0.234" in workflow.read_text(),
}
bad=[k for k,v in checks.items() if not v]
if bad:raise SystemExit("3.0.234 checks failed: "+", ".join(bad))
print("Prepared OnHand 3.0.234: Fleet Feet headerless BARCODE,QTY customer TXT with independent regular reports.")
