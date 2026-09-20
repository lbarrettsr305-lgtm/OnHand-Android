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
