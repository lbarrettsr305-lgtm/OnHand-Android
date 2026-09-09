from pathlib import Path
import re

# Preserve the validated 3.0.104 build first.
base=Path('.github/prepare_30104.py')
exec(compile(base.read_text(),str(base),'exec'),{'__name__':'__main__','__file__':str(base)})

p=Path('app/src/main/java/com/iceinventory/onhand/MainActivity.java')
s=p.read_text()

# Accept a scanner's partial barcode when it is contained in a longer
# imported barcode. The existing caller already handles safety: one match is
# selected automatically and multiple matches require the user to choose.
old='''    private boolean barcodesFlexibleMatch(String a,String b) {
        if(a==null||b==null)return false;
        String x=a.trim(),y=b.trim();
        if(x.equals(y))return true;
        if(!x.matches("\\\\d+")||!y.matches("\\\\d+"))return false;
        if(x.length()<8||y.length()<8)return false;
        List<String> xv=barcodeVariants(x),yv=barcodeVariants(y);
        for(String p:xv)for(String q:yv)if(p.length()>=8&&p.equals(q))return true;
        return false;
    }
'''
new='''    private boolean barcodesFlexibleMatch(String a,String b) {
        if(a==null||b==null)return false;
        String x=a.trim(),y=b.trim();
        if(x.equalsIgnoreCase(y))return true;
        String nx=x.replaceAll("\\\\s+","").toUpperCase(Locale.US);
        String ny=y.replaceAll("\\\\s+","").toUpperCase(Locale.US);
        if(nx.equals(ny))return true;
        if(nx.length()<4||ny.length()<4)return false;
        boolean numeric=nx.matches("\\\\d+")&&ny.matches("\\\\d+");
        List<String> xv=numeric?barcodeVariants(nx):java.util.Collections.singletonList(nx);
        List<String> yv=numeric?barcodeVariants(ny):java.util.Collections.singletonList(ny);
        for(String p:xv)for(String q:yv) {
            if(p.length()<4||q.length()<4)continue;
            if(p.equals(q))return true;
            String shorter=p.length()<=q.length()?p:q;
            String longer=p.length()>q.length()?p:q;
            if(shorter.length()<longer.length()&&longer.contains(shorter))return true;
        }
        return false;
    }
'''
if old not in s: raise SystemExit('3.0.105 target missing: flexible barcode matcher')
s=s.replace(old,new,1)
s=s.replace('Onhand Inventory 3.0.104','Onhand Inventory 3.0.105',1)
if 'Onhand Inventory 3.0.105' not in s: raise SystemExit('3.0.105 visible version target missing')
p.write_text(s)

p=Path('app/build.gradle')
g=p.read_text().replace('versionCode 30104','versionCode 30105',1).replace("versionName '3.0.104'","versionName '3.0.105'",1)
if 'versionCode 30105' not in g or "versionName '3.0.105'" not in g: raise SystemExit('3.0.105 Gradle version target missing')
p.write_text(g)

p=Path('app/src/main/AndroidManifest.xml')
m=p.read_text().replace('iCE Onhand 3.0.104','iCE Onhand 3.0.105',1)
if 'iCE Onhand 3.0.105' not in m: raise SystemExit('3.0.105 manifest version target missing')
p.write_text(m)

main=Path('app/src/main/java/com/iceinventory/onhand/MainActivity.java').read_text()
checks={
    'four-character floor':'if(nx.length()<4||ny.length()<4)return false;' in main,
    'embedded spaces ignored':'replaceAll("\\\\s+","")' in main,
    'alphanumeric matching':'Collections.singletonList(nx)' in main,
    'contained partial match':'longer.contains(shorter)' in main,
    'unique automatic match':'if(flexible.size()==1)' in main,
    'ambiguous choice':'if(flexible.size()>1)' in main and 'showFlexibleBarcodeChoices(flexible)' in main,
    'scanner lookup path':'handleScannedBarcode(scanned)' in main,
}
missing=[k for k,v in checks.items() if not v]
if missing: raise SystemExit('3.0.105 verification failed: '+', '.join(missing))
print('Prepared iCE Onhand 3.0.105: partial scanner barcode matching')
