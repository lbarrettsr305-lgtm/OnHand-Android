from pathlib import Path

# Preserve 3.0.122, then add an explicit route from counting back to Monthly Step 5.
base=Path('.github/prepare_30122.py')
exec(compile(base.read_text(),str(base),'exec'),{'__name__':'__main__','__file__':str(base)})

p=Path('app/build.gradle')
g=p.read_text().replace('versionCode 30122','versionCode 30123',1).replace("versionName '3.0.122'","versionName '3.0.123'",1)
if 'versionCode 30123' not in g or "versionName '3.0.123'" not in g: raise SystemExit('3.0.123 Gradle target missing')
p.write_text(g)

p=Path('app/src/main/java/com/iceinventory/onhand/MainActivity.java')
s=p.read_text().replace('Onhand Inventory 3.0.122','Onhand Inventory 3.0.123',1)
if 'Onhand Inventory 3.0.123' not in s: raise SystemExit('3.0.123 visible version target missing')

old='private String pendingExportFileName="";'
new='private String pendingExportFileName="";\n    private boolean monthlyWorkflowMode;'
if old not in s: raise SystemExit('3.0.123 target missing: workflow field')
s=s.replace(old,new,1)

old='long requestedSession=getIntent()==null?-1L:getIntent().getLongExtra(MonthlyInventoryActivity.EXTRA_SESSION_ID,-1L);'
new='monthlyWorkflowMode=getIntent()!=null&&getIntent().getBooleanExtra(MonthlyInventoryActivity.EXTRA_MONTHLY_WORKFLOW,false);\n        long requestedSession=getIntent()==null?-1L:getIntent().getLongExtra(MonthlyInventoryActivity.EXTRA_SESSION_ID,-1L);'
if old not in s: raise SystemExit('3.0.123 target missing: workflow intent')
s=s.replace(old,new,1)

old='root.addView(sessionBar);'
new='''root.addView(sessionBar);
        if(monthlyWorkflowMode) {
            Button monthly=button("↩ RETURN TO MONTHLY INVENTORY — STEP 5",2);
            monthly.setTypeface(Typeface.DEFAULT,Typeface.BOLD);
            monthly.setTextSize(15);
            monthly.setOnClickListener(v->{hideKeyboard();finish();});
            LinearLayout.LayoutParams mlp=new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT,dp(50));
            mlp.setMargins(0,dp(5),0,dp(4));
            root.addView(monthly,mlp);
        }'''
if old not in s: raise SystemExit('3.0.123 target missing: session bar')
s=s.replace(old,new,1)

checks={
    'monthly mode flag':'monthlyWorkflowMode' in s,
    'return button':'RETURN TO MONTHLY INVENTORY — STEP 5' in s,
    'return preserves activity':'monthly.setOnClickListener(v->{hideKeyboard();finish();});' in s,
}
missing=[k for k,v in checks.items() if not v]
if missing: raise SystemExit('3.0.123 MainActivity verification failed: '+', '.join(missing))
p.write_text(s)

p=Path('app/src/main/java/com/iceinventory/onhand/MonthlyInventoryActivity.java')
s=p.read_text()

old='public static final String EXTRA_SESSION_ID="monthly_session_id",EXTRA_SESSION_NAME="monthly_session_name";'
new='public static final String EXTRA_SESSION_ID="monthly_session_id",EXTRA_SESSION_NAME="monthly_session_name",EXTRA_MONTHLY_WORKFLOW="monthly_workflow";'
if old not in s: raise SystemExit('3.0.123 target missing: monthly extras')
s=s.replace(old,new,1)

old='test.putExtra(EXTRA_SESSION_NAME,loadedName);'
new='test.putExtra(EXTRA_SESSION_NAME,loadedName);test.putExtra(EXTRA_MONTHLY_WORKFLOW,true);'
if old not in s: raise SystemExit('3.0.123 target missing: load count intent')
s=s.replace(old,new,1)

