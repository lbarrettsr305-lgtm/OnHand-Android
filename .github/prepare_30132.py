from pathlib import Path

base=Path('.github/prepare_30131.py')
exec(compile(base.read_text(),str(base),'exec'),{'__name__':'__main__','__file__':str(base)})

def replace(path, old, new, label):
    p=Path(path); s=p.read_text()
    if old not in s: raise SystemExit('3.0.132 target missing: '+label)
    p.write_text(s.replace(old,new,1))

replace('app/build.gradle', 'versionCode 30131', 'versionCode 30132', 'Gradle code')
replace('app/build.gradle', "versionName '3.0.131'", "versionName '3.0.132'", 'Gradle name')
replace('app/src/main/AndroidManifest.xml', 'iCE Onhand 3.0.131', 'iCE Onhand 3.0.132', 'manifest')

p=Path('app/src/main/java/com/iceinventory/onhand/MainActivity.java'); s=p.read_text()
s=s.replace('Onhand Inventory 3.0.131','Onhand Inventory 3.0.132',1)
s=s.replace('private static final String KEY_MASTER_USER="master_report_user";', '''private static final String KEY_MASTER_USER="master_report_user";
    private static final String KEY_DEVICE_ROLE="project_device_role";
    private static final String KEY_MASTER_PIN_HASH="master_pin_hash";
    private static final String ROLE_MASTER="MASTER";
    private static final String ROLE_COUNT_USER="COUNT_USER";''',1)

s=s.replace('''        Button masterUserButton=button(currentMaster.isEmpty()?"SET CURRENT USER AS MASTER":"CHANGE MASTER REPORT USER",2);
        masterUserButton.setTypeface(Typeface.DEFAULT,Typeface.BOLD);masterUserButton.setTextSize(16);
        masterUserButton.setOnClickListener(v->setCurrentUserAsMaster());
        box.addView(masterUserButton,new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT,dp(58)));''','''        boolean masterDevice=isMasterDevice();
        String roleText=masterDevice?"MASTER DEVICE":"COUNT USER — MASTER REPORTS LOCKED";
        TextView roleStatus=text(roleText,16,masterDevice?Color.rgb(120,255,140):Color.rgb(255,170,120),true);
        roleStatus.setPadding(dp(8),dp(4),dp(8),dp(7));box.addView(roleStatus);
        Button masterUserButton=button(masterDevice?"CHANGE MASTER PIN":"TRANSFER / UNLOCK MASTER",2);
        masterUserButton.setTypeface(Typeface.DEFAULT,Typeface.BOLD);masterUserButton.setTextSize(16);
        masterUserButton.setOnClickListener(v->{if(masterDevice)changeMasterPin();else unlockMasterWithPin();});
        box.addView(masterUserButton,new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT,dp(58)));''',1)

s=s.replace('''                    if(which==0)startActivityForResult(new Intent(this,MonthlyInventoryActivity.class),REQ_MONTHLY_INVENTORY);
                    else if(which==1)startActivity(new Intent(this,LiqPosInventoryActivity.class));
                    else startImportFormatFlow();''','''                    if(which==0)ensureMasterPin(()->startActivityForResult(new Intent(this,MonthlyInventoryActivity.class),REQ_MONTHLY_INVENTORY));
                    else if(which==1)ensureMasterPin(()->startActivity(new Intent(this,LiqPosInventoryActivity.class)));
                    else startImportFormatFlow();''',1)

