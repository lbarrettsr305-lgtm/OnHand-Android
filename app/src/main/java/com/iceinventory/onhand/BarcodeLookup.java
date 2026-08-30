package com.iceinventory.onhand;

import org.json.JSONArray;
import org.json.JSONObject;

import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.net.HttpURLConnection;
import java.net.URL;
import java.net.URLEncoder;
import java.nio.charset.StandardCharsets;

public final class BarcodeLookup {
    private BarcodeLookup() {}

    public static String lookupDescription(String barcode) throws Exception {
        String encoded = URLEncoder.encode(barcode, StandardCharsets.UTF_8.name());
        URL url = new URL("https://api.upcitemdb.com/prod/trial/lookup?upc=" + encoded);
        HttpURLConnection conn = (HttpURLConnection) url.openConnection();
        conn.setRequestMethod("GET");
        conn.setConnectTimeout(8000);
        conn.setReadTimeout(8000);
        conn.setRequestProperty("Accept", "application/json");
        conn.setRequestProperty("User-Agent", "OnHand-Android/3");
        int status = conn.getResponseCode();
        if (status == 404) return null;
        if (status == 429) throw new Exception("Internet barcode lookup daily/rate limit reached");
        if (status < 200 || status >= 300) throw new Exception("Internet barcode lookup failed (" + status + ")");

        StringBuilder body = new StringBuilder();
        try (BufferedReader br = new BufferedReader(new InputStreamReader(conn.getInputStream(), StandardCharsets.UTF_8))) {
            String line;
            while ((line = br.readLine()) != null) body.append(line);
        } finally {
            conn.disconnect();
        }

        JSONObject root = new JSONObject(body.toString());
        JSONArray items = root.optJSONArray("items");
        if (items == null || items.length() == 0) return null;
        JSONObject item = items.optJSONObject(0);
        if (item == null) return null;
        String title = item.optString("title", "").trim();
        String brand = item.optString("brand", "").trim();
        if (!title.isEmpty()) return title;
        if (!brand.isEmpty()) return brand;
        return null;
    }
}
