from pathlib import Path

base = Path('.github/prepare_30164.py')
exec(compile(base.read_text(), str(base), 'exec'), {'__name__': '__main__', '__file__': str(base)})


def rep(path, old, new, label):
    p = Path(path)
    s = p.read_text()
    if s.count(old) != 1:
        raise SystemExit('3.0.165 target ' + label + ' count ' + str(s.count(old)))
    p.write_text(s.replace(old, new, 1))


rep('app/build.gradle', 'versionCode 30164', 'versionCode 30165', 'code')
rep('app/build.gradle', "versionName '3.0.164'", "versionName '3.0.165'", 'name')
rep('app/src/main/AndroidManifest.xml', 'iCE Onhand 3.0.164', 'iCE Onhand 3.0.165', 'manifest')
rep('app/src/main/java/com/iceinventory/onhand/MainActivity.java',
    'Onhand Inventory 3.0.164', 'Onhand Inventory 3.0.165', 'header')

old = '''        action.setGravity(Gravity.LEFT|Gravity.CENTER_VERTICAL);
        action.setOnClickListener(v->{if(dialog[0]!=null)dialog[0].dismiss();handleExportChoice(which);});
        LinearLayout.LayoutParams lp=new LinearLayout.LayoutParams(LinearLayout.LayoutParams.MATCH_PARENT,dp(54));
        lp.setMargins(0,0,0,dp(6));
        panel.addView(action,lp);'''
new = '''        action.setGravity(Gravity.LEFT|Gravity.CENTER_VERTICAL);
        action.setSingleLine(false);
        action.setMaxLines(3);
        action.setHorizontallyScrolling(false);
        action.setPadding(dp(16),dp(10),dp(12),dp(10));
        action.setMinHeight(dp(58));
        action.setOnClickListener(v->{if(dialog[0]!=null)dialog[0].dismiss();handleExportChoice(which);});
        LinearLayout.LayoutParams lp=new LinearLayout.LayoutParams(LinearLayout.LayoutParams.MATCH_PARENT,LinearLayout.LayoutParams.WRAP_CONTENT);
        lp.setMargins(0,0,0,dp(7));
        panel.addView(action,lp);'''
rep('app/src/main/java/com/iceinventory/onhand/MainActivity.java', old, new, 'auto-height export buttons')

old_reports = '''        saveCategory=button("CATEGORY REPORT — Excel");saveCategory.setOnClickListener(v->create(SAVE_CATEGORY,"application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",base()+" CATEGORY REPORT-"+day()+".xlsx"));root.addView(saveCategory,params(54));
        saveCigarettes=button("CIGARETTES CATEGORY QTY REPORT — Excel");saveCigarettes.setTextSize(14);saveCigarettes.setSingleLine(false);saveCigarettes.setMaxLines(2);saveCigarettes.setGravity(Gravity.CENTER);saveCigarettes.setOnClickListener(v->create(SAVE_CIGARETTES,"application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",base()+" CIGARETTES QTY-"+day()+".xlsx"));root.addView(saveCigarettes,params(68));'''
new_reports = '''        root.addView(section("PRIORITY CLIENT REPORTS"));
        saveCigarettes=button("🚬 CIGARETTES QUANTITY REPORT — EXCEL");saveCigarettes.setTextSize(16);saveCigarettes.setTypeface(android.graphics.Typeface.DEFAULT,android.graphics.Typeface.BOLD);saveCigarettes.setTextColor(Color.BLACK);saveCigarettes.setBackgroundTintList(android.content.res.ColorStateList.valueOf(Color.rgb(255,215,0)));saveCigarettes.setSingleLine(false);saveCigarettes.setMaxLines(2);saveCigarettes.setGravity(Gravity.CENTER);saveCigarettes.setOnClickListener(v->create(SAVE_CIGARETTES,"application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",base()+" CIGARETTES QTY-"+day()+".xlsx"));root.addView(saveCigarettes,params(76));
        saveCategory=button("CATEGORY DESCRIPTION & QUANTITY — EXCEL");saveCategory.setSingleLine(false);saveCategory.setMaxLines(2);saveCategory.setGravity(Gravity.CENTER);saveCategory.setOnClickListener(v->create(SAVE_CATEGORY,"application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",base()+" CATEGORY REPORT-"+day()+".xlsx"));root.addView(saveCategory,params(64));'''
rep('app/src/main/java/com/iceinventory/onhand/MonthlyInventoryActivity.java', old_reports, new_reports, 'priority monthly reports')

main = Path('app/src/main/java/com/iceinventory/onhand/MainActivity.java').read_text()
checks = {
    'version': "versionName '3.0.165'" in Path('app/build.gradle').read_text(),
    'wrap content': 'LinearLayout.LayoutParams.WRAP_CONTENT' in main,
    'multiple lines': 'action.setMaxLines(3)' in main,
    'no fixed export height': 'MATCH_PARENT,dp(54)' not in main[main.find('private void addExportButton'):main.find('private void handleExportChoice')],
    'reports retained': all(x in main for x in [
        'Location Detail — TXT (Scan Order)',
        'Category Description & Quantity — Excel',
        'Cigarettes Quantity — Excel']),
    'priority cigarettes': '🚬 CIGARETTES QUANTITY REPORT — EXCEL' in Path('app/src/main/java/com/iceinventory/onhand/MonthlyInventoryActivity.java').read_text(),
    'priority section': 'PRIORITY CLIENT REPORTS' in Path('app/src/main/java/com/iceinventory/onhand/MonthlyInventoryActivity.java').read_text()
}
bad = [k for k, v in checks.items() if not v]
if bad:
    raise SystemExit('3.0.165 checks failed: ' + ', '.join(bad))
print('Prepared iCE OnHand 3.0.165: readable auto-height multiline Export Reports buttons')
