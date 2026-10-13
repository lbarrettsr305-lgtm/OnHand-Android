#!/usr/bin/env python3
from pathlib import Path
import runpy

script_dir = Path(__file__).resolve().parent
root = script_dir.parent if script_dir.name == ".github" else script_dir
workflow = root / ".github/workflows/build-apk.yml"

# Recreate the visible 3.0.216 format chooser, then render choices as buttons.
w = workflow.read_text()
for new, old in [
    ("Prepare and verify 3.0.217 import format buttons", "Prepare and verify 3.0.216 import chooser display"),
    (".github/prepare_30217.py", ".github/prepare_30216.py"),
    ("iCE-Onhand-Inventory-3.0.217", "iCE-Onhand-Inventory-3.0.216"),
]:
    if new not in w:
        raise SystemExit("3.0.217 workflow seed missing: " + new)
    w = w.replace(new, old)
workflow.write_text(w)
runpy.run_path(str(root / ".github/prepare_30216.py"), run_name="__main__")

w = workflow.read_text()
for old, new in [
    ("Prepare and verify 3.0.216 import chooser display", "Prepare and verify 3.0.217 import format buttons"),
    (".github/prepare_30216.py", ".github/prepare_30217.py"),
    ("iCE-Onhand-Inventory-3.0.216", "iCE-Onhand-Inventory-3.0.217"),
]:
    if old not in w:
        raise SystemExit("3.0.216 workflow marker missing: " + old)
    w = w.replace(old, new)
workflow.write_text(w)

main = root / "app/src/main/java/com/iceinventory/onhand/MainActivity.java"
s = main.read_text()
start = s.find("    private void showStandardImportFormatDialog(){")
end = s.find("\n    private void startImportFormatFlow()", start)
if start < 0 or end < 0:
    raise SystemExit("Import format dialog boundaries missing")
old_method = s[start:end]
new_method = '''    private void showStandardImportFormatDialog(){
        LinearLayout choices=new LinearLayout(this);choices.setOrientation(LinearLayout.VERTICAL);
        choices.setPadding(dp(12),dp(4),dp(12),dp(4));
        TextView instruction=text("Choose the button matching the columns in the customer file. The file picker opens next.",15,Color.WHITE,false);
        instruction.setPadding(dp(4),dp(4),dp(4),dp(10));choices.addView(instruction);
        AlertDialog dialog=new AlertDialog.Builder(this).setTitle("Choose Import Format").setView(choices)
                .setNegativeButton("CANCEL",null).create();
        String[] labels={
                "USE SAVED FORMAT\\nUse the current setup",
                "FLEET FEET\\nBarcode • Item Number • Description • Size",
                "VICTORIA\\nQty • Barcode • Description • Item Number • Location",
                "GENERIC POS\\nQty • Barcode • Description • Price"
        };
        String[] orders={null,"barcode,item_number,description,size","quantity,barcode,description,item_number,location","quantity,barcode,description,price"};
        for(int i=0;i<labels.length;i++){
            final int selected=i;
            Button choice=button(labels[i],1);choice.setAllCaps(false);choice.setTextSize(15);
            choice.setSingleLine(false);choice.setMaxLines(2);choice.setGravity(Gravity.CENTER);
            LinearLayout.LayoutParams lp=new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT,dp(64));
            lp.setMargins(0,0,0,dp(6));choices.addView(choice,lp);
            choice.setOnClickListener(v->{
                if(orders[selected]!=null)prefs().edit().putString("import_field_order",orders[selected]).apply();
                dialog.dismiss();importCsv();
            });
        }
        dialog.show();
    }
'''
s = s[:start] + new_method + s[end:]
main.write_text(s)

gradle = root / "app/build.gradle"
g = gradle.read_text()
if "versionCode 30216" not in g or "versionName '3.0.216'" not in g:
    raise SystemExit("3.0.216 Gradle version missing")
gradle.write_text(g.replace("versionCode 30216", "versionCode 30217", 1).replace("versionName '3.0.216'", "versionName '3.0.217'", 1))

manifest = root / "app/src/main/AndroidManifest.xml"
m = manifest.read_text()
if m.count("iCE Onhand 3.0.216") != 1:
    raise SystemExit("3.0.216 app label missing")
manifest.write_text(m.replace("iCE Onhand 3.0.216", "iCE Onhand 3.0.217", 1))

if s.count("Onhand Inventory 3.0.216") != 1:
    raise SystemExit("3.0.216 home label missing")
s = s.replace("Onhand Inventory 3.0.216", "Onhand Inventory 3.0.217", 1)
main.write_text(s)

checks = {
    "chooser uses actual button controls": 'Button choice=button(labels[i],1)' in new_method,
    "Fleet Feet columns appear on button": "FLEET FEET\\nBarcode • Item Number • Description • Size" in new_method,
    "button choice launches file picker": "dialog.dismiss();importCsv();" in new_method,
    "all four format choices exist": all(x in new_method for x in ["USE SAVED FORMAT", "FLEET FEET", "VICTORIA", "GENERIC POS"]),
    "release labels": "versionName '3.0.217'" in gradle.read_text() and "iCE Onhand 3.0.217" in manifest.read_text() and "Onhand Inventory 3.0.217" in s,
    "workflow points to release": ".github/prepare_30217.py" in workflow.read_text() and "3.0.217" in workflow.read_text(),
}
failed = [name for name, passed in checks.items() if not passed]
if failed:
    raise SystemExit("3.0.217 validation failed: " + ", ".join(failed))
print("Prepared iCE OnHand 3.0.217: import formats are large labeled buttons followed by file selection.")
