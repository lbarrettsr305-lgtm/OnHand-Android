from pathlib import Path
import re

# Execute the 3.0.82 protection patch with one compatibility adjustment for the
# addOrIncrementAt method produced by the older preparation chain. The first CI
# run proved that the protection script reached this one formatting mismatch
# before Android compilation.
source_path=Path('.github/prepare_3082.py')
src=source_path.read_text()
needle="else:\n    raise SystemExit('3.0.82 DB target missing: addOrIncrement insert')"
if needle not in src:
    raise SystemExit('3.0.82 release wrapper target missing: insert guard')
src=src.replace(needle,"else:\n    pass",1)
exec(compile(src,str(source_path),'exec'),{'__name__':'__main__','__file__':str(source_path)})

# The old source method is addOrIncrementAt(...). Add history to its NEW-item
# branch using a method-scoped regex so both existing-item and new-item counts
# are journaled regardless of whitespace produced by earlier prep scripts.
p=Path('app/src/main/java/com/iceinventory/onhand/InventoryDb.java')
s=p.read_text()
pat=r'''(    public void addOrIncrementAt\(.*?\) \{.*?)(\n    public void setQuantity)'''
m=re.search(pat,s,re.S)
if not m:
    raise SystemExit('3.0.82 release target missing: addOrIncrementAt')
block=m.group(1)
insert_re=r'''(\s*db\.insertOrThrow\("items",\s*null,\s*cv\);)(?!\s*\n\s*recordHistory\()'''
block2,n=re.subn(insert_re,lambda x:x.group(1)+'\n        recordHistory(sessionId,safeBarcode,description,quantity,safeLocation,"COUNT");',block,count=1)
if n!=1 and 'recordHistory(sessionId,safeBarcode,description,quantity,safeLocation,"COUNT");' not in block:
    raise SystemExit('3.0.82 release target missing: new-item insert')
s=s[:m.start(1)]+block2+s[m.end(1):]
p.write_text(s)

# Storage Access Framework createDocument requires the selected tree's document
# URI as parent. Use that parent so external recovery files can actually be
# created in the folder the operator selected.
p=Path('app/src/main/java/com/iceinventory/onhand/MainActivity.java')
s=p.read_text()
old='DocumentsContract.createDocument(getContentResolver(),tree,"text/plain",name)'
new='DocumentsContract.createDocument(getContentResolver(),DocumentsContract.buildDocumentUriUsingTree(tree,DocumentsContract.getTreeDocumentId(tree)),"text/plain",name)'
if old in s:
    s=s.replace(old,new,1)
p.write_text(s)

print('Prepared iCE Onhand 3.0.82 release compatibility fixes')
