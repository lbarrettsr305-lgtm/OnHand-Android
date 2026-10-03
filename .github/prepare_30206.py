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
pat = r"    private static final class Total \{.*?\n    \}"
s,n=re.subn(pat, '''    private static final class Total {
        String barcode="",description="",itemNumber="",price="",location="";
        double quantity;
    }''', s, count=1, flags=re.S)
if n!=1: raise SystemExit("Batch merge total model anchor missing")
pat = r"    private (?:long|double) sourceGrandTotal,outputTotal;"
s,n=re.subn(pat, "    private double sourceGrandTotal,outputTotal,locationGrandTotal;", s, count=1)
if n!=1: raise SystemExit("Batch merge grand totals anchor missing")

if "missingLocationRows=0;" not in s: raise SystemExit("Batch location reset anchor missing")
s=s.replace("missingLocationRows=0;","missingLocationRows=0;locationGrandTotal=0;",1)

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
                double q;try{q=QuantityMath.parse(v[qi]);}catch(Exception e){throw new Exception("Invalid quantity for barcode "+code+" in "+stat.fileName);}
                if(li>=v.length||v[li].trim().isEmpty())throw new Exception("Missing location for barcode "+code+" in "+stat.fileName);
                addBatchRow(stat,v,bi,qi,di,pi,ii,li,q);
            }
        }
        return stat;
    }

    private void addBatchRow(BatchStat stat,String[] v,int bi,int qi,int di,int pi,int ii,int li,double q)throws Exception{
        String code=v[bi].trim(),location=clean(v[li]);
        String key=code+"\u0000"+location;
        Total t=combined.get(key);
        if(t==null){t=new Total();t.barcode=code;t.location=location;combined.put(key,t);}
        t.quantity+=q;
        sourceGrandTotal+=q;sourceRows++;stat.rows++;stat.quantity+=q;
        if(t.description.isEmpty()&&di>=0&&di<v.length)t.description=clean(v[di]);
        if(t.itemNumber.isEmpty()&&ii>=0&&ii<v.length)t.itemNumber=clean(v[ii]);
        if(t.price.isEmpty()&&pi>=0&&pi<v.length)t.price=v[pi].replace("$","").trim();
        String user=stat.userName;
        String userLocationKey=user+"\u0000"+location;
        userLocationTotals.put(userLocationKey,userLocationTotals.getOrDefault(userLocationKey,0d)+q);
        locationSums.put(location,locationSums.getOrDefault(location,0d)+q);
        locationRows.add(new String[]{user,location,QuantityMath.format(q),code,di>=0&&di<v.length?clean(v[di]):"",pi>=0&&pi<v.length?clean(v[pi]):"",stat.fileName});
    }

    private int find(String[] h,String... names){for(int i=0;i<h.length;i++){String x=h[i].trim().toLowerCase(Locale.US).replace('_',' ').replace('-',' ');for(String n:names)if(x.equals(n)||x.contains(n))return i;}return -1;}

