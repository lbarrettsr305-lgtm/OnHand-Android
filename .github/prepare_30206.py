#!/usr/bin/env python3
from pathlib import Path
import re
import runpy

root = Path(__file__).resolve().parents[1]
workflow = root / ".github/workflows/build-apk.yml"
# The preceding preparation step expects its own 3.0.205 workflow markers.
w = workflow.read_text()
w = w.replace("Prepare and verify 3.0.206 Victoria reconciliation and import/export templates", "Prepare and verify 3.0.205 Victoria import/export templates")
w = w.replace(".github/prepare_30206.py", ".github/prepare_30205.py")
w = w.replace("iCE-Onhand-Inventory-3.0.206", "iCE-Onhand-Inventory-3.0.205")
w = w.replace("iCE-Onhand-Inventory-3.0.205-signed", "iCE-Onhand-Inventory-3.0.205-signed")
workflow.write_text(w)
runpy.run_path(str(root / ".github" / "prepare_30205.py"), run_name="__main__")

# Restore this release's workflow markers after 3.0.205 validated and updated its own.
w = workflow.read_text()
w = w.replace("Prepare and verify 3.0.205 Victoria import/export templates", "Prepare and verify 3.0.206 Victoria reconciliation and import/export templates")
w = w.replace(".github/prepare_30205.py", ".github/prepare_30206.py")
w = w.replace("iCE-Onhand-Inventory-3.0.205-signed", "iCE-Onhand-Inventory-3.0.206-signed")
w = w.replace("iCE-Onhand-Inventory-3.0.205", "iCE-Onhand-Inventory-3.0.206")
workflow.write_text(w)

gradle = root / "app/build.gradle"
s = gradle.read_text()
if "versionName '3.0.205'" not in s or "versionCode 30205" not in s:
    raise SystemExit("3.0.205 version source not found")
gradle.write_text(s.replace("versionCode 30205", "versionCode 30206", 1).replace("versionName '3.0.205'", "versionName '3.0.206'", 1))

manifest = root / "app/src/main/AndroidManifest.xml"
s = manifest.read_text()
if "iCE Onhand 3.0.205" not in s: raise SystemExit("3.0.205 app label missing")
manifest.write_text(s.replace("iCE Onhand 3.0.205", "iCE Onhand 3.0.206", 1))

main = root / "app/src/main/java/com/iceinventory/onhand/MainActivity.java"
s = main.read_text()
if "Onhand Inventory 3.0.205" not in s: raise SystemExit("3.0.205 screen version missing")
main.write_text(s.replace("Onhand Inventory 3.0.205", "Onhand Inventory 3.0.206", 1))

p = root / "app/src/main/java/com/iceinventory/onhand/BatchMergeActivity.java"
s = p.read_text()
old = '''    private static final class Total {
        String barcode="",description="",price="";
        long quantity;
    }'''
new = '''    private static final class Total {
        String barcode="",description="",itemNumber="",price="",location="";
        long quantity;
    }'''
if s.count(old) != 1: raise SystemExit("Batch merge total model anchor missing")
s = s.replace(old, new, 1)
old = "    private long sourceGrandTotal,outputTotal;"
new = "    private long sourceGrandTotal,outputTotal,locationGrandTotal;"
if s.count(old) != 1: raise SystemExit("Batch merge grand totals anchor missing")
s = s.replace(old, new, 1)

