from pathlib import Path
import runpy

# Preserve every approved 3.0.76 feature first.
runpy.run_path('.github/prepare_3076.py', run_name='__main__')

p=Path('app/src/main/java/com/iceinventory/onhand/MainActivity.java')
s=p.read_text()

def rep(old,new,label):
    global s
    if old not in s: raise SystemExit('3.0.77 target missing: '+label)
    s=s.replace(old,new,1)

# Track Excel as an additional standard inventory export format.
rep('    private boolean pendingExportLocationQuantityReport=false;\n',
    '    private boolean pendingExportLocationQuantityReport=false;\n    private boolean pendingExportExcel=false;\n',
    'Excel pending flag')

# Standard inventory can now be saved as TXT or a true .xlsx workbook. Existing
# Internet Items With Pictures and Location Quantity reports remain separate.
rep('String[] choices={"All inventory items","Internet items with pictures","Location Quantity Report"};',
    'String[] choices={"All inventory items — TXT","All inventory items — Excel (.xlsx)","Internet items with pictures","Location Quantity Report"};',
    'export format choices')
rep('                    boolean internetOnly=which==1;\n                    boolean locationQuantityReport=which==2;\n',
    '                    boolean excel=which==1;\n                    boolean internetOnly=which==2;\n                    boolean locationQuantityReport=which==3;\n',
    'export format flags')
rep('                    pendingExportInternetOnly=internetOnly;\n                    pendingExportLocationQuantityReport=locationQuantityReport;\n                    showExportDialog();',
    '                    pendingExportInternetOnly=internetOnly;\n                    pendingExportLocationQuantityReport=locationQuantityReport;\n                    pendingExportExcel=excel;\n                    showExportDialog();',
    'Excel scope assignment')

# Filename helpers keep TXT and XLSX distinct while preserving the user's project/user prefix.
marker='    private String locationQuantityExportFileName(String name) {\n'
helper='''    private String cleanExcelName(String s) {
        String n=s==null?"":s.trim();
        if(n.isEmpty())n=safeFileName(sessionName);
        String low=n.toLowerCase(Locale.US);
        if(low.endsWith(".txt"))n=n.substring(0,n.length()-4);
        else if(low.endsWith(".xlsx"))n=n.substring(0,n.length()-5);
        return n+".xlsx";
    }

    private String excelExportFileName(String name) {
        return cleanExcelName(name);
    }

'''
if marker not in s: raise SystemExit('3.0.77 target missing: location filename marker')
s=s.replace(marker,helper+marker,1)

rep('        if(pendingExportInternetOnly)exportName=internetExportFileName(exportName);\n        if(pendingExportLocationQuantityReport)exportName=locationQuantityExportFileName(exportName);',
    '        if(pendingExportExcel)exportName=excelExportFileName(exportName);\n        if(pendingExportInternetOnly)exportName=internetExportFileName(exportName);\n        if(pendingExportLocationQuantityReport)exportName=locationQuantityExportFileName(exportName);',
    'Excel filename')

rep('String exportTitle=pendingExportLocationQuantityReport?"Location Quantity Report":(pendingExportInternetOnly?"Export Internet Items With Pictures":"Export TXT");',
    'String exportTitle=pendingExportLocationQuantityReport?"Location Quantity Report":(pendingExportInternetOnly?"Export Internet Items With Pictures":(pendingExportExcel?"Export Excel":"Export TXT"));',
    'Excel export title')
rep('String exportMessage=pendingExportLocationQuantityReport?"Separate TXT report • total quantity for each location plus a grand total.":(pendingExportInternetOnly?"Separate HTML report • internet-added items with associated product pictures.":"All inventory items • tab-delimited TXT file.");',
    'String exportMessage=pendingExportLocationQuantityReport?"Separate TXT report • total quantity for each location plus a grand total.":(pendingExportInternetOnly?"Separate HTML report • internet-added items with associated product pictures.":(pendingExportExcel?"Excel workbook • same inventory columns and headers as TXT.":"All inventory items • tab-delimited TXT file."));',
    'Excel export message')

