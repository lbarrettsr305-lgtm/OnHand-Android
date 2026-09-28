#!/usr/bin/env python3
from pathlib import Path
import runpy

root = Path(__file__).resolve().parents[1]
runpy.run_path(str(root / ".github" / "prepare_30184.py"), run_name="__main__")

gradle = root / "app" / "build.gradle"
s = gradle.read_text().replace("versionCode 30184", "versionCode 30185").replace("versionName '3.0.184'", "versionName '3.0.185'")
gradle.write_text(s)

manifest = root / "app" / "src" / "main" / "AndroidManifest.xml"
manifest.write_text(manifest.read_text().replace("iCE Onhand 3.0.184", "iCE Onhand 3.0.185"))

main = root / "app" / "src" / "main" / "java" / "com" / "iceinventory" / "onhand" / "MainActivity.java"
s = main.read_text().replace("Onhand Inventory 3.0.184", "Onhand Inventory 3.0.185")

old_header = '''            out.write("#ICE_ONHAND_PROJECT\\tROLE="+(masterCandidate?"MASTER_CANDIDATE":"COUNT_USER")+"\\tMASTER_PIN_HASH="+prefs().getString(KEY_MASTER_PIN_HASH,"")+"\\r\\nQuantity\\tBarcode\\tDescription\\tPrice\\r\\n");'''
new_header = '''            String projectHeader="#ICE_ONHAND_PROJECT\\tROLE="+(masterCandidate?"MASTER_CANDIDATE":"COUNT_USER")+"\\tMASTER_PIN_HASH="+prefs().getString(KEY_MASTER_PIN_HASH,"");
            if(masterCandidate){
                android.content.SharedPreferences workflow=getSharedPreferences("monthly_workflow_state",MODE_PRIVATE);
                java.io.File source=new java.io.File(getFilesDir(),"monthly_workflow_source.xlsx");
                if(source.isFile()&&(workflow.getBoolean("active",false)||workflow.getBoolean("archived",false))){
                    java.io.ByteArrayOutputStream bytes=new java.io.ByteArrayOutputStream();
                    try(java.io.InputStream input=new java.io.FileInputStream(source)){byte[] buffer=new byte[32768];int length;while((length=input.read(buffer))!=-1)bytes.write(buffer,0,length);}
                    projectHeader+="\\tPOS_PROFILE=PETROSOFT"
                        +"\\tWORKFLOW_ACTIVE="+workflow.getBoolean("active",false)
                        +"\\tWORKFLOW_ARCHIVED="+workflow.getBoolean("archived",false)
                        +"\\tWORKFLOW_STAGE="+workflow.getInt("stage",5)
                        +"\\tWORKFLOW_STORE="+shareField(workflow.getString("store",sessionName))
                        +"\\tWORKFLOW_DATE="+shareField(workflow.getString("date",""))
                        +"\\tWORKFLOW_SOURCE_NAME="+shareField(workflow.getString("source_name","Price Management Excel"))
                        +"\\tWORKFLOW_SOURCE_B64="+android.util.Base64.encodeToString(bytes.toByteArray(),android.util.Base64.NO_WRAP);
                }
            }
            out.write(projectHeader+"\\r\\nQuantity\\tBarcode\\tDescription\\tPrice\\r\\n");'''
if s.count(old_header) != 1:
    raise SystemExit("Shared project header source not found")
s = s.replace(old_header, new_header, 1)

old_apply = '''    private void applySharedProjectRole(Uri uri){
        String verifier="",role="";
        try(InputStream in=getContentResolver().openInputStream(uri);BufferedReader br=new BufferedReader(new InputStreamReader(in,StandardCharsets.UTF_8))){String first=br.readLine();if(first!=null&&first.startsWith("#ICE_ONHAND_PROJECT\\t")){for(String part:first.split("\\t")){if(part.startsWith("MASTER_PIN_HASH="))verifier=part.substring("MASTER_PIN_HASH=".length()).trim();else if(part.startsWith("ROLE="))role=part.substring("ROLE=".length()).trim();}}}catch(Exception ignored){}
        if(!isMasterDevice()){android.content.SharedPreferences.Editor e=prefs().edit().putString(KEY_DEVICE_ROLE,ROLE_COUNT_USER).remove(KEY_MASTER_PIN_HASH).remove(KEY_MASTER_USER).putBoolean("pending_master_candidate","MASTER_CANDIDATE".equals(role));if(verifier.matches("[0-9a-fA-F]{64}"))e.putString(KEY_AUTHORIZED_MASTER_PIN_HASH,verifier);e.apply();}
        refreshOperatorStatus();
    }'''