method = r'''    private BatchStat readOne(Uri uri)throws Exception{
        BatchStat stat=new BatchStat();stat.fileName=displayName(uri);stat.userName=userPrefix(stat.fileName);
        if(stat.userName.isEmpty())throw new Exception("Uploader name is missing from filename: "+stat.fileName);
        InputStream is=getContentResolver().openInputStream(uri);if(is==null)throw new Exception("Could not open "+stat.fileName);
        try(BufferedReader br=new BufferedReader(new InputStreamReader(is,StandardCharsets.UTF_8))){
            String first;do{first=br.readLine();}while(first!=null&&first.trim().isEmpty());if(first==null)throw new Exception(stat.fileName+" is empty");
            String[] f=first.split("\t",-1);
            int bi=find(f,"barcode","upc","gtin"),qi=find(f,"quantity","qty","count","on hand","onhand"),di=find(f,"description","item description","name"),pi=find(f,"price","retail","cost"),ii=find(f,"item number","itemnumber","sku"),li=find(f,"location","loc","area");
            if(bi<0||qi<0)throw new Exception(stat.fileName+" is missing Barcode or Quantity header");
            if(li<0)throw new Exception(stat.fileName+" is missing Location header. Re-export it with the Victoria template.");
            String line;while((line=br.readLine())!=null){
                if(line.trim().isEmpty())continue;
                String[] v=line.split("\t",-1);if(bi>=v.length||qi>=v.length)throw new Exception("Incomplete row in "+stat.fileName);
                String code=v[bi].trim();if(code.isEmpty())continue;
                long q;try{q=Long.parseLong(v[qi].replace(",","").trim());}catch(Exception e){throw new Exception("Invalid quantity for barcode "+code+" in "+stat.fileName);}
                if(li>=v.length||v[li].trim().isEmpty())throw new Exception("Missing location for barcode "+code+" in "+stat.fileName);
                addBatchRow(stat,v,bi,qi,di,pi,ii,li,q);
            }
        }
        return stat;
    }

    private void addBatchRow(BatchStat stat,String[] v,int bi,int qi,int di,int pi,int ii,int li,long q)throws Exception{
        String code=v[bi].trim(),location=clean(v[li]);
        String key=code+"\u0000"+location;
        Total t=combined.get(key);
        if(t==null){t=new Total();t.barcode=code;t.location=location;combined.put(key,t);}
        t.quantity=Math.addExact(t.quantity,q);
        sourceGrandTotal=Math.addExact(sourceGrandTotal,q);sourceRows++;stat.rows++;stat.quantity=Math.addExact(stat.quantity,q);
        if(t.description.isEmpty()&&di>=0&&di<v.length)t.description=clean(v[di]);
        if(t.itemNumber.isEmpty()&&ii>=0&&ii<v.length)t.itemNumber=clean(v[ii]);
        if(t.price.isEmpty()&&pi>=0&&pi<v.length)t.price=v[pi].replace("$","").trim();
        String user=stat.userName;
        String userLocationKey=user+"\u0000"+location;
        userLocationTotals.put(userLocationKey,Math.addExact(userLocationTotals.getOrDefault(userLocationKey,0L),q));
        locationSums.put(location,Math.addExact(locationSums.getOrDefault(location,0L),q));
        locationRows.add(new String[]{user,location,String.valueOf(q),code,di>=0&&di<v.length?clean(v[di]):"",pi>=0&&pi<v.length?clean(v[pi]):"",stat.fileName});
    }

    private int find(String[] h,String... names){for(int i=0;i<h.length;i++){String x=h[i].trim().toLowerCase(Locale.US).replace('_',' ').replace('-',' ');for(String n:names)if(x.equals(n)||x.contains(n))return i;}return -1;}

'''
pat = r"    private BatchStat readOne\(Uri uri\)throws Exception\{.*?    private int find\(String\[\] h,String\.\.\. names\)\{.*?\n"
s,n=re.subn(pat,lambda _:method,s,count=1,flags=re.S)
if n!=1: raise SystemExit("Batch file reader method range not found")
old='''        for(Total t:combined.values())outputTotal=Math.addExact(outputTotal,t.quantity);
        verified=errors.isEmpty()&&sourceFiles==selectedFiles&&sourceFiles>0&&sourceGrandTotal==outputTotal;'''
new='''        for(Total t:combined.values())outputTotal=Math.addExact(outputTotal,t.quantity);
        for(Long q:locationSums.values())locationGrandTotal=Math.addExact(locationGrandTotal,q);
        verified=errors.isEmpty()&&sourceFiles==selectedFiles&&sourceFiles>0&&sourceGrandTotal==outputTotal&&sourceGrandTotal==locationGrandTotal;'''