old='count.putExtra(EXTRA_SESSION_NAME,loadedName);'
new='count.putExtra(EXTRA_SESSION_NAME,loadedName);count.putExtra(EXTRA_MONTHLY_WORKFLOW,true);'
if old not in s: raise SystemExit('3.0.123 target missing: shared count intent')
s=s.replace(old,new,1)

if s.count('putExtra(EXTRA_MONTHLY_WORKFLOW,true)')!=2:
    raise SystemExit('3.0.123 verification failed: both monthly count entry paths must show return button')
p.write_text(s)

p=Path('app/src/main/AndroidManifest.xml')
m=p.read_text().replace('iCE Onhand 3.0.122','iCE Onhand 3.0.123',1)
if 'iCE Onhand 3.0.123' not in m: raise SystemExit('3.0.123 manifest version target missing')
p.write_text(m)

print('Prepared iCE Onhand 3.0.123: counting screen includes Return to Monthly Inventory — Step 5')


# Persist an in-progress monthly workflow so closing/stopping the app cannot strand the user.
p=Path('app/src/main/java/com/iceinventory/onhand/MainActivity.java')
s=p.read_text()
old='''        if(monthlyWorkflowMode) {
            Button monthly=button("↩ RETURN TO MONTHLY INVENTORY — STEP 5",2);
            monthly.setTypeface(Typeface.DEFAULT,Typeface.BOLD);
            monthly.setTextSize(15);
            monthly.setOnClickListener(v->{hideKeyboard();finish();});
            LinearLayout.LayoutParams mlp=new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT,dp(50));
            mlp.setMargins(0,dp(5),0,dp(4));
            root.addView(monthly,mlp);
        }'''
new='''        boolean resumableMonthly=getSharedPreferences("monthly_workflow_state",MODE_PRIVATE).getBoolean("active",false);
        if(monthlyWorkflowMode||resumableMonthly) {
            Button monthly=button(monthlyWorkflowMode?"↩ RETURN TO MONTHLY INVENTORY — STEP 5":"↩ RESUME MONTHLY INVENTORY WORKFLOW",2);
            monthly.setTypeface(Typeface.DEFAULT,Typeface.BOLD);
            monthly.setTextSize(15);
            monthly.setOnClickListener(v->{hideKeyboard();if(monthlyWorkflowMode)finish();else startActivity(new Intent(this,MonthlyInventoryActivity.class));});
            LinearLayout.LayoutParams mlp=new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT,dp(50));
            mlp.setMargins(0,dp(5),0,dp(4));
            root.addView(monthly,mlp);
        }'''
if old not in s: raise SystemExit('3.0.123 persistence target missing: resume button')
s=s.replace(old,new,1)
p.write_text(s)

p=Path('app/src/main/java/com/iceinventory/onhand/MonthlyInventoryActivity.java')
s=p.read_text()
s=s.replace('import java.io.BufferedReader;','import java.io.BufferedReader;\\nimport java.io.File;\\nimport java.io.FileInputStream;\\nimport java.io.FileOutputStream;',1)

old='private boolean sourceReady,masterCreated,onHandCreated,deviceLoaded,countsReady,validated,countLaunchPending;'
new='private boolean sourceReady,masterCreated,onHandCreated,deviceLoaded,countsReady,validated,countLaunchPending,restoringMonthly;'
if old not in s: raise SystemExit('3.0.123 persistence target missing: state')
s=s.replace(old,new,1)

old='setContentView(scroll);pendingSourceUri=incomingSource(getIntent());if(pendingSourceUri!=null){sourceName=displayName(pendingSourceUri);importSummary.setText("ATTACHMENT READY: "+sourceName+"\\nEnter the store name, then tap Import.");}setEnabledState();'
new='setContentView(scroll);pendingSourceUri=incomingSource(getIntent());if(pendingSourceUri!=null){sourceName=displayName(pendingSourceUri);importSummary.setText("ATTACHMENT READY: "+sourceName+"\\nEnter the store name, then tap Import.");}setEnabledState();if(pendingSourceUri==null)restoreMonthlyWorkflow();'
if old not in s: raise SystemExit('3.0.123 persistence target missing: restore startup')
s=s.replace(old,new,1)