old='''    private void setCurrentUserAsMaster() {
        String current=savedUserName();
        if(current.isEmpty()){toast("Set User Name first");promptUserName(false);return;}
        String existing=savedMasterUserName();
        String title=existing.isEmpty()?"Set Master Report User":"Change Master Report User";
        String message=(existing.isEmpty()?"Designate ":"Replace "+existing+" with ")+current+" as the Master Report User?\\n\\nThe Master Report User is the authorized operator for combined batch verification and official reconciliation reports on this device.";
        new AlertDialog.Builder(this).setTitle(title).setMessage(message)
                .setPositiveButton("Set Master",(d,w)->{prefs().edit().putString(KEY_MASTER_USER,current).apply();toast("Master Report User: "+current);})
                .setNegativeButton("Cancel",null).show();
    }
'''
new='''    private String deviceRole(){
        String role=prefs().getString(KEY_DEVICE_ROLE,"");
        if(role.isEmpty()&&!savedMasterUserName().isEmpty())return ROLE_MASTER;
        return role;
    }

    private boolean isMasterDevice(){return ROLE_MASTER.equals(deviceRole());}
    private boolean validMasterPin(String pin){return pin!=null&&pin.matches("\\\\d{4}");}
    private String hashMasterPin(String pin){
        try{java.security.MessageDigest md=java.security.MessageDigest.getInstance("SHA-256");byte[] raw=md.digest(("ICE-ONHAND-MASTER:"+pin).getBytes(StandardCharsets.UTF_8));StringBuilder b=new StringBuilder();for(byte x:raw)b.append(String.format(Locale.US,"%02x",x&255));return b.toString();}
        catch(Exception e){throw new IllegalStateException(e);}
    }
    private EditText masterPinEntry(String hint){EditText e=new EditText(this);e.setSingleLine(true);e.setHint(hint);e.setInputType(InputType.TYPE_CLASS_NUMBER|InputType.TYPE_NUMBER_VARIATION_PASSWORD);e.setFilters(new android.text.InputFilter[]{new android.text.InputFilter.LengthFilter(4)});return e;}

    private void ensureMasterPin(Runnable next){
        if(isMasterDevice()&&!prefs().getString(KEY_MASTER_PIN_HASH,"").isEmpty()){next.run();return;}
        EditText pin=masterPinEntry("New 4-digit Master PIN");
        AlertDialog dialog=new AlertDialog.Builder(this).setTitle("Create Master PIN").setMessage("This phone will become the Master device. The PIN is required to transfer Master access.").setView(pin).setPositiveButton("Continue",null).setNegativeButton("Cancel",null).create();
        dialog.setOnShowListener(x->dialog.getButton(AlertDialog.BUTTON_POSITIVE).setOnClickListener(v->{String value=pin.getText().toString();if(!validMasterPin(value)){toast("Master PIN must be exactly 4 digits");return;}String current=savedUserName();prefs().edit().putString(KEY_DEVICE_ROLE,ROLE_MASTER).putString(KEY_MASTER_PIN_HASH,hashMasterPin(value)).putString(KEY_MASTER_USER,current).apply();dialog.dismiss();next.run();}));dialog.show();
    }

    private void unlockMasterWithPin(){
        String expected=prefs().getString(KEY_MASTER_PIN_HASH,"");if(expected.isEmpty()){toast("This count file has no Master PIN. Use the original Master phone.");return;}
        EditText pin=masterPinEntry("4-digit Master PIN");AlertDialog dialog=new AlertDialog.Builder(this).setTitle("Transfer Master Access").setMessage("Enter the Master PIN. This phone will become the Master device for final reports.").setView(pin).setPositiveButton("Transfer",null).setNegativeButton("Cancel",null).create();
        dialog.setOnShowListener(x->dialog.getButton(AlertDialog.BUTTON_POSITIVE).setOnClickListener(v->{if(!expected.equals(hashMasterPin(pin.getText().toString()))){toast("Incorrect Master PIN");pin.selectAll();return;}String current=savedUserName();prefs().edit().putString(KEY_DEVICE_ROLE,ROLE_MASTER).putString(KEY_MASTER_USER,current).apply();dialog.dismiss();toast("This phone is now the Master device");}));dialog.show();
    }

    private void changeMasterPin(){
        String expected=prefs().getString(KEY_MASTER_PIN_HASH,"");if(expected.isEmpty()){ensureMasterPin(()->toast("Master PIN created"));return;}
        EditText oldPin=masterPinEntry("Current Master PIN");AlertDialog first=new AlertDialog.Builder(this).setTitle("Change Master PIN").setView(oldPin).setPositiveButton("Continue",null).setNegativeButton("Cancel",null).create();
        first.setOnShowListener(x->first.getButton(AlertDialog.BUTTON_POSITIVE).setOnClickListener(v->{if(!expected.equals(hashMasterPin(oldPin.getText().toString()))){toast("Incorrect Master PIN");return;}first.dismiss();EditText nextPin=masterPinEntry("New 4-digit Master PIN");AlertDialog second=new AlertDialog.Builder(this).setTitle("New Master PIN").setView(nextPin).setPositiveButton("Save",null).setNegativeButton("Cancel",null).create();second.setOnShowListener(y->second.getButton(AlertDialog.BUTTON_POSITIVE).setOnClickListener(z->{String n=nextPin.getText().toString();if(!validMasterPin(n)){toast("Master PIN must be exactly 4 digits");return;}prefs().edit().putString(KEY_MASTER_PIN_HASH,hashMasterPin(n)).apply();second.dismiss();toast("Master PIN changed");}));second.show();}));first.show();
    }

    private void applySharedProjectRole(Uri uri){
        String hash="";try(InputStream in=getContentResolver().openInputStream(uri);BufferedReader br=new BufferedReader(new InputStreamReader(in,StandardCharsets.UTF_8))){String line;for(int i=0;i<3&&(line=br.readLine())!=null;i++){if(line.startsWith("#ICE_ONHAND_PROJECT\\t")){String[] f=line.split("\\t",-1);for(String x:f)if(x.startsWith("PIN="))hash=x.substring(4).trim();break;}}}catch(Exception ignored){}
        prefs().edit().putString(KEY_DEVICE_ROLE,ROLE_COUNT_USER).putString(KEY_MASTER_PIN_HASH,hash).remove(KEY_MASTER_USER).apply();
    }
'''
if old not in s: raise SystemExit('3.0.132 target missing: old master methods')
s=s.replace(old,new,1)
s=s.replace('''    private void openBatchMergeForMaster() {
        String master=savedMasterUserName();''','''    private void openBatchMergeForMaster() {
        if(!isMasterDevice()){new AlertDialog.Builder(this).setTitle("Master Device Required").setMessage("This phone is a Count User. Final combined reports are locked. Use Transfer / Unlock Master in Options and enter the Master PIN.").setPositiveButton("OK",null).show();return;}
        String master=savedMasterUserName();''',1)
