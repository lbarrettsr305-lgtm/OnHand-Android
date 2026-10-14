package com.iceinventory.onhand;

import android.app.Activity;
import android.app.AlertDialog;
import android.content.ClipData;
import android.content.Intent;
import android.database.Cursor;
import android.graphics.Color;
import android.net.Uri;
import android.os.Bundle;
import android.provider.OpenableColumns;
import android.view.Gravity;
import android.view.ViewGroup;
import android.widget.Button;
import android.widget.EditText;
import android.widget.LinearLayout;
import android.widget.ScrollView;
import android.widget.TextView;
import android.widget.Toast;

import org.json.JSONArray;
import org.json.JSONObject;

import java.io.BufferedReader;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.io.OutputStream;
import java.nio.charset.StandardCharsets;
import java.security.DigestInputStream;
import java.security.MessageDigest;
import java.text.SimpleDateFormat;
import java.util.ArrayList;
import java.util.Date;
import java.util.LinkedHashMap;
import java.util.LinkedHashSet;
import java.util.Locale;
import java.util.Map;

/**
 * Read-only batch quantity audit. It reads completed counter files but never
 * imports them into the active count or changes existing store quantities.
 * A passing location reconciliation does not claim to verify the customer
 * workbook; that comparison remains part of the proper combine/export flow.
 */
public final class BatchQuantityReportActivity extends Activity {
    private static final int PICK_BATCHES=7601, SAVE_REPORT=7602;
    private static final String PREFS="onhand_batch_quantity_audit_v1";
    private final LinkedHashMap<String,Batch> batches=new LinkedHashMap<>();
    private TextView output;
    private String store="Inventory";
    private static final int WHITE=Color.WHITE, GOLD=0xffffd100, GREEN=0xff009b3a;

    private static final class Batch {
        String file="",user="",fingerprint="";
        int rows,missing;
        double qty;
        final LinkedHashMap<String,Double> locations=new LinkedHashMap<>();

        JSONObject json()throws Exception {
            JSONObject o=new JSONObject();
            o.put("file",file);o.put("user",user);o.put("fingerprint",fingerprint);
            o.put("rows",rows);o.put("missing",missing);o.put("qty",qty);
            JSONObject loc=new JSONObject();
            for(Map.Entry<String,Double> e:locations.entrySet())loc.put(e.getKey(),e.getValue());
            o.put("locations",loc);
            return o;
        }
        static Batch fromJson(JSONObject o)throws Exception {
            Batch b=new Batch();
            b.file=o.optString("file");b.user=o.optString("user");
            b.fingerprint=o.optString("fingerprint");b.rows=o.optInt("rows");
            b.missing=o.optInt("missing");b.qty=o.optDouble("qty");
            JSONObject loc=o.optJSONObject("locations");
            if(loc!=null){java.util.Iterator<String> keys=loc.keys();while(keys.hasNext()){String k=keys.next();b.locations.put(k,loc.optDouble(k));}}
            return b;
        }
    }

