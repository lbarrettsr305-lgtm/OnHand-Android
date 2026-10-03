#!/usr/bin/env python3
from pathlib import Path
import runpy

root=Path(__file__).resolve().parents[1]
runpy.run_path(str(root/".github"/"prepare_30194.py"),run_name="__main__")

gradle=root/"app"/"build.gradle"
s=gradle.read_text()
if "versionName '3.0.194'" not in s:raise SystemExit("3.0.194 version source not found")
s=s.replace("versionCode 30194","versionCode 30195").replace("versionName '3.0.194'","versionName '3.0.195'")
gradle.write_text(s)

manifest=root/"app"/"src"/"main"/"AndroidManifest.xml"
s=manifest.read_text()
if "iCE Onhand 3.0.194" not in s:raise SystemExit("3.0.194 app label not found")
manifest.write_text(s.replace("iCE Onhand 3.0.194","iCE Onhand 3.0.195"))

main=root/"app"/"src"/"main"/"java"/"com"/"iceinventory"/"onhand"/"MainActivity.java"
s=main.read_text().replace("Onhand Inventory 3.0.194","Onhand Inventory 3.0.195")
main.write_text(s)

# Require the count location in every counter export so the monthly cigarette
# report can include all counters' Cig Shelf quantities, even with blank POS categories.
tab=root/"app"/"src"/"main"/"java"/"com"/"iceinventory"/"onhand"/"TabTextUtils.java"
t=tab.read_text()
old='''        if(!out.contains("category_description"))out.add("category_description");
        if(out.isEmpty())out.addAll(DEFAULT);'''
new='''        if(!out.contains("category_description"))out.add("category_description");
        if(export&&!out.contains("location"))out.add("location");
        if(out.isEmpty())out.addAll(DEFAULT);'''
if t.count(old)!=1:raise SystemExit("Count export field-order anchor not found")
t=t.replace(old,new,1)
tab.write_text(t)

writer=root/"app"/"src"/"main"/"java"/"com"/"iceinventory"/"onhand"/"MonthlyClientXlsxWriter.java"
w=writer.read_text()
old='''    public static final class ClientRow {
        public Product product;public double quantity;
        public ClientRow(Product product,double quantity){this.product=product;this.quantity=quantity;}
    }'''
new='''    public static final class ClientRow {
        public Product product;public double quantity;public double cigaretteQuantity;
        public ClientRow(Product product,double quantity){this.product=product;this.quantity=quantity;}
    }'''
if w.count(old)!=1:raise SystemExit("Client row cigarette quantity anchor not found")
w=w.replace(old,new,1)
writer.write_text(w)

activity=root/"app"/"src"/"main"/"java"/"com"/"iceinventory"/"onhand"/"MonthlyInventoryActivity.java"
a=activity.read_text()
old='''        final ArrayList<String> locations=new ArrayList<>();'''
new='''        final ArrayList<String> locations=new ArrayList<>();
        final LinkedHashMap<String,Double> locationQuantities=new LinkedHashMap<>();'''
