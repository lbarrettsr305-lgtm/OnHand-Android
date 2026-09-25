from pathlib import Path

base=Path('.github/prepare_30145.py')
exec(compile(base.read_text(),str(base),'exec'),{'__name__':'__main__','__file__':str(base)})

def rep(path,old,new):
    p=Path(path);s=p.read_text()
    if s.count(old)!=1:raise SystemExit('3.0.146 expected one target: '+old[:80])
    p.write_text(s.replace(old,new,1))

rep('app/build.gradle','versionCode 30145','versionCode 30146')
rep('app/build.gradle',"versionName '3.0.145'","versionName '3.0.146'")
rep('app/src/main/AndroidManifest.xml','iCE Onhand 3.0.145','iCE Onhand 3.0.146')
m='app/src/main/java/com/iceinventory/onhand/MainActivity.java'
rep(m,'Onhand Inventory 3.0.145','Onhand Inventory 3.0.146')
rep(m,
'''        Button shareApk=button("📤 Share This Installed APK ("+installedVersion()+")",0);
        shareApk.setOnClickListener(v->shareInstalledApk());
        box.addView(shareApk,new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT,dp(52)));''',
'''        if(masterDevice){
            TextView sharing=text("Share with Count Users",16,gold(),true);
            sharing.setPadding(dp(6),dp(10),0,dp(2));box.addView(sharing);
            Button packageButton=button("📤 New phone / update: APK + current store",0);
            packageButton.setOnClickListener(v->shareCountPackage());
            box.addView(packageButton,new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT,dp(58)));
            Button storeButton=button("📤 New store only: current count file",0);
            storeButton.setOnClickListener(v->shareCurrentCountFile());
            box.addView(storeButton,new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT,dp(58)));
            Button shareApk=button("📤 APK only ("+installedVersion()+")",0);
            shareApk.setOnClickListener(v->shareInstalledApk());
            box.addView(shareApk,new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT,dp(52)));
            Button shareHelp=button("❓ Help: sharing and receiving steps",0);
            shareHelp.setOnClickListener(v->showShareHelp());
            box.addView(shareHelp,new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT,dp(52)));
        }''')
