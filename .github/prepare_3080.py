from pathlib import Path
import runpy

# Preserve every approved 3.0.79 feature first.
runpy.run_path('.github/prepare_3079.py', run_name='__main__')

# -----------------------------------------------------------------------------
# Automatic product-description fallback for unknown barcodes.
# -----------------------------------------------------------------------------
p=Path('app/src/main/java/com/iceinventory/onhand/BarcodeLookup.java')
s=p.read_text()

def rep(old,new,label):
    global s
    if old not in s:
        raise SystemExit('3.0.80 target missing: '+label)
    s=s.replace(old,new,1)

rep('''import java.util.Locale;\n''',
'''import java.util.Locale;\nimport java.util.regex.Matcher;\nimport java.util.regex.Pattern;\n''','regex imports')

old='''        if(!reachedOpenFacts&&lastError!=null)throw lastError;\n        return null;\n    }\n\n    private static Result lookupUpcItemDb(String barcode) throws Exception {\n'''
new='''        for(String code:candidates){\n            try{\n                Result r=lookupWebResults(code);\n                if(r!=null)return r;\n            }catch(Exception e){lastError=e;}\n        }\n\n        if(!reachedOpenFacts&&lastError!=null)throw lastError;\n        return null;\n    }\n\n    private static Result lookupWebResults(String barcode) throws Exception {\n        Exception last=null;\n        try{\n            Result r=lookupDuckDuckGoResults(barcode);\n            if(r!=null)return r;\n        }catch(Exception e){last=e;}\n        try{\n            Result r=lookupGoogleResults(barcode);\n            if(r!=null)return r;\n        }catch(Exception e){last=e;}\n        if(last!=null)throw last;\n        return null;\n    }\n\n    private static Result lookupDuckDuckGoResults(String barcode) throws Exception {\n        String encoded=URLEncoder.encode("\\\""+barcode+"\\\"",StandardCharsets.UTF_8.name());\n        URL url=new URL("https://lite.duckduckgo.com/lite/?q="+encoded);\n        HttpURLConnection conn=open(url);\n        conn.setRequestProperty("Accept","text/html,application/xhtml+xml");\n        int status=conn.getResponseCode();\n        if(status<200||status>=300){conn.disconnect();throw new Exception("Web product search failed ("+status+")");}\n        String html=readBody(conn);\n        Pattern links=Pattern.compile("(?is)<a[^>]*class=['\\\"]result-link['\\\"][^>]*>(.*?)</a>");\n        Matcher lm=links.matcher(html);\n        while(lm.find()){\n            String title=htmlText(lm.group(1));\n            if(!usefulWebTitle(title,barcode))continue;\n            int from=Math.max(0,lm.end());\n            int to=Math.min(html.length(),from+1200);\n            String nearby=htmlText(html.substring(from,to));\n            return new Result(cleanWebTitle(title),"",firstDollarPrice(nearby));\n        }\n        return null;\n    }\n\n    private static Result lookupGoogleResults(String barcode) throws Exception {\n        String encoded=URLEncoder.encode("\\\""+barcode+"\\\"",StandardCharsets.UTF_8.name());\n        URL url=new URL("https://www.google.com/search?q="+encoded+"&hl=en&num=8");\n        HttpURLConnection conn=(HttpURLConnection)url.openConnection();\n        conn.setRequestMethod("GET");\n        conn.setConnectTimeout(7000);\n        conn.setReadTimeout(7000);\n        conn.setInstanceFollowRedirects(true);\n        conn.setRequestProperty("Accept","text/html,application/xhtml+xml");\n        conn.setRequestProperty("Accept-Language","en-US,en;q=0.9");\n        conn.setRequestProperty("User-Agent","Mozilla/5.0 (Linux; Android 16) AppleWebKit/537.36 Chrome/140 Mobile Safari/537.36");\n        int status=conn.getResponseCode();\n        if(status<200||status>=300){conn.disconnect();throw new Exception("Google product search failed ("+status+")");}\n        String html=readBody(conn);\n        Matcher hm=Pattern.compile("(?is)<h3[^>]*>(.*?)</h3>").matcher(html);\n        while(hm.find()){\n            String title=htmlText(hm.group(1));\n            if(!usefulWebTitle(title,barcode))continue;\n            int from=Math.max(0,hm.end());\n            int to=Math.min(html.length(),from+1600);\n            String nearby=htmlText(html.substring(from,to));\n            return new Result(cleanWebTitle(title),"",firstDollarPrice(nearby));\n        }\n        return null;\n    }\n\n    private static String cleanWebTitle(String title){\n        String t=title==null?"":title.trim();\n        int pipe=t.indexOf(" | ");\n        if(pipe>7)t=t.substring(0,pipe).trim();\n        return t;\n    }\n\n    private static boolean usefulWebTitle(String title,String barcode){\n        if(title==null)return false;\n        String t=title.trim();\n        if(t.length()<8)return false;\n        String low=t.toLowerCase(Locale.US);\n        if(low.equals(barcode.toLowerCase(Locale.US)))return false;\n        if(low.contains("search results")||low.contains("barcode lookup")||\n                low.contains("upc lookup")||low.contains("upcitemdb")||\n                low.contains("duckduckgo")||low.contains("google search"))return false;\n        int letters=0;\n        for(int i=0;i<t.length();i++)if(Character.isLetter(t.charAt(i)))letters++;\n        return letters>=4;\n    }\n\n    private static String firstDollarPrice(String text){\n        if(text==null||text.isEmpty())return "";\n        Matcher m=Pattern.compile("\\\\$\\\\s*([0-9]{1,4}(?:\\\\.[0-9]{2})?)").matcher(text);\n        return m.find()?m.group(1):"";\n    }\n\n    private static String htmlText(String html){\n        if(html==null)return "";\n        String s=html.replaceAll("(?is)<[^>]+>"," ");\n        s=s.replace("&amp;","&").replace("&quot;","\\\"")\n                .replace("&#39;","'").replace("&apos;","'")\n                .replace("&nbsp;"," ").replace("&ndash;","–")\n                .replace("&mdash;","—");\n        Matcher m=Pattern.compile("&#(x?[0-9A-Fa-f]+);").matcher(s);\n        StringBuffer out=new StringBuffer();\n        while(m.find()){\n            try{\n                String n=m.group(1);\n                int cp=n.startsWith("x")||n.startsWith("X")?Integer.parseInt(n.substring(1),16):Integer.parseInt(n,10);\n                m.appendReplacement(out,Matcher.quoteReplacement(new String(Character.toChars(cp))));\n            }catch(Exception ignored){m.appendReplacement(out,Matcher.quoteReplacement(m.group(0)));}\n        }\n        m.appendTail(out);\n        return out.toString().replaceAll("\\s+"," ").trim();\n    }\n\n    private static Result lookupUpcItemDb(String barcode) throws Exception {\n'''
rep(old,new,'automatic web description lookup')
p.write_text(s)