if s.count(old)!=1: raise SystemExit("Batch verification calculation anchor missing")
s=s.replace(old,new,1)
old='''        m.append("Source grand total: ").append(sourceGrandTotal).append("\\nCombined grand total: ").append(outputTotal).append("\\nDifference: ").append(outputTotal-sourceGrandTotal).append("\\n\\n");'''
new='''        m.append("Source grand total: ").append(sourceGrandTotal).append("\\nCombined grand total: ").append(outputTotal).append("\\nLocation grand total: ").append(locationGrandTotal).append("\\nCustomer file difference: ").append(outputTotal-sourceGrandTotal).append("\\nLocation difference: ").append(locationGrandTotal-sourceGrandTotal).append("\\n\\n");'''
if s.count(old)!=1: raise SystemExit("Batch on-screen total summary anchor missing")
s=s.replace(old,new,1)
old='''        StringBuilder b=new StringBuilder("Quantity\\tBarcode\\tDescription\\tPrice\\r\\n");for(Map.Entry<String,Total> e:combined.entrySet()){Total t=e.getValue();b.append(t.quantity).append('\\t').append(clean(t.barcode)).append('\\t').append(clean(t.description)).append('\\t').append(clean(t.price)).append("\\r\\n");}'''
new='''        StringBuilder b=new StringBuilder("QTY\\tBARCODE\\tDESCRIPTION\\tITEM NUMBER\\tLOCATION\\r\\n");for(Map.Entry<String,Total> e:combined.entrySet()){Total t=e.getValue();b.append(t.quantity).append('\\t').append(clean(t.barcode)).append('\\t').append(clean(t.description)).append('\\t').append(clean(t.itemNumber)).append('\\t').append(clean(t.location)).append("\\r\\n");}'''
if s.count(old)!=1: raise SystemExit("Combined output format anchor missing")
s=s.replace(old,new,1)
old='''        b.append("Combined Grand Total Quantity\\t").append(outputTotal).append("\\r\\n");
        b.append("Difference\\t").append(outputTotal-sourceGrandTotal).append("\\r\\n\\r\\n");'''
new='''        b.append("Combined Grand Total Quantity\\t").append(outputTotal).append("\\r\\n");
        b.append("Location Grand Total Quantity\\t").append(locationGrandTotal).append("\\r\\n");
        b.append("Customer File Difference\\t").append(outputTotal-sourceGrandTotal).append("\\r\\n");
        b.append("Location Difference\\t").append(locationGrandTotal-sourceGrandTotal).append("\\r\\n\\r\\n");'''
if s.count(old)!=1: raise SystemExit("Verification report totals anchor missing")
s=s.replace(old,new,1)
old='''        b.append("3. Matching barcodes are summed into one combined barcode quantity.\\r\\n");'''
new='''        b.append("3. Matching barcode + location rows are summed; locations are retained in the customer-ready Victoria file.\\r\\n");'''
if s.count(old)!=1: raise SystemExit("Verification method location anchor missing")
s=s.replace(old,new,1)
old='''        b.append("5. PASS requires loaded files = selected files and Source Grand Total = Combined Grand Total.\\r\\n");'''
new='''        b.append("5. PASS requires every uploaded file to include an uploader name and a location on every counted row.\\r\\n");
        b.append("6. PASS requires Source Grand Total = Combined Grand Total = Location Grand Total.\\r\\n");
        b.append("7. The exported customer-ready file uses Victoria headers: QTY, BARCODE, DESCRIPTION, ITEM NUMBER, LOCATION.\\r\\n");'''
if s.count(old)!=1: raise SystemExit("Verification method pass criteria anchor missing")
s=s.replace(old,new,1)
old='''    private String userPrefix(String fileName){String n=fileName==null?"":fileName.trim();int p=n.indexOf(" - ");return p>0?n.substring(0,p).trim():"";}'''
new='''    private String userPrefix(String fileName){
        String n=fileName==null?"":fileName.trim();
        java.util.regex.Matcher m=java.util.regex.Pattern.compile("(?i)^count(.+?)-batch\\d+").matcher(n);
        if(m.find())return m.group(1).trim();
        String upper=n.toUpperCase(Locale.US);
        String marker="BATCH COUNT - ";
        int p=upper.indexOf(marker);
        if(p>=0){String tail=n.substring(p+marker.length()).trim();int cut=tail.indexOf(" - ");return (cut>0?tail.substring(0,cut):tail).trim();}
        int sep=n.indexOf(" - ");return sep>0?n.substring(0,sep).trim():"";
    }'''
if s.count(old)!=1: raise SystemExit("Uploader filename parser anchor missing")
s=s.replace(old,new,1)
p.write_text(s)

checks={
 "version":"versionName '3.0.206'" in gradle.read_text(),
 "Victoria customer headers":"QTY\\tBARCODE\\tDESCRIPTION\\tITEM NUMBER\\tLOCATION" in s,
 "location included in combine key":'String key=code+"\\\\u0000"+location;' in s,
 "location and source totals gate":'sourceGrandTotal==locationGrandTotal' in s,
 "short count filename uploader parsing":'compile("(?i)^count(.+?)-batch\\\\d+")' in s,
 "location header required":'missing Location header' in s,
 "user per-location subtotals retained":'userLocationTotals.put(userLocationKey' in s,
}
failed=[k for k,v in checks.items() if not v]
if failed: raise SystemExit("3.0.206 verification failed: "+", ".join(failed))
print("Prepared iCE OnHand 3.0.206: per-upload user totals, required locations, and reconciled Victoria combined export")
