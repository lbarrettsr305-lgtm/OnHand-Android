from pathlib import Path

base = Path('.github/prepare_30156.py')
exec(compile(base.read_text(), str(base), 'exec'), {'__name__': '__main__', '__file__': str(base)})


def rep(path, old, new, label):
    target = Path(path)
    source = target.read_text()
    if source.count(old) != 1:
        raise SystemExit('3.0.157 expected one target for ' + label)
    target.write_text(source.replace(old, new, 1))


rep('app/build.gradle', 'versionCode 30156', 'versionCode 30157', 'Gradle code')
rep('app/build.gradle', "versionName '3.0.156'", "versionName '3.0.157'", 'Gradle name')
rep('app/src/main/AndroidManifest.xml', 'iCE Onhand 3.0.156', 'iCE Onhand 3.0.157', 'manifest version')
rep('app/src/main/java/com/iceinventory/onhand/MainActivity.java',
    'Onhand Inventory 3.0.156', 'Onhand Inventory 3.0.157', 'visible version')

# Install the approved frequent-location master template on existing and new phones.
db = 'app/src/main/java/com/iceinventory/onhand/InventoryDb.java'
rep(db,
    '''        ContentValues loc = new ContentValues();
        loc.put("name", "Main");
        db.insertWithOnConflict("locations", null, loc, SQLiteDatabase.CONFLICT_IGNORE);''',
    '''        db.execSQL("CREATE TABLE IF NOT EXISTS app_meta (key TEXT PRIMARY KEY, value TEXT NOT NULL DEFAULT '')");
        boolean installLocationMaster=true;
        try(Cursor marker=db.rawQuery("SELECT value FROM app_meta WHERE key='location_master' LIMIT 1",null)){
            installLocationMaster=!marker.moveToFirst()||!"30157".equals(marker.getString(0));
        }
        if(installLocationMaster)db.delete("locations",null,null);
        String[] frequentLocations={
            "Main",
            "Aisle1Front-11","Aisle1Left-12","Aisle1Back-13","Aisle1Right-14","Aisle1All-110",
            "Aisle2Front-21","Aisle2Left-22","Aisle2Back-23","Aisle2Right-24","Aisle2All-210",
            "Aisle3Front-31","Aisle3Left-32","Aisle3Back-33","Aisle3Right-34","Aisle3All-310",
            "Aisle4Front-41","Aisle4Left-42","Aisle4Back-43","Aisle4Right-44","Aisle4All-410",
            "Aisle5Front-51","Aisle5Left-52","Aisle5Back-53","Aisle5Right-54","Aisle5All-510",
            "Aisle6Front-61","Aisle6Left-62","Aisle6Back-63","Aisle6Right-64","Aisle6All-610",
            "FloorDisplay-3010","Backroom-441","Backroom-4444",
            "Wall1-451","Wall2-452","Wall3-453","Wall4-454",
            "Deli-463","Deli-4610","GlassDisplay-4710","Display-5050",
            "Display1-5110","Display2-5210","Display3-5310","Display4-5410","Display5-5510",
            "Display6-5610","Display7-5710","Display8-5810","Display9-5910",
            "Location-6010","Location-7070","Checkout-911","Checkout-913",
            "Checkout-9111","Office-9210","Location-9595","CoolerInside","CoolerDoors",
            "Outside","Fountain"
        };
        for(String name:frequentLocations){
            ContentValues loc=new ContentValues();loc.put("name",name);
            db.insertWithOnConflict("locations",null,loc,SQLiteDatabase.CONFLICT_IGNORE);
        }
        if(installLocationMaster){ContentValues marker=new ContentValues();marker.put("key","location_master");marker.put("value","30157");db.insertWithOnConflict("app_meta",null,marker,SQLiteDatabase.CONFLICT_REPLACE);}''',
    'frequent location master template')

