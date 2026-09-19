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
import android.widget.EditText;
import android.widget.LinearLayout;
import android.widget.ScrollView;
import android.widget.TextView;
import android.widget.Toast;

import java.io.BufferedReader;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.io.OutputStream;
import java.nio.charset.StandardCharsets;
import java.text.SimpleDateFormat;
import java.util.ArrayList;
import java.util.Collections;
import java.util.Comparator;
import java.util.Date;
import java.util.HashMap;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Locale;
import java.util.Map;

/** End-to-end monthly processor. POS-specific mapping is isolated in loadPetrosoft(). */
public final class MonthlyInventoryActivity extends Activity {
    private static final int PICK_SOURCE=5101,SAVE_MASTER=5102,SAVE_ONHAND=5103,PICK_COUNTS=5104,SAVE_COMBINED=5105,SAVE_CLIENT=5106,SAVE_AUDIT=5107;
    private final LinkedHashMap<String,MonthlyClientXlsxWriter.Product> products=new LinkedHashMap<>();
    private final LinkedHashMap<String,Long> combined=new LinkedHashMap<>();
    private final ArrayList<CountFile> countFiles=new ArrayList<>();
    private final ArrayList<String> unmatched=new ArrayList<>();
    private final ArrayList<MonthlyClientXlsxWriter.ClientRow> clientRows=new ArrayList<>();
    private EditText customer,date;
    private TextView status;
    private Button saveMaster,saveOnHand,chooseCounts,saveCombined,saveClient,saveAudit;
    private String sourceName="";
    private int sourceRows,excludedLottery,duplicates;
    private long sourceTotal,combinedTotal,clientTotal;
    private boolean sourceReady,countsReady,validated;

    private static final class CountFile {String name="";int rows;long quantity;}

    @Override public void onCreate(Bundle state){
        super.onCreate(state);
        ScrollView scroll=new ScrollView(this);LinearLayout root=new LinearLayout(this);root.setOrientation(LinearLayout.VERTICAL);root.setPadding(dp(16),dp(16),dp(16),dp(24));root.setBackgroundColor(Color.rgb(8,24,27));scroll.addView(root);
        root.addView(text("Monthly POS Inventory",25,Color.rgb(255,215,0)));
        TextView profile=text("POS FORMAT PROFILE\nPetrosoft / CStoreOffice",16,Color.WHITE);profile.setPadding(0,dp(8),0,dp(10));root.addView(profile);
        customer=input("Customer name", "CHEV2620");root.addView(customer);
        date=input("Inventory date (MM-DD-YYYY)",new SimpleDateFormat("MM-dd-yyyy",Locale.US).format(new Date()));root.addView(date);
        Button source=button("1. Select Petrosoft Items / Price Management Excel");source.setOnClickListener(v->pickSource());root.addView(source,params(58));
        saveMaster=button("2. Export Query Master Excel");saveMaster.setOnClickListener(v->create(SAVE_MASTER,"application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",base()+" MASTER-"+day()+".xlsx"));root.addView(saveMaster,params(54));
        saveOnHand=button("3. Export OnHand Import TXT (Quantity 0)");saveOnHand.setOnClickListener(v->create(SAVE_ONHAND,"text/plain","ONHAND "+base()+" MASTER-"+day()+".txt"));root.addView(saveOnHand,params(54));
        chooseCounts=button("4. Select All User Count Files");chooseCounts.setOnClickListener(v->pickCounts());root.addView(chooseCounts,params(58));
        saveCombined=button("5. Export Verified Combined TXT");saveCombined.setOnClickListener(v->create(SAVE_COMBINED,"text/plain",base()+" ALL-INVENTORY-"+day()+".txt"));root.addView(saveCombined,params(54));
        saveClient=button("6. Export Petrosoft Client Excel");saveClient.setOnClickListener(v->create(SAVE_CLIENT,"application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",base()+" INVENTORY-"+day()+".xlsx"));root.addView(saveClient,params(58));
        saveAudit=button("Export Monthly Verification Report");saveAudit.setOnClickListener(v->create(SAVE_AUDIT,"text/plain",base()+" MONTHLY VERIFICATION-"+day()+".txt"));root.addView(saveAudit,params(54));
        status=text("Start by selecting the Petrosoft Items / Price Management Excel file.",16,Color.WHITE);status.setPadding(0,dp(16),0,dp(16));root.addView(status);
        Button back=button("Back to Inventory");back.setOnClickListener(v->finish());root.addView(back,params(52));
        setContentView(scroll);setEnabledState();
    }

