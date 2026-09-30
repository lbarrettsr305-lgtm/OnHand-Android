#!/usr/bin/env python3
from pathlib import Path
import runpy

root=Path(__file__).resolve().parents[1]
runpy.run_path(str(root/".github"/"prepare_30191.py"),run_name="__main__")

gradle=root/"app"/"build.gradle"
s=gradle.read_text()
if "versionName '3.0.191'" not in s:raise SystemExit("3.0.191 version source not found")
s=s.replace("versionCode 30191","versionCode 30192").replace("versionName '3.0.191'","versionName '3.0.192'")
gradle.write_text(s)

manifest=root/"app"/"src"/"main"/"AndroidManifest.xml"
s=manifest.read_text()
if "iCE Onhand 3.0.191" not in s:raise SystemExit("3.0.191 app label not found")
manifest.write_text(s.replace("iCE Onhand 3.0.191","iCE Onhand 3.0.192"))

main=root/"app"/"src"/"main"/"java"/"com"/"iceinventory"/"onhand"/"MainActivity.java"
s=main.read_text()
s=s.replace("Onhand Inventory 3.0.191","Onhand Inventory 3.0.192")
s=s.replace("import java.text.SimpleDateFormat;","import java.text.SimpleDateFormat;\nimport java.math.BigDecimal;",1)
s=s.replace("    private EditText description;\n","    private EditText description;\n    private TextView pricePreview;\n",1)
old='''        root.addView(label("Description"));
        description=new EditText(this);description.setSingleLine(true);description.setHint("Enter description (optional)");description.setTextSize(16);
        styleEntry(description);installScannerImeWatcher(description);root.addView(description,new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT,dp(48)));'''
new='''        root.addView(label("Description"));
        LinearLayout descriptionRow=new LinearLayout(this);descriptionRow.setOrientation(LinearLayout.HORIZONTAL);descriptionRow.setGravity(Gravity.CENTER_VERTICAL);
        description=new EditText(this);description.setSingleLine(true);description.setHint("Enter description (optional)");description.setTextSize(16);
        styleEntry(description);installScannerImeWatcher(description);descriptionRow.addView(description,new LinearLayout.LayoutParams(0,dp(48),1));
        pricePreview=text("",14,gold(),true);pricePreview.setVisibility(View.GONE);pricePreview.setGravity(Gravity.CENTER_VERTICAL|Gravity.END);pricePreview.setPadding(dp(3),0,0,0);
        descriptionRow.addView(pricePreview,new LinearLayout.LayoutParams(dp(112),dp(48)));
        root.addView(descriptionRow);'''
if s.count(old)!=1:raise SystemExit("Description field layout anchor not found")
s=s.replace(old,new,1)

old='''        ScrollView scroll=new ScrollView(this);LinearLayout map=new LinearLayout(this);map.setOrientation(LinearLayout.VERTICAL);map.setPadding(dp(12),dp(8),dp(12),dp(8));scroll.addView(map);
        TextView grandView=text("STORE GRAND TOTAL: "+grand,20,gold(),true);'''
new='''        ScrollView scroll=new ScrollView(this);LinearLayout map=new LinearLayout(this);map.setOrientation(LinearLayout.VERTICAL);map.setPadding(dp(12),dp(8),dp(12),dp(8));scroll.addView(map);
        Button viewItems=button("VIEW COUNTED ITEMS BY LOCATION",1);viewItems.setOnClickListener(v->showCountedLocationPicker());map.addView(viewItems);
        TextView grandView=text("STORE GRAND TOTAL: "+grand,20,gold(),true);'''
if s.count(old)!=1:raise SystemExit("Store Map button anchor not found")
s=s.replace(old,new,1)

