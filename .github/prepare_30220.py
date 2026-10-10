#!/usr/bin/env python3
from pathlib import Path
import re
import runpy

root=Path(__file__).resolve().parent.parent
workflow=root/".github/workflows/build-apk.yml"
w=workflow.read_text()
for new,old in [
    ("Prepare and verify 3.0.220 external scanner flow","Prepare and verify 3.0.219 replace import instructions"),
    (".github/prepare_30220.py",".github/prepare_30219.py"),
    ("iCE-Onhand-Inventory-3.0.220","iCE-Onhand-Inventory-3.0.219"),
]:
    if new not in w: raise SystemExit("3.0.220 workflow seed missing: "+new)
    w=w.replace(new,old)
workflow.write_text(w)
runpy.run_path(str(root/".github/prepare_30219.py"),run_name="__main__")
w=workflow.read_text()
for old,new in [
    ("Prepare and verify 3.0.219 replace import instructions","Prepare and verify 3.0.220 external scanner flow"),
    (".github/prepare_30219.py",".github/prepare_30220.py"),
    ("iCE-Onhand-Inventory-3.0.219","iCE-Onhand-Inventory-3.0.220"),
]:
    if old not in w: raise SystemExit("3.0.218 workflow marker missing: "+old)
    w=w.replace(old,new)
workflow.write_text(w)

main=root/"app/src/main/java/com/iceinventory/onhand/MainActivity.java"
s=main.read_text()

# Label the phone-camera action distinctly so a hardware scanner is used by scanning
# directly into the barcode field.
button_decl=re.compile(r'Button\s+(\w+)=button\("([^"]+)",\d+\);')
scan_button=next((m for m in button_decl.finditer(s) if "scan" in m.group(2).lower() and "location" not in m.group(2).lower()),None)
if scan_button is None:
    context="\n".join(line.strip() for line in s.splitlines() if "button(" in line and any(k in line.lower() for k in ("scan","camera")))
    raise SystemExit("Phone camera action not found; candidates: "+context)
label_start,label_end=scan_button.span(2)
s=s[:label_start]+"Phone Camera"+s[label_end:]
s=s.replace('barcode.setHint("Scan or type barcode");','barcode.setHint("External scanner or type barcode");',1)

# Restore a ready-to-scan focus when the inventory opens or resumes from another screen.
start='        refreshLocations();\n        refreshList();\n    }'
if s.count(start)!=1: raise SystemExit("Startup refresh block missing")
s=s.replace(start,'        refreshLocations();\n        refreshList();\n        barcode.post(this::focusBarcodeWithoutKeyboard);\n    }',1)

# Highlight known scanned items immediately, including when manual quantity entry is enabled.
existing='        if(existing!=null) {'
if s.count(existing)!=1: raise SystemExit("Known barcode branch missing or ambiguous")
s=s.replace(existing,existing+'\n            lastBarcode=code;\n            applyFilter();\n            scrollToLastBarcode();',1)

# Scroll the highlighted row into view after a scan.
marker='    private void applyFilter() {'
helper='''    private void scrollToLastBarcode() {
        if(list==null||lastBarcode==null||lastBarcode.isEmpty())return;
        list.post(()->{
            for(int i=0;i<visibleRows.size();i++){
                InventoryDb.Row row=visibleRows.get(i);
                if(lastBarcode.equals(row.barcode)){list.setSelection(i);return;}
            }
        });
    }

'''
if 'private void scrollToLastBarcode()' not in s:
    if s.count(marker)!=1: raise SystemExit("List filter method missing")
    s=s.replace(marker,helper+marker,1)

# Store the active location per inventory so scanning after resume starts in the same place.
if 'private static final String KEY_LOCATION_PREFIX=' not in s:
    key='    private static final String KEY_AUTO_GTIN="auto_gtin14";'
    if s.count(key)!=1: raise SystemExit("Preference key insertion point missing")
    s=s.replace(key,key+'\n    private static final String KEY_LOCATION_PREFIX="last_location_session_";',1)
