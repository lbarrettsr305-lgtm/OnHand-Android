from pathlib import Path

base=Path('.github/prepare_30148.py')
exec(compile(base.read_text(),str(base),'exec'),{'__name__':'__main__','__file__':str(base)})

def rep(path,old,new):
    p=Path(path);s=p.read_text()
    if s.count(old)!=1:raise SystemExit('3.0.149 expected one target: '+old[:80])
    p.write_text(s.replace(old,new,1))

rep('app/build.gradle','versionCode 30148','versionCode 30149')
rep('app/build.gradle',"versionName '3.0.148'","versionName '3.0.149'")
rep('app/src/main/AndroidManifest.xml','iCE Onhand 3.0.148','iCE Onhand 3.0.149')
m='app/src/main/java/com/iceinventory/onhand/MainActivity.java'
rep(m,'Onhand Inventory 3.0.148','Onhand Inventory 3.0.149')
rep(m,
'''        root.setOnApplyWindowInsetsListener((v,insets)->{
            int bottom=Build.VERSION.SDK_INT>=20?insets.getSystemWindowInsetBottom():0;
            v.setPadding(dp(10),dp(6),dp(10),Math.max(dp(6),bottom+dp(4)));
            return insets;
        });''',
'''        LinearLayout screen=new LinearLayout(this);screen.setOrientation(LinearLayout.VERTICAL);
        screen.setBackgroundColor(Color.BLACK);
        screen.setOnApplyWindowInsetsListener((v,insets)->{
            int bottom=Build.VERSION.SDK_INT>=20?insets.getSystemWindowInsetBottom():0;
            v.setPadding(0,0,0,Math.max(0,bottom));
            return insets;
        });''')
rep(m,
'''        Button options=button("⚙ Options",0);options.setOnClickListener(v->showOptions());
        sessionBar.addView(inventories,new LinearLayout.LayoutParams(0,dp(48),1));
        LinearLayout.LayoutParams mid=new LinearLayout.LayoutParams(0,dp(48),1);mid.setMargins(dp(4),0,dp(4),0);
        sessionBar.addView(fresh,mid);
        sessionBar.addView(options,new LinearLayout.LayoutParams(0,dp(48),1));
        root.addView(sessionBar);
        if(isMasterDevice()){
            Button shareUsers=button("📤 SHARE WITH COUNT USERS",2);
            shareUsers.setTextSize(17);
            shareUsers.setTypeface(Typeface.DEFAULT,Typeface.BOLD);
            shareUsers.setOnClickListener(v->showMasterShareMenu());
            LinearLayout.LayoutParams shareLp=new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT,dp(56));
            shareLp.setMargins(0,dp(6),0,dp(5));root.addView(shareUsers,shareLp);
        }''',
'''        Button options=button("⚙ Options",0);options.setOnClickListener(v->showOptions());
        sessionBar.addView(inventories,new LinearLayout.LayoutParams(0,dp(48),1));
        LinearLayout.LayoutParams mid=new LinearLayout.LayoutParams(0,dp(48),1);mid.setMargins(dp(4),0,dp(4),0);
        sessionBar.addView(fresh,mid);
        if(isMasterDevice()){
            Button shareUsers=button("📤 Share",2);shareUsers.setTextSize(12);
            shareUsers.setSingleLine(true);shareUsers.setContentDescription("Share with Count Users");
            shareUsers.setOnClickListener(v->showMasterShareMenu());
            LinearLayout.LayoutParams shareLp=new LinearLayout.LayoutParams(0,dp(48),1);
            shareLp.setMargins(0,0,dp(4),0);sessionBar.addView(shareUsers,shareLp);
        }
        sessionBar.addView(options,new LinearLayout.LayoutParams(0,dp(48),1));
        root.addView(sessionBar);''')
rep(m,
'''        root.addView(listArea,new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT,0,1));''',
'''        list.setNestedScrollingEnabled(true);
        root.addView(listArea,new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT,dp(230)));''')
rep(m,
'''        root.addView(io);

        setContentView(root);
        root.requestApplyInsets();''',
'''        io.setPadding(dp(10),dp(4),dp(10),dp(4));
        ScrollView mainScroll=new ScrollView(this);
        mainScroll.setFillViewport(false);
        mainScroll.addView(root,new ScrollView.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT,ViewGroup.LayoutParams.WRAP_CONTENT));
        screen.addView(mainScroll,new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT,0,1));
        screen.addView(io,new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT,dp(60)));
        setContentView(screen);
        screen.requestApplyInsets();''')
rep('app/src/main/java/com/iceinventory/onhand/HelpActivity.java',
'''The Master phone has a SHARE WITH COUNT USERS button directly below the top row.''',
'''The Master phone has a Share button in the top row. Tap it, then choose NEW STORE ONLY to send the current zero-quantity TXT file. START / IMPORT and Export remain at the bottom of the screen.''')
assert 'screen.addView(io' in Path(m).read_text()
print('Prepared iCE OnHand 3.0.149: compact Share tab and fixed Import/Export footer')
