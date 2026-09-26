from pathlib import Path

base = Path('.github/prepare_30165.py')
exec(compile(base.read_text(), str(base), 'exec'), {'__name__': '__main__', '__file__': str(base)})


def rep(path, old, new, label):
    p = Path(path)
    s = p.read_text()
    if s.count(old) != 1:
        raise SystemExit('3.0.166 target ' + label + ' count ' + str(s.count(old)))
    p.write_text(s.replace(old, new, 1))


rep('app/build.gradle', 'versionCode 30165', 'versionCode 30166', 'code')
rep('app/build.gradle', "versionName '3.0.165'", "versionName '3.0.166'", 'name')
rep('app/src/main/AndroidManifest.xml', 'iCE Onhand 3.0.165', 'iCE Onhand 3.0.166', 'manifest')
rep('app/src/main/java/com/iceinventory/onhand/MainActivity.java',
    'Onhand Inventory 3.0.165', 'Onhand Inventory 3.0.166', 'header')

monthly = 'app/src/main/java/com/iceinventory/onhand/MonthlyInventoryActivity.java'
old = '''try(BufferedReader br=new BufferedReader(new InputStreamReader(in,StandardCharsets.UTF_8))){String line;boolean first=true;int qi=0,bi=1,di=2,li=-1;while((line=br.readLine())!=null){if(line.trim().isEmpty()||line.startsWith("#ICE_ONHAND_PROJECT\\t"))continue;String[] v=line.split("\\t",-1);if(first){first=false;int hq=find(v,"quantity","qty","count","on hand","onhand"),hb=find(v,"barcode","upc","gtin"),hd=find(v,"description","item description","name"),hl=find(v,"location","loc","area");if(hq>=0&&hb>=0){qi=hq;bi=hb;if(hd>=0)di=hd;li=hl;continue;}}'''
new = '''try(BufferedReader br=new BufferedReader(new InputStreamReader(in,StandardCharsets.UTF_8))){String line;boolean first=true;int qi=0,bi=1,di=2,li=4;while((line=br.readLine())!=null){if(line.trim().isEmpty()||line.startsWith("#ICE_ONHAND_PROJECT\\t"))continue;String[] v=line.split("\\t",-1);if(first){first=false;int hq=find(v,"quantity","qty","count","on hand","onhand"),hb=find(v,"barcode","upc","gtin"),hd=find(v,"description","item description","name"),hl=find(v,"location","loc","area","section","counting location","exact location","location side","location sides","section side","section sides");if(hq>=0&&hb>=0){qi=hq;bi=hb;if(hd>=0)di=hd;li=hl;continue;}}'''
rep(monthly, old, new, 'current and legacy count locations')

s = Path(monthly).read_text()
checks = {
    'version': "versionName '3.0.166'" in Path('app/build.gradle').read_text(),
    'headerless location': 'int qi=0,bi=1,di=2,li=4' in s,
    'section alias': '"section","counting location","exact location"' in s,
    'missing workbook location': 'r.locations=d==null?"":android.text.TextUtils.join(", ",d.locations)' in s,
    'priority cigarettes retained': 'CIGARETTES QUANTITY REPORT — EXCEL' in s
}
bad = [k for k, v in checks.items() if not v]
if bad:
    raise SystemExit('3.0.166 checks failed: ' + ', '.join(bad))
print('Prepared iCE OnHand 3.0.166: preserve locations in missing/new items Excel from current and legacy counter files')
