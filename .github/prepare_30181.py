from pathlib import Path

base = Path('.github/prepare_30180.py')
exec(compile(base.read_text(), str(base), 'exec'), {'__name__': '__main__', '__file__': str(base)})


def rep(path, old, new, label):
    p = Path(path)
    s = p.read_text()
    if s.count(old) != 1:
        raise SystemExit('3.0.181 target ' + label + ' count ' + str(s.count(old)))
    p.write_text(s.replace(old, new, 1))


rep('app/build.gradle', 'versionCode 30180', 'versionCode 30181', 'code')
rep('app/build.gradle', "versionName '3.0.180'", "versionName '3.0.181'", 'name')
rep('app/src/main/AndroidManifest.xml', 'iCE Onhand 3.0.180', 'iCE Onhand 3.0.181', 'manifest')

main = 'app/src/main/java/com/iceinventory/onhand/MainActivity.java'
monthly = 'app/src/main/java/com/iceinventory/onhand/MonthlyInventoryActivity.java'
help_file = 'app/src/main/java/com/iceinventory/onhand/HelpActivity.java'

rep(main, 'Onhand Inventory 3.0.180', 'Onhand Inventory 3.0.181', 'header')
rep(monthly,
    'EXTRA_REPORT_TARGET="monthly_report_target";',
    'EXTRA_REPORT_TARGET="monthly_report_target",EXTRA_ADDONS_MODE="monthly_addons_mode";',
    'addons extra')

rep(main,
    'private boolean monthlyWorkflowMode,liqPosWorkflowMode,testScanMode,adminUnlocked;',
    'private boolean monthlyWorkflowMode,liqPosWorkflowMode,testScanMode,postCountAddOnsMode,adminUnlocked;',
    'addons field')
rep(main,
    'monthlyWorkflowMode=getIntent()!=null&&getIntent().getBooleanExtra(MonthlyInventoryActivity.EXTRA_MONTHLY_WORKFLOW,false);liqPosWorkflowMode=getIntent()!=null&&getIntent().getBooleanExtra(LiqPosInventoryActivity.EXTRA_LIQPOS_WORKFLOW,false);testScanMode=getIntent()!=null&&getIntent().getBooleanExtra(MonthlyInventoryActivity.EXTRA_TEST_SCAN,false);',
    'monthlyWorkflowMode=getIntent()!=null&&getIntent().getBooleanExtra(MonthlyInventoryActivity.EXTRA_MONTHLY_WORKFLOW,false);liqPosWorkflowMode=getIntent()!=null&&getIntent().getBooleanExtra(LiqPosInventoryActivity.EXTRA_LIQPOS_WORKFLOW,false);testScanMode=getIntent()!=null&&getIntent().getBooleanExtra(MonthlyInventoryActivity.EXTRA_TEST_SCAN,false);postCountAddOnsMode=getIntent()!=null&&getIntent().getBooleanExtra(MonthlyInventoryActivity.EXTRA_ADDONS_MODE,false);',
    'read addons mode')

rep(main,
    'Button monthly=button(monthlyWorkflowMode?"↩ RETURN TO MONTHLY INVENTORY — STEP 5":(resumableMonthly?"↩ RESUME MONTHLY INVENTORY WORKFLOW":"↩ REOPEN LAST MONTHLY PROJECT"),2);',
    'Button monthly=button(monthlyWorkflowMode?(postCountAddOnsMode?"↩ RETURN TO PETROSOFT FINAL REPORTS":"↩ GET USER FILES / COMBINE COUNTS"):(resumableMonthly?"↩ RESUME PETROSOFT MONTHLY INVENTORY":"↩ REOPEN LAST PETROSOFT PROJECT"),2);',
    'specific monthly navigation')
rep(main,
    'TextView monthlyHelp=text("MONTHLY PROJECT OPTIONS: Reopen/Resume above, or start a new monthly project below. The top + New button is for a standard inventory.",12,Color.WHITE,true);',
    'TextView monthlyHelp=text("PETROSOFT PROJECT: Use the button above to collect user files, combine counts, make AddOns, and export the customer import file. Top + New starts a regular inventory.",12,Color.WHITE,true);',
    'monthly help')
rep(main,
    'Button newMonthly=button("＋ START NEW MONTHLY PROJECT",1);',
    'Button newMonthly=button("＋ START NEW PETROSOFT MONTHLY INVENTORY",1);',
    'new monthly label')
