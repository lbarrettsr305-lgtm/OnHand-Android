from pathlib import Path

base=Path('.github/prepare_30129.py')
exec(compile(base.read_text(),str(base),'exec'),{'__name__':'__main__','__file__':str(base)})

p=Path('app/build.gradle')
g=p.read_text().replace('versionCode 30129','versionCode 30130',1).replace("versionName '3.0.129'","versionName '3.0.130'",1)
if 'versionCode 30130' not in g: raise SystemExit('3.0.130 Gradle target missing')
p.write_text(g)

p=Path('app/src/main/java/com/iceinventory/onhand/MainActivity.java')
s=p.read_text().replace('Onhand Inventory 3.0.129','Onhand Inventory 3.0.130',1)
needle='new AlertDialog.Builder(this).setTitle("Options")'
pos=s.find(needle)
if pos<0: raise SystemExit('3.0.130 Main Options dialog missing')
line_start=s.rfind('\n',0,pos)+1
addition='''        Button help=button("❓ Help / Instructions",0);
        help.setOnClickListener(v->startActivity(new Intent(this,HelpActivity.class)));
        box.addView(help,new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT,dp(52)));
'''
s=s[:line_start]+addition+s[line_start:]
p.write_text(s)

p=Path('app/src/main/java/com/iceinventory/onhand/MonthlyInventoryActivity.java')
s=p.read_text()
anchor=r'''        TextView profile=text("POS FORMAT PROFILE\nPetrosoft / CStoreOffice",16,Color.WHITE);profile.setPadding(0,dp(8),0,dp(10));root.addView(profile);'''
addition=anchor+'''
        Button help=button("❓ Help / Instructions");help.setOnClickListener(v->startActivity(new Intent(this,HelpActivity.class)));root.addView(help,params(52));'''
if anchor not in s: raise SystemExit('3.0.130 monthly Help anchor missing')
s=s.replace(anchor,addition,1)
p.write_text(s)

p=Path('app/src/main/java/com/iceinventory/onhand/LiqPosInventoryActivity.java')
s=p.read_text()
anchor='''  root.addView(text("LiqPOS Inventory",26,Color.rgb(255,215,0)));root.addView(text("POS FORMAT PROFILE — LiqPOS DBF / Barcode,Quantity CSV",15,Color.WHITE));'''
addition=anchor+'''
  Button help=button("❓ Help / Instructions");help.setOnClickListener(v->startActivity(new Intent(this,HelpActivity.class)));root.addView(help,params(52));'''
if anchor not in s: raise SystemExit('3.0.130 LiqPOS Help anchor missing')
s=s.replace(anchor,addition,1)
p.write_text(s)

