from pathlib import Path
import re

# Preserve every verified 3.0.95 feature first.
base=Path('.github/prepare_3095.py')
exec(compile(base.read_text(),str(base),'exec'),{'__name__':'__main__','__file__':str(base)})

# -----------------------------------------------------------------------------
# 3.0.96
# - Move multi-user combine/verify access under the main Export menu.
# - Designate one saved operator as the Master Report User.
# - Restrict combined verification reporting to that master operator.
# - Keep TXT combined/audit exports and add the branded professional XLSX report.
# -----------------------------------------------------------------------------
p=Path('app/src/main/java/com/iceinventory/onhand/MainActivity.java')
s=p.read_text()

old='''    private static final String KEY_USER_NAME="export_user_name";\n'''
new='''    private static final String KEY_USER_NAME="export_user_name";\n    private static final String KEY_MASTER_USER="master_report_user";\n'''
if old not in s:raise SystemExit('3.0.96 target missing: user name key')
s=s.replace(old,new,1)

old='''        Button userNameButton=button(userNameButtonLabel(),0);\n        userNameButton.setOnClickListener(v->promptUserName(false));\n        box.addView(userNameButton,new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT,dp(50)));\n'''
new='''        Button userNameButton=button(userNameButtonLabel(),0);\n        userNameButton.setOnClickListener(v->promptUserName(false));\n        box.addView(userNameButton,new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT,dp(50)));\n        Button masterUserButton=button(masterUserButtonLabel(),0);\n        masterUserButton.setOnClickListener(v->setCurrentUserAsMaster());\n        box.addView(masterUserButton,new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT,dp(50)));\n'''
if old not in s:raise SystemExit('3.0.96 target missing: User / Export option block')
s=s.replace(old,new,1)

old='''        TextView batchesTitle=text("Multiple User Batches",16,gold(),true);batchesTitle.setPadding(dp(6),dp(8),0,dp(2));box.addView(batchesTitle);\n        Button combineBatches=button("Combine and Verify User Batches",0);\n        combineBatches.setOnClickListener(v->startActivity(new Intent(this,BatchMergeActivity.class)));\n        box.addView(combineBatches,new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT,dp(52)));\n'''
if old not in s:raise SystemExit('3.0.96 target missing: duplicate Options batch button')
s=s.replace(old,'',1)

anchor='''    private String userNameButtonLabel() {\n        String n=savedUserName();\n        return n.isEmpty()?"Set User Name":"User Name: "+n;\n    }\n\n'''
helpers='''    private String userNameButtonLabel() {\n        String n=savedUserName();\n        return n.isEmpty()?"Set User Name":"User Name: "+n;\n    }\n\n    private String savedMasterUserName() {\n        String n=prefs().getString(KEY_MASTER_USER,"");\n        return n==null?"":n.trim();\n    }\n\n    private String masterUserButtonLabel() {\n        String n=savedMasterUserName();\n        return n.isEmpty()?"Set Current User as Master Report User":"Master Report User: "+n;\n    }\n\n    private void setCurrentUserAsMaster() {\n        String current=savedUserName();\n        if(current.isEmpty()){toast("Set User Name first");promptUserName(false);return;}\n        String existing=savedMasterUserName();\n        String title=existing.isEmpty()?"Set Master Report User":"Change Master Report User";\n        String message=(existing.isEmpty()?"Designate ":"Replace "+existing+" with ")+current+" as the Master Report User?\\n\\nThe Master Report User is the authorized operator for combined batch verification and official reconciliation reports on this device.";\n        new AlertDialog.Builder(this).setTitle(title).setMessage(message)\n                .setPositiveButton("Set Master",(d,w)->{prefs().edit().putString(KEY_MASTER_USER,current).apply();toast("Master Report User: "+current);})\n                .setNegativeButton("Cancel",null).show();\n    }\n\n    private void openBatchMergeForMaster() {\n        String master=savedMasterUserName();\n        String current=savedUserName();\n        if(master.isEmpty()){\n            new AlertDialog.Builder(this).setTitle("Master Report User Not Set")\n                    .setMessage("Before combined reports can be run, designate the current operator as Master Report User in Options > User / Export.")\n                    .setPositiveButton("Open Options",(d,w)->showOptions()).setNegativeButton("Cancel",null).show();\n            return;\n        }\n        if(current.isEmpty()){toast("Set User Name first");promptUserName(false);return;}\n        if(!master.equalsIgnoreCase(current)){\n            new AlertDialog.Builder(this).setTitle("Master Report User Required")\n                    .setMessage("Combined verification reports are restricted to "+master+". Current user: "+current+".")\n                    .setPositiveButton("OK",null).show();\n            return;\n        }\n        startActivity(new Intent(this,BatchMergeActivity.class));\n    }\n\n'''
if anchor not in s:raise SystemExit('3.0.96 target missing: userNameButtonLabel helper')
s=s.replace(anchor,helpers,1)

