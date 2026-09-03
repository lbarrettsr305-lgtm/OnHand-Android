from pathlib import Path

p=Path('app/src/main/java/com/iceinventory/onhand/MainActivity.java')
s=p.read_text()

old='''    private void showAddQuantity(InventoryDb.Row r){
        LinearLayout box=new LinearLayout(this); box.setOrientation(LinearLayout.VERTICAL); box.setPadding(dp(24),dp(8),dp(24),0);
        String[] itemParts=splitDescriptionPrice(r.description); String itemDescription=itemParts[0].trim(); if(itemDescription.isEmpty()) itemDescription=r.barcode;
        TextView itemName=new TextView(this); itemName.setText(itemDescription); itemName.setTextSize(20); itemName.setTextColor(Color.BLACK); itemName.setTypeface(Typeface.create("sans-serif",Typeface.BOLD)); itemName.setPadding(0,dp(4),0,dp(8)); box.addView(itemName);
        TextView current=new TextView(this); current.setText("Current Quantity: "+r.quantity); current.setTextSize(16); current.setTextColor(Color.BLACK); current.setTypeface(Typeface.create("sans-serif",Typeface.BOLD)); box.addView(current);
        EditText amount=new EditText(this); amount.setHint("Amount to add"); amount.setInputType(InputType.TYPE_CLASS_NUMBER|InputType.TYPE_NUMBER_FLAG_SIGNED); amount.setTextSize(22); amount.setSelectAllOnFocus(true); box.addView(amount);
        AlertDialog dialog=new AlertDialog.Builder(this).setTitle("Add Quantity").setView(box).setPositiveButton("Add",null).setNegativeButton("Cancel",null).create();
        dialog.setOnShowListener(x->{
            dialog.getButton(AlertDialog.BUTTON_POSITIVE).setOnClickListener(v->{
                String text=amount.getText().toString().trim(); if(text.isEmpty()){amount.requestFocus();return;}
                try{ int add=Integer.parseInt(text); if(add==0){toast("Enter an amount to add");amount.requestFocus();return;} db.incrementItem(r.id,add); highlightedRowId=r.id; refreshList(); toast("Added "+add+" • Qty "+(r.quantity+add)); dialog.dismiss(); }
                catch(Exception e){toast("Enter a valid quantity");amount.requestFocus();}
            });
            amount.requestFocus(); amount.postDelayed(()->amount.requestFocus(),80);
        });
        dialog.show();
    }
'''

