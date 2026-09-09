from pathlib import Path
import re

# Preserve the complete 3.0.96 master-user, professional workbook and valuation package.
base=Path('.github/prepare_3096_valuation.py')
exec(compile(base.read_text(),str(base),'exec'),{'__name__':'__main__','__file__':str(base)})

# -----------------------------------------------------------------------------
# 3.0.97
# 1) Accept compatible HEADERLESS external tab-delimited files in standard order:
#       Quantity | Barcode | Description | Price
# 2) Make Master Report User selection/status much easier to see.
# 3) Keep all 3.0.96 verification, valuation, branding, and reconciliation rules.
# -----------------------------------------------------------------------------

# ----- MainActivity: make Master Report User control prominent -----
p=Path('app/src/main/java/com/iceinventory/onhand/MainActivity.java')
s=p.read_text()
old='''        Button masterUserButton=button(masterUserButtonLabel(),0);\n        masterUserButton.setOnClickListener(v->setCurrentUserAsMaster());\n        box.addView(masterUserButton,new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT,dp(50)));\n'''
new='''        TextView masterTitle=text("MASTER REPORT USER",18,gold(),true);masterTitle.setPadding(dp(6),dp(14),0,dp(3));box.addView(masterTitle);\n        String currentMaster=savedMasterUserName();\n        TextView masterStatus=text(currentMaster.isEmpty()?"Not set — combined reports are locked":"Current Master: "+currentMaster,16,currentMaster.isEmpty()?Color.rgb(255,140,140):Color.WHITE,true);\n        masterStatus.setPadding(dp(8),dp(4),dp(8),dp(7));box.addView(masterStatus);\n        Button masterUserButton=button(currentMaster.isEmpty()?"SET CURRENT USER AS MASTER":"CHANGE MASTER REPORT USER",2);\n        masterUserButton.setTypeface(Typeface.DEFAULT,Typeface.BOLD);masterUserButton.setTextSize(16);\n        masterUserButton.setOnClickListener(v->setCurrentUserAsMaster());\n        box.addView(masterUserButton,new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT,dp(58)));\n'''
if old not in s:raise SystemExit('3.0.97 target missing: master user option button')
s=s.replace(old,new,1)

# Make the Export menu entry self-explanatory.
s=s.replace('"Combine & Verify User Batches"','"Combine & Verify User Batches — Master User"',1)

# Version.
s=s.replace('Onhand Inventory 3.0.96','Onhand Inventory 3.0.97')
if 'Onhand Inventory 3.0.97' not in s:raise SystemExit('3.0.97 target missing: visible version')
p.write_text(s)

# ----- BatchMergeActivity: headerless compatibility + visible Master User -----
p=Path('app/src/main/java/com/iceinventory/onhand/BatchMergeActivity.java')
m=p.read_text()

# Show authorized master prominently under the title.
old='''        TextView title=text("Combine User Batches",24,Color.rgb(255,215,0));root.addView(title);\n        TextView help=text("Select iCE OnHand batches or compatible external tab-delimited files. Filenames, file extensions, store names, user prefixes, and batch numbers are not required. Barcode and Quantity headers are required; matching barcodes will be summed and reconciled before export.",16,Color.WHITE);help.setPadding(0,dp(10),0,dp(14));root.addView(help);\n'''
new='''        TextView title=text("Combine User Batches",24,Color.rgb(255,215,0));root.addView(title);\n        TextView master=text("MASTER REPORT USER: "+(savedMasterUserName().isEmpty()?"NOT SET":savedMasterUserName()),18,Color.rgb(255,215,0));master.setPadding(0,dp(8),0,dp(4));root.addView(master);\n        TextView help=text("Select iCE OnHand batches or compatible external tab-delimited files. Filenames, file extensions, store names, user prefixes, and batch numbers are not required. Recognizable Barcode and Quantity headers are accepted. Headerless external files are also accepted when they use the standard order Quantity | Barcode | Description | Price. Matching barcodes will be summed and reconciled before export.",16,Color.WHITE);help.setPadding(0,dp(8),0,dp(14));root.addView(help);\n'''
if old not in m:raise SystemExit('3.0.97 target missing: merge title/help block')
m=m.replace(old,new,1)

