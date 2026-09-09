from pathlib import Path
import re

# Preserve the complete 3.0.98 package first.
base=Path('.github/prepare_3098.py')
exec(compile(base.read_text(),str(base),'exec'),{'__name__':'__main__','__file__':str(base)})

# -----------------------------------------------------------------------------
# 3.0.99
# - Detect iCE-generated verification/output reports when selected alongside
#   real batch/source files.
# - Skip those known NON-SOURCE report files explicitly instead of treating them
#   as malformed batches or allowing them to affect inventory totals.
# - Keep verification strict for every actual source file considered.
# -----------------------------------------------------------------------------
p=Path('app/src/main/java/com/iceinventory/onhand/BatchMergeActivity.java')
m=p.read_text()

# Track excluded reports separately from actual source files.
old='''    private final ArrayList<BatchStat> sourceStats=new ArrayList<>();\n    private TextView status;\n    private Button save,report,excel;\n    private long sourceGrandTotal,outputTotal;\n    private int sourceFiles,sourceRows,selectedFiles;\n    private boolean verified;\n'''
new='''    private final ArrayList<BatchStat> sourceStats=new ArrayList<>();\n    private final ArrayList<String> excludedReportFiles=new ArrayList<>();\n    private TextView status;\n    private Button save,report,excel;\n    private long sourceGrandTotal,outputTotal;\n    private int sourceFiles,sourceRows,selectedFiles,candidateFiles,excludedReports;\n    private boolean verified;\n'''
if old not in m:raise SystemExit('3.0.99 target missing: merge fields')
m=m.replace(old,new,1)

# Replace loadFiles so known output reports are never treated as inventory input.
load_files=r'''    private void loadFiles(Intent data){
        combined.clear();sourceStats.clear();excludedReportFiles.clear();sourceGrandTotal=0;outputTotal=0;sourceFiles=0;sourceRows=0;selectedFiles=0;candidateFiles=0;excludedReports=0;verified=false;save.setEnabled(false);report.setEnabled(false);excel.setEnabled(false);
        ArrayList<Uri> uris=new ArrayList<>();
        if(data.getClipData()!=null)for(int i=0;i<data.getClipData().getItemCount();i++)uris.add(data.getClipData().getItemAt(i).getUri());
        else if(data.getData()!=null)uris.add(data.getData());
        selectedFiles=uris.size();
        ArrayList<String> errors=new ArrayList<>();
        for(Uri uri:uris){
            String name=displayName(uri);
            if(isGeneratedReportFile(name)){excludedReports++;excludedReportFiles.add(name);continue;}
            candidateFiles++;
            try{sourceStats.add(readOne(uri));sourceFiles++;}catch(Exception e){errors.add(e.getMessage()==null?"Unreadable batch/source file":e.getMessage());}
        }
        for(Total t:combined.values())outputTotal=Math.addExact(outputTotal,t.quantity);
        verified=errors.isEmpty()&&sourceFiles==candidateFiles&&candidateFiles>0&&sourceGrandTotal==outputTotal;
        StringBuilder s=new StringBuilder();
        s.append("Selected files: ").append(selectedFiles).append("\n");
        s.append("Non-source reports skipped: ").append(excludedReports).append("\n");
        s.append("Source files considered: ").append(candidateFiles).append("\n");
        s.append("Successfully loaded sources: ").append(sourceFiles).append("\n");
        s.append("Original rows: ").append(sourceRows).append("\nCombined barcodes: ").append(combined.size()).append("\n\n");
        if(!excludedReportFiles.isEmpty()){
            s.append("SKIPPED NON-SOURCE REPORT FILES\n");
            for(String n:excludedReportFiles)s.append("• ").append(n).append(" — report output, not inventory source data\n");
            s.append("\n");
        }
        s.append("BATCH / USER QUANTITY TOTALS\n");
        for(BatchStat b:sourceStats)s.append("• ").append(b.sourceType).append(" — ").append(b.userName.isEmpty()?"External / Unidentified":b.userName).append(" — ").append(b.quantity).append(" units — ").append(b.rows).append(" rows\n");
        s.append("\nSource grand total: ").append(sourceGrandTotal).append("\nCombined grand total: ").append(outputTotal).append("\nDifference: ").append(outputTotal-sourceGrandTotal).append("\n\n");
        if(verified)s.append("VERIFIED — ALL SOURCE FILES LOADED AND TOTALS MATCH");else s.append("NOT VERIFIED — EXPORT BLOCKED");
        if(candidateFiles==0&&excludedReports>0)s.append("\n\nSelect original batch/source files. Verification and Excel reports are outputs and cannot be used as source inventory.");
        if(!errors.isEmpty()){s.append("\n\nProblems:");for(String e:errors)s.append("\n• ").append(e);}
        status.setText(s.toString());status.setTextColor(verified?Color.rgb(120,255,140):Color.rgb(255,130,130));save.setEnabled(verified);report.setEnabled(verified);excel.setEnabled(verified);
    }

    private boolean isGeneratedReportFile(String fileName){
        String n=fileName==null?"":fileName.trim().toLowerCase(Locale.US).replace('-','_').replace(' ','_');
        if(n.isEmpty())return false;
        if(n.contains("combined_batch_verification_report"))return true;
        if(n.contains("combined_verification_report"))return true;
        if(n.contains("combined_verification_")&&n.endsWith(".xlsx"))return true;
        return n.contains("verification_report")&&n.contains("combined");
    }

'''
pat=r'''    private void loadFiles\(Intent data\)\{.*?\n    \}\n\n(?=    private BatchStat readOne\()'''
m,n=re.subn(pat,lambda x:load_files,m,count=1,flags=re.S)
if n!=1:raise SystemExit('3.0.99 target missing: loadFiles')

