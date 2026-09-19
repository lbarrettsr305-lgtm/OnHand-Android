from pathlib import Path

# Preserve 3.0.119, then create the OnHand sharing file internally without Android's Save dialog.
base=Path('.github/prepare_30119.py')
exec(compile(base.read_text(),str(base),'exec'),{'__name__':'__main__','__file__':str(base)})

p=Path('app/build.gradle')
g=p.read_text().replace('versionCode 30119','versionCode 30120',1).replace("versionName '3.0.119'","versionName '3.0.120'",1)
dependency="    implementation 'androidx.core:core:1.15.0'\n"
if dependency not in g:
    marker="dependencies {\n"
    if marker not in g: raise SystemExit('3.0.120 target missing: dependencies')
    g=g.replace(marker,marker+dependency,1)
if 'versionCode 30120' not in g or "versionName '3.0.120'" not in g: raise SystemExit('3.0.120 Gradle target missing')
p.write_text(g)

p=Path('app/src/main/java/com/iceinventory/onhand/MainActivity.java')
s=p.read_text().replace('Onhand Inventory 3.0.119','Onhand Inventory 3.0.120',1)
if 'Onhand Inventory 3.0.120' not in s: raise SystemExit('3.0.120 visible version target missing')
p.write_text(s)

p=Path('app/src/main/AndroidManifest.xml')
m=p.read_text().replace('iCE Onhand 3.0.119','iCE Onhand 3.0.120',1)
provider='''        <provider
            android:name="androidx.core.content.FileProvider"
            android:authorities="${applicationId}.fileprovider"
            android:exported="false"
            android:grantUriPermissions="true">
            <meta-data
                android:name="android.support.FILE_PROVIDER_PATHS"
                android:resource="@xml/file_paths" />
        </provider>
'''
anchor='''    </application>'''
if 'androidx.core.content.FileProvider' not in m:
    if anchor not in m: raise SystemExit('3.0.120 target missing: application')
    m=m.replace(anchor,provider+anchor,1)
if 'iCE Onhand 3.0.120' not in m: raise SystemExit('3.0.120 manifest version target missing')
p.write_text(m)

xml=Path('app/src/main/res/xml')
xml.mkdir(parents=True,exist_ok=True)
(xml/'file_paths.xml').write_text('''<?xml version="1.0" encoding="utf-8"?>
<paths xmlns:android="http://schemas.android.com/apk/res/android">
    <cache-path name="shared_onhand" path="shared/" />
</paths>
''')

p=Path('app/src/main/java/com/iceinventory/onhand/MonthlyInventoryActivity.java')
s=p.read_text()
if 'import androidx.core.content.FileProvider;' not in s:
    s=s.replace('import android.widget.Toast;\n','import android.widget.Toast;\n\nimport androidx.core.content.FileProvider;\n',1)
if 'import java.io.File;' not in s:
    s=s.replace('import java.io.BufferedReader;\n','import java.io.BufferedReader;\nimport java.io.File;\nimport java.io.FileOutputStream;\n',1)

old='saveOnHand=button("2. Create OnHand Count File — Tab Delimited");saveOnHand.setOnClickListener(v->create(SAVE_ONHAND,"text/plain",base()+" ONHAND COUNT-"+day()+".txt"));'
new='saveOnHand=button("2. Prepare OnHand File for Sharing");saveOnHand.setOnClickListener(v->createOnHandInternally());'
if old not in s: raise SystemExit('3.0.120 target missing: OnHand save button')
s=s.replace(old,new,1)

anchor='''    private String onHandText(){'''
method='''    private void createOnHandInternally(){try{
        File dir=new File(getCacheDir(),"shared");if(!dir.exists()&&!dir.mkdirs())throw new Exception("Could not prepare the sharing folder");
        File file=new File(dir,base()+" ONHAND COUNT-"+day()+".txt");
        try(FileOutputStream out=new FileOutputStream(file)){out.write(onHandText().getBytes(StandardCharsets.UTF_8));}
        onHandUri=FileProvider.getUriForFile(this,getPackageName()+".fileprovider",file);
        onHandCreated=true;showImportSummary();showProgress();setEnabledState();
        Toast.makeText(this,"OnHand file prepared. Test Scan or Share with users.",Toast.LENGTH_LONG).show();
    }catch(Exception e){fail("Could not prepare OnHand file: "+e.getMessage());}}

'''+anchor
if anchor not in s: raise SystemExit('3.0.120 target missing: onHandText')
s=s.replace(anchor,method,1)

old='i.putExtra(Intent.EXTRA_STREAM,onHandUri);i.putExtra(Intent.EXTRA_SUBJECT'
new='i.putExtra(Intent.EXTRA_STREAM,onHandUri);i.setClipData(android.content.ClipData.newRawUri("OnHand count file",onHandUri));i.putExtra(Intent.EXTRA_SUBJECT'
if old not in s: raise SystemExit('3.0.120 target missing: share stream')
s=s.replace(old,new,1)

checks={
    'internal preparation button':'2. Prepare OnHand File for Sharing' in s,
    'no save document for OnHand':'v->create(SAVE_ONHAND' not in s,
    'cache file creation':'new File(getCacheDir(),"shared")' in s,
    'FileProvider URI':'FileProvider.getUriForFile' in s,
    'optional test scan':'3. Test Scan on This Device' in s,
    'direct sharing':'shareOnHand.setEnabled(onHandCreated&&onHandUri!=null)' in s,
    'provider manifest':'androidx.core.content.FileProvider' in m,
}
missing=[k for k,v in checks.items() if not v]
if missing: raise SystemExit('3.0.120 verification failed: '+', '.join(missing))
p.write_text(s)
print('Prepared iCE Onhand 3.0.120: internal OnHand file, no Downloads/Save prompt, optional test scan, direct sharing')
