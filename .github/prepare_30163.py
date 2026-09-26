from pathlib import Path

base=Path('.github/prepare_30162.py')
exec(compile(base.read_text(),str(base),'exec'),{'__name__':'__main__','__file__':str(base)})

def rep(path,old,new,label):
 p=Path(path);s=p.read_text()
 if s.count(old)!=1:raise SystemExit('3.0.163 expected one target for '+label+' found '+str(s.count(old)))
 p.write_text(s.replace(old,new,1))

rep('app/build.gradle','versionCode 30162','versionCode 30163','code')
rep('app/build.gradle',"versionName '3.0.162'","versionName '3.0.163'",'name')
rep('app/src/main/AndroidManifest.xml','iCE Onhand 3.0.162','iCE Onhand 3.0.163','manifest')
rep('app/src/main/java/com/iceinventory/onhand/MainActivity.java','Onhand Inventory 3.0.162','Onhand Inventory 3.0.163','header')

p=Path('app/src/main/java/com/iceinventory/onhand/MonthlyInventoryActivity.java');s=p.read_text()
s=s.replace('SAVE_CATEGORY=5109,SAVE_CIGARETTES=5110;','SAVE_CATEGORY=5109,SAVE_CIGARETTES=5110,SAVE_UNMATCHED=5111;',1)
s=s.replace('private final ArrayList<String> unmatched=new ArrayList<>();','private final ArrayList<String> unmatched=new ArrayList<>();\n    private final LinkedHashMap<String,UnmatchedDetail> countDetails=new LinkedHashMap<>();',1)
s=s.replace('private Button chooseSource,saveMaster,saveOnHand,loadDevice,shareOnHand,chooseCounts,saveCombined,saveClient,saveAudit,adjustCount,closeProject,saveCategory,saveCigarettes;','private Button chooseSource,saveMaster,saveOnHand,loadDevice,shareOnHand,chooseCounts,saveCombined,saveClient,saveAudit,adjustCount,closeProject,saveCategory,saveCigarettes,saveUnmatched;',1)
s=s.replace('private static final class CountFile {String name="";int rows;double quantity;}','''private static final class CountFile {String name="";int rows;double quantity;}
    private static final class UnmatchedDetail {
        String description="";
        final LinkedHashMap<String,Double> sources=new LinkedHashMap<>();
        final ArrayList<String> locations=new ArrayList<>();
    }''',1)

old='''        chooseCounts=button("5. Select All User Count Files");chooseCounts.setOnClickListener(v->pickCounts());root.addView(chooseCounts,params(58));
        saveCombined=button("6. Export Verified Combined TXT");'''
new='''        chooseCounts=button("5. Select All User Count Files");chooseCounts.setOnClickListener(v->pickCounts());root.addView(chooseCounts,params(58));
        saveUnmatched=button("REVIEW / EXPORT UNMATCHED ITEMS — TXT");saveUnmatched.setTextColor(Color.BLACK);saveUnmatched.setBackgroundTintList(android.content.res.ColorStateList.valueOf(Color.rgb(255,193,7)));saveUnmatched.setOnClickListener(v->create(SAVE_UNMATCHED,"text/plain",base()+" UNMATCHED ITEMS-"+day()+".txt"));root.addView(saveUnmatched,params(58));
        saveCombined=button("6. Export Verified Combined TXT");'''
if old not in s:raise SystemExit('3.0.163 unmatched button target missing')
s=s.replace(old,new,1)
s=s.replace('combined.clear();countFiles.clear();unmatched.clear();clientRows.clear();','combined.clear();countFiles.clear();unmatched.clear();countDetails.clear();clientRows.clear();')

