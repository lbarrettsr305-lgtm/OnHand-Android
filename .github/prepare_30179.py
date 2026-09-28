from pathlib import Path

base = Path('.github/prepare_30178.py')
exec(compile(base.read_text(), str(base), 'exec'), {'__name__': '__main__', '__file__': str(base)})


def rep(path, old, new, label):
    p = Path(path); s = p.read_text()
    if s.count(old) != 1:
        raise SystemExit('3.0.179 target '+label+' count '+str(s.count(old)))
    p.write_text(s.replace(old, new, 1))


rep('app/build.gradle','versionCode 30178','versionCode 30179','code')
rep('app/build.gradle',"versionName '3.0.178'","versionName '3.0.179'",'name')
rep('app/src/main/AndroidManifest.xml','iCE Onhand 3.0.178','iCE Onhand 3.0.179','manifest')

main='app/src/main/java/com/iceinventory/onhand/MainActivity.java'
rep(main,'Onhand Inventory 3.0.178','Onhand Inventory 3.0.179','header')
rep(main,
'''            Button shareUsers=button("SHARE WITH\\nCOUNTERS",2);shareUsers.setTextSize(9);
            shareUsers.setSingleLine(false);shareUsers.setMaxLines(2);shareUsers.setGravity(Gravity.CENTER);shareUsers.setPadding(2,0,2,0);shareUsers.setContentDescription("Share app or current store with counters");''',
'''            Button shareUsers=button("SHARE WITH\\nUSERS",2);shareUsers.setTextSize(9);
            shareUsers.setSingleLine(false);shareUsers.setMaxLines(2);shareUsers.setGravity(Gravity.CENTER);shareUsers.setPadding(2,0,2,0);shareUsers.setContentDescription("Share app or current store with Masters or counters");''',
'share with users label')
rep(main,'Button shareShortcut=button("📤 SHARE WITH COUNT USERS",2);','Button shareShortcut=button("📤 SHARE WITH USERS",2);','options share label')

rep(main,
'''    private java.io.File currentCountFile() throws java.io.IOException {
        if(!isMasterDevice())throw new java.io.IOException("Only the Master phone can share the current store.");''',
'''    private java.io.File currentCountFile() throws java.io.IOException {return currentCountFile(false);}

    private java.io.File currentCountFile(boolean masterCandidate) throws java.io.IOException {
        if(!isMasterDevice())throw new java.io.IOException("Only the Master phone can share the current store.");''',
'role-aware count file')
rep(main,
'''        java.io.File file=new java.io.File(sharedDirectory(),"ONHAND "+name+".txt");
        try(java.io.Writer out=new java.io.OutputStreamWriter(new java.io.FileOutputStream(file),StandardCharsets.UTF_8)){
            out.write("#ICE_ONHAND_PROJECT\\tROLE=COUNT_USER\\tMASTER_PIN_HASH="+prefs().getString(KEY_MASTER_PIN_HASH,"")+"\\r\\nQuantity\\tBarcode\\tDescription\\tPrice\\r\\n");''',
'''        java.io.File file=new java.io.File(sharedDirectory(),"ONHAND "+name+(masterCandidate?" MASTER":"")+".txt");
        try(java.io.Writer out=new java.io.OutputStreamWriter(new java.io.FileOutputStream(file),StandardCharsets.UTF_8)){
            out.write("#ICE_ONHAND_PROJECT\\tROLE="+(masterCandidate?"MASTER_CANDIDATE":"COUNT_USER")+"\\tMASTER_PIN_HASH="+prefs().getString(KEY_MASTER_PIN_HASH,"")+"\\r\\nQuantity\\tBarcode\\tDescription\\tPrice\\r\\n");''',
'master candidate metadata')

