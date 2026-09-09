from pathlib import Path
import re

# Preserve every verified 3.0.94 feature first.
base=Path('.github/prepare_3094.py')
exec(compile(base.read_text(),str(base),'exec'),{'__name__':'__main__','__file__':str(base)})

# -----------------------------------------------------------------------------
# 3.0.95
# 1) Restore the saved user/operator name prefix to NEW batch, replay batch,
#    and complete-inventory filenames. Newer batch filename helpers had
#    overridden the older userExportFileName() result.
# 2) Ship the enhanced multi-user consolidation verification report.
# -----------------------------------------------------------------------------
p=Path('app/src/main/java/com/iceinventory/onhand/MainActivity.java')
s=p.read_text()

batch='''    private String batchExportFileName(){String day=new SimpleDateFormat("yyyy-MM-dd_HHmm",Locale.US).format(new Date());String ext=pendingExportExcel?".xlsx":".txt";String user=safeFilePart(savedUserName());String prefix=user.isEmpty()?"":user+" - ";return prefix+safeFileName(sessionName)+"_Batch"+String.format(Locale.US,"%02d",Math.max(1,pendingBatchNumber))+"_Seq"+seqText(pendingBatchFirstHistoryId)+"-"+seqText(pendingBatchLastHistoryId)+"_"+day+ext;}\n'''
s,n=re.subn(r'''    private String batchExportFileName\(\)\{.*?\}\n''',lambda m:batch,s,count=1,flags=re.S)
if n!=1:raise SystemExit('3.0.95 target missing: batch filename helper')

complete='''    private String completeExportFileName(){String day=new SimpleDateFormat("yyyy-MM-dd_HHmm",Locale.US).format(new Date());String ext=pendingExportExcel?".xlsx":".txt";String user=safeFilePart(savedUserName());String prefix=user.isEmpty()?"":user+" - ";return prefix+safeFileName(sessionName)+"_COMPLETE_Seq"+seqText(pendingBatchFirstHistoryId)+"-"+seqText(pendingBatchLastHistoryId)+"_"+day+ext;}\n'''
s,n=re.subn(r'''    private String completeExportFileName\(\)\{.*?\}\n''',lambda m:complete,s,count=1,flags=re.S)
if n!=1:raise SystemExit('3.0.95 target missing: complete filename helper')

s=s.replace('Onhand Inventory 3.0.94','Onhand Inventory 3.0.95')
if 'Onhand Inventory 3.0.95' not in s:raise SystemExit('3.0.95 target missing: visible version')
p.write_text(s)

p=Path('app/build.gradle')
g=p.read_text().replace('versionCode 30094','versionCode 30095',1).replace("versionName '3.0.94'","versionName '3.0.95'",1)
if 'versionCode 30095' not in g or "versionName '3.0.95'" not in g:raise SystemExit('3.0.95 target missing: Gradle version')
p.write_text(g)

p=Path('app/src/main/AndroidManifest.xml')
m=p.read_text().replace('iCE Onhand 3.0.94','iCE Onhand 3.0.95')
if 'iCE Onhand 3.0.95' not in m:raise SystemExit('3.0.95 target missing: manifest version')
p.write_text(m)

main=Path('app/src/main/java/com/iceinventory/onhand/MainActivity.java').read_text()
merge=Path('app/src/main/java/com/iceinventory/onhand/BatchMergeActivity.java').read_text()
checks={
    'batch filenames keep user prefix':'String prefix=user.isEmpty()?"":user+" - ";return prefix+safeFileName(sessionName)+"_Batch"' in main,
    'complete filenames keep user prefix':'return prefix+safeFileName(sessionName)+"_COMPLETE_Seq"' in main,
    'TXT default preserved':'Export New Counts Only (Batch ' in main and 'pendingExportExcel=false' in main,
    'Quantity header preserved':'Quantity' in Path('app/src/main/java/com/iceinventory/onhand/TabTextUtils.java').read_text(),
    'verification report button':'Export Verification Report' in merge,
    'per-user source totals':'User\\tSource Batch File\\tRows\\tQuantity' in merge,
    'selected-vs-loaded proof':'Successfully Loaded Files' in merge,
    'source grand total proof':'Source Grand Total Quantity' in merge,
    'combined grand total proof':'Combined Grand Total Quantity' in merge,
    'PASS result':'PASS - ALL SELECTED BATCH QUANTITIES INCLUDED AND TOTALS MATCH' in merge,
    'combined export remains standard':'Quantity\\tBarcode\\tDescription\\tPrice' in merge,
    'combined/report names prefixed':'prefixedName("Combined_Verified_Batch.txt")' in merge and 'prefixedName("Combined_Batch_Verification_Report.txt")' in merge,
}
missing=[k for k,v in checks.items() if not v]
if missing:raise SystemExit('3.0.95 verification failed: '+', '.join(missing))
print('Prepared iCE Onhand 3.0.95: user-prefixed batch filenames + auditable multi-user quantity verification report')