# Make TXT verification report distinguish chosen files from true source files.
m=m.replace('b.append("Selected Files\\t").append(selectedFiles).append("\\r\\n");\n        b.append("Successfully Loaded Files\\t").append(sourceFiles).append("\\r\\n");',
'''b.append("Total Selected Files\\t").append(selectedFiles).append("\\r\\n");
        b.append("Excluded Non-Source Reports\\t").append(excludedReports).append("\\r\\n");
        b.append("Source Files Considered\\t").append(candidateFiles).append("\\r\\n");
        b.append("Successfully Loaded Source Files\\t").append(sourceFiles).append("\\r\\n");''',1)

# Add explicit excluded report list to the TXT audit record.
old='''        b.append("Source Type\\tUser / Operator\\tSource File\\tRows\\tQuantity\\r\\n");\n        for(BatchStat s:sourceStats)b.append(clean(s.sourceType)).append('\\t').append(clean(s.userName.isEmpty()?"External / Unidentified":s.userName)).append('\\t').append(clean(s.fileName)).append('\\t').append(s.rows).append('\\t').append(s.quantity).append("\\r\\n");\n        b.append("\\r\\nVerification Method\\r\\n");\n'''
new='''        b.append("Source Type\\tUser / Operator\\tSource File\\tRows\\tQuantity\\r\\n");\n        for(BatchStat s:sourceStats)b.append(clean(s.sourceType)).append('\\t').append(clean(s.userName.isEmpty()?"External / Unidentified":s.userName)).append('\\t').append(clean(s.fileName)).append('\\t').append(s.rows).append('\\t').append(s.quantity).append("\\r\\n");\n        if(!excludedReportFiles.isEmpty()){\n            b.append("\\r\\nExcluded Non-Source Report Files\\r\\n");\n            for(String n:excludedReportFiles)b.append(clean(n)).append("\\tREPORT OUTPUT - NOT USED IN INVENTORY TOTALS\\r\\n");\n        }\n        b.append("\\r\\nVerification Method\\r\\n");\n'''
if old not in m:raise SystemExit('3.0.99 target missing: TXT source audit block')
m=m.replace(old,new,1)