# Replace reader with safe header/headerless handling.
read_one=r'''    private BatchStat readOne(Uri uri)throws Exception{
        BatchStat stat=new BatchStat();stat.fileName=displayName(uri);stat.userName=userPrefix(stat.fileName);stat.sourceType=stat.userName.isEmpty()?"External Tab-Delimited":"iCE OnHand Batch";
        InputStream is=getContentResolver().openInputStream(uri);if(is==null)throw new Exception("Could not open "+stat.fileName);
        try(BufferedReader br=new BufferedReader(new InputStreamReader(is,StandardCharsets.UTF_8))){
            String first;do{first=br.readLine();}while(first!=null&&first.trim().isEmpty());if(first==null)throw new Exception(stat.fileName+" is empty");
            String[] f=first.split("\\t",-1);
            int bi=find(f,"barcode","upc","gtin"),qi=find(f,"quantity","qty","count","on hand","onhand"),di=find(f,"description","item description","name"),pi=find(f,"price","retail","cost");
            boolean hasHeaders=bi>=0&&qi>=0;
            if(!hasHeaders){
                if(!looksLikeHeaderlessStandard(f))throw new Exception(stat.fileName+" is missing Barcode/Quantity headers and does not match headerless Quantity | Barcode | Description | Price");
                qi=0;bi=1;di=f.length>2?2:-1;pi=f.length>3?3:-1;
                stat.sourceType="External Tab-Delimited (Headerless)";
                addBatchRow(stat,f,bi,qi,di,pi);
            }
            String line;while((line=br.readLine())!=null){if(line.trim().isEmpty())continue;addBatchRow(stat,line.split("\\t",-1),bi,qi,di,pi);}
        }
        return stat;
    }

    private boolean looksLikeHeaderlessStandard(String[] f){
        if(f==null||f.length<2)return false;
        String quantity=f[0]==null?"":f[0].replace("\uFEFF","").replace(",","").trim();
        String barcode=f[1]==null?"":f[1].trim();
        if(quantity.isEmpty()||barcode.isEmpty())return false;
        try{Long.parseLong(quantity);return true;}catch(Exception e){return false;}
    }

    private void addBatchRow(BatchStat stat,String[] v,int bi,int qi,int di,int pi)throws Exception{
        if(v==null||bi<0||qi<0||bi>=v.length||qi>=v.length)return;
        String code=v[bi]==null?"":v[bi].replace("\uFEFF","").trim();if(code.isEmpty())return;
        String raw=v[qi]==null?"":v[qi].replace("\uFEFF","").replace(",","").trim();
        long q;try{q=Long.parseLong(raw);}catch(Exception e){throw new Exception("Invalid quantity for barcode "+code+" in "+stat.fileName);}
        Total t=combined.get(code);if(t==null){t=new Total();t.barcode=code;combined.put(code,t);}t.quantity=Math.addExact(t.quantity,q);
        sourceGrandTotal=Math.addExact(sourceGrandTotal,q);sourceRows++;stat.rows++;stat.quantity=Math.addExact(stat.quantity,q);
        if(t.description.isEmpty()&&di>=0&&di<v.length)t.description=v[di].trim();
        if(t.price.isEmpty()&&pi>=0&&pi<v.length)t.price=v[pi].replace("$","").trim();
    }

'''
pat=r'''    private BatchStat readOne\(Uri uri\)throws Exception\{.*?\n    \}\n\n(?=    private int find\()'''
m,n=re.subn(pat,lambda x:read_one,m,count=1,flags=re.S)
if n!=1:raise SystemExit('3.0.97 target missing: BatchMergeActivity readOne')