    private void pickSource(){Intent i=new Intent(Intent.ACTION_OPEN_DOCUMENT);i.addCategory(Intent.CATEGORY_OPENABLE);i.setType("application/vnd.openxmlformats-officedocument.spreadsheetml.sheet");startActivityForResult(i,PICK_SOURCE);}
    private void pickCounts(){Intent i=new Intent(Intent.ACTION_OPEN_DOCUMENT);i.addCategory(Intent.CATEGORY_OPENABLE);i.setType("text/*");i.putExtra(Intent.EXTRA_ALLOW_MULTIPLE,true);startActivityForResult(i,PICK_COUNTS);}
    private void create(int request,String type,String name){Intent i=new Intent(Intent.ACTION_CREATE_DOCUMENT);i.addCategory(Intent.CATEGORY_OPENABLE);i.setType(type);i.putExtra(Intent.EXTRA_TITLE,name);startActivityForResult(i,request);}

    @Override protected void onActivityResult(int request,int result,Intent data){super.onActivityResult(request,result,data);if(result!=RESULT_OK||data==null)return;try{
        if(request==PICK_SOURCE)loadPetrosoft(data.getData());else if(request==PICK_COUNTS)loadCounts(data);else if(data.getData()!=null)write(request,data.getData());
    }catch(Exception e){fail(e.getMessage()==null?e.toString():e.getMessage());}}

    private void loadPetrosoft(Uri uri)throws Exception{
        if(uri==null)return;sourceName=displayName(uri);products.clear();combined.clear();countFiles.clear();unmatched.clear();clientRows.clear();sourceRows=excludedLottery=duplicates=0;sourceTotal=combinedTotal=clientTotal=0;countsReady=validated=false;
        InputStream in=getContentResolver().openInputStream(uri);if(in==null)throw new Exception("Could not open the Petrosoft Excel file");
        List<Map<Integer,String>> rows;try(InputStream use=in){rows=XlsxTableReader.readFirstSheet(use);}
        int header=-1;Map<String,Integer> columns=null;
        for(int i=0;i<rows.size();i++){Map<String,Integer> found=headerMap(rows.get(i));if(found.containsKey("GTIN")&&found.containsKey("UPCA12DIGITS")&&found.containsKey("CURRENTRETAIL")){header=i;columns=found;break;}}
        if(header<0||columns==null)throw new Exception("This file does not match the Petrosoft Items / Price Management format");
        String invDate=clientDate();
        for(int i=header+1;i<rows.size();i++){
            Map<Integer,String> r=rows.get(i);String upc=get(r,columns,"UPCA12DIGITS");String gtin=get(r,columns,"GTIN");if(upc.isEmpty()||gtin.isEmpty())continue;
            String cat=plainNumber(get(r,columns,"CAT"));if(cat.isEmpty())continue;if("9".equals(cat)){excludedLottery++;continue;}
            MonthlyClientXlsxWriter.Product p=product(upc,gtin,cat,get(r,columns,"CURRENTRETAIL"),first(get(r,columns,"CRDESCRIPTION"),get(r,columns,"ITEMDESCRIPTION")),get(r,columns,"COST"),invDate,get(r,columns,"CATEGORYNAME"));
            addProduct(p);
            String upce=get(r,columns,"UPCE8DIGITS");if(!upce.isEmpty()&&!"00000000".equals(upce)){MonthlyClientXlsxWriter.Product alias=product(upce,gtin,cat,p.retail,p.description,p.cost,invDate,p.categoryName);addProduct(alias);}
            sourceRows++;
        }
        if(products.isEmpty())throw new Exception("No countable Petrosoft products were found");sourceReady=true;showSource();setEnabledState();
    }

