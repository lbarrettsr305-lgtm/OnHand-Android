#!/usr/bin/env python3
"""OnHand 3.0.232: Victoria customer totals combine all mapped barcodes by item number."""
from pathlib import Path
import runpy
import re

root=Path(__file__).resolve().parent.parent
workflow=root/".github/workflows/build-apk.yml"
w=workflow.read_text()
for new,old,expected in [
    ("Prepare and verify 3.0.232 Victoria item-number alias reconciliation","Prepare and verify 3.0.231 Fleet Feet import and export formats",1),
    (".github/prepare_30232.py",".github/prepare_30231.py",1),
    ("iCE-Onhand-Inventory-3.0.232","iCE-Onhand-Inventory-3.0.231",4),
]:
    if w.count(new)!=expected:raise SystemExit("3.0.232 workflow marker missing: "+new)
    w=w.replace(new,old)
workflow.write_text(w)
runpy.run_path(str(root/".github/prepare_30231.py"),run_name="__main__")
w=workflow.read_text()
for old,new,expected in [
    ("Prepare and verify 3.0.231 Fleet Feet import and export formats","Prepare and verify 3.0.232 Victoria item-number alias reconciliation",1),
    (".github/prepare_30231.py",".github/prepare_30232.py",1),
    ("iCE-Onhand-Inventory-3.0.231","iCE-Onhand-Inventory-3.0.232",4),
]:
    if w.count(old)!=expected:raise SystemExit("3.0.231 workflow marker missing: "+old)
    w=w.replace(old,new)
workflow.write_text(w)

gradle=root/"app/build.gradle";g=gradle.read_text()
if g.count("versionCode 30231")!=1 or g.count("versionName '3.0.231'")!=1:raise SystemExit("Prior Gradle version missing")
gradle.write_text(g.replace("versionCode 30231","versionCode 30232",1).replace("versionName '3.0.231'","versionName '3.0.232'",1))
manifest=root/"app/src/main/AndroidManifest.xml";m=manifest.read_text()
if m.count("iCE Onhand 3.0.231")!=1:raise SystemExit("Prior manifest version missing")
manifest.write_text(m.replace("iCE Onhand 3.0.231","iCE Onhand 3.0.232",1))
main=root/"app/src/main/java/com/iceinventory/onhand/MainActivity.java";s=main.read_text()
if s.count("Onhand Inventory 3.0.231")!=1:raise SystemExit("Prior visible version missing")
main.write_text(s.replace("Onhand Inventory 3.0.231","Onhand Inventory 3.0.232",1))

batch=root/"app/src/main/java/com/iceinventory/onhand/BatchMergeActivity.java"
s=batch.read_text()

def once(old,new,label):
    global s
    if s.count(old)!=1:raise SystemExit(label+" missing or ambiguous: "+str(s.count(old)))
    s=s.replace(old,new,1)

once('''    private final LinkedHashMap<String,VictoriaProduct> victoriaProducts=new LinkedHashMap<>();''',
     '''    private final LinkedHashMap<String,VictoriaProduct> victoriaProducts=new LinkedHashMap<>();
    private final LinkedHashMap<String,String> primaryBarcodeByItem=new LinkedHashMap<>();
    private int victoriaAliasItems=0;
    private double victoriaCustomerTotal=0;
    private int victoriaCustomerRows=0;''',"primary barcode map")

once('''        victoriaProducts.clear();victoriaSourceLoaded=false;victoriaSourceName=displayName(uri);''',
     '''        victoriaProducts.clear();primaryBarcodeByItem.clear();
        victoriaAliasItems=0;victoriaCustomerTotal=0;victoriaCustomerRows=0;
        victoriaSourceLoaded=false;victoriaSourceName=displayName(uri);''',"source reset")

