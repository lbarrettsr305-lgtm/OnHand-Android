from pathlib import Path

base = Path('.github/prepare_30141.py')
exec(compile(base.read_text(), str(base), 'exec'), {'__name__': '__main__', '__file__': str(base)})

def replace(path, old, new):
    p = Path(path)
    source = p.read_text()
    if source.count(old) != 1:
        raise SystemExit(f'3.0.142 expected one target in {path}: {old[:70]}')
    p.write_text(source.replace(old, new, 1))

replace('app/build.gradle', 'versionCode 30141', 'versionCode 30142')
replace('app/build.gradle', "versionName '3.0.141'", "versionName '3.0.142'")
replace('app/src/main/AndroidManifest.xml', 'iCE Onhand 3.0.141', 'iCE Onhand 3.0.142')

main = 'app/src/main/java/com/iceinventory/onhand/MainActivity.java'
replace(main, 'Onhand Inventory 3.0.141', 'Onhand Inventory 3.0.142')
replace(main,
    '''        if(role.isEmpty()&&!savedMasterUserName().isEmpty())return ROLE_MASTER;
        return role;''',
    '''        return role;''')
replace(main,
    '''String masterActionLabel=masterDevice?"CHANGE MASTER PIN":(prefs().getString(KEY_MASTER_PIN_HASH,"").isEmpty()?"MAKE THIS PHONE MASTER — CREATE PIN":"MAKE THIS PHONE MASTER — PIN REQUIRED");''',
    '''String masterActionLabel=masterDevice?"CHANGE MASTER PIN":"COUNT USER — MASTER ENROLLMENT LOCKED";''')
replace(main,
    '''masterUserButton.setOnClickListener(v->{if(masterDevice)changeMasterPin();else ensureMasterPin(()->{});});''',
    '''masterUserButton.setOnClickListener(v->{if(masterDevice)changeMasterPin();else new AlertDialog.Builder(this).setTitle("Master Enrollment Locked").setMessage("A Count User cannot make this phone Master. Use an already authorized Master phone for combined reports. Authorized enrollment of another Master phone requires a future approval process.").setPositiveButton("OK",null).show();});''')

# Never interpret a local PIN or a hash copied from a shared file as authority.
replace(main,
    '''        if(isMasterDevice()&&!existing.isEmpty()){next.run();return;}
        if(!existing.isEmpty()){unlockMasterWithPin(next);return;}''',
    '''        if(!isMasterDevice()){toast("Count User: Master enrollment is locked");return;}
        if(!existing.isEmpty()){next.run();return;}''')
start = Path(main).read_text()
opening = start.index('    private void unlockMasterWithPin(){')
closing = start.index('    private void changeMasterPin(){', opening)
start = start[:opening] + start[closing:]
Path(main).write_text(start)
replace(main,
    '''    private void applySharedProjectRole(Uri uri){
        String hash="";try(InputStream in=getContentResolver().openInputStream(uri);BufferedReader br=new BufferedReader(new InputStreamReader(in,StandardCharsets.UTF_8))){String line;for(int i=0;i<3&&(line=br.readLine())!=null;i++){if(line.startsWith("#ICE_ONHAND_PROJECT\\t")){String[] f=line.split("\\t",-1);for(String x:f)if(x.startsWith("PIN="))hash=x.substring(4).trim();break;}}}catch(Exception ignored){}
        prefs().edit().putString(KEY_DEVICE_ROLE,ROLE_COUNT_USER).putString(KEY_MASTER_PIN_HASH,hash).remove(KEY_MASTER_USER).apply();refreshOperatorStatus();
    }''',
    '''    private void applySharedProjectRole(Uri uri){
        // A shared count file is untrusted data. It cannot set roles or supply a PIN.
        // Keep the existing Master device's authority when it imports count files.
        if(!isMasterDevice())prefs().edit().putString(KEY_DEVICE_ROLE,ROLE_COUNT_USER)
                .remove(KEY_MASTER_PIN_HASH).remove(KEY_MASTER_USER).apply();
        refreshOperatorStatus();
    }''')
replace(main,
    '''Use Transfer / Unlock Master in Options and enter the Master PIN.''',
    '''Use the authorized Master phone.''')
replace(main,
    '''        String expected=prefs().getString(KEY_MASTER_PIN_HASH,"");
        if(expected.isEmpty()){toast("Advanced import is locked until a Master PIN is created");return;}''',
    '''        if(!isMasterDevice()){toast("Advanced import requires the Master phone");return;}
        String expected=prefs().getString(KEY_MASTER_PIN_HASH,"");
        if(expected.isEmpty()){toast("Set a Master PIN on the authorized Master phone first");return;}''')

# Master PIN hashes are not project data and must not travel with shared files.
replace('app/src/main/java/com/iceinventory/onhand/MonthlyInventoryActivity.java',
    '''String h=getSharedPreferences("onhand_settings",MODE_PRIVATE).getString("master_pin_hash","");return "#ICE_ONHAND_PROJECT\\tROLE=COUNT_USER\\tPIN="+h+"\\r\\n";''',
    '''return "#ICE_ONHAND_PROJECT\\tROLE=COUNT_USER\\r\\n";''')
replace('app/src/main/java/com/iceinventory/onhand/LiqPosInventoryActivity.java',
    '''String h=getSharedPreferences("onhand_settings",MODE_PRIVATE).getString("master_pin_hash","");o.write(("#ICE_ONHAND_PROJECT\\tROLE=COUNT_USER\\tPIN="+h+"\\r\\n").getBytes(StandardCharsets.UTF_8));''',
    '''o.write("#ICE_ONHAND_PROJECT\\tROLE=COUNT_USER\\r\\n".getBytes(StandardCharsets.UTF_8));''')

replace('app/src/main/AndroidManifest.xml',
    '''android:allowBackup="true"''',
    '''android:allowBackup="false"''')

help_path = 'app/src/main/java/com/iceinventory/onhand/HelpActivity.java'
help_source = Path(help_path).read_text()
opening = help_source.index('   "Only the designated Audit Manager phone should be made the Master.')
closing = help_source.index(');', opening)
help_source = help_source[:opening] + '''   "The existing authorized Audit Manager phone remains Master after an update. It can combine count files and create final reports.\\n\\nA Count User phone cannot create a Master PIN or use a PIN copied from a shared count file to become Master. New Master enrollment is locked until a trusted approval process is available.\\n\\nOn the Master phone, use Options to change its PIN. Keep this phone and its PIN safe. If it is lost, stop and arrange recovery rather than promoting a Count User phone.")''' + help_source[closing+1:]
Path(help_path).write_text(help_source)

source = Path(main).read_text()
assert 'unlockMasterWithPin' not in source
assert 'MAKE THIS PHONE MASTER' in source  # Existing Master-only PIN setup label.
assert 'if(!isMasterDevice()){toast("Count User: Master enrollment is locked")' in source
assert 'if(!isMasterDevice()){toast("Advanced import requires the Master phone")' in source
print('Prepared iCE OnHand 3.0.142: Count User cannot self-enroll, import PIN hashes, or unlock advanced import')