    private MonthlyClientXlsxWriter.Product product(String upc,String gtin,String cat,String retail,String desc,String cost,String d,String catName){MonthlyClientXlsxWriter.Product p=new MonthlyClientXlsxWriter.Product();p.upc=clean(upc);p.gtin=clean(gtin);p.category=plainNumber(cat);p.retail=clean(retail);p.description=clean(desc);p.cost=clean(cost);p.date=d;p.categoryName=clean(catName);return p;}
    private void addProduct(MonthlyClientXlsxWriter.Product p){if(products.containsKey(p.upc)){duplicates++;return;}products.put(p.upc,p);}

    private void loadCounts(Intent data)throws Exception{
        if(!sourceReady)throw new Exception("Select the Petrosoft source file first");combined.clear();countFiles.clear();unmatched.clear();clientRows.clear();sourceTotal=combinedTotal=clientTotal=0;validated=false;
        ArrayList<Uri> uris=new ArrayList<>();if(data.getClipData()!=null)for(int i=0;i<data.getClipData().getItemCount();i++)uris.add(data.getClipData().getItemAt(i).getUri());else if(data.getData()!=null)uris.add(data.getData());
        if(uris.isEmpty())throw new Exception("No user count files were selected");
        for(Uri u:uris)countFiles.add(readCountFile(u));
        for(Map.Entry<String,Long> e:combined.entrySet()){combinedTotal=Math.addExact(combinedTotal,e.getValue());MonthlyClientXlsxWriter.Product p=products.get(e.getKey());if(p==null)unmatched.add(e.getKey());}
        LinkedHashMap<String,MonthlyClientXlsxWriter.ClientRow> byGtin=new LinkedHashMap<>();
        for(Map.Entry<String,Long> e:combined.entrySet()){MonthlyClientXlsxWriter.Product p=products.get(e.getKey());if(p==null)continue;MonthlyClientXlsxWriter.ClientRow row=byGtin.get(p.gtin);if(row==null){row=new MonthlyClientXlsxWriter.ClientRow(p,0);byGtin.put(p.gtin,row);}row.quantity=Math.addExact(row.quantity,e.getValue());}
        clientRows.addAll(byGtin.values());Collections.sort(clientRows,(a,b)->Long.compare(b.quantity,a.quantity));for(MonthlyClientXlsxWriter.ClientRow r:clientRows)clientTotal=Math.addExact(clientTotal,r.quantity);
        validated=countFiles.size()==uris.size()&&sourceTotal==combinedTotal&&combinedTotal==clientTotal&&unmatched.isEmpty();countsReady=true;showValidation();setEnabledState();
    }

    private CountFile readCountFile(Uri uri)throws Exception{
        CountFile s=new CountFile();s.name=displayName(uri);String low=s.name.toLowerCase(Locale.US);if(low.contains("combined")||low.contains("all-inventory")||low.contains("verification")||low.contains("report"))throw new Exception(s.name+" is an output/report, not a user count file");
        InputStream in=getContentResolver().openInputStream(uri);if(in==null)throw new Exception("Could not open "+s.name);
        try(BufferedReader br=new BufferedReader(new InputStreamReader(in,StandardCharsets.UTF_8))){String line;boolean first=true;int qi=0,bi=1;while((line=br.readLine())!=null){if(line.trim().isEmpty())continue;String[] v=line.split("\\t",-1);if(first){first=false;int hq=find(v,"quantity","qty","count","on hand","onhand"),hb=find(v,"barcode","upc","gtin");if(hq>=0&&hb>=0){qi=hq;bi=hb;continue;}}if(v.length<=Math.max(qi,bi))continue;String code=v[bi].trim();if(code.isEmpty())continue;long q;try{q=Long.parseLong(v[qi].replace(",","").trim());}catch(Exception e){throw new Exception("Invalid quantity for "+code+" in "+s.name);}Long old=combined.get(code);combined.put(code,Math.addExact(old==null?0:old,q));s.rows++;s.quantity=Math.addExact(s.quantity,q);sourceTotal=Math.addExact(sourceTotal,q);}}
        if(s.rows==0)throw new Exception(s.name+" contains no count rows");return s;
    }

