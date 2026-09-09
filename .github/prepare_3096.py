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
# - Accept compatible external tab-delimited files regardless of filename,
#   store name, user prefix, batch number, or file extension.
# - Keep TXT combined/audit exports and add a branded professional XLSX report.
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

# Professional combined-report activity. Filename is audit metadata only: compatible
# external files are validated by tab-delimited headers and never rejected for naming.
p=Path('app/src/main/java/com/iceinventory/onhand/BatchMergeActivity.java')
m=p.read_text()
m=m.replace('private static final int REQ_FILES=4101,REQ_SAVE=4102,REQ_REPORT=4103;','private static final int REQ_FILES=4101,REQ_SAVE=4102,REQ_REPORT=4103,REQ_XLSX=4104;',1)
m=m.replace('private static final String KEY_USER_NAME="export_user_name";','private static final String KEY_USER_NAME="export_user_name";\n    private static final String KEY_MASTER_USER="master_report_user";',1)
m=m.replace('String fileName="",userName="";','String fileName="",userName="",sourceType="";',1)
m=m.replace('private Button save,report;','private Button save,report,excel;',1)
m=m.replace('Select every user\'s tab-delimited batch file. Matching barcodes will be summed into one verified batch. A separate verification report proves the selected files loaded and the source quantity total equals the combined quantity total.','Select iCE OnHand batches or compatible external tab-delimited files. Filenames, file extensions, store names, user prefixes, and batch numbers are not required. Barcode and Quantity headers are required; matching barcodes will be summed and reconciled before export.',1)
m=m.replace('Button choose=button("Select User Batch Files")','Button choose=button("Select Batch / Source Files")',1)
m=m.replace('save=button("Export Verified Combined Batch")','save=button("Export Combined Batch — TXT")',1)
m=m.replace('report=button("Export Verification Report")','report=button("Export Verification Report — TXT")',1)
old='''        report=button("Export Verification Report — TXT");report.setEnabled(false);report.setOnClickListener(v->saveReport());LinearLayout.LayoutParams rp=new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT,dp(54));rp.setMargins(0,dp(8),0,0);root.addView(report,rp);\n'''
new='''        report=button("Export Verification Report — TXT");report.setEnabled(false);report.setOnClickListener(v->saveReport());LinearLayout.LayoutParams rp=new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT,dp(54));rp.setMargins(0,dp(8),0,0);root.addView(report,rp);\n        excel=button("Export Professional Combined Report — Excel");excel.setEnabled(false);excel.setOnClickListener(v->saveProfessionalXlsx());LinearLayout.LayoutParams xp=new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT,dp(54));xp.setMargins(0,dp(8),0,0);root.addView(excel,xp);\n'''
if old not in m:raise SystemExit('3.0.96 target missing: report button block')
m=m.replace(old,new,1)
m=m.replace('i.setType("text/*")','i.setType("*/*")',1)
m=m.replace('else if(request==REQ_REPORT)writeVerificationReport(data.getData());','else if(request==REQ_REPORT)writeVerificationReport(data.getData());else if(request==REQ_XLSX)writeProfessionalXlsx(data.getData());',1)
m=m.replace('verified=false;save.setEnabled(false);report.setEnabled(false);','verified=false;save.setEnabled(false);report.setEnabled(false);excel.setEnabled(false);',1)
m=m.replace('for(BatchStat s:sourceStats)m.append("• ").append(s.userName.isEmpty()?"User prefix missing":s.userName).append(" — ").append(s.quantity).append(" units — ").append(s.rows).append(" rows\\n");','for(BatchStat s:sourceStats)m.append("• ").append(s.sourceType).append(" — ").append(s.userName.isEmpty()?"External / Unidentified":s.userName).append(" — ").append(s.quantity).append(" units — ").append(s.rows).append(" rows\\n");',1)
m=m.replace('save.setEnabled(verified);report.setEnabled(verified);','save.setEnabled(verified);report.setEnabled(verified);excel.setEnabled(verified);',1)
m=m.replace('BatchStat stat=new BatchStat();stat.fileName=displayName(uri);stat.userName=userPrefix(stat.fileName);','BatchStat stat=new BatchStat();stat.fileName=displayName(uri);stat.userName=userPrefix(stat.fileName);stat.sourceType=stat.userName.isEmpty()?"External Tab-Delimited":"iCE OnHand Batch";',1)
m=m.replace('prefixedName("Combined_Verified_Batch.txt")','prefixedName(sourceInventoryName()+"_Combined_Verified_Batch.txt")',1)
m=m.replace('prefixedName("Combined_Batch_Verification_Report.txt")','prefixedName(sourceInventoryName()+"_Combined_Batch_Verification_Report.txt")',1)

