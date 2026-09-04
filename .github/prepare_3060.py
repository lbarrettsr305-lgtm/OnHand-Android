from pathlib import Path
import runpy

# Preserve every working 3.0.59 feature, including the proven 3.0.58 scanner behavior.
runpy.run_path('.github/prepare_3059.py', run_name='__main__')

p = Path('app/src/main/java/com/iceinventory/onhand/MainActivity.java')
s = p.read_text()

# Smaller/older phones can run out of vertical room after the User/Export and
# Zero-passcode controls were added. Make the Options content scrollable so the
# Unknown Barcode Behavior control is always reachable without changing the
# scanner, inventory, export, or passcode behavior.
old = '''        new AlertDialog.Builder(this).setTitle("Options").setView(box).setPositiveButton("Done",null).show();\n'''
new = '''        ScrollView optionsScroll=new ScrollView(this);\n        optionsScroll.setFillViewport(true);\n        optionsScroll.setVerticalScrollBarEnabled(true);\n        optionsScroll.addView(box,new ScrollView.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT,ViewGroup.LayoutParams.WRAP_CONTENT));\n        new AlertDialog.Builder(this).setTitle("Options").setView(optionsScroll).setPositiveButton("Done",null).show();\n'''
if old not in s:
    raise SystemExit('3.0.60 target missing: Options dialog view')
s = s.replace(old, new, 1)

p.write_text(s)
print('Prepared iCE Onhand 3.0.60: responsive scrollable Options dialog for smaller displays')
