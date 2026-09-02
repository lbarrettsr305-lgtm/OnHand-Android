package com.iceinventory.onhand;

import android.content.ContentValues;
import android.content.Context;
import android.database.Cursor;
import android.database.sqlite.SQLiteDatabase;
import android.database.sqlite.SQLiteOpenHelper;

import java.util.ArrayList;
import java.util.List;
import java.util.Locale;

public final class InventoryDb extends SQLiteOpenHelper {
    public static final String DB_NAME = "onhand302.db";
    private static final int DB_VERSION = 1;
    private static final int MIN_PARTIAL_LENGTH = 4;

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
        super(context.getApplicationContext(), DB_NAME, null, DB_VERSION);
        setWriteAheadLoggingEnabled(true);
    }

    @Override public void onCreate(SQLiteDatabase db) {
        db.beginTransaction();
        try {
            db.execSQL("CREATE TABLE IF NOT EXISTS sessions (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, created_at INTEGER NOT NULL)");
            db.execSQL("CREATE TABLE IF NOT EXISTS locations (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL UNIQUE COLLATE NOCASE)");
            db.execSQL("CREATE TABLE IF NOT EXISTS items (id INTEGER PRIMARY KEY AUTOINCREMENT, session_id INTEGER NOT NULL, barcode TEXT NOT NULL, description TEXT NOT NULL DEFAULT '', quantity INTEGER NOT NULL DEFAULT 0, location TEXT NOT NULL DEFAULT '', updated_at INTEGER NOT NULL, UNIQUE(session_id, barcode, location))");
            ensureDefaults(db);
            db.setTransactionSuccessful();
        } finally {
            db.endTransaction();
        }
    }

    @Override public void onOpen(SQLiteDatabase db) {
        super.onOpen(db);
        if (!db.isReadOnly()) ensureDefaults(db);
    }

    private void ensureDefaults(SQLiteDatabase db) {
        try (Cursor c = db.rawQuery("SELECT COUNT(*) FROM sessions", null)) {
            if (c.moveToFirst() && c.getLong(0) == 0) {
                ContentValues cv = new ContentValues();
                cv.put("name", "Default Inventory");
                cv.put("created_at", System.currentTimeMillis());
                db.insertOrThrow("sessions", null, cv);
            }
        }
        ContentValues loc = new ContentValues();
        loc.put("name", "Main");
        db.insertWithOnConflict("locations", null, loc, SQLiteDatabase.CONFLICT_IGNORE);
    }

    @Override public void onUpgrade(SQLiteDatabase db, int oldVersion, int newVersion) {
    }

    public void verifyReady() {
        SQLiteDatabase db = getWritableDatabase();
        try (Cursor c = db.rawQuery("SELECT name FROM sqlite_master WHERE type='table' AND name='sessions'", null)) {
            if (!c.moveToFirst()) throw new IllegalStateException("Inventory database did not initialize");
        }
        ensureDefaults(db);
    }

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
        if (name == null || name.trim().isEmpty()) return;
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

    private String normalizeBarcode(String value) {
        if (value == null) return "";
        String upper = value.trim().toUpperCase(Locale.US);
        StringBuilder out = new StringBuilder(upper.length());
        for (int i = 0; i < upper.length(); i++) {
            char ch = upper.charAt(i);
            if (Character.isLetterOrDigit(ch)) out.append(ch);
        }
        return out.toString();
    }

    private String resolveBarcode(long sessionId, String scanned) {
        if (sessionId <= 0 || scanned == null || scanned.trim().isEmpty()) return null;
        String raw = scanned.trim();

        try (Cursor c = getReadableDatabase().rawQuery(
                "SELECT barcode FROM items WHERE session_id=? AND barcode=? LIMIT 1",
                new String[]{String.valueOf(sessionId), raw})) {
            if (c.moveToFirst()) return c.getString(0);
        }

        String scanNorm = normalizeBarcode(raw);
        if (scanNorm.length() < MIN_PARTIAL_LENGTH) return null;

        String unique = null;
        try (Cursor c = getReadableDatabase().rawQuery(
                "SELECT DISTINCT barcode FROM items WHERE session_id=?",
                new String[]{String.valueOf(sessionId)})) {
            while (c.moveToNext()) {
                String candidate = c.getString(0);
                String candidateNorm = normalizeBarcode(candidate);
                if (candidateNorm.length() < MIN_PARTIAL_LENGTH) continue;

                boolean match = candidateNorm.contains(scanNorm) || scanNorm.contains(candidateNorm);
                if (!match) continue;

                if (unique == null) {
                    unique = candidate;
                } else if (!normalizeBarcode(unique).equals(candidateNorm)) {
                    return null;
                }
            }
        }
        return unique;
    }

    public boolean barcodeExists(long sessionId, String barcode) {
        return resolveBarcode(sessionId, barcode) != null;
    }

    public String descriptionForBarcode(long sessionId, String barcode) {
        String resolved = resolveBarcode(sessionId, barcode);
        if (resolved == null) return "";
        try (Cursor c = getReadableDatabase().rawQuery(
                "SELECT description FROM items WHERE session_id=? AND barcode=? AND description<>'' ORDER BY updated_at DESC LIMIT 1",
                new String[]{String.valueOf(sessionId), resolved})) {
            return c.moveToFirst() ? c.getString(0) : "";
        }
    }

    public void addOrIncrement(long sessionId, String barcode, String description, int quantity, String location) {
        addOrIncrementInternal(sessionId, barcode, description, quantity, location, true);
    }

    public void addOrIncrementExact(long sessionId, String barcode, String description, int quantity, String location) {
        addOrIncrementInternal(sessionId, barcode, description, quantity, location, false);
    }

    private void addOrIncrementInternal(long sessionId, String barcode, String description, int quantity, String location, boolean allowPartialResolution) {
        if (sessionId <= 0) throw new IllegalStateException("No active inventory session");
        SQLiteDatabase db = getWritableDatabase();
        String enteredBarcode = barcode == null ? "" : barcode.trim();
        String safeBarcode = enteredBarcode;
        if (allowPartialResolution) {
            String resolved = resolveBarcode(sessionId, enteredBarcode);
            if (resolved != null) safeBarcode = resolved;
        }
        String safeLocation = location == null || location.trim().isEmpty() ? "Main" : location.trim();
        String[] args = { String.valueOf(sessionId), safeBarcode, safeLocation };
        try (Cursor c = db.rawQuery("SELECT id,quantity FROM items WHERE session_id=? AND barcode=? AND location=?", args)) {
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
        cv.put("session_id", sessionId); cv.put("barcode", safeBarcode); cv.put("description", description == null ? "" : description.trim());
        cv.put("quantity", quantity); cv.put("location", safeLocation); cv.put("updated_at", System.currentTimeMillis());
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
        if (sessionId <= 0) return out;
        try (Cursor c = getReadableDatabase().rawQuery("SELECT id,session_id,barcode,description,quantity,location FROM items WHERE session_id=? ORDER BY updated_at DESC", new String[]{String.valueOf(sessionId)})) {
            while (c.moveToNext()) {
                Row r = new Row(); r.id=c.getLong(0); r.sessionId=c.getLong(1); r.barcode=c.getString(2); r.description=c.getString(3); r.quantity=c.getInt(4); r.location=c.getString(5); out.add(r);
            }
        }
        return out;
    }
}
