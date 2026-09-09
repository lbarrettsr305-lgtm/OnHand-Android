from pathlib import Path
import re

# Preserve the validated 3.0.105 barcode build first.
base=Path('.github/prepare_30105.py')
exec(compile(base.read_text(),str(base),'exec'),{'__name__':'__main__','__file__':str(base)})

p=Path('app/src/main/java/com/iceinventory/onhand/MainActivity.java')
s=p.read_text()

old='''    private void adjustQty(int delta) {
        int q=0;
        try{String s=qty.getText().toString().trim();if(!s.isEmpty())q=Integer.parseInt(s);}catch(Exception ignored){}
        q=Math.max(0,q+delta);
        qty.setText(q==0?"":String.valueOf(q));
        qty.setSelection(qty.getText().length());
    }
'''
new='''    private void adjustQty(int delta) {
        String raw=qty.getText().toString().trim();
        if(delta<0) {
            if(raw.isEmpty()){qty.setText("-");qty.setSelection(1);return;}
            int q=0;try{q=Integer.parseInt(raw);}catch(Exception ignored){}
            q=-q;
            qty.setText(q==0?"-":String.valueOf(q));
        } else {
            int q=0;try{if(!raw.isEmpty()&&!"-".equals(raw))q=Integer.parseInt(raw);}catch(Exception ignored){}
            q=q<0?-q:q+1;
            qty.setText(String.valueOf(q));
        }
        qty.setSelection(qty.getText().length());
    }
'''
if old not in s: raise SystemExit('3.0.106 target missing: quantity sign control')
s=s.replace(old,new,1)

old='''        try{q=Integer.parseInt(qText);}catch(Exception e){toast("Quantity must be a number");focusQuantity();return;}
        if(q<=0){toast("Quantity must be greater than zero");focusQuantity();return;}
        String loc=location.getSelectedItem()==null?"Main":location.getSelectedItem().toString();
'''
new='''        try{q=Integer.parseInt(qText);}catch(Exception e){toast("Quantity must be a number");focusQuantity();return;}
        if(q==0){toast("Quantity cannot be zero");focusQuantity();return;}
        int current=db.quantityForBarcode(sessionId,code);
        if(q<0&&current+q<0){toast("Cannot subtract more than current quantity "+current);focusQuantity();return;}
        if(q<0&&current==0){toast("Cannot subtract an unknown or zero-quantity item");focusQuantity();return;}
        String loc=location.getSelectedItem()==null?"Main":location.getSelectedItem().toString();
'''
if old not in s: raise SystemExit('3.0.106 target missing: positive-only Add Qty guard')
s=s.replace(old,new,1)

# Keep large partial-barcode searches off the Android UI thread. This prevents
# older devices from showing the system "Wait / Close app" ANR dialog.
old='''        List<InventoryDb.Row> flexible=flexibleBarcodeMatches(code);
        if(flexible.size()==1) {
            useSavedBarcodeMatch(flexible.get(0),true);
            return;
        }
        if(flexible.size()>1) {
            showFlexibleBarcodeChoices(flexible);
            return;
        }

        String mode=getUnknownBarcodeMode();
'''
new='''        final String lookupCode=code;
        final ArrayList<InventoryDb.Row> lookupRows=new ArrayList<>(allRows);
        toast("Searching inventory...");
        new Thread(()->{
            List<InventoryDb.Row> flexible=flexibleBarcodeMatches(lookupCode,lookupRows);
            runOnUiThread(()->finishPartialBarcodeSearch(lookupCode,flexible));
        }).start();
        return;
    }

    private void finishPartialBarcodeSearch(String code,List<InventoryDb.Row> flexible) {
        if(!code.equals(barcode.getText().toString().trim()))return;
        if(flexible.size()==1) { useSavedBarcodeMatch(flexible.get(0),true);return; }
        if(flexible.size()>1) { showFlexibleBarcodeChoices(flexible);return; }
        handleUnknownScannedBarcode(code);
    }

    private void handleUnknownScannedBarcode(String code) {
        String mode=getUnknownBarcodeMode();
'''
if old not in s: raise SystemExit('3.0.106 target missing: synchronous partial search')
s=s.replace(old,new,1)

old='''    private List<InventoryDb.Row> flexibleBarcodeMatches(String input) {
        LinkedHashMap<String,InventoryDb.Row> unique=new LinkedHashMap<>();
        for(InventoryDb.Row r:allRows) {
'''
new='''    private List<InventoryDb.Row> flexibleBarcodeMatches(String input,List<InventoryDb.Row> sourceRows) {
        LinkedHashMap<String,InventoryDb.Row> unique=new LinkedHashMap<>();
        for(InventoryDb.Row r:sourceRows) {
'''
if old not in s: raise SystemExit('3.0.106 target missing: partial search source')
s=s.replace(old,new,1)

s=s.replace('Onhand Inventory 3.0.105','Onhand Inventory 3.0.106',1)
if 'Onhand Inventory 3.0.106' not in s: raise SystemExit('3.0.106 visible version target missing')
p.write_text(s)

p=Path('app/build.gradle')
g=p.read_text().replace('versionCode 30105','versionCode 30106',1).replace("versionName '3.0.105'","versionName '3.0.106'",1)
if 'versionCode 30106' not in g or "versionName '3.0.106'" not in g: raise SystemExit('3.0.106 Gradle version target missing')
p.write_text(g)

p=Path('app/src/main/AndroidManifest.xml')
m=p.read_text().replace('iCE Onhand 3.0.105','iCE Onhand 3.0.106',1)
if 'iCE Onhand 3.0.106' not in m: raise SystemExit('3.0.106 manifest version target missing')
p.write_text(m)

main=Path('app/src/main/java/com/iceinventory/onhand/MainActivity.java').read_text()
checks={
    'minus sign toggle':'if(delta<0)' in main and 'qty.setText("-")' in main and 'q=-q' in main,
    'negative quantity allowed':'if(q==0)' in main,
    'below-zero guard':'if(q<0&&current+q<0)' in main,
    'negative count recorded':'db.addOrIncrement(sessionId,code,description.getText().toString(),currentPrice,q,loc)' in main,
    'background partial search':'new Thread(()->{' in main and 'finishPartialBarcodeSearch' in main,
    'stable row snapshot':'new ArrayList<>(allRows)' in main,
    'partial barcode retained':'replaceAll("\\\\s+","")' in main and 'if(nx.length()<4||ny.length()<4)' in main,
}
missing=[k for k,v in checks.items() if not v]
if missing: raise SystemExit('3.0.106 verification failed: '+', '.join(missing))
print('Prepared iCE Onhand 3.0.106: working subtraction from the main quantity control')
