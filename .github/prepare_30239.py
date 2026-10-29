#!/usr/bin/env python3
"""OnHand 3.0.239: Victoria QTY/UPC/description/item import and grouped customer export."""
from pathlib import Path
import runpy
import os

root=Path(__file__).resolve().parents[1]
workflow=root/".github/workflows/build-apk.yml"
w=workflow.read_text()
for new,old,expected in [
    ("Prepare and verify 3.0.239 Victoria item-number import and customer export",
     "Prepare and verify 3.0.238 Victoria Coffee locations and floor plan",1),
    (".github/prepare_30239.py", ".github/prepare_30238.py",1),
    ("iCE-Onhand-Inventory-3.0.239", "iCE-Onhand-Inventory-3.0.238",4),
]:
    if w.count(new)!=expected: raise SystemExit("3.0.239 workflow marker missing: "+new)
    w=w.replace(new,old)
workflow.write_text(w)
if os.environ.get("ONHAND_PREPARED_30238")!="1":
    runpy.run_path(str(root/".github/prepare_30238.py"),run_name="__main__")
w=workflow.read_text()
for old,new,expected in [
    ("Prepare and verify 3.0.238 Victoria Coffee locations and floor plan",
     "Prepare and verify 3.0.239 Victoria item-number import and customer export",1),
    (".github/prepare_30238.py", ".github/prepare_30239.py",1),
    ("iCE-Onhand-Inventory-3.0.238", "iCE-Onhand-Inventory-3.0.239",4),
]:
    if w.count(old)!=expected: raise SystemExit("3.0.238 workflow restore marker missing: "+old)
    w=w.replace(old,new)
workflow.write_text(w)

gradle=root/"app/build.gradle"; g=gradle.read_text()
if g.count("versionCode 30238")!=1 or g.count("versionName '3.0.238'")!=1: raise SystemExit("Gradle 3.0.238 marker missing")
gradle.write_text(g.replace("versionCode 30238","versionCode 30239",1).replace("versionName '3.0.238'","versionName '3.0.239'",1))
manifest=root/"app/src/main/AndroidManifest.xml"; m=manifest.read_text()
if m.count("iCE Onhand 3.0.238")!=1: raise SystemExit("manifest 3.0.238 marker missing")
manifest.write_text(m.replace("iCE Onhand 3.0.238","iCE Onhand 3.0.239",1))

main=root/"app/src/main/java/com/iceinventory/onhand/MainActivity.java"; s=main.read_text()
def once(text,old,new,label):
    count=text.count(old)
    if count!=1: raise SystemExit(label+" anchor mismatch: "+str(count))
    return text.replace(old,new,1)
s=once(s,"Onhand Inventory 3.0.238","Onhand Inventory 3.0.239","app version")
s=once(s,"VICTORIA\\nQty • Barcode • Description • Item Number • Location",
          "VICTORIA\\nQTY • UPC • DESCRIPTION\\nITEM #","Victoria import preset label")
s=once(s,'"quantity,barcode,description,item_number,location"',
          '"quantity,barcode,description,item_number"',"Victoria import column order")
s=once(s,'findHeader(first,"item number","item no","item #","sku")',
          'findHeader(first,"item number","item num","item no","item #","sku")',
          "ITEM-NUM header recognition")
s=once(s,"choice.setSingleLine(false);choice.setMaxLines(2);choice.setGravity(Gravity.CENTER);",
          "choice.setSingleLine(false);choice.setMaxLines(3);choice.setTextSize(13);choice.setGravity(Gravity.CENTER);",
          "Victoria preset button layout")
s=once(s,"LinearLayout.LayoutParams lp=new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT,dp(64));\n            lp.setMargins(0,0,0,dp(6));choices.addView(choice,lp);",
          "LinearLayout.LayoutParams lp=new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT,dp(72));\n            lp.setMargins(0,0,0,dp(6));choices.addView(choice,lp);",
          "Victoria preset button height")
main.write_text(s)

config=root/"app/src/main/java/com/iceinventory/onhand/FormatConfigActivity.java"; s=config.read_text()
s=once(s,'?new String[]{"quantity","barcode","description","item_number","location"}',
          '?new String[]{"quantity","barcode","description","item_number"}',
          "saved Victoria import preset")
config.write_text(s)

writer=root/"app/src/main/java/com/iceinventory/onhand/VictoriaCustomerXlsxWriter.java"
s=writer.read_text()
s=once(s,"import java.util.List;","import java.util.List;\nimport java.util.LinkedHashSet;","writer imports")
s=once(s,'public static final class Row { public double quantity; public String barcode="",description="",itemNumber=""; }',
          'public static final class Row { public double quantity; public final LinkedHashSet<String> barcodes=new LinkedHashSet<>(); public String description="",itemNumber=""; }',"customer row shape")
