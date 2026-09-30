#!/usr/bin/env python3
from pathlib import Path
import runpy

root=Path(__file__).resolve().parents[1]
runpy.run_path(str(root/".github"/"prepare_30190.py"),run_name="__main__")

gradle=root/"app"/"build.gradle"
s=gradle.read_text().replace("versionCode 30190","versionCode 30191").replace("versionName '3.0.190'","versionName '3.0.191'")
gradle.write_text(s)

manifest=root/"app"/"src"/"main"/"AndroidManifest.xml"
s=manifest.read_text().replace("iCE Onhand 3.0.190","iCE Onhand 3.0.191")
permission='    <uses-permission android:name="android.permission.VIBRATE" />\n'
if "android.permission.VIBRATE" not in s:
    s=s.replace('    <uses-permission android:name="android.permission.INTERNET" />\n','    <uses-permission android:name="android.permission.INTERNET" />\n'+permission,1)
manifest.write_text(s)

main=root/"app"/"src"/"main"/"java"/"com"/"iceinventory"/"onhand"/"MainActivity.java"
s=main.read_text().replace("Onhand Inventory 3.0.190","Onhand Inventory 3.0.191")

old_scan='''        if(code.isEmpty()){toast("No barcode detected");return;}
        scanFeedback();
        barcode.setShowSoftInputOnFocus(false);'''
new_scan='''        if(code.isEmpty()){toast("No barcode detected");return;}
        barcode.setShowSoftInputOnFocus(false);'''
if s.count(old_scan)!=1:raise SystemExit("Early scan feedback target not found")
s=s.replace(old_scan,new_scan,1)

old_saved='''    private void useSavedBarcodeMatch(InventoryDb.Row row,boolean flexible) {
        if(row==null)return;
        String actual='''
new_saved='''    private void useSavedBarcodeMatch(InventoryDb.Row row,boolean flexible) {
        if(row==null)return;
        scanFeedback();
        String actual='''
if s.count(old_saved)!=1:raise SystemExit("Saved barcode success target not found")
s=s.replace(old_saved,new_saved,1)

old_internet='''                    if(found!=null) {
                        String d=found.description==null?"":found.description.trim();'''
new_internet='''                    if(found!=null) {
                        scanFeedback();
                        String d=found.description==null?"":found.description.trim();'''
if s.count(old_internet)!=1:raise SystemExit("Internet match feedback target not found")
s=s.replace(old_internet,new_internet,1)

old_feedback='''    private void scanFeedback() {
        SharedPreferences p=prefs();
        if(p.getBoolean(KEY_BEEP,true)) {
            try {
                ToneGenerator tg=new ToneGenerator(AudioManager.STREAM_NOTIFICATION,85);
                tg.startTone(ToneGenerator.TONE_PROP_BEEP,120);
                barcode.postDelayed(tg::release,180);
            } catch(Exception ignored){}
        }
        if(p.getBoolean(KEY_VIBRATE,true)) {
            try {
                Vibrator vib=(Vibrator)getSystemService(VIBRATOR_SERVICE);
                if(vib!=null&&vib.hasVibrator()) {
                    if(Build.VERSION.SDK_INT>=26)vib.vibrate(VibrationEffect.createOneShot(60,VibrationEffect.DEFAULT_AMPLITUDE));
                    else vib.vibrate(60);
                }
            } catch(Exception ignored){}
        }
    }'''
new_feedback='''    private void scanFeedback() {
        SharedPreferences p=prefs();
        if(p.getBoolean(KEY_BEEP,true)) {
            try {
                final ToneGenerator tg=new ToneGenerator(AudioManager.STREAM_MUSIC,100);
                tg.startTone(ToneGenerator.TONE_PROP_BEEP2,180);
                barcode.postDelayed(tg::release,260);
            } catch(Exception ignored){}
        }
        if(p.getBoolean(KEY_VIBRATE,true)) {
            try {
                Vibrator vib=(Vibrator)getSystemService(VIBRATOR_SERVICE);
                if(vib!=null&&vib.hasVibrator()) {
                    if(Build.VERSION.SDK_INT>=26)vib.vibrate(VibrationEffect.createWaveform(new long[]{0,80,45,80},-1));
                    else vib.vibrate(new long[]{0,80,45,80},-1);
                }
            } catch(Exception ignored){}
        }
    }'''
