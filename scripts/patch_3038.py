from pathlib import Path

p=Path('app/src/main/java/com/iceinventory/onhand/MainActivity.java')
s=p.read_text()
changed=False

# Keep the activity resized when the Samsung numeric keyboard opens, and bring the
# highlighted inventory row into view whenever Quantity receives focus.
set_content='        setContentView(root);'
if 'private void scrollHighlightedIntoView()' not in s:
    build_start=s.find('    private void buildUi() {')
    build_end=s.find('\n    private ', build_start+10)
    if build_start>=0 and build_end>build_start:
        block=s[build_start:build_end]
        pos=block.rfind(set_content)
        if pos>=0:
            replacement='''        qty.setOnFocusChangeListener((v,hasFocus)->{
            if(hasFocus){
                qty.postDelayed(this::scrollHighlightedIntoView,180);
                qty.postDelayed(this::scrollHighlightedIntoView,420);
                qty.postDelayed(this::scrollHighlightedIntoView,700);
            }
        });
        getWindow().setSoftInputMode(android.view.WindowManager.LayoutParams.SOFT_INPUT_ADJUST_RESIZE);
        setContentView(root);'''
            block=block[:pos]+block[pos:].replace(set_content,replacement,1)
            s=s[:build_start]+block+s[build_end:]
            changed=True

helper_anchor='    private SharedPreferences prefs(){'
if helper_anchor in s and 'private void scrollHighlightedIntoView()' not in s:
    helper='''    private void scrollHighlightedIntoView() {
        if(list==null || highlightedRowId<0 || visibleRows.isEmpty()) return;
        for(int i=0;i<visibleRows.size();i++){
            if(visibleRows.get(i).id==highlightedRowId){
                final int position=i;
                list.post(() -> list.setSelectionFromTop(Math.max(0,position),0));
                return;
            }
        }
    }

'''
    s=s.replace(helper_anchor,helper+helper_anchor,1)
    changed=True

# 3.0.39: after Add Count, return to scanner-ready barcode focus without
# allowing Samsung's letter keyboard to stay open over the inventory list.
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
changed=True

if 'private void focusBarcodeForScanner()' not in s:
    scanner_helper='''    private void focusBarcodeForScanner() {
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
    if helper_anchor not in s:
        raise SystemExit('scanner helper insertion marker not found')
    s=s.replace(helper_anchor,scanner_helper+helper_anchor,1)
    changed=True

if not changed or 'private void scrollHighlightedIntoView()' not in s or 'private void focusBarcodeForScanner()' not in s:
    raise SystemExit('3.0.39 keyboard patch could not be applied')

p.write_text(s)

b=Path('app/build.gradle')
g=b.read_text().replace('versionCode 30037','versionCode 30039').replace("versionName '3.0.37'","versionName '3.0.39'")
b.write_text(g)
