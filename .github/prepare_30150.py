from pathlib import Path

base=Path('.github/prepare_30149.py')
exec(compile(base.read_text(),str(base),'exec'),{'__name__':'__main__','__file__':str(base)})

def rep(path,old,new):
    p=Path(path);s=p.read_text()
    if s.count(old)!=1:raise SystemExit('3.0.150 expected one target: '+old[:100])
    p.write_text(s.replace(old,new,1))

rep('app/build.gradle','versionCode 30149','versionCode 30150')
rep('app/build.gradle',"versionName '3.0.149'","versionName '3.0.150'")
rep('app/src/main/AndroidManifest.xml','iCE Onhand 3.0.149','iCE Onhand 3.0.150')
m='app/src/main/java/com/iceinventory/onhand/MainActivity.java'
rep(m,'Onhand Inventory 3.0.149','Onhand Inventory 3.0.150')

rep(m,'user+batchNo+" - ";return prefix+safeFileName(sessionName)+"_Seq"',
    'user+" - ";return prefix+safeFileName(sessionName)+"_Batch"+batchNo+"_Seq"')

b='app/src/main/java/com/iceinventory/onhand/BatchExportText.java'
rep(b,'List<String> order=TabTextUtils.getOrder(prefs,true);',
    'List<String> order=new java.util.ArrayList<>(TabTextUtils.getOrder(prefs,true));\n        if(!order.contains("location"))order.add("location");')

c='app/src/main/java/com/iceinventory/onhand/BatchMergeActivity.java'
rep(c,'REQ_XLSX=4104;','REQ_XLSX=4104,REQ_LOCATION_DETAIL=4105,REQ_LOCATION_TOTALS=4106;')
rep(c,'private Button save,report,excel;',
    'private Button save,report,excel,locationDetail,locationTotals;\n    private final LinkedHashMap<String,Long> userLocationTotals=new LinkedHashMap<>();\n    private final LinkedHashMap<String,Long> locationSums=new LinkedHashMap<>();\n    private final ArrayList<String[]> locationRows=new ArrayList<>();\n    private int missingLocationRows;')
rep(c,'Button close=button("Back to Inventory");',
    '''locationDetail=button("Export User + Location Detail — TXT");locationDetail.setEnabled(false);locationDetail.setOnClickListener(v->saveLocationReport(false));LinearLayout.LayoutParams ld=new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT,dp(54));ld.setMargins(0,dp(8),0,0);page.addView(locationDetail,ld);
        locationTotals=button("Export Location Totals — TXT");locationTotals.setEnabled(false);locationTotals.setOnClickListener(v->saveLocationReport(true));LinearLayout.LayoutParams lt=new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT,dp(54));lt.setMargins(0,dp(8),0,0);page.addView(locationTotals,lt);
        Button close=button("Back to Inventory");''')
rep(c,'else if(request==REQ_XLSX)writeProfessionalXlsx(data.getData());',
    'else if(request==REQ_XLSX)writeProfessionalXlsx(data.getData());else if(request==REQ_LOCATION_DETAIL)writeLocationReport(data.getData(),false);else if(request==REQ_LOCATION_TOTALS)writeLocationReport(data.getData(),true);')
rep(c,'combined.clear();sourceStats.clear();excludedReportFiles.clear();',
    'combined.clear();sourceStats.clear();excludedReportFiles.clear();userLocationTotals.clear();locationSums.clear();locationRows.clear();missingLocationRows=0;locationDetail.setEnabled(false);locationTotals.setEnabled(false);')