anchor='''    private void showMasterShareMenu(){'''
master_methods='''    private void verifyMasterPinForMasterShare(Runnable next){
        String expected=prefs().getString(KEY_MASTER_PIN_HASH,"");if(expected.isEmpty()){toast("Create the Master PIN first");return;}
        EditText pin=masterPinEntry("4-digit Master PIN");AlertDialog dialog=new AlertDialog.Builder(this).setTitle("Authorize New Master Phone").setMessage("Enter the Master PIN before creating a package that can authorize another Master phone.").setView(pin).setPositiveButton("AUTHORIZE",null).setNegativeButton("Cancel",null).create();
        dialog.setOnShowListener(x->dialog.getButton(AlertDialog.BUTTON_POSITIVE).setOnClickListener(v->{if(!expected.equals(hashMasterPin(pin.getText().toString()))){toast("Incorrect Master PIN");pin.selectAll();return;}dialog.dismiss();next.run();}));dialog.show();
    }

    private void shareMasterPackage(){
        if(!isMasterDevice()){toast("Only an authorized Master phone can create this package");return;}
        try{
            java.io.File apk=installedApkFile();java.io.File count=currentCountFile(true);
            String base=safeFileName(sessionName).replaceAll("[^0-9A-Za-z._ -]","_");
            java.io.File zip=new java.io.File(sharedDirectory(),"OnHand "+base+" - New Master.zip");
            try(java.util.zip.ZipOutputStream output=new java.util.zip.ZipOutputStream(new java.io.FileOutputStream(zip))){for(java.io.File file:new java.io.File[]{apk,count}){output.putNextEntry(new java.util.zip.ZipEntry(file.getName()));try(java.io.InputStream input=new java.io.FileInputStream(file)){byte[] buffer=new byte[8192];int length;while((length=input.read(buffer))!=-1)output.write(buffer,0,length);}output.closeEntry();}}
            sendSharedFile(zip,"application/zip","Share OnHand app + current store with new Master");
        }catch(Exception e){showError("Could not share new Master package",e);}
    }

'''
rep(main,anchor,master_methods+anchor,'master share methods')

rep(main,
'''        String[] choices={"NEW COUNTER PHONE — Send App + Current Store",
                "UPDATE COUNTER APP — Send APK Only ("+installedVersion()+")",
                "EXISTING COUNTER PHONE — Send Current Store File Only",
                "HELP — What Should I Send?"};
        new AlertDialog.Builder(this).setTitle("Share With Counters")
                .setItems(choices,(d,which)->{
                    if(which==0)shareCountPackage();
                    else if(which==1)shareInstalledApk();
                    else if(which==2)shareCurrentCountFile();
                    else showShareHelp();
                }).setNegativeButton("Cancel",null).show();''',
'''        String[] choices={"NEW COUNTER PHONE — Send App + Current Store",
                "NEW MASTER PHONE — Send App + Current Store",
                "UPDATE USER APP — Send APK Only ("+installedVersion()+")",
                "EXISTING USER PHONE — Send Current Store File Only",
                "HELP — What Should I Send?"};
        new AlertDialog.Builder(this).setTitle("Share With Users")
                .setItems(choices,(d,which)->{
                    if(which==0)shareCountPackage();
                    else if(which==1)verifyMasterPinForMasterShare(this::shareMasterPackage);
                    else if(which==2)shareInstalledApk();
                    else if(which==3)shareCurrentCountFile();
                    else showShareHelp();
                }).setNegativeButton("Cancel",null).show();''',
'share menu')

rep(main,
'''        new AlertDialog.Builder(this).setTitle("Sharing with Count Users")
            .setMessage("NEW PHONE + CURRENT STORE: Choose app and count ZIP. Send the ZIP. On the receiving phone, extract it, install the APK, set a User Name, then import the ONHAND TXT file using REPLACE CURRENT INVENTORY. The phone stays a Count User.\\n\\nAPP UPDATE ONLY: Choose APK only. Install it over the existing app. Do not import a count file if the user is already counting this store.\\n\\nNEW STORE, APP ALREADY INSTALLED: Choose current count file only. The receiving Count User imports the TXT file using REPLACE CURRENT INVENTORY after finishing/exporting the earlier count.\\n\\nThe shared store file contains products and prices with all quantities zero. Check the store name at the top before scanning. Never uninstall the app to update it: uninstalling can remove local counts.")''',
'''        new AlertDialog.Builder(this).setTitle("Sharing with Users")
            .setMessage("NEW COUNTER PHONE: Send the app + current store ZIP. Install the APK and import the ONHAND TXT. The phone remains a Count User.\\n\\nNEW MASTER PHONE: Enter the Master PIN on this phone, send the protected Master ZIP, install the APK, and import the ONHAND MASTER TXT. On the receiving phone, enter the Master PIN and select Chief, Lbsr, or Lbjr.\\n\\nAPP UPDATE: Send APK only and install over the existing app. Never uninstall during an active count.\\n\\nNEW STORE: If the app is already installed, send only the current zero-quantity store file.")''',
'share help')

