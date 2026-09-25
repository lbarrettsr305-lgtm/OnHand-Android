from pathlib import Path

base=Path('.github/prepare_30144.py')
exec(compile(base.read_text(),str(base),'exec'),{'__name__':'__main__','__file__':str(base)})

def rep(path,old,new):
    p=Path(path);s=p.read_text()
    if s.count(old)!=1:raise SystemExit('3.0.145 expected one target: '+old[:80])
    p.write_text(s.replace(old,new,1))

rep('app/build.gradle','versionCode 30144','versionCode 30145')
rep('app/build.gradle',"versionName '3.0.144'","versionName '3.0.145'")
rep('app/src/main/AndroidManifest.xml','iCE Onhand 3.0.144','iCE Onhand 3.0.145')
m='app/src/main/java/com/iceinventory/onhand/MainActivity.java'
rep(m,'Onhand Inventory 3.0.144','Onhand Inventory 3.0.145')
rep(m,
'''        Button help=button("❓ Help / Instructions",0);''',
'''        Button shareApk=button("📤 Share This Installed APK ("+installedVersion()+")",0);
        shareApk.setOnClickListener(v->shareInstalledApk());
        box.addView(shareApk,new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT,dp(52)));
        Button help=button("❓ Help / Instructions",0);''')
rep(m,
'''    private void showImportMenu() {''',
'''    private String installedVersion() {
        try{return getPackageManager().getPackageInfo(getPackageName(),0).versionName;}
        catch(Exception e){return "unknown";}
    }

    private void shareInstalledApk() {
        try {
            android.content.pm.ApplicationInfo info=getApplicationInfo();
            if(info.splitSourceDirs!=null && info.splitSourceDirs.length>0)
                throw new java.io.IOException("This installation uses split APKs and cannot be shared as one APK.");
            java.io.File source=new java.io.File(info.sourceDir);
            if(!source.isFile())throw new java.io.IOException("Installed APK could not be found.");
            java.io.File dir=new java.io.File(getCacheDir(),"shared");
            if(!dir.isDirectory()&&!dir.mkdirs())throw new java.io.IOException("Could not prepare the sharing folder.");
            String version=installedVersion().replaceAll("[^0-9A-Za-z._-]","_");
            java.io.File apk=new java.io.File(dir,"iCE-Onhand-Inventory-"+version+".apk");
            try(java.io.InputStream input=new java.io.FileInputStream(source);
                java.io.OutputStream output=new java.io.FileOutputStream(apk)) {
                byte[] buffer=new byte[8192];int count;
                while((count=input.read(buffer))!=-1)output.write(buffer,0,count);
            }
            Uri uri=Uri.parse("content://"+getPackageName()+".fileprovider/onhand/"+Uri.encode(apk.getName()));
            Intent intent=new Intent(Intent.ACTION_SEND);
            intent.setType("application/vnd.android.package-archive");
            intent.putExtra(Intent.EXTRA_STREAM,uri);
            intent.setClipData(android.content.ClipData.newRawUri(apk.getName(),uri));
            intent.addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION);
            startActivity(Intent.createChooser(intent,"Share installed OnHand "+version));
        } catch(Exception e){showError("Could not share installed APK",e);}
    }

    private void showImportMenu() {''')
p='app/src/main/java/com/iceinventory/onhand/ShareFileProvider.java'
rep(p,'@Override public String getType(Uri uri){return "text/plain";}',
      '@Override public String getType(Uri uri){return uri!=null&&uri.getLastPathSegment()!=null&&uri.getLastPathSegment().toLowerCase(java.util.Locale.US).endsWith(".apk")?"application/vnd.android.package-archive":"text/plain";}')
assert 'Share This Installed APK' in Path(m).read_text()
print('Prepared iCE OnHand 3.0.145: share the installed single APK with a temporary read grant')