rep(c,'excel.setEnabled(verified);\n    }','excel.setEnabled(verified);locationDetail.setEnabled(verified);locationTotals.setEnabled(verified);\n    }')
rep(c,'pi=find(f,"price","retail","cost");','pi=find(f,"price","retail","cost"),li=find(f,"location","loc","area");')
rep(c,'addBatchRow(stat,f,bi,qi,di,pi);','addBatchRow(stat,f,bi,qi,di,pi,li);')
rep(c,'addBatchRow(stat,line.split("\\\\t",-1),bi,qi,di,pi);','addBatchRow(stat,line.split("\\\\t",-1),bi,qi,di,pi,li);')
rep(c,'int bi,int qi,int di,int pi)throws Exception{','int bi,int qi,int di,int pi,int li)throws Exception{')
rep(c,'if(t.price.isEmpty()&&pi>=0&&pi<v.length)t.price=v[pi].replace("$","").trim();',
    '''if(t.price.isEmpty()&&pi>=0&&pi<v.length)t.price=v[pi].replace("$","").trim();
        String location=li>=0&&li<v.length?clean(v[li]):"";
        if(location.isEmpty()){location="Unspecified (older export)";missingLocationRows++;}
        String user=stat.userName.isEmpty()?"External / Unidentified":stat.userName;
        String key=user+"\\u0000"+location;
        userLocationTotals.put(key,Math.addExact(userLocationTotals.getOrDefault(key,0L),q));
        locationSums.put(location,Math.addExact(locationSums.getOrDefault(location,0L),q));
        locationRows.add(new String[]{user,location,String.valueOf(q),code,di>=0&&di<v.length?clean(v[di]):"",pi>=0&&pi<v.length?clean(v[pi]):"",stat.fileName});''')
rep(c,'private void writeCombined(Uri uri)',
    '''private void saveLocationReport(boolean totals){
        if(!verified)return;
        Intent i=new Intent(Intent.ACTION_CREATE_DOCUMENT);i.addCategory(Intent.CATEGORY_OPENABLE);i.setType("text/plain");
        i.putExtra(Intent.EXTRA_TITLE,combinedOutputName(sourceInventoryName()+(totals?" - Location Totals.txt":" - User Location Detail.txt")));
        startActivityForResult(i,totals?REQ_LOCATION_TOTALS:REQ_LOCATION_DETAIL);
    }

    private void writeLocationReport(Uri uri,boolean totals){
        if(uri==null||!verified)return;
        try(OutputStream os=getContentResolver().openOutputStream(uri)){
            if(os==null)throw new Exception("Could not create location report");
            StringBuilder b=new StringBuilder("iCE OnHand ").append(totals?"Location Totals":"User + Location Detail").append("\\r\\n");
            b.append("Inventory\\t").append(clean(sourceInventoryName())).append("\\r\\n");
            b.append("Source total\\t").append(sourceGrandTotal).append("\\r\\n");
            b.append("Location rows without a location in older files\\t").append(missingLocationRows).append("\\r\\n\\r\\n");
            if(totals){
                b.append("Location\\tTotal Quantity\\r\\n");
                long sum=0;
                for(Map.Entry<String,Long> e:locationSums.entrySet()){b.append(clean(e.getKey())).append('\\t').append(e.getValue()).append("\\r\\n");sum=Math.addExact(sum,e.getValue());}
                b.append("GRAND TOTAL\\t").append(sum).append("\\r\\n\\r\\nUser\\tLocation\\tQuantity\\r\\n");
                for(Map.Entry<String,Long> e:userLocationTotals.entrySet()){
                    String[] parts=e.getKey().split("\\u0000",-1);
                    b.append(clean(parts[0])).append('\\t').append(clean(parts[1])).append('\\t').append(e.getValue()).append("\\r\\n");
                }
            }else{
                b.append("User\\tLocation\\tQuantity\\tBarcode\\tDescription\\tPrice\\tSource File\\r\\n");
                for(String[] row:locationRows){for(int j=0;j<row.length;j++){if(j>0)b.append('\\t');b.append(clean(row[j]));}b.append("\\r\\n");}
                b.append("\\r\\nUser\\tLocation\\tQuantity\\r\\n");
                for(Map.Entry<String,Long> e:userLocationTotals.entrySet()){
                    String[] parts=e.getKey().split("\\u0000",-1);
                    b.append(clean(parts[0])).append('\\t').append(clean(parts[1])).append('\\t').append(e.getValue()).append("\\r\\n");
                }
            }
            os.write(b.toString().getBytes(StandardCharsets.UTF_8));status.append("\\n\\nLocation report exported.");
        }catch(Exception e){status.append("\\n\\nLocation report failed: "+e.getMessage());}
    }

    private void writeCombined(Uri uri)''')
print('Prepared iCE OnHand 3.0.150: location preserving batches and combined location reports')
