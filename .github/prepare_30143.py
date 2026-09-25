from pathlib import Path

base=Path('.github/prepare_30142.py')
exec(compile(base.read_text(),str(base),'exec'),{'__name__':'__main__','__file__':str(base)})

def rep(path,old,new):
    p=Path(path);s=p.read_text()
    if s.count(old)!=1:raise SystemExit('3.0.143 expected one target: '+old[:75])
    p.write_text(s.replace(old,new,1))

rep('app/build.gradle','versionCode 30142','versionCode 30143')
rep('app/build.gradle',"versionName '3.0.142'","versionName '3.0.143'")
rep('app/src/main/AndroidManifest.xml','iCE Onhand 3.0.142','iCE Onhand 3.0.143')
m='app/src/main/java/com/iceinventory/onhand/MainActivity.java'
rep(m,'Onhand Inventory 3.0.142','Onhand Inventory 3.0.143')
rep(m,'private static final String KEY_DEVICE_ROLE="project_device_role";',
      'private static final String KEY_DEVICE_ROLE="project_device_role";\n    private static final String KEY_ACTIVE_SESSION="active_count_session_id";')
rep(m,'private long sessionId;','private long sessionId;\n    private long activeSessionId;')
rep(m,
'''        if(requestedSession>0)for(InventoryDb.Session s:sessions)if(s.id==requestedSession){sessionId=s.id;sessionName=s.name;break;}
        normalizeNoActiveInventoryName();''',
'''        long savedActive=prefs().getLong(KEY_ACTIVE_SESSION,-1L);
        activeSessionId=sessions.isEmpty()?sessionId:sessions.get(0).id;
        for(InventoryDb.Session s:sessions)if(s.id==savedActive){activeSessionId=s.id;break;}
        if(requestedSession>0){for(InventoryDb.Session s:sessions)if(s.id==requestedSession){sessionId=s.id;sessionName=s.name;activeSessionId=s.id;break;}}
        else {for(InventoryDb.Session s:sessions)if(s.id==activeSessionId){sessionId=s.id;sessionName=s.name;break;}}
        prefs().edit().putLong(KEY_ACTIVE_SESSION,activeSessionId).apply();
        normalizeNoActiveInventoryName();''')
rep(m,'Button inventories=button("📁 Inventories",0);',
      'Button inventories=button(isMasterDevice()?"📁 Files":"📁 Current",0);inventories.setTextSize(13);inventories.setSingleLine(true);inventories.setContentDescription(isMasterDevice()?"Current and previous inventories":"Current inventory only");')
rep(m,'titleSession.setText(sessionName);',
      'titleSession.setText(isPreviousInventory()?"PREVIOUS — READ ONLY\\n"+sessionName:sessionName);')
rep(m,
'''    private void chooseSession() {
        List<InventoryDb.Session> sessions=db.sessions();
        String[] names=new String[sessions.size()];
        for(int i=0;i<sessions.size();i++)names[i]=sessions.get(i).name;
        new AlertDialog.Builder(this).setTitle("Inventories")
                .setItems(names,(d,w)->{
                    InventoryDb.Session s=sessions.get(w);
                    sessionId=s.id;sessionName=s.name;lastBarcode="";
                    refreshList();
                }).setNegativeButton("Cancel",null).show();
    }''',
'''    private boolean isPreviousInventory(){return activeSessionId>0&&sessionId!=activeSessionId;}
    private boolean requireCurrentCount(){
        if(!isPreviousInventory())return true;
        new AlertDialog.Builder(this).setTitle("Previous Inventory — Read Only")
                .setMessage("This inventory is saved for review. Counting here is blocked so a similar barcode cannot be added to an earlier job. Select CURRENT COUNT in Inventories / Previous to resume counting.")
                .setPositiveButton("OK",null).show();
        return false;
    }
    private void chooseSession() {
        List<InventoryDb.Session> sessions=db.sessions();
        if(!isMasterDevice()){
            for(InventoryDb.Session current:sessions)if(current.id==activeSessionId){
                sessionId=current.id;sessionName=current.name;lastBarcode="";refreshList();
                new AlertDialog.Builder(this).setTitle("Current Inventory")
                        .setMessage(current.name+"\\n\\nPrevious inventories are available only on the Master phone.")
                        .setPositiveButton("OK",null).show();
                return;
            }
            toast("No current inventory found");return;
        }
        String[] names=new String[sessions.size()];
        for(int i=0;i<sessions.size();i++)names[i]=(sessions.get(i).id==activeSessionId?"CURRENT COUNT — ":"PREVIOUS • READ ONLY — ")+sessions.get(i).name;
        new AlertDialog.Builder(this).setTitle("Inventories / Previous")
                .setMessage("Previous inventories open for review only. Select CURRENT COUNT before scanning.")
                .setItems(names,(d,w)->{
                    InventoryDb.Session s=sessions.get(w);
                    sessionId=s.id;sessionName=s.name;lastBarcode="";
                    refreshList();
                    if(isPreviousInventory())toast("Previous inventory — read only");
                }).setNegativeButton("Cancel",null).show();
    }''')
