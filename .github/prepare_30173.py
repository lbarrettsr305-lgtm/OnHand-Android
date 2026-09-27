from pathlib import Path

base = Path('.github/prepare_30172.py')
exec(compile(base.read_text(), str(base), 'exec'), {'__name__': '__main__', '__file__': str(base)})


def rep(path, old, new, label):
    p = Path(path)
    s = p.read_text()
    if s.count(old) != 1:
        raise SystemExit('3.0.173 target ' + label + ' count ' + str(s.count(old)))
    p.write_text(s.replace(old, new, 1))


rep('app/build.gradle', 'versionCode 30172', 'versionCode 30173', 'code')
rep('app/build.gradle', "versionName '3.0.172'", "versionName '3.0.173'", 'name')
rep('app/src/main/AndroidManifest.xml', 'iCE Onhand 3.0.172', 'iCE Onhand 3.0.173', 'manifest')

main = 'app/src/main/java/com/iceinventory/onhand/MainActivity.java'
rep(main, 'Onhand Inventory 3.0.172', 'Onhand Inventory 3.0.173', 'header')

# Counter phones get a deliberately small home screen: current inventory, count,
# import and send. Administrative menus can be exposed temporarily with the PIN
# carried as a verifier in the Master-created count file.
rep(main,
    'private boolean monthlyWorkflowMode,liqPosWorkflowMode,testScanMode;',
    'private boolean monthlyWorkflowMode,liqPosWorkflowMode,testScanMode,adminUnlocked;',
    'temporary admin flag')
rep(main,
    'private static final String KEY_MASTER_PIN_HASH="master_pin_hash";',
    'private static final String KEY_MASTER_PIN_HASH="master_pin_hash";\n    private static final String KEY_AUTHORIZED_MASTER_PIN_HASH="authorized_master_pin_hash";',
    'authorized verifier key')
rep(main,
    'Button fresh=button("＋ New",0);fresh.setOnClickListener(v->newSession());',
    'Button fresh=button("＋ New",0);fresh.setOnClickListener(v->newSession());fresh.setVisibility(hasAdminAccess()?View.VISIBLE:View.GONE);',
    'hide new inventory')
rep(main,
    'if(isMasterDevice()){\n            Button shareUsers=button("📤 Share",2);',
    'if(hasAdminAccess()){\n            Button shareUsers=button("📤 Share",2);',
    'admin header share')
rep(main,
    'if(monthlyWorkflowMode||resumableMonthly||archivedMonthly) {',
    'if(hasAdminAccess()&&(monthlyWorkflowMode||resumableMonthly||archivedMonthly)) {',
    'hide monthly workflow')
rep(main,
    'Button imp=button("↓ START / IMPORT",1);imp.setTypeface(Typeface.DEFAULT,Typeface.BOLD);imp.setOnClickListener(v->showImportMenu());\n        Button exp=button("⬆ Export",2);exp.setTypeface(Typeface.DEFAULT,Typeface.BOLD);exp.setOnClickListener(v->showExportScopeDialog());',
    'Button imp=button("↓ START / IMPORT",1);imp.setTypeface(Typeface.DEFAULT,Typeface.BOLD);imp.setOnClickListener(v->showImportMenu());\n        Button exp=button(hasAdminAccess()?"⬆ Export":"⬆ SEND COMPLETED COUNT",2);exp.setTextSize(hasAdminAccess()?14:12);exp.setSingleLine(false);exp.setTypeface(Typeface.DEFAULT,Typeface.BOLD);exp.setOnClickListener(v->{if(hasAdminAccess())showExportScopeDialog();else beginCompleteInventoryExport();});',
    'counter send button')
rep(main,
    'private void showImportMenu() {\n        String[] choices={"Petrosoft Monthly Inventory","LiqPOS Inventory","Shared User / Standard TXT File"};',
    'private void showImportMenu() {\n        if(!hasAdminAccess()){startImportFormatFlow();return;}\n        String[] choices={"Petrosoft Monthly Inventory","LiqPOS Inventory","Shared User / Standard TXT File"};',
    'counter import direct')