help=Path('app/src/main/java/com/iceinventory/onhand/HelpActivity.java')
help.write_text(r'''package com.iceinventory.onhand;

import android.app.Activity;
import android.graphics.Color;
import android.os.Bundle;
import android.view.ViewGroup;
import android.widget.Button;
import android.widget.LinearLayout;
import android.widget.ScrollView;
import android.widget.TextView;

public final class HelpActivity extends Activity {
 private LinearLayout root;
 private int dp(int n){return Math.round(n*getResources().getDisplayMetrics().density);}
 private TextView text(String value,int size,int color){TextView t=new TextView(this);t.setText(value);t.setTextSize(size);t.setTextColor(color);t.setPadding(dp(4),dp(5),dp(4),dp(5));return t;}
 private void section(String title,String body){
  TextView h=text(title,19,Color.rgb(255,193,7));h.setPadding(dp(4),dp(18),dp(4),dp(4));root.addView(h);
  TextView b=text(body,16,Color.WHITE);b.setLineSpacing(0,1.15f);root.addView(b);
 }
 @Override public void onCreate(Bundle state){
  super.onCreate(state);
  ScrollView scroll=new ScrollView(this);root=new LinearLayout(this);root.setOrientation(LinearLayout.VERTICAL);root.setPadding(dp(16),dp(16),dp(16),dp(28));root.setBackgroundColor(Color.rgb(8,24,27));scroll.addView(root);
  root.addView(text("iCE OnHand Help / Instructions",25,Color.rgb(255,215,0)));

  section("1. Start a New Inventory",
   "From the main counting screen, tap ↓ START HERE — IMPORT.\n\nChoose the correct format:\n• Petrosoft Monthly Inventory\n• LiqPOS Inventory\n• Standard TXT Inventory\n\nDo not select a format that does not match the customer file.");

  section("2. Standard TXT Inventory",
   "Use this for a normal tab-delimited OnHand file. Select the file, confirm the store or session name, and verify a few barcodes before beginning the full count.");

  section("3. Petrosoft Monthly Inventory",
   "1. Enter the store name or file prefix.\n2. Import the Petrosoft Price Management Excel file.\n3. Create the OnHand tab-delimited count file.\n4. Load and test it on this device.\n5. Share the same count file with every user.\n6. After counting, select all user count files.\n7. Export the verified combined TXT, Petrosoft client Excel, and verification report.\n8. Close the project only after all required exports are saved.");

  section("4. LiqPOS Inventory",
   "1. Enter the store name or file prefix.\n2. Import the customer LiqPOS DBF file.\n3. Prepare the OnHand count file.\n4. Test scan on this device.\n5. Share the same file with all users.\n6. After counting, select all user count files.\n7. Export the verified combined TXT, LiqPOS CSV, and verification report.\n8. Close the project only after all required exports are saved.");

  section("5. Scanning and Quantities",
   "Scan or type the barcode in the yellow barcode field. Enter the quantity, then tap ADD QTY. Use the minus control when a quantity must be subtracted. Confirm the correct location before adding the quantity.");

  section("6. Locations",
   "Create a new location when moving to another area. Check Location Totals to confirm quantities by location. Location Detail reports retain the user, location, quantity, barcode, description, and price.");

  section("7. Sharing With Count Users",
   "Every counting device must receive the same prepared OnHand file. Share it using Quick Share, Bluetooth, Wi-Fi, Google Drive, email, or another available Android sharing option.");

  section("8. Combining User Counts",
   "After all users finish, collect each user's exported count file. Select all user count files together. Do not select an earlier COMBINED file, verification report, or customer upload file.");

  section("9. Exporting Reports",
   "Save the verified combined inventory first, then the customer upload or Excel file, and finally the verification report. Report filenames begin with the report or store name so they are easy to identify.");

  section("10. Return to Counting / Adjust",
   "Use ↩ Return to Counting / Adjust if a quantity, barcode, or location needs correction. Make the correction, return to the project workflow, reselect the corrected user files if required, and export fresh final reports.");

  section("11. Close a Project Safely",
   "Close the monthly or LiqPOS project only after every required file has been exported and checked. Closing removes the active workflow prompt but does not delete the files already saved on the device.");

  Button done=new Button(this);done.setText("Close Help");done.setTextSize(17);done.setTextColor(Color.BLACK);done.setBackgroundColor(Color.rgb(255,193,7));done.setOnClickListener(v->finish());
  LinearLayout.LayoutParams lp=new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT,dp(56));lp.setMargins(0,dp(20),0,0);root.addView(done,lp);
  setContentView(scroll);
 }
}
''')

p=Path('app/src/main/AndroidManifest.xml')
m=p.read_text().replace('iCE Onhand 3.0.129','iCE Onhand 3.0.130',1)
anchor='''    </application>'''
addition='''        <activity android:name=".HelpActivity" android:exported="false" android:screenOrientation="unspecified" />
'''
if '.HelpActivity' not in m:m=m.replace(anchor,addition+anchor,1)
if 'iCE Onhand 3.0.130' not in m: raise SystemExit('3.0.130 manifest version missing')
p.write_text(m)

print('Prepared iCE Onhand 3.0.130: section-by-section in-app Help manual')
