#!/usr/bin/env python3
from pathlib import Path
import runpy

root=Path(__file__).resolve().parents[1]
runpy.run_path(str(root/".github"/"prepare_30195.py"),run_name="__main__")

gradle=root/"app"/"build.gradle"
s=gradle.read_text()
if "versionName '3.0.195'" not in s:raise SystemExit("3.0.195 version source not found")
gradle.write_text(s.replace("versionCode 30195","versionCode 30196").replace("versionName '3.0.195'","versionName '3.0.196'"))

manifest=root/"app"/"src"/"main"/"AndroidManifest.xml"
s=manifest.read_text()
if "iCE Onhand 3.0.195" not in s:raise SystemExit("3.0.195 app label not found")
manifest.write_text(s.replace("iCE Onhand 3.0.195","iCE Onhand 3.0.196"))

main=root/"app"/"src"/"main"/"java"/"com"/"iceinventory"/"onhand"/"MainActivity.java"
s=main.read_text().replace("Onhand Inventory 3.0.195","Onhand Inventory 3.0.196")
old='''    private String batchExportFileName(){String day=new SimpleDateFormat("yyyy-MM-dd_HHmm",Locale.US).format(new Date());String ext=pendingExportExcel?".xlsx":".txt";String user=safeFilePart(savedUserName());int batchNo=Math.max(1,pendingBatchNumber);String prefix="BATCH COUNT - "+(user.isEmpty()?"":user+" - ");return prefix+safeFileName(sessionName)+"_Batch"+batchNo+"_Seq"+seqText(pendingBatchFirstHistoryId)+"-"+seqText(pendingBatchLastHistoryId)+"_"+day+ext;}'''
new='''    private String batchExportFileName(){String ext=pendingExportExcel?".xlsx":".txt";String user=safeFilePart(savedUserName());if(user.isEmpty())user="Counter";return "count"+user+"-Batch"+Math.max(1,pendingBatchNumber)+ext;}'''
if s.count(old)!=1:raise SystemExit("Long batch export filename anchor not found")
main.write_text(s.replace(old,new,1))

adapter=root/"app"/"src"/"main"/"java"/"com"/"iceinventory"/"onhand"/"InventoryAdapter.java"
s=adapter.read_text()
if "import android.graphics.drawable.GradientDrawable;" not in s:
    s=s.replace("import android.graphics.Color;","import android.graphics.Color;\nimport android.graphics.drawable.GradientDrawable;",1)
old='''        LinearLayout quantityLine=new LinearLayout(context);quantityLine.setOrientation(LinearLayout.HORIZONTAL);quantityLine.setGravity(Gravity.END|Gravity.CENTER_VERTICAL);
        TextView qtyLabel=text("Qty: ",compact?12:14,primary,true);
        TextView qtyValue=text(QuantityMath.format(r.quantity),active?(compact?20:22):(compact?13:15),active?Color.rgb(0,120,45):primary,true);
        quantityLine.addView(qtyLabel);quantityLine.addView(qtyValue);right.addView(quantityLine);'''
new='''        TextView q=text("QTY: "+QuantityMath.format(r.quantity),compact?15:18,Color.BLACK,true);
        q.setGravity(Gravity.END);
        q.setPadding(dp(compact?8:10),dp(2),dp(compact?8:10),dp(2));
        GradientDrawable quantityBadge=new GradientDrawable();
        quantityBadge.setColor(Color.rgb(255,215,0));
        quantityBadge.setCornerRadius(dp(6));
        q.setBackground(quantityBadge);
        right.addView(q);'''
if s.count(old)!=1:raise SystemExit("Quantity display anchor not found")
adapter.write_text(s.replace(old,new,1))

checks={
    "version":"versionName '3.0.196'" in gradle.read_text(),
    "all counter exports include location":"if(export&&!out.contains(\"location\"))out.add(\"location\")" in (root/"app/src/main/java/com/iceinventory/onhand/TabTextUtils.java").read_text(),
    "short batch filename":"return \"count\"+user+\"-Batch\"+Math.max(1,pendingBatchNumber)+ext;" in main.read_text(),
    "high contrast quantity badge":"quantityBadge.setColor(Color.rgb(255,215,0))" in adapter.read_text() and 'text("QTY: "+QuantityMath.format(r.quantity)' in adapter.read_text(),
    "cigarette reconciliation retained":"row.cigaretteQuantity=cigaretteByGtin.getOrDefault(row.product.gtin,0d)" in (root/"app/src/main/java/com/iceinventory/onhand/MonthlyInventoryActivity.java").read_text(),
}
failed=[name for name,ok in checks.items() if not ok]
if failed:raise SystemExit("3.0.196 verification failed: "+", ".join(failed))
print("Prepared iCE Onhand 3.0.196: high-contrast quantities, short batch filenames, location exports retained")