# -----------------------------------------------------------------------------
# Protect ONLY import/export column setup. Import and Export themselves stay open.
# The format screen opens normally and CONTINUE still works with the saved setup,
# but checked columns, order, Move Up/Down, and Reset cannot change until unlocked.
# -----------------------------------------------------------------------------
p=Path('app/src/main/java/com/iceinventory/onhand/FormatConfigActivity.java')
s=p.read_text()

def frep(old,new,label):
    global s
    if old not in s:
        raise SystemExit('3.0.80 format target missing: '+label)
    s=s.replace(old,new,1)

frep('''import android.app.Activity;\n''','''import android.app.Activity;\nimport android.app.AlertDialog;\n''','AlertDialog import')
frep('''import android.graphics.Typeface;\n''','''import android.graphics.Typeface;\nimport android.text.InputType;\n''','InputType import')
frep('''import android.widget.CheckBox;\n''','''import android.widget.CheckBox;\nimport android.widget.EditText;\n''','EditText import')
frep('''import android.widget.TextView;\n''','''import android.widget.TextView;\nimport android.widget.Toast;\n''','Toast import')

frep('''    private static final String KEY_EXPORT_POSITIVE_ONLY="export_quantity_above_zero_only";\n''',
'''    private static final String KEY_EXPORT_POSITIVE_ONLY="export_quantity_above_zero_only";\n    private static final String KEY_COLUMN_PIN="column_setup_pin";\n''','column PIN key')