old_read='''        try(BufferedReader br=new BufferedReader(new InputStreamReader(in,StandardCharsets.UTF_8))){String line;boolean first=true;int qi=0,bi=1;while((line=br.readLine())!=null){if(line.trim().isEmpty()||line.startsWith("#ICE_ONHAND_PROJECT\\t"))continue;String[] v=line.split("\\t",-1);if(first){first=false;int hq=find(v,"quantity","qty","count","on hand","onhand"),hb=find(v,"barcode","upc","gtin");if(hq>=0&&hb>=0){qi=hq;bi=hb;continue;}}if(v.length<=Math.max(qi,bi))continue;String code=v[bi].trim();if(code.isEmpty())continue;double q;try{q=QuantityMath.parse(v[qi]);}catch(Exception e){throw new Exception("Invalid quantity for "+code+" in "+s.name);}Double old=combined.get(code);combined.put(code,(old==null?0:old)+q);s.rows++;s.quantity+=q;sourceTotal=sourceTotal+q;}}'''
new_read='''        try(BufferedReader br=new BufferedReader(new InputStreamReader(in,StandardCharsets.UTF_8))){String line;boolean first=true;int qi=0,bi=1,di=2,li=-1;while((line=br.readLine())!=null){if(line.trim().isEmpty()||line.startsWith("#ICE_ONHAND_PROJECT\\t"))continue;String[] v=line.split("\\t",-1);if(first){first=false;int hq=find(v,"quantity","qty","count","on hand","onhand"),hb=find(v,"barcode","upc","gtin"),hd=find(v,"description","item description","name"),hl=find(v,"location","loc","area");if(hq>=0&&hb>=0){qi=hq;bi=hb;if(hd>=0)di=hd;li=hl;continue;}}if(v.length<=Math.max(qi,bi))continue;String code=v[bi].trim();if(code.isEmpty())continue;double q;try{q=QuantityMath.parse(v[qi]);}catch(Exception e){throw new Exception("Invalid quantity for "+code+" in "+s.name);}Double old=combined.get(code);combined.put(code,(old==null?0:old)+q);UnmatchedDetail detail=countDetails.get(code);if(detail==null){detail=new UnmatchedDetail();countDetails.put(code,detail);}if(di>=0&&di<v.length&&!v[di].trim().isEmpty())detail.description=v[di].trim();detail.sources.put(s.name,detail.sources.getOrDefault(s.name,0d)+q);if(li>=0&&li<v.length&&!v[li].trim().isEmpty()&&!detail.locations.contains(v[li].trim()))detail.locations.add(v[li].trim());s.rows++;s.quantity+=q;sourceTotal=sourceTotal+q;}}'''
start=s.find('        try(BufferedReader br=new BufferedReader(new InputStreamReader(in,StandardCharsets.UTF_8)))',s.find('private CountFile readCountFile'))
end=s.find('\n        if(s.rows==0)',start)
if start<0 or end<0:raise SystemExit('3.0.163 read target missing')
s=s[:start]+new_read+s[end:]

s=s.replace('''        else if(request==SAVE_AUDIT){use.write(auditText().getBytes(StandardCharsets.UTF_8));auditExported=true;workflowPrefs().edit().putBoolean("audit_exported",true).apply();}''','''        else if(request==SAVE_AUDIT){use.write(auditText().getBytes(StandardCharsets.UTF_8));auditExported=true;workflowPrefs().edit().putBoolean("audit_exported",true).apply();}
        else if(request==SAVE_UNMATCHED){if(unmatched.isEmpty())throw new Exception("There are no unmatched items");use.write(unmatchedText().getBytes(StandardCharsets.UTF_8));}''',1)

anchor='    private String auditText(){'
unmatched_method='''    private String unmatchedText(){StringBuilder b=new StringBuilder("ICE ONHAND UNMATCHED ITEMS — ACTION REQUIRED\\r\\n");b.append("CUSTOMER\\t").append(tab(base())).append("\\r\\nINVENTORY DATE\\t").append(clientDate()).append("\\r\\nSTATUS\\tCLIENT EXPORT BLOCKED UNTIL THESE ITEMS ARE RESOLVED\\r\\n\\r\\nBARCODE\\tQUANTITY\\tDESCRIPTION\\tCOUNTER FILES\\tLOCATIONS\\r\\n");double total=0;for(String code:unmatched){UnmatchedDetail d=countDetails.get(code);double q=combined.getOrDefault(code,0d);total+=q;b.append(tab(code)).append('\\t').append(QuantityMath.format(q)).append('\\t').append(tab(d==null?"":d.description)).append('\\t').append(tab(sourceText(d))).append('\\t').append(tab(d==null?"":android.text.TextUtils.join(", ",d.locations))).append("\\r\\n");}b.append("\\r\\nUNMATCHED BARCODES\\t").append(unmatched.size()).append("\\r\\nUNMATCHED QUANTITY\\t").append(QuantityMath.format(total)).append("\\r\\n\\r\\nACTION: Verify each barcode. Correct a bad scan, or add the valid product to Price Management and restart validation with the updated source file.\\r\\n");return b.toString();}
    private String sourceText(UnmatchedDetail d){if(d==null)return "";StringBuilder b=new StringBuilder();for(Map.Entry<String,Double> e:d.sources.entrySet()){if(b.length()>0)b.append("; ");b.append(e.getKey()).append(" = ").append(QuantityMath.format(e.getValue()));}return b.toString();}

'''
if anchor not in s:raise SystemExit('3.0.163 audit anchor missing')
s=s.replace(anchor,unmatched_method+anchor,1)