    private void write(int request,Uri uri)throws Exception{OutputStream out=getContentResolver().openOutputStream(uri);if(out==null)throw new Exception("Could not create output file");try(OutputStream use=out){
        if(request==SAVE_MASTER)MonthlyClientXlsxWriter.writeMaster(use,new ArrayList<>(products.values()));
        else if(request==SAVE_ONHAND)use.write(onHandText().getBytes(StandardCharsets.UTF_8));
        else if(request==SAVE_COMBINED)use.write(combinedText().getBytes(StandardCharsets.UTF_8));
        else if(request==SAVE_CLIENT){if(!validated)throw new Exception("Client export is blocked until validation passes");MonthlyClientXlsxWriter.writeClient(use,clientRows);}
        else if(request==SAVE_AUDIT)use.write(auditText().getBytes(StandardCharsets.UTF_8));
    }Toast.makeText(this,"File exported successfully",Toast.LENGTH_LONG).show();}

    private String onHandText(){StringBuilder b=new StringBuilder();for(MonthlyClientXlsxWriter.Product p:products.values())b.append("0\t").append(tab(p.upc)).append('\t').append(tab(p.description)).append("\t$").append(money(p.retail)).append("\r\n");return b.toString();}
    private String combinedText(){StringBuilder b=new StringBuilder();for(Map.Entry<String,Long> e:combined.entrySet()){MonthlyClientXlsxWriter.Product p=products.get(e.getKey());b.append(e.getValue()).append('\t').append(tab(e.getKey())).append('\t').append(tab(p==null?"":p.description)).append("\t$").append(money(p==null?"":p.retail)).append("\r\n");}return b.toString();}
    private String auditText(){StringBuilder b=new StringBuilder("ICE ONHAND MONTHLY POS VERIFICATION\r\n");b.append("POS PROFILE\tPETROSOFT / CSTOREOFFICE\r\nCUSTOMER\t").append(tab(base())).append("\r\nINVENTORY DATE\t").append(clientDate()).append("\r\nSOURCE FILE\t").append(tab(sourceName)).append("\r\nSTATUS\t").append(validated?"PASS - VERIFIED":"FAIL - CLIENT EXPORT BLOCKED").append("\r\n\r\nUSER FILES\t").append(countFiles.size()).append("\r\n");for(CountFile f:countFiles)b.append(tab(f.name)).append('\t').append(f.rows).append(" rows\t").append(f.quantity).append(" units\r\n");b.append("\r\nMACHINE TOTAL\t").append(sourceTotal).append("\r\nCOMBINED TOTAL\t").append(combinedTotal).append("\r\nCLIENT EXCEL TOTAL\t").append(clientTotal).append("\r\nUNMATCHED BARCODES\t").append(unmatched.size()).append("\r\nFINAL HEADERS\tGTIN | QUANTITY | CATEGORY_ID | RETAIL | DESCRIPTION | COST | DATE | TIME | SECTION\r\n");for(String x:unmatched)b.append("UNMATCHED\t").append(tab(x)).append("\r\n");return b.toString();}