frep('''    private Button moveDown;\n    private CheckBox positiveOnly;\n''',
'''    private Button moveDown;\n    private Button unlockColumns;\n    private Button defaults;\n    private TextView lockStatus;\n    private CheckBox positiveOnly;\n    private boolean columnSetupUnlocked=false;\n''','lock fields')

frep('''        TextView help=text(helpText,14,Color.WHITE,false);help.setPadding(0,dp(5),0,dp(10));body.addView(help);\n\n        rows=new LinearLayout(this);rows.setOrientation(LinearLayout.VERTICAL);body.addView(rows);\n''',
'''        TextView help=text(helpText,14,Color.WHITE,false);help.setPadding(0,dp(5),0,dp(10));body.addView(help);\n\n        lockStatus=text("Column setup is LOCKED. You can continue using the saved setup.",14,gold(),true);\n        lockStatus.setPadding(dp(8),dp(8),dp(8),dp(6));\n        body.addView(lockStatus,new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT,ViewGroup.LayoutParams.WRAP_CONTENT));\n        unlockColumns=button("Unlock Column Setup");\n        unlockColumns.setTypeface(Typeface.DEFAULT,Typeface.BOLD);\n        unlockColumns.setOnClickListener(v->unlockColumnSetup());\n        body.addView(unlockColumns,new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT,dp(50)));\n\n        rows=new LinearLayout(this);rows.setOrientation(LinearLayout.VERTICAL);body.addView(rows);\n''','locked column banner')

frep('''        Button defaults=button("Reset standard order");defaults.setOnClickListener(v->resetDefaults());\n''',
'''        defaults=button("Reset standard order");defaults.setOnClickListener(v->resetDefaults());defaults.setEnabled(false);\n''','protected reset button')

frep('''            use.setEnabled(!"barcode".equals(field));\n''',
'''            use.setEnabled(columnSetupUnlocked&&!"barcode".equals(field));\n''','protect column checkbox')

frep('''            View.OnClickListener select=v->{selectedIndex=index;renderRows();};\n''',
'''            View.OnClickListener select=v->{\n                if(!columnSetupUnlocked){toast("Column setup is locked");return;}\n                selectedIndex=index;renderRows();\n            };\n''','protect row selection')

frep('''        moveUp.setEnabled(selectedIndex>0);\n        moveDown.setEnabled(selectedIndex>=0&&selectedIndex<order.size()-1);\n''',
'''        moveUp.setEnabled(columnSetupUnlocked&&selectedIndex>0);\n        moveDown.setEnabled(columnSetupUnlocked&&selectedIndex>=0&&selectedIndex<order.size()-1);\n''','protect move buttons')

frep('''    private void moveSelected(int direction){\n        int to=selectedIndex+direction;\n''',
'''    private void moveSelected(int direction){\n        if(!columnSetupUnlocked){toast("Column setup is locked");return;}\n        int to=selectedIndex+direction;\n''','protect move method')

frep('''    private void resetDefaults(){\n        order.clear();enabled.clear();\n''',
'''    private void resetDefaults(){\n        if(!columnSetupUnlocked){toast("Column setup is locked");return;}\n        order.clear();enabled.clear();\n''','protect reset method')