anchor='''    private void showLocationTotals() {'''
methods='''    private void showCountedLocationPicker() {
        LinkedHashMap<String,Integer> units=new LinkedHashMap<>();
        for(InventoryDb.Row r:allRows) {
            if(r.quantity<=0)continue;
            String loc=r.location==null||r.location.trim().isEmpty()?"Main":r.location.trim();
            units.put(loc,units.getOrDefault(loc,0)+r.quantity);
        }
        if(units.isEmpty()){toast("No counted locations yet");return;}
        ArrayList<String> locations=new ArrayList<>(units.keySet());
        String[] choices=new String[locations.size()];
        for(int i=0;i<locations.size();i++)choices[i]=locations.get(i)+"  •  "+units.get(locations.get(i))+" units";
        new AlertDialog.Builder(this).setTitle("Choose a Location")
                .setItems(choices,(dialog,which)->showCountedItemsAtLocation(locations.get(which)))
                .setNegativeButton("Back",null).show();
    }

    private void showCountedItemsAtLocation(String selectedLocation) {
        ArrayList<String> items=new ArrayList<>();
        double total=0;
        for(InventoryDb.Row r:allRows) {
            String loc=r.location==null||r.location.trim().isEmpty()?"Main":r.location.trim();
            if(r.quantity<=0||!selectedLocation.equalsIgnoreCase(loc))continue;
            String description=r.description==null||r.description.trim().isEmpty()?r.barcode:r.description.trim();
            String price=r.price==null||r.price.trim().isEmpty()?"":"  •  $"+r.price.trim();
            String category=r.categoryName==null||r.categoryName.trim().isEmpty()?"Uncategorized":r.categoryName.trim();
            items.add(description+"\\nCategory: "+category+"  •  Barcode: "+r.barcode+"  •  Qty: "+QuantityMath.format(r.quantity)+price);
            total+=r.quantity;
        }
        if(items.isEmpty()){toast("No counted items in "+selectedLocation);return;}
        new AlertDialog.Builder(this).setTitle(selectedLocation+" — "+items.size()+" counted lines, "+QuantityMath.format(total)+" units")
                .setItems(items.toArray(new String[0]),null).setPositiveButton("Done",null).show();
    }

'''
if s.count(anchor)!=1:raise SystemExit("Location item picker method anchor not found")
s=s.replace(anchor,methods+anchor,1)

old='''        qty.setText("");
        currentPrice="";

        InventoryDb.Row existing'''
new='''        qty.setText("");
        currentPrice="";
        updatePricePreview();

        InventoryDb.Row existing'''
if s.count(old)!=1:raise SystemExit("Scan price reset anchor not found")
s=s.replace(old,new,1)

old='''        currentPrice=row.price==null?"":row.price;
        highlightAndRevealBarcode(actual);'''
new='''        currentPrice=row.price==null?"":row.price;
        updatePricePreview();
        highlightAndRevealBarcode(actual);'''
if s.count(old)!=1:raise SystemExit("Saved item price anchor not found")
s=s.replace(old,new,1)

old='''                        currentPrice=found.price==null?"":found.price.trim();
                        if(found.imageUrl'''
new='''                        currentPrice=found.price==null?"":found.price.trim();
                        updatePricePreview();
                        if(found.imageUrl'''
if s.count(old)!=1:raise SystemExit("Internet item price anchor not found")
s=s.replace(old,new,1)

anchor='''    private void focusBarcodeWithoutKeyboard() {'''
method='''    private void updatePricePreview() {
        if(pricePreview==null)return;
        String value=currentPrice==null?"":currentPrice.trim();
        if(value.isEmpty()) {
            pricePreview.setText("");
            pricePreview.setVisibility(View.GONE);
            return;
        }
        String display=value;
        try {
            BigDecimal amount=new BigDecimal(value.replace("$","").replace(",","").trim());
            display="$"+String.format(Locale.US,"%.2f",amount);
        } catch(Exception ignored) {
            if(!display.startsWith("$"))display="$"+display;
        }
        pricePreview.setText("PRICE: "+display);
        pricePreview.setVisibility(View.VISIBLE);
    }

'''
if s.count(anchor)!=1:raise SystemExit("Price display method anchor not found")
s=s.replace(anchor,method+anchor,1)

old='''        prefs().edit().putString(KEY_UNKNOWN_MODE,"add").apply();
        barcode.setText("");description.setText("");qty.setText("");currentPrice="";
        barcode.setShowSoftInputOnFocus(true);barcode.requestFocus();'''
new='''        prefs().edit().putString(KEY_UNKNOWN_MODE,"add").apply();
        barcode.setText("");description.setText("");qty.setText("");currentPrice="";updatePricePreview();
        barcode.setShowSoftInputOnFocus(true);barcode.requestFocus();'''
if s.count(old)!=1:raise SystemExit("Manual item price clear anchor not found")
s=s.replace(old,new,1)

old='''        barcode.setText("");description.setText("");qty.setText("");currentPrice="";refreshList();'''
new='''        barcode.setText("");description.setText("");qty.setText("");currentPrice="";updatePricePreview();refreshList();'''
if s.count(old)!=1:raise SystemExit("Saved count price clear anchor not found")
s=s.replace(old,new,1)

main.write_text(s)