rep(main,
    'private boolean isMasterDevice(){return ROLE_MASTER.equals(deviceRole());}',
    'private boolean isMasterDevice(){return ROLE_MASTER.equals(deviceRole());}\n    private boolean hasAdminAccess(){return isMasterDevice()||adminUnlocked;}',
    'admin access helper')
rep(main,
    'if(isMasterDevice()){\n            Button shareShortcut=button("📤 SHARE WITH COUNT USERS",2);',
    'if(hasAdminAccess()){\n            Button shareShortcut=button("📤 SHARE WITH COUNT USERS",2);',
    'options admin share')

# Give a Counter User one clear, temporary unlock action. The role is unchanged.
anchor = '''        TextView scanning=text("Scanning",16,gold(),true);scanning.setPadding(dp(6),dp(6),0,dp(2));box.addView(scanning);'''
unlock = '''        if(!isMasterDevice()&&!adminUnlocked){
            Button unlock=button("🔒 UNLOCK MASTER TOOLS",2);unlock.setTypeface(Typeface.DEFAULT,Typeface.BOLD);
            unlock.setOnClickListener(v->unlockMasterTools());box.addView(unlock,new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT,dp(58)));
        }
''' + anchor
rep(main, anchor, unlock, 'counter unlock button')

insert_before = '    private void changeMasterPin(){'
unlock_method = '''    private void unlockMasterTools(){
        String expected=prefs().getString(KEY_AUTHORIZED_MASTER_PIN_HASH,"");
        if(expected.isEmpty()){new AlertDialog.Builder(this).setTitle("Master PIN Not Available").setMessage("Import a count file prepared by the Master phone first. That file authorizes this phone to verify the Master PIN without changing its Count User role.").setPositiveButton("OK",null).show();return;}
        EditText pin=masterPinEntry("4-digit Master PIN");AlertDialog dialog=new AlertDialog.Builder(this).setTitle("Temporarily Unlock Master Tools").setMessage("Tools stay unlocked only while this app screen remains open. This phone remains a Count User.").setView(pin).setPositiveButton("UNLOCK",null).setNegativeButton("Cancel",null).create();
        dialog.setOnShowListener(x->dialog.getButton(AlertDialog.BUTTON_POSITIVE).setOnClickListener(v->{if(!expected.equals(hashMasterPin(pin.getText().toString()))){toast("Incorrect Master PIN");pin.selectAll();return;}adminUnlocked=true;dialog.dismiss();toast("Master tools unlocked temporarily");buildUi();refreshLocations();refreshList();}));dialog.show();
    }

'''+insert_before
rep(main, insert_before, unlock_method, 'temporary unlock method')

old_role = '''    private void applySharedProjectRole(Uri uri){
        // A shared count file is untrusted data. It cannot set roles or supply a PIN.
        // Keep the existing Master device's authority when it imports count files.
        if(!isMasterDevice())prefs().edit().putString(KEY_DEVICE_ROLE,ROLE_COUNT_USER)
                .remove(KEY_MASTER_PIN_HASH).remove(KEY_MASTER_USER).apply();
        refreshOperatorStatus();
    }'''
new_role = '''    private void applySharedProjectRole(Uri uri){
        String verifier="";
        try(InputStream in=getContentResolver().openInputStream(uri);BufferedReader br=new BufferedReader(new InputStreamReader(in,StandardCharsets.UTF_8))){String first=br.readLine();if(first!=null&&first.startsWith("#ICE_ONHAND_PROJECT\\t")){for(String part:first.split("\\t")){if(part.startsWith("MASTER_PIN_HASH="))verifier=part.substring("MASTER_PIN_HASH=".length()).trim();}}}catch(Exception ignored){}
        if(!isMasterDevice()){android.content.SharedPreferences.Editor e=prefs().edit().putString(KEY_DEVICE_ROLE,ROLE_COUNT_USER).remove(KEY_MASTER_PIN_HASH).remove(KEY_MASTER_USER);if(verifier.matches("[0-9a-fA-F]{64}"))e.putString(KEY_AUTHORIZED_MASTER_PIN_HASH,verifier);e.apply();}
        refreshOperatorStatus();
    }'''