old_show='''    private void showValidation(){StringBuilder b=new StringBuilder();b.append(validated?"PASS — CLIENT REPORT READY":"FAILED VALIDATION — CLIENT EXPORT BLOCKED").append("\\n\\nUser count files: ").append(countFiles.size()).append("\\nMachine total: ").append(sourceTotal).append("\\nCombined total: ").append(combinedTotal).append("\\nClient Excel total: ").append(clientTotal).append("\\nCombined unique barcodes: ").append(combined.size()).append("\\nFinal GTIN rows: ").append(clientRows.size()).append("\\nUnmatched barcodes: ").append(unmatched.size());if(!unmatched.isEmpty()){b.append("\\n\\nUNMATCHED:");for(String x:unmatched)b.append("\\n").append(x);}b.append("\\n\\nLocked client columns:\\nGTIN, QUANTITY, CATEGORY_ID, RETAIL, DESCRIPTION, COST, DATE, TIME, SECTION");status.setText(b.toString());status.setTextColor(validated?Color.rgb(120,255,140):Color.rgb(255,130,130));}'''
new_show='''    private void showValidation(){StringBuilder b=new StringBuilder();b.append(validated?"PASS — CLIENT REPORT READY":"FAILED VALIDATION — ACTION REQUIRED").append("\\n\\nUser count files: ").append(countFiles.size()).append("\\nMachine total: ").append(QuantityMath.format(sourceTotal)).append("\\nCombined total: ").append(QuantityMath.format(combinedTotal)).append("\\nClient Excel total: ").append(QuantityMath.format(clientTotal)).append("\\nDifference requiring review: ").append(QuantityMath.format(combinedTotal-clientTotal)).append("\\nCombined unique barcodes: ").append(combined.size()).append("\\nFinal GTIN rows: ").append(clientRows.size()).append("\\nUnmatched barcodes: ").append(unmatched.size());if(!unmatched.isEmpty()){b.append("\\n\\nUNMATCHED ITEMS:");for(String code:unmatched){UnmatchedDetail d=countDetails.get(code);b.append("\\n\\n").append(code).append("  •  Qty ").append(QuantityMath.format(combined.getOrDefault(code,0d)));if(d!=null&&!d.description.isEmpty())b.append("\\n").append(d.description);b.append("\\nFrom: ").append(sourceText(d));if(d!=null&&!d.locations.isEmpty())b.append("\\nLocation: ").append(android.text.TextUtils.join(", ",d.locations));}b.append("\\n\\nPress REVIEW / EXPORT UNMATCHED ITEMS to save the correction list. Verify bad scans or add valid products to Price Management, then re-import and validate again.");}b.append("\\n\\nLocked client columns:\\nGTIN, QUANTITY, CATEGORY_ID, RETAIL, DESCRIPTION, COST, DATE, TIME, SECTION");status.setText(b.toString());status.setTextColor(validated?Color.rgb(120,255,140):Color.rgb(255,130,130));}'''
if old_show not in s:raise SystemExit('3.0.163 validation target missing')
s=s.replace(old_show,new_show,1)

s=s.replace('saveAudit.setEnabled(countsReady);if(adjustCount!=null)','saveAudit.setEnabled(countsReady);if(saveUnmatched!=null)saveUnmatched.setEnabled(countsReady&&!unmatched.isEmpty());if(adjustCount!=null)',1)
p.write_text(s)

checks={'version':"versionName '3.0.163'" in Path('app/build.gradle').read_text(),'button':'REVIEW / EXPORT UNMATCHED ITEMS' in s,'sources':'sourceText(d)' in s,'blocked':'CLIENT EXPORT BLOCKED UNTIL THESE ITEMS ARE RESOLVED' in s}
bad=[k for k,v in checks.items() if not v]
if bad:raise SystemExit('3.0.163 checks failed: '+', '.join(bad))
print('Prepared iCE OnHand 3.0.163: actionable unmatched-item validation and export')