m=m.replace('b.append("1. Every selected source file must open successfully. Files may use recognizable headers or the headerless standard order Quantity | Barcode | Description | Price.\\r\\n");',
'b.append("1. Every actual source file considered must open successfully. Known iCE-generated verification/output reports are excluded as non-source files and never included in inventory totals. Files may use recognizable headers or the headerless standard order Quantity | Barcode | Description | Price.\\r\\n");',1)
m=m.replace('b.append("5. PASS requires loaded files = selected files and Source Grand Total = Combined Grand Total.\\r\\n");',
'b.append("5. PASS requires successfully loaded source files = source files considered and Source Grand Total = Combined Grand Total.\\r\\n");',1)

# Keep the help text explicit so operators know output reports are not input.
m=m.replace('Filenames, extensions, store names and batch numbers are not required.',
'Filenames, extensions, store names and batch numbers are not required. Prior Verification/Excel report outputs are automatically identified as non-source reports and skipped.',1)
p.write_text(m)

# Professional workbook wording: all listed files are source files; reports are excluded before workbook generation.
p=Path('app/src/main/java/com/iceinventory/onhand/ProfessionalCombinedXlsxWriter.java')
x=p.read_text()
x=x.replace('The system verified that every selected source file shown as loaded was included in the calculation, matching barcodes were consolidated, and the Source Grand Total Quantity equals the Combined Grand Total Quantity when the report status is PASS.',
'The system verified that every inventory source file listed above was included in the calculation, matching barcodes were consolidated, and the Source Grand Total Quantity equals the Combined Grand Total Quantity when the report status is PASS. Known iCE-generated verification/output reports are excluded before reconciliation and are never used as source inventory data.',1)
p.write_text(x)

# Version package and visible labels.
p=Path('app/src/main/java/com/iceinventory/onhand/MainActivity.java')
s=p.read_text().replace('Onhand Inventory 3.0.98','Onhand Inventory 3.0.99')
if 'Onhand Inventory 3.0.99' not in s:raise SystemExit('3.0.99 target missing: visible version')
p.write_text(s)
p=Path('app/build.gradle')
g=p.read_text().replace('versionCode 30098','versionCode 30099',1).replace("versionName '3.0.98'","versionName '3.0.99'",1)
if 'versionCode 30099' not in g or "versionName '3.0.99'" not in g:raise SystemExit('3.0.99 target missing: Gradle version')
p.write_text(g)
p=Path('app/src/main/AndroidManifest.xml')
a=p.read_text().replace('iCE Onhand 3.0.98','iCE Onhand 3.0.99')
if 'iCE Onhand 3.0.99' not in a:raise SystemExit('3.0.99 target missing: manifest version')
p.write_text(a)

# Regression checks.
merge=Path('app/src/main/java/com/iceinventory/onhand/BatchMergeActivity.java').read_text()
xlsx=Path('app/src/main/java/com/iceinventory/onhand/ProfessionalCombinedXlsxWriter.java').read_text()
checks={
    'report detection helper':'isGeneratedReportFile' in merge,
    'verification report excluded':'combined_batch_verification_report' in merge,
    'professional xlsx excluded':'combined_verification_' in merge and '.xlsx' in merge,
    'combined verified batch not excluded':'combined_verified_batch' not in merge,
    'source candidate proof':'sourceFiles==candidateFiles' in merge and 'candidateFiles>0' in merge,
    'explicit skipped status':'SKIPPED NON-SOURCE REPORT FILES' in merge,
    'TXT audit exclusions':'Excluded Non-Source Report Files' in merge,
    'headerless support preserved':'looksLikeHeaderlessStandard' in merge,
    'master visibility preserved':'MASTER REPORT USER:' in merge,
    'valuation preserved':'Grand Total Inventory Value' in xlsx and 'Inventory Valuation' in xlsx,
    'professional logo preserved':'ice_inventory_master_3070' in xlsx,
    'full page scrolling preserved':'ScrollView pageScroll=new ScrollView(this)' in merge,
}
missing=[k for k,v in checks.items() if not v]
if missing:raise SystemExit('3.0.99 verification failed: '+', '.join(missing))
print('Prepared iCE Onhand 3.0.99: skip non-source verification/report outputs while preserving strict source reconciliation')
