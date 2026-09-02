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

    public static final class Result {
        public final String description;
        public final String imageUrl;
        public final String source;
        public Result(String description,String imageUrl,String source){
            this.description=description==null?"":description;
            this.imageUrl=imageUrl==null?"":imageUrl;
            this.source=source==null?"":source;
        }
    }

    public static Result lookup(String barcode) throws Exception {
        String code=barcode==null?"":barcode.trim();
        if(code.isEmpty()) return null;
        Exception firstError=null;
        try { Result r=lookupUpcItemDb(code); if(useful(r)) return r; } catch(Exception e){ firstError=e; }
        try { Result r=lookupOpenFoodFacts(code); if(useful(r)) return r; } catch(Exception ignored) {}
        // Try common GTIN representations because some databases store the UPC-A form
        // while the inventory may be scanning/storing a padded GTIN-14 form.
        String alt=stripGtinPadding(code);
        if(!alt.equals(code)) {
            try { Result r=lookupUpcItemDb(alt); if(useful(r)) return r; } catch(Exception ignored) {}
            try { Result r=lookupOpenFoodFacts(alt); if(useful(r)) return r; } catch(Exception ignored) {}
        }
        if(firstError!=null && firstError.getMessage()!=null && firstError.getMessage().contains("rate limit"))
            throw new Exception("Primary lookup limit reached; backup sources found no match");
        return null;
    }

    private static boolean useful(Result r){ return r!=null && (!r.description.trim().isEmpty() || !r.imageUrl.trim().isEmpty()); }

    private static String stripGtinPadding(String code){
        if(!code.matches("\\d+")) return code;
        String s=code;
        while(s.length()>12 && s.startsWith("0")) s=s.substring(1);
        return s;
    }

    private static Result lookupUpcItemDb(String barcode) throws Exception {
        String encoded=URLEncoder.encode(barcode,StandardCharsets.UTF_8.name());
        JSONObject root=getJson("https://api.upcitemdb.com/prod/trial/lookup?upc="+encoded,"UPCitemdb");
        JSONArray items=root.optJSONArray("items");
        if(items==null||items.length()==0) return null;
        JSONObject item=items.optJSONObject(0); if(item==null) return null;
        String title=item.optString("title","").trim();
        String brand=item.optString("brand","").trim();
        String desc=title.isEmpty()?brand:title;
        String image=""; JSONArray images=item.optJSONArray("images");
        if(images!=null&&images.length()>0) image=images.optString(0,"").trim();
        return new Result(desc,image,"UPCitemdb");
    }

    private static Result lookupOpenFoodFacts(String barcode) throws Exception {
        String encoded=URLEncoder.encode(barcode,StandardCharsets.UTF_8.name());
        JSONObject root=getJson("https://world.openfoodfacts.org/api/v2/product/"+encoded+"?fields=product_name,product_name_en,brands,quantity,image_front_url,image_url","Open Food Facts");
        if(root.optInt("status",0)!=1) return null;
        JSONObject p=root.optJSONObject("product"); if(p==null) return null;
        String name=p.optString("product_name","").trim(); if(name.isEmpty()) name=p.optString("product_name_en","").trim();
        String brand=p.optString("brands","").trim(); String quantity=p.optString("quantity","").trim();
        StringBuilder d=new StringBuilder();
        if(!brand.isEmpty() && !name.toLowerCase().contains(brand.toLowerCase())) d.append(brand).append(" ");
        d.append(name);
        if(!quantity.isEmpty() && d.indexOf(quantity)<0) d.append(" ").append(quantity);
        String image=p.optString("image_front_url","").trim(); if(image.isEmpty()) image=p.optString("image_url","").trim();
        return new Result(d.toString().trim(),image,"Open Food Facts");
    }

    private static JSONObject getJson(String address,String source) throws Exception {
        HttpURLConnection conn=(HttpURLConnection)new URL(address).openConnection();
        try {
            conn.setRequestMethod("GET"); conn.setConnectTimeout(8000); conn.setReadTimeout(8000);
            conn.setRequestProperty("Accept","application/json");
            conn.setRequestProperty("User-Agent","iCE-Onhand-Inventory/3.0 (inventory barcode lookup)");
            int status=conn.getResponseCode();
            if(status==404) return new JSONObject();
            if(status==429) throw new Exception(source+" rate limit reached");
            if(status<200||status>=300) throw new Exception(source+" lookup failed ("+status+")");
            StringBuilder body=new StringBuilder();
            try(BufferedReader br=new BufferedReader(new InputStreamReader(conn.getInputStream(),StandardCharsets.UTF_8))){ String line; while((line=br.readLine())!=null) body.append(line); }
            return new JSONObject(body.toString());
        } finally { conn.disconnect(); }
    }

    public static String lookupDescription(String barcode) throws Exception { Result r=lookup(barcode); return r==null?null:r.description; }
}
