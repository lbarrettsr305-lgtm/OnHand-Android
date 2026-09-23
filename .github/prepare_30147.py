from pathlib import Path

base=Path('.github/prepare_30146.py')
exec(compile(base.read_text(),str(base),'exec'),{'__name__':'__main__','__file__':str(base)})

def rep(path,old,new):
    p=Path(path);s=p.read_text()
    if s.count(old)!=1:raise SystemExit('3.0.147 expected one target: '+old[:80])
    p.write_text(s.replace(old,new,1))

rep('app/build.gradle','versionCode 30146','versionCode 30147')
rep('app/build.gradle',"versionName '3.0.146'","versionName '3.0.147'")
rep('app/src/main/AndroidManifest.xml','iCE Onhand 3.0.146','iCE Onhand 3.0.147')
rep('app/src/main/AndroidManifest.xml','<application\n','<application\n        android:name=".OnHandApplication"\n')
rep('app/src/main/java/com/iceinventory/onhand/MainActivity.java','Onhand Inventory 3.0.146','Onhand Inventory 3.0.147')

Path('app/src/main/java/com/iceinventory/onhand/OnHandApplication.java').write_text('''package com.iceinventory.onhand;

import android.app.Activity;
import android.app.Application;
import android.content.Intent;
import android.graphics.Color;
import android.graphics.Typeface;
import android.os.Bundle;
import android.view.Gravity;
import android.view.View;
import android.view.ViewGroup;
import android.widget.Button;
import android.widget.FrameLayout;

/** A consistent Help shortcut on every app screen, including workflow steps. */
public final class OnHandApplication extends Application {
    @Override public void onCreate(){
        super.onCreate();
        registerActivityLifecycleCallbacks(new ActivityLifecycleCallbacks(){
            @Override public void onActivityResumed(Activity activity){attachHelp(activity);}
            @Override public void onActivityCreated(Activity activity,Bundle state){}
            @Override public void onActivityStarted(Activity activity){}
            @Override public void onActivityPaused(Activity activity){}
            @Override public void onActivityStopped(Activity activity){}
            @Override public void onActivitySaveInstanceState(Activity activity,Bundle state){}
            @Override public void onActivityDestroyed(Activity activity){}
        });
    }
    private void attachHelp(Activity activity){
        if(activity instanceof HelpActivity)return;
        View content=activity.findViewById(android.R.id.content);
        if(!(content instanceof FrameLayout))return;
        FrameLayout frame=(FrameLayout)content;
        if(frame.findViewWithTag("onhand_help_shortcut")!=null)return;
        Button help=new Button(activity);
        help.setTag("onhand_help_shortcut");
        help.setText("?");help.setTextSize(22);help.setTypeface(Typeface.DEFAULT,Typeface.BOLD);
        help.setTextColor(Color.BLACK);help.setBackgroundTintList(android.content.res.ColorStateList.valueOf(Color.rgb(255,193,7)));
        help.setContentDescription("Help for this screen");help.setElevation(dp(activity,8));
        help.setOnClickListener(v->{Intent intent=new Intent(activity,HelpActivity.class);
            intent.putExtra("help_screen",activity.getClass().getSimpleName());activity.startActivity(intent);});
        FrameLayout.LayoutParams params=new FrameLayout.LayoutParams(dp(activity,48),dp(activity,48),Gravity.TOP|Gravity.END);
        params.topMargin=dp(activity,4);params.rightMargin=dp(activity,5);
        frame.addView(help,params);
    }
    private int dp(Activity a,int value){return Math.round(value*a.getResources().getDisplayMetrics().density);}
}
''')

h='app/src/main/java/com/iceinventory/onhand/HelpActivity.java'
rep(h,
'''  root.addView(text("iCE OnHand Help / Instructions",25,Color.rgb(255,215,0)));
''',
'''  root.addView(text("iCE OnHand Help / Instructions",25,Color.rgb(255,215,0)));
  String screen=getIntent().getStringExtra("help_screen");
  if("BatchMergeActivity".equals(screen))section("This screen: combine counts","Select exported count files from each Count User for the same store. Check the users and totals before creating the combined report. Do not include an earlier combined file.");
  else if("FormatConfigActivity".equals(screen))section("This screen: TXT format","Match the barcode, description, price and quantity columns to the customer's TXT file. Check the preview before import; use the standard tab-delimited format when it matches.");
  else if("QuantityActivity".equals(screen))section("This screen: quantity","Enter the amount for the selected barcode and location. Verify the barcode before saving. Use the minus control on the main screen to subtract a mistaken quantity.");
  else if("MonthlyInventoryActivity".equals(screen))section("This screen: Petrosoft project","Work down the numbered steps. Import the customer Excel file, prepare and test the zero-quantity count file, share it with Count Users, then collect and verify their exports before creating the final reports.");
  else if("LiqPosInventoryActivity".equals(screen))section("This screen: LiqPOS project","Work down the numbered steps. Import the customer's DBF, prepare and test the zero-quantity count file, share it with Count Users, then verify combined exports and the client CSV.");
  else if("MainActivity".equals(screen))section("This screen: current count","Check the store name at the top before scanning. Use START / IMPORT for a new shared store file; choose REPLACE CURRENT INVENTORY after finishing and exporting any earlier count. The Master phone can share the app and current store from Options.");
  else if("ScanActivity".equals(screen))section("This screen: camera scan","Point the camera at one barcode and return to the main count screen to verify its description and quantity.");
''')
rep(h,
'''  section("8. Sharing With Count Users",
   "Every counting device must receive the same prepared OnHand file. Share it using Quick Share, Bluetooth, Wi-Fi, Google Drive, email, or another available Android sharing option.");''',
'''  section("8. Sharing With Count Users",
   "On the Master phone, open Options. For a new phone and store, choose APK + current store and send the ZIP; the recipient extracts it, installs the APK, then imports the TXT with REPLACE CURRENT INVENTORY. For an app update while a user is counting, send APK only and install over the existing app. For a new store with the app already installed, send the current count file only. The shared file has zero quantities and leaves the recipient a Count User. Do not uninstall to update; export the old count before replacing its store.");''')
print('Prepared iCE OnHand 3.0.147: Help shortcut on every app screen and contextual workflow instructions')
