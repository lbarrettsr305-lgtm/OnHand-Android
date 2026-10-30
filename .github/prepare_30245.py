#!/usr/bin/env python3
"""OnHand 3.0.245: make each counter upload contain only unsent count changes."""
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


# Replay the signed release chain from 3.0.244. Its preparation script expects
# the previous release markers and only the 3.0.243/244 build branch triggers.
if os.environ.get("ONHAND_PREPARED_30244") != "1":
    w = workflow.read_text()
    for current, previous, expected in [
        ("Prepare and verify 3.0.245 incremental counter batches",
         "Prepare and verify 3.0.244 negative quantity safeguards", 1),
        (".github/prepare_30245.py", ".github/prepare_30244.py", 1),
        ("iCE-Onhand-Inventory-3.0.245", "iCE-Onhand-Inventory-3.0.244", 4),
    ]:
        if w.count(current) != expected:
            raise SystemExit("3.0.245 workflow marker missing: " + current)
        w = w.replace(current, previous)
    for branch in [
        ", feature/30245-incremental-counter-batches",
        ", feature/30244-negative-quantity-verification",
    ]:
        if w.count(branch) != 2:
            raise SystemExit("3.0.245 workflow branch marker missing: " + branch)
        w = w.replace(branch, "")
    workflow.write_text(w)
    runpy.run_path(str(root / ".github/prepare_30244.py"), run_name="__main__")

for old, new, expected in [
    ("Prepare and verify 3.0.244 negative quantity safeguards",
     "Prepare and verify 3.0.245 incremental counter batches", 1),
    (".github/prepare_30244.py", ".github/prepare_30245.py", 1),
    ("iCE-Onhand-Inventory-3.0.244", "iCE-Onhand-Inventory-3.0.245", 4),
]:
    w = workflow.read_text()
    if w.count(old) != expected:
        raise SystemExit("3.0.244 workflow restore marker missing: " + old)
    workflow.write_text(w.replace(old, new))

w = workflow.read_text()
branch = "feature/30244-negative-quantity-verification ]"
if w.count(branch) != 2:
    raise SystemExit("3.0.245 workflow trigger anchor missing")
workflow.write_text(w.replace(branch, "feature/30244-negative-quantity-verification, feature/30245-incremental-counter-batches ]"))

gradle = root / "app/build.gradle"
replace_once(gradle, "versionCode 30244", "versionCode 30245", "Gradle version code")
replace_once(gradle, "versionName '3.0.244'", "versionName '3.0.245'", "Gradle version name")
manifest = root / "app/src/main/AndroidManifest.xml"
replace_once(manifest, "iCE Onhand 3.0.244", "iCE Onhand 3.0.245", "Manifest version")
main = root / "app/src/main/java/com/iceinventory/onhand/MainActivity.java"
replace_once(main, "Onhand Inventory 3.0.244", "Onhand Inventory 3.0.245", "Main screen version")

# The 3.0.244 flow exported all rows ever counted on the device. Continue each
# counter's sequence from the last successfully saved COUNTED batch, and export
# only scan-history changes after that marker. A correction such as -14 remains
# in its own later batch and is not removed by the positive-only report setting.
replace_once(
    main,
    '    private void beginCountedCountExport() {\n'
    '        List<InventoryDb.Row> rows=db.countedRows(sessionId);\n'
    '        if(rows.isEmpty()){toast("No counted item lines to send");return;}\n'
    '        pendingExportInternetOnly=false;pendingExportLocationQuantityReport=false;pendingExportLocationDetailReport=false;\n'
    '        pendingBatchMode=4;pendingBatchNumber=db.nextCompleteExportNumber(sessionId);\n'
    '        long last=db.maxHistoryId(sessionId);pendingBatchFirstHistoryId=db.firstHistoryIdAfter(sessionId,0L,last);pendingBatchLastHistoryId=last;pendingBatchReplayId=0L;\n'
    '        startExportFormatFlow();\n'
    '    }',
    '    private void beginCountedCountExport() {\n'
    '        long previous=db.lastCountedBatchHistoryId(sessionId);\n'
    '        long last=db.maxHistoryId(sessionId);\n'
    '        List<InventoryDb.Row> rows=db.batchRows(sessionId,previous,last);\n'
    '        if(rows.isEmpty()){toast("No new count changes since the last batch was sent");return;}\n'
    '        pendingExportInternetOnly=false;pendingExportLocationQuantityReport=false;pendingExportLocationDetailReport=false;\n'
    '        pendingBatchMode=4;pendingBatchNumber=db.nextCountedBatchNumber(sessionId);\n'
    '        pendingBatchAfterHistoryId=previous;pendingBatchFirstHistoryId=db.firstHistoryIdAfter(sessionId,previous,last);pendingBatchLastHistoryId=last;pendingBatchReplayId=0L;\n'
    '        startExportFormatFlow();\n'
    '    }',
    "Incremental counted batch selection",
)

