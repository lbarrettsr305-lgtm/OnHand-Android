from pathlib import Path

p=Path('app/src/main/java/com/iceinventory/onhand/MainActivity.java')
s=p.read_text()

# Replace Add Quantity dialog with a fixed header and scrollable controls so the keyboard cannot cover the item description.
start=s.find('    private void showAddQuantity(InventoryDb.Row r){')
end=s.find('\n    private ', start+10)
if start<0 or end<0:
    raise SystemExit('showAddQuantity method not found')

new_method='''    private void showAddQuantity(InventoryDb.Row r){
        String[] itemParts=splitDescriptionPrice(r.description); String itemDescription=itemParts[0].trim(); if(itemDescription.isEmpty()) itemDescription=r.barcode;

        LinearLayout shell=new LinearLayout(this); shell.setOrientation(LinearLayout.VERTICAL); shell.setPadding(dp(20),dp(8),dp(20),dp(8));

        LinearLayout header=new LinearLayout(this); header.setOrientation(LinearLayout.VERTICAL); header.setPadding(0,0,0,dp(8)); header.setBackgroundColor(Color.rgb(255,248,210));
        TextView itemName=new TextView(this); itemName.setText(itemDescription); itemName.setTextSize(20); itemName.setTextColor(Color.BLACK); itemName.setTypeface(Typeface.create("sans-serif",Typeface.BOLD)); itemName.setPadding(dp(10),dp(8),dp(10),dp(4)); header.addView(itemName);
        TextView current=new TextView(this); current.setText("Current Quantity: "+r.quantity); current.setTextSize(16); current.setTextColor(Color.BLACK); current.setTypeface(Typeface.create("sans-serif",Typeface.BOLD)); current.setPadding(dp(10),0,dp(10),dp(8)); header.addView(current);
        shell.addView(header,new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT,ViewGroup.LayoutParams.WRAP_CONTENT));

        LinearLayout controls=new LinearLayout(this); controls.setOrientation(LinearLayout.VERTICAL); controls.setPadding(0,dp(6),0,dp(8));
        TextView directLabel=new TextView(this); directLabel.setText("Amount to add"); directLabel.setTextColor(Color.BLACK); directLabel.setTypeface(Typeface.create("sans-serif",Typeface.BOLD)); controls.addView(directLabel);
        EditText amount=new EditText(this); amount.setHint("Example: 12"); amount.setInputType(InputType.TYPE_CLASS_NUMBER|InputType.TYPE_NUMBER_FLAG_SIGNED); amount.setTextSize(20); amount.setSelectAllOnFocus(true); controls.addView(amount);

        TextView multiplyLabel=new TextView(this); multiplyLabel.setText("OR multiply cases"); multiplyLabel.setTextColor(Color.BLACK); multiplyLabel.setTypeface(Typeface.create("sans-serif",Typeface.BOLD)); multiplyLabel.setPadding(0,dp(10),0,dp(2)); controls.addView(multiplyLabel);
        LinearLayout multiplyRow=new LinearLayout(this); multiplyRow.setOrientation(LinearLayout.HORIZONTAL); multiplyRow.setGravity(Gravity.CENTER_VERTICAL);
        EditText pack=new EditText(this); pack.setHint("Units/case"); pack.setInputType(InputType.TYPE_CLASS_NUMBER); pack.setTextSize(18); pack.setGravity(Gravity.CENTER);
        TextView times=new TextView(this); times.setText(" × "); times.setTextSize(22); times.setTextColor(Color.BLACK); times.setTypeface(Typeface.DEFAULT_BOLD); times.setGravity(Gravity.CENTER);
        EditText cases=new EditText(this); cases.setHint("Cases"); cases.setInputType(InputType.TYPE_CLASS_NUMBER); cases.setTextSize(18); cases.setGravity(Gravity.CENTER);
        multiplyRow.addView(pack,new LinearLayout.LayoutParams(0,ViewGroup.LayoutParams.WRAP_CONTENT,1)); multiplyRow.addView(times); multiplyRow.addView(cases,new LinearLayout.LayoutParams(0,ViewGroup.LayoutParams.WRAP_CONTENT,1)); controls.addView(multiplyRow);
        TextView calculated=new TextView(this); calculated.setText("Calculated amount: —"); calculated.setTextSize(17); calculated.setTextColor(Color.BLACK); calculated.setTypeface(Typeface.create("sans-serif",Typeface.BOLD)); calculated.setPadding(0,dp(4),0,dp(4)); controls.addView(calculated);

        android.text.TextWatcher watcher=new android.text.TextWatcher(){
            public void beforeTextChanged(CharSequence a,int b,int c,int d){}
            public void onTextChanged(CharSequence a,int b,int c,int d){
                try{ String ps=pack.getText().toString().trim(), cs=cases.getText().toString().trim(); if(ps.isEmpty()||cs.isEmpty()){calculated.setText("Calculated amount: —");return;} long total=Long.parseLong(ps)*Long.parseLong(cs); calculated.setText("Calculated amount: "+total); }catch(Exception e){calculated.setText("Calculated amount: —");}
            }
            public void afterTextChanged(android.text.Editable e){}
        };
        pack.addTextChangedListener(watcher); cases.addTextChangedListener(watcher);

        ScrollView scroll=new ScrollView(this); scroll.setFillViewport(false); scroll.addView(controls);
        shell.addView(scroll,new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT,0,1));
        shell.setFocusableInTouchMode(true); shell.requestFocus();

        AlertDialog dialog=new AlertDialog.Builder(this).setTitle("Add Quantity").setView(shell).setPositiveButton("Add",null).setNegativeButton("Cancel",null).create();
        dialog.setOnShowListener(x->{
            if(dialog.getWindow()!=null){
                dialog.getWindow().setSoftInputMode(android.view.WindowManager.LayoutParams.SOFT_INPUT_ADJUST_RESIZE|android.view.WindowManager.LayoutParams.SOFT_INPUT_STATE_ALWAYS_HIDDEN);
                int target=Math.min(dp(520),(int)(getResources().getDisplayMetrics().heightPixels*0.78f));
                dialog.getWindow().setLayout(ViewGroup.LayoutParams.MATCH_PARENT,target);
            }
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

s=s[:start]+new_method+s[end:]
p.write_text(s)

b=Path('app/build.gradle')
g=b.read_text().replace('versionCode 30036','versionCode 30037').replace("versionName '3.0.36'","versionName '3.0.37'")
b.write_text(g)
