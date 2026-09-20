from pathlib import Path

base=Path('.github/prepare_30132.py')
exec(compile(base.read_text(),str(base),'exec'),{'__name__':'__main__','__file__':str(base)})

def rep(path, old, new, label):
    p=Path(path); s=p.read_text()
    if old not in s: raise SystemExit('3.0.133 target missing: '+label)
    p.write_text(s.replace(old,new,1))

rep('app/build.gradle','versionCode 30132','versionCode 30133','Gradle code')
rep('app/build.gradle',"versionName '3.0.132'","versionName '3.0.133'",'Gradle name')
rep('app/src/main/AndroidManifest.xml','iCE Onhand 3.0.132','iCE Onhand 3.0.133','manifest')

p=Path('app/src/main/java/com/iceinventory/onhand/MainActivity.java'); s=p.read_text()
s=s.replace('Onhand Inventory 3.0.132','Onhand Inventory 3.0.133',1)
s=s.replace('''    private TextView titleSession;
    private TextView summary;''','''    private TextView titleSession;
    private TextView operatorStatus;
    private TextView summary;''',1)
s=s.replace('''        titleSession=text(sessionName,19,gold(),true);
        heading.addView(ice);heading.addView(app);heading.addView(titleSession);''','''        titleSession=text(sessionName,19,gold(),true);
        operatorStatus=text(operatorStatusText(),14,Color.WHITE,true);
        heading.addView(ice);heading.addView(app);heading.addView(titleSession);heading.addView(operatorStatus);''',1)

# Keep the label current after name, role, or PIN actions.
s=s.replace('''    private String userNameButtonLabel() {
        String n=savedUserName();''','''    private String operatorStatusText(){String n=savedUserName();if(n.isEmpty())n="NOT SET";String role=isMasterDevice()?"MASTER":"COUNT USER";return "User: "+n+"  •  Role: "+role;}
    private void refreshOperatorStatus(){if(operatorStatus!=null)operatorStatus.setText(operatorStatusText());}

    private String userNameButtonLabel() {
        String n=savedUserName();''',1)
s=s.replace('''prefs().edit().putString(KEY_DEVICE_ROLE,ROLE_MASTER).putString(KEY_MASTER_PIN_HASH,hashMasterPin(value)).putString(KEY_MASTER_USER,current).apply();dialog.dismiss();next.run();''','''prefs().edit().putString(KEY_DEVICE_ROLE,ROLE_MASTER).putString(KEY_MASTER_PIN_HASH,hashMasterPin(value)).putString(KEY_MASTER_USER,current).apply();refreshOperatorStatus();dialog.dismiss();next.run();''',1)
s=s.replace('''prefs().edit().putString(KEY_DEVICE_ROLE,ROLE_MASTER).putString(KEY_MASTER_USER,current).apply();dialog.dismiss();toast("This phone is now the Master device");''','''prefs().edit().putString(KEY_DEVICE_ROLE,ROLE_MASTER).putString(KEY_MASTER_USER,current).apply();refreshOperatorStatus();dialog.dismiss();toast("This phone is now the Master device");''',1)
s=s.replace('''prefs().edit().putString(KEY_DEVICE_ROLE,ROLE_COUNT_USER).putString(KEY_MASTER_PIN_HASH,hash).remove(KEY_MASTER_USER).apply();''','''prefs().edit().putString(KEY_DEVICE_ROLE,ROLE_COUNT_USER).putString(KEY_MASTER_PIN_HASH,hash).remove(KEY_MASTER_USER).apply();refreshOperatorStatus();''',1)
s=s.replace('''            editor.apply();
            dialog.dismiss();''','''            editor.apply();
            refreshOperatorStatus();
            dialog.dismiss();''',1)

# Prompt once when the main screen first opens if this phone has no operator name.
anchor='''        setContentView(root);
        root.requestApplyInsets();'''
replacement='''        setContentView(root);
        root.requestApplyInsets();
        if(savedUserName().isEmpty())root.postDelayed(()->promptUserName(false),450);'''
if anchor not in s: raise SystemExit('3.0.133 target missing: main screen completion')
s=s.replace(anchor,replacement,1)
p.write_text(s)

main=p.read_text()
checks={'visible version':'Onhand Inventory 3.0.133','header user':'User: "+n+"  •  Role: "+role','startup prompt':'root.postDelayed(()->promptUserName(false),450)','role refresh':'refreshOperatorStatus()'}
missing=[k for k,v in checks.items() if v not in main]
if missing: raise SystemExit('3.0.133 verification failed: '+', '.join(missing))
print('Prepared iCE Onhand 3.0.133: visible main-screen user and Master/Count User role')
