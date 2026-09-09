package com.iceinventory.onhand;

import android.app.Activity;
import android.content.Intent;
import android.database.Cursor;
import android.graphics.Color;
import android.net.Uri;
import android.os.Bundle;
import android.provider.OpenableColumns;
import android.view.Gravity;
import android.view.ViewGroup;
import android.widget.Button;
import android.widget.LinearLayout;
import android.widget.ScrollView;
import android.widget.TextView;

import java.io.BufferedReader;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.io.OutputStream;
import java.nio.charset.StandardCharsets;
import java.text.SimpleDateFormat;
import java.util.ArrayList;
import java.util.Date;
import java.util.LinkedHashMap;
import java.util.Locale;
import java.util.Map;

/** Combines returned user batch files without changing the originals or active inventory. */
public final class BatchMergeActivity extends Activity {
    private static final int REQ_FILES=4101,REQ_SAVE=4102,REQ_REPORT=4103;
    private static final String SETTINGS="onhand_settings";
    private static final String KEY_USER_NAME="export_user_name";

    private static final class Total {
        String barcode="",description="",price="";
        long quantity;
    }

    private static final class BatchStat {
        String fileName="",userName="";
        int rows;
        long quantity;
    }

    private final LinkedHashMap<String,Total> combined=new LinkedHashMap<>();
    private final ArrayList<BatchStat> sourceStats=new ArrayList<>();
    private TextView status;
    private Button save,report;
    private long sourceGrandTotal,outputTotal;
    private int sourceFiles,sourceRows,selectedFiles;
    private boolean verified;