rep(main, old_role, new_role, 'import master verifier')

rep(main,
    'out.write("#ICE_ONHAND_PROJECT\\tROLE=COUNT_USER\\r\\nQuantity\\tBarcode\\tDescription\\tPrice\\r\\n");',
    'out.write("#ICE_ONHAND_PROJECT\\tROLE=COUNT_USER\\tMASTER_PIN_HASH="+prefs().getString(KEY_MASTER_PIN_HASH,"")+"\\r\\nQuantity\\tBarcode\\tDescription\\tPrice\\r\\n");',
    'shared file verifier')

monthly = 'app/src/main/java/com/iceinventory/onhand/MonthlyInventoryActivity.java'
rep(monthly,
    'private String projectMetadata(){return "#ICE_ONHAND_PROJECT\\tROLE=COUNT_USER\\r\\n";}',
    'private String projectMetadata(){String h=getSharedPreferences("onhand_settings",MODE_PRIVATE).getString("master_pin_hash","");return "#ICE_ONHAND_PROJECT\\tROLE=COUNT_USER\\tMASTER_PIN_HASH="+h+"\\r\\n";}',
    'monthly file verifier')

# Exception controls do not exist visually until after user files were selected,
# and remain absent entirely in the normal no-unmatched case.
rep(monthly,
    'approveExceptions.setOnClickListener(v->approveMissingItems());root.addView(approveExceptions,params(76));',
    'approveExceptions.setOnClickListener(v->approveMissingItems());approveExceptions.setVisibility(View.GONE);root.addView(approveExceptions,params(76));',
    'hide review initially')
rep(monthly,
    'saveUnmatched.setOnClickListener(v->create(SAVE_UNMATCHED,"application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",base()+" MISSING NEW ITEMS-"+day()+".xlsx"));root.addView(saveUnmatched,params(78));',
    'saveUnmatched.setOnClickListener(v->create(SAVE_UNMATCHED,"application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",base()+" MISSING NEW ITEMS-"+day()+".xlsx"));saveUnmatched.setVisibility(View.GONE);root.addView(saveUnmatched,params(78));',
    'hide missing export initially')

