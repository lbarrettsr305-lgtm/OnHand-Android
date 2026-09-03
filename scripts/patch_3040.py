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

p.write_text(s)

b=Path('app/build.gradle')
g=b.read_text().replace('versionCode 30039','versionCode 30040').replace("versionName '3.0.39'","versionName '3.0.40'")
b.write_text(g)
