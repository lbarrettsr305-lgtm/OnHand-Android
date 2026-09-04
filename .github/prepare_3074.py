from pathlib import Path
import runpy

# Preserve every working 3.0.73 feature first: proven scanning/counting,
# verified glossy logo, safe Replace/Append import, Internet Items With Pictures,
# Location Quantity Report, and the Cases multiplication logic.
runpy.run_path('.github/prepare_3073.py', run_name='__main__')

p=Path('app/src/main/java/com/iceinventory/onhand/QuantityActivity.java')
s=p.read_text()

def rep(old,new,label):
    global s
    if old not in s:
        raise SystemExit('3.0.74 target missing: '+label)
    s=s.replace(old,new,1)

# Keep the change intentionally narrow: the screen already uses a ScrollView,
# so make it fill the display and automatically reveal the bottom custom keypad
# whenever Number of Cases receives focus. The multiplication logic is untouched.
rep('        ScrollView scroll=new ScrollView(this);\n',
    '        ScrollView scroll=new ScrollView(this);\n        scroll.setFillViewport(true);\n        scroll.setClipToPadding(false);\n','scroll behavior')

rep('cases.setOnFocusChangeListener((v,has)->{if(has){active=cases;hideKeyboard();}});',
    'cases.setOnFocusChangeListener((v,has)->{if(has){active=cases;hideKeyboard();scroll.post(()->scroll.fullScroll(View.FOCUS_DOWN));}});',
    'cases focus auto-scroll')

# Recover vertical space without changing any buttons or their functions.
rep('body.setPadding(dp(14),dp(10),dp(14),dp(16));',
    'body.setPadding(dp(14),dp(6),dp(14),dp(12));','body padding')
rep('keypad.setPadding(0,dp(10),0,0);',
    'keypad.setPadding(0,dp(4),0,dp(8));','keypad padding')
rep('body.addView(add,new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT,dp(56)));',
    'body.addView(add,new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT,dp(50)));','add count height')

# There are exactly two 54dp keypad-cell height assignments after the chained
# preparations: one for blank spacer cells and one for active keypad buttons.
old_height='lp.width=0;lp.height=dp(54);lp.columnSpec=GridLayout.spec(GridLayout.UNDEFINED,1f);'
count=s.count(old_height)
if count!=2:
    raise SystemExit('3.0.74 target missing: expected two keypad heights, found '+str(count))
s=s.replace(old_height,
            'lp.width=0;lp.height=dp(46);lp.columnSpec=GridLayout.spec(GridLayout.UNDEFINED,1f);')

p.write_text(s)

# Advance app version only; scanner/count logic remains unchanged.
p=Path('app/src/main/java/com/iceinventory/onhand/MainActivity.java')
s=p.read_text()
old='TextView app=text("Onhand Inventory 3.0.73",19,Color.WHITE,true);'
new='TextView app=text("Onhand Inventory 3.0.74",19,Color.WHITE,true);'
if old not in s: raise SystemExit('3.0.74 target missing: visible version')
p.write_text(s.replace(old,new,1))

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

print('Prepared iCE Onhand 3.0.74: full Cases keypad reveal + compact keypad; multiplication logic unchanged')