# BOM-safe header matching.
old='''    private int find(String[] h,String... names){for(int i=0;i<h.length;i++){String x=h[i].trim().toLowerCase(Locale.US).replace('_',' ').replace('-',' ');for(String n:names)if(x.equals(n)||x.contains(n))return i;}return -1;}'''
new='''    private int find(String[] h,String... names){for(int i=0;i<h.length;i++){String x=h[i].replace("\\uFEFF","").trim().toLowerCase(Locale.US).replace('_',' ').replace('-',' ');for(String n:names)if(x.equals(n)||x.contains(n))return i;}return -1;}'''
if old not in m:raise SystemExit('3.0.97 target missing: header finder')
m=m.replace(old,new,1)

# TXT audit report documents both supported layouts.
m=m.replace('b.append("1. Every selected source file must open successfully.\\r\\n");','b.append("1. Every selected source file must open successfully. Files may use recognizable headers or the headerless standard order Quantity | Barcode | Description | Price.\\r\\n");',1)
p.write_text(m)

# ----- Professional Excel verification note -----
p=Path('app/src/main/java/com/iceinventory/onhand/ProfessionalCombinedXlsxWriter.java')
x=p.read_text()
x=x.replace(
    '1. Each selected file is validated as tab-delimited inventory data by its headers, not by its filename.  2. Barcode and Quantity columns are required; Description and Price are optional.',
    '1. Each selected file is validated by its tab-delimited content, not by its filename.  2. Files may contain recognizable Barcode and Quantity headers, or be headerless in the standard Quantity | Barcode | Description | Price order. Description and Price remain optional for consolidation.',
    1)
p.write_text(x)

# Package/manifest version.
p=Path('app/build.gradle')
g=p.read_text().replace('versionCode 30096','versionCode 30097',1).replace("versionName '3.0.96'","versionName '3.0.97'",1)
if 'versionCode 30097' not in g or "versionName '3.0.97'" not in g:raise SystemExit('3.0.97 target missing: Gradle version')
p.write_text(g)
p=Path('app/src/main/AndroidManifest.xml')
a=p.read_text().replace('iCE Onhand 3.0.96','iCE Onhand 3.0.97')
if 'iCE Onhand 3.0.97' not in a:raise SystemExit('3.0.97 target missing: manifest version')
p.write_text(a)

# Regression checks.
main=Path('app/src/main/java/com/iceinventory/onhand/MainActivity.java').read_text()
merge=Path('app/src/main/java/com/iceinventory/onhand/BatchMergeActivity.java').read_text()
xlsx=Path('app/src/main/java/com/iceinventory/onhand/ProfessionalCombinedXlsxWriter.java').read_text()
checks={
    'prominent master title':'MASTER REPORT USER' in main,
    'master current status':'Current Master:' in main,
    'large gold master button':'CHANGE MASTER REPORT USER' in main and 'dp(58)' in main,
    'master visible on merge screen':'MASTER REPORT USER:' in merge,
    'export menu labels master':'Combine & Verify User Batches — Master User' in main,
    'headerless supported':'looksLikeHeaderlessStandard' in merge and 'External Tab-Delimited (Headerless)' in merge,
    'headerless first row included':'addBatchRow(stat,f,bi,qi,di,pi)' in merge,
    'strict malformed rejection':'does not match headerless Quantity | Barcode | Description | Price' in merge,
    'BOM safe':'replace("\\uFEFF","")' in merge,
    'valuation preserved':'Grand Total Inventory Value' in xlsx and 'Inventory Valuation' in xlsx,
    'professional report preserved':'Formal Verification Note' in xlsx and 'Ice Inventory LLC' in xlsx,
}
missing=[k for k,v in checks.items() if not v]
if missing:raise SystemExit('3.0.97 verification failed: '+', '.join(missing))
print('Prepared iCE Onhand 3.0.97: headerless external batches + prominent Master Report User controls')
