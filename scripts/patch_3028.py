from pathlib import Path

p=Path('app/src/main/java/com/iceinventory/onhand/MainActivity.java')
s=p.read_text()

# Older Android devices sometimes ignore a single posted focus request after a hardware scan.
old='''    private void focusQuantityAfterScan(){
        if(qty==null) return;
        qty.post(()->{
            qty.requestFocus();
            qty.setSelection(qty.length());
        });
    }
'''
new='''    private void focusQuantityAfterScan(){
        if(qty==null) return;
        qty.setFocusable(true);
        qty.setFocusableInTouchMode(true);
        Runnable focus=()->{
            qty.requestFocus();
            qty.requestFocusFromTouch();
            qty.setSelection(qty.length());
        };
        qty.post(focus);
        qty.postDelayed(focus,80);
        qty.postDelayed(focus,180);
    }
'''
if old not in s: raise SystemExit('focus helper not found')
s=s.replace(old,new,1)

# Remove the old description-only +1 target.
s=s.replace('''                    desc.setOnClickListener(v->{ highlightedRowId=r.id; db.incrementItem(r.id,1); refreshList(); toast("Quantity +1"); });
''','',1)

# Replace combined detail line with a dedicated, large Quantity control.
old_detail='''                String loc=(r.location==null||r.location.trim().isEmpty())?"Main":r.location.trim();
                TextView detail=new TextView(MainActivity.this); detail.setText("Qty "+r.quantity+"   •   "+loc+(price.isEmpty()?"":"   •   "+price)); detail.setTextSize(11); detail.setTypeface(Typeface.create("sans-serif",Typeface.NORMAL)); row.addView(detail);
                TextView code=new TextView(MainActivity.this); code.setText(displayCode); code.setTextSize(10); code.setTypeface(Typeface.create("sans-serif-monospace",Typeface.NORMAL)); row.addView(code);
                row.setOnClickListener(v->{ highlightedRowId=r.id; db.incrementItem(r.id,1); refreshList(); toast("Quantity +1"); });
                row.setOnLongClickListener(v->{editRow(position);return true;});
'''
new_detail='''                String loc=(r.location==null||r.location.trim().isEmpty())?"Main":r.location.trim();
                LinearLayout qtyLine=new LinearLayout(MainActivity.this); qtyLine.setOrientation(LinearLayout.HORIZONTAL); qtyLine.setGravity(Gravity.CENTER_VERTICAL);
                TextView qtyBox=new TextView(MainActivity.this); qtyBox.setText("Qty  "+r.quantity); qtyBox.setTextSize(16); qtyBox.setTypeface(Typeface.create("sans-serif",Typeface.BOLD)); qtyBox.setGravity(Gravity.CENTER); qtyBox.setPadding(dp(14),dp(8),dp(14),dp(8)); qtyBox.setBackgroundColor(r.id==highlightedRowId?Color.rgb(246,197,0):Color.rgb(45,45,45));
                qtyBox.setOnClickListener(v->showAddQuantity(r));
                qtyLine.addView(qtyBox,new LinearLayout.LayoutParams(0,ViewGroup.LayoutParams.WRAP_CONTENT,1));
                TextView locPrice=new TextView(MainActivity.this); locPrice.setText(loc+(price.isEmpty()?"":"   •   "+price)); locPrice.setTextSize(11); locPrice.setGravity(Gravity.CENTER_VERTICAL|Gravity.END); locPrice.setPadding(dp(10),0,dp(4),0); qtyLine.addView(locPrice,new LinearLayout.LayoutParams(0,ViewGroup.LayoutParams.MATCH_PARENT,2));
                row.addView(qtyLine);
                TextView code=new TextView(MainActivity.this); code.setText(displayCode); code.setTextSize(10); code.setTypeface(Typeface.create("sans-serif-monospace",Typeface.NORMAL)); row.addView(code);
                row.setOnLongClickListener(v->{editRow(position);return true;});
'''
if old_detail not in s: raise SystemExit('3.0.25/26 row detail block not found')
s=s.replace(old_detail,new_detail,1)

# Stop the whole row from incrementing; quantity itself is now the deliberate target.
old_list='''list.setAdapter(listAdapter); list.setOnItemClickListener((p,v,pos,id)->{ if(pos>=0&&pos<visibleRows.size()){ InventoryDb.Row r=visibleRows.get(pos); highlightedRowId=r.id; db.incrementItem(r.id,1); refreshList(); toast("Quantity +1"); }});'''
new_list='''list.setAdapter(listAdapter); list.setOnItemClickListener((p,v,pos,id)->{});'''
if old_list not in s: raise SystemExit('list increment handler not found')
s=s.replace(old_list,new_list,1)

# Add a manual amount-to-add dialog. Example: current 4 + entered 9 = 13.
anchor='    private void editRow(int pos){'
method='''    private void showAddQuantity(InventoryDb.Row r){
        LinearLayout box=new LinearLayout(this); box.setOrientation(LinearLayout.VERTICAL); box.setPadding(dp(24),dp(8),dp(24),0);
        TextView current=new TextView(this); current.setText("Current Quantity: "+r.quantity); current.setTextSize(16); box.addView(current);
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
if method not in s:
    if anchor not in s: raise SystemExit('editRow anchor not found')
    s=s.replace(anchor,method+anchor,1)

# Export files should use .txt while keeping the existing comma-separated content format.
s=s.replace('safeFileName(sessionName)+".csv"','safeFileName(sessionName)+".txt"')
s=s.replace('if(!requested.toLowerCase(Locale.US).endsWith(".csv"))requested+=".csv";','if(!requested.toLowerCase(Locale.US).endsWith(".txt"))requested+=".txt";')
s=s.replace('i.setType("text/csv")','i.setType("text/plain")')
s=s.replace('values.put(MediaStore.MediaColumns.MIME_TYPE,"text/csv")','values.put(MediaStore.MediaColumns.MIME_TYPE,"text/plain")')
s=s.replace('toast("CSV exported")','toast("TXT exported")')

p.write_text(s)

b=Path('app/build.gradle')
g=b.read_text()
for old in ('30027','30026','30025','30024','30023'):
    g=g.replace('versionCode '+old,'versionCode 30028')
for old in ('3.0.27','3.0.26','3.0.25','3.0.24','3.0.23'):
    g=g.replace("versionName '"+old+"'","versionName '3.0.28'")
b.write_text(g)
