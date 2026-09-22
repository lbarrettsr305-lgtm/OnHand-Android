from pathlib import Path

base=Path('.github/prepare_30147.py')
exec(compile(base.read_text(),str(base),'exec'),{'__name__':'__main__','__file__':str(base)})

def rep(path,old,new):
    p=Path(path);s=p.read_text()
    if s.count(old)!=1:raise SystemExit('3.0.148 expected one target: '+old[:80])
    p.write_text(s.replace(old,new,1))

rep('app/build.gradle','versionCode 30147','versionCode 30148')
rep('app/build.gradle',"versionName '3.0.147'","versionName '3.0.148'")
rep('app/src/main/AndroidManifest.xml','iCE Onhand 3.0.147','iCE Onhand 3.0.148')
m='app/src/main/java/com/iceinventory/onhand/MainActivity.java'
rep(m,'Onhand Inventory 3.0.147','Onhand Inventory 3.0.148')
rep(m,
'''        root.addView(sessionBar);
        android.content.SharedPreferences mw=''',
'''        root.addView(sessionBar);
        if(isMasterDevice()){
            Button shareUsers=button("📤 SHARE WITH COUNT USERS",2);
            shareUsers.setTextSize(17);
            shareUsers.setTypeface(Typeface.DEFAULT,Typeface.BOLD);
            shareUsers.setOnClickListener(v->showMasterShareMenu());
            LinearLayout.LayoutParams shareLp=new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT,dp(56));
            shareLp.setMargins(0,dp(6),0,dp(5));root.addView(shareUsers,shareLp);
        }
        android.content.SharedPreferences mw=''' )
source=Path(m).read_text()
opening=source.index('        if(masterDevice){\n            TextView sharing=text("Share with Count Users"')
closing=source.index('        Button help=button("❓ Help / Instructions",0);',opening)
source=source[:opening]+source[closing:]
Path(m).write_text(source)
rep(m,
'''        TextView scanning=text("Scanning",16,gold(),true);''',
'''        if(isMasterDevice()){
            Button shareShortcut=button("📤 SHARE WITH COUNT USERS",2);
            shareShortcut.setOnClickListener(v->showMasterShareMenu());
            box.addView(shareShortcut,new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT,dp(56)));
        }
        TextView scanning=text("Scanning",16,gold(),true);''')
rep(m,
'''    private void showShareHelp(){''',
'''    private void showMasterShareMenu(){
        if(!isMasterDevice()){toast("Only the Master phone can share with Count Users");return;}
        hideKeyboard();
        String[] choices={"NEW PHONE + CURRENT STORE — app and count ZIP",
                "APP UPDATE ONLY — APK "+installedVersion(),
                "NEW STORE ONLY — current zero-quantity TXT",
                "HELP — what to send and how to receive"};
        new AlertDialog.Builder(this).setTitle("Share with Count Users")
                .setItems(choices,(d,which)->{
                    if(which==0)shareCountPackage();
                    else if(which==1)shareInstalledApk();
                    else if(which==2)shareCurrentCountFile();
                    else showShareHelp();
                }).setNegativeButton("Cancel",null).show();
    }

    private void showShareHelp(){''')
rep(m,
'''"NEW PHONE + STORE: Choose APK + current store. Send the ZIP.''',
'''"NEW PHONE + CURRENT STORE: Choose app and count ZIP. Send the ZIP.''')
rep('app/src/main/java/com/iceinventory/onhand/HelpActivity.java',
'''The Master phone can share the app and current store from Options.''',
'''The Master phone has a SHARE WITH COUNT USERS button directly below the top row.''')
rep('app/src/main/java/com/iceinventory/onhand/HelpActivity.java',
'''On the Master phone, open Options. For a new phone and store,''',
'''On the Master phone, tap SHARE WITH COUNT USERS below the top row. For a new phone and store,''')
assert 'shareUsers.setOnClickListener(v->showMasterShareMenu())' in Path(m).read_text()
print('Prepared iCE OnHand 3.0.148: visible Master share button and clear small-screen chooser')
