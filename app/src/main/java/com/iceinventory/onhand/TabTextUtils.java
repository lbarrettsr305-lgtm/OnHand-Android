package com.iceinventory.onhand;

import android.content.SharedPreferences;

import java.io.BufferedReader;
import java.text.SimpleDateFormat;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Calendar;
import java.util.Date;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Locale;
import java.util.Map;

public final class TabTextUtils {
    private static final String KEY_IMPORT="import_field_order";
    private static final String KEY_EXPORT="export_field_order";
    private static final String KEY_EXPORT_POSITIVE_ONLY="export_quantity_above_zero_only";
    private static final String DEFAULT_STRING="quantity,barcode,description,price";
    private static final String OLD_DEFAULT="barcode,description,price,quantity,location";
    private static final List<String> DEFAULT=Arrays.asList("quantity","barcode","description","price");

    private TabTextUtils(){}

    public static List<String> getOrder(SharedPreferences prefs,boolean export){
        String saved=prefs.getString(export?KEY_EXPORT:KEY_IMPORT,DEFAULT_STRING);
        if(saved==null||saved.trim().isEmpty()||OLD_DEFAULT.equals(saved.trim()))saved=DEFAULT_STRING;
        ArrayList<String> out=new ArrayList<>();
        for(String part:saved.split(",")){
            String f=normalizeField(part);
            if(f!=null&&!out.contains(f))out.add(f);
        }
        if(!out.contains("barcode"))out.add(Math.min(1,out.size()),"barcode");
        if(out.isEmpty())out.addAll(DEFAULT);
        return out;
    }

    public static String exportRows(List<InventoryDb.Row> rows,SharedPreferences prefs){
        List<String> order=getOrder(prefs,true);
        boolean positiveOnly=prefs.getBoolean(KEY_EXPORT_POSITIVE_ONLY,false);
        StringBuilder b=new StringBuilder();
        SimpleDateFormat dateFmt=new SimpleDateFormat("yyyy-MM-dd",Locale.US);
        SimpleDateFormat timeFmt=new SimpleDateFormat("HH:mm:ss",Locale.US);
        for(InventoryDb.Row r:rows){
            if(positiveOnly&&r.quantity<=0)continue;
            Date when=new Date(r.updatedAt>0?r.updatedAt:System.currentTimeMillis());
            for(int i=0;i<order.size();i++){
                if(i>0)b.append('\t');
                String f=order.get(i);
                if("barcode".equals(f))b.append(clean(r.barcode));
                else if("description".equals(f))b.append(clean(r.description));
                else if("price".equals(f))b.append(clean(r.price));
                else if("quantity".equals(f))b.append(r.quantity);
                else if("location".equals(f))b.append(clean(r.location));
                else if("scan_date".equals(f))b.append(dateFmt.format(when));
                else if("scan_time".equals(f))b.append(timeFmt.format(when));
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
        long scannedAt=parseScanTimestamp(value(m,"scan_date"),value(m,"scan_time"));
        db.addLocation(loc);
        db.addOrIncrementAt(sessionId,code,desc,price,qty,loc,scannedAt);
        return 1;
    }

    private static long parseScanTimestamp(String date,String time){
        String d=date==null?"":date.trim();
        String t=time==null?"":time.trim();
        if(d.isEmpty()&&t.isEmpty())return System.currentTimeMillis();

        String[] datePatterns={"yyyy-MM-dd","MM/dd/yyyy","M/d/yyyy"};
        String[] timePatterns={"HH:mm:ss","HH:mm","h:mm:ss a","h:mm a"};

        if(!d.isEmpty()&&!t.isEmpty()){
            for(String dp:datePatterns)for(String tp:timePatterns){
                Long parsed=parse(dp+" "+tp,d+" "+t);
                if(parsed!=null)return parsed;
            }
        }
        if(!d.isEmpty()){
            for(String dp:datePatterns){
                Long parsed=parse(dp,d);
                if(parsed!=null)return parsed;
            }
        }
        if(!t.isEmpty()){
            Calendar now=Calendar.getInstance();
            for(String tp:timePatterns){
                Long parsed=parse(tp,t);
                if(parsed!=null){
                    Calendar clock=Calendar.getInstance();clock.setTimeInMillis(parsed);
                    now.set(Calendar.HOUR_OF_DAY,clock.get(Calendar.HOUR_OF_DAY));
                    now.set(Calendar.MINUTE,clock.get(Calendar.MINUTE));
                    now.set(Calendar.SECOND,clock.get(Calendar.SECOND));
                    now.set(Calendar.MILLISECOND,0);
                    return now.getTimeInMillis();
                }
            }
        }
        return System.currentTimeMillis();
    }

    private static Long parse(String pattern,String value){
        try{
            SimpleDateFormat f=new SimpleDateFormat(pattern,Locale.US);f.setLenient(false);
            Date d=f.parse(value);return d==null?null:d.getTime();
        }catch(Exception ignored){return null;}
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
        if(f.equals("date")||f.equals("scan date")||f.equals("date scanned")||f.equals("scanned date")||f.contains("scan date"))return "scan_date";
        if(f.equals("time")||f.equals("scan time")||f.equals("time scanned")||f.equals("scanned time")||f.contains("scan time"))return "scan_time";
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
