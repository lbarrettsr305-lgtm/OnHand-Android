from pathlib import Path
import runpy, re

runpy.run_path('.github/prepare_3067.py', run_name='__main__')

p=Path('app/src/main/java/com/iceinventory/onhand/MainActivity.java')
s=p.read_text()

def rep(old,new,label):
    global s
    if old not in s:
        raise SystemExit('3.0.68 target missing: '+label)
    s=s.replace(old,new,1)

rep('TextView app=text("Onhand Inventory 3.0.67",19,Color.WHITE,true);',
    'TextView app=text("Onhand Inventory 3.0.68",19,Color.WHITE,true);','visible version')
rep('logo.setImageResource(R.drawable.ice_inventory_logo_3066);',
    'logo.setImageResource(R.drawable.ice_onhand_approved);','approved header logo')
rep('String[] choices={"All inventory items","Internet items only"};',
    'String[] choices={"All inventory items","Internet items with pictures"};','export scope')

pattern=r'''    private String internetExportFileName\(String name\) \{.*?    \}\n\n'''
replacement='''    private String internetExportFileName(String name) {
        String n=name==null?"":name.trim();
        if(n.toLowerCase(Locale.US).endsWith(".txt"))n=n.substring(0,n.length()-4);
        if(n.toLowerCase(Locale.US).endsWith(".html"))n=n.substring(0,n.length()-5);
        if(!n.toLowerCase(Locale.US).endsWith(" - internet items with pictures"))n+=" - Internet Items With Pictures";
        return cleanInternetReportName(n);
    }

    private String cleanInternetReportName(String s) {
        String n=s==null?"":s.trim();
        if(n.isEmpty())n=safeFileName(sessionName)+" - Internet Items With Pictures";
        if(n.toLowerCase(Locale.US).endsWith(".txt"))n=n.substring(0,n.length()-4);
        if(!n.toLowerCase(Locale.US).endsWith(".html"))n+=".html";
        return n;
    }

'''
s2,n=re.subn(pattern,replacement,s,count=1,flags=re.S)
if n!=1: raise SystemExit('3.0.68 target missing: internet filename method')
s=s2

rep('String exportTitle=pendingExportInternetOnly?"Export Internet Items":"Export TXT";',
    'String exportTitle=pendingExportInternetOnly?"Export Internet Items With Pictures":"Export TXT";','export title')
rep('String exportMessage=pendingExportInternetOnly?"Internet-added items only • tab-delimited TXT file.":"All inventory items • tab-delimited TXT file.";',
    'String exportMessage=pendingExportInternetOnly?"Separate HTML report • internet-added items with associated product pictures.":"All inventory items • tab-delimited TXT file.";',
    'export message')
rep('.setPositiveButton("Save to Downloads",(d,w)->saveToDownloads(cleanTextName(name.getText().toString())))',
    '.setPositiveButton("Save to Downloads",(d,w)->saveToDownloads(pendingExportInternetOnly?cleanInternetReportName(name.getText().toString()):cleanTextName(name.getText().toString())))',
    'download filename')
rep('.setNeutralButton("Save to Google Drive",(d,w)->startDocumentExport(cleanTextName(name.getText().toString())))',
    '.setNeutralButton("Save to Google Drive",(d,w)->startDocumentExport(pendingExportInternetOnly?cleanInternetReportName(name.getText().toString()):cleanTextName(name.getText().toString())))',
    'drive filename')
rep('values.put(MediaStore.Downloads.MIME_TYPE,"text/plain");',
    'values.put(MediaStore.Downloads.MIME_TYPE,pendingExportInternetOnly?"text/html":"text/plain");','downloads MIME')
rep('i.setType("text/plain");',
    'i.setType(pendingExportInternetOnly?"text/html":"text/plain");','document MIME')

