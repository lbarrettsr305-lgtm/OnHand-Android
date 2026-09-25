from pathlib import Path

base = Path('.github/prepare_30157.py')
exec(compile(base.read_text(), str(base), 'exec'), {'__name__': '__main__', '__file__': str(base)})


def rep(path, old, new, label):
    target = Path(path)
    source = target.read_text()
    if source.count(old) != 1:
        raise SystemExit('3.0.158 expected one target for ' + label)
    target.write_text(source.replace(old, new, 1))


rep('app/build.gradle', 'versionCode 30157', 'versionCode 30158', 'Gradle code')
rep('app/build.gradle', "versionName '3.0.157'", "versionName '3.0.158'", 'Gradle name')
rep('app/src/main/AndroidManifest.xml', 'iCE Onhand 3.0.157', 'iCE Onhand 3.0.158', 'manifest version')
rep('app/src/main/java/com/iceinventory/onhand/MainActivity.java',
    'Onhand Inventory 3.0.157', 'Onhand Inventory 3.0.158', 'visible version')

monthly = 'app/src/main/java/com/iceinventory/onhand/MonthlyInventoryActivity.java'
rep(monthly,
    '''        ScrollView scroll=new ScrollView(this);LinearLayout root=new LinearLayout(this);root.setOrientation(LinearLayout.VERTICAL);root.setPadding(dp(16),dp(16),dp(16),dp(24));root.setBackgroundColor(Color.rgb(8,24,27));scroll.addView(root);''',
    '''        ScrollView scroll=new ScrollView(this);LinearLayout root=new LinearLayout(this);root.setOrientation(LinearLayout.VERTICAL);root.setPadding(dp(16),dp(16),dp(16),dp(24));root.setBackgroundColor(Color.rgb(8,24,27));scroll.addView(root);
        scroll.setClipToPadding(false);
        scroll.setOnApplyWindowInsetsListener((v,insets)->{
            int bottom=android.os.Build.VERSION.SDK_INT>=20?insets.getSystemWindowInsetBottom():0;
            root.setPadding(dp(16),dp(16),dp(16),Math.max(dp(24),bottom+dp(16)));
            return insets;
        });''',
    'Samsung navigation clearance')
rep(monthly,
    '''        saveCigarettes=button("CIGARETTES CATEGORY QTY REPORT — Excel");saveCigarettes.setOnClickListener(v->create(SAVE_CIGARETTES,"application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",base()+" CIGARETTES QTY-"+day()+".xlsx"));root.addView(saveCigarettes,params(54));''',
    '''        saveCigarettes=button("CIGARETTES CATEGORY QTY REPORT — Excel");saveCigarettes.setTextSize(14);saveCigarettes.setSingleLine(false);saveCigarettes.setMaxLines(2);saveCigarettes.setGravity(Gravity.CENTER);saveCigarettes.setOnClickListener(v->create(SAVE_CIGARETTES,"application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",base()+" CIGARETTES QTY-"+day()+".xlsx"));root.addView(saveCigarettes,params(68));''',
    'full cigarettes report label')
rep(monthly,
    '''        setContentView(scroll);pendingSourceUri=incomingSource(getIntent());''',
    '''        setContentView(scroll);scroll.requestApplyInsets();pendingSourceUri=incomingSource(getIntent());''',
    'apply navigation insets')

source = Path(monthly).read_text()
required = {
    'full report label': 'saveCigarettes.setSingleLine(false)',
    'two-line report label': 'saveCigarettes.setMaxLines(2)',
    'taller report button': 'root.addView(saveCigarettes,params(68))',
    'navigation inset listener': 'scroll.setOnApplyWindowInsetsListener',
    'navigation bottom clearance': 'bottom+dp(16)',
    'corrections section preserved': 'CORRECTIONS / PROJECT CONTROL',
}
missing = [label for label, needle in required.items() if needle not in source]
if missing:
    raise SystemExit('3.0.158 verification missing: ' + ', '.join(missing))

print('Prepared iCE OnHand 3.0.158: full cigarettes report label and Samsung navigation clearance')