s=once(s,'data.append("<row r=\\\"1\\\">");text(data,"A1","QTY",1);text(data,"B1","BARCODE",1);text(data,"C1","DESCRIPTION",1);text(data,"D1","ITEM NUMBER",1);data.append("</row>");r++;',
          'data.append("<row r=\\\"1\\\">");text(data,"A1","QTY",1);text(data,"B1","ITEM NUMBER",1);text(data,"C1","UPC",1);text(data,"D1","DESCRIPTION",1);data.append("</row>");r++;',"customer headers")
s=once(s,'for(Row row:rows){data.append("<row r=\\\"").append(r).append("\\\">");number(data,"A"+r,row.quantity);text(data,"B"+r,row.barcode,0);text(data,"C"+r,row.description,0);text(data,"D"+r,row.itemNumber,0);data.append("</row>");r++;}',
          'for(Row row:rows){data.append("<row r=\\\"").append(r).append("\\\">");number(data,"A"+r,row.quantity);text(data,"B"+r,row.itemNumber,0);text(data,"C"+r,joinedBarcodes(row.barcodes),0);text(data,"D"+r,row.description,0);data.append("</row>");r++;}',"customer columns")
s=once(s,'<col min=\\"2\\" max=\\"2\\" width=\\"22\\" customWidth=\\"1\\"/><col min=\\"3\\" max=\\"3\\" width=\\"55\\" customWidth=\\"1\\"/><col min=\\"4\\" max=\\"4\\" width=\\"20\\" customWidth=\\"1\\"/>',
          '<col min=\\"2\\" max=\\"2\\" width=\\"20\\" customWidth=\\"1\\"/><col min=\\"3\\" max=\\"3\\" width=\\"32\\" customWidth=\\"1\\"/><col min=\\"4\\" max=\\"4\\" width=\\"55\\" customWidth=\\"1\\"/>',
          "customer column widths")
s=once(s,'    private static void text(StringBuilder b,String ref,String value,int style){',
          '    private static String joinedBarcodes(LinkedHashSet<String> barcodes){StringBuilder out=new StringBuilder();for(String barcode:barcodes){if(out.length()>0)out.append(", ");out.append(barcode);}return out.toString();}\n    private static void text(StringBuilder b,String ref,String value,int style){',"UPC join helper")
writer.write_text(s)

merge=root/"app/src/main/java/com/iceinventory/onhand/BatchMergeActivity.java"; s=merge.read_text()
s=once(s,"Onhand Inventory 3.0.238","Onhand Inventory 3.0.239","Batch merge version") if "Onhand Inventory 3.0.238" in s else s
s=once(s,'findExcel(headers,"new item number","item number","item-number","itemnumber","sku")',
          'findExcel(headers,"new item number","item number","item-number","item num","itemnumber","sku")',
          "Victoria master ITEM-NUM header")
s=once(s,'findExcelExact(headers,"description")',
          'findExcel(headers,"victoria description","description")',
          "Victoria master description header")
s=once(s,'ii=find(f,"item number","itemnumber","sku")',
          'ii=find(f,"item number","item num","itemnumber","sku")',
          "batch ITEM-NUM header")
s=once(s,'    private int victoriaAliasItems=0;','    private int victoriaAliasItems=0;\n    private int victoriaUnmappedBarcodes=0;','unmapped UPC count')
s=once(s,'victoriaAliasItems=0;victoriaCustomerTotal=0;victoriaCustomerRows=0;',
          'victoriaAliasItems=0;victoriaUnmappedBarcodes=0;victoriaCustomerTotal=0;victoriaCustomerRows=0;','Victoria source reset')
old='''    /**
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
    }'''
new='''    /** Customer QTY rolls up by item number across locations and UPC aliases.
     * Rows without an item number stay separate by UPC for later manual fill-in. */
    private LinkedHashMap<String,VictoriaCustomerXlsxWriter.Row> groupVictoriaByItem(){
        LinkedHashMap<String,VictoriaCustomerXlsxWriter.Row> items=new LinkedHashMap<>();
        for(Total counted:combined.values()){
            String itemKey=itemKey(counted.itemNumber);
            String barcode=normalizeBarcode(counted.barcode);
            String key=itemKey.isEmpty()?"UPC:"+barcode:"ITEM:"+itemKey;
            VictoriaCustomerXlsxWriter.Row row=items.get(key);
            if(row==null){
                row=new VictoriaCustomerXlsxWriter.Row();
                row.itemNumber=counted.itemNumber;
                VictoriaProduct source=victoriaProducts.get(barcode);
                row.description=source!=null&&!source.description.isEmpty()?source.description:counted.description;
                items.put(key,row);
            }
            if(!barcode.isEmpty())row.barcodes.add(barcode);
            if(row.description.isEmpty())row.description=counted.description;
            row.quantity+=counted.quantity;
        }
        return items;
    }'''
