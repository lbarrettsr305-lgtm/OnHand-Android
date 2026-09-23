from pathlib import Path

base = Path('.github/prepare_30153.py')
exec(compile(base.read_text(), str(base), 'exec'), {'__name__': '__main__', '__file__': str(base)})


def rep(path, old, new):
    target = Path(path)
    source = target.read_text()
    if source.count(old) != 1:
        raise SystemExit('3.0.154 expected one target: ' + old[:120])
    target.write_text(source.replace(old, new, 1))


rep('app/build.gradle', 'versionCode 30153', 'versionCode 30154')
rep('app/build.gradle', "versionName '3.0.153'", "versionName '3.0.154'")
rep('app/src/main/AndroidManifest.xml', 'iCE Onhand 3.0.153', 'iCE Onhand 3.0.154')
m = 'app/src/main/java/com/iceinventory/onhand/MainActivity.java'
rep(m, 'Onhand Inventory 3.0.153', 'Onhand Inventory 3.0.154')

rep(m, '        root.addView(actionBar);\n        countActionBar=actionBar;',
       '        countActionBar=actionBar;')
rep(m,
'''        screen.addView(mainScroll,new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT,0,1));
        screen.addView(io,new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT,dp(60)));''',
'''        screen.addView(mainScroll,new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT,0,1));
        screen.addView(actionBar,new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT,dp(58)));
        screen.addView(io,new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT,dp(60)));''')
rep(m,
'''    private void setCountingKeyboardMode(boolean active){
        if(bottomIoBar!=null)bottomIoBar.setVisibility(active?View.GONE:View.VISIBLE);
        if(active&&countActionBar!=null)countActionBar.postDelayed(()->countActionBar.requestRectangleOnScreen(new android.graphics.Rect(0,0,countActionBar.getWidth(),countActionBar.getHeight()),true),100);
    }''',
'''    private void setCountingKeyboardMode(boolean active){
        if(bottomIoBar!=null)bottomIoBar.setVisibility(active?View.GONE:View.VISIBLE);
        if(countActionBar!=null)countActionBar.setVisibility(View.VISIBLE);
    }''')

rep(m,
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
    }''',
'''    private void showMasterShareMenu(){
        if(!isMasterDevice()){toast("Only the Master phone can share with Count Users");return;}
        hideKeyboard();
        LinearLayout panel=new LinearLayout(this);panel.setOrientation(LinearLayout.VERTICAL);
        panel.setPadding(dp(14),dp(8),dp(14),dp(8));
        final AlertDialog[] holder=new AlertDialog[1];
        Button newPhone=button("NEW PHONE + CURRENT STORE\\nApp and count ZIP",1);
        Button appOnly=button("APP UPDATE ONLY\\nAPK "+installedVersion(),2);
        Button newStore=button("NEW STORE ONLY\\nCurrent zero-quantity TXT",1);
        Button help=button("HELP\\nWhat to send and how to receive",0);
        Button[] buttons={newPhone,appOnly,newStore,help};
        for(Button b:buttons){
            b.setTextSize(16);b.setGravity(Gravity.CENTER);b.setAllCaps(false);
            LinearLayout.LayoutParams lp=new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT,dp(68));
            lp.setMargins(0,dp(5),0,dp(5));panel.addView(b,lp);
        }
        newPhone.setOnClickListener(v->{holder[0].dismiss();shareCountPackage();});
        appOnly.setOnClickListener(v->{holder[0].dismiss();shareInstalledApk();});
        newStore.setOnClickListener(v->{holder[0].dismiss();shareCurrentCountFile();});
        help.setOnClickListener(v->{holder[0].dismiss();showShareHelp();});
        holder[0]=new AlertDialog.Builder(this).setTitle("Share with Count Users")
                .setView(panel).setNegativeButton("Cancel",null).create();
        holder[0].show();
    }''')

print('Prepared iCE OnHand 3.0.154: fixed quantity footer and separated Share actions')
