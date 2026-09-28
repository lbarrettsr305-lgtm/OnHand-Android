from pathlib import Path

base = Path('.github/prepare_30179.py')
exec(compile(base.read_text(), str(base), 'exec'), {'__name__': '__main__', '__file__': str(base)})


def rep(path, old, new, label):
    p = Path(path); s = p.read_text()
    if s.count(old) != 1:
        raise SystemExit('3.0.180 target '+label+' count '+str(s.count(old)))
    p.write_text(s.replace(old, new, 1))


rep('app/build.gradle','versionCode 30179','versionCode 30180','code')
rep('app/build.gradle',"versionName '3.0.179'","versionName '3.0.180'",'name')
rep('app/src/main/AndroidManifest.xml','iCE Onhand 3.0.179','iCE Onhand 3.0.180','manifest')

main='app/src/main/java/com/iceinventory/onhand/MainActivity.java'
rep(main,'Onhand Inventory 3.0.179','Onhand Inventory 3.0.180','header')

old='''    private void showMasterShareMenu(){
        if(!isMasterDevice()){toast("Only the Master phone can share with Count Users");return;}
        hideKeyboard();
        String[] choices={"NEW COUNTER PHONE — Send App + Current Store",
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
                }).setNegativeButton("Cancel",null).show();
    }
'''

new='''    private LinearLayout.LayoutParams shareChoiceParams(){
        LinearLayout.LayoutParams p=new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT,dp(68));p.setMargins(0,dp(5),0,dp(5));return p;
    }

    private void showMasterShareMenu(){
        if(!isMasterDevice()){toast("Only the Master phone can share with users");return;}
        hideKeyboard();
        LinearLayout panel=new LinearLayout(this);panel.setOrientation(LinearLayout.VERTICAL);panel.setPadding(dp(14),dp(6),dp(14),dp(8));
        Button setup=button("1. SET UP NEW PHONE",1);setup.setTextSize(17);setup.setTypeface(Typeface.DEFAULT,Typeface.BOLD);panel.addView(setup,shareChoiceParams());
        Button update=button("2. UPDATE APP ONLY\\nSend APK • Keep Current Count",1);update.setTextSize(15);update.setSingleLine(false);update.setMaxLines(2);panel.addView(update,shareChoiceParams());
        Button store=button("3. SEND NEW STORE FILE\\nApp Already Installed",1);store.setTextSize(15);store.setSingleLine(false);store.setMaxLines(2);panel.addView(store,shareChoiceParams());
        Button help=button("4. HELP / INSTRUCTIONS",0);help.setTextSize(16);panel.addView(help,shareChoiceParams());
        AlertDialog dialog=new AlertDialog.Builder(this).setTitle("WHAT DO YOU WANT TO SHARE?").setView(panel).setNegativeButton("CANCEL",null).create();
        setup.setOnClickListener(v->{dialog.dismiss();showNewPhoneTypeMenu();});
        update.setOnClickListener(v->{dialog.dismiss();shareInstalledApk();});
        store.setOnClickListener(v->{dialog.dismiss();shareCurrentCountFile();});
        help.setOnClickListener(v->{dialog.dismiss();showShareHelp();});
        dialog.show();
    }

    private void showNewPhoneTypeMenu(){
        LinearLayout panel=new LinearLayout(this);panel.setOrientation(LinearLayout.VERTICAL);panel.setPadding(dp(14),dp(6),dp(14),dp(8));
        Button counter=button("COUNTER PHONE\\nApp + Current Store",1);counter.setTextSize(17);counter.setTypeface(Typeface.DEFAULT,Typeface.BOLD);counter.setSingleLine(false);counter.setMaxLines(2);panel.addView(counter,shareChoiceParams());
        Button master=button("MASTER PHONE — PIN REQUIRED\\nApp + Current Store",2);master.setTextSize(16);master.setTypeface(Typeface.DEFAULT,Typeface.BOLD);master.setSingleLine(false);master.setMaxLines(2);panel.addView(master,shareChoiceParams());
        AlertDialog dialog=new AlertDialog.Builder(this).setTitle("CHOOSE PHONE TYPE").setMessage("Select the role for the new phone.").setView(panel).setNegativeButton("BACK",(d,w)->showMasterShareMenu()).create();
        counter.setOnClickListener(v->{dialog.dismiss();shareCountPackage();});
        master.setOnClickListener(v->{dialog.dismiss();verifyMasterPinForMasterShare(this::shareMasterPackage);});
        dialog.show();
    }
'''
rep(main,old,new,'large share buttons')

s=Path(main).read_text()
checks={'version':"versionName '3.0.180'" in Path('app/build.gradle').read_text(),'main menu':'WHAT DO YOU WANT TO SHARE?' in s,'setup':'1. SET UP NEW PHONE' in s,'update':'2. UPDATE APP ONLY' in s,'store':'3. SEND NEW STORE FILE' in s,'help':'4. HELP / INSTRUCTIONS' in s,'role menu':'CHOOSE PHONE TYPE' in s and 'MASTER PHONE — PIN REQUIRED' in s,'protected':'verifyMasterPinForMasterShare(this::shareMasterPackage)' in s}
bad=[k for k,v in checks.items() if not v]
if bad: raise SystemExit('3.0.180 checks failed: '+', '.join(bad))
print('Prepared iCE OnHand 3.0.180: large guided Share With Users choices')