new='''    private void showAddQuantity(InventoryDb.Row r){
        LinearLayout box=new LinearLayout(this); box.setOrientation(LinearLayout.VERTICAL); box.setPadding(dp(24),dp(8),dp(24),dp(10));
        String[] itemParts=splitDescriptionPrice(r.description); String itemDescription=itemParts[0].trim(); if(itemDescription.isEmpty()) itemDescription=r.barcode;
        TextView itemName=new TextView(this); itemName.setText(itemDescription); itemName.setTextSize(20); itemName.setTextColor(Color.BLACK); itemName.setTypeface(Typeface.create("sans-serif",Typeface.BOLD)); itemName.setPadding(0,dp(4),0,dp(8)); box.addView(itemName);
        TextView current=new TextView(this); current.setText("Current Quantity: "+r.quantity); current.setTextSize(16); current.setTextColor(Color.BLACK); current.setTypeface(Typeface.create("sans-serif",Typeface.BOLD)); current.setPadding(0,0,0,dp(8)); box.addView(current);

        TextView directLabel=new TextView(this); directLabel.setText("Amount to add"); directLabel.setTextColor(Color.BLACK); directLabel.setTypeface(Typeface.create("sans-serif",Typeface.BOLD)); box.addView(directLabel);
        EditText amount=new EditText(this); amount.setHint("Example: 12"); amount.setInputType(InputType.TYPE_CLASS_NUMBER|InputType.TYPE_NUMBER_FLAG_SIGNED); amount.setTextSize(20); amount.setSelectAllOnFocus(true); box.addView(amount);

        TextView multiplyLabel=new TextView(this); multiplyLabel.setText("OR multiply cases"); multiplyLabel.setTextColor(Color.BLACK); multiplyLabel.setTypeface(Typeface.create("sans-serif",Typeface.BOLD)); multiplyLabel.setPadding(0,dp(10),0,dp(2)); box.addView(multiplyLabel);
        LinearLayout multiplyRow=new LinearLayout(this); multiplyRow.setOrientation(LinearLayout.HORIZONTAL); multiplyRow.setGravity(Gravity.CENTER_VERTICAL);
        EditText pack=new EditText(this); pack.setHint("Units/case"); pack.setInputType(InputType.TYPE_CLASS_NUMBER); pack.setTextSize(18); pack.setGravity(Gravity.CENTER);
        TextView times=new TextView(this); times.setText(" × "); times.setTextSize(22); times.setTextColor(Color.BLACK); times.setTypeface(Typeface.DEFAULT_BOLD); times.setGravity(Gravity.CENTER);
        EditText cases=new EditText(this); cases.setHint("Cases"); cases.setInputType(InputType.TYPE_CLASS_NUMBER); cases.setTextSize(18); cases.setGravity(Gravity.CENTER);
        multiplyRow.addView(pack,new LinearLayout.LayoutParams(0,ViewGroup.LayoutParams.WRAP_CONTENT,1)); multiplyRow.addView(times); multiplyRow.addView(cases,new LinearLayout.LayoutParams(0,ViewGroup.LayoutParams.WRAP_CONTENT,1)); box.addView(multiplyRow);
        TextView calculated=new TextView(this); calculated.setText("Calculated amount: —"); calculated.setTextSize(17); calculated.setTextColor(Color.BLACK); calculated.setTypeface(Typeface.create("sans-serif",Typeface.BOLD)); calculated.setPadding(0,dp(4),0,dp(4)); box.addView(calculated);

        android.text.TextWatcher watcher=new android.text.TextWatcher(){
            public void beforeTextChanged(CharSequence a,int b,int c,int d){}
            public void onTextChanged(CharSequence a,int b,int c,int d){
                try{ String ps=pack.getText().toString().trim(), cs=cases.getText().toString().trim(); if(ps.isEmpty()||cs.isEmpty()){calculated.setText("Calculated amount: —");return;} long total=Long.parseLong(ps)*Long.parseLong(cs); calculated.setText("Calculated amount: "+total); }catch(Exception e){calculated.setText("Calculated amount: —");}
            }
            public void afterTextChanged(android.text.Editable e){}
        };
        pack.addTextChangedListener(watcher); cases.addTextChangedListener(watcher);

        ScrollView scroll=new ScrollView(this); scroll.setFillViewport(true); scroll.addView(box);
        AlertDialog dialog=new AlertDialog.Builder(this).setTitle("Add Quantity").setView(scroll).setPositiveButton("Add",null).setNegativeButton("Cancel",null).create();
        dialog.setOnShowListener(x->{
            if(dialog.getWindow()!=null) dialog.getWindow().setSoftInputMode(android.view.WindowManager.LayoutParams.SOFT_INPUT_ADJUST_RESIZE|android.view.WindowManager.LayoutParams.SOFT_INPUT_STATE_ALWAYS_HIDDEN);
            dialog.getButton(AlertDialog.BUTTON_POSITIVE).setOnClickListener(v->{
                try{
                    int add;
                    String direct=amount.getText().toString().trim();
                    if(!direct.isEmpty()) add=Integer.parseInt(direct);
                    else {
                        String ps=pack.getText().toString().trim(), cs=cases.getText().toString().trim();
                        if(ps.isEmpty()||cs.isEmpty()){toast("Enter an amount or multiply units × cases");return;}
                        long total=Long.parseLong(ps)*Long.parseLong(cs); if(total>Integer.MAX_VALUE) throw new Exception("too large"); add=(int)total;
                    }
                    if(add==0){toast("Amount cannot be zero");return;}
                    db.incrementItem(r.id,add); highlightedRowId=r.id; refreshList(); toast("Added "+add+" • Qty "+(r.quantity+add)); dialog.dismiss();
                } catch(Exception e){toast("Enter a valid quantity");}
            });
        });
        dialog.show();
    }
'''

if old not in s: raise SystemExit('3.0.30 Add Quantity dialog block not found')
s=s.replace(old,new,1)
p.write_text(s)

b=Path('app/build.gradle')
g=b.read_text().replace('versionCode 30032','versionCode 30033').replace("versionName '3.0.32'","versionName '3.0.33'")
b.write_text(g)
