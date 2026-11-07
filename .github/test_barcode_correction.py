"""SQLite regression checks for barcode correction's identifier-only updates."""
import re
import sqlite3
from pathlib import Path

source=Path("app/src/main/java/com/iceinventory/onhand/InventoryDb.java").read_text()
method=source.split("public void correctBarcode(",1)[1].split("public double quantityForBarcode(",1)[0]
tables=re.search(r'String\[\] tables=\{([^}]+)\}',method).group(1)
tables=re.findall(r'"([^"]+)"',tables)
assert tables==["items","scan_history","store_setup_new_items","retail_price_changes"]
assert 'values.put("barcode",newCode)' in method
assert 'values.put("quantity"' not in method and 'values.put("updated_at"' not in method
assert "beginTransaction()" in method and "setTransactionSuccessful()" in method and "endTransaction()" in method
assert method.index("createRecoverySnapshot")<method.index('for(String table:tables)sql.update')
assert method.index('if(c.moveToFirst())throw')<method.index('for(String table:tables)sql.update')

def setup():
    c=sqlite3.connect(":memory:")
    for ddl in re.findall(r'"(CREATE TABLE IF NOT EXISTS [^"]+)"',source):
        c.execute(ddl)
    for session,code,location,quantity,stamp in [(1,"074164614700","Aisle-01",19,100),(1,"074164614700","Back",4,200),(2,"074164614700","Aisle-01",9,300)]:
        c.execute("INSERT INTO items(session_id,barcode,description,item_number,price,category_name,quantity,location,updated_at) VALUES(?,?,?,'ITEM9','3.99','Beauty',?,?,?)",(session,code,"BEAUTY TIME ARDEL",quantity,location,stamp))
        c.execute("INSERT INTO scan_history(session_id,barcode,description,quantity_delta,location,source,created_at) VALUES(?,?,?, ?,?,'COUNT',?)",(session,code,"BEAUTY TIME ARDEL",quantity,location,stamp))
    c.execute("INSERT INTO store_setup_new_items VALUES(1,'074164614700','BEAUTY TIME ARDEL','MANUAL','Chief',100)")
    c.execute("INSERT INTO retail_price_changes(session_id,barcode,description,old_price,new_price,changed_by,source,changed_at) VALUES(1,'074164614700','BEAUTY TIME ARDEL','3.49','3.99','Chief','MANUAL',101)")
    c.execute("INSERT INTO export_batches(session_id,batch_no,created_at,first_history_id,last_history_id,line_count,unit_total) VALUES(1,1,110,1,2,2,23)")
    c.commit()
    return c

def correct(c):
    with c:
        for table in tables:
            if c.execute("SELECT 1 FROM "+table+" WHERE session_id=? AND barcode=? COLLATE NOCASE LIMIT 1",(1,"074764614100")).fetchone():
                raise ValueError("Barcode conflict")
        for table in tables:
            c.execute("UPDATE "+table+" SET barcode=? WHERE session_id=? AND barcode=?",("074764614100",1,"074164614700"))

c=setup()
before_items=c.execute("SELECT id,session_id,description,item_number,price,category_name,quantity,location,updated_at FROM items ORDER BY id").fetchall()
before_history=c.execute("SELECT id,session_id,quantity_delta,location,source,created_at FROM scan_history ORDER BY id").fetchall()
before_batches=c.execute("SELECT * FROM export_batches").fetchall()
correct(c)
assert before_items==c.execute("SELECT id,session_id,description,item_number,price,category_name,quantity,location,updated_at FROM items ORDER BY id").fetchall()
assert before_history==c.execute("SELECT id,session_id,quantity_delta,location,source,created_at FROM scan_history ORDER BY id").fetchall()
assert before_batches==c.execute("SELECT * FROM export_batches").fetchall()
assert c.execute("SELECT COUNT(*) FROM items WHERE session_id=1 AND barcode='074764614100'").fetchone()[0]==2
assert c.execute("SELECT barcode FROM items WHERE session_id=2").fetchone()[0]=="074164614700"
for table in tables:
    assert c.execute("SELECT COUNT(*) FROM "+table+" WHERE session_id=1 AND barcode='074164614700'").fetchone()[0]==0

# Even a target with zero count must block, preserving the original records.
c=setup()
c.execute("INSERT INTO items(session_id,barcode,location,updated_at) VALUES(1,'074764614100','Other',400)");c.commit()
before=c.execute("SELECT * FROM items ORDER BY id").fetchall()
try:correct(c);raise AssertionError("Conflict allowed")
except ValueError:pass
assert before==c.execute("SELECT * FROM items ORDER BY id").fetchall()
# Historical target identifiers also block, avoiding collisions in old batches.
c=setup()
c.execute("INSERT INTO scan_history(session_id,barcode,created_at) VALUES(1,'074764614100',400)");c.commit()
try:correct(c);raise AssertionError("Historical conflict allowed")
except ValueError:pass

# A failure after the item update must roll the whole operation back.
c=setup()
before=c.execute("SELECT * FROM items ORDER BY id").fetchall()
c.execute("CREATE TRIGGER reject_update BEFORE UPDATE ON scan_history BEGIN SELECT RAISE(ABORT,'forced failure'); END;");c.commit()
try:correct(c);raise AssertionError("Failure was not raised")
except sqlite3.IntegrityError:pass
assert before==c.execute("SELECT * FROM items ORDER BY id").fetchall()
print("Barcode correction SQL checks passed: quantities, locations, metadata, history/batch IDs, session isolation, conflicts, rollback.")