rep(main,
    '.setTitle("Start New Monthly Project?")',
    '.setTitle("Start New Petrosoft Monthly Inventory?")',
    'new monthly dialog')

old_reports = '''        LinearLayout reportBar=new LinearLayout(this);reportBar.setOrientation(LinearLayout.HORIZONTAL);
        Button totals=button("▥ Store Map",0);totals.setOnClickListener(v->showLocationTotals());
        Button internet=button("◎ Internet Items",0);internet.setOnClickListener(v->showInternetItems());
        reportBar.addView(totals,new LinearLayout.LayoutParams(0,dp(44),1));
        LinearLayout.LayoutParams rbp=new LinearLayout.LayoutParams(0,dp(44),1);rbp.setMargins(dp(5),0,0,0);
        reportBar.addView(internet,rbp);
        root.addView(reportBar);'''
new_reports = '''        LinearLayout reportBar=new LinearLayout(this);reportBar.setOrientation(LinearLayout.HORIZONTAL);
        Button totals=button("▥ Store Map",0);totals.setTextSize(11);totals.setOnClickListener(v->showLocationTotals());
        Button manualItem=button("＋ Add Item",1);manualItem.setTextSize(11);manualItem.setOnClickListener(v->beginManualItem());
        Button internet=button("◎ Internet Items",0);internet.setTextSize(11);internet.setOnClickListener(v->showInternetItems());
        reportBar.addView(totals,new LinearLayout.LayoutParams(0,dp(46),1));
        LinearLayout.LayoutParams rbp=new LinearLayout.LayoutParams(0,dp(46),1);rbp.setMargins(dp(4),0,0,0);
        reportBar.addView(manualItem,rbp);
        LinearLayout.LayoutParams ibp=new LinearLayout.LayoutParams(0,dp(46),1);ibp.setMargins(dp(4),0,0,0);
        reportBar.addView(internet,ibp);
        root.addView(reportBar);'''
rep(main, old_reports, new_reports, 'regular add item button')

rep(main,
    '    private void addItem() {',
    '''    private void beginManualItem() {
        if(testScanMode){toast("Test scan only — adding items is disabled");return;}
        if(!requireCurrentCount()||!ensureCountingLocation())return;
        prefs().edit().putString(KEY_UNKNOWN_MODE,"add").apply();
        barcode.setText("");description.setText("");qty.setText("");currentPrice="";
        barcode.setShowSoftInputOnFocus(true);barcode.requestFocus();
        barcode.postDelayed(()->showKeyboard(barcode),80);
        toast("Scan or type the new barcode, enter its description and quantity, then press ADD QTY");
    }

    private void addItem() {''',
    'manual add method')

rep(main,
    'if(testScanMode){confirmedLocation="Main";confirmedLocationSession=sessionId;refreshLocations();if(currentLocationBanner!=null)currentLocationBanner.setText("TEST SCAN — BARCODE LOOKUP ONLY");if(countActionBar!=null)countActionBar.setVisibility(View.GONE);}',
    'if(testScanMode){confirmedLocation="Main";confirmedLocationSession=sessionId;refreshLocations();if(currentLocationBanner!=null)currentLocationBanner.setText("TEST SCAN — BARCODE LOOKUP ONLY");if(countActionBar!=null)countActionBar.setVisibility(View.GONE);}else if(postCountAddOnsMode){db.addLocation("AddOns");confirmedLocation="AddOns";confirmedLocationSession=sessionId;refreshLocations();if(currentLocationBanner!=null)currentLocationBanner.setText("CURRENT LOCATION: ADDONS");Toast.makeText(this,"AddOns is selected for missed or new items. Use Change Location for an adjustment to an existing area.",Toast.LENGTH_LONG).show();}',
    'automatic AddOns location')

scroll_hint = '''
        TextView scrollHint=text("SCROLL DOWN FOR ALL REPORTS ↓",13,Color.WHITE,true);
        scrollHint.setGravity(Gravity.CENTER);scrollHint.setPadding(0,dp(5),0,dp(5));
        exportPanel.addView(scrollHint);'''
rep(main, scroll_hint, '', 'remove incorrect scroll hint')

rep(monthly,
    'saveClient.setBackgroundTintList(android.content.res.ColorStateList.valueOf(Color.rgb(255,215,0)))',
    'saveClient.setBackgroundTintList(android.content.res.ColorStateList.valueOf(Color.rgb(0,190,90)))',
    'customer export green')