source=Path(m).read_text()
opening=source.index('    private void shareInstalledApk() {')
closing=source.index('    private void showImportMenu() {',opening)
source=source[:opening]+'''    private java.io.File sharedDirectory() throws java.io.IOException {
        java.io.File dir=new java.io.File(getCacheDir(),"shared");
        if(!dir.isDirectory()&&!dir.mkdirs())throw new java.io.IOException("Could not prepare the sharing folder.");
        return dir;
    }

    private java.io.File installedApkFile() throws java.io.IOException {
        android.content.pm.ApplicationInfo info=getApplicationInfo();
        if(info.splitSourceDirs!=null&&info.splitSourceDirs.length>0)
            throw new java.io.IOException("This installation uses split APKs and cannot be shared as one APK.");
        java.io.File source=new java.io.File(info.sourceDir);
        if(!source.isFile())throw new java.io.IOException("Installed APK could not be found.");
        String version=installedVersion().replaceAll("[^0-9A-Za-z._-]","_");
        java.io.File apk=new java.io.File(sharedDirectory(),"iCE-Onhand-Inventory-"+version+".apk");
        try(java.io.InputStream input=new java.io.FileInputStream(source);
            java.io.OutputStream output=new java.io.FileOutputStream(apk)){
            byte[] buffer=new byte[8192];int count;
            while((count=input.read(buffer))!=-1)output.write(buffer,0,count);
        }
        return apk;
    }

    private java.io.File currentCountFile() throws java.io.IOException {
        if(!isMasterDevice())throw new java.io.IOException("Only the Master phone can share the current store.");
        if(activeSessionId<=0||sessionId!=activeSessionId||"NO ACTIVE INVENTORY".equalsIgnoreCase(sessionName))
            throw new java.io.IOException("Select the current inventory before sharing a store.");
        List<InventoryDb.Row> rows=db.items(activeSessionId);
        if(rows.isEmpty())throw new java.io.IOException("The current store has no products to share.");
        String name=safeFileName(sessionName).replaceAll("[^0-9A-Za-z._ -]","_");
        java.io.File file=new java.io.File(sharedDirectory(),"ONHAND "+name+".txt");
        try(java.io.Writer out=new java.io.OutputStreamWriter(new java.io.FileOutputStream(file),StandardCharsets.UTF_8)){
            out.write("#ICE_ONHAND_PROJECT\\tROLE=COUNT_USER\\r\\nQuantity\\tBarcode\\tDescription\\tPrice\\r\\n");
            for(InventoryDb.Row row:rows){
                if(row.barcode==null||row.barcode.trim().isEmpty())continue;
                out.write("0\\t"+shareField(row.barcode)+"\\t"+shareField(row.description)+"\\t"+shareField(row.price)+"\\r\\n");
            }
        }
        return file;
    }

    private String shareField(String value){return value==null?"":value.replace('\\t',' ').replace('\\r',' ').replace('\\n',' ');}
    private Uri sharedUri(java.io.File file){return Uri.parse("content://"+getPackageName()+".fileprovider/onhand/"+Uri.encode(file.getName()));}
    private void sendSharedFile(java.io.File file,String mime,String title){
        Uri uri=sharedUri(file);Intent intent=new Intent(Intent.ACTION_SEND);
        intent.setType(mime);intent.putExtra(Intent.EXTRA_STREAM,uri);
        intent.setClipData(android.content.ClipData.newRawUri(file.getName(),uri));
        intent.addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION);
        startActivity(Intent.createChooser(intent,title));
    }

    private void shareInstalledApk(){
        if(!isMasterDevice()){toast("Only the Master phone shares the app with Count Users");return;}
        try{sendSharedFile(installedApkFile(),"application/vnd.android.package-archive","Share installed OnHand "+installedVersion());}
        catch(Exception e){showError("Could not share installed APK",e);}
    }

    private void shareCurrentCountFile(){
        try{sendSharedFile(currentCountFile(),"text/plain","Share current count file — zero quantities");}
        catch(Exception e){showError("Could not share current store",e);}
    }

    private void shareCountPackage(){
        if(!isMasterDevice()){toast("Only the Master phone shares a count package");return;}
        try{
            java.io.File apk=installedApkFile();java.io.File count=currentCountFile();
            String base=safeFileName(sessionName).replaceAll("[^0-9A-Za-z._ -]","_");
            java.io.File zip=new java.io.File(sharedDirectory(),"OnHand "+base+" - App and Count.zip");
            try(java.util.zip.ZipOutputStream output=new java.util.zip.ZipOutputStream(new java.io.FileOutputStream(zip))){
                for(java.io.File file:new java.io.File[]{apk,count}){
                    output.putNextEntry(new java.util.zip.ZipEntry(file.getName()));
                    try(java.io.InputStream input=new java.io.FileInputStream(file)){
                        byte[] buffer=new byte[8192];int length;
                        while((length=input.read(buffer))!=-1)output.write(buffer,0,length);
                    }
                    output.closeEntry();
                }
            }
            sendSharedFile(zip,"application/zip","Share OnHand app + current store with Count User");
        }catch(Exception e){showError("Could not share app and current store",e);}
    }

    private void showShareHelp(){
        new AlertDialog.Builder(this).setTitle("Sharing with Count Users")
            .setMessage("NEW PHONE + STORE: Choose APK + current store. Send the ZIP. On the receiving phone, extract it, install the APK, set a User Name, then import the ONHAND TXT file using REPLACE CURRENT INVENTORY. The phone stays a Count User.\\n\\nAPP UPDATE ONLY: Choose APK only. Install it over the existing app. Do not import a count file if the user is already counting this store.\\n\\nNEW STORE, APP ALREADY INSTALLED: Choose current count file only. The receiving Count User imports the TXT file using REPLACE CURRENT INVENTORY after finishing/exporting the earlier count.\\n\\nThe shared store file contains products and prices with all quantities zero. Check the store name at the top before scanning. Never uninstall the app to update it: uninstalling can remove local counts.")
            .setPositiveButton("OK",null).show();
    }

'''+source[closing:]
Path(m).write_text(source)
rep('app/src/main/java/com/iceinventory/onhand/ShareFileProvider.java',
'''?"application/vnd.android.package-archive":"text/plain";}''',
'''?"application/vnd.android.package-archive":uri.getLastPathSegment().toLowerCase(java.util.Locale.US).endsWith(".zip")?"application/zip":"text/plain";}''')
assert 'out.write("0\\t"+shareField(row.barcode)' in Path(m).read_text()
print('Prepared iCE OnHand 3.0.146: Master-only app + zero-quantity current store sharing')
