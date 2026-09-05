from pathlib import Path
import runpy

# Run the complete 3.0.80 preparation first, preserving every 3.0.79 feature.
runpy.run_path('.github/prepare_3080.py', run_name='__main__')

# Correct Java regex escaping for the optional dollar-price parser.
p=Path('app/src/main/java/com/iceinventory/onhand/BarcodeLookup.java')
s=p.read_text()
old=r'''        Matcher m=Pattern.compile("\$\s*([0-9]{1,4}(?:\.[0-9]{2})?)").matcher(text);'''
new=r'''        Matcher m=Pattern.compile("\\$\\s*([0-9]{1,4}(?:\\.[0-9]{2})?)").matcher(text);'''
if old not in s:
    raise SystemExit('3.0.80 release target missing: price regex')
s=s.replace(old,new,1)
p.write_text(s)

print('Prepared iCE Onhand 3.0.80 release: corrected web-price regex escaping')