    @Override public void onCreate(Bundle state){
        super.onCreate(state);
        LinearLayout root=new LinearLayout(this);root.setOrientation(LinearLayout.VERTICAL);root.setPadding(dp(16),dp(16),dp(16),dp(16));root.setBackgroundColor(Color.rgb(8,24,27));
        TextView title=text("Combine User Batches",24,Color.rgb(255,215,0));root.addView(title);
        TextView help=text("Select every user's tab-delimited batch file. Matching barcodes will be summed into one verified batch. A separate verification report proves the selected files loaded and the source quantity total equals the combined quantity total.",16,Color.WHITE);help.setPadding(0,dp(10),0,dp(14));root.addView(help);
        Button choose=button("Select User Batch Files");choose.setOnClickListener(v->chooseFiles());root.addView(choose,new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT,dp(54)));
        status=text("No batch files selected.",17,Color.WHITE);status.setPadding(0,dp(18),0,dp(18));ScrollView scroll=new ScrollView(this);scroll.addView(status);root.addView(scroll,new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT,0,1));
        save=button("Export Verified Combined Batch");save.setEnabled(false);save.setOnClickListener(v->saveCombined());root.addView(save,new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT,dp(54)));
        report=button("Export Verification Report");report.setEnabled(false);report.setOnClickListener(v->saveReport());LinearLayout.LayoutParams rp=new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT,dp(54));rp.setMargins(0,dp(8),0,0);root.addView(report,rp);
        Button close=button("Back to Inventory");close.setOnClickListener(v->finish());LinearLayout.LayoutParams cp=new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT,dp(50));cp.setMargins(0,dp(8),0,0);root.addView(close,cp);
        setContentView(root);
    }

    private void chooseFiles(){
        Intent i=new Intent(Intent.ACTION_OPEN_DOCUMENT);i.addCategory(Intent.CATEGORY_OPENABLE);i.setType("text/*");i.putExtra(Intent.EXTRA_ALLOW_MULTIPLE,true);startActivityForResult(i,REQ_FILES);
    }

    @Override protected void onActivityResult(int request,int result,Intent data){
        super.onActivityResult(request,result,data);if(result!=RESULT_OK||data==null)return;
        if(request==REQ_FILES)loadFiles(data);else if(request==REQ_SAVE)writeCombined(data.getData());else if(request==REQ_REPORT)writeVerificationReport(data.getData());
    }

    private void loadFiles(Intent data){
        combined.clear();sourceStats.clear();sourceGrandTotal=0;outputTotal=0;sourceFiles=0;sourceRows=0;selectedFiles=0;verified=false;save.setEnabled(false);report.setEnabled(false);
        ArrayList<Uri> uris=new ArrayList<>();
        if(data.getClipData()!=null)for(int i=0;i<data.getClipData().getItemCount();i++)uris.add(data.getClipData().getItemAt(i).getUri());
        else if(data.getData()!=null)uris.add(data.getData());
        selectedFiles=uris.size();
        ArrayList<String> errors=new ArrayList<>();
        for(Uri uri:uris){try{sourceStats.add(readOne(uri));sourceFiles++;}catch(Exception e){errors.add(e.getMessage()==null?"Unreadable batch":e.getMessage());}}
        for(Total t:combined.values())outputTotal=Math.addExact(outputTotal,t.quantity);
        verified=errors.isEmpty()&&sourceFiles==selectedFiles&&sourceFiles>0&&sourceGrandTotal==outputTotal;
        StringBuilder m=new StringBuilder();
        m.append("Selected files: ").append(selectedFiles).append("\nSuccessfully loaded: ").append(sourceFiles).append("\nOriginal rows: ").append(sourceRows).append("\nCombined barcodes: ").append(combined.size()).append("\n\n");
        m.append("BATCH / USER QUANTITY TOTALS\n");
        for(BatchStat s:sourceStats)m.append("• ").append(s.userName.isEmpty()?"User prefix missing":s.userName).append(" — ").append(s.quantity).append(" units — ").append(s.rows).append(" rows\n");
        m.append("\nSource grand total: ").append(sourceGrandTotal).append("\nCombined grand total: ").append(outputTotal).append("\nDifference: ").append(outputTotal-sourceGrandTotal).append("\n\n");
        if(verified)m.append("VERIFIED — ALL SELECTED FILES LOADED AND TOTALS MATCH");else m.append("NOT VERIFIED — EXPORT BLOCKED");
        if(!errors.isEmpty()){m.append("\n\nProblems:");for(String e:errors)m.append("\n• ").append(e);}
        status.setText(m.toString());status.setTextColor(verified?Color.rgb(120,255,140):Color.rgb(255,130,130));save.setEnabled(verified);report.setEnabled(verified);
    }

    private BatchStat readOne(Uri uri)throws Exception{
        BatchStat stat=new BatchStat();stat.fileName=displayName(uri);stat.userName=userPrefix(stat.fileName);
        InputStream is=getContentResolver().openInputStream(uri);if(is==null)throw new Exception("Could not open "+stat.fileName);
        try(BufferedReader br=new BufferedReader(new InputStreamReader(is,StandardCharsets.UTF_8))){
            String first;do{first=br.readLine();}while(first!=null&&first.trim().isEmpty());if(first==null)throw new Exception(stat.fileName+" is empty");
            String[] f=first.split("\\t",-1);int bi=find(f,"barcode","upc","gtin"),qi=find(f,"quantity","qty","count","on hand","onhand"),di=find(f,"description","item description","name"),pi=find(f,"price","retail","cost");
            if(bi<0||qi<0)throw new Exception(stat.fileName+" is missing Barcode or Quantity header");
            String line;while((line=br.readLine())!=null){if(line.trim().isEmpty())continue;String[] v=line.split("\\t",-1);if(bi>=v.length||qi>=v.length)continue;String code=v[bi].trim();if(code.isEmpty())continue;long q;try{q=Long.parseLong(v[qi].replace(",","").trim());}catch(Exception e){throw new Exception("Invalid quantity for barcode "+code+" in "+stat.fileName);}
                Total t=combined.get(code);if(t==null){t=new Total();t.barcode=code;combined.put(code,t);}t.quantity=Math.addExact(t.quantity,q);sourceGrandTotal=Math.addExact(sourceGrandTotal,q);sourceRows++;stat.rows++;stat.quantity=Math.addExact(stat.quantity,q);
                if(t.description.isEmpty()&&di>=0&&di<v.length)t.description=v[di].trim();if(t.price.isEmpty()&&pi>=0&&pi<v.length)t.price=v[pi].replace("$","").trim();
            }
        }
        return stat;
    }

    private int find(String[] h,String... names){for(int i=0;i<h.length;i++){String x=h[i].trim().toLowerCase(Locale.US).replace('_',' ').replace('-',' ');for(String n:names)if(x.equals(n)||x.contains(n))return i;}return -1;}

    private void saveCombined(){if(!verified)return;Intent i=new Intent(Intent.ACTION_CREATE_DOCUMENT);i.addCategory(Intent.CATEGORY_OPENABLE);i.setType("text/plain");i.putExtra(Intent.EXTRA_TITLE,prefixedName("Combined_Verified_Batch.txt"));startActivityForResult(i,REQ_SAVE);}

    private void saveReport(){if(!verified)return;Intent i=new Intent(Intent.ACTION_CREATE_DOCUMENT);i.addCategory(Intent.CATEGORY_OPENABLE);i.setType("text/plain");i.putExtra(Intent.EXTRA_TITLE,prefixedName("Combined_Batch_Verification_Report.txt"));startActivityForResult(i,REQ_REPORT);}

    private void writeCombined(Uri uri){if(uri==null||!verified)return;try(OutputStream os=getContentResolver().openOutputStream(uri)){if(os==null)throw new Exception("Could not create combined file");StringBuilder b=new StringBuilder("Quantity\tBarcode\tDescription\tPrice\r\n");for(Map.Entry<String,Total> e:combined.entrySet()){Total t=e.getValue();b.append(t.quantity).append('\t').append(clean(t.barcode)).append('\t').append(clean(t.description)).append('\t').append(clean(t.price)).append("\r\n");}os.write(b.toString().getBytes(StandardCharsets.UTF_8));status.append("\n\nVerified combined batch exported successfully. Export the Verification Report for the audit record.");}catch(Exception e){status.append("\n\nExport failed: "+e.getMessage());}}

    private void writeVerificationReport(Uri uri){if(uri==null||!verified)return;try(OutputStream os=getContentResolver().openOutputStream(uri)){if(os==null)throw new Exception("Could not create verification report");os.write(buildVerificationReport().getBytes(StandardCharsets.UTF_8));status.append("\n\nVerification report exported successfully.");}catch(Exception e){status.append("\n\nVerification report failed: "+e.getMessage());}}

    private String buildVerificationReport(){
        StringBuilder b=new StringBuilder();
        b.append("iCE OnHand Combined Batch Verification Report\r\n");
        b.append("Created by\t").append(clean(savedUserName())).append("\r\n");
        b.append("Created at\t").append(new SimpleDateFormat("yyyy-MM-dd HH:mm:ss",Locale.US).format(new Date())).append("\r\n");
        b.append("Status\t").append(verified?"PASS - VERIFIED":"FAIL - NOT VERIFIED").append("\r\n\r\n");
        b.append("Selected Files\t").append(selectedFiles).append("\r\n");
        b.append("Successfully Loaded Files\t").append(sourceFiles).append("\r\n");
        b.append("Source Rows\t").append(sourceRows).append("\r\n");
        b.append("Combined Unique Barcodes\t").append(combined.size()).append("\r\n");
        b.append("Source Grand Total Quantity\t").append(sourceGrandTotal).append("\r\n");
        b.append("Combined Grand Total Quantity\t").append(outputTotal).append("\r\n");
        b.append("Difference\t").append(outputTotal-sourceGrandTotal).append("\r\n\r\n");
        b.append("User\tSource Batch File\tRows\tQuantity\r\n");
        for(BatchStat s:sourceStats)b.append(clean(s.userName.isEmpty()?"USER PREFIX MISSING":s.userName)).append('\t').append(clean(s.fileName)).append('\t').append(s.rows).append('\t').append(s.quantity).append("\r\n");
        b.append("\r\nVerification Method\r\n");
        b.append("1. Every selected source file must open successfully.\r\n");
        b.append("2. Every source row quantity is added to the Source Grand Total.\r\n");
        b.append("3. Matching barcodes are summed into one combined barcode quantity.\r\n");
        b.append("4. Every combined barcode quantity is added to the Combined Grand Total.\r\n");
        b.append("5. PASS requires loaded files = selected files and Source Grand Total = Combined Grand Total.\r\n");
        b.append("\r\nFINAL RESULT\t").append(verified?"PASS - ALL SELECTED BATCH QUANTITIES INCLUDED AND TOTALS MATCH":"FAIL").append("\r\n");
        return b.toString();
    }

    private String displayName(Uri uri){
        String name="";Cursor c=null;try{c=getContentResolver().query(uri,new String[]{OpenableColumns.DISPLAY_NAME},null,null,null);if(c!=null&&c.moveToFirst())name=c.getString(0);}catch(Exception ignored){}finally{if(c!=null)c.close();}
        if(name==null||name.trim().isEmpty())name=uri.getLastPathSegment();return name==null?"Selected batch":name.trim();
    }

    private String userPrefix(String fileName){String n=fileName==null?"":fileName.trim();int p=n.indexOf(" - ");return p>0?n.substring(0,p).trim():"";}
    private String savedUserName(){String n=getSharedPreferences(SETTINGS,MODE_PRIVATE).getString(KEY_USER_NAME,"");return n==null?"":n.trim();}
    private String prefixedName(String base){String u=safeFilePart(savedUserName());return u.isEmpty()?base:u+" - "+base;}
    private String safeFilePart(String s){String n=s==null?"":s.trim();return n.replaceAll("[\\\\/:*?\"<>|]+","_").replaceAll("\\s+"," ").trim();}
    private String clean(String s){return s==null?"":s.replace('\t',' ').replace('\r',' ').replace('\n',' ').trim();}
    private Button button(String s){Button b=new Button(this);b.setText(s);b.setTextSize(16);b.setAllCaps(false);return b;}
    private TextView text(String s,int size,int color){TextView v=new TextView(this);v.setText(s);v.setTextSize(size);v.setTextColor(color);v.setGravity(Gravity.CENTER_VERTICAL);return v;}
    private int dp(int n){return Math.round(n*getResources().getDisplayMetrics().density);}
}
