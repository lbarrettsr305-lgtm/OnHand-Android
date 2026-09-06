from pathlib import Path

base=Path('.github/prepare_3086.py')
exec(compile(base.read_text(),str(base),'exec'),{'__name__':'__main__','__file__':str(base)})

p=Path('app/src/main/java/com/iceinventory/onhand/FormatConfigActivity.java')
s=p.read_text()

old='''        Button save=button(MODE_EXPORT.equals(mode)?"CONTINUE TO SAVE":"CONTINUE TO FILE");save.setTextColor(Color.WHITE);save.setTypeface(Typeface.DEFAULT,Typeface.BOLD);save.setBackgroundColor(green());save.setOnClickListener(v->saveAndFinish());
        LinearLayout.LayoutParams sp=new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT,dp(54));sp.setMargins(0,dp(12),0,0);body.addView(save,sp);

        defaults=button("Reset standard order");defaults.setOnClickListener(v->resetDefaults());defaults.setEnabled(false);
'''
new='''        Button save=button("CONTINUE TO FILE");save.setTextColor(Color.WHITE);save.setTypeface(Typeface.DEFAULT,Typeface.BOLD);save.setBackgroundColor(green());save.setOnClickListener(v->saveAndFinish());

        defaults=button("Reset standard order");defaults.setOnClickListener(v->resetDefaults());defaults.setEnabled(false);
'''
if old not in s:raise SystemExit('3.0.87 target missing: scrolling continue button')
s=s.replace(old,new,1)

old='''        scroll.addView(body);root.addView(scroll,new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT,0,1));setContentView(root);
        renderRows();
'''
new='''        scroll.addView(body);root.addView(scroll,new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT,0,1));
        LinearLayout.LayoutParams sp=new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT,dp(58));sp.setMargins(dp(12),dp(6),dp(12),dp(10));root.addView(save,sp);
        setContentView(root);
        renderRows();
'''
if old not in s:raise SystemExit('3.0.87 target missing: screen footer')
s=s.replace(old,new,1)
p.write_text(s)

p=Path('app/src/main/java/com/iceinventory/onhand/MainActivity.java')
s=p.read_text().replace('Onhand Inventory 3.0.86','Onhand Inventory 3.0.87')
if 'Onhand Inventory 3.0.87' not in s:raise SystemExit('3.0.87 target missing: title version')
p.write_text(s)

p=Path('app/build.gradle');s=p.read_text().replace('versionCode 30086','versionCode 30087',1).replace("versionName '3.0.86'","versionName '3.0.87'",1)
if 'versionCode 30087' not in s or "versionName '3.0.87'" not in s:raise SystemExit('3.0.87 target missing: Gradle version')
p.write_text(s)

p=Path('app/src/main/AndroidManifest.xml');s=p.read_text().replace('iCE Onhand 3.0.86','iCE Onhand 3.0.87')
if 'iCE Onhand 3.0.87' not in s:raise SystemExit('3.0.87 target missing: manifest version')
p.write_text(s)

fmt=Path('app/src/main/java/com/iceinventory/onhand/FormatConfigActivity.java').read_text()
checks={
    'fixed label':'Button save=button("CONTINUE TO FILE")',
    'footer placement':'root.addView(save,sp)',
    'scroll remains flexible':'root.addView(scroll,new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT,0,1))',
}
missing=[k for k,v in checks.items() if v not in fmt]
if missing:raise SystemExit('3.0.87 verification failed: '+', '.join(missing))
if 'body.addView(save,sp)' in fmt:raise SystemExit('3.0.87 verification failed: continue button still scrolls')
print('Prepared iCE Onhand 3.0.87: fixed Continue to File footer for Import and Export')