rep(m,'sessionId=db.createSession(n);sessionName=n;lastBarcode="";',
      'sessionId=db.createSession(n);activeSessionId=sessionId;prefs().edit().putLong(KEY_ACTIVE_SESSION,activeSessionId).apply();sessionName=n;lastBarcode="";')
rep(m,'private void addItem() {','private void addItem() {\n        if(!requireCurrentCount())return;')
rep(m,'private void scanBarcode() {','private void scanBarcode() {\n        if(!requireCurrentCount())return;')
rep(m,'private void handleScannedBarcode(String rawCode) {','private void handleScannedBarcode(String rawCode) {\n        if(!requireCurrentCount())return;')
rep(m,'private void addLocation() {','private void addLocation() {\n        if(!requireCurrentCount())return;')
rep(m,'private void confirmZeroAllQuantities() {','private void confirmZeroAllQuantities() {\n        if(!requireCurrentCount())return;')
rep(m,'private void showZeroAllFinalConfirmation() {','private void showZeroAllFinalConfirmation() {\n        if(!requireCurrentCount())return;')
rep(m,'public void onAddOne(InventoryDb.Row row) {','public void onAddOne(InventoryDb.Row row) {\n        if(!requireCurrentCount())return;')
rep(m,'public void onSubtractOne(InventoryDb.Row row) {','public void onSubtractOne(InventoryDb.Row row) {\n        if(!requireCurrentCount())return;')
rep(m,'public void onEdit(InventoryDb.Row r) {','public void onEdit(InventoryDb.Row r) {\n        if(!requireCurrentCount())return;')
rep(m,'private void launchCurrentMultiply() {','private void launchCurrentMultiply() {\n        if(!requireCurrentCount())return;')
rep(m,'private void launchQuantity(InventoryDb.Row r) {','private void launchQuantity(InventoryDb.Row r) {\n        if(!requireCurrentCount())return;')
rep(m,'if(amount>0&&pendingQuantityRowId>0) {','if(amount>0&&pendingQuantityRowId>0&&requireCurrentCount()) {')
rep(m,'if(monthlyId>0){sessionId=monthlyId;',
      'if(monthlyId>0){activeSessionId=monthlyId;prefs().edit().putLong(KEY_ACTIVE_SESSION,activeSessionId).apply();sessionId=monthlyId;')
rep(m,'private void readImport(Uri uri) {\n        if(uri==null)return;',
      'private void readImport(Uri uri) {\n        if(uri==null||!requireCurrentCount())return;')
rep(m,'private void performImport(Uri uri,boolean replaceCurrent) {\n        if(uri==null)return;',
      'private void performImport(Uri uri,boolean replaceCurrent) {\n        if(uri==null||!requireCurrentCount())return;')
rep(m,'refreshLocations();refreshList();\n        toast((replaceCurrent?',
      'activeSessionId=sessionId;prefs().edit().putLong(KEY_ACTIVE_SESSION,activeSessionId).apply();\n        refreshLocations();refreshList();\n        toast((replaceCurrent?')

source=Path(m).read_text()
assert 'PREVIOUS — READ ONLY' in source and 'CURRENT COUNT — ' in source
assert 'Previous inventories are available only on the Master phone.' in source
assert source.count('if(!requireCurrentCount())return;')>=11
print('Prepared iCE OnHand 3.0.143: previous inventories are clearly labeled and read only')
