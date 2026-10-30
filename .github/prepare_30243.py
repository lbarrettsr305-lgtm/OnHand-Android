#!/usr/bin/env python3
"""OnHand 3.0.243: simplify Victoria combine and send only counted rows."""
from pathlib import Path
import os
import runpy

root = Path(__file__).resolve().parents[1]
workflow = root / ".github/workflows/build-apk.yml"


def replace_once(path, old, new, label):
    data = path.read_text()
    count = data.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected one anchor, found {count}")
    path.write_text(data.replace(old, new, 1))


# Run the established 3.0.242 preparation chain on the release baseline.
if os.environ.get("ONHAND_PREPARED_30242") != "1":
    w = workflow.read_text()
    for current, previous, expected in [
        ("Prepare and verify 3.0.243 Victoria counted batch workflow",
         "Prepare and verify 3.0.242 Victoria batch location UPC reports", 1),
        (".github/prepare_30243.py", ".github/prepare_30242.py", 1),
        ("iCE-Onhand-Inventory-3.0.243", "iCE-Onhand-Inventory-3.0.242", 4),
    ]:
        if w.count(current) != expected:
            raise SystemExit("3.0.243 workflow marker missing: " + current)
        w = w.replace(current, previous)
    workflow.write_text(w)
    runpy.run_path(str(root / ".github/prepare_30242.py"), run_name="__main__")

# Set the next release version and restore the workflow's release labels.
for old, new, expected in [
    ("Prepare and verify 3.0.242 Victoria batch location UPC reports",
     "Prepare and verify 3.0.243 Victoria counted batch workflow", 1),
    (".github/prepare_30242.py", ".github/prepare_30243.py", 1),
    ("iCE-Onhand-Inventory-3.0.242", "iCE-Onhand-Inventory-3.0.243", 4),
]:
    w = workflow.read_text()
    if w.count(old) != expected:
        raise SystemExit("3.0.242 workflow restore marker missing: " + old)
    workflow.write_text(w.replace(old, new))

gradle = root / "app/build.gradle"
replace_once(gradle, "versionCode 30242", "versionCode 30243", "Gradle version code")
replace_once(gradle, "versionName '3.0.242'", "versionName '3.0.243'", "Gradle version name")
manifest = root / "app/src/main/AndroidManifest.xml"
replace_once(manifest, "iCE Onhand 3.0.242", "iCE Onhand 3.0.243", "Manifest version")
main = root / "app/src/main/java/com/iceinventory/onhand/MainActivity.java"
replace_once(main, "Onhand Inventory 3.0.242", "Onhand Inventory 3.0.243", "Main screen version")

# Default all normal exports to omit zero-quantity master rows, including on
# existing phones. The user can still uncheck this setting deliberately.
application = root / "app/src/main/java/com/iceinventory/onhand/OnHandApplication.java"
replace_once(application,
             "import android.content.Intent;",
             "import android.content.Intent;\nimport android.content.SharedPreferences;",
             "Application preferences import")
replace_once(application,
             "        super.onCreate();\n        registerActivityLifecycleCallbacks",
             "        super.onCreate();\n"
             "        SharedPreferences settings=getSharedPreferences(\"onhand_settings\",MODE_PRIVATE);\n"
             "        String positiveOnlyMigration=\"export_positive_only_default_migrated\";\n"
             "        if(!settings.getBoolean(positiveOnlyMigration,false)){\n"
             "            settings.edit().putBoolean(\"export_quantity_above_zero_only\",true)\n"
             "                    .putBoolean(positiveOnlyMigration,true).apply();\n"
             "        }\n"
             "        registerActivityLifecycleCallbacks",
             "Positive quantity export default migration")
fmt = root / "app/src/main/java/com/iceinventory/onhand/FormatConfigActivity.java"
replace_once(fmt,
             "positiveOnly.setChecked(prefs().getBoolean(KEY_EXPORT_POSITIVE_ONLY,false));",
             "positiveOnly.setChecked(prefs().getBoolean(KEY_EXPORT_POSITIVE_ONLY,true));",
             "Export checkbox default")