    private void showSource(){status.setText("PETROSOFT SOURCE READY\n\nSource: "+sourceName+"\nCountable source products: "+sourceRows+"\nMaster / OnHand barcode rows: "+products.size()+"\nLottery category 9 excluded: "+excludedLottery+"\nDuplicate barcodes removed: "+duplicates+"\n\nExport the Master and OnHand files, then conduct the physical inventory.");status.setTextColor(Color.rgb(180,235,255));}
    private void showValidation(){StringBuilder b=new StringBuilder();b.append(validated?"PASS — CLIENT REPORT READY":"FAILED VALIDATION — CLIENT EXPORT BLOCKED").append("\n\nUser count files: ").append(countFiles.size()).append("\nMachine total: ").append(sourceTotal).append("\nCombined total: ").append(combinedTotal).append("\nClient Excel total: ").append(clientTotal).append("\nCombined unique barcodes: ").append(combined.size()).append("\nFinal GTIN rows: ").append(clientRows.size()).append("\nUnmatched barcodes: ").append(unmatched.size());if(!unmatched.isEmpty()){b.append("\n\nUNMATCHED:");for(String x:unmatched)b.append("\n").append(x);}b.append("\n\nLocked client columns:\nGTIN, QUANTITY, CATEGORY_ID, RETAIL, DESCRIPTION, COST, DATE, TIME, SECTION");status.setText(b.toString());status.setTextColor(validated?Color.rgb(120,255,140):Color.rgb(255,130,130));}
    private void setEnabledState(){saveMaster.setEnabled(sourceReady);saveOnHand.setEnabled(sourceReady);chooseCounts.setEnabled(sourceReady);saveCombined.setEnabled(countsReady&&validated);saveClient.setEnabled(countsReady&&validated);saveAudit.setEnabled(countsReady);}
    private Map<String,Integer> headerMap(Map<Integer,String> row){HashMap<String,Integer> m=new HashMap<>();for(Map.Entry<Integer,String> e:row.entrySet())m.put(norm(e.getValue()),e.getKey());return m;}
    private String get(Map<Integer,String> row,Map<String,Integer> cols,String name){Integer c=cols.get(name);return c==null?"":clean(row.get(c));}
    private String norm(String s){return clean(s).toUpperCase(Locale.US).replaceAll("[^A-Z0-9]","");}
    private String plainNumber(String s){String n=clean(s);if(n.endsWith(".0"))n=n.substring(0,n.length()-2);return n;}
    private int find(String[] v,String... names){for(int i=0;i<v.length;i++){String x=norm(v[i]);for(String n:names)if(x.equals(norm(n)))return i;}return -1;}
    private String clientDate(){String s=date==null?"":date.getText().toString().trim();try{Date d=new SimpleDateFormat("MM-dd-yyyy",Locale.US).parse(s);return new SimpleDateFormat("M/d/yyyy",Locale.US).format(d);}catch(Exception e){return s.replace('-','/');}}
    private String day(){String s=date==null?"":date.getText().toString().trim();return s.replace('/','-').replaceAll("[^0-9-]","");}
    private String base(){String s=customer==null?"":customer.getText().toString().trim().toUpperCase(Locale.US);s=s.replaceAll("[^A-Z0-9 _-]","").replaceAll("\\s+"," ").trim();return s.isEmpty()?"CUSTOMER":s;}
    private String first(String a,String b){return a==null||a.trim().isEmpty()?b:a;}
    private String money(String s){try{return String.format(Locale.US,"%.2f",Double.parseDouble(clean(s)));}catch(Exception e){return clean(s).replace("$","");}}
    private String clean(String s){return s==null?"":s.replace('\u00a0',' ').trim();}
    private String tab(String s){return clean(s).replace('\t',' ').replace('\r',' ').replace('\n',' ');}
    private String displayName(Uri uri){Cursor c=null;try{c=getContentResolver().query(uri,new String[]{OpenableColumns.DISPLAY_NAME},null,null,null);if(c!=null&&c.moveToFirst())return c.getString(0);}catch(Exception ignored){}finally{if(c!=null)c.close();}return uri==null?"Selected file":String.valueOf(uri.getLastPathSegment());}
    private void fail(String message){status.setText("ERROR\n\n"+message);status.setTextColor(Color.rgb(255,130,130));Toast.makeText(this,message,Toast.LENGTH_LONG).show();setEnabledState();}
    private EditText input(String hint,String value){EditText e=new EditText(this);e.setHint(hint);e.setText(value);e.setTextColor(Color.WHITE);e.setHintTextColor(Color.LTGRAY);e.setSingleLine(true);e.setPadding(dp(10),0,dp(10),0);LinearLayout.LayoutParams p=params(54);p.setMargins(0,0,0,dp(8));e.setLayoutParams(p);return e;}
    private Button button(String s){Button b=new Button(this);b.setText(s);b.setTextSize(15);b.setAllCaps(false);b.setGravity(Gravity.CENTER);return b;}
    private TextView text(String s,int size,int color){TextView t=new TextView(this);t.setText(s);t.setTextSize(size);t.setTextColor(color);t.setGravity(Gravity.CENTER_VERTICAL);return t;}
    private LinearLayout.LayoutParams params(int h){LinearLayout.LayoutParams p=new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT,dp(h));p.setMargins(0,0,0,dp(8));return p;}
    private int dp(int n){return Math.round(n*getResources().getDisplayMetrics().density);}
}
