package com.iceinventory.onhand;

import org.json.JSONArray;
import org.json.JSONObject;

import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.net.HttpURLConnection;
import java.net.URL;
import java.net.URLEncoder;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.List;
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
        List<String> candidates=lookupCandidates(barcode);
        Exception lastError=null;

        for(String code:candidates){
            try{
                Result r=lookupUpcItemDb(code);
                if(r!=null)return r;
            }catch(Exception e){lastError=e;}
        }

        String[] domains={
                "world.openfoodfacts.org",
                "world.openbeautyfacts.org",
                "world.openpetfoodfacts.org",
                "world.openproductsfacts.org"
        };
        boolean reachedOpenFacts=false;
        for(String code:candidates){
            for(String domain:domains){
                try{
                    Result r=lookupOpenFacts(domain,code);
                    reachedOpenFacts=true;
                    if(r!=null)return r;
                }catch(Exception e){lastError=e;}
            }
        }

        if(!reachedOpenFacts&&lastError!=null)throw lastError;
        return null;
    }

    private static Result lookupUpcItemDb(String barcode) throws Exception {
        String encoded = URLEncoder.encode(barcode, StandardCharsets.UTF_8.name());
        URL url = new URL("https://api.upcitemdb.com/prod/trial/lookup?upc=" + encoded);
        HttpURLConnection conn = open(url);
        int status = conn.getResponseCode();
        if (status == 404) {conn.disconnect();return null;}
        if (status == 429) {conn.disconnect();throw new Exception("UPCitemdb rate limit reached");}
        if (status < 200 || status >= 300) {conn.disconnect();throw new Exception("UPCitemdb lookup failed ("+status+")");}

        JSONObject root=new JSONObject(readBody(conn));
        JSONArray items=root.optJSONArray("items");
        if(items==null||items.length()==0)return null;
        JSONObject item=items.optJSONObject(0);
        if(item==null)return null;

        String title=item.optString("title","").trim();
        String brand=item.optString("brand","").trim();
        String description=!title.isEmpty()?title:brand;

        String imageUrl="";
        JSONArray images=item.optJSONArray("images");
        if(images!=null&&images.length()>0)imageUrl=images.optString(0,"").trim();

        String price="";
        double low=item.optDouble("lowest_recorded_price",0d);
        if(low>0d)price=String.format(Locale.US,"%.2f",low);
        if(price.isEmpty()){
            JSONArray offers=item.optJSONArray("offers");
            if(offers!=null&&offers.length()>0){
                JSONObject offer=offers.optJSONObject(0);
                if(offer!=null){
                    double p=offer.optDouble("price",0d);
                    if(p>0d)price=String.format(Locale.US,"%.2f",p);
                }
            }
        }

        if(description.isEmpty()&&imageUrl.isEmpty()&&price.isEmpty())return null;
        return new Result(description,imageUrl,price);
    }

    private static Result lookupOpenFacts(String domain,String barcode) throws Exception {
        String encoded=URLEncoder.encode(barcode,StandardCharsets.UTF_8.name()).replace("+","%20");
        String fields="product_name,product_name_en,generic_name,brands,image_front_url,image_url";
        URL url=new URL("https://"+domain+"/api/v2/product/"+encoded+".json?fields="+fields);
        HttpURLConnection conn=open(url);
        conn.setInstanceFollowRedirects(true);
        int status=conn.getResponseCode();
        if(status==404){conn.disconnect();return null;}
        if(status<200||status>=300){conn.disconnect();throw new Exception(domain+" lookup failed ("+status+")");}
        JSONObject root=new JSONObject(readBody(conn));
        if(root.optInt("status",0)!=1)return null;
        JSONObject product=root.optJSONObject("product");
        if(product==null)return null;

        String description=firstNonBlank(
                product.optString("product_name",""),
                product.optString("product_name_en",""),
                product.optString("generic_name",""),
                product.optString("brands","")
        );
        String image=firstNonBlank(product.optString("image_front_url",""),product.optString("image_url",""));
        if(description.isEmpty()&&image.isEmpty())return null;
        return new Result(description,image,"");
    }

    private static HttpURLConnection open(URL url) throws Exception {
        HttpURLConnection conn=(HttpURLConnection)url.openConnection();
        conn.setRequestMethod("GET");
        conn.setConnectTimeout(7000);
        conn.setReadTimeout(7000);
        conn.setRequestProperty("Accept","application/json");
        conn.setRequestProperty("User-Agent","iCE-Onhand-Inventory/3.0.46 (Android; inventorycount.net)");
        return conn;
    }

    private static String readBody(HttpURLConnection conn) throws Exception {
        StringBuilder body=new StringBuilder();
        try(BufferedReader br=new BufferedReader(new InputStreamReader(conn.getInputStream(),StandardCharsets.UTF_8))){
            String line;while((line=br.readLine())!=null)body.append(line);
        }finally{conn.disconnect();}
        return body.toString();
    }

    private static String firstNonBlank(String... values){
        for(String v:values)if(v!=null&&!v.trim().isEmpty())return v.trim();
        return "";
    }

    private static List<String> lookupCandidates(String raw){
        ArrayList<String> out=new ArrayList<>();
        String s=raw==null?"":raw.trim();
        add(out,s);
        if(!s.matches("\\d+"))return out;

        String stripped=stripLeadingZeros(s);
        add(out,stripped);

        if(s.length()==10){
            String base="0"+s;
            add(out,base+gtinCheckDigit(base));
        }else if(s.length()==11){
            add(out,s+gtinCheckDigit(s));
        }else if(s.length()==12){
            add(out,"0"+s);
        }
        return out;
    }

    private static char gtinCheckDigit(String body){
        int sum=0;
        boolean triple=true;
        for(int i=body.length()-1;i>=0;i--){
            int d=body.charAt(i)-'0';
            sum+=d*(triple?3:1);
            triple=!triple;
        }
        return (char)('0'+((10-(sum%10))%10));
    }

    private static String stripLeadingZeros(String s){
        int i=0;while(i<s.length()-1&&s.charAt(i)=='0')i++;
        return s.substring(i);
    }

    private static void add(List<String> out,String s){
        if(s!=null&&!s.isEmpty()&&!out.contains(s))out.add(s);
    }

    public static String lookupDescription(String barcode) throws Exception {
        Result result=lookup(barcode);
        return result==null?null:result.description;
    }
}
