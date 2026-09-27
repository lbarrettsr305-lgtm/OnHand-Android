from pathlib import Path

base = Path('.github/prepare_30174.py')
exec(compile(base.read_text(), str(base), 'exec'), {'__name__': '__main__', '__file__': str(base)})


def rep(path, old, new, label):
    p = Path(path); s = p.read_text()
    if s.count(old) != 1:
        raise SystemExit('3.0.175 target '+label+' count '+str(s.count(old)))
    p.write_text(s.replace(old, new, 1))


rep('app/build.gradle','versionCode 30174','versionCode 30175','code')
rep('app/build.gradle',"versionName '3.0.174'","versionName '3.0.175'",'name')
rep('app/src/main/AndroidManifest.xml','iCE Onhand 3.0.174','iCE Onhand 3.0.175','manifest')

main='app/src/main/java/com/iceinventory/onhand/MainActivity.java'
rep(main,'Onhand Inventory 3.0.174','Onhand Inventory 3.0.175','header')
rep(main,
'''            Button shareUsers=button("📤 SHARE WITH\\nCOUNTERS",2);shareUsers.setTextSize(10);
            shareUsers.setSingleLine(false);shareUsers.setMaxLines(2);shareUsers.setGravity(Gravity.CENTER);shareUsers.setContentDescription("Share app or current store with counters");''',
'''            Button shareUsers=button("SHARE WITH\\nCOUNTERS",2);shareUsers.setTextSize(9);
            shareUsers.setSingleLine(false);shareUsers.setMaxLines(2);shareUsers.setGravity(Gravity.CENTER);shareUsers.setPadding(2,0,2,0);shareUsers.setContentDescription("Share app or current store with counters");''',
'fully visible share label')

s=Path(main).read_text()
checks={
 'version':"versionName '3.0.175'" in Path('app/build.gradle').read_text(),
 'button':'SHARE WITH\\nCOUNTERS' in s,
 'button size':'shareUsers.setTextSize(9)' in s,
 'menu':'NEW COUNTER PHONE — Send App + Current Store' in s,
}
bad=[k for k,v in checks.items() if not v]
if bad: raise SystemExit('3.0.175 checks failed: '+', '.join(bad))
print('Prepared iCE OnHand 3.0.175: full Share With Counters button label')