tab = root / "app/src/main/java/com/iceinventory/onhand/TabTextUtils.java"
replace_once(tab,
             "prefs.getBoolean(KEY_EXPORT_POSITIVE_ONLY,false)",
             "prefs.getBoolean(KEY_EXPORT_POSITIVE_ONLY,true)",
             "TXT positive-only default")
xlsx = root / "app/src/main/java/com/iceinventory/onhand/SimpleXlsxWriter.java"
replace_once(xlsx,
             'prefs.getBoolean("export_quantity_above_zero_only",false)',
             'prefs.getBoolean("export_quantity_above_zero_only",true)',
             "Excel positive-only default")

# Make a counter's completed-count button export items that actually have
# count history, then apply the checked-by-default positive-quantity filter.
replace_once(main,
             'Button exp=button(hasAdminAccess()?"⬆ Export":"⬆ SEND COMPLETED COUNT",2);exp.setTextSize(hasAdminAccess()?14:12);exp.setSingleLine(false);exp.setTypeface(Typeface.DEFAULT,Typeface.BOLD);exp.setOnClickListener(v->{if(hasAdminAccess())showExportScopeDialog();else beginCompleteInventoryExport();});',
             'Button exp=button(hasAdminAccess()?"⬆ Export":"⬆ SEND COUNTED ITEMS",2);exp.setTextSize(hasAdminAccess()?14:12);exp.setSingleLine(false);exp.setTypeface(Typeface.DEFAULT,Typeface.BOLD);exp.setOnClickListener(v->{if(hasAdminAccess())showExportScopeDialog();else beginCountedCountExport();});',
             "Count user export action")
replace_once(main,
             '    private void showBatchReExportDialog() {',
             '    private void beginCountedCountExport() {\n'
             '        List<InventoryDb.Row> rows=db.countedRows(sessionId);\n'
             '        if(rows.isEmpty()){toast("No counted item lines to send");return;}\n'
             '        pendingExportInternetOnly=false;pendingExportLocationQuantityReport=false;pendingExportLocationDetailReport=false;\n'
             '        pendingBatchMode=4;pendingBatchNumber=db.nextCompleteExportNumber(sessionId);\n'
             '        long last=db.maxHistoryId(sessionId);pendingBatchFirstHistoryId=db.firstHistoryIdAfter(sessionId,0L,last);pendingBatchLastHistoryId=last;pendingBatchReplayId=0L;\n'
             '        startExportFormatFlow();\n'
             '    }\n\n'
             '    private void showBatchReExportDialog() {',
             "Count user export flow")
replace_once(main,
             '    private String batchExportFileName(){String ext=pendingExportExcel?".xlsx":".txt";String store=safeFilePart(sessionName);String user=safeFilePart(savedUserName());if(store.isEmpty())store="Inventory";if(user.isEmpty())user="Counter";return store+"-"+user+"-Batch"+String.format(Locale.US,"%02d",Math.max(1,pendingBatchNumber))+ext;}\n',
             '    private String batchExportFileName(){String ext=pendingExportExcel?".xlsx":".txt";String store=safeFilePart(sessionName);String user=batchExportUserName();if(store.isEmpty())store="Inventory";if(user.isEmpty())user="Counter";return user+" Batch "+Math.max(1,pendingBatchNumber)+" - "+store+ext;}\n'
             '    private String countedExportFileName(){String ext=pendingExportExcel?".xlsx":".txt";String store=safeFilePart(sessionName);String user=batchExportUserName();if(store.isEmpty())store="Inventory";if(user.isEmpty())user="Counter";return user+" Batch "+Math.max(1,pendingBatchNumber)+" - "+store+ext;}\n'
             '    private String batchExportUserName(){String user=safeFilePart(savedUserName());return "RobertFad".equalsIgnoreCase(user)?"Robert":user;}\n',
             "Short user-first batch filenames")
replace_once(main,
             '        else if(pendingBatchMode==2)exportName=completeExportFileName();',
             '        else if(pendingBatchMode==2)exportName=completeExportFileName();\n'
             '        else if(pendingBatchMode==4)exportName=countedExportFileName();',
             "Counted filename selection")