if s.count(old_feedback)!=1:raise SystemExit("Scan feedback method target not found")
s=s.replace(old_feedback,new_feedback,1)

old_session='''        if(requestedSession>0){for(InventoryDb.Session s:sessions)if(s.id==requestedSession){sessionId=s.id;sessionName=s.name;activeSessionId=s.id;break;}}
        else {for(InventoryDb.Session s:sessions)if(s.id==activeSessionId){sessionId=s.id;sessionName=s.name;break;}}
        prefs().edit().putLong(KEY_ACTIVE_SESSION,activeSessionId).apply();'''
new_session='''        if(requestedSession>0){for(InventoryDb.Session s:sessions)if(s.id==requestedSession){sessionId=s.id;sessionName=s.name;activeSessionId=s.id;break;}}
        else {for(InventoryDb.Session s:sessions)if(s.id==activeSessionId){sessionId=s.id;sessionName=s.name;break;}}
        String rememberedLocation=prefs().getString(confirmedLocationKey(sessionId),"").trim();
        if(!rememberedLocation.isEmpty()){confirmedLocation=rememberedLocation;confirmedLocationSession=sessionId;db.addLocation(rememberedLocation);}
        prefs().edit().putLong(KEY_ACTIVE_SESSION,activeSessionId).apply();'''
if s.count(old_session)!=1:raise SystemExit("Active session location restore target not found")
s=s.replace(old_session,new_session,1)

old_submit='''    private void submitCountingLocation(String name){
        String n=name==null?"":name.trim();
        if(n.isEmpty()){toast("Choose or scan a location first");return;}
        db.addLocation(n);confirmedLocation=n;confirmedLocationSession=sessionId;
        refreshLocations();'''
new_submit='''    private String confirmedLocationKey(long id){return "confirmed_count_location_"+id;}

    private void rememberConfirmedLocation(String value){
        if(sessionId>0&&value!=null&&!value.trim().isEmpty())prefs().edit().putString(confirmedLocationKey(sessionId),value.trim()).apply();
    }

    private void submitCountingLocation(String name){
        String n=name==null?"":name.trim();
        if(n.isEmpty()){toast("Choose or scan a location first");return;}
        db.addLocation(n);confirmedLocation=n;confirmedLocationSession=sessionId;rememberConfirmedLocation(n);
        refreshLocations();'''
if s.count(old_submit)!=1:raise SystemExit("Counting location persistence target not found")
s=s.replace(old_submit,new_submit,1)
s=s.replace('''confirmedLocation=target;confirmedLocationSession=sessionId;refreshLocations();refreshList();''','''confirmedLocation=target;confirmedLocationSession=sessionId;rememberConfirmedLocation(target);refreshLocations();refreshList();''',1)
main.write_text(s)

checks={
 "version":"versionName '3.0.191'" in gradle.read_text(),
 "vibrate permission":"android.permission.VIBRATE" in manifest.read_text(),
 "media beep":"AudioManager.STREAM_MUSIC,100" in s,
 "strong vibration":"new long[]{0,80,45,80}" in s,
 "match only":s.count("scanFeedback();")==2 and "useSavedBarcodeMatch" in s,
 "location restored":"rememberedLocation" in s and "confirmedLocationKey(sessionId)" in s,
 "location saved":"rememberConfirmedLocation(n)" in s and "rememberConfirmedLocation(target)" in s,
 "prior count protection":"physicalCountStarted" in s,
}
failed=[k for k,v in checks.items() if not v]
if failed:raise SystemExit("3.0.191 verification failed: "+", ".join(failed))
print("Prepared iCE OnHand 3.0.191: reliable scan feedback and remembered counting location")
