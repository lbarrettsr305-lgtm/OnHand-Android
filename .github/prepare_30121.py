from pathlib import Path

# Preserve 3.0.120, then show the next physical-count step immediately after sharing.
base=Path('.github/prepare_30120.py')
exec(compile(base.read_text(),str(base),'exec'),{'__name__':'__main__','__file__':str(base)})

p=Path('app/build.gradle')
g=p.read_text().replace('versionCode 30120','versionCode 30121',1).replace("versionName '3.0.120'","versionName '3.0.121'",1)
if 'versionCode 30121' not in g or "versionName '3.0.121'" not in g: raise SystemExit('3.0.121 Gradle target missing')
p.write_text(g)

p=Path('app/src/main/java/com/iceinventory/onhand/MainActivity.java')
s=p.read_text().replace('Onhand Inventory 3.0.120','Onhand Inventory 3.0.121',1)
if 'Onhand Inventory 3.0.121' not in s: raise SystemExit('3.0.121 visible version target missing')
p.write_text(s)

p=Path('app/src/main/AndroidManifest.xml')
m=p.read_text().replace('iCE Onhand 3.0.120','iCE Onhand 3.0.121',1)
if 'iCE Onhand 3.0.121' not in m: raise SystemExit('3.0.121 manifest version target missing')
p.write_text(m)

p=Path('app/src/main/java/com/iceinventory/onhand/MonthlyInventoryActivity.java')
s=p.read_text()
if 'import android.view.View;' not in s:
    s=s.replace('import android.view.Gravity;\n','import android.view.Gravity;\nimport android.view.View;\n',1)

old='private TextView importSummary,status;'
new='private TextView importSummary,status,nextStep;'
if old not in s: raise SystemExit('3.0.121 target missing: text fields')
s=s.replace(old,new,1)

old='shareOnHand=button("4. Share File With All Users");shareOnHand.setOnClickListener(v->shareOnHand());root.addView(shareOnHand,params(54));'
new='shareOnHand=button("4. Share File With All Users");shareOnHand.setOnClickListener(v->shareOnHand());root.addView(shareOnHand,params(54));nextStep=text("",15,Color.BLACK);nextStep.setPadding(dp(12),dp(10),dp(12),dp(10));nextStep.setBackgroundColor(Color.rgb(255,193,7));nextStep.setVisibility(View.GONE);root.addView(nextStep);'
if old not in s: raise SystemExit('3.0.121 target missing: share button')
s=s.replace(old,new,1)

old='onHandUri=null;'
new='onHandUri=null;if(nextStep!=null)nextStep.setVisibility(View.GONE);'
if old not in s: raise SystemExit('3.0.121 target missing: source reset')
s=s.replace(old,new,1)

old='startActivity(Intent.createChooser(i,"Share with users — Quick Share, Bluetooth, Drive or email"));}'
new='showNextStep();startActivity(Intent.createChooser(i,"Share with users — Quick Share, Bluetooth, Drive or email"));}'
if old not in s: raise SystemExit('3.0.121 target missing: share chooser')
s=s.replace(old,new,1)

anchor='''    private void setEnabledState(){'''
method='''    private void showNextStep(){nextStep.setText("NEXT STEP\\nUsers import the shared file and complete the physical count.\\nWhen all users finish, press 5. Select All User Count Files.");nextStep.setVisibility(View.VISIBLE);chooseCounts.setBackgroundColor(Color.rgb(255,193,7));chooseCounts.setTextColor(Color.BLACK);status.setText("FILE SHARED / READY FOR USERS\\n\\nNext: complete the physical inventory. After all users export their counts, press 5. Select All User Count Files.");status.setTextColor(Color.rgb(180,235,255));}

'''+anchor
if anchor not in s: raise SystemExit('3.0.121 target missing: enabled state')
s=s.replace(anchor,method,1)

checks={
    'next-step panel':'NEXT STEP\\nUsers import the shared file' in s,
    'user count instruction':'press 5. Select All User Count Files' in s,
    'highlight count button':'chooseCounts.setBackgroundColor(Color.rgb(255,193,7))' in s,
    'next step after share':'showNextStep();startActivity(Intent.createChooser' in s,
}
missing=[k for k,v in checks.items() if not v]
if missing: raise SystemExit('3.0.121 verification failed: '+', '.join(missing))
p.write_text(s)
print('Prepared iCE Onhand 3.0.121: visible next step after sharing and highlighted user-count selection')
