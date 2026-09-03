from pathlib import Path
import runpy

# Preserve every approved 3.0.55 behavior first.
runpy.run_path('.github/prepare_3055.py', run_name='__main__')

p=Path('app/src/main/java/com/iceinventory/onhand/MainActivity.java')
s=p.read_text()

# Samsung can deliver the Bluetooth scanner through the active EditText's IME connection.
# Track a rapid barcode burst regardless of whether Barcode, Description, or Quantity has focus.
old='''    private int barcodeTextGeneration=0;\n'''
new='''    private int barcodeTextGeneration=0;\n    private boolean scannerRedirectInternal=false;\n    private final StringBuilder scannerImeBuffer=new StringBuilder();\n    private EditText scannerImeSource=null;\n    private String scannerImeOriginalText=\"\";\n    private long scannerImeLastMs=0L;\n    private int scannerImeFragments=0;\n    private int scannerImeGeneration=0;\n'''
if old not in s: raise SystemExit('3.0.56 target missing: barcode text generation field')
s=s.replace(old,new,1)

# Install a second, field-independent scanner detector on Barcode itself. This detector uses
# only the newly inserted text, so a fresh scan replaces an old barcode instead of appending.
old='''        barcode.setOnEditorActionListener((v,action,event)->{\n'''
new='''        installScannerImeWatcher(barcode);\n        barcode.setOnEditorActionListener((v,action,event)->{\n'''
if old not in s: raise SystemExit('3.0.56 target missing: barcode editor listener')
s=s.replace(old,new,1)

# Unknown items intentionally focus Description for manual entry, but a new scan while
# Description is active must be recognized as a barcode and routed back to Barcode.
old='''        description=new EditText(this);description.setSingleLine(true);description.setHint(\"Enter description (optional)\");description.setTextSize(16);\n        styleEntry(description);root.addView(description,new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT,dp(48)));\n'''
new='''        description=new EditText(this);description.setSingleLine(true);description.setHint(\"Enter description (optional)\");description.setTextSize(16);\n        styleEntry(description);installScannerImeWatcher(description);root.addView(description,new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT,dp(48)));\n'''
if old not in s: raise SystemExit('3.0.56 target missing: description creation')
s=s.replace(old,new,1)

# Known items focus Quantity. A subsequent Bluetooth scan must not type into Quantity;
# recognize the rapid numeric burst and route it back to Barcode automatically.
old='''        qty.setInputType(InputType.TYPE_CLASS_NUMBER);styleEntry(qty);\n'''
new='''        qty.setInputType(InputType.TYPE_CLASS_NUMBER);styleEntry(qty);installScannerImeWatcher(qty);\n'''
if old not in s: raise SystemExit('3.0.56 target missing: quantity creation')
s=s.replace(old,new,1)

