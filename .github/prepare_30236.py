#!/usr/bin/env python3
"""3.0.236: readable main-only button and explicit external Bluetooth / camera scanner choices."""
from pathlib import Path
import runpy

root=Path(__file__).resolve().parents[1]
workflow=root/".github/workflows/build-apk.yml"
w=workflow.read_text()
markers=[
    ("Prepare and verify 3.0.236 Bluetooth location scanning and readable buttons","Prepare and verify 3.0.235 main-location-only counting",1),
    (".github/prepare_30236.py",".github/prepare_30235.py",1),
    ("iCE-Onhand-Inventory-3.0.236","iCE-Onhand-Inventory-3.0.235",4),
]
for new,old,expected in markers:
    if w.count(new)!=expected:
        raise SystemExit("3.0.236 workflow marker mismatch: "+new)
    w=w.replace(new,old)
workflow.write_text(w)
runpy.run_path(str(root/".github/prepare_30235.py"),run_name="__main__")
w=workflow.read_text()
for new,old,expected in markers:
    if w.count(old)!=expected:
        raise SystemExit("3.0.235 workflow marker restore mismatch: "+old)
    w=w.replace(old,new)
workflow.write_text(w)

gradle=root/"app/build.gradle"
g=gradle.read_text()
if g.count("versionCode 30235")!=1 or g.count("versionName '3.0.235'")!=1:
    raise SystemExit("3.0.235 Gradle version absent")
gradle.write_text(g.replace("versionCode 30235","versionCode 30236",1).replace("versionName '3.0.235'","versionName '3.0.236'",1))
manifest=root/"app/src/main/AndroidManifest.xml"
m=manifest.read_text()
if m.count("iCE Onhand 3.0.235")!=1:
    raise SystemExit("3.0.235 manifest version absent")
manifest.write_text(m.replace("iCE Onhand 3.0.235","iCE Onhand 3.0.236",1))

main=root/"app/src/main/java/com/iceinventory/onhand/MainActivity.java"
s=main.read_text()
def once(old,new,label):
    global s
    hits=s.count(old)
    if hits!=1:
        raise SystemExit("3.0.236 "+label+" unexpected source matches: "+str(hits))
    s=s.replace(old,new,1)

once("Onhand Inventory 3.0.235","Onhand Inventory 3.0.236","visible version")

# Bluetooth HID scanners type into whichever location field is focused.
# Do not launch the camera unless the user explicitly chooses Phone Camera.
# Tapping inside a field restores the soft keyboard for manual entry.
once('''        Button scanMain=button("SCAN MAIN LOCATION LABEL",1);
        scanMain.setOnClickListener(v->{
            locationScanInput=mainOnlyInput;
            pendingLocationScanEntry=mainOnlyInput;
            startActivityForResult(new Intent(this,ScanActivity.class),REQ_SCAN_LOCATION);
        });
        panel.addView(scanMain,new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT,dp(48)));''',
'''        mainOnlyInput.setShowSoftInputOnFocus(false);
        mainOnlyInput.setOnTouchListener((view,event)->{
            if(event.getAction()==android.view.MotionEvent.ACTION_DOWN)
                mainOnlyInput.setShowSoftInputOnFocus(true);
            return false;
        });
        TextView scannerHelp=text("BLUETOOTH: scan directly into the main location field. PHONE CAMERA: tap the camera button. To type, tap the field.",13,Color.WHITE,false);
        panel.addView(scannerHelp);
        Button bluetoothMain=button("BLUETOOTH SCANNER — MAIN LOCATION",1);
        bluetoothMain.setTextSize(13);
        bluetoothMain.setOnClickListener(v->{
            locationScanInput=mainOnlyInput;
            mainOnlyInput.setShowSoftInputOnFocus(false);
            mainOnlyInput.requestFocus();
            mainOnlyInput.setSelection(mainOnlyInput.length());
            hideKeyboard();
            toast("Bluetooth ready — scan your main location label.");
        });
        panel.addView(bluetoothMain,new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT,dp(55)));
        Button scanMain=button("PHONE CAMERA — MAIN LOCATION",1);
        scanMain.setTextSize(13);
        scanMain.setOnClickListener(v->{
            locationScanInput=mainOnlyInput;
            pendingLocationScanEntry=mainOnlyInput;
            startActivityForResult(new Intent(this,ScanActivity.class),REQ_SCAN_LOCATION);
        });
        panel.addView(scanMain,new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT,dp(55)));''',
"main location scanner choice")

