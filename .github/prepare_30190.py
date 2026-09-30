#!/usr/bin/env python3
from pathlib import Path
import runpy

root=Path(__file__).resolve().parents[1]
runpy.run_path(str(root/".github"/"prepare_30189.py"),run_name="__main__")

gradle=root/"app"/"build.gradle"
s=gradle.read_text().replace("versionCode 30189","versionCode 30190").replace("versionName '3.0.189'","versionName '3.0.190'")
gradle.write_text(s)

manifest=root/"app"/"src"/"main"/"AndroidManifest.xml"
manifest.write_text(manifest.read_text().replace("iCE Onhand 3.0.189","iCE Onhand 3.0.190"))

main=root/"app"/"src"/"main"/"java"/"com"/"iceinventory"/"onhand"/"MainActivity.java"
s=main.read_text().replace("Onhand Inventory 3.0.189","Onhand Inventory 3.0.190")
old='''        monthlyWorkflowMode=getIntent()!=null&&getIntent().getBooleanExtra(MonthlyInventoryActivity.EXTRA_MONTHLY_WORKFLOW,false);liqPosWorkflowMode=getIntent()!=null&&getIntent().getBooleanExtra(LiqPosInventoryActivity.EXTRA_LIQPOS_WORKFLOW,false);testScanMode=getIntent()!=null&&getIntent().getBooleanExtra(MonthlyInventoryActivity.EXTRA_TEST_SCAN,false);postCountAddOnsMode=getIntent()!=null&&getIntent().getBooleanExtra(MonthlyInventoryActivity.EXTRA_ADDONS_MODE,false);
        long requestedSession='''
new='''        monthlyWorkflowMode=getIntent()!=null&&getIntent().getBooleanExtra(MonthlyInventoryActivity.EXTRA_MONTHLY_WORKFLOW,false);liqPosWorkflowMode=getIntent()!=null&&getIntent().getBooleanExtra(LiqPosInventoryActivity.EXTRA_LIQPOS_WORKFLOW,false);testScanMode=getIntent()!=null&&getIntent().getBooleanExtra(MonthlyInventoryActivity.EXTRA_TEST_SCAN,false);postCountAddOnsMode=getIntent()!=null&&getIntent().getBooleanExtra(MonthlyInventoryActivity.EXTRA_ADDONS_MODE,false);
        SharedPreferences monthlyState=getSharedPreferences("monthly_workflow_state",MODE_PRIVATE);
        boolean physicalCountStarted=monthlyState.getInt("stage",0)>=5;
        boolean testAlreadyPassed=monthlyState.getBoolean("test_scan_passed",false);
        if(testScanMode&&(physicalCountStarted||testAlreadyPassed)){
            testScanMode=false;
            if(getIntent()!=null)getIntent().removeExtra(MonthlyInventoryActivity.EXTRA_TEST_SCAN);
        }
        long requestedSession='''
if s.count(old)!=1:raise SystemExit("Main test-scan initialization target not found")
s=s.replace(old,new,1)
main.write_text(s)

checks={
 "version":"versionName '3.0.190'" in gradle.read_text(),
 "physical count guard":"physicalCountStarted" in s and 'getInt("stage",0)>=5' in s,
 "passed test guard":"testAlreadyPassed" in s,
 "stale flag cleared":"removeExtra(MonthlyInventoryActivity.EXTRA_TEST_SCAN)" in s,
 "live cigarette total":"CIGARETTES QTY:" in s,
 "quantity emphasis":"active?(compact?20:22)" in (root/"app"/"src"/"main"/"java"/"com"/"iceinventory"/"onhand"/"InventoryAdapter.java").read_text(),
}
failed=[k for k,v in checks.items() if not v]
if failed:raise SystemExit("3.0.190 verification failed: "+", ".join(failed))
print("Prepared iCE OnHand 3.0.190: stale Test Scan can never interrupt an active physical count")
