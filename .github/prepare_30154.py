from pathlib import Path

base = Path('.github/prepare_30153.py')
exec(compile(base.read_text(), str(base), 'exec'), {'__name__': '__main__', '__file__': str(base)})


def rep(path, old, new, label):
    p = Path(path)
    s = p.read_text()
    if s.count(old) != 1:
        raise SystemExit('3.0.154 expected one target for ' + label)
    p.write_text(s.replace(old, new, 1))


rep('app/build.gradle', 'versionCode 30153', 'versionCode 30154', 'Gradle code')
rep('app/build.gradle', "versionName '3.0.153'", "versionName '3.0.154'", 'Gradle name')
rep('app/src/main/AndroidManifest.xml', 'iCE Onhand 3.0.153', 'iCE Onhand 3.0.154', 'manifest version')
rep('app/src/main/java/com/iceinventory/onhand/MainActivity.java', 'Onhand Inventory 3.0.153', 'Onhand Inventory 3.0.154', 'visible version')

m = 'app/src/main/java/com/iceinventory/onhand/MonthlyInventoryActivity.java'
rep(m,
    'private static final int PICK_SOURCE=5101,SAVE_MASTER=5102,SAVE_ONHAND=5103,PICK_COUNTS=5104,SAVE_COMBINED=5105,SAVE_CLIENT=5106,SAVE_AUDIT=5107,SHARE_ONHAND=5108;',
    'private static final int PICK_SOURCE=5101,SAVE_MASTER=5102,SAVE_ONHAND=5103,PICK_COUNTS=5104,SAVE_COMBINED=5105,SAVE_CLIENT=5106,SAVE_AUDIT=5107,SHARE_ONHAND=5108,SAVE_CATEGORY=5109,SAVE_CIGARETTES=5110;',
    'report request codes')
rep(m,
    'private Button chooseSource,saveMaster,saveOnHand,loadDevice,shareOnHand,chooseCounts,saveCombined,saveClient,saveAudit,adjustCount,closeProject;',
    'private Button chooseSource,saveMaster,saveOnHand,loadDevice,shareOnHand,chooseCounts,saveCombined,saveClient,saveAudit,adjustCount,closeProject,saveCategory,saveCigarettes;',
    'report buttons')
rep(m,
    '''        saveClient=button("7. Export Petrosoft Client Excel");saveClient.setOnClickListener(v->create(SAVE_CLIENT,"application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",base()+" INVENTORY-"+day()+".xlsx"));root.addView(saveClient,params(58));
        saveAudit=button("Export Monthly Verification Report");''',
    '''        saveClient=button("7. CUSTOMER IMPORT REPORT");saveClient.setTypeface(android.graphics.Typeface.DEFAULT,android.graphics.Typeface.BOLD);saveClient.setTextColor(Color.BLACK);saveClient.setBackgroundTintList(android.content.res.ColorStateList.valueOf(Color.rgb(255,215,0)));saveClient.setOnClickListener(v->create(SAVE_CLIENT,"application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",base()+" CUSTOMER IMPORT REPORT-"+day()+".xlsx"));root.addView(saveClient,params(62));
        saveCategory=button("CATEGORY REPORT — Excel");saveCategory.setOnClickListener(v->create(SAVE_CATEGORY,"application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",base()+" CATEGORY REPORT-"+day()+".xlsx"));root.addView(saveCategory,params(54));
        saveCigarettes=button("CIGARETTES CATEGORY QTY REPORT — Excel");saveCigarettes.setOnClickListener(v->create(SAVE_CIGARETTES,"application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",base()+" CIGARETTES QTY-"+day()+".xlsx"));root.addView(saveCigarettes,params(54));
        saveAudit=button("Export Monthly Verification Report");''',
    'customer and category report buttons')
rep(m,
    '''        else if(request==SAVE_CLIENT){if(!validated)throw new Exception("Client export is blocked until validation passes");MonthlyClientXlsxWriter.writeClient(use,clientRows);clientExported=true;workflowPrefs().edit().putBoolean("client_exported",true).apply();}
        else if(request==SAVE_AUDIT){use.write(auditText().getBytes(StandardCharsets.UTF_8));auditExported=true;workflowPrefs().edit().putBoolean("audit_exported",true).apply();}''',
    '''        else if(request==SAVE_CLIENT){if(!validated)throw new Exception("Customer import report is blocked until validation passes");MonthlyClientXlsxWriter.writeClient(use,clientRows);clientExported=true;workflowPrefs().edit().putBoolean("client_exported",true).apply();}
        else if(request==SAVE_CATEGORY){if(!validated)throw new Exception("Category report is blocked until validation passes");MonthlyCategoryXlsxWriter.writeCategorySummary(use,clientRows);}
        else if(request==SAVE_CIGARETTES){if(!validated)throw new Exception("Cigarettes report is blocked until validation passes");MonthlyCategoryXlsxWriter.writeCigarettes(use,clientRows);}
        else if(request==SAVE_AUDIT){use.write(auditText().getBytes(StandardCharsets.UTF_8));auditExported=true;workflowPrefs().edit().putBoolean("audit_exported",true).apply();}''',
    'report writers')
rep(m,
    'saveClient.setEnabled(countsReady&&validated);saveAudit.setEnabled(countsReady);if(adjustCount!=null)adjustCount.setEnabled(deviceSessionId>0);',
    'saveClient.setEnabled(countsReady&&validated);saveCategory.setEnabled(countsReady&&validated);saveCigarettes.setEnabled(countsReady&&validated);saveAudit.setEnabled(countsReady);if(adjustCount!=null)adjustCount.setEnabled(deviceSessionId>0);',
    'report enabled state')

monthly = Path(m).read_text()
checks = {
    'customer report label': '7. CUSTOMER IMPORT REPORT',
    'yellow button': 'Color.rgb(255,215,0)',
    'category report': 'MonthlyCategoryXlsxWriter.writeCategorySummary',
    'cigarettes report': 'MonthlyCategoryXlsxWriter.writeCigarettes',
    'category source': 'CATEGORYNAME',
}
missing = [name for name, value in checks.items() if value not in monthly]
if missing:
    raise SystemExit('3.0.154 verification failed: ' + ', '.join(missing))

writer = Path('app/src/main/java/com/iceinventory/onhand/MonthlyCategoryXlsxWriter.java').read_text()
for required in ('CATEGORY NAME', 'TOTAL CIGARETTES QTY', 'GRAND TOTAL'):
    if required not in writer:
        raise SystemExit('3.0.154 category writer missing: ' + required)

print('Prepared iCE OnHand 3.0.154: Petrosoft category reports and yellow Customer Import Report')