replace_once(main,
             '        new AlertDialog.Builder(this).setTitle(exportTitle).setMessage(exportMessage).setView(name)',
             '        if(pendingBatchMode==4){exportTitle=pendingExportExcel?"Send Counted Items — Excel":"Send Counted Items — TXT";exportMessage="Counted items only. By default, zero-quantity rows and untouched master items are omitted.";}\n'
             '        new AlertDialog.Builder(this).setTitle(exportTitle).setMessage(exportMessage).setView(name)',
             "Counted export instructions")
replace_once(main,
             '            } else if(pendingBatchMode==2) {',
             '            } else if(pendingBatchMode==4) {\n'
             '                List<InventoryDb.Row> rows=new ArrayList<>(db.countedRows(sessionId));\n'
             '                if(prefs().getBoolean("export_quantity_above_zero_only",true))rows.removeIf(row->row==null||row.quantity<=0);\n'
             '                if(rows.isEmpty())throw new Exception("No positive-quantity counted lines are available to send");\n'
             '                if(pendingExportExcel)SimpleXlsxWriter.writeBatch(os,rows,prefs());\n'
             '                else os.write(BatchExportText.exportRows(rows,prefs()).getBytes(StandardCharsets.UTF_8));\n'
             '                double units=0;for(InventoryDb.Row r:rows)units+=r.quantity;\n'
             '                db.recordExportBatch(sessionId,pendingBatchNumber,"COUNTED",pendingBatchFirstHistoryId,pendingBatchLastHistoryId,rows.size(),units,pendingExportFileName);\n'
             '                safetyCheckpoint("After Count Submission Export",true);\n'
             '                toast("Counted items sent • "+rows.size()+" lines");\n'
             '            } else if(pendingBatchMode==2) {',
             "Counted export writer")

# Add a query which selects items touched by scan history. The shared master
# remains loaded, but untouched zero-quantity master rows never enter the file.
db = root / "app/src/main/java/com/iceinventory/onhand/InventoryDb.java"
replace_once(db,
             '    public List<Row> batchRows(long sessionId,long afterExclusive,long throughInclusive) {',
             '    public List<Row> countedRows(long sessionId) {\n'
             '        ArrayList<Row> out=new ArrayList<>();\n'
             '        if(sessionId<=0)return out;\n'
             '        ensureRecoveryTables(getReadableDatabase());\n'
             '        String sql="SELECT i.id,i.session_id,i.barcode,i.description,i.item_number,i.price,i.quantity,i.location,i.updated_at,i.category_name,COALESCE((SELECT MIN(h.id) FROM scan_history h WHERE h.session_id=i.session_id AND h.barcode=i.barcode COLLATE NOCASE AND h.location=i.location COLLATE NOCASE),i.id) FROM items i WHERE i.session_id=? AND EXISTS(SELECT 1 FROM scan_history h WHERE h.session_id=i.session_id AND h.barcode=i.barcode COLLATE NOCASE AND h.location=i.location COLLATE NOCASE) ORDER BY i.updated_at DESC";\n'
             '        try(Cursor c=getReadableDatabase().rawQuery(sql,new String[]{String.valueOf(sessionId)})){while(c.moveToNext())out.add(rowFromCursor(c));}\n'
             '        return out;\n'
             '    }\n\n'
             '    public List<Row> batchRows(long sessionId,long afterExclusive,long throughInclusive) {',
             "Counted rows database query")
replace_once(db,
             "export_type='COMPLETE'",
             "export_type IN ('COMPLETE','COUNTED')",
             "Complete/count batch sequence")

