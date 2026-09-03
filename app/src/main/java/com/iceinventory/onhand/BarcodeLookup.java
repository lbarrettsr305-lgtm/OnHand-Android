package com.iceinventory.onhand;

import org.json.JSONArray;
import org.json.JSONObject;

import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.net.HttpURLConnection;
import java.net.URL;
import java.net.URLEncoder;
import java.nio.charset.StandardCharsets;
import java.util.Locale;

public final class BarcodeLookup {
    private BarcodeLookup() {}

    public static final class Result {
        public final String description;
        public final String imageUrl;
        public final String price;

        public Result(String description, String imageUrl, String price) {
            this.description = description == null ? "" : description;
            this.imageUrl = imageUrl == null ? "" : imageUrl;
            this.price = price == null ? "" : price;
        }
    }

    public static Result lookup(String barcode) throws Exception {
        String encoded = URLEncoder.encode(barcode, StandardCharsets.UTF_8.name());
        URL url = new URL("https://api.upcitemdb.com/prod/trial/lookup?upc=" + encoded);
        HttpURLConnection conn = (HttpURLConnection) url.openConnection();
        conn.setRequestMethod("GET");
        conn.setConnectTimeout(8000);
        conn.setReadTimeout(8000);
        conn.setRequestProperty("Accept", "application/json");
        conn.setRequestProperty("User-Agent", "iCE-Onhand-Inventory/3");
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
        String description = !title.isEmpty() ? title : brand;

        String imageUrl = "";
        JSONArray images = item.optJSONArray("images");
        if (images != null && images.length() > 0) imageUrl = images.optString(0, "").trim();

        String price = "";
        double low = item.optDouble("lowest_recorded_price", 0d);
        if (low > 0d) price = String.format(Locale.US, "%.2f", low);
        if (price.isEmpty()) {
            JSONArray offers=item.optJSONArray("offers");
            if (offers!=null && offers.length()>0) {
                JSONObject offer=offers.optJSONObject(0);
                if (offer!=null) {
                    double p=offer.optDouble("price",0d);
                    if(p>0d) price=String.format(Locale.US,"%.2f",p);
                }
            }
        }

        if (description.isEmpty() && imageUrl.isEmpty() && price.isEmpty()) return null;
        return new Result(description, imageUrl, price);
    }

    public static String lookupDescription(String barcode) throws Exception {
        Result result = lookup(barcode);
        return result == null ? null : result.description;
    }
}
