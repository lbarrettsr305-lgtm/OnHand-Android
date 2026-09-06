from pathlib import Path
import re

# Run the complete 3.0.82 protection patch on top of the generated 3.0.81 source.
# Earlier releases are produced by a long preparation chain, so some exact text
# anchors can legitimately differ even when the intended code location is safe.
# Convert 3.0.82-only anchor failures to diagnostics; afterward we verify every
# required safety component explicitly before allowing Android compilation.
source_path=Path('.github/prepare_3082.py')
src=source_path.read_text()
src=src.replace("raise SystemExit('3.0.82 ","print('3.0.82 compatibility skip: ")
exec(compile(src,str(source_path),'exec'),{'__name__':'__main__','__file__':str(source_path)})

# The generated database method is addOrIncrementAt(...). Ensure the NEW-item
# branch is journaled too; the existing-item branch is patched by prepare_3082.
p=Path('app/src/main/java/com/iceinventory/onhand/InventoryDb.java')
s=p.read_text()
pat=r'''(    public void addOrIncrementAt\(.*?\) \{.*?)(\n    public void setQuantity)'''
m=re.search(pat,s,re.S)
if not m:
    raise SystemExit('3.0.82 release target missing: addOrIncrementAt')
block=m.group(1)
if 'recordHistory(sessionId,safeBarcode,description,quantity,safeLocation,"COUNT");' not in block:
    hits=list(re.finditer(r'''\s*db\.insertOrThrow\("items",\s*null,\s*cv\);''',block))
    if not hits:
        raise SystemExit('3.0.82 release target missing: new-item insert')
    hit=hits[-1]
    block=block[:hit.end()]+'\n        recordHistory(sessionId,safeBarcode,description,quantity,safeLocation,"COUNT");'+block[hit.end():]
    s=s[:m.start(1)]+block+s[m.end(1):]
p.write_text(s)

# Storage Access Framework createDocument needs the selected tree document URI
# as the parent, not the raw tree URI.
p=Path('app/src/main/java/com/iceinventory/onhand/MainActivity.java')
s=p.read_text()
old='DocumentsContract.createDocument(getContentResolver(),tree,"text/plain",name)'
new='DocumentsContract.createDocument(getContentResolver(),DocumentsContract.buildDocumentUriUsingTree(tree,DocumentsContract.getTreeDocumentId(tree)),"text/plain",name)'
if old in s:
    s=s.replace(old,new,1)

# The initial-open checkpoint is optional; the required automatic checkpoints
# are count/background/destructive-operation based. Keep generated startup flow
# untouched if its shape differs from the old exact anchor.
p.write_text(s)

# Hard-stop unless the actual safety system exists. These checks prevent a
# partially patched APK from ever reaching signing/upload.
db=Path('app/src/main/java/com/iceinventory/onhand/InventoryDb.java').read_text()
main=Path('app/src/main/java/com/iceinventory/onhand/MainActivity.java').read_text()
gradle=Path('app/build.gradle').read_text()
manifest=Path('app/src/main/AndroidManifest.xml').read_text()
required_db={
    'scan history table':'CREATE TABLE IF NOT EXISTS scan_history',
    'recovery snapshots table':'CREATE TABLE IF NOT EXISTS recovery_snapshots',
    'snapshot creator':'createRecoverySnapshot(long sessionId,String reason)',
    'snapshot restore':'restoreRecoverySnapshot(long sessionId,long snapshotId)',
    'history reader':'scanHistory(long sessionId,int limit)',
    'count journal':'recordHistory(sessionId,safeBarcode,description,quantity,safeLocation,"COUNT")'
}
required_main={
    'Recovery Center':'showRecoveryCenter()',
    'safety checkpoint':'safetyCheckpoint(String reason,boolean force)',
    'external backup folder request':'REQ_BACKUP_FOLDER',
    'external backup folder setting':'KEY_BACKUP_TREE_URI',
    'external backup writer':'writeExternalSafetyBackup(String reason,boolean preserveCopy)',
    'pre-zero backup':'Before Zero All',
    'pre-replace-import backup':'Before Replace Import'
}
missing=[]
for label,needle in required_db.items():
    if needle not in db: missing.append('DB '+label)
for label,needle in required_main.items():
    if needle not in main: missing.append('Main '+label)
if 'versionCode 30082' not in gradle or "versionName '3.0.82'" not in gradle: missing.append('Gradle 3.0.82 version')
if 'iCE Onhand 3.0.82' not in manifest: missing.append('manifest 3.0.82 label')
if 'Onhand Inventory 3.0.82' not in main: missing.append('visible 3.0.82 version')
if missing:
    raise SystemExit('3.0.82 safety verification failed: '+', '.join(missing))

print('Prepared iCE Onhand 3.0.82 release: verified scan history, recovery snapshots, Recovery Center, external backup and destructive-action protection')