marker='''    private void saveAndFinish(){\n'''
helpers='''    private void toast(String message){\n        Toast.makeText(this,message,Toast.LENGTH_SHORT).show();\n    }\n\n    private boolean validColumnPin(String pin){\n        if(pin==null||pin.length()!=4)return false;\n        for(int i=0;i<pin.length();i++)if(!Character.isDigit(pin.charAt(i)))return false;\n        return true;\n    }\n\n    private EditText pinEntry(String hint){\n        EditText input=new EditText(this);\n        input.setSingleLine(true);\n        input.setHint(hint);\n        input.setInputType(InputType.TYPE_CLASS_NUMBER|InputType.TYPE_NUMBER_VARIATION_PASSWORD);\n        input.setFilters(new android.text.InputFilter[]{new android.text.InputFilter.LengthFilter(4)});\n        return input;\n    }\n\n    private void unlockColumnSetup(){\n        String saved=prefs().getString(KEY_COLUMN_PIN,"");\n        if(!validColumnPin(saved)){createColumnPin();return;}\n        EditText input=pinEntry("4-digit column PIN");\n        AlertDialog dialog=new AlertDialog.Builder(this)\n                .setTitle("Unlock Column Setup")\n                .setMessage("Enter the 4-digit PIN to change checked columns or their order.")\n                .setView(input)\n                .setPositiveButton("Unlock",null)\n                .setNegativeButton("Cancel",null)\n                .create();\n        dialog.setOnShowListener(x->dialog.getButton(AlertDialog.BUTTON_POSITIVE).setOnClickListener(v->{\n            if(!saved.equals(input.getText().toString())){toast("Incorrect column PIN");input.selectAll();return;}\n            dialog.dismiss();\n            setColumnSetupUnlocked();\n        }));\n        dialog.show();\n    }\n\n    private void createColumnPin(){\n        EditText first=pinEntry("New 4-digit column PIN");\n        AlertDialog dialog=new AlertDialog.Builder(this)\n                .setTitle("Create Column Setup PIN")\n                .setMessage("This PIN protects the import/export checked columns and column order. Import and Export themselves will not require the PIN.")\n                .setView(first)\n                .setPositiveButton("Next",null)\n                .setNegativeButton("Cancel",null)\n                .create();\n        dialog.setOnShowListener(x->dialog.getButton(AlertDialog.BUTTON_POSITIVE).setOnClickListener(v->{\n            String pin=first.getText().toString();\n            if(!validColumnPin(pin)){toast("PIN must be exactly 4 digits");first.selectAll();return;}\n            dialog.dismiss();\n            confirmColumnPin(pin);\n        }));\n        dialog.show();\n    }\n\n    private void confirmColumnPin(String pin){\n        EditText second=pinEntry("Confirm 4-digit PIN");\n        AlertDialog dialog=new AlertDialog.Builder(this)\n                .setTitle("Confirm Column Setup PIN")\n                .setView(second)\n                .setPositiveButton("Save",null)\n                .setNegativeButton("Cancel",null)\n                .create();\n        dialog.setOnShowListener(x->dialog.getButton(AlertDialog.BUTTON_POSITIVE).setOnClickListener(v->{\n            if(!pin.equals(second.getText().toString())){toast("PINs do not match");second.selectAll();return;}\n            prefs().edit().putString(KEY_COLUMN_PIN,pin).apply();\n            dialog.dismiss();\n            toast("Column setup PIN saved");\n            setColumnSetupUnlocked();\n        }));\n        dialog.show();\n    }\n\n    private void setColumnSetupUnlocked(){\n        columnSetupUnlocked=true;\n        if(lockStatus!=null)lockStatus.setText("Column setup UNLOCKED. Changes can now be made.");\n        if(unlockColumns!=null){unlockColumns.setText("Column Setup Unlocked");unlockColumns.setEnabled(false);}\n        if(defaults!=null)defaults.setEnabled(true);\n        renderRows();\n    }\n\n'''
if marker not in s:
    raise SystemExit('3.0.80 format target missing: save marker')
s=s.replace(marker,helpers+marker,1)
p.write_text(s)

# -----------------------------------------------------------------------------
# Version bump only. Do NOT password-protect normal Import / Export actions.
# -----------------------------------------------------------------------------
p=Path('app/src/main/java/com/iceinventory/onhand/MainActivity.java')
s=p.read_text()
if 'TextView app=text("Onhand Inventory 3.0.79",19,Color.WHITE,true);' not in s:
    raise SystemExit('3.0.80 target missing: visible version')
s=s.replace('TextView app=text("Onhand Inventory 3.0.79",19,Color.WHITE,true);',
            'TextView app=text("Onhand Inventory 3.0.80",19,Color.WHITE,true);',1)
p.write_text(s)

p=Path('app/build.gradle')
s=p.read_text().replace('versionCode 30079','versionCode 30080',1).replace("versionName '3.0.79'","versionName '3.0.80'",1)
if 'versionCode 30080' not in s or "versionName '3.0.80'" not in s:
    raise SystemExit('3.0.80 target missing: Gradle version')
p.write_text(s)

p=Path('app/src/main/AndroidManifest.xml')
s=p.read_text().replace('android:label="iCE Onhand 3.0.79"','android:label="iCE Onhand 3.0.80"',1)
if 'android:label="iCE Onhand 3.0.80"' not in s:
    raise SystemExit('3.0.80 target missing: manifest version')
p.write_text(s)

print('Prepared iCE Onhand 3.0.80: locked column setup only + automatic Internet description fallback')
