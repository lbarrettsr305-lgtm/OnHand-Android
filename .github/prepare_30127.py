from pathlib import Path

base=Path('.github/prepare_30126.py')
exec(compile(base.read_text(),str(base),'exec'),{'__name__':'__main__','__file__':str(base)})

p=Path('app/build.gradle')
g=p.read_text().replace('versionCode 30126','versionCode 30127',1).replace("versionName '3.0.126'","versionName '3.0.127'",1)
if 'versionCode 30127' not in g: raise SystemExit('3.0.127 Gradle target missing')
p.write_text(g)

p=Path('app/src/main/java/com/iceinventory/onhand/MainActivity.java')
s=p.read_text().replace('Onhand Inventory 3.0.126','Onhand Inventory 3.0.127',1)
old='String[] choices={"Petrosoft Monthly Inventory","Standard TXT Inventory"};'
new='String[] choices={"Petrosoft Monthly Inventory","LiqPOS Inventory","Standard TXT Inventory"};'
if old not in s: raise SystemExit('3.0.127 target missing: import templates')
s=s.replace(old,new,1)
old='if(which==0)startActivityForResult(new Intent(this,MonthlyInventoryActivity.class),REQ_MONTHLY_INVENTORY);\n                    else startImportFormatFlow();'
new='if(which==0)startActivityForResult(new Intent(this,MonthlyInventoryActivity.class),REQ_MONTHLY_INVENTORY);\n                    else if(which==1)startActivity(new Intent(this,LiqPosInventoryActivity.class));\n                    else startImportFormatFlow();'
if old not in s: raise SystemExit('3.0.127 target missing: import choice handler')
s=s.replace(old,new,1)
old='private boolean monthlyWorkflowMode;'
new='private boolean monthlyWorkflowMode,liqPosWorkflowMode;'
if old not in s: raise SystemExit('3.0.127 target missing: workflow flags')
s=s.replace(old,new,1)
old='monthlyWorkflowMode=getIntent()!=null&&getIntent().getBooleanExtra(MonthlyInventoryActivity.EXTRA_MONTHLY_WORKFLOW,false);'
new='monthlyWorkflowMode=getIntent()!=null&&getIntent().getBooleanExtra(MonthlyInventoryActivity.EXTRA_MONTHLY_WORKFLOW,false);liqPosWorkflowMode=getIntent()!=null&&getIntent().getBooleanExtra(LiqPosInventoryActivity.EXTRA_LIQPOS_WORKFLOW,false);'
s=s.replace(old,new,1)
anchor='''        root.addView(label("Barcode"));'''
addition='''        android.content.SharedPreferences lpw=getSharedPreferences("liqpos_workflow_state",MODE_PRIVATE);
        boolean liqActive=lpw.getBoolean("active",false);
        if(liqPosWorkflowMode||liqActive) {
            Button liq=button(liqPosWorkflowMode?"↩ RETURN TO LIQPOS — STEP 5":"↩ RESUME LIQPOS INVENTORY",2);
            liq.setTypeface(Typeface.DEFAULT,Typeface.BOLD);
            liq.setOnClickListener(v->{hideKeyboard();if(liqPosWorkflowMode)finish();else startActivity(new Intent(this,LiqPosInventoryActivity.class));});
            LinearLayout.LayoutParams llp=new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT,dp(50));llp.setMargins(0,dp(4),0,dp(4));root.addView(liq,llp);
        }

'''+anchor
if anchor not in s: raise SystemExit('3.0.127 target missing: barcode anchor')
s=s.replace(anchor,addition,1)
p.write_text(s)

