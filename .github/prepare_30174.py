from pathlib import Path

base = Path('.github/prepare_30173.py')
exec(compile(base.read_text(), str(base), 'exec'), {'__name__': '__main__', '__file__': str(base)})


def rep(path, old, new, label):
    p = Path(path); s = p.read_text()
    if s.count(old) != 1:
        raise SystemExit('3.0.174 target '+label+' count '+str(s.count(old)))
    p.write_text(s.replace(old, new, 1))


rep('app/build.gradle','versionCode 30173','versionCode 30174','code')
rep('app/build.gradle',"versionName '3.0.173'","versionName '3.0.174'",'name')
rep('app/src/main/AndroidManifest.xml','iCE Onhand 3.0.173','iCE Onhand 3.0.174','manifest')

main='app/src/main/java/com/iceinventory/onhand/MainActivity.java'
rep(main,'Onhand Inventory 3.0.173','Onhand Inventory 3.0.174','header')
rep(main,
'''            Button shareUsers=button("📤 Share",2);shareUsers.setTextSize(12);
            shareUsers.setSingleLine(true);shareUsers.setContentDescription("Share with Count Users");''',
'''            Button shareUsers=button("📤 SHARE WITH\\nCOUNTERS",2);shareUsers.setTextSize(10);
            shareUsers.setSingleLine(false);shareUsers.setMaxLines(2);shareUsers.setGravity(Gravity.CENTER);shareUsers.setContentDescription("Share app or current store with counters");''',
'top share label')
rep(main,
'''        String[] choices={"NEW PHONE + CURRENT STORE — app and count ZIP",
                "APP UPDATE ONLY — APK "+installedVersion(),
                "NEW STORE ONLY — current zero-quantity TXT",
                "HELP — what to send and how to receive"};''',
'''        String[] choices={"NEW COUNTER PHONE — Send App + Current Store",
                "UPDATE COUNTER APP — Send APK Only ("+installedVersion()+")",
                "EXISTING COUNTER PHONE — Send Current Store File Only",
                "HELP — What Should I Send?"};''',
'share menu descriptions')
rep(main,'.setTitle("Share with Count Users")','.setTitle("Share With Counters")','share title')

s=Path(main).read_text()
checks={
 'version':"versionName '3.0.174'" in Path('app/build.gradle').read_text(),
 'button':'SHARE WITH\\nCOUNTERS' in s,
 'new phone':'NEW COUNTER PHONE — Send App + Current Store' in s,
 'existing phone':'EXISTING COUNTER PHONE — Send Current Store File Only' in s,
 'app only':'UPDATE COUNTER APP — Send APK Only' in s,
}
bad=[k for k,v in checks.items() if not v]
if bad: raise SystemExit('3.0.174 checks failed: '+', '.join(bad))
print('Prepared iCE OnHand 3.0.174: explicit Share With Counters controls')