'''
pat = r"    private BatchStat readOne\(Uri uri\)throws Exception\{.*?    private int find\(String\[\] h,String\.\.\. names\)\{.*?\n"
s,n=re.subn(pat,lambda _:method,s,count=1,flags=re.S)
if n!=1: raise SystemExit("Batch file reader method range not found")
pat = r"        for\(Total t:combined\.values\(\)\)outputTotal=.*?;\n        verified=.*?;"
new = '''        for(Total t:combined.values())outputTotal+=t.quantity;
        for(Double q:locationSums.values())locationGrandTotal+=q;
        verified=errors.isEmpty()&&sourceFiles==selectedFiles&&sourceFiles>0&&QuantityMath.equal(sourceGrandTotal,outputTotal)&&QuantityMath.equal(sourceGrandTotal,locationGrandTotal);'''
s,n=re.subn(pat,lambda _:new,s,count=1,flags=re.S)
if n!=1: raise SystemExit("Batch verification calculation range missing")
pat = r'    private void writeCombined\(Uri uri\)\{.*?\n    \}'
new = '''    private void writeCombined(Uri uri){
        if(uri==null||!verified)return;
        try(OutputStream os=getContentResolver().openOutputStream(uri)){
            if(os==null)throw new Exception("Could not create combined file");
            StringBuilder b=new StringBuilder("QTY\\tBARCODE\\tDESCRIPTION\\tITEM NUMBER\\tLOCATION\\r\\n");
            for(Map.Entry<String,Total> e:combined.entrySet()){
                Total t=e.getValue();
                b.append(QuantityMath.format(t.quantity)).append('\\t').append(clean(t.barcode)).append('\\t').append(clean(t.description)).append('\\t').append(clean(t.itemNumber)).append('\\t').append(clean(t.location)).append("\\r\\n");
            }
            os.write(b.toString().getBytes(StandardCharsets.UTF_8));
            status.append("\\n\\nVerified Victoria customer file exported. Export the Verification Report for the audit record.");
        }catch(Exception e){status.append("\\n\\nExport failed: "+e.getMessage());}
    }'''
s,n=re.subn(pat,lambda _:new,s,count=1,flags=re.S)
if n!=1: raise SystemExit("Combined customer output method range missing")
pat = r"    private String buildVerificationReport\(\)\{.*?    private String displayName"
reportMethod = r'''    private String buildVerificationReport(){
        StringBuilder b=new StringBuilder();
        b.append("iCE OnHand Victoria Batch Reconciliation Report\r\n");
        b.append("Created by\t").append(clean(savedUserName())).append("\r\n");
        b.append("Created at\t").append(new SimpleDateFormat("yyyy-MM-dd HH:mm:ss",Locale.US).format(new Date())).append("\r\n");
        b.append("Status\t").append(verified?"PASS - VERIFIED":"FAIL - NOT VERIFIED").append("\r\n\r\n");
        b.append("Selected Files\t").append(selectedFiles).append("\r\n");
        b.append("Successfully Loaded Files\t").append(sourceFiles).append("\r\n");
        b.append("Source Rows\t").append(sourceRows).append("\r\n");
        b.append("Combined Barcode + Location Rows\t").append(combined.size()).append("\r\n");
        b.append("Source Grand Total Quantity\t").append(QuantityMath.format(sourceGrandTotal)).append("\r\n");
        b.append("Combined / Customer File Quantity\t").append(QuantityMath.format(outputTotal)).append("\r\n");
        b.append("Location Grand Total Quantity\t").append(QuantityMath.format(locationGrandTotal)).append("\r\n");
        b.append("Customer File Difference\t").append(QuantityMath.format(outputTotal-sourceGrandTotal)).append("\r\n");
        b.append("Location Difference\t").append(QuantityMath.format(locationGrandTotal-sourceGrandTotal)).append("\r\n\r\n");
        b.append("Uploader\tSource Batch File\tRows\tQuantity\r\n");
        for(BatchStat stat:sourceStats)b.append(clean(stat.userName)).append('\t').append(clean(stat.fileName)).append('\t').append(stat.rows).append('\t').append(QuantityMath.format(stat.quantity)).append("\r\n");
        b.append("\r\nLocation\tQuantity\r\n");
        for(Map.Entry<String,Double> e:locationSums.entrySet())b.append(clean(e.getKey())).append('\t').append(QuantityMath.format(e.getValue())).append("\r\n");
        b.append("\r\nUser\tLocation\tQuantity\r\n");
        for(Map.Entry<String,Double> e:userLocationTotals.entrySet()){
            String[] parts=e.getKey().split("\\u0000",-1);
            b.append(clean(parts[0])).append('\t').append(clean(parts.length>1?parts[1]:"")).append('\t').append(QuantityMath.format(e.getValue())).append("\r\n");
        }
        b.append("\r\nVerification Method\r\n");
        b.append("1. Every selected inventory source must open successfully.\r\n");
        b.append("2. Each uploader's batch quantity is summed independently, including the Master upload when selected.\r\n");
        b.append("3. Matching barcode + location quantities are combined; the location is written to each customer file row.\r\n");
        b.append("4. PASS requires a named uploader and nonblank location for every counted source row.\r\n");
        b.append("5. PASS requires source, combined/customer-file, and location grand totals to match.\r\n");
        b.append("6. Customer file headers: QTY, BARCODE, DESCRIPTION, ITEM NUMBER, LOCATION.\r\n");
        b.append("\r\nFINAL RESULT\t").append(verified?"PASS - ALL UPLOADS AND LOCATION TOTALS RECONCILE":"FAIL - EXPORT BLOCKED").append("\r\n");
        return b.toString();
    }

    private String displayName''';
s,n=re.subn(pat,lambda _:reportMethod,s,count=1,flags=re.S)
if n!=1: raise SystemExit("Verification report method range missing")
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