# Include product category in both TXT and Excel location-detail exports.
old='''        StringBuilder out=new StringBuilder("User\\tLocation\\tQuantity\\tBarcode\\tDescription\\tPrice\\r\\n");'''
new='''        StringBuilder out=new StringBuilder("User\\tLocation\\tQuantity\\tBarcode\\tDescription\\tCategory\\tPrice\\r\\n");'''
if s.count(old)!=1:raise SystemExit("Location detail TXT header anchor not found")
s=s.replace(old,new,1)
old='''                    .append(reportField(r.description)).append('\\t')
                    .append(reportField(r.price)).append("\\r\\n");'''
new='''                    .append(reportField(r.description)).append('\\t')
                    .append(reportField(r.categoryName)).append('\\t')
                    .append(reportField(r.price)).append("\\r\\n");'''
if s.count(old)!=1:raise SystemExit("Location detail TXT columns anchor not found")
s=s.replace(old,new,1)
main.write_text(s)

simple=root/"app"/"src"/"main"/"java"/"com"/"iceinventory"/"onhand"/"SimpleXlsxWriter.java"
x=simple.read_text()
old='''        x.append("<cols><col min=\\"1\\" max=\\"1\\" width=\\"18\\" customWidth=\\"1\\"/><col min=\\"2\\" max=\\"2\\" width=\\"20\\" customWidth=\\"1\\"/><col min=\\"3\\" max=\\"3\\" width=\\"12\\" customWidth=\\"1\\"/><col min=\\"4\\" max=\\"4\\" width=\\"20\\" customWidth=\\"1\\"/><col min=\\"5\\" max=\\"5\\" width=\\"46\\" customWidth=\\"1\\"/><col min=\\"6\\" max=\\"6\\" width=\\"14\\" customWidth=\\"1\\"/></cols><sheetData>");'''
new='''        x.append("<cols><col min=\\"1\\" max=\\"1\\" width=\\"18\\" customWidth=\\"1\\"/><col min=\\"2\\" max=\\"2\\" width=\\"20\\" customWidth=\\"1\\"/><col min=\\"3\\" max=\\"3\\" width=\\"12\\" customWidth=\\"1\\"/><col min=\\"4\\" max=\\"4\\" width=\\"20\\" customWidth=\\"1\\"/><col min=\\"5\\" max=\\"5\\" width=\\"46\\" customWidth=\\"1\\"/><col min=\\"6\\" max=\\"6\\" width=\\"24\\" customWidth=\\"1\\"/><col min=\\"7\\" max=\\"7\\" width=\\"14\\" customWidth=\\"1\\"/></cols><sheetData>");'''
if x.count(old)!=1:raise SystemExit("Location detail Excel widths anchor not found")
x=x.replace(old,new,1)
old='''        String[] headers={"User","Location","Quantity","Barcode","Description","Price"};'''
new='''        String[] headers={"User","Location","Quantity","Barcode","Description","Category","Price"};'''
if x.count(old)!=1:raise SystemExit("Location detail Excel header anchor not found")
x=x.replace(old,new,1)
old='''            textCell(x,"F"+n,clean(r.price),0);'''
new='''            textCell(x,"F"+n,clean(r.categoryName),0);
            textCell(x,"G"+n,clean(r.price),0);'''
if x.count(old)!=1:raise SystemExit("Location detail Excel category column anchor not found")
x=x.replace(old,new,1)
old='''        x.append("</sheetData><autoFilter ref=\\"A1:F").append(Math.max(1,n)).append("\\"/></worksheet>");'''
new='''        x.append("</sheetData><autoFilter ref=\\"A1:G").append(Math.max(1,n)).append("\\"/></worksheet>");'''
if x.count(old)!=1:raise SystemExit("Location detail Excel filter anchor not found")
x=x.replace(old,new,1)
simple.write_text(x)

