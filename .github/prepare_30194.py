#!/usr/bin/env python3
from pathlib import Path
import runpy

root=Path(__file__).resolve().parents[1]
runpy.run_path(str(root/".github"/"prepare_30193.py"),run_name="__main__")

gradle=root/"app"/"build.gradle"
s=gradle.read_text()
if "versionName '3.0.193'" not in s:raise SystemExit("3.0.193 version source not found")
s=s.replace("versionCode 30193","versionCode 30194").replace("versionName '3.0.193'","versionName '3.0.194'")
gradle.write_text(s)

manifest=root/"app"/"src"/"main"/"AndroidManifest.xml"
s=manifest.read_text()
if "iCE Onhand 3.0.193" not in s:raise SystemExit("3.0.193 app label not found")
manifest.write_text(s.replace("iCE Onhand 3.0.193","iCE Onhand 3.0.194"))

main=root/"app"/"src"/"main"/"java"/"com"/"iceinventory"/"onhand"/"MainActivity.java"
s=main.read_text().replace("Onhand Inventory 3.0.193","Onhand Inventory 3.0.194")
main.write_text(s)

activity=root/"app"/"src"/"main"/"java"/"com"/"iceinventory"/"onhand"/"MonthlyInventoryActivity.java"
a=activity.read_text()
old='''else if(request==SAVE_CLIENT){if(!validated)throw new Exception("Customer import report is blocked until validation passes");MonthlyClientXlsxWriter.writeClient(use,clientRows);clientExported=true;workflowPrefs().edit().putBoolean("client_exported",true).apply();}'''
new='''else if(request==SAVE_CLIENT){if(!validated)throw new Exception("Customer import report is blocked until validation passes");ArrayList<MonthlyClientXlsxWriter.ClientRow> countedRows=new ArrayList<>();for(MonthlyClientXlsxWriter.ClientRow row:clientRows)if(row.quantity>0)countedRows.add(row);if(countedRows.isEmpty())throw new Exception("No counted items are available for the customer import report");MonthlyClientXlsxWriter.writeClient(use,countedRows);clientExported=true;workflowPrefs().edit().putBoolean("client_exported",true).apply();}'''
if a.count(old)!=1:raise SystemExit("Customer import export branch anchor not found")
a=a.replace(old,new,1)
activity.write_text(a)

checks={
    "version":"versionName '3.0.194'" in gradle.read_text(),
    "customer import filters zero quantity rows":"if(row.quantity>0)countedRows.add(row)" in a,
    "customer writer receives counted rows":"MonthlyClientXlsxWriter.writeClient(use,countedRows)" in a,
    "empty counted report is blocked":"No counted items are available for the customer import report" in a,
    "source catalog and other reports remain intact":"clientRows.addAll(byGtin.values())" in a,
}
failed=[k for k,v in checks.items() if not v]
if failed:raise SystemExit("3.0.194 verification failed: "+", ".join(failed))
print("Prepared iCE OnHand 3.0.194: customer import includes only counted items")