once('''                if(product.itemNumber.isEmpty())product.itemNumber=item;
                String description=descriptionColumn<0?"":clean(cell(values,descriptionColumn));''',
     '''                if(!product.itemNumber.isEmpty()&&!product.itemNumber.equalsIgnoreCase(item))
                    throw new Exception("Conflicting Victoria ITEM NUMBER for barcode "+barcode+": "+product.itemNumber+" versus "+item);
                if(product.itemNumber.isEmpty())product.itemNumber=item;
                String itemKey=itemKey(item);
                if(!primaryBarcodeByItem.containsKey(itemKey))primaryBarcodeByItem.put(itemKey,barcode);
                String description=descriptionColumn<0?"":clean(cell(values,descriptionColumn));''',
     "authoritative Victoria master barcode mappings")

marker='    private void chooseFiles(){'
helper='''    private String itemKey(String item){
        return item==null?"":item.trim().toUpperCase(Locale.US);
    }

    /**
     * Customer file groups scanned barcode/location quantities by ORIGINAL
     * Victoria ITEM NUMBER. The barcode sent to the customer is the first
     * barcode for this Item Number in their original master workbook.
     * Barcode/location rows remain untouched in combined and location audit.
     */
    private LinkedHashMap<String,VictoriaCustomerXlsxWriter.Row> groupVictoriaByItem(){
        LinkedHashMap<String,VictoriaCustomerXlsxWriter.Row> items=new LinkedHashMap<>();
        for(Total counted:combined.values()){
            String key=itemKey(counted.itemNumber);
            if(key.isEmpty())throw new IllegalStateException("Unmapped counted barcode "+counted.barcode);
            String primary=primaryBarcodeByItem.get(key);
            if(primary==null||primary.isEmpty())
                throw new IllegalStateException("No original Victoria master barcode for Item Number "+counted.itemNumber);
            VictoriaCustomerXlsxWriter.Row row=items.get(key);
            if(row==null){
                row=new VictoriaCustomerXlsxWriter.Row();
                row.itemNumber=counted.itemNumber;
                row.barcode=primary;
                VictoriaProduct source=victoriaProducts.get(primary);
                row.description=source!=null&&!source.description.isEmpty()?source.description:counted.description;
                items.put(key,row);
            }
            row.quantity+=counted.quantity;
        }
        return items;
    }

    private LinkedHashMap<String,LinkedHashMap<String,Double>> victoriaItemBarcodeAudit(){
        LinkedHashMap<String,LinkedHashMap<String,Double>> byItem=new LinkedHashMap<>();
        for(Total counted:combined.values()){
            String key=itemKey(counted.itemNumber);
            if(key.isEmpty())continue;
            LinkedHashMap<String,Double> barcodes=byItem.get(key);
            if(barcodes==null){barcodes=new LinkedHashMap<>();byItem.put(key,barcodes);}
            String barcode=normalizeBarcode(counted.barcode);
            barcodes.put(barcode,barcodes.getOrDefault(barcode,0d)+counted.quantity);
        }
        return byItem;
    }

'''
once(marker,helper+marker,"item grouping helper")

old='''        verified=errors.isEmpty()&&victoriaSourceLoaded&&sourceFiles==candidateFiles&&candidateFiles>0&&QuantityMath.equal(sourceGrandTotal,outputTotal)&&QuantityMath.equal(sourceGrandTotal,locationGrandTotal);'''
new='''        victoriaCustomerTotal=0;victoriaCustomerRows=0;victoriaAliasItems=0;
        if(errors.isEmpty()){
            try{
                LinkedHashMap<String,VictoriaCustomerXlsxWriter.Row> rows=groupVictoriaByItem();
                victoriaCustomerRows=rows.size();
                for(VictoriaCustomerXlsxWriter.Row row:rows.values())victoriaCustomerTotal+=row.quantity;
                for(LinkedHashMap<String,Double> barcodes:victoriaItemBarcodeAudit().values())
                    if(barcodes.size()>1)victoriaAliasItems++;
                if(!QuantityMath.equal(sourceGrandTotal,victoriaCustomerTotal))
                    errors.add("Victoria customer ITEM NUMBER totals do not balance to source count: "+QuantityMath.format(victoriaCustomerTotal));
            }catch(Exception e){errors.add("Customer grouping failed: "+e.getMessage());}
        }
        verified=errors.isEmpty()&&victoriaSourceLoaded&&sourceFiles==candidateFiles&&candidateFiles>0
                &&QuantityMath.equal(sourceGrandTotal,outputTotal)
                &&QuantityMath.equal(sourceGrandTotal,locationGrandTotal)
                &&QuantityMath.equal(sourceGrandTotal,victoriaCustomerTotal);'''
