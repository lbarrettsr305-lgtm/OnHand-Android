from pathlib import Path

p=Path('app/src/main/java/com/iceinventory/onhand/MainActivity.java')
s=p.read_text()

# 3.0.40: keep Barcode focused for the hardware/Bluetooth scanner but do not
# let Samsung's letter keyboard reopen after Add Count. Manual taps on Barcode
# explicitly re-enable the soft keyboard.
old_helper='''    private void focusBarcodeForScanner() {
        if(barcode==null) return;
        if(Build.VERSION.SDK_INT>=Build.VERSION_CODES.LOLLIPOP) barcode.setShowSoftInputOnFocus(false);
        barcode.requestFocus();
        hideKeyboard(barcode);
        barcode.postDelayed(()->{
            hideKeyboard(barcode);
            if(Build.VERSION.SDK_INT>=Build.VERSION_CODES.LOLLIPOP) barcode.setShowSoftInputOnFocus(true);
        },350);
        barcode.postDelayed(()->hideKeyboard(barcode),650);
    }
'''
new_helper='''    private void focusBarcodeForScanner() {
        if(barcode==null) return;
        if(Build.VERSION.SDK_INT>=Build.VERSION_CODES.LOLLIPOP) barcode.setShowSoftInputOnFocus(false);
        barcode.requestFocus();
        hideKeyboard(barcode);
        barcode.postDelayed(()->hideKeyboard(barcode),250);
        barcode.postDelayed(()->hideKeyboard(barcode),600);
    }
'''
if old_helper not in s:
    raise SystemExit('3.0.39 scanner focus helper not found')
s=s.replace(old_helper,new_helper,1)

# Allow manual barcode typing when the user deliberately taps the Barcode field.
marker='''        barcode.setOnKeyListener((v,keyCode,event)->{
            if(keyCode==KeyEvent.KEYCODE_ENTER&&event.getAction()==KeyEvent.ACTION_DOWN){ handleScannedBarcode(barcode.getText().toString().trim()); return true; }
            return false;
        });'''
replacement=marker+'''
        barcode.setOnTouchListener((v,event)->{
            if(event.getAction()==android.view.MotionEvent.ACTION_DOWN && Build.VERSION.SDK_INT>=Build.VERSION_CODES.LOLLIPOP){
                barcode.setShowSoftInputOnFocus(true);
            }
            return false;
        });'''
if marker not in s:
    raise SystemExit('barcode key listener marker not found')
s=s.replace(marker,replacement,1)

# Make the visible file controls clearly describe the new tab-delimited TXT format.
s=s.replace('Button imp=button("Import CSV"); imp.setOnClickListener(v->importCsv()); Button exp=button("Export CSV"); exp.setOnClickListener(v->exportCsv());',
            'Button imp=button("Import TXT"); imp.setOnClickListener(v->importCsv()); Button exp=button("Export TXT"); exp.setOnClickListener(v->exportCsv());',1)

# Export true TAB-delimited text instead of comma-separated text with a .txt extension.
start=s.find('    private String buildExportCsv(){')
end=s.find('    private void writeExport(Uri uri)',start)
if start<0 or end<=start:
    raise SystemExit('buildExportCsv method not found')
new_export='''    private String tsvField(String value){
        if(value==null)return "";
        return value.replace('\\t',' ').replace('\\r',' ').replace('\\n',' ');
    }

    private String buildExportTsv(){
        ArrayList<String>active=new ArrayList<>();
        for(String c:exportColumns)if(Boolean.TRUE.equals(exportEnabled.get(c)))active.add(c);
        if(active.isEmpty())active.add("Barcode");
        StringBuilder out=new StringBuilder();
        for(int i=0;i<active.size();i++){
            if(i>0)out.append('\\t');
            out.append(tsvField(active.get(i)));
        }
        out.append("\\r\\n");
        for(InventoryDb.Row r:db.items(sessionId)){
            if(pendingExportLocation!=null&&!pendingExportLocation.equalsIgnoreCase(r.location==null?"":r.location))continue;
            if(pendingExportPositiveOnly&&r.quantity<=0)continue;
            if(pendingExportModifiedOnly&&!r.modified)continue;
            String[]parts=splitDescriptionPrice(r.description);
            String cleanDescription=parts[0],price=parts[1];
            boolean separate=active.contains("Price");
            for(int i=0;i<active.size();i++){
                if(i>0)out.append('\\t');
                String c=active.get(i),value="";
                if("Barcode".equals(c))value=r.barcode;
                else if("Description".equals(c))value=separate?cleanDescription:(r.description==null?"":r.description);
                else if("Price".equals(c))value=price;
                else if("Quantity".equals(c))value=String.valueOf(r.quantity);
                else if("Location".equals(c))value=r.location;
                out.append(tsvField(value));
            }
            out.append("\\r\\n");
        }
        return out.toString();
    }

'''
s=s[:start]+new_export+s[end:]

# Write the tab-delimited output.
s=s.replace('os.write(buildExportCsv().getBytes(StandardCharsets.UTF_8));toast("TXT exported")',
            'os.write(buildExportTsv().getBytes(StandardCharsets.UTF_8));toast("Tab-delimited TXT exported")',1)

# Import TAB-delimited TXT. Keep CSV fallback so existing older inventory files
# remain usable after upgrading.
read_marker='while((line=br.readLine())!=null)if(!line.trim().isEmpty())rows.add(CsvUtils.parseLine(line));'
if read_marker not in s:
    raise SystemExit('import parser marker not found')
s=s.replace(read_marker,'while((line=br.readLine())!=null)if(!line.trim().isEmpty())rows.add(parseImportLine(line));',1)
s=s.replace('toast("CSV is empty")','toast("Text file is empty")',1)

helper_anchor='    private String inventoryNameFromUri(Uri uri)'
if helper_anchor not in s:
    raise SystemExit('import helper anchor not found')
parse_helper='''    private List<String> parseImportLine(String line){
        if(line!=null && line.indexOf('\\t')>=0){
            ArrayList<String> fields=new ArrayList<>();
            String[] parts=line.split("\\\\t",-1);
            for(String part:parts)fields.add(part);
            return fields;
        }
        return CsvUtils.parseLine(line==null?"":line);
    }

'''
s=s.replace(helper_anchor,parse_helper+helper_anchor,1)

p.write_text(s)

b=Path('app/build.gradle')
g=b.read_text().replace('versionCode 30039','versionCode 30040').replace("versionName '3.0.39'","versionName '3.0.40'")
b.write_text(g)