if a.count(old)!=1:raise SystemExit("Count location quantity storage anchor not found")
a=a.replace(old,new,1)
old='''if(li>=0&&li<v.length&&!v[li].trim().isEmpty()&&!detail.locations.contains(v[li].trim()))detail.locations.add(v[li].trim());'''
new='''if(li>=0&&li<v.length&&!v[li].trim().isEmpty()){String countedLocation=v[li].trim();if(!detail.locations.contains(countedLocation))detail.locations.add(countedLocation);detail.locationQuantities.put(countedLocation,detail.locationQuantities.getOrDefault(countedLocation,0d)+q);}'''
if a.count(old)!=1:raise SystemExit("Count location quantity accumulation anchor not found")
a=a.replace(old,new,1)
old='''        clientRows.addAll(byGtin.values());Collections.sort(clientRows,(a,b)->Double.compare(b.quantity,a.quantity));for(MonthlyClientXlsxWriter.ClientRow r:clientRows)clientTotal=clientTotal+r.quantity;'''
new='''        clientRows.addAll(byGtin.values());
        LinkedHashMap<String,Double> cigaretteByGtin=new LinkedHashMap<>();
        for(Map.Entry<String,Double> e:combined.entrySet()){
            MonthlyClientXlsxWriter.Product product=products.get(e.getKey());if(product==null)continue;
            String category=product.categoryName==null?"":product.categoryName.trim().toUpperCase(Locale.US);
            double cigaretteQty=0;
            if(category.contains("CIGARETTE"))cigaretteQty=e.getValue();
            else if(category.isEmpty()){
                UnmatchedDetail detail=countDetails.get(e.getKey());
                if(detail!=null)for(Map.Entry<String,Double> locationQty:detail.locationQuantities.entrySet())
                    if(locationQty.getKey().trim().toUpperCase(Locale.US).startsWith("CIG SHELF"))cigaretteQty+=locationQty.getValue();
            }
            if(cigaretteQty!=0)cigaretteByGtin.put(product.gtin,cigaretteByGtin.getOrDefault(product.gtin,0d)+cigaretteQty);
        }
        for(MonthlyClientXlsxWriter.ClientRow row:clientRows)row.cigaretteQuantity=cigaretteByGtin.getOrDefault(row.product.gtin,0d);
        Collections.sort(clientRows,(a,b)->Double.compare(b.quantity,a.quantity));for(MonthlyClientXlsxWriter.ClientRow r:clientRows)clientTotal=clientTotal+r.quantity;'''
if a.count(old)!=1:raise SystemExit("Monthly cigarette aggregation anchor not found")
a=a.replace(old,new,1)
activity.write_text(a)

report=root/"app"/"src"/"main"/"java"/"com"/"iceinventory"/"onhand"/"MonthlyCategoryXlsxWriter.java"
r=report.read_text()
old='''        for(MonthlyClientXlsxWriter.ClientRow row:rows)if(categoryName(row.product).toUpperCase(Locale.US).contains("CIGARETTE"))cigarettes.add(row);'''
new='''        for(MonthlyClientXlsxWriter.ClientRow row:rows)if(row.cigaretteQuantity!=0)cigarettes.add(row);'''
if r.count(old)!=1:raise SystemExit("Cigarette report filter anchor not found")
r=r.replace(old,new,1)
old='''number(body,3,r,row.quantity,0);rowEnd(body);total=total+row.quantity;r++;}'''
new='''number(body,3,r,row.cigaretteQuantity,0);rowEnd(body);total=total+row.cigaretteQuantity;r++;}'''
if r.count(old)!=1:raise SystemExit("Cigarette report line quantity anchor not found")
r=r.replace(old,new,1)
report.write_text(r)

checks={
    "version":"versionName '3.0.195'" in gradle.read_text(),
    "all counter exports include location":"if(export&&!out.contains(\"location\"))out.add(\"location\")" in t,
    "counter location quantities are retained":"detail.locationQuantities.put(countedLocation,detail.locationQuantities.getOrDefault(countedLocation,0d)+q)" in a,
    "cigarette categories use all counter quantities":"if(category.contains(\"CIGARETTE\"))cigaretteQty=e.getValue()" in a,
    "blank categories use Cig Shelf quantities":"startsWith(\"CIG SHELF\")" in a,
    "cigarette report uses cigarette-only amounts":"row.cigaretteQuantity,0" in r,
    "customer export still filters zero rows":"if(row.quantity>0)countedRows.add(row)" in a,
}
failed=[name for name,ok in checks.items() if not ok]
if failed:raise SystemExit("3.0.195 verification failed: "+", ".join(failed))
print("Prepared iCE OnHand 3.0.195: combine cigarette counts across counters and Cig Shelf locations")