marker='''    private void writeCombined(Uri uri){'''
methods='''    private void saveProfessionalXlsx(){if(!verified)return;Intent i=new Intent(Intent.ACTION_CREATE_DOCUMENT);i.addCategory(Intent.CATEGORY_OPENABLE);i.setType("application/vnd.openxmlformats-officedocument.spreadsheetml.sheet");String stamp=new SimpleDateFormat("yyyy-MM-dd_HHmm",Locale.US).format(new Date());i.putExtra(Intent.EXTRA_TITLE,prefixedName(sourceInventoryName()+"_Combined_Verification_"+stamp+".xlsx"));startActivityForResult(i,REQ_XLSX);}\n\n    private void writeProfessionalXlsx(Uri uri){\n        if(uri==null||!verified)return;\n        try(OutputStream os=getContentResolver().openOutputStream(uri)){\n            if(os==null)throw new Exception("Could not create Excel report");\n            ArrayList<ProfessionalCombinedXlsxWriter.SourceRow> sources=new ArrayList<>();\n            for(BatchStat s:sourceStats)sources.add(new ProfessionalCombinedXlsxWriter.SourceRow(s.sourceType,s.userName.isEmpty()?"External / Unidentified":s.userName,s.fileName,s.rows,s.quantity));\n            ArrayList<ProfessionalCombinedXlsxWriter.CombinedRow> rows=new ArrayList<>();\n            for(Total t:combined.values())rows.add(new ProfessionalCombinedXlsxWriter.CombinedRow(t.barcode,t.description,t.price,t.quantity));\n            ProfessionalCombinedXlsxWriter.write(this,os,sourceInventoryName(),savedMasterUserName(),sources,rows,sourceGrandTotal,outputTotal,verified,new Date());\n            status.append("\\n\\nProfessional Ice Inventory LLC Excel verification report exported successfully.");\n        }catch(Exception e){status.append("\\n\\nExcel report failed: "+e.getMessage());}\n    }\n\n'''
if marker not in m:raise SystemExit('3.0.96 target missing: writeCombined marker')
m=m.replace(marker,methods+marker,1)

m=m.replace('b.append("iCE OnHand Combined Batch Verification Report\\r\\n");','b.append("Ice Inventory LLC\\r\\n");\n        b.append("iCE OnHand Combined Batch Verification Report\\r\\n");\n        b.append("Report / Inventory\\t").append(clean(sourceInventoryName())).append("\\r\\n");\n        b.append("Master Report User\\t").append(clean(savedMasterUserName())).append("\\r\\n");',1)
m=m.replace('b.append("User\\tSource Batch File\\tRows\\tQuantity\\r\\n");\n        for(BatchStat s:sourceStats)b.append(clean(s.userName.isEmpty()?"USER PREFIX MISSING":s.userName)).append(\'\\t\').append(clean(s.fileName)).append(\'\\t\').append(s.rows).append(\'\\t\').append(s.quantity).append("\\r\\n");','b.append("Source Type\\tUser / Operator\\tSource File\\tRows\\tQuantity\\r\\n");\n        for(BatchStat s:sourceStats)b.append(clean(s.sourceType)).append(\'\\t\').append(clean(s.userName.isEmpty()?"External / Unidentified":s.userName)).append(\'\\t\').append(clean(s.fileName)).append(\'\\t\').append(s.rows).append(\'\\t\').append(s.quantity).append("\\r\\n");',1)
m=m.replace('b.append("5. PASS requires loaded files = selected files and Source Grand Total = Combined Grand Total.\\r\\n");','b.append("5. PASS requires loaded files = selected files and Source Grand Total = Combined Grand Total.\\r\\n");\n        b.append("\\r\\nFormal Verification Note\\r\\n");\n        b.append("Ice Inventory LLC certifies that this report was generated by the designated Master Report User using the source files listed above. A PASS confirms computational reconciliation of the selected electronic files: all selected files loaded, matching barcodes were consolidated, and source and combined grand totals match exactly. This verification does not independently certify the physical accuracy of the underlying inventory counts.\\r\\n");',1)

