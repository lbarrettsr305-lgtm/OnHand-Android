from pathlib import Path
import runpy
import re

# Preserve every working 3.0.74 feature first, then correct the UI misunderstanding:
# SCAN COUNT ACCURATELY belongs under the logo, the main action is ADD QTY,
# and the Cases keypad must remain fully visible above the phone navigation area.
runpy.run_path('.github/prepare_3074.py', run_name='__main__')

# --- Main screen corrections. ---
p=Path('app/src/main/java/com/iceinventory/onhand/MainActivity.java')
s=p.read_text()

def rep(old,new,label):
    global s
    if old not in s:
        raise SystemExit('3.0.75 target missing: '+label)
    s=s.replace(old,new,1)

# Move the approved blue motto under the glossy logo. Earlier prep versions have
# used different LayoutParams variable names, so match only the stable header add.
logo_pat=r'header\.addView\(logo\s*,\s*[A-Za-z_][A-Za-z0-9_]*\);'
logo_match=re.search(logo_pat,s)
if not logo_match:
    raise SystemExit('3.0.75 target missing: logo header add')
new_logo='''LinearLayout brandMark=new LinearLayout(this);
        brandMark.setOrientation(LinearLayout.VERTICAL);
        brandMark.setGravity(Gravity.CENTER_HORIZONTAL);
        LinearLayout.LayoutParams brandLogoLp=new LinearLayout.LayoutParams(dp(96),dp(84));
        brandMark.addView(logo,brandLogoLp);
        TextView accuracy=text("SCAN COUNT ACCURATELY",9,Color.rgb(35,120,255),true);
        accuracy.setGravity(Gravity.CENTER);
        accuracy.setSingleLine(true);
        accuracy.setTextScaleX(0.84f);
        brandMark.addView(accuracy,new LinearLayout.LayoutParams(dp(112),dp(18)));
        LinearLayout.LayoutParams brandLp=new LinearLayout.LayoutParams(dp(112),dp(104));
        brandLp.setMargins(0,0,dp(4),0);
        header.addView(brandMark,brandLp);'''
s=s[:logo_match.start()]+new_logo+s[logo_match.end():]

# Restore the main action to ADD QTY and return it to the green inventory action style.
old_add='Button add=button("SCAN COUNT\\nACCURATELY",1);add.setTypeface(Typeface.DEFAULT_BOLD,Typeface.BOLD);add.setTextSize(17);add.setTextColor(Color.WHITE);add.setBackgroundColor(Color.rgb(15,70,205));add.setSingleLine(false);add.setMaxLines(2);add.setGravity(Gravity.CENTER);add.setPadding(dp(4),0,dp(4),0);add.setContentDescription("Scan count accurately");add.setOnClickListener(v->addItem());'
new_add='Button add=button("＋ ADD QTY",1);add.setTypeface(Typeface.DEFAULT_BOLD,Typeface.BOLD);add.setTextSize(16);add.setSingleLine(true);add.setGravity(Gravity.CENTER);add.setPadding(dp(4),0,dp(4),0);add.setContentDescription("Add quantity");add.setOnClickListener(v->addItem());'
rep(old_add,new_add,'restore ADD QTY')
rep('actionBar.addView(add,new LinearLayout.LayoutParams(0,dp(72),1.85f));',
    'actionBar.addView(add,new LinearLayout.LayoutParams(0,dp(58),1.55f));',
    'restore main action size')
rep('TextView app=text("Onhand Inventory 3.0.74",19,Color.WHITE,true);',
    'TextView app=text("Onhand Inventory 3.0.75",19,Color.WHITE,true);',
    'visible version')
p.write_text(s)

# --- Cases screen: guarantee the entire custom keypad can clear the Samsung nav bar. ---
p=Path('app/src/main/java/com/iceinventory/onhand/QuantityActivity.java')
s=p.read_text()

# Extra bottom scroll room lets the final 0/00 row move above the Android nav bar.
old='body.setPadding(dp(14),dp(6),dp(14),dp(12));'
if old not in s: raise SystemExit('3.0.75 target missing: Cases body padding')
s=s.replace(old,'body.setPadding(dp(14),dp(6),dp(14),dp(56));',1)

old='keypad.setPadding(0,dp(4),0,dp(8));'
if old not in s: raise SystemExit('3.0.75 target missing: Cases keypad padding')
s=s.replace(old,'keypad.setPadding(0,dp(4),0,dp(12));',1)

old='body.addView(addButton,new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT,dp(50)));'
if old not in s: raise SystemExit('3.0.75 target missing: Cases add-count height')
s=s.replace(old,'body.addView(addButton,new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT,dp(46)));',1)

old='lp.width=0;lp.height=dp(46);lp.columnSpec=GridLayout.spec(GridLayout.UNDEFINED,1f);'
count=s.count(old)
if count!=2:
    raise SystemExit('3.0.75 target missing: expected two 3.0.74 keypad heights, found '+str(count))
s=s.replace(old,'lp.width=0;lp.height=dp(40);lp.columnSpec=GridLayout.spec(GridLayout.UNDEFINED,1f);')

old='cases.setOnFocusChangeListener((v,has)->{if(has){active=cases;hideKeyboard();scroll.post(()->scroll.fullScroll(View.FOCUS_DOWN));}});'
new='cases.setOnFocusChangeListener((v,has)->{if(has){active=cases;hideKeyboard();scroll.postDelayed(()->scroll.fullScroll(View.FOCUS_DOWN),120);}});cases.setOnClickListener(v->{active=cases;hideKeyboard();scroll.postDelayed(()->scroll.fullScroll(View.FOCUS_DOWN),120);});'
if old not in s: raise SystemExit('3.0.75 target missing: Cases focus scrolling')
s=s.replace(old,new,1)
p.write_text(s)

# Advance installable Android version.
p=Path('app/build.gradle')
s=p.read_text().replace('versionCode 30074','versionCode 30075',1).replace("versionName '3.0.74'","versionName '3.0.75'",1)
if 'versionCode 30075' not in s or "versionName '3.0.75'" not in s:
    raise SystemExit('3.0.75 target missing: Gradle version')
p.write_text(s)

p=Path('app/src/main/AndroidManifest.xml')
s=p.read_text().replace('android:label="iCE Onhand 3.0.74"','android:label="iCE Onhand 3.0.75"',1)
if 'android:label="iCE Onhand 3.0.75"' not in s:
    raise SystemExit('3.0.75 target missing: manifest version')
p.write_text(s)

print('Prepared iCE Onhand 3.0.75: blue SCAN COUNT ACCURATELY motto under logo + restored ADD QTY + full Cases keypad clearance')
