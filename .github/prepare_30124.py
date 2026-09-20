from pathlib import Path

# Preserve 3.0.123, then add safe close/reopen and correction controls.
base=Path('.github/prepare_30123.py')
exec(compile(base.read_text(),str(base),'exec'),{'__name__':'__main__','__file__':str(base)})

p=Path('app/build.gradle')
g=p.read_text().replace('versionCode 30123','versionCode 30124',1).replace("versionName '3.0.123'","versionName '3.0.124'",1)
if 'versionCode 30124' not in g or "versionName '3.0.124'" not in g: raise SystemExit('3.0.124 Gradle target missing')
p.write_text(g)

p=Path('app/src/main/java/com/iceinventory/onhand/MainActivity.java')
s=p.read_text().replace('Onhand Inventory 3.0.123','Onhand Inventory 3.0.124',1)
if 'Onhand Inventory 3.0.124' not in s: raise SystemExit('3.0.124 visible version target missing')

old='boolean resumableMonthly=getSharedPreferences("monthly_workflow_state",MODE_PRIVATE).getBoolean("active",false);'
new='android.content.SharedPreferences mw=getSharedPreferences("monthly_workflow_state",MODE_PRIVATE);boolean resumableMonthly=mw.getBoolean("active",false);boolean archivedMonthly=mw.getBoolean("archived",false);'
if old not in s: raise SystemExit('3.0.124 target missing: resume state')
s=s.replace(old,new,1)

old='if(monthlyWorkflowMode||resumableMonthly) {'
new='if(monthlyWorkflowMode||resumableMonthly||archivedMonthly) {'
s=s.replace(old,new,1)

old='Button monthly=button(monthlyWorkflowMode?"↩ RETURN TO MONTHLY INVENTORY — STEP 5":"↩ RESUME MONTHLY INVENTORY WORKFLOW",2);'
new='Button monthly=button(monthlyWorkflowMode?"↩ RETURN TO MONTHLY INVENTORY — STEP 5":(resumableMonthly?"↩ RESUME MONTHLY INVENTORY WORKFLOW":"↩ REOPEN LAST MONTHLY PROJECT"),2);'
if old not in s: raise SystemExit('3.0.124 target missing: resume label')
s=s.replace(old,new,1)

old='monthly.setOnClickListener(v->{hideKeyboard();if(monthlyWorkflowMode)finish();else startActivity(new Intent(this,MonthlyInventoryActivity.class));});'
new='monthly.setOnClickListener(v->{hideKeyboard();if(monthlyWorkflowMode)finish();else{if(archivedMonthly)mw.edit().putBoolean("active",true).putBoolean("archived",false).putInt("stage",5).putBoolean("combined_exported",false).putBoolean("client_exported",false).putBoolean("audit_exported",false).apply();startActivity(new Intent(this,MonthlyInventoryActivity.class));}});'
if old not in s: raise SystemExit('3.0.124 target missing: reopen action')
s=s.replace(old,new,1)
p.write_text(s)

p=Path('app/src/main/java/com/iceinventory/onhand/MonthlyInventoryActivity.java')
s=p.read_text()

old='private Button chooseSource,saveMaster,saveOnHand,loadDevice,shareOnHand,chooseCounts,saveCombined,saveClient,saveAudit;'
new='private Button chooseSource,saveMaster,saveOnHand,loadDevice,shareOnHand,chooseCounts,saveCombined,saveClient,saveAudit,adjustCount,closeProject;'
if old not in s: raise SystemExit('3.0.124 target missing: buttons')
s=s.replace(old,new,1)

old='private boolean sourceReady,masterCreated,onHandCreated,deviceLoaded,countsReady,validated,countLaunchPending,restoringMonthly;'
new='private boolean sourceReady,masterCreated,onHandCreated,deviceLoaded,countsReady,validated,countLaunchPending,restoringMonthly,combinedExported,clientExported,auditExported;'
if old not in s: raise SystemExit('3.0.124 target missing: export flags')
s=s.replace(old,new,1)

old='saveAudit=button("Export Monthly Verification Report");saveAudit.setOnClickListener(v->create(SAVE_AUDIT,"text/plain",base()+" MONTHLY VERIFICATION-"+day()+".txt"));root.addView(saveAudit,params(54));'
new='''saveAudit=button("Export Monthly Verification Report");saveAudit.setOnClickListener(v->create(SAVE_AUDIT,"text/plain",base()+" MONTHLY VERIFICATION-"+day()+".txt"));root.addView(saveAudit,params(54));
        root.addView(section("CORRECTIONS / PROJECT CONTROL"));
        adjustCount=button("Return to Counting — Adjust This Device");adjustCount.setOnClickListener(v->adjustDeviceCount());root.addView(adjustCount,params(54));
        closeProject=button("8. Close Monthly Project");closeProject.setOnClickListener(v->confirmCloseProject());root.addView(closeProject,params(58));'''
if old not in s: raise SystemExit('3.0.124 target missing: project controls')
s=s.replace(old,new,1)

old='else if(request==SAVE_COMBINED)use.write(combinedText().getBytes(StandardCharsets.UTF_8));'
new='else if(request==SAVE_COMBINED){use.write(combinedText().getBytes(StandardCharsets.UTF_8));combinedExported=true;workflowPrefs().edit().putBoolean("combined_exported",true).apply();}'
if old not in s: raise SystemExit('3.0.124 target missing: combined export')
s=s.replace(old,new,1)