helper='''    private String savedUserName(){String n=getSharedPreferences(SETTINGS,MODE_PRIVATE).getString(KEY_USER_NAME,"");return n==null?"":n.trim();}\n'''
replacement='''    private String savedUserName(){String n=getSharedPreferences(SETTINGS,MODE_PRIVATE).getString(KEY_USER_NAME,"");return n==null?"":n.trim();}\n    private String savedMasterUserName(){String n=getSharedPreferences(SETTINGS,MODE_PRIVATE).getString(KEY_MASTER_USER,"");return n==null?"":n.trim();}\n    private String sourceInventoryName(){\n        String candidate="";\n        for(BatchStat s:sourceStats){\n            if(!"iCE OnHand Batch".equals(s.sourceType))continue;\n            String n=s.fileName==null?"":s.fileName.trim();int p=n.indexOf(" - ");if(p>=0)n=n.substring(p+3);\n            n=n.replaceFirst("(?i)_Batch\\\\d+.*$","").replaceFirst("(?i)_COMPLETE.*$","").replaceFirst("(?i)\\\\.(txt|xlsx|csv)$","");\n            n=safeFilePart(n).replace(\' \',\'_\');if(n.isEmpty())continue;\n            if(candidate.isEmpty())candidate=n;else if(!candidate.equalsIgnoreCase(n))return "Combined_Inventory";\n        }\n        return candidate.isEmpty()?"Combined_Inventory":candidate;\n    }\n'''
if helper not in m:raise SystemExit('3.0.96 target missing: saved user helper')
m=m.replace(helper,replacement,1)
p.write_text(m)

p=Path('app/build.gradle')
g=p.read_text().replace('versionCode 30095','versionCode 30096',1).replace("versionName '3.0.95'","versionName '3.0.96'",1)
if 'versionCode 30096' not in g or "versionName '3.0.96'" not in g:raise SystemExit('3.0.96 target missing: Gradle version')
p.write_text(g)

p=Path('app/src/main/AndroidManifest.xml')
a=p.read_text().replace('iCE Onhand 3.0.95','iCE Onhand 3.0.96')
if 'iCE Onhand 3.0.96' not in a:raise SystemExit('3.0.96 target missing: manifest version')
p.write_text(a)

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
    'external filenames unrestricted':'i.setType("*/*")' in merge and 'Filenames, file extensions, store names, user prefixes, and batch numbers are not required' in merge,
    'content header validation':'missing Barcode or Quantity header' in merge,
    'external source audit':'External Tab-Delimited' in merge and 'Source Type\\tUser / Operator\\tSource File' in merge,
    'professional Excel button':'Export Professional Combined Report — Excel' in merge,
    'Excel MIME':'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' in merge,
    'company branding':'Ice Inventory LLC' in merge and 'ice_inventory_logo_3066' in xlsx,
    'formal note':'Formal Verification Note' in xlsx and 'does not independently certify the physical accuracy' in xlsx,
    'master recorded in workbook':'Master Report User' in xlsx,
    'verification sheet':'Verification' in xlsx,
    'combined sheet':'Combined Inventory' in xlsx,
    'source-file audit':'Source Batch Audit' in xlsx,
    'source-derived report naming':'sourceInventoryName()' in merge,
}
missing=[k for k,v in checks.items() if not v]
if missing:raise SystemExit('3.0.96 verification failed: '+', '.join(missing))
print('Prepared iCE Onhand 3.0.96: Export-based combined reports + Master Report User + external tab-delimited compatibility + branded Excel reconciliation workbook')
