from pathlib import Path
import runpy

# Preserve every approved 3.0.79 feature first: corrected Cases entry,
# continuous phone-camera scanning, Google fallback, scan list behavior,
# TXT/Excel exports, import safety, and all prior UI fixes.
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

# After the structured barcode databases are exhausted, try broader exact-barcode
# web results. This gives the app a keyless automatic chance to populate Description
# before the existing browser-based Google fallback is shown.
old='''        if(!reachedOpenFacts&&lastError!=null)throw lastError;\n        return null;\n    }\n\n    private static Result lookupUpcItemDb(String barcode) throws Exception {\n'''
new='''        for(String code:candidates){\n            try{\n                Result r=lookupWebResults(code);\n                if(r!=null)return r;\n            }catch(Exception e){lastError=e;}\n        }\n\n        if(!reachedOpenFacts&&lastError!=null)throw lastError;\n        return null;\n    }\n\n    private static Result lookupWebResults(String barcode) throws Exception {\n        Exception last=null;\n        try{\n            Result r=lookupDuckDuckGoResults(barcode);\n            if(r!=null)return r;\n        }catch(Exception e){last=e;}\n\n        // Google found the user's test barcode 051497398323 when the structured\n        // product databases did not. Try a lightweight exact-barcode Google result\n        // page automatically before falling back to opening the browser.\n        try{\n            Result r=lookupGoogleResults(barcode);\n            if(r!=null)return r;\n        }catch(Exception e){last=e;}\n\n        if(last!=null)throw last;\n        return null;\n    }\n\n    private static Result lookupDuckDuckGoResults(String barcode) throws Exception {\n        String encoded=URLEncoder.encode("\\\""+barcode+"\\\"",StandardCharsets.UTF_8.name());\n        URL url=new URL("https://lite.duckduckgo.com/lite/?q="+encoded);\n        HttpURLConnection conn=open(url);\n        conn.setRequestProperty("Accept","text/html,application/xhtml+xml");\n        int status=conn.getResponseCode();\n        if(status<200||status>=300){conn.disconnect();throw new Exception("Web product search failed ("+status+")");}\n        String html=readBody(conn);\n\n        Pattern links=Pattern.compile("(?is)<a[^>]*class=['\\\"]result-link['\\\"][^>]*>(.*?)</a>");\n        Matcher lm=links.matcher(html);\n        while(lm.find()){\n            String title=htmlText(lm.group(1));\n            if(!usefulWebTitle(title,barcode))continue;\n            int from=Math.max(0,lm.end());\n            int to=Math.min(html.length(),from+1200);\n            String nearby=htmlText(html.substring(from,to));\n            return new Result(cleanWebTitle(title),"",firstDollarPrice(nearby));\n        }\n        return null;\n    }\n\n    private static Result lookupGoogleResults(String barcode) throws Exception {\n        String encoded=URLEncoder.encode("\\\""+barcode+"\\\"",StandardCharsets.UTF_8.name());\n        URL url=new URL("https://www.google.com/search?q="+encoded+"&hl=en&num=8");\n        HttpURLConnection conn=(HttpURLConnection)url.openConnection();\n        conn.setRequestMethod("GET");\n        conn.setConnectTimeout(7000);\n        conn.setReadTimeout(7000);\n        conn.setInstanceFollowRedirects(true);\n        conn.setRequestProperty("Accept","text/html,application/xhtml+xml");\n        conn.setRequestProperty("Accept-Language","en-US,en;q=0.9");\n        conn.setRequestProperty("User-Agent","Mozilla/5.0 (Linux; Android 16) AppleWebKit/537.36 Chrome/140 Mobile Safari/537.36");\n        int status=conn.getResponseCode();\n        if(status<200||status>=300){conn.disconnect();throw new Exception("Google product search failed ("+status+")");}\n        String html=readBody(conn);\n\n        Matcher hm=Pattern.compile("(?is)<h3[^>]*>(.*?)</h3>").matcher(html);\n        while(hm.find()){\n            String title=htmlText(hm.group(1));\n            if(!usefulWebTitle(title,barcode))continue;\n            int from=Math.max(0,hm.end());\n            int to=Math.min(html.length(),from+1600);\n            String nearby=htmlText(html.substring(from,to));\n            return new Result(cleanWebTitle(title),"",firstDollarPrice(nearby));\n        }\n        return null;\n    }\n\n    private static String cleanWebTitle(String title){\n        String t=title==null?"":title.trim();\n        int pipe=t.indexOf(" | ");\n        if(pipe>7)t=t.substring(0,pipe).trim();\n        return t;\n    }\n\n    private static boolean usefulWebTitle(String title,String barcode){\n        if(title==null)return false;\n        String t=title.trim();\n        if(t.length()<8)return false;\n        String low=t.toLowerCase(Locale.US);\n        if(low.equals(barcode.toLowerCase(Locale.US)))return false;\n        if(low.contains("search results")||low.contains("barcode lookup")||\n                low.contains("upc lookup")||low.contains("upcitemdb")||\n                low.contains("duckduckgo")||low.contains("google search"))return false;\n        int letters=0;\n        for(int i=0;i<t.length();i++)if(Character.isLetter(t.charAt(i)))letters++;\n        return letters>=4;\n    }\n\n    private static String firstDollarPrice(String text){\n        if(text==null||text.isEmpty())return "";\n        Matcher m=Pattern.compile("\\$\\s*([0-9]{1,4}(?:\\.[0-9]{2})?)").matcher(text);\n        return m.find()?m.group(1):"";\n    }\n\n    private static String htmlText(String html){\n        if(html==null)return "";\n        String s=html.replaceAll("(?is)<[^>]+>"," ");\n        s=s.replace("&amp;","&").replace("&quot;","\\\"")\n                .replace("&#39;","'").replace("&apos;","'")\n                .replace("&nbsp;"," ").replace("&ndash;","–")\n                .replace("&mdash;","—");\n        Matcher m=Pattern.compile("&#(x?[0-9A-Fa-f]+);").matcher(s);\n        StringBuffer out=new StringBuffer();\n        while(m.find()){\n            try{\n                String n=m.group(1);\n                int cp=n.startsWith("x")||n.startsWith("X")?Integer.parseInt(n.substring(1),16):Integer.parseInt(n,10);\n                m.appendReplacement(out,Matcher.quoteReplacement(new String(Character.toChars(cp))));\n            }catch(Exception ignored){m.appendReplacement(out,Matcher.quoteReplacement(m.group(0)));}\n        }\n        m.appendTail(out);\n        return out.toString().replaceAll("\\s+"," ").trim();\n    }\n\n    private static Result lookupUpcItemDb(String barcode) throws Exception {\n'''
rep(old,new,'general web lookup')
p.write_text(s)