# Put the report type at the beginning of exported report filenames. Keep the
# user and inventory identifiers in the name so files remain easy to identify.
replacements={
'''    private String batchExportFileName(){String day=new SimpleDateFormat("yyyy-MM-dd_HHmm",Locale.US).format(new Date());String ext=pendingExportExcel?".xlsx":".txt";String user=safeFilePart(savedUserName());int batchNo=Math.max(1,pendingBatchNumber);String prefix=user.isEmpty()?"Batch"+batchNo+" - ":user+" - ";return prefix+safeFileName(sessionName)+"_Batch"+batchNo+"_Seq"+seqText(pendingBatchFirstHistoryId)+"-"+seqText(pendingBatchLastHistoryId)+"_"+day+ext;}''':
'''    private String batchExportFileName(){String day=new SimpleDateFormat("yyyy-MM-dd_HHmm",Locale.US).format(new Date());String ext=pendingExportExcel?".xlsx":".txt";String user=safeFilePart(savedUserName());int batchNo=Math.max(1,pendingBatchNumber);String prefix="BATCH COUNT - "+(user.isEmpty()?"":user+" - ");return prefix+safeFileName(sessionName)+"_Batch"+batchNo+"_Seq"+seqText(pendingBatchFirstHistoryId)+"-"+seqText(pendingBatchLastHistoryId)+"_"+day+ext;}''',
'''    private String completeExportFileName(){String ext=pendingExportExcel?".xlsx":".txt";String store=safeFilePart(sessionName);String user=safeFilePart(savedUserName());if(store.isEmpty())store="Inventory";if(user.isEmpty())user="Counter";return store+"-"+user+"-"+String.format(Locale.US,"%02d",Math.max(1,pendingBatchNumber))+ext;}''':
'''    private String completeExportFileName(){String ext=pendingExportExcel?".xlsx":".txt";String store=safeFilePart(sessionName);String user=safeFilePart(savedUserName());if(store.isEmpty())store="Inventory";if(user.isEmpty())user="Counter";return "COMPLETED INVENTORY - "+user+" - "+store+"-"+String.format(Locale.US,"%02d",Math.max(1,pendingBatchNumber))+ext;}''',
'''        if(!n.toLowerCase(Locale.US).endsWith(" - internet items with pictures"))n+=" - Internet Items With Pictures";''':
'''        String lower=n.toLowerCase(Locale.US);if(lower.endsWith(" - internet items with pictures"))n=n.substring(0,n.length()-" - internet items with pictures".length());n="INTERNET ITEMS WITH PICTURES - "+n;''',
'''        if(!n.toLowerCase(Locale.US).endsWith(" - location quantity"))n+=" - Location Quantity";''':
'''        String lower=n.toLowerCase(Locale.US);if(lower.endsWith(" - location quantity"))n=n.substring(0,n.length()-" - location quantity".length());n="LOCATION QUANTITY REPORT - "+n;''',
'''        if(!n.toLowerCase(Locale.US).endsWith(" - location detail"))n+=" - Location Detail";''':
'''        String lowerName=n.toLowerCase(Locale.US);if(lowerName.endsWith(" - location detail"))n=n.substring(0,n.length()-" - location detail".length());n="LOCATION DETAIL REPORT - "+n;''',
'''        return cleanTextName(u+" - "+b);''':
'''        return cleanTextName(b+(u.isEmpty()?"":" - "+u));'''
}
for old,new in replacements.items():
    if s.count(old)!=1:raise SystemExit("Report filename anchor not found: "+old[:90])
    s=s.replace(old,new,1)
main.write_text(s)

# Monthly exports are named by report first; the store and date follow it.
monthly=root/"app"/"src"/"main"/"java"/"com"/"iceinventory"/"onhand"/"MonthlyInventoryActivity.java"
m=monthly.read_text()
for report in ["CUSTOMER IMPORT REPORT","MISSING NEW ITEMS","COMPLETE COMBINED INVENTORY","ALL-INVENTORY","CIGARETTES QTY","CATEGORY REPORT","MONTHLY VERIFICATION","MASTER"]:
    old='base()+" '+report+'-"+day()'
    new='"'+report+' - "+base()+" - "+day()'
    if m.count(old)!=1:raise SystemExit("Monthly report filename anchor not found: "+report)
    m=m.replace(old,new,1)
monthly.write_text(m)

