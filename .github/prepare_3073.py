from pathlib import Path
import runpy

# Preserve all 3.0.72 behavior first, including safe Replace / Append / Cancel import,
# and the existing Internet Items With Pictures HTML export.
runpy.run_path('.github/prepare_3072.py', run_name='__main__')

p = Path('app/src/main/java/com/iceinventory/onhand/MainActivity.java')
s = p.read_text()

def rep(old,new,label):
    global s
    if old not in s:
        raise SystemExit('3.0.73 target missing: '+label)
    s=s.replace(old,new,1)

# Track the dedicated location-summary export while Android's save picker is open.
rep('    private boolean pendingExportInternetOnly=false;\n',
    '    private boolean pendingExportInternetOnly=false;\n    private boolean pendingExportLocationQuantityReport=false;\n',
    'pending export field')

# The current app already calls its second export "Internet items with pictures".
# Add the new report without changing that working feature.
rep('String[] choices={"All inventory items","Internet items with pictures"};',
    'String[] choices={"All inventory items","Internet items with pictures","Location Quantity Report"};',
    'export scope choices')
rep('                    boolean internetOnly=which==1;\n',
    '                    boolean internetOnly=which==1;\n                    boolean locationQuantityReport=which==2;\n',
    'location export choice flag')
rep('                    pendingExportInternetOnly=internetOnly;\n                    showExportDialog();',
    '                    pendingExportInternetOnly=internetOnly;\n                    pendingExportLocationQuantityReport=locationQuantityReport;\n                    showExportDialog();',
    'location export scope assignment')

# Separate filename and report builder. Include every defined location even when
# its current quantity is zero, then provide a grand total.
marker = '    private void showExportDialog() {\n'
helper = '''    private String locationQuantityExportFileName(String name) {
        String n=cleanTextName(name);
        if(n.toLowerCase(Locale.US).endsWith(".txt"))n=n.substring(0,n.length()-4);
        if(!n.toLowerCase(Locale.US).endsWith(" - location quantity"))n+=" - Location Quantity";
        return n+".txt";
    }

    private String buildLocationQuantityReport(List<InventoryDb.Row> rows) {
        java.util.TreeMap<String,Integer> totals=new java.util.TreeMap<>(String.CASE_INSENSITIVE_ORDER);
        for(String loc:db.locations()) {
            String key=loc==null||loc.trim().isEmpty()?"Main":loc.trim();
            totals.put(key,0);
        }
        int grandTotal=0;
        for(InventoryDb.Row r:rows) {
            String key=r.location==null||r.location.trim().isEmpty()?"Main":r.location.trim();
            int qty=r.quantity;
            Integer current=totals.get(key);
            totals.put(key,(current==null?0:current)+qty);
            grandTotal+=qty;
        }
        StringBuilder out=new StringBuilder();
        out.append("Location\\tQuantity\\r\\n");
        for(java.util.Map.Entry<String,Integer> e:totals.entrySet()) {
            out.append(e.getKey().replace("\\t"," ").replace("\\r"," ").replace("\\n"," "))
                    .append('\\t').append(e.getValue()).append("\\r\\n");
        }
        out.append("GRAND TOTAL\\t").append(grandTotal).append("\\r\\n");
        return out.toString();
    }

'''
if marker not in s:
    raise SystemExit('3.0.73 target missing: export dialog marker')
s=s.replace(marker,helper+marker,1)

# Give the report an independent TXT filename and clear dialog wording.
rep('        if(pendingExportInternetOnly)exportName=internetExportFileName(exportName);\n        name.setText(exportName);',
    '        if(pendingExportInternetOnly)exportName=internetExportFileName(exportName);\n        if(pendingExportLocationQuantityReport)exportName=locationQuantityExportFileName(exportName);\n        name.setText(exportName);',
    'location report filename')
rep('String exportTitle=pendingExportInternetOnly?"Export Internet Items With Pictures":"Export TXT";',
    'String exportTitle=pendingExportLocationQuantityReport?"Location Quantity Report":(pendingExportInternetOnly?"Export Internet Items With Pictures":"Export TXT");',
    'export title')
rep('String exportMessage=pendingExportInternetOnly?"Separate HTML report • internet-added items with associated product pictures.":"All inventory items • tab-delimited TXT file.";',
    'String exportMessage=pendingExportLocationQuantityReport?"Separate TXT report • total quantity for each location plus a grand total.":(pendingExportInternetOnly?"Separate HTML report • internet-added items with associated product pictures.":"All inventory items • tab-delimited TXT file.");',
    'export message')

# Keep Internet Items With Pictures exactly as HTML; the location report is plain TXT.
old = '''            if(pendingExportInternetOnly) {
                os.write(buildInternetItemsHtml().getBytes(StandardCharsets.UTF_8));
                toast("Internet items with pictures exported");
            } else {
                os.write(TabTextUtils.exportRows(db.items(sessionId),prefs()).getBytes(StandardCharsets.UTF_8));
                toast("Tab-delimited TXT exported");
            }
'''
new = '''            if(pendingExportLocationQuantityReport) {
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
rep(old,new,'export writer')

# Advance visible and installable Android versions.
rep('TextView app=text("Onhand Inventory 3.0.72",19,Color.WHITE,true);',
    'TextView app=text("Onhand Inventory 3.0.73",19,Color.WHITE,true);',
    'visible version')
p.write_text(s)

p=Path('app/build.gradle')
s=p.read_text().replace('versionCode 30072','versionCode 30073',1).replace("versionName '3.0.72'","versionName '3.0.73'",1)
if 'versionCode 30073' not in s or "versionName '3.0.73'" not in s:
    raise SystemExit('3.0.73 target missing: Gradle version')
p.write_text(s)

p=Path('app/src/main/AndroidManifest.xml')
s=p.read_text().replace('android:label="iCE Onhand 3.0.72"','android:label="iCE Onhand 3.0.73"',1)
p.write_text(s)

print('Prepared iCE Onhand 3.0.73: separate Location Quantity Report with per-location totals and grand total')