once(old,new,"three/four-way source to customer reconciliation")
old='''        StringBuilder s=new StringBuilder();s.append("Original Victoria Excel: ").append(victoriaSourceName).append(" — ").append(victoriaProducts.size()).append(" products\\n");'''
new='''        StringBuilder s=new StringBuilder();
        s.append("VICTORIA CUSTOMER FILE: GROUP BY ITEM NUMBER\\n");
        s.append("Original Victoria Excel: ").append(victoriaSourceName).append(" — ").append(victoriaProducts.size()).append(" barcodes\\n");
        s.append("Customer unique item numbers: ").append(victoriaCustomerRows).append("\\n");
        s.append("Items with more than one counted barcode: ").append(victoriaAliasItems).append("\\n");
        s.append("Customer grouped QTY: ").append(QuantityMath.format(victoriaCustomerTotal)).append("\\n");'''
once(old,new,"Victoria status explanation")

# Require explicit confirmation if alternative barcodes will be consolidated.
old='''    private void saveCombined(){if(!verified)return;Intent i=new Intent(Intent.ACTION_CREATE_DOCUMENT);i.addCategory(Intent.CATEGORY_OPENABLE);i.setType("application/vnd.openxmlformats-officedocument.spreadsheetml.sheet");i.putExtra(Intent.EXTRA_TITLE,combinedOutputName("VICTORIA CUSTOMER REPORT",sourceInventoryName()+".xlsx"));startActivityForResult(i,REQ_SAVE);}'''
new='''    private void saveCombined(){
        if(!verified)return;
        if(victoriaAliasItems>0){
            new AlertDialog.Builder(this)
                .setTitle("Victoria: combined barcode aliases")
                .setMessage(victoriaAliasItems+" ITEM NUMBER(s) have multiple counted barcodes. The customer Excel will have ONE line per ITEM NUMBER. Its BARCODE will be the first matching barcode from the original Victoria Excel, and the QTY will include every counted barcode and location. Review the Verification Report for alias details. Continue?")
                .setNegativeButton("CANCEL",null)
                .setPositiveButton("EXPORT GROUPED TOTALS",(d,w)->beginVictoriaCustomerExport())
                .show();
        }else beginVictoriaCustomerExport();
    }

    private void beginVictoriaCustomerExport(){
        Intent i=new Intent(Intent.ACTION_CREATE_DOCUMENT);
        i.addCategory(Intent.CATEGORY_OPENABLE);
        i.setType("application/vnd.openxmlformats-officedocument.spreadsheetml.sheet");
        i.putExtra(Intent.EXTRA_TITLE,combinedOutputName("VICTORIA CUSTOMER REPORT",sourceInventoryName()+".xlsx"));
        startActivityForResult(i,REQ_SAVE);
    }'''
once(old,new,"confirmation before consolidation")

old='''            LinkedHashMap<String,VictoriaCustomerXlsxWriter.Row> customer=new LinkedHashMap<>();
            for(Total t:combined.values()){
                String key=normalizeBarcode(t.barcode);VictoriaCustomerXlsxWriter.Row row=customer.get(key);
                if(row==null){row=new VictoriaCustomerXlsxWriter.Row();row.barcode=t.barcode;row.description=t.description;row.itemNumber=t.itemNumber;customer.put(key,row);}
                row.quantity+=t.quantity;
            }
            VictoriaCustomerXlsxWriter.write(os,new java.util.ArrayList<>(customer.values()));'''