replace_once(
    main,
    '            } else if(pendingBatchMode==4) {\n'
    '                List<InventoryDb.Row> rows=new ArrayList<>(db.countedRows(sessionId));\n'
    '                if(prefs().getBoolean("export_quantity_above_zero_only",true))rows.removeIf(row->row==null||row.quantity<=0);\n'
    '                if(rows.isEmpty())throw new Exception("No positive-quantity counted lines are available to send");\n'
    '                if(pendingExportExcel)SimpleXlsxWriter.writeBatch(os,rows,prefs());',
    '            } else if(pendingBatchMode==4) {\n'
    '                List<InventoryDb.Row> rows=new ArrayList<>(db.batchRows(sessionId,pendingBatchAfterHistoryId,pendingBatchLastHistoryId));\n'
    '                if(rows.isEmpty())throw new Exception("No net quantity changes are available in this batch");\n'
    '                if(pendingExportExcel)SimpleXlsxWriter.writeBatch(os,rows,prefs());',
    "Write only unsent batch changes and retain signed adjustments",
)

replace_once(
    main,
    '    private long pendingBatchLastHistoryId=0L;\n',
    '    private long pendingBatchLastHistoryId=0L;\n    private long pendingBatchAfterHistoryId=0L;\n',
    "Remember the previous batch boundary",
)

db = root / "app/src/main/java/com/iceinventory/onhand/InventoryDb.java"
replace_once(
    db,
    '    public List<Row> batchRows(long sessionId,long afterExclusive,long throughInclusive) {',
    '    public long lastCountedBatchHistoryId(long sessionId) {\n'
    '        if(sessionId<=0)return 0L;\n'
    '        ensureRecoveryTables(getReadableDatabase());\n'
    '        try(Cursor c=getReadableDatabase().rawQuery("SELECT COALESCE(MAX(last_history_id),0) FROM export_batches WHERE session_id=? AND export_type=\'COUNTED\'",new String[]{String.valueOf(sessionId)})) {\n'
    '            return c.moveToFirst()?c.getLong(0):0L;\n'
    '        }\n'
    '    }\n\n'
    '    public int nextCountedBatchNumber(long sessionId) {\n'
    '        if(sessionId<=0)return 1;\n'
    '        ensureRecoveryTables(getReadableDatabase());\n'
    '        try(Cursor c=getReadableDatabase().rawQuery("SELECT COALESCE(MAX(batch_no),0)+1 FROM export_batches WHERE session_id=? AND export_type=\'COUNTED\'",new String[]{String.valueOf(sessionId)})) {\n'
    '            return c.moveToFirst()?Math.max(1,c.getInt(0)):1;\n'
    '        }\n'
    '    }\n\n'
    '    public List<Row> batchRows(long sessionId,long afterExclusive,long throughInclusive) {',
    "Counted batch ledger helpers",
)

# Make Change Location easy to distinguish on the compact phone controls.
replace_once(
    main,
    'Button addLoc=button("Change\\nLocation",0);',
    'Button addLoc=button("Change\\nLocation",2);addLoc.setTypeface(Typeface.DEFAULT_BOLD,Typeface.BOLD);addLoc.setTextSize(17);',
    "Readable Change Location button",
)

checks = {
    "release version": "versionCode 30245" in gradle.read_text() and "versionName '3.0.245'" in gradle.read_text(),
    "batch delta export": "db.batchRows(sessionId,pendingBatchAfterHistoryId,pendingBatchLastHistoryId)" in main.read_text(),
    "previous COUNTED batch marker": "lastCountedBatchHistoryId(sessionId)" in main.read_text(),
    "count-only sequence": "nextCountedBatchNumber(sessionId)" in main.read_text(),
    "no cumulative countedRows export": "List<InventoryDb.Row> rows=new ArrayList<>(db.countedRows(sessionId))" not in main.read_text(),
    "negative adjustments retained": "SimpleXlsxWriter.writeBatch(os,rows,prefs())" in main.read_text() and "BatchExportText.exportRows(rows,prefs())" in main.read_text(),
    "location control is bold and high contrast": 'Button addLoc=button("Change\\nLocation",2);addLoc.setTypeface(Typeface.DEFAULT_BOLD,Typeface.BOLD);' in main.read_text(),
    "history marker method": "public long lastCountedBatchHistoryId(long sessionId)" in db.read_text(),
    "batch count sequence method": "public int nextCountedBatchNumber(long sessionId)" in db.read_text(),
}
failed = [name for name, passed in checks.items() if not passed]
if failed:
    raise SystemExit("3.0.245 validation failed: " + ", ".join(failed))
print("Prepared OnHand 3.0.245: each counted upload contains only changes since the prior saved batch, keeps verified negative corrections, and highlights Change Location.")