# Add the field-independent IME scanner watcher before adjustQty().
marker='''    private void adjustQty(int delta) {\n'''
if marker not in s: raise SystemExit('3.0.56 target missing: adjustQty marker')
helper=r'''    private void installScannerImeWatcher(EditText field) {
        field.addTextChangedListener(new TextWatcher(){
            private String prior="";
            @Override public void beforeTextChanged(CharSequence text,int st,int count,int after){
                prior=text==null?"":text.toString();
            }
            @Override public void onTextChanged(CharSequence text,int st,int before,int count){
                if(scannerRedirectInternal||barcodeInternalUpdate||count<=0||field==null||!field.hasFocus())return;
                int length=text==null?0:text.length();
                int end=Math.min(length,st+count);
                if(st<0||end<=st)return;
                String inserted=text.subSequence(st,end).toString().replace("\r","").replace("\n","").replace("\t","").trim();
                if(inserted.isEmpty())return;

                // Quantity/Description scanner redirects are numeric UPC/EAN/GTIN bursts.
                // Barcode itself also allows common alphanumeric scanner values.
                boolean allowed=(field==barcode)?inserted.matches("[0-9A-Za-z._-]+") : inserted.matches("[0-9]+" );
                if(!allowed){
                    scannerImeBuffer.setLength(0);
                    scannerImeSource=null;
                    scannerImeLastMs=0L;
                    scannerImeFragments=0;
                    scannerImeGeneration++;
                    return;
                }

                long now=System.currentTimeMillis();
                boolean newBurst=field!=scannerImeSource || scannerImeLastMs==0L || now-scannerImeLastMs>180L;
                if(newBurst){
                    scannerImeBuffer.setLength(0);
                    scannerImeSource=field;
                    scannerImeOriginalText=prior;
                    scannerImeFragments=0;
                }
                scannerImeLastMs=now;
                scannerImeBuffer.append(inserted);
                scannerImeFragments++;

                String candidate=scannerImeBuffer.toString().trim();
                boolean wholeCommit=inserted.length()>=8;
                boolean rapidBurst=candidate.length()>=8&&scannerImeFragments>=4;
                if(candidate.length()>=8&&(wholeCommit||rapidBurst)){
                    final int token=++scannerImeGeneration;
                    field.postDelayed(()->commitScannerImeBurst(token),220);
                }
            }
            @Override public void afterTextChanged(Editable e){}
        });
    }

    private void commitScannerImeBurst(int token) {
        if(token!=scannerImeGeneration)return;
        String candidate=scannerImeBuffer.toString().trim();
        EditText source=scannerImeSource;
        String original=scannerImeOriginalText==null?"":scannerImeOriginalText;
        if(candidate.length()<8)return;

        scannerImeBuffer.setLength(0);
        scannerImeSource=null;
        scannerImeOriginalText="";
        scannerImeLastMs=0L;
        scannerImeFragments=0;
        scannerImeGeneration++;
        barcodeTextGeneration++; // cancel any older Barcode-only delayed detection

        scannerRedirectInternal=true;
        try {
            // Remove scanner characters from whichever non-barcode field received them.
            if(source!=null&&source!=barcode){
                source.setText(original);
                source.setSelection(source.getText().length());
            }

            // Scanner always owns Barcode and replaces whatever was already there.
            barcode.setShowSoftInputOnFocus(false);
            barcodeInternalUpdate=true;
            try {
                barcode.setText(candidate);
                barcode.setSelection(candidate.length());
            } finally {
                barcodeInternalUpdate=false;
            }
            barcode.requestFocus();
            hideKeyboard();
            handleScannedBarcode(candidate);
        } finally {
            scannerRedirectInternal=false;
        }
    }

'''
s=s.replace(marker,helper+marker,1)

# Unknown Add mode: barcode stays captured, but cursor/keyboard moves to Description so the
# operator can type the unknown description. If they scan instead, the watcher above wins.
old='''        description.setText(\"\");\n        if(!\"search\".equals(mode)) {\n            focusQuantity();\n            return;\n        }\n'''
new='''        description.setText(\"\");\n        if(!\"search\".equals(mode)) {\n            focusDescription();\n            return;\n        }\n'''
if old not in s: raise SystemExit('3.0.56 target missing: unknown add focus')
s=s.replace(old,new,1)

# If an internet search cannot supply a description, put the operator in Description rather
# than Quantity. If it finds a description, continue to Quantity as before.
old='''                        toast(d.isEmpty()?\"Internet item data found\":\"Internet item found\");\n                    } else toast(\"No internet item found\");\n                    focusQuantity();\n'''
new='''                        toast(d.isEmpty()?\"Internet item data found\":\"Internet item found\");\n                        if(d.isEmpty())focusDescription(); else focusQuantity();\n                    } else {\n                        toast(\"No internet item found\");\n                        focusDescription();\n                    }\n'''
if old not in s: raise SystemExit('3.0.56 target missing: internet lookup focus')
s=s.replace(old,new,1)

old='''                    toast(e.getMessage()==null?\"Internet lookup failed\":e.getMessage());\n                    focusQuantity();\n'''
new='''                    toast(e.getMessage()==null?\"Internet lookup failed\":e.getMessage());\n                    focusDescription();\n'''
if old not in s: raise SystemExit('3.0.56 target missing: internet failure focus')
s=s.replace(old,new,1)

# Manual description entry helper.
old='''    private void focusQuantity() {\n        qty.requestFocus();\n        qty.setSelection(qty.getText().length());\n        qty.postDelayed(()->showKeyboard(qty),80);\n    }\n\n'''
new='''    private void focusDescription() {\n        description.requestFocus();\n        description.setSelection(description.getText().length());\n        description.postDelayed(()->showKeyboard(description),80);\n    }\n\n    private void focusQuantity() {\n        qty.requestFocus();\n        qty.setSelection(qty.getText().length());\n        qty.postDelayed(()->showKeyboard(qty),80);\n    }\n\n'''
if old not in s: raise SystemExit('3.0.56 target missing: focusQuantity method')
s=s.replace(old,new,1)

p.write_text(s)
print('Prepared iCE Onhand 3.0.56: scanner always reroutes from Barcode/Description/Quantity + unknown items focus Description')