main = 'app/src/main/java/com/iceinventory/onhand/MainActivity.java'
rep(main,
    'private boolean monthlyWorkflowMode,liqPosWorkflowMode;',
    'private boolean monthlyWorkflowMode,liqPosWorkflowMode,testScanMode;',
    'test scan mode field')
rep(main,
    '''        monthlyWorkflowMode=getIntent()!=null&&getIntent().getBooleanExtra(MonthlyInventoryActivity.EXTRA_MONTHLY_WORKFLOW,false);liqPosWorkflowMode=getIntent()!=null&&getIntent().getBooleanExtra(LiqPosInventoryActivity.EXTRA_LIQPOS_WORKFLOW,false);''',
    '''        monthlyWorkflowMode=getIntent()!=null&&getIntent().getBooleanExtra(MonthlyInventoryActivity.EXTRA_MONTHLY_WORKFLOW,false);liqPosWorkflowMode=getIntent()!=null&&getIntent().getBooleanExtra(LiqPosInventoryActivity.EXTRA_LIQPOS_WORKFLOW,false);testScanMode=getIntent()!=null&&getIntent().getBooleanExtra(MonthlyInventoryActivity.EXTRA_TEST_SCAN,false);''',
    'read test scan mode')
rep(main,
    '''        refreshLocations();
        refreshList();
        barcode.postDelayed(this::showLocationStepIfNeeded,650);''',
    '''        refreshLocations();
        refreshList();
        if(testScanMode){confirmedLocation="Main";confirmedLocationSession=sessionId;refreshLocations();if(currentLocationBanner!=null)currentLocationBanner.setText("TEST SCAN — BARCODE LOOKUP ONLY");if(countActionBar!=null)countActionBar.setVisibility(View.GONE);}
        barcode.postDelayed(this::showLocationStepIfNeeded,650);''',
    'test scan default location')
rep(main,
    '''    private void showLocationStepIfNeeded(){
        if(!isPreviousInventory()&&!"NO ACTIVE INVENTORY".equals(sessionName))ensureCountingLocation();
    }''',
    '''    private void showLocationStepIfNeeded(){
        if(testScanMode)return;
        if(!isPreviousInventory()&&!"NO ACTIVE INVENTORY".equals(sessionName))ensureCountingLocation();
    }''',
    'bypass location during test scan')
rep(main,
    '''    private void addItem() {
        if(!requireCurrentCount()||!ensureCountingLocation())return;''',
    '''    private void addItem() {
        if(testScanMode){toast("Test scan only — no quantity recorded");barcode.setText("");description.setText("");focusBarcodeWithoutKeyboard();return;}
        if(!requireCurrentCount()||!ensureCountingLocation())return;''',
    'block quantities during test scan')
rep(main,
    '''        if(liqPosWorkflowMode||liqActive) {''',
    '''        if(!testScanMode&&(liqPosWorkflowMode||liqActive)) {''',
    'hide LiqPOS resume during Petrosoft test')
rep(main,
    '''                    Intent next=new Intent(this,MonthlyInventoryActivity.class);
                    startActivity(next);''',
    '''                    getSharedPreferences("liqpos_workflow_state",MODE_PRIVATE).edit().putBoolean("active",false).apply();
                    Intent next=new Intent(this,MonthlyInventoryActivity.class);
                    next.putExtra(MonthlyInventoryActivity.EXTRA_START_NEW,true);
                    startActivity(next);''',
    'start clean monthly project')
rep(main,
    '''                    if(which==0)ensureMasterPin(()->startActivityForResult(new Intent(this,MonthlyInventoryActivity.class),REQ_MONTHLY_INVENTORY));''',
    '''                    if(which==0)ensureMasterPin(this::confirmStartPetrosoftWorkflow);''',
    'guard Petrosoft start')
