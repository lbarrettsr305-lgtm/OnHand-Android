from pathlib import Path

base = Path('.github/prepare_30177.py')
exec(compile(base.read_text(), str(base), 'exec'), {'__name__': '__main__', '__file__': str(base)})


def rep(path, old, new, label):
    p = Path(path); s = p.read_text()
    if s.count(old) != 1:
        raise SystemExit('3.0.178 target '+label+' count '+str(s.count(old)))
    p.write_text(s.replace(old, new, 1))


rep('app/build.gradle','versionCode 30177','versionCode 30178','code')
rep('app/build.gradle',"versionName '3.0.177'","versionName '3.0.178'",'name')
rep('app/src/main/AndroidManifest.xml','iCE Onhand 3.0.177','iCE Onhand 3.0.178','manifest')

main='app/src/main/java/com/iceinventory/onhand/MainActivity.java'
rep(main,'Onhand Inventory 3.0.177','Onhand Inventory 3.0.178','header')
rep(main,
'''        final String[] counters={"Chief","RobertFad","JoseFad","Lbsr","Lbjr","QuselahJ","MataiJ","DelilahW","AdrianB","HailahJ"};
        new AlertDialog.Builder(this)
                .setTitle("SELECT COUNTER NAME")
                .setMessage("Choose the person using this phone. The selected name is remembered and added to completed-count filenames.")''',
'''        final boolean master=isMasterDevice();
        final String[] counters=master?new String[]{"Chief","Lbsr","Lbjr"}:new String[]{"RobertFad","JoseFad","QuselahJ","MataiJ","DelilahW","AdrianB","HailahJ"};
        new AlertDialog.Builder(this)
                .setTitle(master?"SELECT MASTER NAME":"SELECT COUNTER NAME")
                .setMessage(master?"Choose the authorized Master using this phone. The selected name is remembered and added to reports.":"Choose the counter using this phone. The selected name is remembered and added to completed-count filenames.")''',
'role-specific lookup')

s=Path(main).read_text()
checks={
 'version':"versionName '3.0.178'" in Path('app/build.gradle').read_text(),
 'masters':'new String[]{"Chief","Lbsr","Lbjr"}' in s,
 'counters':'new String[]{"RobertFad","JoseFad","QuselahJ","MataiJ","DelilahW","AdrianB","HailahJ"}' in s,
 'role title':'master?"SELECT MASTER NAME":"SELECT COUNTER NAME"' in s,
 'protected add':'verifyMasterPinForNewCounter' in s,
}
bad=[k for k,v in checks.items() if not v]
if bad: raise SystemExit('3.0.178 checks failed: '+', '.join(bad))
print('Prepared iCE OnHand 3.0.178: separate Master and Counter name lookups')