s=once(s,old,new,"item grouped output with all UPCs")
s=once(s,'if(barcodes.size()>1)victoriaAliasItems++;','if(barcodes.size()>1)victoriaAliasItems++;','alias tally')
old='''        int unmatched=0;java.util.ArrayList<String> unmatchedBarcodes=new java.util.ArrayList<>();
        for(Total total:combined.values()){
            VictoriaProduct product=victoriaProducts.get(normalizeBarcode(total.barcode));
            if(product==null||product.itemNumber.isEmpty()){unmatched++;if(unmatchedBarcodes.size()<20)unmatchedBarcodes.add(total.barcode);continue;}
            total.itemNumber=product.itemNumber;
            if(!product.description.isEmpty())total.description=product.description;
        }
        if(unmatched>0)errors.add(unmatched+" counted barcode(s) were not found with an item number in the original Victoria Excel: "+android.text.TextUtils.join(", ",unmatchedBarcodes)+(unmatched>unmatchedBarcodes.size()?" ...":""));'''
new='''        victoriaUnmappedBarcodes=0;
        for(Total total:combined.values()){
            VictoriaProduct product=victoriaProducts.get(normalizeBarcode(total.barcode));
            if(product==null||product.itemNumber.isEmpty()){victoriaUnmappedBarcodes++;continue;}
            total.itemNumber=product.itemNumber;
            if(!product.description.isEmpty())total.description=product.description;
        }'''
s=once(s,old,new,"allow blank item numbers for customer fill-in")
s=once(s,'s.append("Items with more than one counted barcode: ").append(victoriaAliasItems).append("\\n");',
          's.append("Items with more than one counted barcode: ").append(victoriaAliasItems).append("\\n");\n        s.append("Rows needing ITEM NUMBER fill-in: ").append(victoriaUnmappedBarcodes).append("\\n");',"verification summary unmapped count")
s=once(s,'" ITEM NUMBER(s) have multiple counted barcodes. The customer Excel will have ONE line per ITEM NUMBER. Its BARCODE will be the first matching barcode from the original Victoria Excel, and the QTY will include every counted barcode and location. Review the Verification Report for alias details. Continue?"',
          '" ITEM NUMBER(s) have multiple counted barcodes. The customer Excel will have one line per ITEM NUMBER with every UPC listed, and QTY summed across locations. Rows without ITEM NUMBER stay separate by UPC for manual completion. Review the Verification Report. Continue?"',"alias confirmation copy")
s=once(s,'b.append("Multiple-barcode item numbers\\t").append(victoriaAliasItems).append("\\r\\n");',
          'b.append("Multiple-barcode item numbers\\t").append(victoriaAliasItems).append("\\r\\n");\n        b.append("Rows needing ITEM NUMBER fill-in\\t").append(victoriaUnmappedBarcodes).append("\\r\\n");',"audit missing item summary")
s=once(s,'b.append("ITEM NUMBER\\tCUSTOMER PRIMARY BARCODE\\tCOUNTED BARCODE\\tCOUNTED QTY\\r\\n");',
          'b.append("ITEM NUMBER\\tCUSTOMER UPC LIST\\tCOUNTED BARCODE\\tCOUNTED QTY\\r\\n");',"audit UPC header")
s=once(s,'String primary=primaryBarcodeByItem.get(entry.getKey());','String primary=android.text.TextUtils.join(", ",entry.getValue().keySet());',"audit UPC list")
s=once(s,'b.append("IMPORTANT: Final customer workbook totals are checked by ITEM NUMBER.\\r\\n");',
          'b.append("Rows with a blank ITEM NUMBER are retained as separate UPC lines for manual completion.\\r\\n");\n        b.append("IMPORTANT: Final customer workbook totals are checked by ITEM NUMBER and blank-item UPC rows.\\r\\n");',"audit explanation")
merge.write_text(s)

checks={
 "version": "versionCode 30239" in gradle.read_text() and "versionName '3.0.239'" in gradle.read_text(),
 "visible Victoria import fields": "QTY • UPC • DESCRIPTION\\nITEM #" in main.read_text() and "quantity,barcode,description,item_number,location" not in main.read_text(),
 "saved Victoria preset excludes location": 'new String[]{"quantity","barcode","description","item_number"}' in config.read_text(),
 "Victoria custom headers recognized": 'findHeader(first,"item number","item num"' in main.read_text() and 'findExcel(headers,"victoria description","description")' in merge.read_text(),
 "customer order": 'text(data,"B1","ITEM NUMBER"' in writer.read_text() and 'text(data,"C1","UPC"' in writer.read_text() and 'text(data,"D1","DESCRIPTION"' in writer.read_text(),
 "all UPC aliases retained": "row.barcodes.add(barcode)" in merge.read_text(),
 "missing item lines retained": '"UPC:"+barcode' in merge.read_text() and "Rows needing ITEM NUMBER fill-in" in merge.read_text(),
 "workflow points to new script": ".github/prepare_30239.py" in workflow.read_text(),
}
failed=[k for k,v in checks.items() if not v]
if failed: raise SystemExit("3.0.239 validation failed: "+", ".join(failed))
print("Prepared OnHand 3.0.239: Victoria import preset visibly includes ITEM #; customer QTY groups by item number across locations and carries every UPC, while blank item-number lines remain editable.")