rep(monthly,
    'saveCombinedXlsx.setBackgroundTintList(android.content.res.ColorStateList.valueOf(Color.rgb(0,190,90)))',
    'saveCombinedXlsx.setBackgroundTintList(android.content.res.ColorStateList.valueOf(Color.rgb(255,193,7)))',
    'combined report yellow')
rep(monthly,
    'adjustCount=button("↩ Return to Counting / Adjust");',
    'adjustCount=button("POST-COUNT CORRECTIONS / ADDONS");adjustCount.setSingleLine(false);adjustCount.setMaxLines(2);adjustCount.setTypeface(android.graphics.Typeface.DEFAULT,android.graphics.Typeface.BOLD);adjustCount.setTextColor(Color.BLACK);adjustCount.setBackgroundTintList(android.content.res.ColorStateList.valueOf(Color.rgb(255,193,7)));',
    'addons button')
rep(monthly,
    'Intent count=new Intent(this,MainActivity.class);count.putExtra(EXTRA_SESSION_ID,deviceSessionId);count.putExtra(EXTRA_SESSION_NAME,base()+" "+day());count.putExtra(EXTRA_MONTHLY_WORKFLOW,true);startActivity(count);\n        Toast.makeText(this,"Adjust the count, export this device again, then reselect all user files at Step 5.",Toast.LENGTH_LONG).show();',
    'Intent count=new Intent(this,MainActivity.class);count.putExtra(EXTRA_SESSION_ID,deviceSessionId);count.putExtra(EXTRA_SESSION_NAME,base()+" "+day());count.putExtra(EXTRA_MONTHLY_WORKFLOW,true);count.putExtra(EXTRA_ADDONS_MODE,true);startActivity(count);\n        Toast.makeText(this,"Use AddOns for missed/new items, or Change Location for an adjustment to an existing area. Export the correction batch, then reselect all user files at Step 5.",Toast.LENGTH_LONG).show();',
    'launch addons mode')
rep(monthly,
    'if(adjustCount!=null)adjustCount.setEnabled(deviceSessionId>0);',
    'if(adjustCount!=null)adjustCount.setEnabled(countsReady&&deviceSessionId>0);',
    'addons after combine only')

rep(help_file,
    'section("11. Return to Counting / Adjust",\n   "Use ↩ Return to Counting / Adjust if a quantity, barcode, or location needs correction. Make the correction, return to the project workflow, reselect the corrected user files if required, and export fresh final reports.");',
    'section("11. Petrosoft Post-Count AddOns",\n   "After selecting and combining all user count files, use POST-COUNT CORRECTIONS / ADDONS. AddOns is selected by default for missed items, new items, and client-requested additions. For a quantity adjustment belonging to an existing aisle, cooler, checkout, or other area, press Change Location and select that original location before entering the positive or negative adjustment. Export the correction batch, reselect all user files at Step 5, and then create fresh final reports. Regular inventories can use the visible + Add Item button at any time.");',
    'help addons')

s = Path(main).read_text()
m = Path(monthly).read_text()
checks = {
    'version': "versionName '3.0.181'" in Path('app/build.gradle').read_text(),
    'specific Petrosoft resume': 'RESUME PETROSOFT MONTHLY INVENTORY' in s,
    'regular add item': 'Button manualItem=button("＋ Add Item",1)' in s and 'beginManualItem()' in s,
    'addons location': 'confirmedLocation="AddOns"' in s,
    'customer green': 'saveClient.setBackgroundTintList(android.content.res.ColorStateList.valueOf(Color.rgb(0,190,90)))' in m,
    'combined yellow': 'saveCombinedXlsx.setBackgroundTintList(android.content.res.ColorStateList.valueOf(Color.rgb(255,193,7)))' in m,
    'post count button': 'POST-COUNT CORRECTIONS / ADDONS' in m,
    'after combine only': 'adjustCount.setEnabled(countsReady&&deviceSessionId>0)' in m,
    'bad scroll hint removed': 'SCROLL DOWN FOR ALL REPORTS' not in s,
}
bad = [k for k, v in checks.items() if not v]
if bad:
    raise SystemExit('3.0.181 checks failed: ' + ', '.join(bad))
print('Prepared iCE OnHand 3.0.181: Petrosoft labels, AddOns workflow, regular Add Item, and report priority colors')
