from pathlib import Path

# Preserve 3.0.112, then move the monthly workflow to Import and shorten its labels.
base=Path('.github/prepare_30112.py')
exec(compile(base.read_text(),str(base),'exec'),{'__name__':'__main__','__file__':str(base)})

p=Path('app/src/main/java/com/iceinventory/onhand/MainActivity.java')
s=p.read_text()
s=s.replace('''        Button imp=button("⬇ Import TXT",1);imp.setTypeface(Typeface.DEFAULT,Typeface.BOLD);imp.setOnClickListener(v->startImportFormatFlow());''','''        Button imp=button("⬇ Import",1);imp.setTypeface(Typeface.DEFAULT,Typeface.BOLD);imp.setOnClickListener(v->showImportMenu());''',1)

marker='''    private void startImportFormatFlow() {'''
menu='''    private void showImportMenu() {
        String[] choices={"Petrosoft Monthly Inventory","Standard TXT Inventory"};
        new AlertDialog.Builder(this).setTitle("Import Inventory")
                .setItems(choices,(d,which)->{
                    if(which==0)startActivity(new Intent(this,MonthlyInventoryActivity.class));
                    else startImportFormatFlow();
                }).setNegativeButton("Cancel",null).show();
    }

'''+marker
if marker not in s: raise SystemExit('3.0.113 target missing: import flow')
s=s.replace(marker,menu,1)

monthly='''
        addExportSection(exportPanel,"MONTHLY CLIENT WORKFLOW");
        addExportButton(exportPanel,exportDialog,"Monthly POS Inventory — Prepare, Combine & Client Excel",12);
'''
if monthly not in s: raise SystemExit('3.0.113 target missing: monthly export section')
s=s.replace(monthly,'\n',1)
s=s.replace('''        if(which==12){startActivity(new Intent(this,MonthlyInventoryActivity.class));return;}\n''','',1)
s=s.replace('Onhand Inventory 3.0.112','Onhand Inventory 3.0.113',1)
if 'Onhand Inventory 3.0.113' not in s: raise SystemExit('3.0.113 visible version target missing')
p.write_text(s)

p=Path('app/build.gradle')
g=p.read_text().replace('versionCode 30112','versionCode 30113',1).replace("versionName '3.0.112'","versionName '3.0.113'",1)
if 'versionCode 30113' not in g or "versionName '3.0.113'" not in g: raise SystemExit('3.0.113 Gradle target missing')
p.write_text(g)

p=Path('app/src/main/AndroidManifest.xml')
m=p.read_text().replace('iCE Onhand 3.0.112','iCE Onhand 3.0.113',1)
if 'iCE Onhand 3.0.113' not in m: raise SystemExit('3.0.113 manifest target missing')
p.write_text(m)

checks={
    'monthly import first':'String[] choices={"Petrosoft Monthly Inventory","Standard TXT Inventory"}' in s,
    'short main import label':'button("⬇ Import",1)' in s,
    'removed from export':'MONTHLY CLIENT WORKFLOW' not in s,
    'removed export handler':'which==12' not in s,
    'separate monthly sections':all(v in Path('app/src/main/java/com/iceinventory/onhand/MonthlyInventoryActivity.java').read_text() for v in ['IMPORT CLIENT FILE','PREPARE COUNT FILES','AFTER PHYSICAL COUNT — EXPORT']),
}
missing=[k for k,v in checks.items() if not v]
if missing: raise SystemExit('3.0.113 verification failed: '+', '.join(missing))
print('Prepared iCE Onhand 3.0.113: Petrosoft workflow moved to Import with separate export controls')
