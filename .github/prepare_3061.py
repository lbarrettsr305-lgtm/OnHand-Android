from pathlib import Path
import runpy

# Preserve every working 3.0.60 feature, including the proven 3.0.58 scanner,
# 3.0.59 export/passcode behavior, and the 3.0.60 scrollable Options dialog.
runpy.run_path('.github/prepare_3060.py', run_name='__main__')

p = Path('app/src/main/java/com/iceinventory/onhand/MainActivity.java')
s = p.read_text()

# On narrower phones the third action button can collapse until only the plus
# sign is obvious. Keep the same action and vertical footprint, but give the
# New Location control enough width and a clear two-line label.
old = '''        LinearLayout actionBar=new LinearLayout(this);actionBar.setOrientation(LinearLayout.HORIZONTAL);\n        Button add=button("＋ Add Count",1);add.setTypeface(Typeface.DEFAULT,Typeface.BOLD);add.setOnClickListener(v->addItem());\n        Button multiply=button("× Cases",2);multiply.setTypeface(Typeface.DEFAULT,Typeface.BOLD);multiply.setOnClickListener(v->launchCurrentMultiply());\n        Button addLoc=button("＋ Location",0);addLoc.setOnClickListener(v->addLocation());\n        actionBar.addView(add,new LinearLayout.LayoutParams(0,dp(52),2));\n        LinearLayout.LayoutParams ml=new LinearLayout.LayoutParams(0,dp(52),1);ml.setMargins(dp(5),0,dp(5),0);\n        actionBar.addView(multiply,ml);\n        actionBar.addView(addLoc,new LinearLayout.LayoutParams(0,dp(52),1));\n        root.addView(actionBar);\n'''
new = '''        LinearLayout actionBar=new LinearLayout(this);actionBar.setOrientation(LinearLayout.HORIZONTAL);\n        Button add=button("＋ Add Count",1);add.setTypeface(Typeface.DEFAULT,Typeface.BOLD);add.setOnClickListener(v->addItem());\n        Button multiply=button("× Cases",2);multiply.setTypeface(Typeface.DEFAULT,Typeface.BOLD);multiply.setOnClickListener(v->launchCurrentMultiply());\n        Button addLoc=button("＋ New\\nLocation",0);\n        addLoc.setTextSize(11);addLoc.setGravity(Gravity.CENTER);addLoc.setPadding(dp(2),0,dp(2),0);\n        addLoc.setOnClickListener(v->addLocation());\n        actionBar.addView(add,new LinearLayout.LayoutParams(0,dp(52),1.35f));\n        LinearLayout.LayoutParams ml=new LinearLayout.LayoutParams(0,dp(52),1.0f);ml.setMargins(dp(4),0,dp(4),0);\n        actionBar.addView(multiply,ml);\n        actionBar.addView(addLoc,new LinearLayout.LayoutParams(0,dp(52),1.35f));\n        root.addView(actionBar);\n'''
if old not in s:
    raise SystemExit('3.0.61 target missing: main action bar')
s = s.replace(old, new, 1)

p.write_text(s)
print('Prepared iCE Onhand 3.0.61: visible New Location button + scrollable Options on smaller displays')
