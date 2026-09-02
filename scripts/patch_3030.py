from pathlib import Path

p=Path('app/src/main/java/com/iceinventory/onhand/MainActivity.java')
s=p.read_text()
old='''        TextView current=new TextView(this); current.setText("Current Quantity: "+r.quantity); current.setTextSize(16); box.addView(current);
        EditText amount=new EditText(this); amount.setHint("Amount to add");'''
new='''        String[] itemParts=splitDescriptionPrice(r.description); String itemDescription=itemParts[0].trim(); if(itemDescription.isEmpty()) itemDescription=r.barcode;
        TextView itemName=new TextView(this); itemName.setText(itemDescription); itemName.setTextSize(20); itemName.setTextColor(Color.BLACK); itemName.setTypeface(Typeface.create("sans-serif",Typeface.BOLD)); itemName.setPadding(0,dp(4),0,dp(8)); box.addView(itemName);
        TextView current=new TextView(this); current.setText("Current Quantity: "+r.quantity); current.setTextSize(16); current.setTextColor(Color.BLACK); current.setTypeface(Typeface.create("sans-serif",Typeface.BOLD)); box.addView(current);
        EditText amount=new EditText(this); amount.setHint("Amount to add");'''
if old not in s: raise SystemExit('Add Quantity dialog block not found')
s=s.replace(old,new,1)
p.write_text(s)

b=Path('app/build.gradle')
g=b.read_text().replace('versionCode 30029','versionCode 30030').replace("versionName '3.0.29'","versionName '3.0.30'")
b.write_text(g)