# -----------------------------------------------------------------------------
# Protect Options + Import + Export + format settings with a supervisor PIN.
# -----------------------------------------------------------------------------
p=Path('app/src/main/java/com/iceinventory/onhand/MainActivity.java')
s=p.read_text()

rep('''    private static final String KEY_COMPACT="compact_list";\n''',
'''    private static final String KEY_COMPACT="compact_list";\n    private static final String KEY_ADMIN_PIN="supervisor_pin";\n''','supervisor PIN preference')

# Protect the Options entry point. Existing option controls remain unchanged once unlocked.
rep('''    private void showOptions() {\n''',
'''    private void showOptions() {\n        requireSupervisorPin("Options / Settings",this::showOptionsUnlocked);\n    }\n\n    private void showOptionsUnlocked() {\n''','protect Options')

# Protect the two import/export format-entry flows. This means the format screen itself
# cannot be reached accidentally, and the eventual file import/export belongs to the same
# authenticated flow.
rep('''    private void startImportFormatFlow() {\n''',
'''    private void startImportFormatFlow() {\n        requireSupervisorPin("Import / Import Settings",this::startImportFormatFlowUnlocked);\n    }\n\n    private void startImportFormatFlowUnlocked() {\n''','protect import flow')
rep('''    private void startExportFormatFlow() {\n''',
'''    private void startExportFormatFlow() {\n        requireSupervisorPin("Export / Export Settings",this::startExportFormatFlowUnlocked);\n    }\n\n    private void startExportFormatFlowUnlocked() {\n''','protect export flow')

