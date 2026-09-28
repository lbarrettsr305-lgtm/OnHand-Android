#!/usr/bin/env python3
from pathlib import Path
import runpy

root = Path(__file__).resolve().parents[1]
runpy.run_path(str(root / ".github" / "prepare_30183.py"), run_name="__main__")

gradle = root / "app" / "build.gradle"
s = gradle.read_text().replace("versionCode 30183", "versionCode 30184").replace("versionName '3.0.183'", "versionName '3.0.184'")
gradle.write_text(s)

manifest = root / "app" / "src" / "main" / "AndroidManifest.xml"
manifest.write_text(manifest.read_text().replace("iCE Onhand 3.0.183", "iCE Onhand 3.0.184"))

main = root / "app" / "src" / "main" / "java" / "com" / "iceinventory" / "onhand" / "MainActivity.java"
s = main.read_text().replace("Onhand Inventory 3.0.183", "Onhand Inventory 3.0.184")

old_bar = '''        sessionBar.addView(inventories,new LinearLayout.LayoutParams(0,dp(48),1));'''
new_bar = '''        if(hasAdminAccess())sessionBar.addView(inventories,new LinearLayout.LayoutParams(0,dp(48),1));'''
if s.count(old_bar) != 1:
    raise SystemExit("Session Current button source not found")
s = s.replace(old_bar, new_bar, 1)

old_options = '''    private void showOptions() {
        LinearLayout box=new LinearLayout(this);box.setOrientation(LinearLayout.VERTICAL);box.setPadding(dp(10),dp(4),dp(10),dp(4));box.setBackgroundColor(Color.rgb(8,24,27));'''
new_options = '''    private void showCounterOptions() {
        LinearLayout box=new LinearLayout(this);box.setOrientation(LinearLayout.VERTICAL);box.setPadding(dp(10),dp(8),dp(10),dp(8));box.setBackgroundColor(Color.rgb(8,24,27));
        Button unlock=button("🔒 UNLOCK MASTER TOOLS",2);unlock.setTypeface(Typeface.DEFAULT,Typeface.BOLD);
        box.addView(unlock,new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT,dp(58)));
        TextView counterTitle=text("COUNTER NAME",18,gold(),true);counterTitle.setPadding(dp(6),dp(16),0,dp(3));box.addView(counterTitle);
        String current=savedUserName();if(current.isEmpty())current="NOT SELECTED";
        TextView currentCounter=text("CURRENT COUNTER: "+current,18,Color.rgb(120,255,140),true);currentCounter.setPadding(dp(8),dp(6),dp(8),dp(6));box.addView(currentCounter);
        TextView instruction=text("Select the name of the person using this phone. The selected name is saved and used in the completed-count filename.",15,Color.WHITE,false);instruction.setPadding(dp(8),dp(5),dp(8),dp(14));box.addView(instruction);
        Button selectCounter=button("CHANGE / SELECT COUNTER NAME",1);selectCounter.setTypeface(Typeface.DEFAULT,Typeface.BOLD);selectCounter.setTextSize(16);
        box.addView(selectCounter,new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT,dp(64)));
        TextView protectedMessage=text("Scan, display, inventory, and administrative settings are protected. A Master can temporarily unlock them with the Master PIN.",13,Color.LTGRAY,false);protectedMessage.setPadding(dp(8),dp(16),dp(8),dp(8));box.addView(protectedMessage);
        Button help=button("❓ Help / Instructions",0);help.setOnClickListener(v->startActivity(new Intent(this,HelpActivity.class)));box.addView(help,new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT,dp(52)));
        ScrollView scroll=new ScrollView(this);scroll.setFillViewport(true);scroll.addView(box,new ScrollView.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT,ViewGroup.LayoutParams.WRAP_CONTENT));
        AlertDialog dialog=new AlertDialog.Builder(this).setTitle("Count User Options").setView(scroll).setPositiveButton("Done",null).create();
        unlock.setOnClickListener(v->{dialog.dismiss();unlockMasterTools();});
        selectCounter.setOnClickListener(v->{dialog.dismiss();promptUserName(false);});
        dialog.show();
    }

    private void showOptions() {
        if(!hasAdminAccess()){showCounterOptions();return;}
        LinearLayout box=new LinearLayout(this);box.setOrientation(LinearLayout.VERTICAL);box.setPadding(dp(10),dp(4),dp(10),dp(4));box.setBackgroundColor(Color.rgb(8,24,27));'''
if s.count(old_options) != 1:
    raise SystemExit("Options method source not found")
s = s.replace(old_options, new_options, 1)
main.write_text(s)

checks = {
    "version": "versionName '3.0.184'" in gradle.read_text(),
    "counter current removed": "if(hasAdminAccess())sessionBar.addView(inventories" in s,
    "count options guard": "if(!hasAdminAccess()){showCounterOptions();return;}" in s,
    "counter instruction": "Select the name of the person using this phone." in s,
    "counter selector": "CHANGE / SELECT COUNTER NAME" in s,
    "master unlock retained": "UNLOCK MASTER TOOLS" in s,
    "full settings retained": "Auto Convert to GTIN-14" in s and "Beep on Scan" in s,
}
failed = [name for name, ok in checks.items() if not ok]
if failed:
    raise SystemExit("3.0.184 verification failed: " + ", ".join(failed))
print("Prepared iCE OnHand 3.0.184: simplified protected Count User options")