    private int dp(int v){return Math.round(v*getResources().getDisplayMetrics().density);}
    private TextView text(String s,int size,int color){
        TextView t=new TextView(this);t.setText(s);t.setTextSize(size);t.setTextColor(color);
        return t;
    }
    private Button button(String label){
        Button b=new Button(this);b.setText(label);b.setAllCaps(false);b.setTextSize(15);
        b.setTextColor(WHITE);b.setBackgroundColor(GREEN);
        b.setMinHeight(0);b.setMinimumHeight(0);return b;
    }
    private void addButton(LinearLayout box,Button b){
        LinearLayout.LayoutParams lp=new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT,dp(54));
        lp.setMargins(0,dp(7),0,0);box.addView(b,lp);
    }
    @Override public void onCreate(Bundle saved){
        super.onCreate(saved);
        String passed=getIntent().getStringExtra("report_store");
        if(passed!=null&&!passed.trim().isEmpty())store=passed.trim();
        loadSaved();

        ScrollView scroll=new ScrollView(this);
        scroll.setFillViewport(true);
        LinearLayout page=new LinearLayout(this);page.setOrientation(LinearLayout.VERTICAL);
        page.setPadding(dp(16),dp(18),dp(16),dp(22));page.setBackgroundColor(0xff081819);
        scroll.addView(page);
        TextView title=text("BATCH QTY REPORT",23,GOLD);title.setGravity(Gravity.CENTER);
        page.addView(title);
        TextView storeName=text(store,17,WHITE);storeName.setGravity(Gravity.CENTER);
        page.addView(storeName);
        TextView help=text("MASTER AUDIT: Select completed user batch TXT or CSV files after receiving them. You can add one or several batches at a time; this review never changes the actual inventory. Each user, file, and location total is shown below. The final customer file is NOT verified until the regular combine/export process checks it.",14,WHITE);
        help.setPadding(0,dp(10),0,dp(6));page.addView(help);
        Button choose=button("SELECT / ADD USER BATCH FILES");
        choose.setOnClickListener(v->chooseFiles());addButton(page,choose);
        Button report=button("SAVE BATCH QTY REPORT (TXT)");
        report.setOnClickListener(v->saveReport());addButton(page,report);
        Button clear=button("CLEAR AUDIT FILE LIST");
        clear.setBackgroundColor(0xff404040);
        clear.setOnClickListener(v->new AlertDialog.Builder(this)
                .setTitle("Clear batch audit list?")
                .setMessage("This only clears the list of batches reviewed here. No inventory counts or user files are deleted.")
                .setNegativeButton("Cancel",null)
                .setPositiveButton("CLEAR LIST",(d,w)->{batches.clear();persist();refresh();}).show());
        addButton(page,clear);
        output=text("",15,WHITE);
        output.setTextIsSelectable(true);output.setPadding(dp(4),dp(20),dp(4),dp(12));
        page.addView(output);
        setContentView(scroll);
        refresh();
    }

    private String key(){return "store:"+store;}
    private void loadSaved(){
        try{
            String raw=getSharedPreferences(PREFS,MODE_PRIVATE).getString(key(),"[]");
            JSONArray a=new JSONArray(raw);
            for(int i=0;i<a.length();i++){Batch b=Batch.fromJson(a.getJSONObject(i));if(!b.fingerprint.isEmpty())batches.put(b.fingerprint,b);}
        }catch(Exception ignored){batches.clear();}
    }
    private void persist(){
        try{
            JSONArray a=new JSONArray();
            for(Batch b:batches.values())a.put(b.json());
            getSharedPreferences(PREFS,MODE_PRIVATE).edit().putString(key(),a.toString()).apply();
        }catch(Exception e){toast("Unable to save audit list: "+e.getMessage());}
    }
    private void toast(String s){Toast.makeText(this,s,Toast.LENGTH_LONG).show();}
    private void chooseFiles(){
        Intent intent=new Intent(Intent.ACTION_OPEN_DOCUMENT);
        intent.addCategory(Intent.CATEGORY_OPENABLE);
        intent.setType("*/*");
        intent.putExtra(Intent.EXTRA_ALLOW_MULTIPLE,true);
        startActivityForResult(intent,PICK_BATCHES);
    }
    private String displayName(Uri uri){
        String name="";
        try(Cursor c=getContentResolver().query(uri,new String[]{OpenableColumns.DISPLAY_NAME},null,null,null)){
            if(c!=null&&c.moveToFirst())name=c.getString(0);
        }catch(Exception ignored){}
        if(name==null||name.trim().isEmpty())name=uri.getLastPathSegment();
        return name==null?"UserBatch":name;
    }

    private static String cleanHeader(String h){return h.replace("\ufeff","").toLowerCase(Locale.US).replaceAll("[^a-z0-9]","");}
    private static int column(String[] h,String...names){
        for(int i=0;i<h.length;i++){String candidate=cleanHeader(h[i]);for(String n:names)if(candidate.equals(n))return i;}
        return -1;
    }
    private static String field(String[] f,int i){return i>=0&&i<f.length?f[i].trim():"";}
    private static String[] fields(String line,char delimiter){
        if(delimiter=='\t')return line.split("\t",-1);
        ArrayList<String> all=new ArrayList<>();
        StringBuilder b=new StringBuilder();boolean quoted=false;
        for(int i=0;i<line.length();i++){
            char ch=line.charAt(i);
            if(ch=='"'){if(quoted&&i+1<line.length()&&line.charAt(i+1)=='"'){b.append('"');i++;}else quoted=!quoted;}
            else if(ch==','&&!quoted){all.add(b.toString());b.setLength(0);}
            else b.append(ch);
        }
        all.add(b.toString());return all.toArray(new String[0]);
    }
    private static String userFromName(String file){
        String n=file.replaceFirst("(?i)\\.(txt|csv)$","");
        java.util.regex.Matcher m=java.util.regex.Pattern.compile("(?i).*[-_]([a-z0-9]+)[-_]batch[ -]*\\d+$").matcher(n);
        if(m.matches())return m.group(1);
        m=java.util.regex.Pattern.compile("(?i)^count(.+?)[-_]?batch[ -]*\\d+$").matcher(n);
        if(m.matches())return m.group(1);
        return n;
    }
    private static String number(double d){
        if(Math.abs(d-Math.rint(d))<0.00000001)return String.format(Locale.US,"%.0f",d);
        return String.format(Locale.US,"%.3f",d);
    }
    private Batch read(Uri uri)throws Exception {
        Batch b=new Batch();b.file=displayName(uri);b.user=userFromName(b.file);
        String upper=b.file.toUpperCase(Locale.US);
        if(upper.startsWith("COMBINED")||upper.contains("VERIFICATION")||upper.contains("BATCH QTY REPORT"))
            throw new Exception("This is a report/combined output, not an individual user batch: "+b.file);
        MessageDigest md=MessageDigest.getInstance("SHA-256");
        try(InputStream raw=getContentResolver().openInputStream(uri)){
            if(raw==null)throw new Exception("Cannot open "+b.file);
            try(BufferedReader reader=new BufferedReader(new InputStreamReader(new DigestInputStream(raw,md),StandardCharsets.UTF_8))){
                String line;
                char delim='\t';int qi=-1,bi=-1,li=-1,ui=-1;boolean headerFound=false;
                while((line=reader.readLine())!=null){
                    if(line.trim().isEmpty()||line.startsWith("#"))continue;
                    if(!headerFound){
                        delim=line.indexOf('\t')>=0?'\t':',';
                        String[] head=fields(line,delim);
                        qi=column(head,"qty","quantity","count","onhand","onhandqty");
                        bi=column(head,"barcode","upc","gtin");
                        li=column(head,"location","loc","section","area");
                        ui=column(head,"user","counter","username");
                        if(qi<0||bi<0)throw new Exception(b.file+" needs QTY and BARCODE headers. Export this counter file with headers.");
                        headerFound=true;continue;
                    }
                    String[] f=fields(line,delim);
                    String code=field(f,bi);
                    if(code.isEmpty())continue;
                    double quantity;
                    try{quantity=Double.parseDouble(field(f,qi).replace(",",""));}
                    catch(Exception e){throw new Exception("Invalid QTY for "+code+" in "+b.file);}
                    if(!Double.isFinite(quantity))throw new Exception("Invalid QTY for "+code);
                    String user=field(f,ui);if(!user.isEmpty()&&b.rows==0)b.user=user;
                    String loc=field(f,li);
                    if(loc.isEmpty()){loc="MISSING LOCATION";b.missing++;}
                    b.rows++;b.qty+=quantity;
                    b.locations.put(loc,b.locations.getOrDefault(loc,0d)+quantity);
                }
                if(!headerFound||b.rows==0)throw new Exception("No counted rows found in "+b.file);
                if(li<0)b.missing=b.rows;
            }
        }
        StringBuilder hash=new StringBuilder();
        for(byte byteValue:md.digest())hash.append(String.format(Locale.US,"%02x",byteValue&255));
        b.fingerprint=b.file+"|"+hash;
        return b;
    }
    @Override protected void onActivityResult(int code,int result,Intent data){
        super.onActivityResult(code,result,data);
        if(result!=RESULT_OK||data==null)return;
        if(code==SAVE_REPORT){
            try(OutputStream out=getContentResolver().openOutputStream(data.getData())){
                if(out==null)throw new Exception("Cannot open output");
                out.write(reportText().getBytes(StandardCharsets.UTF_8));
                toast("Batch Qty Report saved");
            }catch(Exception e){toast("Report not saved: "+e.getMessage());}
            return;
        }
        if(code!=PICK_BATCHES)return;
        LinkedHashSet<Uri> list=new LinkedHashSet<>();
        if(data.getData()!=null)list.add(data.getData());
        ClipData clip=data.getClipData();
        if(clip!=null)for(int i=0;i<clip.getItemCount();i++)list.add(clip.getItemAt(i).getUri());
        int added=0,duplicates=0;ArrayList<String> errors=new ArrayList<>();
        for(Uri uri:list){
            try{
                Batch b=read(uri);
                if(batches.containsKey(b.fingerprint))duplicates++;
                else {batches.put(b.fingerprint,b);added++;}
            }catch(Exception e){errors.add(e.getMessage());}
        }
        persist();refresh();
        if(!errors.isEmpty())new AlertDialog.Builder(this).setTitle("Files needing attention")
                .setMessage(android.text.TextUtils.join("\n\n",errors))
                .setPositiveButton("OK",null).show();
        toast(added+" batch(es) added"+(duplicates>0?"; "+duplicates+" duplicate(s) skipped":""));
    }
    private String reportText(){
        StringBuilder b=new StringBuilder();
        b.append("ICE INVENTORY LLC - USER BATCH QUANTITY REPORT\n");
        b.append("STORE\t").append(store).append("\n");
        b.append("DATE\t").append(new SimpleDateFormat("yyyy-MM-dd HH:mm",Locale.US).format(new Date())).append("\n\n");
        b.append("USER\tBATCH FILE\tROWS\tQTY\tLOCATION STATUS\n");
        LinkedHashMap<String,Double> users=new LinkedHashMap<>();
        LinkedHashMap<String,Double> userLocations=new LinkedHashMap<>();
        double sources=0,locations=0;int missing=0,rows=0;
        for(Batch batch:batches.values()){
            b.append(batch.user).append('\t').append(batch.file).append('\t').append(batch.rows)
                    .append('\t').append(number(batch.qty)).append('\t')
                    .append(batch.missing==0?"OK":"MISSING "+batch.missing).append('\n');
            sources+=batch.qty;rows+=batch.rows;missing+=batch.missing;
            users.put(batch.user,users.getOrDefault(batch.user,0d)+batch.qty);
            for(Map.Entry<String,Double> entry:batch.locations.entrySet()){
                locations+=entry.getValue();
                String key=batch.user+" / "+entry.getKey();
                userLocations.put(key,userLocations.getOrDefault(key,0d)+entry.getValue());
            }
        }
        b.append("\nTOTAL PER USER\nUSER\tQTY\n");
        for(Map.Entry<String,Double> e:users.entrySet())b.append(e.getKey()).append('\t').append(number(e.getValue())).append('\n');
        b.append("\nUSER AND LOCATION TOTALS\nUSER / LOCATION\tQTY\n");
        for(Map.Entry<String,Double> e:userLocations.entrySet())b.append(e.getKey()).append('\t').append(number(e.getValue())).append('\n');
        b.append("\nBatch files\t").append(batches.size()).append("\nRows\t").append(rows)
         .append("\nTotal source batch QTY\t").append(number(sources))
         .append("\nTotal location QTY\t").append(number(locations))
         .append("\nDifference\t").append(number(locations-sources))
         .append("\nMissing location rows\t").append(missing).append('\n');
        b.append(missing==0&&!batches.isEmpty()&&Math.abs(locations-sources)<0.000001
                ?"SOURCE / LOCATION TOTALS MATCH\n":"LOCATION AUDIT NEEDS REVIEW\n");
        b.append("FINAL CUSTOMER FILE TOTAL\tNOT CHECKED BY THIS REPORT\n");
        b.append("Run the normal combine/export workflow to reconcile the actual customer file.\n");
        return b.toString();
    }
    private void refresh(){
        String report=reportText();
        if(batches.isEmpty())report="No user batches selected yet.\n\nTap SELECT / ADD USER BATCH FILES after receiving counter files. You can add files from multiple counters, including Master, without editing their inventory.\n\nNo final customer-file total is verified on this screen.";
        output.setText(report);
    }
    private void saveReport(){
        if(batches.isEmpty()){toast("Select at least one user batch first");return;}
        Intent i=new Intent(Intent.ACTION_CREATE_DOCUMENT);
        i.addCategory(Intent.CATEGORY_OPENABLE);
        i.setType("text/plain");
        String safe=store.replaceAll("[^a-zA-Z0-9_-]","_");
        i.putExtra(Intent.EXTRA_TITLE,"BATCH-QTY-"+safe+"-REPORT.txt");
        startActivityForResult(i,SAVE_REPORT);
    }
}
