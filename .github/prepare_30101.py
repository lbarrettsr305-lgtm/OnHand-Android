from pathlib import Path
import re

# Preserve the complete 3.0.100 combined-output and reporting package first.
base=Path('.github/prepare_30100.py')
exec(compile(base.read_text(),str(base),'exec'),{'__name__':'__main__','__file__':str(base)})

# -----------------------------------------------------------------------------
# 3.0.101
# Make the batch number immediately visible by joining it directly to the saved
# user/operator name at the beginning of NEW-COUNT batch export filenames.
#
# Example:
#   Before: Chief - ONHAND_GARDEN_L..._Batch04_Seq...txt
#   After:  Chief4 - ONHAND_GARDEN_L..._Seq...txt
#
# The formal batch number remains stored internally in export_batches for
# history/re-export/audit. We only remove the redundant visible _Batch04 text.
# -----------------------------------------------------------------------------
p=Path('app/src/main/java/com/iceinventory/onhand/MainActivity.java')
s=p.read_text()

batch='''    private String batchExportFileName(){String day=new SimpleDateFormat("yyyy-MM-dd_HHmm",Locale.US).format(new Date());String ext=pendingExportExcel?".xlsx":".txt";String user=safeFilePart(savedUserName());int batchNo=Math.max(1,pendingBatchNumber);String prefix=user.isEmpty()?"Batch"+batchNo+" - ":user+batchNo+" - ";return prefix+safeFileName(sessionName)+"_Seq"+seqText(pendingBatchFirstHistoryId)+"-"+seqText(pendingBatchLastHistoryId)+"_"+day+ext;}\n'''
s,n=re.subn(r'''    private String batchExportFileName\(\)\{.*?\}\n''',lambda m:batch,s,count=1,flags=re.S)
if n!=1:raise SystemExit('3.0.101 target missing: batch filename helper')

s=s.replace('Onhand Inventory 3.0.100','Onhand Inventory 3.0.101')
if 'Onhand Inventory 3.0.101' not in s:raise SystemExit('3.0.101 target missing: visible version')
p.write_text(s)

p=Path('app/build.gradle')
g=p.read_text().replace('versionCode 30100','versionCode 30101',1).replace("versionName '3.0.100'","versionName '3.0.101'",1)
if 'versionCode 30101' not in g or "versionName '3.0.101'" not in g:raise SystemExit('3.0.101 target missing: Gradle version')
p.write_text(g)

p=Path('app/src/main/AndroidManifest.xml')
m=p.read_text().replace('iCE Onhand 3.0.100','iCE Onhand 3.0.101')
if 'iCE Onhand 3.0.101' not in m:raise SystemExit('3.0.101 target missing: manifest version')
p.write_text(m)

# Regression checks.
main=Path('app/src/main/java/com/iceinventory/onhand/MainActivity.java').read_text()
merge=Path('app/src/main/java/com/iceinventory/onhand/BatchMergeActivity.java').read_text()
xlsx=Path('app/src/main/java/com/iceinventory/onhand/ProfessionalCombinedXlsxWriter.java').read_text()
checks={
    'compact user batch prefix':'user+batchNo+" - "' in main,
    'no redundant visible Batch token':'return prefix+safeFileName(sessionName)+"_Seq"' in main,
    'internal batch history preserved':'nextBatchNumber(sessionId)' in main and 'pendingBatchNumber' in main,
    'sequence preserved':'_Seq"+seqText(pendingBatchFirstHistoryId)+"-"+seqText(pendingBatchLastHistoryId)' in main,
    'TXT default preserved':'Export New Counts Only (Batch ' in main and 'pendingExportExcel=false' in main,
    'master user preserved':'MASTER REPORT USER' in main and 'MASTER REPORT USER:' in merge,
    'headerless external preserved':'looksLikeHeaderlessStandard' in merge,
    'combined prefix preserved':'combinedOutputName' in merge and 'COMBINED - ' in merge,
    'valuation preserved':'Inventory Valuation' in xlsx and 'Grand Total Inventory Value' in xlsx,
    'professional report preserved':'Formal Verification Note' in xlsx and 'Ice Inventory LLC' in xlsx,
}
missing=[k for k,v in checks.items() if not v]
if missing:raise SystemExit('3.0.101 verification failed: '+', '.join(missing))
print('Prepared iCE Onhand 3.0.101: compact visible batch prefix such as Chief4')