new='''            LinkedHashMap<String,VictoriaCustomerXlsxWriter.Row> customer=groupVictoriaByItem();
            double customerQty=0;
            for(VictoriaCustomerXlsxWriter.Row row:customer.values())customerQty+=row.quantity;
            if(!QuantityMath.equal(sourceGrandTotal,customerQty)
                    ||!QuantityMath.equal(locationGrandTotal,customerQty))
                throw new Exception("BLOCKED: Victoria customer QTY does not balance with batches and locations");
            VictoriaCustomerXlsxWriter.write(os,new java.util.ArrayList<>(customer.values()));'''
once(old,new,"Victoria customer writer grouping")

start=s.find("    private String buildVerificationReport(){")
end=s.find("\n    private ",start+7)
if start<0 or end<0:raise SystemExit("Verification report method boundaries missing")
report=s[start:end]
anchor='        return b.toString();'
if report.count(anchor)!=1:raise SystemExit("Verification report return anchor missing")
extra='''        b.append("\\r\\nVICTORIA ITEM NUMBER / BARCODE ALIAS AUDIT\\r\\n");
        b.append("Customer lines are grouped by ITEM NUMBER, not by barcode.\\r\\n");
        b.append("Customer grouped quantity\\t").append(QuantityMath.format(victoriaCustomerTotal)).append("\\r\\n");
        b.append("Source / customer difference\\t").append(QuantityMath.format(sourceGrandTotal-victoriaCustomerTotal)).append("\\r\\n");
        b.append("Multiple-barcode item numbers\\t").append(victoriaAliasItems).append("\\r\\n");
        b.append("ITEM NUMBER\\tCUSTOMER PRIMARY BARCODE\\tCOUNTED BARCODE\\tCOUNTED QTY\\r\\n");
        for(Map.Entry<String,LinkedHashMap<String,Double>> entry:victoriaItemBarcodeAudit().entrySet()){
            String primary=primaryBarcodeByItem.get(entry.getKey());
            for(Map.Entry<String,Double> alias:entry.getValue().entrySet()){
                b.append(clean(entry.getKey())).append('\\t').append(clean(primary)).append('\\t')
                    .append(clean(alias.getKey())).append('\\t')
                    .append(QuantityMath.format(alias.getValue())).append("\\r\\n");
            }
        }
        b.append("IMPORTANT: Final customer workbook totals are checked by ITEM NUMBER.\\r\\n");
'''
report=report.replace(anchor,extra+anchor,1)
s=s[:start]+report+s[end:]
batch.write_text(s)

checks={
    "version": "versionName '3.0.232'" in gradle.read_text() and "iCE Onhand 3.0.232" in manifest.read_text() and "Onhand Inventory 3.0.232" in main.read_text(),
    "master crosswalk": "primaryBarcodeByItem.put(itemKey,barcode)" in s,
    "conflicting item mapping blocks": "Conflicting Victoria ITEM NUMBER for barcode" in s,
    "customer groups by item": "LinkedHashMap<String,VictoriaCustomerXlsxWriter.Row> groupVictoriaByItem()" in s,
    "alias calculation": "if(barcodes.size()>1)victoriaAliasItems++" in s,
    "final workbook grouped": "customer=groupVictoriaByItem()" in s and "customerQty+=row.quantity" in s,
    "customer totals checked": "QuantityMath.equal(sourceGrandTotal,victoriaCustomerTotal)" in s and "QuantityMath.equal(locationGrandTotal,customerQty)" in s,
    "audit shows aliases": "VICTORIA ITEM NUMBER / BARCODE ALIAS AUDIT" in s,
    "user confirmation": "EXPORT GROUPED TOTALS" in s,
    "master and user batches preserved": "readOne(Uri uri)" in s and "String key=code+" in s,
    "Fleet Feet export remains": 'new String[]{"quantity","barcode","description","item_number","size"}' in (root/"app/src/main/java/com/iceinventory/onhand/FormatConfigActivity.java").read_text(),
    "workflow": ".github/prepare_30232.py" in workflow.read_text() and "3.0.232" in workflow.read_text(),
}
failed=[key for key,value in checks.items() if not value]
if failed:raise SystemExit("3.0.232 validation failed: "+", ".join(failed))
print("Prepared OnHand 3.0.232: Victoria sums quantities by Item Number across all counted barcodes, reconciles totals and writes alias audit.")
