#!/usr/bin/env python3
from pathlib import Path
import runpy

root = Path(__file__).resolve().parents[1]
runpy.run_path(str(root / ".github" / "prepare_30187.py"), run_name="__main__")

gradle = root / "app" / "build.gradle"
s = gradle.read_text().replace("versionCode 30187", "versionCode 30188").replace("versionName '3.0.187'", "versionName '3.0.188'")
gradle.write_text(s)

manifest = root / "app" / "src" / "main" / "AndroidManifest.xml"
manifest.write_text(manifest.read_text().replace("iCE Onhand 3.0.187", "iCE Onhand 3.0.188"))

main = root / "app" / "src" / "main" / "java" / "com" / "iceinventory" / "onhand" / "MainActivity.java"
s = main.read_text().replace("Onhand Inventory 3.0.187", "Onhand Inventory 3.0.188")

old_focus = '''    private void focusQuantity() {
        qty.setShowSoftInputOnFocus(false);
        qty.requestFocus();
        qty.setSelection(qty.getText().length());
        qty.postDelayed(this::hideKeyboard,40);
        qty.postDelayed(this::hideKeyboard,180);
    }'''
new_focus = '''    private void focusQuantity() {
        qty.setShowSoftInputOnFocus(true);
        qty.requestFocus();
        qty.setSelection(qty.getText().length());
        setCountingKeyboardMode(true);
        qty.postDelayed(()->showKeyboard(qty),100);
    }'''
if s.count(old_focus) != 1:
    raise SystemExit("Quantity focus source not found")
s = s.replace(old_focus, new_focus, 1)

old_report = '''        Button totals=button("▥ Store Map",0);totals.setTextSize(11);totals.setOnClickListener(v->showLocationTotals());
        Button manualItem=button("＋ Add Item",1);manualItem.setTextSize(11);manualItem.setOnClickListener(v->beginManualItem());
        Button internet=button("◎ Internet Items",0);internet.setTextSize(11);internet.setOnClickListener(v->showInternetItems());
        reportBar.addView(totals,new LinearLayout.LayoutParams(0,dp(46),1));
        LinearLayout.LayoutParams rbp=new LinearLayout.LayoutParams(0,dp(46),1);rbp.setMargins(dp(4),0,0,0);
        reportBar.addView(manualItem,rbp);
        LinearLayout.LayoutParams ibp=new LinearLayout.LayoutParams(0,dp(46),1);ibp.setMargins(dp(4),0,0,0);
        reportBar.addView(internet,ibp);'''
new_report = '''        Button totals=button("▥ Store Map",0);totals.setTextSize(10);totals.setOnClickListener(v->showLocationTotals());
        Button recent=button("↶ Recent\\nCounts",0);recent.setTextSize(10);recent.setSingleLine(false);recent.setMaxLines(2);recent.setOnClickListener(v->showScanHistory());
        Button manualItem=button("＋ Add Item",1);manualItem.setTextSize(10);manualItem.setOnClickListener(v->beginManualItem());
        Button internet=button("◎ Internet\\nItems",0);internet.setTextSize(10);internet.setSingleLine(false);internet.setMaxLines(2);internet.setOnClickListener(v->showInternetItems());
        reportBar.addView(totals,new LinearLayout.LayoutParams(0,dp(46),1));
        LinearLayout.LayoutParams recentLp=new LinearLayout.LayoutParams(0,dp(46),1);recentLp.setMargins(dp(3),0,0,0);reportBar.addView(recent,recentLp);
        LinearLayout.LayoutParams rbp=new LinearLayout.LayoutParams(0,dp(46),1);rbp.setMargins(dp(3),0,0,0);
        reportBar.addView(manualItem,rbp);
        LinearLayout.LayoutParams ibp=new LinearLayout.LayoutParams(0,dp(46),1);ibp.setMargins(dp(3),0,0,0);
        reportBar.addView(internet,ibp);'''
if s.count(old_report) != 1:
    raise SystemExit("Main report button row source not found")
s = s.replace(old_report, new_report, 1)
main.write_text(s)

checks = {
    "version": "versionName '3.0.188'" in gradle.read_text(),
    "numeric keyboard": "qty.postDelayed(()->showKeyboard(qty),100)" in s,
    "quantity focus": "qty.setShowSoftInputOnFocus(true)" in s,
    "recent counts": 'button("↶ Recent\\nCounts",0)' in s and "recent.setOnClickListener(v->showScanHistory())" in s,
    "previous-location safety retained": "PREVIOUS LOCATION — READ ONLY" in s,
}
failed = [name for name, ok in checks.items() if not ok]
if failed:
    raise SystemExit("3.0.188 verification failed: " + ", ".join(failed))
print("Prepared iCE OnHand 3.0.188: automatic quantity keypad and visible Recent Counts")
