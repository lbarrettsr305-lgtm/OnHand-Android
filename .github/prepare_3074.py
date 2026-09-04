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

# Compact the Cases screen vertically so the full custom keypad fits better
# on Samsung/Android phones while preserving all controls and math.
rep('bar.setPadding(dp(8),dp(8),dp(8),dp(8));',
    'bar.setPadding(dp(8),dp(4),dp(8),dp(4));','top bar padding')
rep('bar.addView(back,new LinearLayout.LayoutParams(dp(58),dp(54)));',
    'bar.addView(back,new LinearLayout.LayoutParams(dp(54),dp(48)));','back button height')
rep('body.setPadding(dp(14),dp(10),dp(14),dp(16));',
    'body.setPadding(dp(12),dp(6),dp(12),dp(18));','body padding')
rep('card.setPadding(dp(12),dp(10),dp(12),dp(10));',
    'card.setPadding(dp(10),dp(5),dp(10),dp(5));','item card padding')
rep('TextView bc=text(barcode,18,Color.BLACK,true);',
    'TextView bc=text(barcode,16,Color.BLACK,true);','barcode text size')
rep('TextView ds=text(description.trim(),20,Color.BLACK,true);',
    'TextView ds=text(description.trim(),16,Color.BLACK,true);','description text size')
rep('TextView cq=text(String.format(Locale.US,"Current Qty: %d",current),17,Color.BLACK,true);',
    'TextView cq=text(String.format(Locale.US,"Current Qty: %d",current),15,Color.BLACK,true);','current quantity text size')

old_info='''        TextView info=text("ⓘ  Enter the quantity you want to add.\\n     You can enter a single amount\\n     or use multiply (Qty × Cases).",15,Color.rgb(0,60,180),true);\n        info.setPadding(dp(12),dp(10),dp(12),dp(10));\n'''
new_info='''        TextView info=text("ⓘ  Enter Qty per Case × Number of Cases",14,Color.rgb(0,60,180),true);\n        info.setPadding(dp(10),dp(6),dp(10),dp(6));\n'''
rep(old_info,new_info,'compact help text')
rep('infoLp.setMargins(0,dp(10),0,dp(10));',
    'infoLp.setMargins(0,dp(6),0,dp(6));','help margins')
rep('TextView l1=text("Quantity per Unit / Case",14,Color.rgb(0,50,170),true);',
    'TextView l1=text("Quantity per Unit / Case",12,Color.rgb(0,50,170),true);','left label size')
rep('TextView l2=text("Number of Cases",14,Color.rgb(0,50,170),true);',
    'TextView l2=text("Number of Cases",12,Color.rgb(0,50,170),true);','right label size')
rep('inputs.addView(perUnit,new LinearLayout.LayoutParams(0,dp(54),1));',
    'inputs.addView(perUnit,new LinearLayout.LayoutParams(0,dp(48),1));','per-unit input height')
rep('inputs.addView(times,new LinearLayout.LayoutParams(dp(60),dp(54)));',
    'inputs.addView(times,new LinearLayout.LayoutParams(dp(54),dp(48)));','times height')
rep('inputs.addView(cases,new LinearLayout.LayoutParams(0,dp(54),1));',
    'inputs.addView(cases,new LinearLayout.LayoutParams(0,dp(48),1));','cases input height')
rep('new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT,dp(56))',
    'new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT,dp(50))','add count height')
rep('keypad.setPadding(0,dp(10),0,0);',
    'keypad.setPadding(0,dp(4),0,dp(8));','keypad padding')
# Two keypad height occurrences: spacer and buttons.
s=s.replace('lp.width=0;lp.height=dp(54);lp.columnSpec=GridLayout.spec(GridLayout.UNDEFINED,1f);',
            'lp.width=0;lp.height=dp(46);lp.columnSpec=GridLayout.spec(GridLayout.UNDEFINED,1f);',2)
if s.count('lp.height=dp(46)') < 2:
    raise SystemExit('3.0.74 target missing: keypad heights')

# Fill the viewport and automatically reveal the lower keypad when the user
# selects Number of Cases. This avoids the bottom row being hidden off-screen.
rep('        ScrollView scroll=new ScrollView(this);\n',
    '        ScrollView scroll=new ScrollView(this);\n        scroll.setFillViewport(true);\n        scroll.setClipToPadding(false);\n','scroll behavior')
rep('cases.setOnFocusChangeListener((v,has)->{if(has){active=cases;hideKeyboard();}});',
    'cases.setOnFocusChangeListener((v,has)->{if(has){active=cases;hideKeyboard();scroll.post(()->scroll.fullScroll(View.FOCUS_DOWN));}});',
    'cases focus auto-scroll')

p.write_text(s)

# Advance app version only; scanner/count logic remains unchanged.
p=Path('app/src/main/java/com/iceinventory/onhand/MainActivity.java')
s=p.read_text()
rep_old='TextView app=text("Onhand Inventory 3.0.73",19,Color.WHITE,true);'
rep_new='TextView app=text("Onhand Inventory 3.0.74",19,Color.WHITE,true);'
if rep_old not in s: raise SystemExit('3.0.74 target missing: visible version')
s=s.replace(rep_old,rep_new,1)
p.write_text(s)

p=Path('app/build.gradle')
s=p.read_text().replace('versionCode 30073','versionCode 30074',1).replace("versionName '3.0.73'","versionName '3.0.74'",1)
if 'versionCode 30074' not in s or "versionName '3.0.74'" not in s:
    raise SystemExit('3.0.74 target missing: Gradle version')
p.write_text(s)

p=Path('app/src/main/AndroidManifest.xml')
s=p.read_text().replace('android:label="iCE Onhand 3.0.73"','android:label="iCE Onhand 3.0.74"',1)
p.write_text(s)

print('Prepared iCE Onhand 3.0.74: compact Cases screen + automatic keypad reveal; multiplication logic unchanged')