old='else if(request==SAVE_CLIENT){if(!validated)throw new Exception("Client export is blocked until validation passes");MonthlyClientXlsxWriter.writeClient(use,clientRows);}'
new='else if(request==SAVE_CLIENT){if(!validated)throw new Exception("Client export is blocked until validation passes");MonthlyClientXlsxWriter.writeClient(use,clientRows);clientExported=true;workflowPrefs().edit().putBoolean("client_exported",true).apply();}'
if old not in s: raise SystemExit('3.0.124 target missing: client export')
s=s.replace(old,new,1)

old='else if(request==SAVE_AUDIT)use.write(auditText().getBytes(StandardCharsets.UTF_8));'
new='else if(request==SAVE_AUDIT){use.write(auditText().getBytes(StandardCharsets.UTF_8));auditExported=true;workflowPrefs().edit().putBoolean("audit_exported",true).apply();}'
if old not in s: raise SystemExit('3.0.124 target missing: audit export')
s=s.replace(old,new,1)

old='private void loadCounts(Intent data)throws Exception{\n        if(!sourceReady)throw new Exception("Select the Petrosoft source file first");'
new='private void loadCounts(Intent data)throws Exception{\n        if(!sourceReady)throw new Exception("Select the Petrosoft source file first");combinedExported=clientExported=auditExported=false;workflowPrefs().edit().putBoolean("combined_exported",false).putBoolean("client_exported",false).putBoolean("audit_exported",false).apply();'
if old not in s: raise SystemExit('3.0.124 target missing: count revalidation')
s=s.replace(old,new,1)

old='deviceLoaded=true;deviceSessionId=id;String loadedName=base()+" "+day();'
new='deviceLoaded=true;deviceSessionId=id;workflowPrefs().edit().putLong("device_session_id",id).apply();String loadedName=base()+" "+day();'
if old not in s: raise SystemExit('3.0.124 target missing: persist device session')
s=s.replace(old,new,1)

old='if(w.getInt("stage",1)>=5)showNextStep();'
new='deviceSessionId=w.getLong("device_session_id",-1);combinedExported=w.getBoolean("combined_exported",false);clientExported=w.getBoolean("client_exported",false);auditExported=w.getBoolean("audit_exported",false);if(w.getInt("stage",1)>=5)showNextStep();'
if old not in s: raise SystemExit('3.0.124 target missing: restore controls')
s=s.replace(old,new,1)

old='saveAudit.setEnabled(countsReady);}'
new='saveAudit.setEnabled(countsReady);if(adjustCount!=null)adjustCount.setEnabled(deviceSessionId>0);if(closeProject!=null)closeProject.setEnabled(combinedExported&&clientExported&&auditExported);}'
if old not in s: raise SystemExit('3.0.124 target missing: enabled state tail')
s=s.replace(old,new,1)

anchor='''    private android.content.SharedPreferences workflowPrefs()'''
methods='''    private void adjustDeviceCount(){
        if(deviceSessionId<=0){fail("No count session is available on this device");return;}
        combinedExported=clientExported=auditExported=false;
        workflowPrefs().edit().putBoolean("combined_exported",false).putBoolean("client_exported",false).putBoolean("audit_exported",false).putInt("stage",5).apply();
        Intent count=new Intent(this,MainActivity.class);count.putExtra(EXTRA_SESSION_ID,deviceSessionId);count.putExtra(EXTRA_SESSION_NAME,base()+" "+day());count.putExtra(EXTRA_MONTHLY_WORKFLOW,true);startActivity(count);
        Toast.makeText(this,"Adjust the count, export this device again, then reselect all user files at Step 5.",Toast.LENGTH_LONG).show();
    }
    private void confirmCloseProject(){
        if(!(combinedExported&&clientExported&&auditExported)){fail("Export the combined TXT, Petrosoft client Excel, and verification report before closing");return;}
        new android.app.AlertDialog.Builder(this).setTitle("Close Monthly Project?")
            .setMessage("This removes the active Resume button but keeps a recoverable copy. If a count changes later, use Reopen Last Monthly Project and export all final reports again.")
            .setNegativeButton("Cancel",null).setPositiveButton("Close Project",(d,w)->closeMonthlyProject()).show();
    }
    private void closeMonthlyProject(){
        workflowPrefs().edit().putBoolean("active",false).putBoolean("archived",true).putInt("stage",8).apply();
        Toast.makeText(this,"Monthly project closed and archived. It can be reopened if a correction is needed.",Toast.LENGTH_LONG).show();finish();
    }

'''+anchor
if anchor not in s: raise SystemExit('3.0.124 target missing: methods')
s=s.replace(anchor,methods,1)

p.write_text(s)

p=Path('app/src/main/AndroidManifest.xml')
m=p.read_text().replace('iCE Onhand 3.0.123','iCE Onhand 3.0.124',1)
if 'iCE Onhand 3.0.124' not in m: raise SystemExit('3.0.124 manifest version target missing')
p.write_text(m)

checks={
 'close gated by all reports':'combinedExported&&clientExported&&auditExported' in s,
 'archive retained':'putBoolean("archived",true)' in s,
 'reopen available':'REOPEN LAST MONTHLY PROJECT' in Path('app/src/main/java/com/iceinventory/onhand/MainActivity.java').read_text(),
 'correction invalidates exports':'Adjust the count, export this device again' in s,
 'device session persisted':'putLong("device_session_id",id)' in s,
}
missing=[k for k,v in checks.items() if not v]
if missing: raise SystemExit('3.0.124 verification failed: '+', '.join(missing))
print('Prepared iCE Onhand 3.0.124: close/archive/reopen monthly project with correction safeguards')