java=Path('app/src/main/java/com/iceinventory/onhand/LiqPosInventoryActivity.java')
java.write_text(r'''package com.iceinventory.onhand;

import android.app.Activity;
import android.app.AlertDialog;
import android.content.Intent;
import android.graphics.Color;
import android.net.Uri;
import android.os.Bundle;
import android.view.Gravity;
import android.view.ViewGroup;
import android.widget.*;
import java.io.*;
import java.math.BigDecimal;
import java.math.RoundingMode;
import java.nio.charset.StandardCharsets;
import java.text.SimpleDateFormat;
import java.util.*;

public final class LiqPosInventoryActivity extends Activity {
 public static final String EXTRA_LIQPOS_WORKFLOW="liqpos_workflow";
 private static final int PICK_DBF=6201,PICK_COUNTS=6202,SAVE_COMBINED=6203,SAVE_CLIENT=6204,SAVE_AUDIT=6205,SHARE=6206;
 private static final class Product{String barcode,description,price;}
 private static final class Field{String name;int length,offset;Field(String n,int l,int o){name=n;length=l;offset=o;}}
 private final LinkedHashMap<String,Product> products=new LinkedHashMap<>();
 private final LinkedHashMap<String,Long> combined=new LinkedHashMap<>();
 private EditText store,date;private TextView summary,status;private Button prepare,test,share,counts,saveCombined,saveClient,saveAudit,close;
 private Uri shareUri;private long sessionId=-1;private boolean sourceReady,onhandReady,countsReady,validated,combinedSaved,clientSaved,auditSaved;
 private int dbfRows,blank,invalid,duplicates,normalized;private String sourceName="";
 @Override public void onCreate(Bundle b){super.onCreate(b);buildUi();restore();}
 private int dp(int n){return Math.round(n*getResources().getDisplayMetrics().density);}
 private Button button(String x){Button b=new Button(this);b.setText(x);b.setTextSize(15);b.setAllCaps(false);b.setTextColor(Color.WHITE);return b;}
 private TextView text(String x,int z,int c){TextView t=new TextView(this);t.setText(x);t.setTextSize(z);t.setTextColor(c);return t;}
 private LinearLayout.LayoutParams params(int h){LinearLayout.LayoutParams p=new LinearLayout.LayoutParams(-1,dp(h));p.setMargins(0,0,0,dp(8));return p;}
 private TextView section(String x){TextView t=text(x,15,Color.rgb(255,193,7));t.setPadding(2,12,2,6);return t;}
 private void buildUi(){
  ScrollView sv=new ScrollView(this);LinearLayout root=new LinearLayout(this);root.setOrientation(LinearLayout.VERTICAL);root.setPadding(dp(16),dp(16),dp(16),dp(24));root.setBackgroundColor(Color.rgb(8,24,27));sv.addView(root);
  root.addView(text("LiqPOS Inventory",26,Color.rgb(255,215,0)));root.addView(text("POS FORMAT PROFILE — LiqPOS DBF / Barcode,Quantity CSV",15,Color.WHITE));
  root.addView(section("STORE NAME / FILE PREFIX — REQUIRED"));store=new EditText(this);store.setHint("Example: GARDENWINE");store.setTextColor(Color.WHITE);store.setHintTextColor(Color.LTGRAY);store.setSingleLine();root.addView(store,params(54));
  date=new EditText(this);date.setText(new SimpleDateFormat("MM-dd-yyyy",Locale.US).format(new Date()));date.setTextColor(Color.WHITE);date.setSingleLine();root.addView(date,params(54));
  root.addView(section("IMPORT CUSTOMER FILE"));Button pick=button("1. Import LiqPOS Customer DBF");pick.setOnClickListener(v->pickDbf());root.addView(pick,params(58));
  summary=text("NOT IMPORTED\\nSelect the customer .dbf product file.",15,Color.LTGRAY);summary.setPadding(dp(10),dp(10),dp(10),dp(10));summary.setBackgroundColor(Color.DKGRAY);root.addView(summary);
  root.addView(section("PREPARE COUNT FILES"));prepare=button("2. Prepare OnHand File for Sharing");prepare.setOnClickListener(v->prepare());root.addView(prepare,params(54));
  test=button("3. Test Scan on This Device");test.setOnClickListener(v->openCount(false));root.addView(test,params(54));
  share=button("4. Share File With All Users");share.setOnClickListener(v->share());root.addView(share,params(54));
  root.addView(section("AFTER PHYSICAL COUNT — EXPORT"));counts=button("5. Select All User Count Files");counts.setOnClickListener(v->pickCounts());root.addView(counts,params(58));
  saveCombined=button("6. Export Verified Combined TXT");saveCombined.setOnClickListener(v->create(SAVE_COMBINED,"text/plain",base()+" ALL-INVENTORY-"+day()+".txt"));root.addView(saveCombined,params(54));
  saveClient=button("7. Export LiqPOS Barcode-Quantity CSV");saveClient.setOnClickListener(v->create(SAVE_CLIENT,"text/csv",base()+" UPLOAD TO LIQ POS "+day()+".csv"));root.addView(saveClient,params(58));
  saveAudit=button("Export LiqPOS Verification Report");saveAudit.setOnClickListener(v->create(SAVE_AUDIT,"text/plain",base()+" LIQPOS VERIFICATION-"+day()+".txt"));root.addView(saveAudit,params(54));
  root.addView(section("PROJECT CONTROL"));close=button("8. Close LiqPOS Project");close.setOnClickListener(v->closeProject());root.addView(close,params(58));
  status=text("Start by entering the store name and importing the LiqPOS DBF.",16,Color.WHITE);status.setPadding(0,dp(12),0,dp(12));root.addView(status);
  Button back=button("Back to Inventory");back.setOnClickListener(v->finish());root.addView(back,params(52));setContentView(sv);setEnabled();
 }
 private void pickDbf(){if(base().equals("CUSTOMER")){store.setError("Store name is required");return;}Intent i=new Intent(Intent.ACTION_OPEN_DOCUMENT);i.addCategory(Intent.CATEGORY_OPENABLE);i.setType("*/*");startActivityForResult(i,PICK_DBF);}
 private void pickCounts(){Intent i=new Intent(Intent.ACTION_OPEN_DOCUMENT);i.addCategory(Intent.CATEGORY_OPENABLE);i.setType("*/*");i.putExtra(Intent.EXTRA_ALLOW_MULTIPLE,true);startActivityForResult(i,PICK_COUNTS);}
 private void create(int r,String type,String name){Intent i=new Intent(Intent.ACTION_CREATE_DOCUMENT);i.addCategory(Intent.CATEGORY_OPENABLE);i.setType(type);i.putExtra(Intent.EXTRA_TITLE,name);startActivityForResult(i,r);}
 @Override protected void onActivityResult(int r,int result,Intent data){super.onActivityResult(r,result,data);if(r==SHARE){openCount(true);return;}if(result!=RESULT_OK||data==null)return;try{if(r==PICK_DBF)loadDbf(data.getData(),true);else if(r==PICK_COUNTS)loadCounts(data);else write(r,data.getData());}catch(Exception e){fail(e.getMessage());}}
 private static int u16(byte[]b,int p){return (b[p]&255)|((b[p+1]&255)<<8);}private static long u32(byte[]b,int p){return (b[p]&255L)|((b[p+1]&255L)<<8)|((b[p+2]&255L)<<16)|((b[p+3]&255L)<<24);}
 private void loadDbf(Uri uri,boolean preserve)throws Exception{
  byte[] b;try(InputStream in="file".equals(uri.getScheme())?new FileInputStream(uri.getPath()):getContentResolver().openInputStream(uri);ByteArrayOutputStream out=new ByteArrayOutputStream()){if(in==null)throw new Exception("Could not open DBF");byte[] q=new byte[32768];int n;while((n=in.read(q))>0)out.write(q,0,n);b=out.toByteArray();}
  if(b.length<64||b[0]!=3)throw new Exception("Unsupported DBF. Expected dBase III / FoxBase DBF.");
  int rows=(int)u32(b,4),header=u16(b,8),record=u16(b,10),pos=32,off=1;ArrayList<Field> fs=new ArrayList<>();
  while(pos+32<=b.length&&b[pos]!=13){String name=new String(b,pos,11,StandardCharsets.US_ASCII).replace("\0","").trim().toUpperCase(Locale.US);int len=b[pos+16]&255;fs.add(new Field(name,len,off));off+=len;pos+=32;}
  HashMap<String,Field> fm=new HashMap<>();for(Field f:fs)fm.put(f.name,f);for(String req:new String[]{"BARCODE","BRAND","DESCRIP","TYPE","SIZE","PRICE"})if(!fm.containsKey(req))throw new Exception("DBF is missing "+req);
  products.clear();dbfRows=blank=invalid=duplicates=normalized=0;
  for(int i=0;i<rows;i++){int rp=header+i*record;if(rp+record>b.length)break;if(b[rp]=='*')continue;dbfRows++;String code=value(b,rp,fm.get("BARCODE"));if(code.startsWith(".")&&code.substring(1).matches("\\d+")){code=code.substring(1);normalized++;}if(code.isEmpty()){blank++;continue;}if(code.length()<2){invalid++;continue;}if(products.containsKey(code)){duplicates++;continue;}Product p=new Product();p.barcode=code;p.description=join(value(b,rp,fm.get("BRAND")),value(b,rp,fm.get("DESCRIP")),value(b,rp,fm.get("TYPE")),value(b,rp,fm.get("SIZE")));p.price=money(value(b,rp,fm.get("PRICE")));products.put(code,p);}
  sourceName=uri.getLastPathSegment()==null?"LiqPOS DBF":uri.getLastPathSegment();sourceReady=!products.isEmpty();onhandReady=countsReady=validated=false;if(preserve)saveSource(b);showSource();setEnabled();
 }
 private String value(byte[]b,int r,Field f){return new String(b,r+f.offset,f.length,java.nio.charset.Charset.forName("Cp1252")).trim();}
 private String join(String...v){StringBuilder b=new StringBuilder();for(String x:v)if(!x.isEmpty()){if(b.length()>0)b.append('-');b.append(x);}return b.toString();}
 private String money(String x){try{return new BigDecimal(x).setScale(2,RoundingMode.HALF_UP).toPlainString();}catch(Exception e){return x;}}
 private void saveSource(byte[]b)throws Exception{try(FileOutputStream o=new FileOutputStream(new File(getFilesDir(),"liqpos_source.dbf"))){o.write(b);}getSharedPreferences("liqpos_workflow_state",MODE_PRIVATE).edit().putBoolean("active",true).putString("store",base()).putString("date",date.getText().toString()).apply();}
 private void restore(){android.content.SharedPreferences p=getSharedPreferences("liqpos_workflow_state",MODE_PRIVATE);File f=new File(getFilesDir(),"liqpos_source.dbf");if(!p.getBoolean("active",false)||!f.isFile())return;store.setText(p.getString("store",""));date.setText(p.getString("date",date.getText().toString()));try{loadDbf(Uri.fromFile(f),false);Toast.makeText(this,"LiqPOS project restored",Toast.LENGTH_LONG).show();}catch(Exception e){fail("Could not restore LiqPOS project: "+e.getMessage());}}
 private void showSource(){summary.setText("✓ IMPORTED: "+sourceName+"\\nDBF RECORDS: "+dbfRows+"\\nONHAND PRODUCTS: "+products.size()+"\\nBLANK EXCLUDED: "+blank+"  INVALID EXCLUDED: "+invalid+"\\nDUPLICATES REMOVED: "+duplicates+"  BARCODES NORMALIZED: "+normalized);summary.setTextColor(Color.WHITE);summary.setBackgroundColor(Color.rgb(20,105,55));status.setText("DBF validated. Prepare the OnHand file, test, and share.");}
 private void prepare(){try{File d=new File(getCacheDir(),"shared");d.mkdirs();File f=new File(d,base()+" ONHAND-"+day()+".txt");try(FileOutputStream o=new FileOutputStream(f)){for(Product p:products.values())o.write(("0\\t"+tab(p.barcode)+"\\t"+tab(p.description)+"\\t"+p.price+"\\r\\n").getBytes(StandardCharsets.UTF_8));}shareUri=Uri.parse("content://"+getPackageName()+".fileprovider/onhand/"+Uri.encode(f.getName()));onhandReady=true;setEnabled();Toast.makeText(this,"LiqPOS OnHand file prepared",Toast.LENGTH_LONG).show();}catch(Exception e){fail(e.getMessage());}}
 private void openCount(boolean afterShare){try{if(sessionId<=0){InventoryDb db=new InventoryDb(this);sessionId=db.createSession(base()+" "+day());for(Product p:products.values())db.addOrIncrement(sessionId,p.barcode,p.description,p.price,0,"Main");db.close();}Intent i=new Intent(this,MainActivity.class);i.putExtra(MonthlyInventoryActivity.EXTRA_SESSION_ID,sessionId);i.putExtra(MonthlyInventoryActivity.EXTRA_SESSION_NAME,base()+" "+day());i.putExtra(EXTRA_LIQPOS_WORKFLOW,true);startActivity(i);if(afterShare)Toast.makeText(this,"Begin counting on this machine",Toast.LENGTH_LONG).show();}catch(Exception e){fail(e.getMessage());}}
 private void share(){if(shareUri==null){fail("Prepare the OnHand file first");return;}Intent i=new Intent(Intent.ACTION_SEND);i.setType("text/plain");i.putExtra(Intent.EXTRA_STREAM,shareUri);i.setClipData(android.content.ClipData.newRawUri("LiqPOS OnHand file",shareUri));i.addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION);startActivityForResult(Intent.createChooser(i,"Share LiqPOS count file"),SHARE);}
 private void loadCounts(Intent data)throws Exception{combined.clear();ArrayList<Uri> us=new ArrayList<>();if(data.getClipData()!=null)for(int i=0;i<data.getClipData().getItemCount();i++)us.add(data.getClipData().getItemAt(i).getUri());else if(data.getData()!=null)us.add(data.getData());if(us.isEmpty())throw new Exception("No count files selected");for(Uri u:us)readCount(u);ArrayList<String> bad=new ArrayList<>();for(String x:combined.keySet())if(!products.containsKey(x))bad.add(x);validated=bad.isEmpty();countsReady=true;combinedSaved=clientSaved=auditSaved=false;status.setText((validated?"PASS — LIQPOS EXPORT READY":"FAILED — UNKNOWN BARCODES")+"\\nUser files: "+us.size()+"\\nUnique counted barcodes: "+positiveCount()+"\\nTotal quantity: "+total()+"\\nUnknown barcodes: "+bad.size());status.setTextColor(validated?Color.rgb(120,255,140):Color.rgb(255,130,130));setEnabled();}
 private void readCount(Uri u)throws Exception{String name=String.valueOf(u.getLastPathSegment()).toLowerCase(Locale.US);if(name.contains("combined")||name.contains("verification")||name.contains("upload to liq"))throw new Exception("Output/report selected as a user count file");try(BufferedReader br=new BufferedReader(new InputStreamReader(getContentResolver().openInputStream(u),StandardCharsets.UTF_8))){String line;boolean first=true;int bi=1,qi=0,rows=0;while((line=br.readLine())!=null){if(line.trim().isEmpty())continue;List<String> v=line.indexOf('\t')>=0?Arrays.asList(line.split("\\t",-1)):CsvUtils.parseLine(line);if(first){first=false;int hb=find(v,"barcode"),hq=find(v,"quantity");if(hb>=0&&hq>=0){bi=hb;qi=hq;continue;}}if(v.size()<=Math.max(bi,qi))continue;String code=v.get(bi).trim();if(code.isEmpty())continue;long q;try{q=Long.parseLong(v.get(qi).replace(",","").trim());}catch(Exception e){throw new Exception("Invalid quantity for "+code);}combined.put(code,Math.addExact(combined.getOrDefault(code,0L),q));rows++;}if(rows==0)throw new Exception("Count file contains no rows");}}
 private int find(List<String>v,String n){for(int i=0;i<v.size();i++)if(v.get(i).trim().toLowerCase(Locale.US).replace("_"," ").contains(n))return i;return-1;}
 private long total(){long n=0;for(long q:combined.values())n=Math.addExact(n,q);return n;}private int positiveCount(){int n=0;for(long q:combined.values())if(q>0)n++;return n;}
 private List<Map.Entry<String,Long>> sorted(){ArrayList<Map.Entry<String,Long>> a=new ArrayList<>();for(Map.Entry<String,Long>e:combined.entrySet())if(e.getValue()>0)a.add(e);Collections.sort(a,(x,y)->{int c=Long.compare(y.getValue(),x.getValue());return c!=0?c:x.getKey().compareTo(y.getKey());});return a;}
 private void write(int r,Uri u)throws Exception{if(u==null)return;try(OutputStream o=getContentResolver().openOutputStream(u)){if(o==null)throw new Exception("Could not create file");if(r==SAVE_COMBINED){for(Map.Entry<String,Long>e:sorted()){Product p=products.get(e.getKey());o.write((e.getValue()+"\\t"+e.getKey()+"\\t"+tab(p.description)+"\\t"+p.price+"\\r\\n").getBytes(StandardCharsets.UTF_8));}combinedSaved=true;}else if(r==SAVE_CLIENT){if(!validated)throw new Exception("Validation must pass first");o.write("Barcode,Quantity\\r\\n".getBytes(StandardCharsets.US_ASCII));for(Map.Entry<String,Long>e:sorted())o.write((e.getKey()+","+e.getValue()+"\\r\\n").getBytes(StandardCharsets.US_ASCII));clientSaved=true;}else{o.write(("ICE ONHAND LIQPOS VERIFICATION\\r\\nSTORE\\t"+base()+"\\r\\nSOURCE\\t"+sourceName+"\\r\\nSTATUS\\t"+(validated?"PASS":"FAIL")+"\\r\\nPRODUCTS\\t"+products.size()+"\\r\\nCOUNTED BARCODES\\t"+positiveCount()+"\\r\\nTOTAL QUANTITY\\t"+total()+"\\r\\nFINAL HEADERS\\tBarcode,Quantity\\r\\n").getBytes(StandardCharsets.UTF_8));auditSaved=true;}}Toast.makeText(this,"File created successfully",Toast.LENGTH_LONG).show();setEnabled();}
 private void closeProject(){if(!(combinedSaved&&clientSaved&&auditSaved)){fail("Export the combined TXT, LiqPOS CSV, and verification report first");return;}new AlertDialog.Builder(this).setTitle("Close LiqPOS Project?").setMessage("Exported files and inventory counts will remain available.").setNegativeButton("Cancel",null).setPositiveButton("Close",(d,w)->{getSharedPreferences("liqpos_workflow_state",MODE_PRIVATE).edit().putBoolean("active",false).apply();Intent h=new Intent(this,MainActivity.class);h.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK|Intent.FLAG_ACTIVITY_CLEAR_TASK);startActivity(h);finish();}).show();}
 private void setEnabled(){if(prepare==null)return;prepare.setEnabled(sourceReady);test.setEnabled(onhandReady);share.setEnabled(onhandReady);counts.setEnabled(sourceReady);saveCombined.setEnabled(countsReady&&validated);saveClient.setEnabled(countsReady&&validated);saveAudit.setEnabled(countsReady);close.setEnabled(combinedSaved&&clientSaved&&auditSaved);}
 private String base(){String x=store==null?"":store.getText().toString().trim().toUpperCase(Locale.US).replaceAll("[^A-Z0-9 _-]","");return x.isEmpty()?"CUSTOMER":x;}private String day(){return date.getText().toString().replace('/','-').replaceAll("[^0-9-]","");}private String tab(String x){return x==null?"":x.replace('\t',' ').replace('\r',' ').replace('\n',' ');}
 private void fail(String x){if(x==null)x="Unknown error";status.setText("ERROR\\n\\n"+x);status.setTextColor(Color.rgb(255,130,130));Toast.makeText(this,x,Toast.LENGTH_LONG).show();}
}
''')

p=Path('app/src/main/AndroidManifest.xml')
m=p.read_text().replace('iCE Onhand 3.0.126','iCE Onhand 3.0.127',1)
anchor='''    </application>'''
addition='''        <activity android:name=".LiqPosInventoryActivity" android:exported="false" android:screenOrientation="unspecified" />
'''
if '.LiqPosInventoryActivity' not in m:m=m.replace(anchor,addition+anchor,1)
if 'iCE Onhand 3.0.127' not in m: raise SystemExit('3.0.127 manifest version missing')
p.write_text(m)

checks={'liqpos import menu':'LiqPOS Inventory' in s,'dbf parser':'Unsupported DBF' in java.read_text(),'exact csv headers':'Barcode,Quantity' in java.read_text(),'quantity sort':'Long.compare(y.getValue(),x.getValue())' in java.read_text(),'duplicate first':'products.containsKey(code)' in java.read_text(),'activity manifest':'.LiqPosInventoryActivity' in m}
missing=[k for k,v in checks.items() if not v]
if missing:raise SystemExit('3.0.127 verification failed: '+', '.join(missing))
print('Prepared iCE Onhand 3.0.127: separate LiqPOS DBF-to-OnHand-to-Barcode,Quantity CSV workflow')