helper='''    private String htmlEscape(String v) {
        String x=v==null?"":v;
        return x.replace("&","&amp;").replace("<","&lt;").replace(">","&gt;")
                .replace("\\\"","&quot;").replace("'","&#39;");
    }

    private String buildInternetItemsHtml() {
        StringBuilder b=new StringBuilder();
        String when=new SimpleDateFormat("yyyy-MM-dd HH:mm",Locale.US).format(new Date());
        b.append("<!doctype html><html><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'>");
        b.append("<title>iCE Internet Items With Pictures</title><style>");
        b.append("body{font-family:Arial,sans-serif;background:#111;color:#eee;margin:20px}h1{color:#ffd200}.meta{color:#bbb;margin-bottom:18px}");
        b.append("table{width:100%;border-collapse:collapse;background:#181818}th,td{border:1px solid #555;padding:8px;vertical-align:top;text-align:left}");
        b.append("th{background:#063b20;color:#ffd200}img{max-width:160px;max-height:160px;object-fit:contain;background:#fff;border-radius:6px}a{color:#65d86e}.none{color:#999;font-style:italic}");
        b.append("</style></head><body><h1>iCE Internet Items With Pictures</h1>");
        b.append("<div class='meta'><b>Inventory:</b> ").append(htmlEscape(sessionName))
         .append("<br><b>User:</b> ").append(htmlEscape(savedUserName()))
         .append("<br><b>Generated:</b> ").append(htmlEscape(when)).append("</div>");
        b.append("<table><tr><th>Picture</th><th>Barcode</th><th>Description</th><th>Quantity</th><th>Location</th><th>Price</th></tr>");
        int count=0;
        for(InventoryDb.Row r:db.items(sessionId)) {
            String d=r.description==null?"":r.description.trim();
            if(!d.startsWith(INTERNET_PREFIX))continue;
            count++;
            String desc=d.substring(INTERNET_PREFIX.length()).trim();
            String imageUrl=prefs().getString(IMAGE_KEY_PREFIX+(r.barcode==null?"":r.barcode),"");
            b.append("<tr><td>");
            if(imageUrl!=null&&!imageUrl.trim().isEmpty()) {
                String u=htmlEscape(imageUrl.trim());
                b.append("<img src='").append(u).append("' alt='Product picture'><br><a href='").append(u).append("'>Open picture</a>");
            } else b.append("<span class='none'>No picture available</span>");
            b.append("</td><td>").append(htmlEscape(r.barcode))
             .append("</td><td>").append(htmlEscape(desc))
             .append("</td><td>").append(r.quantity)
             .append("</td><td>").append(htmlEscape(r.location))
             .append("</td><td>").append(htmlEscape(r.price)).append("</td></tr>");
        }
        if(count==0)b.append("<tr><td colspan='6' class='none'>No internet items in this inventory.</td></tr>");
        b.append("</table></body></html>");
        return b.toString();
    }

'''
marker='    private void writeExport(Uri uri) {\n'
if marker not in s: raise SystemExit('3.0.68 target missing: writeExport marker')
s=s.replace(marker,helper+marker,1)

pattern=r'''    private void writeExport\(Uri uri\) \{.*?    \}\n\n    private void readImport'''
replacement='''    private void writeExport(Uri uri) {
        if(uri==null)return;
        try(OutputStream os=getContentResolver().openOutputStream(uri)) {
            if(os==null)throw new Exception("No output stream");
            if(pendingExportInternetOnly) {
                os.write(buildInternetItemsHtml().getBytes(StandardCharsets.UTF_8));
                toast("Internet items with pictures exported");
            } else {
                os.write(TabTextUtils.exportRows(db.items(sessionId),prefs()).getBytes(StandardCharsets.UTF_8));
                toast("Tab-delimited TXT exported");
            }
        } catch(Exception e){showError("Export failed",e);}
    }

    private void readImport'''
s2,n=re.subn(pattern,replacement,s,count=1,flags=re.S)
if n!=1: raise SystemExit('3.0.68 target missing: writeExport method')
s=s2
p.write_text(s)

p=Path('app/build.gradle')
s=p.read_text().replace('versionCode 30067','versionCode 30068',1).replace("versionName '3.0.67'","versionName '3.0.68'",1)
if 'versionCode 30068' not in s or "versionName '3.0.68'" not in s: raise SystemExit('3.0.68 target missing: Gradle version')
p.write_text(s)

p=Path('app/src/main/AndroidManifest.xml')
s=p.read_text().replace('android:label="iCE Onhand 3.0.67"','android:label="iCE Onhand 3.0.68"',1)
old='''android:icon="@mipmap/ice_launcher"
        android:roundIcon="@mipmap/ice_launcher_round"'''
new='''android:icon="@drawable/ice_onhand_approved"
        android:roundIcon="@drawable/ice_onhand_approved"'''
if old not in s: raise SystemExit('3.0.68 target missing: launcher icon')
s=s.replace(old,new,1)
p.write_text(s)

print('Prepared iCE Onhand 3.0.68: approved raster logo + separate Internet Items picture report')
