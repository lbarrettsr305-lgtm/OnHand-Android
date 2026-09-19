from pathlib import Path

# Preserve 3.0.113 and add guided status, same-device verification, sharing, and email attachment intake.
base=Path('.github/prepare_30113.py')
exec(compile(base.read_text(),str(base),'exec'),{'__name__':'__main__','__file__':str(base)})

p=Path('app/build.gradle')
g=p.read_text().replace('versionCode 30113','versionCode 30114',1).replace("versionName '3.0.113'","versionName '3.0.114'",1)
if 'versionCode 30114' not in g or "versionName '3.0.114'" not in g: raise SystemExit('3.0.114 Gradle target missing')
p.write_text(g)

p=Path('app/src/main/java/com/iceinventory/onhand/MainActivity.java')
s=p.read_text()
s=s.replace('''    private static final int REQ_EXPORT_FORMAT=1007;''','''    private static final int REQ_EXPORT_FORMAT=1007;
    private static final int REQ_MONTHLY_INVENTORY=1014;''',1)
s=s.replace('''                    if(which==0)startActivity(new Intent(this,MonthlyInventoryActivity.class));''','''                    if(which==0)startActivityForResult(new Intent(this,MonthlyInventoryActivity.class),REQ_MONTHLY_INVENTORY);''',1)
anchor='''        if(requestCode==REQ_MULTIPLY_CURRENT){'''
handler='''        if(requestCode==REQ_MONTHLY_INVENTORY){
            if(data!=null){
                long monthlyId=data.getLongExtra(MonthlyInventoryActivity.EXTRA_SESSION_ID,-1L);
                String monthlyName=data.getStringExtra(MonthlyInventoryActivity.EXTRA_SESSION_NAME);
                if(monthlyId>0){sessionId=monthlyId;sessionName=monthlyName==null?"Monthly Inventory":monthlyName;lastBarcode="";refreshLocations();refreshList();toast("Verified monthly inventory is ready to count");}
            }
            return;
        }
'''+anchor
if anchor not in s: raise SystemExit('3.0.114 monthly result handler target missing')
s=s.replace(anchor,handler,1)
s=s.replace('Onhand Inventory 3.0.113','Onhand Inventory 3.0.114',1)
if 'Onhand Inventory 3.0.114' not in s: raise SystemExit('3.0.114 visible version target missing')
p.write_text(s)

p=Path('app/src/main/AndroidManifest.xml')
m=p.read_text().replace('iCE Onhand 3.0.113','iCE Onhand 3.0.114',1)
old='''        <activity
            android:name=".MonthlyInventoryActivity"
            android:exported="false"
            android:screenOrientation="unspecified" />'''
new='''        <activity
            android:name=".MonthlyInventoryActivity"
            android:exported="true"
            android:screenOrientation="unspecified">
            <intent-filter>
                <action android:name="android.intent.action.VIEW" />
                <category android:name="android.intent.category.DEFAULT" />
                <category android:name="android.intent.category.BROWSABLE" />
                <data android:mimeType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet" />
            </intent-filter>
            <intent-filter>
                <action android:name="android.intent.action.SEND" />
                <category android:name="android.intent.category.DEFAULT" />
                <data android:mimeType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet" />
            </intent-filter>
        </activity>'''
if old not in m: raise SystemExit('3.0.114 manifest monthly activity target missing')
m=m.replace(old,new,1)
p.write_text(m)

monthly=Path('app/src/main/java/com/iceinventory/onhand/MonthlyInventoryActivity.java').read_text()
checks={
    'blank GTIN excluded':'if(gtin.isEmpty()){blankGtin++;continue;}' in monthly,
    'visible status':'✓ PETROSOFT FILE IMPORTED AND VALIDATED' in monthly,
    'master completion':'✓ MASTER FILE CREATED' in monthly,
    'onhand completion':'✓ ONHAND TAB-DELIMITED FILE CREATED' in monthly,
    'device verification':'rows.size()!=products.size()||qty!=0' in monthly,
    'share file':'Intent.EXTRA_STREAM,onHandUri' in monthly,
    'email/view import':'incomingSource(getIntent())' in monthly,
    'email manifest':all(v in m for v in ['android.intent.action.VIEW','android.intent.action.SEND','spreadsheetml.sheet']),
    'active device session':'REQ_MONTHLY_INVENTORY' in s and 'Verified monthly inventory is ready to count' in s,
}
missing=[k for k,v in checks.items() if not v]
if missing: raise SystemExit('3.0.114 verification failed: '+', '.join(missing))
print('Prepared iCE Onhand 3.0.114: guided Petrosoft workflow, exclusions, device verification, sharing, and email attachment import')
