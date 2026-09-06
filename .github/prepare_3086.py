from pathlib import Path
import re

base=Path('.github/prepare_3085.py')
exec(compile(base.read_text(),str(base),'exec'),{'__name__':'__main__','__file__':str(base)})

p=Path('app/src/main/java/com/iceinventory/onhand/MainActivity.java')
s=p.read_text()

old='''    @Override public void onAddOne(InventoryDb.Row row) {
        db.incrementQuantity(row.id,1);lastBarcode=row.barcode;refreshList();
    }

    @Override public void onSubtractOne(InventoryDb.Row row) {
        if(row.quantity<=0)return;
        db.incrementQuantity(row.id,-1);lastBarcode=row.barcode;refreshList();
    }
'''
new='''    @Override public void onAddOne(InventoryDb.Row row) {
        db.incrementQuantity(row.id,1);lastBarcode=row.barcode;refreshList();noteCountForSafety();
    }

    @Override public void onSubtractOne(InventoryDb.Row row) {
        if(row.quantity<=0)return;
        db.incrementQuantity(row.id,-1);lastBarcode=row.barcode;refreshList();noteCountForSafety();
    }
'''
if old not in s:raise SystemExit('3.0.86 target missing: plus/minus callbacks')
s=s.replace(old,new,1)

replacement='''    @Override public void onEdit(InventoryDb.Row r) {
        LinearLayout box=new LinearLayout(this);box.setOrientation(LinearLayout.VERTICAL);box.setPadding(dp(18),dp(6),dp(18),0);
        String desc=r.description==null?"":r.description;
        String price=(r.price==null||r.price.trim().isEmpty())?"":"$"+r.price.trim();
        String details="Barcode: "+r.barcode+"\\nDescription: "+desc+"\\nPrice: "+price+"\\nCurrent Qty: "+r.quantity+"\\nLocation: "+(r.location==null?"Main":r.location);
        TextView info=text(details,15,Color.BLACK,false);box.addView(info);
        EditText adjustment=new EditText(this);
        adjustment.setHint("Adjustment: + add or - subtract");
        adjustment.setInputType(InputType.TYPE_CLASS_NUMBER|InputType.TYPE_NUMBER_FLAG_SIGNED);
        adjustment.setSingleLine(true);box.addView(adjustment);
        TextView result=text("New Qty: "+r.quantity,17,Color.BLACK,true);result.setPadding(0,dp(6),0,0);box.addView(result);
        adjustment.addTextChangedListener(new android.text.TextWatcher(){
            public void beforeTextChanged(CharSequence x,int start,int count,int after){}
            public void onTextChanged(CharSequence x,int start,int before,int count){
                int amount=0;try{amount=Integer.parseInt(String.valueOf(x).trim());}catch(Exception ignored){}
                int next=r.quantity+amount;result.setText("New Qty: "+next);result.setTextColor(next<0?Color.RED:Color.BLACK);
            }
            public void afterTextChanged(android.text.Editable x){}
        });
        AlertDialog dialog=new AlertDialog.Builder(this).setTitle("Adjust Quantity").setView(box)
                .setPositiveButton("Apply",null).setNegativeButton("Cancel",null).create();
        dialog.setOnShowListener(x->{
            dialog.getButton(AlertDialog.BUTTON_POSITIVE).setOnClickListener(v->{
                String raw=adjustment.getText().toString().trim();int amount=0;try{amount=Integer.parseInt(raw);}catch(Exception ignored){}
                if(amount==0){toast("Enter an amount such as 5 or -500");adjustment.requestFocus();showKeyboard(adjustment);return;}
                int next=r.quantity+amount;if(next<0){toast("Quantity cannot go below zero");adjustment.requestFocus();return;}
                db.incrementQuantity(r.id,amount);lastBarcode=r.barcode;refreshList();noteCountForSafety();dialog.dismiss();
                toast(amount<0?"Subtracted "+Math.abs(amount)+" • New quantity "+next:"Added "+amount+" • New quantity "+next);
            });
            adjustment.requestFocus();adjustment.postDelayed(()->showKeyboard(adjustment),100);
        });
        dialog.show();
    }
'''
pat=r'''    @Override public void onEdit\(InventoryDb\.Row r\) \{.*?\n    \}\n(?=\n    @Override public void onHighlight)'''
s,n=re.subn(pat,lambda m:replacement,s,count=1,flags=re.S)
if n!=1:raise SystemExit('3.0.86 target missing: quantity adjustment dialog')

s=s.replace('Onhand Inventory 3.0.85','Onhand Inventory 3.0.86')
p.write_text(s)

p=Path('app/build.gradle');s=p.read_text().replace('versionCode 30085','versionCode 30086',1).replace("versionName '3.0.85'","versionName '3.0.86'",1)
if 'versionCode 30086' not in s or "versionName '3.0.86'" not in s:raise SystemExit('3.0.86 target missing: Gradle version')
p.write_text(s)
p=Path('app/src/main/AndroidManifest.xml');s=p.read_text().replace('iCE Onhand 3.0.85','iCE Onhand 3.0.86')
if 'iCE Onhand 3.0.86' not in s:raise SystemExit('3.0.86 target missing: manifest version')
p.write_text(s)

main=Path('app/src/main/java/com/iceinventory/onhand/MainActivity.java').read_text()
checks={'signed input':'TYPE_NUMBER_FLAG_SIGNED','subtract example':'5 or -500','new quantity preview':'result.setText("New Qty: "+next)','negative adjustment':'db.incrementQuantity(r.id,amount)','below-zero guard':'Quantity cannot go below zero','Excel default':'Export New Counts Only — Excel (.xlsx)'}
missing=[k for k,v in checks.items() if v not in main]
if missing:raise SystemExit('3.0.86 verification failed: '+', '.join(missing))
print('Prepared iCE Onhand 3.0.86: signed quantity adjustments with preview, below-zero guard, backups, and Excel default')