rep(main,
    '''    private void startImportFormatFlow() {''',
    '''    private void confirmStartPetrosoftWorkflow(){
        android.content.SharedPreferences mw=getSharedPreferences("monthly_workflow_state",MODE_PRIVATE);
        android.content.SharedPreferences lw=getSharedPreferences("liqpos_workflow_state",MODE_PRIVATE);
        boolean monthly=mw.getBoolean("active",false),liq=lw.getBoolean("active",false);
        if(!monthly&&!liq){Intent i=new Intent(this,MonthlyInventoryActivity.class);i.putExtra(MonthlyInventoryActivity.EXTRA_START_NEW,true);startActivityForResult(i,REQ_MONTHLY_INVENTORY);return;}
        String current=monthly?"Petrosoft monthly inventory":"LiqPOS inventory";
        new AlertDialog.Builder(this).setTitle("Close Current Inventory First?")
            .setMessage("A "+current+" is still open. Close its active workflow and start a new Petrosoft inventory? Existing count records and exported files will not be deleted.")
            .setNegativeButton("Cancel",null)
            .setPositiveButton("Close & Start New",(d,w)->{
                mw.edit().putBoolean("active",false).apply();lw.edit().putBoolean("active",false).apply();
                Intent i=new Intent(this,MonthlyInventoryActivity.class);i.putExtra(MonthlyInventoryActivity.EXTRA_START_NEW,true);startActivityForResult(i,REQ_MONTHLY_INVENTORY);
            }).show();
    }

    private void startImportFormatFlow() {''',
    'current inventory safeguard')

monthly = 'app/src/main/java/com/iceinventory/onhand/MonthlyInventoryActivity.java'
rep(monthly,
    '''    public static final String EXTRA_SESSION_ID="monthly_session_id",EXTRA_SESSION_NAME="monthly_session_name",EXTRA_MONTHLY_WORKFLOW="monthly_workflow";''',
    '''    public static final String EXTRA_SESSION_ID="monthly_session_id",EXTRA_SESSION_NAME="monthly_session_name",EXTRA_MONTHLY_WORKFLOW="monthly_workflow",EXTRA_TEST_SCAN="monthly_test_scan",EXTRA_START_NEW="monthly_start_new";''',
    'monthly intent extras')
rep(monthly,
    '''        setContentView(scroll);pendingSourceUri=incomingSource(getIntent());if(pendingSourceUri!=null){sourceName=displayName(pendingSourceUri);importSummary.setText("ATTACHMENT READY: "+sourceName+"\\nEnter the store name, then tap Import.");}setEnabledState();if(pendingSourceUri==null)restoreMonthlyWorkflow();''',
    '''        setContentView(scroll);pendingSourceUri=incomingSource(getIntent());if(pendingSourceUri!=null){sourceName=displayName(pendingSourceUri);importSummary.setText("ATTACHMENT READY: "+sourceName+"\\nEnter the store name, then tap Import.");}setEnabledState();boolean startNew=getIntent()!=null&&getIntent().getBooleanExtra(EXTRA_START_NEW,false);if(startNew){workflowPrefs().edit().clear().apply();new File(getFilesDir(),"monthly_workflow_source.xlsx").delete();getSharedPreferences("liqpos_workflow_state",MODE_PRIVATE).edit().putBoolean("active",false).apply();}else if(pendingSourceUri==null)restoreMonthlyWorkflow();''',
    'fresh Petrosoft workflow state')
rep(monthly,
    '''    private void confirmTestScan(){new android.app.AlertDialog.Builder(this).setTitle("Test Scan").setMessage("Open a temporary zero-quantity inventory for a test scan? Press Back after testing to return and share the count file.").setPositiveButton("Start Test Scan",(d,w)->loadOnDevice()).setNegativeButton("Cancel",null).show();}''',
    '''    private void confirmTestScan(){new android.app.AlertDialog.Builder(this).setTitle("Test Barcode Only").setMessage("Scan a barcode to confirm it is in the Petrosoft file. No counting location is required and no quantity will be recorded. Press Back when finished.").setPositiveButton("Start Test Scan",(d,w)->loadOnDevice()).setNegativeButton("Cancel",null).show();}''',
    'clear test scan instructions')
