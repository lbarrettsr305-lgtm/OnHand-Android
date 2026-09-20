from pathlib import Path

# Preserve 3.0.125, then add explicit instructions and a safe Start New Monthly Project action.
base=Path('.github/prepare_30125.py')
exec(compile(base.read_text(),str(base),'exec'),{'__name__':'__main__','__file__':str(base)})

p=Path('app/build.gradle')
g=p.read_text().replace('versionCode 30125','versionCode 30126',1).replace("versionName '3.0.125'","versionName '3.0.126'",1)
if 'versionCode 30126' not in g or "versionName '3.0.126'" not in g: raise SystemExit('3.0.126 Gradle target missing')
p.write_text(g)

p=Path('app/src/main/java/com/iceinventory/onhand/MainActivity.java')
s=p.read_text().replace('Onhand Inventory 3.0.125','Onhand Inventory 3.0.126',1)
if 'Onhand Inventory 3.0.126' not in s: raise SystemExit('3.0.126 visible version target missing')

old='''            root.addView(monthly,mlp);
        }'''
new='''            root.addView(monthly,mlp);
            TextView monthlyHelp=text("MONTHLY PROJECT OPTIONS: Reopen/Resume above, or start a new monthly project below. The top + New button is for a standard inventory.",12,Color.WHITE,true);
            monthlyHelp.setPadding(dp(7),dp(3),dp(7),dp(3));
            monthlyHelp.setGravity(Gravity.CENTER);
            root.addView(monthlyHelp);
            Button newMonthly=button("＋ START NEW MONTHLY PROJECT",1);
            newMonthly.setTypeface(Typeface.DEFAULT,Typeface.BOLD);
            newMonthly.setTextSize(15);
            newMonthly.setOnClickListener(v->new AlertDialog.Builder(this)
                .setTitle("Start New Monthly Project?")
                .setMessage("This replaces the saved monthly recovery project. Previously exported files and inventory counts will not be deleted.")
                .setNegativeButton("Cancel",null)
                .setPositiveButton("Start New",(d,w)->{
                    mw.edit().clear().apply();
                    new java.io.File(getFilesDir(),"monthly_workflow_source.xlsx").delete();
                    Intent next=new Intent(this,MonthlyInventoryActivity.class);
                    startActivity(next);
                }).show());
            LinearLayout.LayoutParams nmp=new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT,dp(50));
            nmp.setMargins(0,dp(4),0,dp(5));
            root.addView(newMonthly,nmp);
        }'''
if old not in s: raise SystemExit('3.0.126 target missing: monthly options block')
s=s.replace(old,new,1)

checks={
 'new project button':'START NEW MONTHLY PROJECT' in s,
 'standard new distinction':'top + New button is for a standard inventory' in s,
 'replacement warning':'replaces the saved monthly recovery project' in s,
 'export safety':'Previously exported files and inventory counts will not be deleted.' in s,
 'recovery reset':'monthly_workflow_source.xlsx").delete()' in s,
}
missing=[k for k,v in checks.items() if not v]
if missing: raise SystemExit('3.0.126 verification failed: '+', '.join(missing))
p.write_text(s)

p=Path('app/src/main/AndroidManifest.xml')
m=p.read_text().replace('iCE Onhand 3.0.125','iCE Onhand 3.0.126',1)
if 'iCE Onhand 3.0.126' not in m: raise SystemExit('3.0.126 manifest version target missing')
p.write_text(m)
print('Prepared iCE Onhand 3.0.126: clear monthly project instructions and safe Start New Monthly Project')
