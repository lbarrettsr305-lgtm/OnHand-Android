from pathlib import Path

p=Path('app/src/main/java/com/iceinventory/onhand/MainActivity.java')
s=p.read_text()

# After Add Count, return to scanner-ready barcode focus without leaving the
# Samsung software keyboard open over the inventory list.
start=s.find('    private void addItem() {')
end=s.find('\n    private ', start+10) if start>=0 else -1
if start<0 or end<=start:
    raise SystemExit('addItem method not found')
block=s[start:end]
old='barcode.setText("");description.setText("");qty.setText("");barcode.requestFocus();refreshList();'
new='barcode.setText("");description.setText("");qty.setText("");focusBarcodeForScanner();refreshList();'
if old not in block:
    raise SystemExit('Add Count focus marker not found')
block=block.replace(old,new,1)
s=s[:start]+block+s[end:]

anchor='    private SharedPreferences prefs(){'
if 'private void focusBarcodeForScanner()' not in s:
    helper='''    private void focusBarcodeForScanner() {
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

    private void hideKeyboard(View target) {
        if(target==null) return;
        Object service=getSystemService(INPUT_METHOD_SERVICE);
        if(service instanceof android.view.inputmethod.InputMethodManager){
            ((android.view.inputmethod.InputMethodManager)service).hideSoftInputFromWindow(target.getWindowToken(),0);
        }
    }

'''
    if anchor not in s:
        raise SystemExit('helper insertion marker not found')
    s=s.replace(anchor,helper+anchor,1)

p.write_text(s)

b=Path('app/build.gradle')
g=b.read_text().replace('versionCode 30038','versionCode 30039').replace("versionName '3.0.38'","versionName '3.0.39'")
if g==b.read_text():
    raise SystemExit('3.0.39 version marker not found')
b.write_text(g)
