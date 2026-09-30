#!/usr/bin/env python3
from pathlib import Path
import runpy

root = Path(__file__).resolve().parents[1]
runpy.run_path(str(root / ".github" / "prepare_30185.py"), run_name="__main__")

gradle = root / "app" / "build.gradle"
s = gradle.read_text().replace("versionCode 30185", "versionCode 30186").replace("versionName '3.0.185'", "versionName '3.0.186'")
gradle.write_text(s)

manifest = root / "app" / "src" / "main" / "AndroidManifest.xml"
manifest.write_text(manifest.read_text().replace("iCE Onhand 3.0.185", "iCE Onhand 3.0.186"))

main = root / "app" / "src" / "main" / "java" / "com" / "iceinventory" / "onhand" / "MainActivity.java"
s = main.read_text().replace("Onhand Inventory 3.0.185", "Onhand Inventory 3.0.186")

old_instruction = '''        TextView instructions=text("First choose the MAIN LOCATION. Then choose the exact aisle side or subsection. A location with only one choice is selected automatically.",16,Color.WHITE,false);'''
new_instruction = '''        boolean changingLocation=confirmedLocationSession==sessionId&&!confirmedLocation.isEmpty();
        TextView instructions=text(changingLocation?"Your current MAIN LOCATION is selected below. Choose the new exact location. Use the first list only if you need to change the main location.":"First choose the MAIN LOCATION. Then choose the exact aisle side or subsection. A location with only one choice is selected automatically.",16,Color.WHITE,false);'''
if s.count(old_instruction) != 1:
    raise SystemExit("Location instruction source not found")
s = s.replace(old_instruction, new_instruction, 1)

old_listener_end = '''        childChoice.setOnItemSelectedListener(new android.widget.AdapterView.OnItemSelectedListener(){
            public void onNothingSelected(android.widget.AdapterView<?> parent){}
            public void onItemSelected(android.widget.AdapterView<?> parent,android.view.View view,int pos,long id){if(pos>0)entry.setText(children.get(pos));}
        });

        Button camera=button("Scan Location Label",1);'''
new_listener_end = '''        childChoice.setOnItemSelectedListener(new android.widget.AdapterView.OnItemSelectedListener(){
            public void onNothingSelected(android.widget.AdapterView<?> parent){}
            public void onItemSelected(android.widget.AdapterView<?> parent,android.view.View view,int pos,long id){if(pos>0)entry.setText(children.get(pos));}
        });

        if(changingLocation){
            String currentParent=locationParent(confirmedLocation);
            int parentIndex=parents.indexOf(currentParent);
            if(parentIndex>0)parentChoice.setSelection(parentIndex);
        }

        Button camera=button("Scan Location Label",1);'''
if s.count(old_listener_end) != 1:
    raise SystemExit("Location selector listener source not found")
s = s.replace(old_listener_end, new_listener_end, 1)
main.write_text(s)

checks = {
    "version": "versionName '3.0.186'" in gradle.read_text(),
    "change detection": "boolean changingLocation=confirmedLocationSession==sessionId" in s,
    "parent remembered": "parentChoice.setSelection(parentIndex)" in s,
    "clear guidance": "Your current MAIN LOCATION is selected below" in s,
}
failed = [name for name, ok in checks.items() if not ok]
if failed:
    raise SystemExit("3.0.186 verification failed: " + ", ".join(failed))
print("Prepared iCE OnHand 3.0.186: remember current main location when changing exact location")