scope='''    private void showExportScopeDialog() {
        int next=db.nextBatchNumber(sessionId);
        String batch=String.format(Locale.US,"%02d",next);
        String[] choices={"Export New Counts Only (Batch "+batch+")","Export Complete Inventory — TXT","Export Complete Inventory — Excel (.xlsx)","Re-export Previous Batch","Combine & Verify User Batches","Internet Items With Pictures","Location Quantity Report"};
        new AlertDialog.Builder(this).setTitle("Export Items").setItems(choices,(d,which)->{
            if(which==0){pendingExportExcel=false;pendingExportInternetOnly=false;pendingExportLocationQuantityReport=false;beginNewBatchExport();return;}
            if(which==1){pendingExportExcel=false;pendingExportInternetOnly=false;pendingExportLocationQuantityReport=false;beginCompleteInventoryExport();return;}
            if(which==2){pendingExportExcel=true;pendingExportInternetOnly=false;pendingExportLocationQuantityReport=false;beginCompleteInventoryExport();return;}
            if(which==3){pendingExportExcel=false;pendingExportInternetOnly=false;pendingExportLocationQuantityReport=false;showBatchReExportDialog();return;}
            if(which==4){resetBatchExportState();openBatchMergeForMaster();return;}
            resetBatchExportState();
            if(which==5){pendingExportExcel=false;pendingExportInternetOnly=true;pendingExportLocationQuantityReport=false;if(internetItemCount()==0){toast("No internet items to export");return;}startExportFormatFlow();return;}
            pendingExportExcel=false;pendingExportInternetOnly=false;pendingExportLocationQuantityReport=true;startExportFormatFlow();
        }).setNegativeButton("Cancel",null).show();
    }
'''
pat=r'''    private void showExportScopeDialog\(\) \{.*?\n    \}\n(?=\n    private void beginNewBatchExport\(\))'''
s,n=re.subn(pat,lambda m:scope,s,count=1,flags=re.S)
if n!=1:raise SystemExit('3.0.96 target missing: Export Items menu')

s=s.replace('Onhand Inventory 3.0.95','Onhand Inventory 3.0.96')
if 'Onhand Inventory 3.0.96' not in s:raise SystemExit('3.0.96 target missing: visible version')
p.write_text(s)

p=Path('app/build.gradle')
g=p.read_text().replace('versionCode 30095','versionCode 30096',1).replace("versionName '3.0.95'","versionName '3.0.96'",1)
if 'versionCode 30096' not in g or "versionName '3.0.96'" not in g:raise SystemExit('3.0.96 target missing: Gradle version')
p.write_text(g)

p=Path('app/src/main/AndroidManifest.xml')
m=p.read_text().replace('iCE Onhand 3.0.95','iCE Onhand 3.0.96')
if 'iCE Onhand 3.0.96' not in m:raise SystemExit('3.0.96 target missing: manifest version')
p.write_text(m)

main=Path('app/src/main/java/com/iceinventory/onhand/MainActivity.java').read_text()
merge=Path('app/src/main/java/com/iceinventory/onhand/BatchMergeActivity.java').read_text()
xlsx=Path('app/src/main/java/com/iceinventory/onhand/ProfessionalCombinedXlsxWriter.java').read_text()
checks={
    'combined reports are under Export':'"Combine & Verify User Batches"' in main and 'openBatchMergeForMaster()' in main,
    'old Options combine button removed':'button("Combine and Verify User Batches",0)' not in main,
    'master report key':'KEY_MASTER_USER="master_report_user"' in main,
    'master option button':'masterUserButtonLabel()' in main and 'setCurrentUserAsMaster()' in main,
    'master gate':'Master Report User Required' in main and 'equalsIgnoreCase(current)' in main,
    'TXT default preserved':'Export New Counts Only (Batch ' in main and 'pendingExportExcel=false' in main,
    'professional Excel button':'Export Professional Combined Report — Excel' in merge,
    'Excel MIME':'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' in merge,
    'company branding':'Ice Inventory LLC' in merge and 'ice_inventory_logo_3066' in xlsx,
    'formal note':'Formal Verification Note' in xlsx and 'does not independently certify the physical accuracy' in xlsx,
    'master recorded in workbook':'Master Report User' in xlsx,
    'verification sheet':'name=\\"Verification\\"' in xlsx,
    'combined sheet':'name=\\"Combined Inventory\\"' in xlsx,
    'source-file audit':'Source Batch Audit' in xlsx,
    'source-derived report naming':'sourceInventoryName()' in merge,
}
missing=[k for k,v in checks.items() if not v]
if missing:raise SystemExit('3.0.96 verification failed: '+', '.join(missing))
print('Prepared iCE Onhand 3.0.96: Export-based combined reports + designated Master Report User + professional branded Excel verification workbook')
