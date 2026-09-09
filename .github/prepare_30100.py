from pathlib import Path
import re

# Preserve the complete 3.0.99 source/report filtering package first.
base=Path('.github/prepare_3099.py')
exec(compile(base.read_text(),str(base),'exec'),{'__name__':'__main__','__file__':str(base)})

# -----------------------------------------------------------------------------
# 3.0.100
# Reserve COMBINED as the filename prefix for every combined output.
# This makes combined outputs obvious to the operator and lets the app identify
# them immediately as NON-SOURCE files so they can never be accidentally
# re-imported and double-counted in a later reconciliation.
# -----------------------------------------------------------------------------
p=Path('app/src/main/java/com/iceinventory/onhand/BatchMergeActivity.java')
m=p.read_text()

# Prefix every combined output with COMBINED at the very beginning of the name.
m=m.replace('prefixedName(sourceInventoryName()+"_Combined_Verified_Batch.txt")','combinedOutputName(sourceInventoryName()+" - Verified Batch.txt")',1)
m=m.replace('prefixedName(sourceInventoryName()+"_Combined_Batch_Verification_Report.txt")','combinedOutputName(sourceInventoryName()+" - Verification Report.txt")',1)
m=m.replace('prefixedName(sourceInventoryName()+"_Combined_Verification_"+stamp+".xlsx")','combinedOutputName(sourceInventoryName()+" - Professional Report - "+stamp+".xlsx")',1)

# A reserved COMBINED prefix is now the primary non-source identifier. Keep the
# legacy patterns too so older reports from 3.0.96-3.0.99 remain protected.
old='''    private boolean isGeneratedReportFile(String fileName){
        String n=fileName==null?"":fileName.trim().toLowerCase(Locale.US).replace('-','_').replace(' ','_');
        if(n.isEmpty())return false;
        if(n.contains("combined_batch_verification_report"))return true;
        if(n.contains("combined_verification_report"))return true;
        if(n.contains("combined_verification_")&&n.endsWith(".xlsx"))return true;
        return n.contains("verification_report")&&n.contains("combined");
    }
'''
new='''    private boolean isGeneratedReportFile(String fileName){
        String n=fileName==null?"":fileName.trim().toLowerCase(Locale.US).replace('-','_').replace(' ','_');
        if(n.isEmpty())return false;
        if(n.startsWith("combined_"))return true;
        if(n.contains("combined_batch_verification_report"))return true;
        if(n.contains("combined_verification_report"))return true;
        if(n.contains("combined_verification_")&&n.endsWith(".xlsx"))return true;
        if(n.contains("combined_verified_batch"))return true;
        return n.contains("verification_report")&&n.contains("combined");
    }
'''
if old not in m:raise SystemExit('3.0.100 target missing: report detector')
m=m.replace(old,new,1)

# New filename helper: COMBINED is always first, then master/operator, then report.
anchor='''    private String prefixedName(String base){String u=safeFilePart(savedUserName());return u.isEmpty()?base:u+" - "+base;}\n'''
helper='''    private String prefixedName(String base){String u=safeFilePart(savedUserName());return u.isEmpty()?base:u+" - "+base;}\n    private String combinedOutputName(String base){String u=safeFilePart(savedUserName());String b=safeFilePart(base);return u.isEmpty()?"COMBINED - "+b:"COMBINED - "+u+" - "+b;}\n'''
if anchor not in m:raise SystemExit('3.0.100 target missing: prefixedName helper')
m=m.replace(anchor,helper,1)

# Make the on-screen guidance explicit.
m=m.replace('Prior Verification/Excel report outputs are automatically identified as non-source reports and skipped.',
'All new combined outputs begin with COMBINED. Any file beginning with COMBINED is automatically identified as a non-source output and skipped to prevent double-counting. Older verification/report filenames are also protected.',1)

# Clarify skipped-output text.
m=m.replace(' — report output, not inventory source data',' — COMBINED/report output, not inventory source data',1)
p.write_text(m)

# Professional workbook note documents the reserved prefix rule.
p=Path('app/src/main/java/com/iceinventory/onhand/ProfessionalCombinedXlsxWriter.java')
x=p.read_text()
x=x.replace('Known iCE-generated verification/output reports are excluded before reconciliation and are never used as source inventory data.',
'All iCE combined outputs use the reserved COMBINED filename prefix. COMBINED files and older recognized verification/output reports are excluded before reconciliation and are never used as source inventory data.',1)
p.write_text(x)

# Version package and visible labels.
p=Path('app/src/main/java/com/iceinventory/onhand/MainActivity.java')
s=p.read_text().replace('Onhand Inventory 3.0.99','Onhand Inventory 3.0.100')
if 'Onhand Inventory 3.0.100' not in s:raise SystemExit('3.0.100 target missing: visible version')
p.write_text(s)
p=Path('app/build.gradle')
g=p.read_text().replace('versionCode 30099','versionCode 30100',1).replace("versionName '3.0.99'","versionName '3.0.100'",1)
if 'versionCode 30100' not in g or "versionName '3.0.100'" not in g:raise SystemExit('3.0.100 target missing: Gradle version')
p.write_text(g)
p=Path('app/src/main/AndroidManifest.xml')
a=p.read_text().replace('iCE Onhand 3.0.99','iCE Onhand 3.0.100')
if 'iCE Onhand 3.0.100' not in a:raise SystemExit('3.0.100 target missing: manifest version')
p.write_text(a)

# Regression checks.
merge=Path('app/src/main/java/com/iceinventory/onhand/BatchMergeActivity.java').read_text()
xlsx=Path('app/src/main/java/com/iceinventory/onhand/ProfessionalCombinedXlsxWriter.java').read_text()
checks={
    'reserved combined prefix':'combinedOutputName' in merge and '"COMBINED - "+' in merge,
    'prefix auto-detection':'n.startsWith("combined_")' in merge,
    'legacy combined batch protected':'combined_verified_batch' in merge,
    'combined txt prefixed':'combinedOutputName(sourceInventoryName()+" - Verified Batch.txt")' in merge,
    'verification txt prefixed':'combinedOutputName(sourceInventoryName()+" - Verification Report.txt")' in merge,
    'professional xlsx prefixed':'combinedOutputName(sourceInventoryName()+" - Professional Report - "+stamp+".xlsx")' in merge,
    'source filtering preserved':'sourceFiles==candidateFiles' in merge,
    'headerless preserved':'looksLikeHeaderlessStandard' in merge,
    'master visibility preserved':'MASTER REPORT USER:' in merge,
    'valuation preserved':'Grand Total Inventory Value' in xlsx and 'Inventory Valuation' in xlsx,
    'logo preserved':'ice_inventory_master_3070' in xlsx,
    'scroll preserved':'ScrollView pageScroll=new ScrollView(this)' in merge,
}
missing=[k for k,v in checks.items() if not v]
if missing:raise SystemExit('3.0.100 verification failed: '+', '.join(missing))
print('Prepared iCE Onhand 3.0.100: COMBINED reserved output prefix + automatic non-source identification')