rep(monthly,
    '''test.putExtra(EXTRA_MONTHLY_WORKFLOW,true);startActivity(test);''',
    '''test.putExtra(EXTRA_MONTHLY_WORKFLOW,true);test.putExtra(EXTRA_TEST_SCAN,!countLaunchPending);startActivity(test);''',
    'launch test-only scan mode')

# The ready message and launch flag must use the value before countLaunchPending is reset.
rep(monthly,
    '''String ready=countLaunchPending?"Inventory ready with "+rows.size()+" barcodes. Begin counting on this machine.":"Test inventory ready with "+rows.size()+" barcodes. Test a scan, then press Back to share.";countLaunchPending=false;Toast.makeText(this,ready,Toast.LENGTH_LONG).show();showProgress();setEnabledState();Intent test=new Intent(this,MainActivity.class);''',
    '''boolean startingCount=countLaunchPending;String ready=startingCount?"Inventory ready with "+rows.size()+" barcodes. Begin counting on this machine.":"Test inventory ready with "+rows.size()+" barcodes. Scan only; quantities are not recorded.";countLaunchPending=false;Toast.makeText(this,ready,Toast.LENGTH_LONG).show();showProgress();setEnabledState();Intent test=new Intent(this,MainActivity.class);''',
    'preserve test versus count launch state')
rep(monthly,
    '''test.putExtra(EXTRA_MONTHLY_WORKFLOW,true);test.putExtra(EXTRA_TEST_SCAN,!countLaunchPending);startActivity(test);''',
    '''test.putExtra(EXTRA_MONTHLY_WORKFLOW,true);test.putExtra(EXTRA_TEST_SCAN,!startingCount);startActivity(test);''',
    'correct test flag')
rep(monthly,
    '''    private void launchCountAfterShare(){showNextStep();if(deviceLoaded&&deviceSessionId>0){String loadedName=base()+" "+day();Intent count=new Intent(this,MainActivity.class);count.putExtra(EXTRA_SESSION_ID,deviceSessionId);count.putExtra(EXTRA_SESSION_NAME,loadedName);count.putExtra(EXTRA_MONTHLY_WORKFLOW,true);Toast.makeText(this,"Shared file complete. Begin counting on this machine.",Toast.LENGTH_LONG).show();startActivity(count);}else{countLaunchPending=true;loadOnDevice();}}''',
    '''    private void launchCountAfterShare(){
        showNextStep();
        new android.app.AlertDialog.Builder(this).setTitle("File Shared")
            .setMessage("Start the live inventory on this Master phone now? The first step will be choosing the actual counting location.")
            .setNegativeButton("Not Yet",null)
            .setPositiveButton("START INVENTORY ON MASTER",(d,w)->startInventoryOnMaster()).show();
    }

    private void startInventoryOnMaster(){
        if(deviceLoaded&&deviceSessionId>0){
            String loadedName=base()+" "+day();Intent count=new Intent(this,MainActivity.class);
            count.putExtra(EXTRA_SESSION_ID,deviceSessionId);count.putExtra(EXTRA_SESSION_NAME,loadedName);count.putExtra(EXTRA_MONTHLY_WORKFLOW,true);
            Toast.makeText(this,"Live inventory started. Choose the first counting location.",Toast.LENGTH_LONG).show();startActivity(count);
        }else{countLaunchPending=true;loadOnDevice();}
    }''',
    'explicit Master count start after sharing')

for path, required in [
    (db, 'Aisle6All-610'),
    (main, 'Close Current Inventory First?'),
    (main, 'if(testScanMode)return;'),
    (monthly, 'EXTRA_TEST_SCAN'),
    (monthly, 'Test Barcode Only')]:
    if required not in Path(path).read_text():
        raise SystemExit('3.0.157 verification missing: ' + required)

print('Prepared iCE OnHand 3.0.157: frequent locations, test-only scan, and clean project transitions')
