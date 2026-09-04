from pathlib import Path
import runpy

# Preserve every working 3.0.73 feature first: proven scanning/counting,
# verified glossy logo, safe Replace/Append import, Internet Items With Pictures,
# Location Quantity Report, and the Cases multiplication logic.
runpy.run_path('.github/prepare_3073.py', run_name='__main__')

# --- Cases screen: keep the entire custom keypad visible on the Samsung test phone. ---
p=Path('app/src/main/java/com/iceinventory/onhand/QuantityActivity.java')
s=p.read_text()

def rep(old,new,label):
    global s
    if old not in s:
        raise SystemExit('3.0.74 target missing: '+label)
    s=s.replace(old,new,1)

rep('        ScrollView scroll=new ScrollView(this);\n',
    '        ScrollView scroll=new ScrollView(this);\n        scroll.setFillViewport(true);\n        scroll.setClipToPadding(false);\n','scroll behavior')

rep('cases.setOnFocusChangeListener((v,has)->{if(has){active=cases;hideKeyboard();}});',
    'cases.setOnFocusChangeListener((v,has)->{if(has){active=cases;hideKeyboard();scroll.post(()->scroll.fullScroll(View.FOCUS_DOWN));}});',
    'cases focus auto-scroll')

# Recover vertical space without changing any calculator functions.
rep('body.setPadding(dp(14),dp(10),dp(14),dp(16));',
    'body.setPadding(dp(14),dp(6),dp(14),dp(12));','body padding')
rep('keypad.setPadding(0,dp(10),0,0);',
    'keypad.setPadding(0,dp(4),0,dp(8));','keypad padding')
rep('body.addView(addButton,new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT,dp(56)));',
    'body.addView(addButton,new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT,dp(50)));',
    'Cases add-count height')

# Make the app's custom calculator rows slightly shorter so the lower row fits.
old_height='lp.width=0;lp.height=dp(54);lp.columnSpec=GridLayout.spec(GridLayout.UNDEFINED,1f);'
count=s.count(old_height)
if count!=2:
    raise SystemExit('3.0.74 target missing: expected two keypad heights, found '+str(count))
s=s.replace(old_height,
            'lp.width=0;lp.height=dp(46);lp.columnSpec=GridLayout.spec(GridLayout.UNDEFINED,1f);')

p.write_text(s)

# --- Main screen: make the primary count action unmistakable. ---
p=Path('app/src/main/java/com/iceinventory/onhand/MainActivity.java')
s=p.read_text()
old_add='Button add=button("＋ Add Count",1);add.setTypeface(Typeface.DEFAULT,Typeface.BOLD);add.setTextSize(14);add.setSingleLine(true);add.setGravity(Gravity.CENTER);add.setPadding(dp(4),0,dp(4),0);add.setOnClickListener(v->addItem());'
new_add='Button add=button("SCAN COUNT\\nACCURATELY",1);add.setTypeface(Typeface.DEFAULT_BOLD,Typeface.BOLD);add.setTextSize(17);add.setSingleLine(false);add.setMaxLines(2);add.setGravity(Gravity.CENTER);add.setPadding(dp(4),0,dp(4),0);add.setContentDescription("Scan count accurately");add.setOnClickListener(v->addItem());'
if old_add not in s:
    raise SystemExit('3.0.74 target missing: main Add Count control')
s=s.replace(old_add,new_add,1)

# Give the primary action more width and height so it draws attention first.
if 'actionBar.addView(add,new LinearLayout.LayoutParams(0,dp(58),1.55f));' not in s:
    raise SystemExit('3.0.74 target missing: main Add Count layout')
s=s.replace('actionBar.addView(add,new LinearLayout.LayoutParams(0,dp(58),1.55f));',
            'actionBar.addView(add,new LinearLayout.LayoutParams(0,dp(72),1.85f));',1)

old='TextView app=text("Onhand Inventory 3.0.73",19,Color.WHITE,true);'
new='TextView app=text("Onhand Inventory 3.0.74",19,Color.WHITE,true);'
if old not in s:
    raise SystemExit('3.0.74 target missing: visible version')
s=s.replace(old,new,1)
p.write_text(s)

p=Path('app/build.gradle')
s=p.read_text().replace('versionCode 30073','versionCode 30074',1).replace("versionName '3.0.73'","versionName '3.0.74'",1)
if 'versionCode 30074' not in s or "versionName '3.0.74'" not in s:
    raise SystemExit('3.0.74 target missing: Gradle version')
p.write_text(s)

p=Path('app/src/main/AndroidManifest.xml')
s=p.read_text().replace('android:label="iCE Onhand 3.0.73"','android:label="iCE Onhand 3.0.74"',1)
if 'android:label="iCE Onhand 3.0.74"' not in s:
    raise SystemExit('3.0.74 target missing: manifest version')
p.write_text(s)

print('Prepared iCE Onhand 3.0.74: full Cases keypad reveal + prominent SCAN COUNT ACCURATELY control; scanner and multiplication logic unchanged')
