from pathlib import Path

base = Path('.github/prepare_30155.py')
exec(compile(base.read_text(), str(base), 'exec'), {'__name__': '__main__', '__file__': str(base)})


def rep(path, old, new, label):
    target = Path(path)
    source = target.read_text()
    if source.count(old) != 1:
        raise SystemExit('3.0.156 expected one target for ' + label)
    target.write_text(source.replace(old, new, 1))


rep('app/build.gradle', 'versionCode 30155', 'versionCode 30156', 'Gradle code')
rep('app/build.gradle', "versionName '3.0.155'", "versionName '3.0.156'", 'Gradle name')
rep('app/src/main/AndroidManifest.xml', 'iCE Onhand 3.0.155', 'iCE Onhand 3.0.156', 'manifest version')
rep('app/src/main/java/com/iceinventory/onhand/MainActivity.java',
    'Onhand Inventory 3.0.155', 'Onhand Inventory 3.0.156', 'visible version')

m = 'app/src/main/java/com/iceinventory/onhand/MonthlyInventoryActivity.java'
rep(m,
    'chooseSource=button("1. Import Petrosoft Price Management Excel");chooseSource.setOnClickListener(v->pickSource());root.addView(chooseSource,params(58));',
    'chooseSource=button("1. IMPORT PRICE MANAGEMENT EXCEL");chooseSource.setOnClickListener(v->pickSource());root.addView(chooseSource,params(62));',
    'clear import label')

main_path = 'app/src/main/java/com/iceinventory/onhand/MainActivity.java'
rep(main_path, 'private Spinner location;\n    private LinearLayout bottomIoBar;',
    'private Spinner location;\n    private TextView currentLocationBanner;\n    private LinearLayout bottomIoBar;',
    'current location field')
rep(main_path,
    '''        LinearLayout labels=new LinearLayout(this);labels.setOrientation(LinearLayout.HORIZONTAL);''',
    '''        currentLocationBanner=text("CURRENT LOCATION: NOT SET",17,gold(),true);
        currentLocationBanner.setGravity(Gravity.CENTER);
        currentLocationBanner.setPadding(dp(8),dp(7),dp(8),dp(7));
        currentLocationBanner.setBackgroundColor(darkGreen());
        root.addView(currentLocationBanner,new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT,dp(44)));

        LinearLayout labels=new LinearLayout(this);labels.setOrientation(LinearLayout.HORIZONTAL);''',
    'current location banner')
rep(main_path,
    '''        if(confirmedLocationSession==sessionId){
            for(int i=0;i<locs.size();i++)if(locs.get(i).equalsIgnoreCase(confirmedLocation)){location.setSelection(i);break;}
        }
    }''',
    '''        if(confirmedLocationSession==sessionId){
            for(int i=0;i<locs.size();i++)if(locs.get(i).equalsIgnoreCase(confirmedLocation)){location.setSelection(i);break;}
        }
        if(currentLocationBanner!=null)currentLocationBanner.setText("CURRENT LOCATION: "+
                (confirmedLocationSession==sessionId&&!confirmedLocation.isEmpty()?confirmedLocation.toUpperCase(java.util.Locale.US):"NOT SET"));
    }''',
    'current location refresh')
rep(main_path, '        root.addView(actionBar);\n        countActionBar=actionBar;',
    '        countActionBar=actionBar;', 'fixed count footer removal')
rep(main_path,
    '''        screen.addView(mainScroll,new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT,0,1));
        screen.addView(io,new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT,dp(60)));''',
    '''        screen.addView(mainScroll,new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT,0,1));
        screen.addView(actionBar,new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT,dp(58)));
        screen.addView(io,new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT,dp(60)));''',
    'fixed count footer placement')
rep(main_path,
    '''    private void setCountingKeyboardMode(boolean active){
        if(bottomIoBar!=null)bottomIoBar.setVisibility(active?View.GONE:View.VISIBLE);
        if(active&&countActionBar!=null){
            // Samsung keyboards finish resizing after their toolbar and number pad animate in.
            // Re-request the ADD QTY row after each stage so it stays fully above the keyboard.
            countActionBar.postDelayed(this::revealCountActionBar,120);
            countActionBar.postDelayed(this::revealCountActionBar,350);
            countActionBar.postDelayed(this::revealCountActionBar,700);
        }
    }''',
    '''    private void setCountingKeyboardMode(boolean active){
        if(bottomIoBar!=null)bottomIoBar.setVisibility(active?View.GONE:View.VISIBLE);
        if(countActionBar!=null)countActionBar.setVisibility(View.VISIBLE);
    }''',
    'keyboard-safe count footer')

monthly = Path(m).read_text()
for required in ('1. IMPORT PRICE MANAGEMENT EXCEL', '7. CUSTOMER IMPORT REPORT',
                 'Color.rgb(255,215,0)', 'MonthlyCategoryXlsxWriter.writeCategorySummary',
                 'MonthlyCategoryXlsxWriter.writeCigarettes', 'CATEGORYNAME'):
    if required not in monthly:
        raise SystemExit('3.0.156 verification missing: ' + required)

main = Path('app/src/main/java/com/iceinventory/onhand/MainActivity.java').read_text()
for required in ('▥ Store Map', 'showMoveLocation', 'CURRENT LOCATION:'):
    if required not in main:
        raise SystemExit('3.0.156 location feature missing: ' + required)

print('Prepared iCE OnHand 3.0.156: Store Map plus clear Petrosoft import and category reports')