s=s.replace('''        else if(requestCode==REQ_IMPORT)readImport(data.getData());''','''        else if(requestCode==REQ_IMPORT){applySharedProjectRole(data.getData());readImport(data.getData());}''',1)
s=s.replace('''            prefs().edit().putString(KEY_USER_NAME,n).apply();
            dialog.dismiss();''','''            android.content.SharedPreferences.Editor editor=prefs().edit().putString(KEY_USER_NAME,n);
            if(isMasterDevice()&&savedMasterUserName().isEmpty())editor.putString(KEY_MASTER_USER,n);
            editor.apply();
            dialog.dismiss();''',1)
p.write_text(s)

# Shared-file metadata is ignored by the inventory reader but carries the role and PIN hash.
p=Path('app/src/main/java/com/iceinventory/onhand/TabTextUtils.java'); s=p.read_text()
s=s.replace('''        while((first=br.readLine())!=null&&first.trim().isEmpty()){}''','''        while((first=br.readLine())!=null&&(first.trim().isEmpty()||first.startsWith("#ICE_ONHAND_PROJECT\\t"))){}''',1)
s=s.replace('''            if(line.trim().isEmpty())continue;
            imported+=importOne''','''            if(line.trim().isEmpty()||line.startsWith("#ICE_ONHAND_PROJECT\\t"))continue;
            imported+=importOne''',1)
p.write_text(s)

meta='''    private String projectMetadata(){String h=getSharedPreferences("onhand_settings",MODE_PRIVATE).getString("master_pin_hash","");return "#ICE_ONHAND_PROJECT\\tROLE=COUNT_USER\\tPIN="+h+"\\r\\n";}\n'''
p=Path('app/src/main/java/com/iceinventory/onhand/MonthlyInventoryActivity.java'); s=p.read_text()
s=s.replace('''    private String onHandText(){StringBuilder b=new StringBuilder();''',meta+'''    private String onHandText(){StringBuilder b=new StringBuilder(projectMetadata());''',1)
s=s.replace('''if(line.trim().isEmpty())continue;String[] v=line.split''','''if(line.trim().isEmpty()||line.startsWith("#ICE_ONHAND_PROJECT\\t"))continue;String[] v=line.split''',1)
p.write_text(s)

p=Path('app/src/main/java/com/iceinventory/onhand/LiqPosInventoryActivity.java'); s=p.read_text()
s=s.replace('''try(FileOutputStream o=new FileOutputStream(f)){for(Product p:products.values())''','''try(FileOutputStream o=new FileOutputStream(f)){String h=getSharedPreferences("onhand_settings",MODE_PRIVATE).getString("master_pin_hash","");o.write(("#ICE_ONHAND_PROJECT\\tROLE=COUNT_USER\\tPIN="+h+"\\r\\n").getBytes(StandardCharsets.UTF_8));for(Product p:products.values())''',1)
s=s.replace('''if(line.trim().isEmpty())continue;List<String> v=''','''if(line.trim().isEmpty()||line.startsWith("#ICE_ONHAND_PROJECT\\t"))continue;List<String> v=''',1)
p.write_text(s)

# Ensure manually-created inventories also establish the device as Master.
p=Path('app/src/main/java/com/iceinventory/onhand/MainActivity.java'); s=p.read_text()
old='''    private void newSession() {
        EditText input=new EditText(this);input.setHint("Inventory name");'''
new='''    private void newSession() {ensureMasterPin(this::showNewSessionDialog);}

    private void showNewSessionDialog() {
        EditText input=new EditText(this);input.setHint("Inventory name");'''
if old not in s: raise SystemExit('3.0.132 target missing: new session')
s=s.replace(old,new,1);p.write_text(s)

checks={
 'version':'3.0.132', 'role lock':'COUNT USER — MASTER REPORTS LOCKED',
 'pin transfer':'TRANSFER / UNLOCK MASTER', 'metadata':'#ICE_ONHAND_PROJECT',
 'master gate':'Master Device Required'}
alltext='\n'.join(Path(x).read_text() for x in ['app/src/main/java/com/iceinventory/onhand/MainActivity.java','app/src/main/java/com/iceinventory/onhand/MonthlyInventoryActivity.java','app/src/main/java/com/iceinventory/onhand/LiqPosInventoryActivity.java'])
missing=[k for k,v in checks.items() if v not in alltext]
if missing: raise SystemExit('3.0.132 verification failed: '+', '.join(missing))
print('Prepared iCE Onhand 3.0.132: project Master role + protected 4-digit Master PIN transfer')
