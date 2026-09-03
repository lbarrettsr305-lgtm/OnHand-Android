from pathlib import Path
import runpy

# Preserve every approved 3.0.52 behavior first.
runpy.run_path('.github/prepare_3052.py', run_name='__main__')

# The 3.0.52 reveal used smoothScrollToPosition across 5,000+ rows, which looked
# like the list was going crazy after a scan. Jump directly to the matched row.
p=Path('app/src/main/java/com/iceinventory/onhand/MainActivity.java')
s=p.read_text()
old='''                list.post(()->list.smoothScrollToPosition(pos));\n'''
new='''                list.post(()->list.setSelection(pos));\n'''
if old not in s: raise SystemExit('3.0.53 target missing: smooth reveal')
s=s.replace(old,new,1)
p.write_text(s)

print('Prepared iCE Onhand 3.0.53: instant jump to matched yellow row')
