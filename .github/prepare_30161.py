from pathlib import Path

base = Path('.github/prepare_30160.py')
exec(compile(base.read_text(), str(base), 'exec'), {'__name__': '__main__', '__file__': str(base)})


def rep(path, old, new, label):
    target = Path(path)
    source = target.read_text()
    if source.count(old) != 1:
        raise SystemExit('3.0.161 expected one target for ' + label)
    target.write_text(source.replace(old, new, 1))


rep('app/build.gradle', 'versionCode 30160', 'versionCode 30161', 'Gradle code')
rep('app/build.gradle', "versionName '3.0.160'", "versionName '3.0.161'", 'Gradle name')
rep('app/src/main/AndroidManifest.xml', 'iCE Onhand 3.0.160', 'iCE Onhand 3.0.161', 'manifest version')
rep('app/src/main/java/com/iceinventory/onhand/MainActivity.java',
    'Onhand Inventory 3.0.160', 'Onhand Inventory 3.0.161', 'visible version')

main_path = Path('app/src/main/java/com/iceinventory/onhand/MainActivity.java')
main = main_path.read_text()
old_match = '''        highlightAndRevealBarcode(actual);
        if(flexible)toast("Matched saved barcode: "+actual);
        focusQuantity();'''
new_match = '''        highlightAndRevealBarcode(actual);
        if(testScanMode){
            qty.setText("");hideKeyboard();
            getSharedPreferences("monthly_workflow_state",MODE_PRIVATE).edit()
                .putBoolean("test_scan_passed",true).putString("test_scan_barcode",actual).apply();
            Toast.makeText(this,"TEST SCAN PASSED — barcode verified in the database. Returning to Step 4: Share Count File to Users.",Toast.LENGTH_LONG).show();
            barcode.postDelayed(this::finish,900);return;
        }
        if(flexible)toast("Matched saved barcode: "+actual);
        focusQuantity();'''
if old_match not in main:
    raise SystemExit('3.0.161 saved barcode match target missing')
main = main.replace(old_match, new_match, 1)

old_back = '    @Override public void onBackPressed(){leaveCountingSafely(this::finish);}'
new_back = '    @Override public void onBackPressed(){if(testScanMode){barcode.setText("");qty.setText("");finish();}else leaveCountingSafely(this::finish);}'
if old_back not in main:
    raise SystemExit('3.0.161 Android Back test-mode target missing')
main = main.replace(old_back, new_back, 1)

old_return = 'monthly.setOnClickListener(v->{if(monthlyWorkflowMode)leaveCountingSafely(this::finish);else{hideKeyboard();'
new_return = 'monthly.setOnClickListener(v->{if(monthlyWorkflowMode){if(testScanMode){barcode.setText("");qty.setText("");finish();}else leaveCountingSafely(this::finish);}else{hideKeyboard();'
if old_return not in main:
    raise SystemExit('3.0.161 Return to Monthly test-mode target missing')
main = main.replace(old_return, new_return, 1)
main_path.write_text(main)

monthly_path = Path('app/src/main/java/com/iceinventory/onhand/MonthlyInventoryActivity.java')
monthly = monthly_path.read_text()
monthly = monthly.replace('private boolean sourceReady,masterCreated,onHandCreated,deviceLoaded,countsReady,validated,countLaunchPending,restoringMonthly,combinedExported,clientExported,auditExported;',
                          'private boolean sourceReady,masterCreated,onHandCreated,deviceLoaded,testScanPassed,countsReady,validated,countLaunchPending,restoringMonthly,combinedExported,clientExported,auditExported;', 1)
monthly = monthly.replace('deviceSessionId=w.getLong("device_session_id",-1);deviceLoaded=deviceSessionId>0;combinedExported=',
                          'deviceSessionId=w.getLong("device_session_id",-1);deviceLoaded=deviceSessionId>0;testScanPassed=w.getBoolean("test_scan_passed",false);combinedExported=', 1)
monthly = monthly.replace('deviceLoaded=true;deviceSessionId=id;workflowPrefs().edit().putLong("device_session_id",id).apply();',
                          'deviceLoaded=true;testScanPassed=false;deviceSessionId=id;workflowPrefs().edit().putLong("device_session_id",id).putBoolean("test_scan_passed",false).remove("test_scan_barcode").apply();', 1)

old_progress = '''b.append(deviceLoaded?"\\n✓ TEST SCAN READY — PRESS BACK TO SHARE":"\\n○ TEST SCAN ON THIS DEVICE (OPTIONAL)");b.append(onHandCreated?"\\n○ SHARE VERIFIED COUNT FILE WITH USERS":"");'''
new_progress = '''b.append(testScanPassed?"\\n✓ TEST SCAN PASSED — BARCODE VERIFIED":(deviceLoaded?"\\n○ TEST SCAN READY — SCAN ONE BARCODE":"\\n○ TEST SCAN ON THIS DEVICE (OPTIONAL)"));b.append(onHandCreated?"\\n○ NEXT STEP 4: SHARE VERIFIED COUNT FILE WITH USERS":"");'''
if old_progress not in monthly:
    raise SystemExit('3.0.161 progress target missing')
monthly = monthly.replace(old_progress, new_progress, 1)

old_confirm = 'setMessage("Scan a barcode to confirm it is in the Petrosoft file. No counting location is required and no quantity will be recorded. Press Back when finished.")'
new_confirm = 'setMessage("Scan one barcode to confirm it is in the Petrosoft file. No quantity will be recorded. When the barcode is verified, OnHand will automatically return and highlight Step 4: Share Count File to Users.")'
if old_confirm not in monthly:
    raise SystemExit('3.0.161 test instructions target missing')
monthly = monthly.replace(old_confirm, new_confirm, 1)

anchor = '    private void pickSource(){'
resume = '''    @Override protected void onResume(){
        super.onResume();
        boolean passed=workflowPrefs().getBoolean("test_scan_passed",false);
        if(passed&&!testScanPassed){testScanPassed=true;showProgress();setEnabledState();}
        if(testScanPassed&&shareOnHand!=null){
            shareOnHand.setBackgroundTintList(android.content.res.ColorStateList.valueOf(Color.rgb(255,215,0)));
            shareOnHand.setTextColor(Color.BLACK);shareOnHand.setText("4. NEXT: SHARE COUNT FILE TO USERS");
            shareOnHand.postDelayed(()->{shareOnHand.requestFocus();Toast.makeText(this,"Test passed. Next, press Step 4 to share the count file.",Toast.LENGTH_LONG).show();},250);
        }
    }

'''
if anchor not in monthly:
    raise SystemExit('3.0.161 onResume anchor missing')
monthly = monthly.replace(anchor, resume + anchor, 1)
monthly_path.write_text(monthly)

checks = {
    'version': "versionName '3.0.161'" in Path('app/build.gradle').read_text(),
    'auto return': 'barcode.postDelayed(this::finish,900)' in main,
    'no test quantity': 'if(testScanMode)' in main and 'qty.setText("");hideKeyboard();' in main,
    'test persisted': 'putBoolean("test_scan_passed",true)' in main,
    'test return bypasses count safeguard': 'if(testScanMode){barcode.setText("");qty.setText("");finish();}' in main,
    'step 4 highlighted': '4. NEXT: SHARE COUNT FILE TO USERS' in monthly,
    'instructions': 'automatically return and highlight Step 4' in monthly,
}
missing = [name for name, ok in checks.items() if not ok]
if missing:
    raise SystemExit('3.0.161 verification failed: ' + ', '.join(missing))

print('Prepared iCE OnHand 3.0.161: one-scan verification returns automatically to highlighted Share step')