new_apply = '''    private void applySharedProjectRole(Uri uri){
        String verifier="",role="",profile="",source64="",workflowStore="",workflowDate="",workflowSourceName="";boolean workflowActive=false,workflowArchived=false;int workflowStage=5;
        try(InputStream in=getContentResolver().openInputStream(uri);BufferedReader br=new BufferedReader(new InputStreamReader(in,StandardCharsets.UTF_8))){
            String first=br.readLine();
            if(first!=null&&first.startsWith("#ICE_ONHAND_PROJECT\\t")){
                for(String part:first.split("\\t")){
                    if(part.startsWith("MASTER_PIN_HASH="))verifier=part.substring("MASTER_PIN_HASH=".length()).trim();
                    else if(part.startsWith("ROLE="))role=part.substring("ROLE=".length()).trim();
                    else if(part.startsWith("POS_PROFILE="))profile=part.substring("POS_PROFILE=".length()).trim();
                    else if(part.startsWith("WORKFLOW_ACTIVE="))workflowActive=Boolean.parseBoolean(part.substring("WORKFLOW_ACTIVE=".length()).trim());
                    else if(part.startsWith("WORKFLOW_ARCHIVED="))workflowArchived=Boolean.parseBoolean(part.substring("WORKFLOW_ARCHIVED=".length()).trim());
                    else if(part.startsWith("WORKFLOW_STAGE="))try{workflowStage=Integer.parseInt(part.substring("WORKFLOW_STAGE=".length()).trim());}catch(Exception ignored){}
                    else if(part.startsWith("WORKFLOW_STORE="))workflowStore=part.substring("WORKFLOW_STORE=".length()).trim();
                    else if(part.startsWith("WORKFLOW_DATE="))workflowDate=part.substring("WORKFLOW_DATE=".length()).trim();
                    else if(part.startsWith("WORKFLOW_SOURCE_NAME="))workflowSourceName=part.substring("WORKFLOW_SOURCE_NAME=".length()).trim();
                    else if(part.startsWith("WORKFLOW_SOURCE_B64="))source64=part.substring("WORKFLOW_SOURCE_B64=".length()).trim();
                }
            }
        }catch(Exception ignored){}
        if(!isMasterDevice()){android.content.SharedPreferences.Editor e=prefs().edit().putString(KEY_DEVICE_ROLE,ROLE_COUNT_USER).remove(KEY_MASTER_PIN_HASH).remove(KEY_MASTER_USER).putBoolean("pending_master_candidate","MASTER_CANDIDATE".equals(role));if(verifier.matches("[0-9a-fA-F]{64}"))e.putString(KEY_AUTHORIZED_MASTER_PIN_HASH,verifier);e.apply();}
        if("MASTER_CANDIDATE".equals(role)&&"PETROSOFT".equals(profile)&&!source64.isEmpty()){
            try{
                byte[] source=android.util.Base64.decode(source64,android.util.Base64.DEFAULT);
                try(java.io.FileOutputStream output=new java.io.FileOutputStream(new java.io.File(getFilesDir(),"monthly_workflow_source.xlsx"))){output.write(source);}
                getSharedPreferences("monthly_workflow_state",MODE_PRIVATE).edit()
                    .putBoolean("active",workflowActive).putBoolean("archived",workflowArchived).putInt("stage",workflowStage)
                    .putString("store",workflowStore).putString("date",workflowDate).putString("source_name",workflowSourceName)
                    .putLong("device_session_id",sessionId).apply();
                toast("Petrosoft Master project received");
            }catch(Exception e){showError("Could not restore Petrosoft Master project",e);}
        }
        refreshOperatorStatus();
    }'''
if s.count(old_apply) != 1:
    raise SystemExit("Shared project role source not found")
s = s.replace(old_apply, new_apply, 1)

s = s.replace('''Button master=button("MASTER PHONE — PIN REQUIRED\\nApp + Current Store",2);''','''Button master=button("MASTER PHONE — PIN REQUIRED\\nApp + Complete Petrosoft Project",2);''',1)
s = s.replace('''sendSharedFile(zip,"application/zip","Share OnHand app + current store with new Master");''','''sendSharedFile(zip,"application/zip","Share OnHand app + complete Petrosoft project with new Master");''',1)
s = s.replace('''NEW MASTER PHONE: Enter the Master PIN on this phone, send the protected Master ZIP, install the APK, and import the ONHAND MASTER TXT.''','''NEW MASTER PHONE: Enter the Master PIN on this phone, send the protected Master ZIP, install the APK, and import the ONHAND MASTER TXT. The Petrosoft source, workflow stage, locations, and current store are restored automatically.''',1)
main.write_text(s)

checks = {
    "version": "versionName '3.0.185'" in gradle.read_text(),
    "source embedded": "WORKFLOW_SOURCE_B64=" in s and "Base64.encodeToString" in s,
    "source restored": "Base64.decode" in s and "monthly_workflow_source.xlsx" in s,
    "workflow restored": "Petrosoft Master project received" in s and ".putLong(\"device_session_id\",sessionId)" in s,
    "clear master label": "App + Complete Petrosoft Project" in s,
}
failed = [name for name, ok in checks.items() if not ok]
if failed:
    raise SystemExit("3.0.185 verification failed: " + ", ".join(failed))
print("Prepared iCE OnHand 3.0.185: complete Petrosoft project transfer to new Master phones")