old_state = '''private void setEnabledState(){if(chooseSource!=null)chooseSource.setEnabled(!storeName().isEmpty()&&!sourceReady);saveMaster.setEnabled(sourceReady&&!masterCreated);saveOnHand.setEnabled(sourceReady&&!onHandCreated);loadDevice.setEnabled(onHandCreated&&!deviceLoaded);shareOnHand.setEnabled(onHandCreated&&onHandUri!=null);chooseCounts.setEnabled(sourceReady);saveCombined.setEnabled(countsReady&&validated);saveClient.setEnabled(countsReady&&validated);if(saveCombinedXlsx!=null)saveCombinedXlsx.setEnabled(countsReady&&validated);saveCategory.setEnabled(countsReady&&validated);saveCigarettes.setEnabled(countsReady&&validated);saveAudit.setEnabled(countsReady);if(saveUnmatched!=null)saveUnmatched.setEnabled(countsReady&&!unmatched.isEmpty());if(approveExceptions!=null)approveExceptions.setEnabled(countsReady&&!unmatched.isEmpty()&&!exceptionsApproved);if(adjustCount!=null)adjustCount.setEnabled(deviceSessionId>0);if(closeProject!=null)closeProject.setEnabled(combinedExported&&clientExported&&auditExported&&(unmatched.isEmpty()||missingItemsExported));}'''
new_state = '''private void setEnabledState(){if(chooseSource!=null)chooseSource.setEnabled(!storeName().isEmpty()&&!sourceReady);saveMaster.setEnabled(sourceReady&&!masterCreated);saveOnHand.setEnabled(sourceReady&&!onHandCreated);loadDevice.setEnabled(onHandCreated&&!deviceLoaded);shareOnHand.setEnabled(onHandCreated&&onHandUri!=null);chooseCounts.setEnabled(sourceReady);boolean exceptions=countsReady&&!unmatched.isEmpty();if(approveExceptions!=null){approveExceptions.setVisibility(exceptions?View.VISIBLE:View.GONE);approveExceptions.setEnabled(exceptions&&!exceptionsApproved);approveExceptions.setText("6. REVIEW MISSING ITEMS & INSTRUCTIONS");}if(saveUnmatched!=null){saveUnmatched.setVisibility(exceptions?View.VISIBLE:View.GONE);saveUnmatched.setEnabled(exceptions);saveUnmatched.setText("7. EXPORT MISSING / NEW ITEMS — EXCEL");}saveClient.setText(exceptions?"8. EXPORT CUSTOMER IMPORT — EXCEL":"6. EXPORT CUSTOMER IMPORT — EXCEL");if(saveCombinedXlsx!=null)saveCombinedXlsx.setText(exceptions?"9. COMPLETE COMBINED INVENTORY — EXCEL":"7. COMPLETE COMBINED INVENTORY — EXCEL");saveCombined.setText(exceptions?"10. EXPORT VERIFIED COMBINED — TXT":"8. EXPORT VERIFIED COMBINED — TXT");saveAudit.setText(exceptions?"11. EXPORT MONTHLY VERIFICATION — TXT":"9. EXPORT MONTHLY VERIFICATION — TXT");closeProject.setText(exceptions?"12. CLOSE MONTHLY PROJECT":"10. CLOSE MONTHLY PROJECT");saveCombined.setEnabled(countsReady&&validated);saveClient.setEnabled(countsReady&&validated);if(saveCombinedXlsx!=null)saveCombinedXlsx.setEnabled(countsReady&&validated);saveCategory.setEnabled(countsReady&&validated);saveCigarettes.setEnabled(countsReady&&validated);saveAudit.setEnabled(countsReady);if(adjustCount!=null)adjustCount.setEnabled(deviceSessionId>0);if(closeProject!=null)closeProject.setEnabled(combinedExported&&clientExported&&auditExported&&(unmatched.isEmpty()||missingItemsExported));}'''
rep(monthly, old_state, new_state, 'conditional exception workflow')
rep(monthly,
    'NEXT: Press 7. EXPORT CUSTOMER IMPORT — EXCEL',
    'NEXT: Press 6. EXPORT CUSTOMER IMPORT — EXCEL',
    'normal next instruction')

s = Path(main).read_text(); m = Path(monthly).read_text()
checks = {
    'version': "versionName '3.0.173'" in Path('app/build.gradle').read_text(),
    'counter direct import': 'if(!hasAdminAccess()){startImportFormatFlow();return;}' in s,
    'counter send': 'SEND COMPLETED COUNT' in s,
    'temporary unlock': 'unlockMasterTools()' in s and 'authorized_master_pin_hash' in s,
    'exceptions hidden': 'approveExceptions.setVisibility(View.GONE)' in m and 'saveUnmatched.setVisibility(View.GONE)' in m,
    'conditional visibility': 'boolean exceptions=countsReady&&!unmatched.isEmpty()' in m,
}
bad = [k for k,v in checks.items() if not v]
if bad: raise SystemExit('3.0.173 checks failed: '+', '.join(bad))
print('Prepared iCE OnHand 3.0.173: simplified Counter mode and conditional missing-item workflow')