rep(main,
'''    private void applySharedProjectRole(Uri uri){
        String verifier="";
        try(InputStream in=getContentResolver().openInputStream(uri);BufferedReader br=new BufferedReader(new InputStreamReader(in,StandardCharsets.UTF_8))){String first=br.readLine();if(first!=null&&first.startsWith("#ICE_ONHAND_PROJECT\\t")){for(String part:first.split("\\t")){if(part.startsWith("MASTER_PIN_HASH="))verifier=part.substring("MASTER_PIN_HASH=".length()).trim();}}}catch(Exception ignored){}
        if(!isMasterDevice()){android.content.SharedPreferences.Editor e=prefs().edit().putString(KEY_DEVICE_ROLE,ROLE_COUNT_USER).remove(KEY_MASTER_PIN_HASH).remove(KEY_MASTER_USER);if(verifier.matches("[0-9a-fA-F]{64}"))e.putString(KEY_AUTHORIZED_MASTER_PIN_HASH,verifier);e.apply();}
        refreshOperatorStatus();
    }''',
'''    private void applySharedProjectRole(Uri uri){
        String verifier="",role="";
        try(InputStream in=getContentResolver().openInputStream(uri);BufferedReader br=new BufferedReader(new InputStreamReader(in,StandardCharsets.UTF_8))){String first=br.readLine();if(first!=null&&first.startsWith("#ICE_ONHAND_PROJECT\\t")){for(String part:first.split("\\t")){if(part.startsWith("MASTER_PIN_HASH="))verifier=part.substring("MASTER_PIN_HASH=".length()).trim();else if(part.startsWith("ROLE="))role=part.substring("ROLE=".length()).trim();}}}catch(Exception ignored){}
        if(!isMasterDevice()){android.content.SharedPreferences.Editor e=prefs().edit().putString(KEY_DEVICE_ROLE,ROLE_COUNT_USER).remove(KEY_MASTER_PIN_HASH).remove(KEY_MASTER_USER).putBoolean("pending_master_candidate","MASTER_CANDIDATE".equals(role));if(verifier.matches("[0-9a-fA-F]{64}"))e.putString(KEY_AUTHORIZED_MASTER_PIN_HASH,verifier);e.apply();}
        refreshOperatorStatus();
    }

    private void offerMasterCandidateActivation(){
        if(!prefs().getBoolean("pending_master_candidate",false)||isMasterDevice())return;
        String expected=prefs().getString(KEY_AUTHORIZED_MASTER_PIN_HASH,"");if(expected.isEmpty()){toast("Master authorization is missing");return;}
        EditText pin=masterPinEntry("4-digit Master PIN");AlertDialog dialog=new AlertDialog.Builder(this).setTitle("ACTIVATE MASTER PHONE").setMessage("Enter the Master PIN. After verification, select Chief, Lbsr, or Lbjr.").setView(pin).setPositiveButton("ACTIVATE",null).setNegativeButton("KEEP AS COUNT USER",(d,w)->prefs().edit().putBoolean("pending_master_candidate",false).apply()).create();
        dialog.setOnShowListener(x->dialog.getButton(AlertDialog.BUTTON_POSITIVE).setOnClickListener(v->{if(!expected.equals(hashMasterPin(pin.getText().toString()))){toast("Incorrect Master PIN");pin.selectAll();return;}prefs().edit().putString(KEY_DEVICE_ROLE,ROLE_MASTER).putString(KEY_MASTER_PIN_HASH,expected).remove(KEY_MASTER_USER).putBoolean("pending_master_candidate",false).apply();dialog.dismiss();refreshOperatorStatus();toast("Master phone authorized — select the Master name");promptUserName(false);buildUi();refreshLocations();refreshList();}));dialog.show();
    }''',
'master candidate activation')

rep(main,
'''        toast((replaceCurrent?"Replaced current data • ":"Appended • ")+"Imported "+imported+" tab-delimited TXT rows");''',
'''        toast((replaceCurrent?"Replaced current data • ":"Appended • ")+"Imported "+imported+" tab-delimited TXT rows");
        if(replaceCurrent)offerMasterCandidateActivation();''',
'activate after import')

s=Path(main).read_text()
checks={'version':"versionName '3.0.179'" in Path('app/build.gradle').read_text(),'button':'SHARE WITH\\nUSERS' in s,'options button':'📤 SHARE WITH USERS' in s,'menu':'NEW MASTER PHONE — Send App + Current Store' in s,'metadata':'MASTER_CANDIDATE' in s,'activation':'ACTIVATE MASTER PHONE' in s,'masters':'new String[]{"Chief","Lbsr","Lbjr"}' in s}
bad=[k for k,v in checks.items() if not v]
if bad: raise SystemExit('3.0.179 checks failed: '+', '.join(bad))
print('Prepared iCE OnHand 3.0.179: protected new Master phone sharing and activation')
