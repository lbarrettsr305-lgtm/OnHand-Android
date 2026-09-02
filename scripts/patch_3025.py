from pathlib import Path

p = Path('app/src/main/java/com/iceinventory/onhand/MainActivity.java')
s = p.read_text()

old_row = '''                LinearLayout row=new LinearLayout(MainActivity.this); row.setOrientation(LinearLayout.VERTICAL); row.setPadding(dp(10),dp(5),dp(10),dp(5));
                row.setBackgroundColor(r.id==highlightedRowId?Color.rgb(92,73,0):Color.TRANSPARENT);
                String[] parts=splitDescriptionPrice(r.description); String descText=parts[0].isEmpty()?"(No description)":parts[0];
                TextView desc=new TextView(MainActivity.this); desc.setText(descText); desc.setTextSize(14); desc.setTypeface(Typeface.create("sans-serif",Typeface.BOLD)); desc.setPadding(0,0,0,dp(1));
                desc.setOnClickListener(v->{ highlightedRowId=r.id; db.incrementItem(r.id,1); refreshList(); toast("Quantity +1"); });
                row.addView(desc);
                TextView detail=new TextView(MainActivity.this); String price=parts[1]; String loc=(r.location==null||r.location.trim().isEmpty())?"Main":r.location.trim(); detail.setText("Qty "+r.quantity+(price.isEmpty()?"":"     "+price)+"     "+loc); detail.setTextSize(12); detail.setTypeface(Typeface.create("sans-serif",Typeface.NORMAL)); row.addView(detail);
                TextView code=new TextView(MainActivity.this); code.setText(r.barcode); code.setTextSize(11); code.setTypeface(Typeface.create("sans-serif-monospace",Typeface.NORMAL)); row.addView(code);
'''
new_row = '''                LinearLayout row=new LinearLayout(MainActivity.this); row.setOrientation(LinearLayout.VERTICAL); row.setPadding(dp(8),dp(3),dp(8),dp(3));
                row.setBackgroundColor(r.id==highlightedRowId?Color.rgb(92,73,0):Color.TRANSPARENT);
                String[] parts=splitDescriptionPrice(r.description); String displayDesc=parts[0], price=parts[1];
                String displayCode=r.barcode==null?"":r.barcode.trim();
                Matcher packed=Pattern.compile("^0\\\\s+(\\\\d{6,14})\\\\s+(.+)$").matcher(displayCode);
                if(displayDesc.isEmpty()&&packed.matches()){
                    displayCode=packed.group(1);
                    String[] packedParts=splitDescriptionPrice(packed.group(2));
                    displayDesc=packedParts[0];
                    if(price.isEmpty()) price=packedParts[1];
                }
                if(!displayDesc.isEmpty()){
                    TextView desc=new TextView(MainActivity.this); desc.setText(displayDesc); desc.setTextSize(13); desc.setTypeface(Typeface.create("sans-serif",Typeface.BOLD)); desc.setPadding(0,0,0,0);
                    desc.setOnClickListener(v->{ highlightedRowId=r.id; db.incrementItem(r.id,1); refreshList(); toast("Quantity +1"); });
                    row.addView(desc);
                }
                String loc=(r.location==null||r.location.trim().isEmpty())?"Main":r.location.trim();
                TextView detail=new TextView(MainActivity.this); detail.setText("Qty "+r.quantity+"   •   "+loc+(price.isEmpty()?"":"   •   "+price)); detail.setTextSize(11); detail.setTypeface(Typeface.create("sans-serif",Typeface.NORMAL)); row.addView(detail);
                TextView code=new TextView(MainActivity.this); code.setText(displayCode); code.setTextSize(10); code.setTypeface(Typeface.create("sans-serif-monospace",Typeface.NORMAL)); row.addView(code);
'''
if old_row not in s:
    raise SystemExit('row block not found')
s = s.replace(old_row, new_row)

s = s.replace('io.setTranslationY(dp(-36));', 'io.setTranslationY(dp(-52));')

old_zero = 'zero.setOnClickListener(v->{String selected=exportLocation.getSelectedItem()==null?"All Locations":exportLocation.getSelectedItem().toString();confirmZeroQuantities("All Locations".equals(selected)?null:selected);});'
new_zero = 'zero.setOnClickListener(v->chooseZeroScope());'
if old_zero not in s:
    raise SystemExit('zero click block not found')
s = s.replace(old_zero, new_zero)

anchor = '    private void confirmZeroQuantities(String loc){String scope=loc==null?"ALL locations":"location \'"+loc+"\'";new AlertDialog.Builder(this).setTitle("Zero quantities?").setMessage("Set every quantity in "+scope+" for this inventory to 0? This changes the inventory and cannot be undone automatically.").setPositiveButton("Zero Quantities",(d,w)->{int changed=db.zeroQuantities(sessionId,loc);refreshList();toast("Zeroed "+changed+" item lines");}).setNegativeButton("Cancel",null).show();}\n'
insert = '''    private void chooseZeroScope(){
        ArrayList<String> scopes=new ArrayList<>(); scopes.add("All Locations"); scopes.addAll(db.locations());
        new AlertDialog.Builder(this).setTitle("Zero / Reset Quantities").setSingleChoiceItems(scopes.toArray(new String[0]),0,null)
                .setPositiveButton("Continue",(d,w)->{int which=((AlertDialog)d).getListView().getCheckedItemPosition();String selected=which<=0?"All Locations":scopes.get(which);confirmZeroQuantities("All Locations".equals(selected)?null:selected);})
                .setNegativeButton("Cancel",null).show();
    }

'''
if anchor not in s:
    raise SystemExit('confirmZeroQuantities anchor not found')
s = s.replace(anchor, insert + anchor)

p.write_text(s)

b = Path('app/build.gradle')
g = b.read_text().replace('versionCode 30024','versionCode 30025').replace("versionName '3.0.24'","versionName '3.0.25'")
# Support branch state if the prior source version did not persist correctly.
g = g.replace('versionCode 30023','versionCode 30025').replace("versionName '3.0.23'","versionName '3.0.25'")
b.write_text(g)
