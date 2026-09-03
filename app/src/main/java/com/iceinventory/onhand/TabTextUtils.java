package com.iceinventory.onhand;

import android.content.SharedPreferences;

import java.io.BufferedReader;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Locale;
import java.util.Map;

public final class TabTextUtils {
    private static final String KEY_IMPORT="import_field_order";
    private static final String KEY_EXPORT="export_field_order";
    private static final List<String> DEFAULT=Arrays.asList("barcode","description","price","quantity","location");

    private TabTextUtils(){}

    public static List<String> getOrder(SharedPreferences prefs,boolean export){
        String saved=prefs.getString(export?KEY_EXPORT:KEY_IMPORT,"barcode,description,price,quantity,location");
        ArrayList<String> out=new ArrayList<>();
        for(String part:saved.split(",")){
            String f=normalizeField(part);
            if(f!=null&&!out.contains(f))out.add(f);
        }
        if(!out.contains("barcode"))out.add(0,"barcode");
        if(out.isEmpty())out.addAll(DEFAULT);
        return out;
    }

    public static String exportRows(List<InventoryDb.Row> rows,SharedPreferences prefs){
        List<String> order=getOrder(prefs,true);
        StringBuilder b=new StringBuilder();
        for(InventoryDb.Row r:rows){
            for(int i=0;i<order.size();i++){
                if(i>0)b.append('\t');
                String f=order.get(i);
                if("barcode".equals(f))b.append(clean(r.barcode));
                else if("description".equals(f))b.append(clean(r.description));
                else if("price".equals(f))b.append(clean(r.price));
                else if("quantity".equals(f))b.append(r.quantity);
                else if("location".equals(f))b.append(clean(r.location));
            }
            b.append("\r\n");
        }
        return b.toString();
    }

    public static int importRows(BufferedReader br,InventoryDb db,long sessionId,SharedPreferences prefs,boolean autoGtin) throws Exception{
        List<String> configured=getOrder(prefs,false);
        String first=null;
        while((first=br.readLine())!=null&&first.trim().isEmpty()){}
        if(first==null)return 0;

        String[] firstFields=split(first);
        List<String> activeOrder=configured;
        boolean header=looksLikeHeader(firstFields);
        if(header)activeOrder=headerOrder(firstFields);

        int imported=0;
        if(!header)imported+=importOne(firstFields,activeOrder,db,sessionId,autoGtin);
        String line;
        while((line=br.readLine())!=null){
            if(line.trim().isEmpty())continue;
            imported+=importOne(split(line),activeOrder,db,sessionId,autoGtin);
        }
        return imported;
    }

    private static String[] split(String line){return line.split("\\t",-1);}

    private static boolean looksLikeHeader(String[] fields){
        for(String f:fields){
            String n=normalizeField(f);
            if("barcode".equals(n))return true;
        }
        return false;
    }

    private static List<String> headerOrder(String[] fields){
        ArrayList<String> out=new ArrayList<>();
        for(String f:fields){
            String n=normalizeField(f);
            out.add(n==null?"ignore":n);
        }
        return out;
    }

    private static int importOne(String[] values,List<String> order,InventoryDb db,long sessionId,boolean autoGtin){
        Map<String,String> m=new LinkedHashMap<>();
        for(int i=0;i<values.length&&i<order.size();i++){
            String key=order.get(i);
            if(!"ignore".equals(key))m.put(key,values[i].trim());
        }
        String code=m.get("barcode");
        if(code==null||code.trim().isEmpty())return 0;
        code=code.trim();
        if(autoGtin)code=toGtin14(code);
        String desc=value(m,"description");
        String price=value(m,"price").replace("$","").trim();
        String loc=value(m,"location");
        if(loc.isEmpty())loc="Main";
        int qty=0;
        try{String q=value(m,"quantity");if(!q.isEmpty())qty=Integer.parseInt(q.replace(",","").trim());}catch(Exception ignored){}
        db.addLocation(loc);
        db.addOrIncrement(sessionId,code,desc,price,qty,loc);
        return 1;
    }

    private static String value(Map<String,String> m,String k){String v=m.get(k);return v==null?"":v;}

    private static String normalizeField(String raw){
        if(raw==null)return null;
        String f=raw.trim().toLowerCase(Locale.US).replace("_"," ").replace("-"," ");
        if(f.equals("barcode")||f.equals("upc")||f.equals("gtin")||f.contains("barcode"))return "barcode";
        if(f.equals("description")||f.equals("item description")||f.equals("name")||f.contains("description"))return "description";
        if(f.equals("price")||f.equals("retail")||f.equals("cost")||f.contains("price"))return "price";
        if(f.equals("quantity")||f.equals("qty")||f.equals("count")||f.equals("on hand")||f.equals("onhand")||f.contains("quantity"))return "quantity";
        if(f.equals("location")||f.equals("loc")||f.equals("area")||f.contains("location"))return "location";
        return null;
    }

    private static String clean(String s){
        if(s==null)return "";
        return s.replace('\t',' ').replace('\r',' ').replace('\n',' ').trim();
    }

    private static String toGtin14(String code){
        if(code==null)return "";
        String s=code.trim();
        if(!s.matches("\\d+")||s.length()>=14)return s;
        StringBuilder b=new StringBuilder(14);
        for(int i=s.length();i<14;i++)b.append('0');
        b.append(s);return b.toString();
    }
}