if 'import android.widget.AdapterView;' not in s:
    imp='import android.widget.ArrayAdapter;'
    if s.count(imp)!=1: raise SystemExit("Spinner import insertion point missing")
    s=s.replace(imp,'import android.widget.AdapterView;\n'+imp,1)
old='''    private void refreshLocations() {
        List<String> locs=db.locations();
        ArrayAdapter<String> a=new ArrayAdapter<>(this,android.R.layout.simple_spinner_dropdown_item,locs);
        location.setAdapter(a);
    }'''
new='''    private void refreshLocations() {
        List<String> locs=db.locations();
        ArrayAdapter<String> a=new ArrayAdapter<>(this,android.R.layout.simple_spinner_dropdown_item,locs);
        location.setAdapter(a);
        String key=KEY_LOCATION_PREFIX+sessionId;
        String preferred=prefs().getString(key,"");
        int index=locs.indexOf(preferred);
        if(index<0)index=locs.indexOf("Main");
        if(index>=0)location.setSelection(index);
        location.setOnItemSelectedListener(new AdapterView.OnItemSelectedListener(){
            @Override public void onItemSelected(AdapterView<?> parent,View view,int position,long id){
                Object selected=parent.getItemAtPosition(position);
                if(selected!=null)prefs().edit().putString(key,selected.toString()).apply();
                applyFilter();
            }
            @Override public void onNothingSelected(AdapterView<?> parent){}
        });
    }'''
if s.count(old)==1:
    s=s.replace(old,new,1)
elif 'KEY_LOCATION_PREFIX+sessionId' not in s:
    raise SystemExit("Location spinner setup not found")
    
gradle=root/"app/build.gradle"
g=gradle.read_text()
if "versionCode 30219" not in g or "versionName '3.0.219'" not in g:raise SystemExit("3.0.219 Gradle version missing")
gradle.write_text(g.replace("versionCode 30219","versionCode 30220",1).replace("versionName '3.0.219'","versionName '3.0.220'",1))
manifest=root/"app/src/main/AndroidManifest.xml"
m=manifest.read_text()
if m.count("iCE Onhand 3.0.219")!=1:raise SystemExit("3.0.219 manifest label missing")
manifest.write_text(m.replace("iCE Onhand 3.0.219","iCE Onhand 3.0.220",1))
s=main.read_text()
if s.count("Onhand Inventory 3.0.219")!=1:raise SystemExit("3.0.219 home label missing")
main.write_text(s.replace("Onhand Inventory 3.0.219","Onhand Inventory 3.0.220",1))

checks={
    "phone camera action distinct": 'button("Phone Camera",1)' in main.read_text(),
    "external scanner hint": 'barcode.setHint("External scanner or type barcode")' in main.read_text(),
    "barcode field ready on startup": 'barcode.post(this::focusBarcodeWithoutKeyboard)' in main.read_text(),
    "known scans highlight before quantity entry": 'if(existing!=null) {\n            lastBarcode=code;\n            applyFilter();' in main.read_text(),
    "highlighted row is scrolled into view": 'list.setSelection(i)' in main.read_text(),
    "location remembered per inventory": 'KEY_LOCATION_PREFIX+sessionId' in main.read_text(),
    "existing automatic increment retained": 'auto_increment_count' in main.read_text(),
    "shared scanning settings retained": 'UNKNOWN_BARCODE_MODE=' in main.read_text() and 'MAXIMUM_QTY=' in main.read_text(),
    "version labels": "versionName '3.0.220'" in gradle.read_text() and "iCE Onhand 3.0.220" in manifest.read_text() and "Onhand Inventory 3.0.220" in main.read_text(),
    "workflow markers": ".github/prepare_30220.py" in workflow.read_text() and "3.0.220" in workflow.read_text(),
}
failed=[k for k,v in checks.items() if not v]
if failed:raise SystemExit("3.0.220 validation failed: "+", ".join(failed))
print("Prepared iCE OnHand 3.0.220 with hardware-scanner focus, location persistence, and live count highlighting.")
