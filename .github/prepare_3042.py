from pathlib import Path

main = Path('app/src/main/java/com/iceinventory/onhand/MainActivity.java')
s = main.read_text()

if 'import android.content.Context;' not in s:
    s = s.replace('import android.content.Intent;\n', 'import android.content.Intent;\nimport android.content.Context;\n', 1)
if 'import android.view.MotionEvent;' not in s:
    s = s.replace('import android.view.KeyEvent;\n', 'import android.view.KeyEvent;\nimport android.view.MotionEvent;\n', 1)
if 'import android.view.inputmethod.InputMethodManager;' not in s:
    s = s.replace('import android.view.ViewGroup;\n', 'import android.view.ViewGroup;\nimport android.view.inputmethod.InputMethodManager;\n', 1)

old_barcode = 'barcode=new EditText(this); barcode.setSingleLine(true); barcode.setTextSize(20); barcode.setHint("Scan or type barcode"); barcode.setInputType(InputType.TYPE_CLASS_TEXT);'
new_barcode = '''barcode=new EditText(this); barcode.setSingleLine(true); barcode.setTextSize(20); barcode.setHint("Scan or type barcode"); barcode.setInputType(InputType.TYPE_CLASS_TEXT);
        // Stay ready for a hardware scanner without automatically opening the full keyboard.
        // A direct tap still enables manual typing.
        barcode.setShowSoftInputOnFocus(false);
        barcode.setOnTouchListener((v,event)->{
            if(event.getAction()==MotionEvent.ACTION_DOWN){
                barcode.setShowSoftInputOnFocus(true);
                barcode.postDelayed(() -> {
                    InputMethodManager imm=(InputMethodManager)getSystemService(Context.INPUT_METHOD_SERVICE);
                    if(imm!=null) imm.showSoftInput(barcode,InputMethodManager.SHOW_IMPLICIT);
                },50);
            }
            return false;
        });
        barcode.setOnFocusChangeListener((v,hasFocus)->{
            if(!hasFocus) barcode.setShowSoftInputOnFocus(false);
        });'''
if old_barcode not in s:
    raise SystemExit('Barcode field marker not found')
s = s.replace(old_barcode, new_barcode, 1)

old_add = 'barcode.setText(""); description.setText(""); qty.setText(""); barcode.requestFocus(); refreshList();'
new_add = '''barcode.setText(""); description.setText(""); qty.setText("");
        barcode.setShowSoftInputOnFocus(false);
        barcode.requestFocus();
        hideKeyboardAfterAdd();
        refreshList();'''
if old_add not in s:
    raise SystemExit('Add Count focus marker not found')
s = s.replace(old_add, new_add, 1)

marker = '    private void scanBarcode() {'
helper = '''    private void hideKeyboardAfterAdd() {
        InputMethodManager imm=(InputMethodManager)getSystemService(Context.INPUT_METHOD_SERVICE);
        if(imm!=null) imm.hideSoftInputFromWindow(barcode.getWindowToken(),0);
        barcode.postDelayed(() -> {
            barcode.setShowSoftInputOnFocus(false);
            InputMethodManager again=(InputMethodManager)getSystemService(Context.INPUT_METHOD_SERVICE);
            if(again!=null) again.hideSoftInputFromWindow(barcode.getWindowToken(),0);
        },300);
    }

'''
if marker not in s:
    raise SystemExit('Scanner method marker not found')
s = s.replace(marker, helper + marker, 1)
main.write_text(s)

gradle = Path('app/build.gradle')
t = gradle.read_text()
t = t.replace('versionCode 30020', 'versionCode 30042')
t = t.replace("versionName '3.0.20'", "versionName '3.0.42'")
if 'versionCode 30042' not in t or "versionName '3.0.42'" not in t:
    raise SystemExit('Version update failed')
gradle.write_text(t)

icon = '''<?xml version="1.0" encoding="utf-8"?>
<vector xmlns:android="http://schemas.android.com/apk/res/android"
    android:width="108dp"
    android:height="108dp"
    android:viewportWidth="108"
    android:viewportHeight="108">
    <path android:fillColor="#050505" android:pathData="M0,0h108v108h-108z"/>
    <path android:fillColor="#FFD100" android:pathData="M54,8a46,46 0,1 0,0,92a46,46 0,1 0,0,-92z"/>
    <path android:fillColor="#050505" android:pathData="M54,17a37,37 0,1 0,0,74a37,37 0,1 0,0,-74z"/>
    <path android:fillColor="#009B3A" android:pathData="M20,57 L33,44 L47,58 L76,28 L89,41 L47,83 Z"/>
    <path android:fillColor="#FFD100" android:pathData="M28,29h4v16h-4z M35,26h5v19h-5z M43,30h4v15h-4z M51,25h6v20h-6z M61,29h4v16h-4z M69,26h5v19h-5z M77,30h4v15h-4z"/>
    <path android:fillColor="#FFFFFF" android:fillAlpha="0.16" android:pathData="M54,19a35,35 0,0 0,-27,13c12,-7 27,-9 40,-5c7,2 13,5 18,10c-6,-11 -17,-18 -31,-18z"/>
</vector>
'''
Path('app/src/main/res/drawable/ice_onhand_icon.xml').write_text(icon)
print('Prepared iCE Onhand Inventory 3.0.42')