old='InputStream in=getContentResolver().openInputStream(uri);if(in==null)throw new Exception("Could not open the Petrosoft Excel file");'
new='InputStream in="file".equals(uri.getScheme())?new FileInputStream(new File(uri.getPath())):getContentResolver().openInputStream(uri);if(in==null)throw new Exception("Could not open the Petrosoft Excel file");'
if old not in s: raise SystemExit('3.0.123 persistence target missing: source stream')
s=s.replace(old,new,1)

old='if(products.isEmpty())throw new Exception("No countable Petrosoft products were found");sourceReady=true;customer.setEnabled(false);showSource();setEnabledState();'
new='if(products.isEmpty())throw new Exception("No countable Petrosoft products were found");sourceReady=true;customer.setEnabled(false);if(!restoringMonthly)saveMonthlyWorkflow(uri);showSource();setEnabledState();'
if old not in s: raise SystemExit('3.0.123 persistence target missing: save source')
s=s.replace(old,new,1)

anchor='''    private MonthlyClientXlsxWriter.Product product('''
methods='''    private android.content.SharedPreferences workflowPrefs(){return getSharedPreferences("monthly_workflow_state",MODE_PRIVATE);}
    private File workflowSource(){return new File(getFilesDir(),"monthly_workflow_source.xlsx");}
    private void saveMonthlyWorkflow(Uri uri)throws Exception{
        File target=workflowSource();
        try(InputStream in=getContentResolver().openInputStream(uri);FileOutputStream out=new FileOutputStream(target)){
            if(in==null)throw new Exception("Could not preserve the Price Management file");
            byte[] b=new byte[32768];int n;while((n=in.read(b))>0)out.write(b,0,n);
        }
        workflowPrefs().edit().putBoolean("active",true).putInt("stage",1).putString("store",storeName()).putString("date",date.getText().toString().trim()).putString("source_name",sourceName).apply();
    }
    private void restoreMonthlyWorkflow(){
        android.content.SharedPreferences w=workflowPrefs();File source=workflowSource();
        if(!w.getBoolean("active",false)||!source.isFile())return;
        customer.setText(w.getString("store",""));date.setText(w.getString("date",date.getText().toString()));
        restoringMonthly=true;
        try{
            String savedName=w.getString("source_name","Price Management Excel");
            loadPetrosoft(Uri.fromFile(source));sourceName=savedName;showSource();
            if(w.getInt("stage",1)>=5)showNextStep();
            Toast.makeText(this,"Monthly workflow restored. Continue from the highlighted step.",Toast.LENGTH_LONG).show();
        }catch(Exception e){fail("Could not restore monthly workflow: "+(e.getMessage()==null?e.toString():e.getMessage()));}
        finally{restoringMonthly=false;}
    }

'''+anchor
if anchor not in s: raise SystemExit('3.0.123 persistence target missing: method anchor')
s=s.replace(anchor,methods,1)

old='private void showNextStep(){nextStep.setText('
new='private void showNextStep(){workflowPrefs().edit().putBoolean("active",true).putInt("stage",5).putString("store",storeName()).putString("date",date.getText().toString().trim()).apply();nextStep.setText('
if old not in s: raise SystemExit('3.0.123 persistence target missing: stage 5')
s=s.replace(old,new,1)

checks={
    'persistent source copy':'monthly_workflow_source.xlsx' in s,
    'workflow restore':'restoreMonthlyWorkflow()' in s,
    'stage five restore':'getInt("stage",1)>=5' in s,
    'main screen resume':'RESUME MONTHLY INVENTORY WORKFLOW' in Path('app/src/main/java/com/iceinventory/onhand/MainActivity.java').read_text(),
}
missing=[k for k,v in checks.items() if not v]
if missing: raise SystemExit('3.0.123 persistence verification failed: '+', '.join(missing))
p.write_text(s)
print('Added persistent resume/override for an in-progress monthly workflow')
