from pathlib import Path
import runpy

# Preserve every approved 3.0.78 feature first, including the corrected Cases
# keypad/input behavior, scan list visibility, TXT/Excel exports, and import logic.
runpy.run_path('.github/prepare_3078.py', run_name='__main__')

p=Path('app/src/main/java/com/iceinventory/onhand/MainActivity.java')
s=p.read_text()

def rep(old,new,label):
    global s
    if old not in s:
        raise SystemExit('3.0.79 target missing: '+label)
    s=s.replace(old,new,1)

# Phone-camera scanning becomes a continuous cycle. Bluetooth/manual input remain
# independent because only the camera Scan button enables this flag.
rep('''    private String pendingQuantityBarcode="";\n''',
'''    private String pendingQuantityBarcode="";\n    private boolean continuousPhoneScan=false;\n    private boolean returnFromWebSearch=false;\n''','phone scan flags')

rep('''        Button scan=button("📷 Scan",1);scan.setOnClickListener(v->scanBarcode());\n''',
'''        Button scan=button("📷 Scan",1);scan.setOnClickListener(v->startPhoneScanCycle());\n''','camera scan button')

# Add the camera-cycle starter immediately before scanBarcode().
marker='''    private void scanBarcode() {\n'''
helper='''    private void startPhoneScanCycle(){\n        continuousPhoneScan=true;\n        hideKeyboard();\n        scanBarcode();\n    }\n\n'''
if marker not in s: raise SystemExit('3.0.79 target missing: scanBarcode marker')
s=s.replace(marker,helper+marker,1)

# Canceling/backing out of the camera stops continuous scanning. A scanner error
# also stops the cycle rather than repeatedly reopening.
rep('''                .addOnCanceledListener(()->{})\n                .addOnFailureListener(e->showError("Scanner error",e));\n''',
'''                .addOnCanceledListener(()->{continuousPhoneScan=false;focusBarcodeWithoutKeyboard();})\n                .addOnFailureListener(e->{continuousPhoneScan=false;showError("Scanner error",e);});\n''','camera cancel/failure')

# After a successful Add Count, reopen the phone camera only when the count came
# from an active phone-camera cycle. This intentionally does not affect hardware
# scanner/manual workflows.
start=s.find('''    private void addItem() {\n''')
end=s.find('''    private void refreshLocations() {\n''',start)
if start<0 or end<0: raise SystemExit('3.0.79 target missing: addItem method')
seg=s[start:end]
needle='''        focusBarcodeWithoutKeyboard();\n'''
pos=seg.rfind(needle)
if pos<0: raise SystemExit('3.0.79 target missing: final addItem focus')
replacement='''        if(continuousPhoneScan){\n            hideKeyboard();\n            barcode.postDelayed(this::scanBarcode,180);\n        } else {\n            focusBarcodeWithoutKeyboard();\n        }\n'''
seg=seg[:pos]+replacement+seg[pos+len(needle):]
s=s[:start]+seg+s[end:]

# Structured barcode databases can miss products that a general Google search
# can find. Offer a one-tap exact-barcode web fallback instead of forcing the
# operator to leave the app and retype the UPC manually.
old='''                    } else {\n                        toast("No internet item found");\n                        focusDescription();\n                    }\n'''
new='''                    } else {\n                        toast("No barcode-database match");\n                        offerWebSearch(lookupCode);\n                    }\n'''
if old not in s: raise SystemExit('3.0.79 target missing: no internet item branch')
s=s.replace(old,new,1)

old='''                    toast(e.getMessage()==null?"Internet lookup failed":e.getMessage());\n                    focusDescription();\n'''
new='''                    toast(e.getMessage()==null?"Internet lookup failed":e.getMessage());\n                    offerWebSearch(lookupCode);\n'''
if old not in s: raise SystemExit('3.0.79 target missing: lookup failure branch')
s=s.replace(old,new,1)

# Add the web-search fallback before scanFeedback(). Google is opened only after
# explicit operator approval. When the operator returns, Description is focused
# so the product name can be entered/pasted without re-scanning the barcode.
marker='''    private void scanFeedback() {\n'''
helper='''    private void offerWebSearch(String code){\n        final String c=code==null?"":code.trim();\n        if(c.isEmpty()){focusDescription();return;}\n        new AlertDialog.Builder(this)\n                .setTitle("Barcode not found")\n                .setMessage("The barcode databases did not find "+c+". Search Google for this exact barcode?")\n                .setPositiveButton("Search Google",(d,w)->{\n                    try{\n                        returnFromWebSearch=true;\n                        Intent web=new Intent(Intent.ACTION_VIEW,Uri.parse("https://www.google.com/search?q="+Uri.encode(c)));\n                        startActivity(web);\n                    }catch(Exception e){\n                        returnFromWebSearch=false;\n                        showError("Web search failed",e);\n                        focusDescription();\n                    }\n                })\n                .setNegativeButton("Enter Manually",(d,w)->focusDescription())\n                .setNeutralButton("Count Only",(d,w)->focusQuantity())\n                .show();\n    }\n\n'''
if marker not in s: raise SystemExit('3.0.79 target missing: scanFeedback marker')
s=s.replace(marker,helper+marker,1)

# Returning from the Google result keeps the unknown barcode loaded and moves
# directly to Description. This flag is only set by the web fallback above.
marker='''    private void initializeApp() {\n'''
resume='''    @Override protected void onResume(){\n        super.onResume();\n        if(returnFromWebSearch){\n            returnFromWebSearch=false;\n            if(description!=null)description.postDelayed(this::focusDescription,140);\n        }\n    }\n\n'''
if marker not in s: raise SystemExit('3.0.79 target missing: initializeApp marker')
s=s.replace(marker,resume+marker,1)

# Advance visible/installable version.
if 'TextView app=text("Onhand Inventory 3.0.78",19,Color.WHITE,true);' not in s:
    raise SystemExit('3.0.79 target missing: visible version')
s=s.replace('TextView app=text("Onhand Inventory 3.0.78",19,Color.WHITE,true);',
            'TextView app=text("Onhand Inventory 3.0.79",19,Color.WHITE,true);',1)
p.write_text(s)

p=Path('app/build.gradle')
s=p.read_text().replace('versionCode 30078','versionCode 30079',1).replace("versionName '3.0.78'","versionName '3.0.79'",1)
if 'versionCode 30079' not in s or "versionName '3.0.79'" not in s:
    raise SystemExit('3.0.79 target missing: Gradle version')
p.write_text(s)

p=Path('app/src/main/AndroidManifest.xml')
s=p.read_text().replace('android:label="iCE Onhand 3.0.78"','android:label="iCE Onhand 3.0.79"',1)
if 'android:label="iCE Onhand 3.0.79"' not in s:
    raise SystemExit('3.0.79 target missing: manifest version')
p.write_text(s)

print('Prepared iCE Onhand 3.0.79: continuous phone scan after count + Google barcode fallback')
