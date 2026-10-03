#!/usr/bin/env python3
from pathlib import Path
import runpy

root=Path(__file__).resolve().parents[1]
runpy.run_path(str(root/".github"/"prepare_30192.py"),run_name="__main__")

gradle=root/"app"/"build.gradle"
s=gradle.read_text()
if "versionName '3.0.192'" not in s:raise SystemExit("3.0.192 version source not found")
s=s.replace("versionCode 30192","versionCode 30193").replace("versionName '3.0.192'","versionName '3.0.193'")
gradle.write_text(s)

manifest=root/"app"/"src"/"main"/"AndroidManifest.xml"
s=manifest.read_text()
if "iCE Onhand 3.0.192" not in s:raise SystemExit("3.0.192 app label not found")
manifest.write_text(s.replace("iCE Onhand 3.0.192","iCE Onhand 3.0.193"))

main=root/"app"/"src"/"main"/"java"/"com"/"iceinventory"/"onhand"/"MainActivity.java"
s=main.read_text()
s=s.replace("Onhand Inventory 3.0.192","Onhand Inventory 3.0.193")
old='''        long after=db.lastNewBatchHistoryId(sessionId),through=db.maxHistoryId(sessionId);
        if(through<=after){toast("No new counts since the last batch");return;}'''
new='''        int recovered=db.recoverMissingNewBatchHistory(sessionId);
        long after=db.lastNewBatchHistoryId(sessionId),through=db.maxHistoryId(sessionId);
        if(through<=after){toast("No new counts since the last batch");return;}
        if(recovered>0)toast("Recovered "+recovered+" unlogged count lines for Batch "+String.format(Locale.US,"%02d",db.nextBatchNumber(sessionId)));'''
if s.count(old)!=1:raise SystemExit("New batch recovery hook anchor not found")
s=s.replace(old,new,1)
main.write_text(s)

db=root/"app"/"src"/"main"/"java"/"com"/"iceinventory"/"onhand"/"InventoryDb.java"
d=db.read_text()
old='''        db.insertOrThrow("items", null, cv);
    }

    private String canonicalLocation(String location) {'''
new='''        db.insertOrThrow("items", null, cv);
        if(quantity!=0)recordHistory(sessionId,safeBarcode,description,quantity,safeLocation,"COUNT");
    }

    private String canonicalLocation(String location) {'''
if d.count(old)!=1:raise SystemExit("First-location count history anchor not found")
d=d.replace(old,new,1)

anchor='''    public int nextBatchNumber(long sessionId) {'''
method='''    /** Recover first counts saved before their history entry was recorded. */
    public int recoverMissingNewBatchHistory(long sessionId) {
        if(sessionId<=0)return 0;
        ensureRecoveryTables(getWritableDatabase());
        long afterHistoryId=0L,lastBatchTime=0L;
        try(Cursor c=getReadableDatabase().rawQuery("SELECT last_history_id,created_at FROM export_batches WHERE session_id=? AND export_type='NEW' ORDER BY batch_no DESC,id DESC LIMIT 1",new String[]{String.valueOf(sessionId)})) {
            if(c.moveToFirst()){afterHistoryId=c.getLong(0);lastBatchTime=c.getLong(1);}
        }
        int recovered=0;
        for(Row row:items(sessionId)) {
            if(row.quantity==0||(lastBatchTime>0&&row.updatedAt<=lastBatchTime))continue;
            boolean alreadyLogged=false;
            try(Cursor c=getReadableDatabase().rawQuery("SELECT 1 FROM scan_history WHERE session_id=? AND barcode=? AND location=? COLLATE NOCASE AND id>? LIMIT 1",new String[]{String.valueOf(sessionId),row.barcode==null?"":row.barcode,row.location==null?"":row.location,String.valueOf(afterHistoryId)})) {
                alreadyLogged=c.moveToFirst();
            }
            if(!alreadyLogged) {
                recordHistory(sessionId,row.barcode,row.description,row.quantity,row.location,"COUNT_RECOVERY");
                recovered++;
            }
        }
        return recovered;
    }

'''
if d.count(anchor)!=1:raise SystemExit("Batch history recovery method anchor not found")
d=d.replace(anchor,method+anchor,1)
db.write_text(d)

checks={
    "version":"versionName '3.0.193'" in gradle.read_text(),
    "first location insert records history":"if(quantity!=0)recordHistory(sessionId,safeBarcode,description,quantity,safeLocation,\"COUNT\")" in d,
    "pre-batch recovery query":"recoverMissingNewBatchHistory(sessionId)" in s,
    "only post-export items recovered":"row.updatedAt<=lastBatchTime" in d,
    "existing history not duplicated":"alreadyLogged=c.moveToFirst()" in d,
}
failed=[k for k,v in checks.items() if not v]
if failed:raise SystemExit("3.0.193 verification failed: "+", ".join(failed))
print("Prepared iCE OnHand 3.0.193: recover first-location counts for Batch 2")