# Combined-batch report names also begin with the report type; COMBINED is
# retained so the importer can continue recognizing its own generated files.
merge=root/"app"/"src"/"main"/"java"/"com"/"iceinventory"/"onhand"/"BatchMergeActivity.java"
b=merge.read_text()
# Preserve category when a source count file provides it, and show a blank
# category for older/external formats without a category column.
old='''int bi=find(f,"barcode","upc","gtin"),qi=find(f,"quantity","qty","count","on hand","onhand"),di=find(f,"description","item description","name"),pi=find(f,"price","retail","cost"),li=find(f,"location","loc","area");'''
new='''int bi=find(f,"barcode","upc","gtin"),qi=find(f,"quantity","qty","count","on hand","onhand"),di=find(f,"description","item description","name"),pi=find(f,"price","retail","cost"),li=find(f,"location","loc","area"),ci=find(f,"category","category name");'''
if b.count(old)!=1:raise SystemExit("Combined category parser anchor not found")
b=b.replace(old,new,1)
b=b.replace('''qi=0;bi=1;di=f.length>2?2:-1;pi=f.length>3?3:-1;''','''qi=0;bi=1;di=f.length>2?2:-1;pi=f.length>3?3:-1;ci=-1;''',1)
b=b.replace('''addBatchRow(stat,f,bi,qi,di,pi,li);''','''addBatchRow(stat,f,bi,qi,di,pi,li,ci);''',1)
b=b.replace('''addBatchRow(stat,line.split("\\t",-1),bi,qi,di,pi,li);''','''addBatchRow(stat,line.split("\\t",-1),bi,qi,di,pi,li,ci);''',1)
old='''private void addBatchRow(BatchStat stat,String[] v,int bi,int qi,int di,int pi,int li)throws Exception{'''
new='''private void addBatchRow(BatchStat stat,String[] v,int bi,int qi,int di,int pi,int li,int ci)throws Exception{'''
if b.count(old)!=1:raise SystemExit("Combined category row method anchor not found")
b=b.replace(old,new,1)
old='''locationRows.add(new String[]{user,location,String.valueOf(q),code,di>=0&&di<v.length?clean(v[di]):"",pi>=0&&pi<v.length?clean(v[pi]):"",stat.fileName});'''
new='''locationRows.add(new String[]{user,location,String.valueOf(q),code,di>=0&&di<v.length?clean(v[di]):"",ci>=0&&ci<v.length?clean(v[ci]):"",pi>=0&&pi<v.length?clean(v[pi]):"",stat.fileName});'''
if b.count(old)!=1:raise SystemExit("Combined location category value anchor not found")
b=b.replace(old,new,1)
b=b.replace('''button("Export User + Location Detail — TXT")''','''button("Export User + Location + Category Detail — TXT")''',1)
b=b.replace('''b.append("User\\tLocation\\tQuantity\\tBarcode\\tDescription\\tPrice\\tSource File\\r\\n");''','''b.append("User\\tLocation\\tQuantity\\tBarcode\\tDescription\\tCategory\\tPrice\\tSource File\\r\\n");''',1)
changes={
'''combinedOutputName(sourceInventoryName()+" - Verified Batch.txt")''':'''combinedOutputName("VERIFIED BATCH",sourceInventoryName()+".txt")''',
'''combinedOutputName(sourceInventoryName()+" - Verification Report.txt")''':'''combinedOutputName("VERIFICATION REPORT",sourceInventoryName()+".txt")''',
'''combinedOutputName(sourceInventoryName()+" - Professional Report - "+stamp+".xlsx")''':'''combinedOutputName("PROFESSIONAL REPORT",sourceInventoryName()+" - "+stamp+".xlsx")''',
'''combinedOutputName(sourceInventoryName()+(totals?" - Location Totals.txt":" - User Location Detail.txt"))''':'''combinedOutputName(totals?"LOCATION TOTALS":"USER LOCATION DETAIL",sourceInventoryName()+".txt")''',
'''    private String combinedOutputName(String base){String u=safeFilePart(savedUserName());String b=safeFilePart(base);return u.isEmpty()?"COMBINED - "+b:"COMBINED - "+u+" - "+b;}''':'''    private String combinedOutputName(String report,String inventory){String u=safeFilePart(savedUserName());String b=safeFilePart(inventory);return report+" - COMBINED"+(u.isEmpty()?"":" - "+u)+" - "+b;}'''
}
for old,new in changes.items():
    if b.count(old)!=1:raise SystemExit("Combined report filename anchor not found: "+old[:90])
    b=b.replace(old,new,1)
merge.write_text(b)

checks={
    "version":"versionName '3.0.192'" in gradle.read_text(),
    "matched price":"pricePreview.setText(\"PRICE: \"+display)" in s,
    "saved barcode price":"currentPrice=row.price==null?\"\":row.price;\n        updatePricePreview();" in s,
    "internet lookup price":"currentPrice=found.price==null?\"\":found.price.trim();\n                        updatePricePreview();" in s,
    "description kept separate":"db.addOrIncrement(sessionId,code,desc,price,amount,loc)" in s,
    "location drill-down":"showCountedItemsAtLocation(locations.get(which))" in s,
    "location detail contents":"Category: \"+category+\"  •  Barcode: \"+r.barcode+\"  •  Qty: \"+QuantityMath.format(r.quantity)+price" in s,
    "location report category":"reportField(r.categoryName)" in s,
    "excel report category":"clean(r.categoryName)" in x,
    "report-first merged names":"return report+\" - COMBINED\"" in b,
}
failed=[k for k,v in checks.items() if not v]
if failed:raise SystemExit("3.0.192 verification failed: "+", ".join(failed))
print("Prepared iCE OnHand 3.0.192: visible item prices and location count drill-down")
