from pathlib import Path

# Preserve all proven 3.0.111 behavior, then add reusable POS-profile monthly processing.
base=Path('.github/prepare_30111.py')
exec(compile(base.read_text(),str(base),'exec'),{'__name__':'__main__','__file__':str(base)})

p=Path('app/src/main/java/com/iceinventory/onhand/MainActivity.java')
s=p.read_text()
old='''        addExportButton(exportPanel,exportDialog,"Highest Quantity — Excel",11);

        exportDialog[0]='''
new='''        addExportButton(exportPanel,exportDialog,"Highest Quantity — Excel",11);

        addExportSection(exportPanel,"MONTHLY CLIENT WORKFLOW");
        addExportButton(exportPanel,exportDialog,"Monthly POS Inventory — Prepare, Combine & Client Excel",12);

        exportDialog[0]='''
if old not in s: raise SystemExit('3.0.112 target missing: export panel')
s=s.replace(old,new,1)
old='''    private void handleExportChoice(int which){
        pendingAuditSort=0;'''
new='''    private void handleExportChoice(int which){
        pendingAuditSort=0;
        if(which==12){startActivity(new Intent(this,MonthlyInventoryActivity.class));return;}'''
if old not in s: raise SystemExit('3.0.112 target missing: export handler')
s=s.replace(old,new,1).replace('Onhand Inventory 3.0.111','Onhand Inventory 3.0.112',1)
if 'Onhand Inventory 3.0.112' not in s: raise SystemExit('3.0.112 visible version target missing')
p.write_text(s)

p=Path('app/src/main/AndroidManifest.xml')
m=p.read_text()
anchor='''        <activity
            android:name=".BatchMergeActivity"'''
addition='''        <activity
            android:name=".MonthlyInventoryActivity"
            android:exported="false"
            android:screenOrientation="unspecified" />
        <activity
            android:name=".BatchMergeActivity"'''
if anchor not in m: raise SystemExit('3.0.112 target missing: manifest activity')
m=m.replace(anchor,addition,1).replace('iCE Onhand 3.0.111','iCE Onhand 3.0.112',1)
p.write_text(m)

p=Path('app/build.gradle')
g=p.read_text().replace('versionCode 30111','versionCode 30112',1).replace("versionName '3.0.111'","versionName '3.0.112'",1)
if 'versionCode 30112' not in g or "versionName '3.0.112'" not in g: raise SystemExit('3.0.112 Gradle version target missing')
p.write_text(g)

checks={
    'monthly activity':Path('app/src/main/java/com/iceinventory/onhand/MonthlyInventoryActivity.java').exists(),
    'locked client headers':'{"GTIN","QUANTITY","CATEGORY_ID","RETAIL","DESCRIPTION","COST","DATE","TIME","SECTION"}' in Path('app/src/main/java/com/iceinventory/onhand/MonthlyClientXlsxWriter.java').read_text(),
    'Petrosoft profile':'Petrosoft / CStoreOffice' in Path('app/src/main/java/com/iceinventory/onhand/MonthlyInventoryActivity.java').read_text(),
    'three-way validation':'sourceTotal==combinedTotal&&combinedTotal==clientTotal' in Path('app/src/main/java/com/iceinventory/onhand/MonthlyInventoryActivity.java').read_text(),
    'client block':'Client export is blocked until validation passes' in Path('app/src/main/java/com/iceinventory/onhand/MonthlyInventoryActivity.java').read_text(),
    'export entry':'Monthly POS Inventory — Prepare, Combine & Client Excel' in s,
}
missing=[k for k,v in checks.items() if not v]
if missing: raise SystemExit('3.0.112 verification failed: '+', '.join(missing))
print('Prepared iCE Onhand 3.0.112: Petrosoft monthly profile, locked client Excel, three-way validation')