# Make both lines fully readable; the entire dialog is scrollable since 3.0.235.
once('''        Button useMain=button("USE MAIN LOCATION ONLY — START COUNTING",1);
        useMain.setOnClickListener(v->submitMainOnlyLocation(mainOnlyInput.getText().toString()));
        panel.addView(useMain,new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT,dp(56)));''',
'''        Button useMain=button("USE MAIN LOCATION ONLY\nSTART COUNTING",1);
        useMain.setSingleLine(false);
        useMain.setMaxLines(2);
        useMain.setTextSize(14);
        useMain.setGravity(android.view.Gravity.CENTER);
        useMain.setPadding(dp(6),dp(7),dp(6),dp(7));
        useMain.setOnClickListener(v->submitMainOnlyLocation(mainOnlyInput.getText().toString()));
        panel.addView(useMain,new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT,dp(76)));''',
"full main location button text")

# Keep the existing exact-location camera handler but give the external scanner
# its own explicit focus action, so it never opens the internal scanner by mistake.
once('''        Button camera=button("Scan Location Label",1);''',
'''        entry.setOnTouchListener((view,event)->{
            if(event.getAction()==android.view.MotionEvent.ACTION_DOWN)
                entry.setShowSoftInputOnFocus(true);
            return false;
        });
        Button bluetoothExact=button("BLUETOOTH SCANNER — EXACT LOCATION",1);
        bluetoothExact.setTextSize(13);
        bluetoothExact.setOnClickListener(v->{
            locationScanInput=entry;
            entry.setShowSoftInputOnFocus(false);
            entry.requestFocus();
            entry.setSelection(entry.length());
            hideKeyboard();
            toast("Bluetooth ready — scan the exact location label.");
        });
        panel.addView(bluetoothExact,new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT,dp(55)));
        Button camera=button("PHONE CAMERA — EXACT LOCATION",1);
        camera.setTextSize(13);''',
"exact location scanner choice")

# Default focus goes to external scanner/main location. Touching a field can
# still open the keyboard for typed input; no camera is triggered automatically.
once('''        locationDialog.show();
    }
''',
'''        locationDialog.show();
        mainOnlyInput.setShowSoftInputOnFocus(false);
        mainOnlyInput.requestFocus();
        locationScanInput=mainOnlyInput;
        android.view.Window locationWindow=locationDialog.getWindow();
        if(locationWindow!=null)
            locationWindow.setSoftInputMode(android.view.WindowManager.LayoutParams.SOFT_INPUT_STATE_ALWAYS_HIDDEN);
    }
''',
"default Bluetooth focus without phone camera")

main.write_text(s)
checks={
    "version": ("versionName '3.0.236'" in gradle.read_text() and
                "iCE Onhand 3.0.236" in manifest.read_text() and
                "Onhand Inventory 3.0.236" in s),
    "main Bluetooth focus": 'bluetoothMain.setOnClickListener' in s and
                            'locationScanInput=mainOnlyInput;' in s,
    "main camera manual": 'Button scanMain=button("PHONE CAMERA — MAIN LOCATION",1);' in s and
                          'startActivityForResult(new Intent(this,ScanActivity.class),REQ_SCAN_LOCATION);' in s,
    "exact choice": 'Button bluetoothExact=' in s and
                    'Button camera=button("PHONE CAMERA — EXACT LOCATION",1);' in s,
    "complete button": 'USE MAIN LOCATION ONLY\\nSTART COUNTING' in s and
                       'ViewGroup.LayoutParams.MATCH_PARENT,dp(76)' in s,
    "soft keyboard manual": 'mainOnlyInput.setOnTouchListener' in s and 'entry.setOnTouchListener' in s,
    "Bluetooth first": 'mainOnlyInput.requestFocus();' in s and
                       'SOFT_INPUT_STATE_ALWAYS_HIDDEN' in s,
    "all inventory templates kept": 'Fleet Feet Client — Barcode + Qty (No Headers)' in s and
                                    'Victoria' in s and 'Petrosoft' in s,
    "location persistence": 'rememberConfirmedLocation(n)' in s,
    "location selection": 'submitMainOnlyLocation(mainOnlyInput.getText().toString())' in s and
                          'submitCountingLocation(entry.getText().toString().trim())' in s,
    "workflow": '.github/prepare_30236.py' in workflow.read_text() and '3.0.236' in workflow.read_text()
}
bad=[key for key,value in checks.items() if not value]
if bad:
    raise SystemExit("3.0.236 checks failed: "+", ".join(bad))
print("Prepared iCE OnHand 3.0.236: full-height Use Main Location, default Bluetooth focus, separate Phone Camera choices.")