# Existing save buttons already handle Internet HTML specially. Add XLSX filename handling.
old='pendingExportInternetOnly?cleanInternetReportName(name.getText().toString()):cleanTextName(name.getText().toString())'
new='pendingExportExcel?cleanExcelName(name.getText().toString()):(pendingExportInternetOnly?cleanInternetReportName(name.getText().toString()):cleanTextName(name.getText().toString()))'
if s.count(old)<2: raise SystemExit('3.0.77 target missing: save filename expressions')
s=s.replace(old,new)

# Correct MIME type for Downloads and Android document picker.
old='pendingExportInternetOnly?"text/html":"text/plain"'
new='pendingExportExcel?"application/vnd.openxmlformats-officedocument.spreadsheetml.sheet":(pendingExportInternetOnly?"text/html":"text/plain")'
if s.count(old)<2: raise SystemExit('3.0.77 target missing: export MIME expressions')
s=s.replace(old,new)

# Write a true XLSX ZIP/XML workbook rather than a renamed text file.
old='''            if(pendingExportLocationQuantityReport) {
                os.write(buildLocationQuantityReport(db.items(sessionId)).getBytes(StandardCharsets.UTF_8));
                toast("Location quantity report exported");
            } else if(pendingExportInternetOnly) {
                os.write(buildInternetItemsHtml().getBytes(StandardCharsets.UTF_8));
                toast("Internet items with pictures exported");
            } else {
                os.write(TabTextUtils.exportRows(db.items(sessionId),prefs()).getBytes(StandardCharsets.UTF_8));
                toast("Tab-delimited TXT exported");
            }
'''
new='''            if(pendingExportLocationQuantityReport) {
                os.write(buildLocationQuantityReport(db.items(sessionId)).getBytes(StandardCharsets.UTF_8));
                toast("Location quantity report exported");
            } else if(pendingExportExcel) {
                SimpleXlsxWriter.write(os,db.items(sessionId),prefs());
                toast("Excel workbook exported");
            } else if(pendingExportInternetOnly) {
                os.write(buildInternetItemsHtml().getBytes(StandardCharsets.UTF_8));
                toast("Internet items with pictures exported");
            } else {
                os.write(TabTextUtils.exportRows(db.items(sessionId),prefs()).getBytes(StandardCharsets.UTF_8));
                toast("Tab-delimited TXT exported");
            }
'''
rep(old,new,'Excel writer')

# The bottom control now represents multiple export formats, not TXT only.
s=s.replace('Button exp=button("⬆ Export TXT",2);','Button exp=button("⬆ Export",2);',1)

rep('TextView app=text("Onhand Inventory 3.0.76",19,Color.WHITE,true);',
    'TextView app=text("Onhand Inventory 3.0.77",19,Color.WHITE,true);','visible version')
p.write_text(s)

# Update the format screen wording so it applies to both TXT and Excel exports.
p=Path('app/src/main/java/com/iceinventory/onhand/FormatConfigActivity.java')
s=p.read_text()
old='        body.addView(text("TXT file • TAB delimited",18,gold(),true));\n'
new='        body.addView(text(MODE_EXPORT.equals(mode)?"Inventory export • TXT or Excel":"TXT file • TAB delimited",18,gold(),true));\n'
if old not in s: raise SystemExit('3.0.77 target missing: format screen wording')
s=s.replace(old,new,1)
p.write_text(s)

p=Path('app/build.gradle')
s=p.read_text().replace('versionCode 30076','versionCode 30077',1).replace("versionName '3.0.76'","versionName '3.0.77'",1)
if 'versionCode 30077' not in s or "versionName '3.0.77'" not in s: raise SystemExit('3.0.77 target missing: Gradle version')
p.write_text(s)

p=Path('app/src/main/AndroidManifest.xml')
s=p.read_text().replace('android:label="iCE Onhand 3.0.76"','android:label="iCE Onhand 3.0.77"',1)
if 'android:label="iCE Onhand 3.0.77"' not in s: raise SystemExit('3.0.77 target missing: manifest version')
p.write_text(s)

print('Prepared iCE Onhand 3.0.77: TXT headers + true Excel XLSX export + 3.0.76 scan/Cases fixes')
