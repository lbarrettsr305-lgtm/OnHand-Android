from pathlib import Path
import runpy

# Preserve every approved 3.0.79 feature first: corrected Cases entry,
# continuous phone-camera scanning, Google fallback, scan list behavior,
# TXT/Excel exports, import safety, and all prior UI fixes.
runpy.run_path('.github/prepare_3079.py', run_name='__main__')

p=Path('app/src/main/java/com/iceinventory/onhand/BarcodeLookup.java')
s=p.read_text()

def rep(old,new,label):
    global s
    if old not in s:
        raise SystemExit('3.0.80 target missing: '+label)
    s=s.replace(old,new,1)

# Add regex helpers for the keyless general-web result parser.
rep('''import java.util.Locale;\n''',
'''import java.util.Locale;\nimport java.util.regex.Matcher;\nimport java.util.regex.Pattern;\n''','regex imports')

# After the structured barcode databases are exhausted, try a broader exact-barcode
# web-result lookup. This does not require an API key and does not replace the explicit
# Google fallback in MainActivity; it simply gives the app one more automatic chance
# to populate Description/Price before asking the operator to search manually.
old='''        if(!reachedOpenFacts&&lastError!=null)throw lastError;\n        return null;\n    }\n\n    private static Result lookupUpcItemDb(String barcode) throws Exception {\n'''
new='''        for(String code:candidates){\n            try{\n                Result r=lookupWebResults(code);\n                if(r!=null)return r;\n            }catch(Exception e){lastError=e;}\n        }\n\n        if(!reachedOpenFacts&&lastError!=null)throw lastError;\n        return null;\n    }\n\n    private static Result lookupWebResults(String barcode) throws Exception {\n        String encoded=URLEncoder.encode("\\\""+barcode+"\\\"",StandardCharsets.UTF_8.name());\n        URL url=new URL("https://lite.duckduckgo.com/lite/?q="+encoded);\n        HttpURLConnection conn=open(url);\n        conn.setRequestProperty("Accept","text/html,application/xhtml+xml");\n        int status=conn.getResponseCode();\n        if(status<200||status>=300){conn.disconnect();throw new Exception("Web product search failed ("+status+")");}\n        String html=readBody(conn);\n\n        Pattern links=Pattern.compile("(?is)<a[^>]*class=['\\\"]result-link['\\\"][^>]*>(.*?)</a>");\n        Matcher lm=links.matcher(html);\n        while(lm.find()){\n            String title=htmlText(lm.group(1));\n            if(!usefulWebTitle(title,barcode))continue;\n\n            // Product pages often include the current selling price in the nearby result\n            // snippet. Capture it when present; otherwise leave Price blank for review.\n            int from=Math.max(0,lm.end());\n            int to=Math.min(html.length(),from+1200);\n            String nearby=htmlText(html.substring(from,to));\n            String price=firstDollarPrice(nearby);\n            return new Result(cleanWebTitle(title),"",price);\n        }\n        return null;\n    }\n\n    private static String cleanWebTitle(String title){\n        String t=title==null?"":title.trim();\n        // Result titles frequently append a retailer/site after a vertical bar. Keep the\n        // product side as the inventory description when that leaves a meaningful title.\n        int pipe=t.indexOf(" | ");\n        if(pipe>7)t=t.substring(0,pipe).trim();\n        return t;\n    }\n\n    private static boolean usefulWebTitle(String title,String barcode){\n        if(title==null)return false;\n        String t=title.trim();\n        if(t.length()<8)return false;\n        String low=t.toLowerCase(Locale.US);\n        if(low.equals(barcode.toLowerCase(Locale.US)))return false;\n        if(low.contains("search results")||low.contains("barcode lookup")||\n                low.contains("upc lookup")||low.contains("upcitemdb")||\n                low.contains("duckduckgo"))return false;\n        int letters=0;\n        for(int i=0;i<t.length();i++)if(Character.isLetter(t.charAt(i)))letters++;\n        return letters>=4;\n    }\n\n    private static String firstDollarPrice(String text){\n        if(text==null||text.isEmpty())return "";\n        Matcher m=Pattern.compile("\\$\\s*([0-9]{1,4}(?:\\.[0-9]{2})?)").matcher(text);\n        return m.find()?m.group(1):"";\n    }\n\n    private static String htmlText(String html){\n        if(html==null)return "";\n        String s=html.replaceAll("(?is)<[^>]+>"," ");\n        s=s.replace("&amp;","&").replace("&quot;","\\\"")\n                .replace("&#39;","'").replace("&apos;","'")\n                .replace("&nbsp;"," ").replace("&ndash;","–")\n                .replace("&mdash;","—");\n        // Decode the numeric entities most commonly seen in product titles.\n        Matcher m=Pattern.compile("&#(x?[0-9A-Fa-f]+);").matcher(s);\n        StringBuffer out=new StringBuffer();\n        while(m.find()){\n            try{\n                String n=m.group(1);\n                int cp=n.startsWith("x")||n.startsWith("X")?Integer.parseInt(n.substring(1),16):Integer.parseInt(n,10);\n                m.appendReplacement(out,Matcher.quoteReplacement(new String(Character.toChars(cp))));\n            }catch(Exception ignored){m.appendReplacement(out,Matcher.quoteReplacement(m.group(0)));}\n        }\n        m.appendTail(out);\n        return out.toString().replaceAll("\\s+"," ").trim();\n    }\n\n    private static Result lookupUpcItemDb(String barcode) throws Exception {\n'''
rep(old,new,'general web lookup')
p.write_text(s)

# Advance visible/installable version while preserving all MainActivity behavior.
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

print('Prepared iCE Onhand 3.0.80: broader automatic web product lookup before Google fallback')
