package com.iceinventory.onhand;

import android.content.ContentValues;
import android.content.Context;
import android.database.Cursor;
import android.database.sqlite.SQLiteDatabase;
import android.database.sqlite.SQLiteOpenHelper;

import java.util.ArrayList;
import java.util.List;

public final class InventoryDb extends SQLiteOpenHelper {
    public static final class Row {
        public long id;
        public long sessionId;
        public String barcode;
        public String description;
        public int quantity;
        public String location;
    }

    public static final class Session {
        public long id;
        public String name;
    }

    public InventoryDb(Context context) {
        super(context, "onhand3.db", null, 1);
    }

    @Override public void onCreate(SQLiteDatabase db) {
        db.execSQL("CREATE TABLE sessions (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, created_at INTEGER NOT NULL)");
        db.execSQL("CREATE TABLE locations (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL UNIQUE COLLATE NOCASE)");
        db.execSQL("CREATE TABLE items (id INTEGER PRIMARY KEY AUTOINCREMENT, session_id INTEGER NOT NULL, barcode TEXT NOT NULL, description TEXT NOT NULL DEFAULT '', quantity INTEGER NOT NULL DEFAULT 0, location TEXT NOT NULL DEFAULT '', updated_at INTEGER NOT NULL, UNIQUE(session_id, barcode, location))");
        ContentValues cv = new ContentValues();
        cv.put("name", "Default Inventory");
        cv.put("created_at", System.currentTimeMillis());
        db.insert("sessions", null, cv);
        cv.clear(); cv.put("name", "Main"); db.insert("locations", null, cv);
    }

    @Override public void onUpgrade(SQLiteDatabase db, int oldVersion, int newVersion) { }

    public long createSession(String name) {
        ContentValues cv = new ContentValues();
        cv.put("name", name);
        cv.put("created_at", System.currentTimeMillis());
        return getWritableDatabase().insertOrThrow("sessions", null, cv);
    }

    public List<Session> sessions() {
        ArrayList<Session> out = new ArrayList<>();
        try (Cursor c = getReadableDatabase().rawQuery("SELECT id,name FROM sessions ORDER BY created_at DESC", null)) {
            while (c.moveToNext()) {
                Session s = new Session(); s.id = c.getLong(0); s.name = c.getString(1); out.add(s);
            }
        }
        return out;
    }

    public void addLocation(String name) {
        ContentValues cv = new ContentValues(); cv.put("name", name.trim());
        getWritableDatabase().insertWithOnConflict("locations", null, cv, SQLiteDatabase.CONFLICT_IGNORE);
    }

    public List<String> locations() {
        ArrayList<String> out = new ArrayList<>();
        try (Cursor c = getReadableDatabase().rawQuery("SELECT name FROM locations ORDER BY name COLLATE NOCASE", null)) {
            while (c.moveToNext()) out.add(c.getString(0));
        }
        if (out.isEmpty()) out.add("Main");
        return out;
    }

    public void addOrIncrement(long sessionId, String barcode, String description, int quantity, String location) {
        SQLiteDatabase db = getWritableDatabase();
        String[] args = { String.valueOf(sessionId), barcode, location };
        try (Cursor c = db.rawQuery("SELECT id,quantity,description FROM items WHERE session_id=? AND barcode=? AND location=?", args)) {
            if (c.moveToFirst()) {
                ContentValues cv = new ContentValues();
                cv.put("quantity", c.getInt(1) + quantity);
                if (description != null && !description.trim().isEmpty()) cv.put("description", description.trim());
                cv.put("updated_at", System.currentTimeMillis());
                db.update("items", cv, "id=?", new String[]{String.valueOf(c.getLong(0))});
                return;
            }
        }
        ContentValues cv = new ContentValues();
        cv.put("session_id", sessionId); cv.put("barcode", barcode); cv.put("description", description == null ? "" : description.trim());
        cv.put("quantity", quantity); cv.put("location", location); cv.put("updated_at", System.currentTimeMillis());
        db.insertOrThrow("items", null, cv);
    }

    public void setQuantity(long id, int quantity) {
        ContentValues cv = new ContentValues(); cv.put("quantity", quantity); cv.put("updated_at", System.currentTimeMillis());
        getWritableDatabase().update("items", cv, "id=?", new String[]{String.valueOf(id)});
    }

    public void deleteItem(long id) {
        getWritableDatabase().delete("items", "id=?", new String[]{String.valueOf(id)});
    }

    public List<Row> items(long sessionId) {
        ArrayList<Row> out = new ArrayList<>();
        try (Cursor c = getReadableDatabase().rawQuery("SELECT id,session_id,barcode,description,quantity,location FROM items WHERE session_id=? ORDER BY updated_at DESC", new String[]{String.valueOf(sessionId)})) {
            while (c.moveToNext()) {
                Row r = new Row(); r.id=c.getLong(0); r.sessionId=c.getLong(1); r.barcode=c.getString(2); r.description=c.getString(3); r.quantity=c.getInt(4); r.location=c.getString(5); out.add(r);
            }
        }
        return out;
    }
}
