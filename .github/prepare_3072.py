from pathlib import Path
import runpy, re

# Preserve every working 3.0.71 feature first: verified glossy logo,
# proven scanner/count flow, Cases keyboard fix, exports, Options and Sort.
runpy.run_path('.github/prepare_3071.py', run_name='__main__')

# --- MainActivity: Import TXT must never silently append. Ask the operator to
# Replace Current Data, Append to Current Data, or Cancel before changing data.
p = Path('app/src/main/java/com/iceinventory/onhand/MainActivity.java')
s = p.read_text()

pattern = r'''    private void readImport\(Uri uri\) \{.*?\n    \}\n\n    private String importFileNameKey\(\)\{'''
replacement = '''    private void readImport(Uri uri) {\n        if(uri==null)return;\n        new AlertDialog.Builder(this)\n                .setTitle("Import TXT")\n                .setMessage("Choose how to import this file.\\n\\nReplace Current Data clears the current inventory rows first, then loads this file.\\n\\nAppend to Current Data keeps the current rows and adds this file.")\n                .setPositiveButton("Replace Current Data",(d,w)->performImport(uri,true))\n                .setNeutralButton("Append to Current Data",(d,w)->performImport(uri,false))\n                .setNegativeButton("Cancel",null)\n                .show();\n    }\n\n    private void performImport(Uri uri,boolean replaceCurrent) {\n        if(uri==null)return;\n        String selectedName=displayNameForImport(uri);\n        boolean transactionStarted=false;\n        int imported=0;\n        try {\n            if(replaceCurrent) {\n                db.beginInventoryTransaction();\n                transactionStarted=true;\n                db.clearSessionItems(sessionId);\n            }\n            try(InputStream is=getContentResolver().openInputStream(uri);\n                BufferedReader br=new BufferedReader(new InputStreamReader(is,StandardCharsets.UTF_8))) {\n                imported=TabTextUtils.importRows(br,db,sessionId,prefs(),prefs().getBoolean(KEY_AUTO_GTIN,false));\n            }\n            if(imported>0&&!selectedName.isEmpty()) {\n                prefs().edit().putString(importFileNameKey(),selectedName).apply();\n                String inventoryName=selectedName.trim();\n                int dot=inventoryName.lastIndexOf('.');if(dot>0)inventoryName=inventoryName.substring(0,dot);\n                if(!inventoryName.isEmpty()) {\n                    db.renameSession(sessionId,inventoryName);\n                    sessionName=inventoryName;\n                }\n            }\n            if(transactionStarted)db.setInventoryTransactionSuccessful();\n        } catch(Exception e) {\n            showError("Import failed",e);\n            return;\n        } finally {\n            if(transactionStarted)db.endInventoryTransaction();\n        }\n        refreshLocations();refreshList();\n        toast((replaceCurrent?"Replaced current data • ":"Appended • ")+"Imported "+imported+" tab-delimited TXT rows");\n    }\n\n    private String importFileNameKey(){'''

# Use a function replacement so Python's regex engine does not turn the Java
# \n escape sequences into literal source-code line breaks.
s2, n = re.subn(pattern, lambda m: replacement, s, count=1, flags=re.S)
if n != 1:
    raise SystemExit('3.0.72 target missing: readImport method')
s = s2

oldv = 'TextView app=text("Onhand Inventory 3.0.71",19,Color.WHITE,true);'
newv = 'TextView app=text("Onhand Inventory 3.0.72",19,Color.WHITE,true);'
if oldv not in s:
    raise SystemExit('3.0.72 target missing: visible version')
s = s.replace(oldv,newv,1)
p.write_text(s)

# --- InventoryDb: support a transaction-protected replace import. If reading the
# new file fails, SQLite rolls the clear operation back instead of losing the
# current inventory.
p = Path('app/src/main/java/com/iceinventory/onhand/InventoryDb.java')
s = p.read_text()
marker = '''    public List<Session> sessions() {\n'''
helpers = '''    public void clearSessionItems(long sessionId) {\n        if(sessionId<=0)return;\n        getWritableDatabase().delete("items","session_id=?",new String[]{String.valueOf(sessionId)});\n    }\n\n    public void beginInventoryTransaction() {\n        getWritableDatabase().beginTransaction();\n    }\n\n    public void setInventoryTransactionSuccessful() {\n        getWritableDatabase().setTransactionSuccessful();\n    }\n\n    public void endInventoryTransaction() {\n        android.database.sqlite.SQLiteDatabase sql=getWritableDatabase();\n        if(sql.inTransaction())sql.endTransaction();\n    }\n\n'''
if 'public void clearSessionItems(long sessionId)' not in s:
    if marker not in s:
        raise SystemExit('3.0.72 target missing: InventoryDb sessions marker')
    s = s.replace(marker,helpers+marker,1)
p.write_text(s)

# Advance Android package version so 3.0.72 installs over 3.0.71.
p = Path('app/build.gradle')
s = p.read_text().replace('versionCode 30071','versionCode 30072',1).replace("versionName '3.0.71'","versionName '3.0.72'",1)
if 'versionCode 30072' not in s or "versionName '3.0.72'" not in s:
    raise SystemExit('3.0.72 target missing: Gradle version')
p.write_text(s)

# Keep package label synchronized where the generated manifest uses the versioned label.
p = Path('app/src/main/AndroidManifest.xml')
s = p.read_text().replace('android:label="iCE Onhand 3.0.71"','android:label="iCE Onhand 3.0.72"',1)
p.write_text(s)

print('Prepared iCE Onhand 3.0.72: Import TXT asks Replace / Append / Cancel; Replace is transaction-safe')