# Add PIN helpers immediately before the protected Options method.
marker='''    private void showOptions() {\n'''
helpers='''    private void requireSupervisorPin(String area,Runnable action) {\n        String stored=prefs().getString(KEY_ADMIN_PIN,"");\n        if(stored==null||stored.isEmpty()){\n            createSupervisorPin(area,action);\n            return;\n        }\n\n        EditText input=new EditText(this);\n        input.setSingleLine(true);\n        input.setHint("4-digit PIN");\n        input.setInputType(InputType.TYPE_CLASS_NUMBER|InputType.TYPE_NUMBER_VARIATION_PASSWORD);\n        input.setFilters(new android.text.InputFilter[]{new android.text.InputFilter.LengthFilter(4)});\n\n        AlertDialog dialog=new AlertDialog.Builder(this)\n                .setTitle("Protected: "+area)\n                .setMessage("Enter the supervisor PIN to continue.")\n                .setView(input)\n                .setPositiveButton("Unlock",null)\n                .setNegativeButton("Cancel",null)\n                .create();\n        dialog.setOnShowListener(x->{\n            dialog.getButton(AlertDialog.BUTTON_POSITIVE).setOnClickListener(v->{\n                String entered=input.getText().toString().trim();\n                if(stored.equals(entered)){\n                    dialog.dismiss();\n                    if(action!=null)action.run();\n                }else{\n                    input.setText("");\n                    toast("Incorrect supervisor PIN");\n                    input.requestFocus();\n                    showKeyboard(input);\n                }\n            });\n            input.requestFocus();\n            input.postDelayed(()->showKeyboard(input),100);\n        });\n        dialog.show();\n    }\n\n    private void createSupervisorPin(String area,Runnable action) {\n        EditText input=new EditText(this);\n        input.setSingleLine(true);\n        input.setHint("Create 4-digit PIN");\n        input.setInputType(InputType.TYPE_CLASS_NUMBER|InputType.TYPE_NUMBER_VARIATION_PASSWORD);\n        input.setFilters(new android.text.InputFilter[]{new android.text.InputFilter.LengthFilter(4)});\n\n        AlertDialog dialog=new AlertDialog.Builder(this)\n                .setTitle("Create Supervisor PIN")\n                .setMessage("This PIN will protect Options, Import, Export, and import/export settings. Keep it in a safe place.")\n                .setView(input)\n                .setPositiveButton("Save PIN",null)\n                .setNegativeButton("Cancel",null)\n                .create();\n        dialog.setOnShowListener(x->{\n            dialog.getButton(AlertDialog.BUTTON_POSITIVE).setOnClickListener(v->{\n                String pin=input.getText().toString().trim();\n                if(!pin.matches("[0-9]{4}")){\n                    toast("PIN must be exactly 4 digits");\n                    return;\n                }\n                prefs().edit().putString(KEY_ADMIN_PIN,pin).apply();\n                dialog.dismiss();\n                toast("Supervisor PIN saved");\n                if(action!=null)action.run();\n            });\n            input.requestFocus();\n            input.postDelayed(()->showKeyboard(input),100);\n        });\n        dialog.show();\n    }\n\n    private void changeSupervisorPin() {\n        // This button is inside Options, so the current PIN has already been verified.\n        createSupervisorPin("Change Supervisor PIN",null);\n    }\n\n'''
if marker not in s:
    raise SystemExit('3.0.80 target missing: protected Options marker')
s=s.replace(marker,helpers+marker,1)

# Make PIN management visible only after Options has already been unlocked.
needle='''        box.addView(unknown,new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT,dp(50)));\n'''
if needle not in s:
    raise SystemExit('3.0.80 target missing: Options unknown barcode control')
s=s.replace(needle,needle+'''        Button pinButton=button("Change Supervisor PIN",0);\n        pinButton.setOnClickListener(v->changeSupervisorPin());\n        box.addView(pinButton,new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT,dp(50)));\n''',1)

# Advance visible/installable version while preserving all 3.0.79 behavior.
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

print('Prepared iCE Onhand 3.0.80: protected supervisor settings/import/export + automatic web descriptions')