# The combined Victoria report receives ITEM NUMBER and DESCRIPTION from the
# shared inventory file already present in each count batch. No second master
# import is needed in the combine screen.
merge = root / "app/src/main/java/com/iceinventory/onhand/BatchMergeActivity.java"
replace_once(merge,
             'TextView help=text("VICTORIA WORKFLOW: First select the original Victoria Excel file. It supplies ITEM NUMBER and the official DESCRIPTION. Then select every returned counter file. Counter files supply QTY and LOCATION. Location remains in the verification reports but is excluded from the final four-column Victoria customer Excel.",15,Color.WHITE);help.setPadding(0,dp(8),0,dp(12));page.addView(help);\n'
             '        Button victoriaSource=button("1. Select Original Victoria Excel");victoriaSource.setOnClickListener(v->chooseVictoriaSource());page.addView(victoriaSource,new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT,dp(58)));\n'
             '        Button choose=button("2. Select All Counter Files");',
             'TextView help=text("VICTORIA: The shared inventory already includes ITEM NUMBER and DESCRIPTION. Select all returned counter files once. The count files carry QTY, UPC, ITEM NUMBER, DESCRIPTION, and LOCATION; no second master import is needed.",15,Color.WHITE);help.setPadding(0,dp(8),0,dp(12));page.addView(help);\n'
             '        Button choose=button("1. Select All Counter Files");',
             "Victoria combine screen")
replace_once(merge,
             '        if(!victoriaSourceLoaded){status.setText("STEP 1 REQUIRED: Select the original Victoria Excel file before selecting counter files.");status.setTextColor(Color.rgb(255,130,130));return;}\n',
             '',
             "Remove redundant master-file requirement")
replace_once(merge,
             '            VictoriaProduct product=victoriaProducts.get(normalizeBarcode(total.barcode));\n'
             '            if(product==null||product.itemNumber.isEmpty()){victoriaUnmappedBarcodes++;continue;}\n'
             '            total.itemNumber=product.itemNumber;\n'
             '            if(!product.description.isEmpty())total.description=product.description;\n',
             '            if(total.itemNumber==null||total.itemNumber.trim().isEmpty())victoriaUnmappedBarcodes++;\n',
             "Use item data embedded in shared count files")
replace_once(merge,
             '        verified=errors.isEmpty()&&victoriaSourceLoaded&&sourceFiles==candidateFiles&&candidateFiles>0',
             '        verified=errors.isEmpty()&&sourceFiles==candidateFiles&&candidateFiles>0',
             "Remove redundant master verification")
replace_once(merge,
             '        s.append("Original Victoria Excel: ").append(victoriaSourceName).append(" — ").append(victoriaProducts.size()).append(" barcodes\\n");',
             '        s.append("Item numbers and descriptions: embedded in shared counter files\\n");',
             "Verification report source label")
replace_once(merge,
             '        String n=fileName==null?"":fileName.trim();\n'
             '        java.util.regex.Matcher m=java.util.regex.Pattern.compile("(?i)^count(.+?)-batch[0-9]+").matcher(n);',
             '        String n=fileName==null?"":fileName.trim();\n'
             '        java.util.regex.Matcher m=java.util.regex.Pattern.compile("(?i)^(?:count)?(.+?)[-_ ]+batch[ _-]*[0-9]+").matcher(n);',
             "Support short user-first filenames")

# Validation before the signed build.
checks = {
    "release version": "versionCode 30243" in gradle.read_text() and "versionName '3.0.243'" in gradle.read_text(),
    "count-only export action": 'else beginCountedCountExport();' in main.read_text(),
    "zero rows excluded by default": 'row.quantity<=0' in main.read_text() and 'export_quantity_above_zero_only",true' in main.read_text(),
    "counted query": "public List<Row> countedRows(long sessionId)" in db.read_text(),
    "short batch file names": 'return user+" Batch "' in main.read_text(),
    "no Victoria master required": "STEP 1 REQUIRED" not in merge.read_text() and "Select Original Victoria Excel" not in merge.read_text(),
    "combine uses embedded item data": "embedded in shared counter files" in merge.read_text(),
    "workflow uses current prep": ".github/prepare_30243.py" in workflow.read_text(),
}
failed = [name for name, passed in checks.items() if not passed]
if failed:
    raise SystemExit("3.0.243 validation failed: " + ", ".join(failed))
print("Prepared OnHand 3.0.243: count-only user batches, positive quantities by default, user-first filenames, and Victoria combine without importing its master twice.")
