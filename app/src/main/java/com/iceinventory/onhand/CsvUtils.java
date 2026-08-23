package com.iceinventory.onhand;

import java.util.ArrayList;
import java.util.List;

public final class CsvUtils {
    private CsvUtils() { }

    public static String escape(String s) {
        if (s == null) return "";
        if (s.contains(",") || s.contains("\"") || s.contains("\n") || s.contains("\r")) return "\"" + s.replace("\"", "\"\"") + "\"";
        return s;
    }

    public static String exportRows(List<InventoryDb.Row> rows) {
        StringBuilder b = new StringBuilder("Barcode,Description,Quantity,Location\r\n");
        for (InventoryDb.Row r : rows) {
            b.append(escape(r.barcode)).append(',').append(escape(r.description)).append(',').append(r.quantity).append(',').append(escape(r.location)).append("\r\n");
        }
        return b.toString();
    }

    public static List<String> parseLine(String line) {
        ArrayList<String> out = new ArrayList<>();
        StringBuilder cur = new StringBuilder();
        boolean quoted = false;
        for (int i=0;i<line.length();i++) {
            char ch=line.charAt(i);
            if (ch=='\"') {
                if (quoted && i+1<line.length() && line.charAt(i+1)=='\"') { cur.append('\"'); i++; }
                else quoted=!quoted;
            } else if (ch==',' && !quoted) { out.add(cur.toString()); cur.setLength(0); }
            else cur.append(ch);
        }
        out.add(cur.toString());
        return out;
    }
}
