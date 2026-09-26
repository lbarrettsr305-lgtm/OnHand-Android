from pathlib import Path

base = Path('.github/prepare_30171.py')
exec(compile(base.read_text(), str(base), 'exec'), {'__name__': '__main__', '__file__': str(base)})


def rep(path, old, new, label):
    p = Path(path); s = p.read_text()
    if s.count(old) != 1:
        raise SystemExit('3.0.172 target ' + label + ' count ' + str(s.count(old)))
    p.write_text(s.replace(old, new, 1))


rep('app/build.gradle', 'versionCode 30171', 'versionCode 30172', 'code')
rep('app/build.gradle', "versionName '3.0.171'", "versionName '3.0.172'", 'name')
rep('app/src/main/AndroidManifest.xml', 'iCE Onhand 3.0.171', 'iCE Onhand 3.0.172', 'manifest')
rep('app/src/main/java/com/iceinventory/onhand/MainActivity.java',
    'Onhand Inventory 3.0.171', 'Onhand Inventory 3.0.172', 'header')

main='app/src/main/java/com/iceinventory/onhand/MainActivity.java'
rep(main,
'''            Button clearAll=button("MASTER: CLEAR ALL INVENTORIES",2);
            clearAll.setTypeface(Typeface.DEFAULT,Typeface.BOLD);
            clearAll.setTextSize(15);
            clearAll.setOnClickListener(v->confirmClearAllInventories());
            LinearLayout.LayoutParams clearLp=new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT,dp(58));
''',
'''            Button clearAll=button("CLEAR ALL INVENTORY FILES",2);
            clearAll.setTypeface(Typeface.DEFAULT,Typeface.BOLD);
            clearAll.setTextSize(14);
            clearAll.setSingleLine(false);
            clearAll.setGravity(Gravity.CENTER);
            clearAll.setPadding(dp(8),dp(4),dp(8),dp(4));
            clearAll.setOnClickListener(v->confirmClearAllInventories());
            LinearLayout.LayoutParams clearLp=new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT,dp(72));
''', 'readable clear button')

s=Path(main).read_text()
checks={
    'version': "versionName '3.0.172'" in Path('app/build.gradle').read_text(),
    'short label': 'CLEAR ALL INVENTORY FILES' in s,
    'multiline': 'clearAll.setSingleLine(false)' in s,
    'height': 'MATCH_PARENT,dp(72)' in s,
}
bad=[k for k,v in checks.items() if not v]
if bad: raise SystemExit('3.0.172 checks failed: '+', '.join(bad))
print('Prepared iCE OnHand 3.0.172: readable clear inventory files control')
