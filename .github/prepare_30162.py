from pathlib import Path
import re

base = Path('.github/prepare_30161.py')
exec(compile(base.read_text(), str(base), 'exec'), {'__name__': '__main__', '__file__': str(base)})

def sub(path, old, new, count=0):
    p=Path(path); s=p.read_text(); n=s.count(old)
    if n==0: raise SystemExit('3.0.162 target missing in '+path+': '+old[:80])
    if count and n!=count: raise SystemExit('3.0.162 target count '+str(n)+' in '+path+': '+old[:80])
    p.write_text(s.replace(old,new,count or -1))

sub('app/build.gradle','versionCode 30161','versionCode 30162',1)
sub('app/build.gradle',"versionName '3.0.161'","versionName '3.0.162'",1)
sub('app/src/main/AndroidManifest.xml','iCE Onhand 3.0.161','iCE Onhand 3.0.162',1)
sub('app/src/main/java/com/iceinventory/onhand/MainActivity.java','Onhand Inventory 3.0.161','Onhand Inventory 3.0.162',1)

# One canonical representation keeps whole counts clean (1, not 1.0) while retaining fractions.
Path('app/src/main/java/com/iceinventory/onhand/QuantityMath.java').write_text('''package com.iceinventory.onhand;
import java.math.BigDecimal;
public final class QuantityMath {
 private QuantityMath(){}
 public static double parse(String value){double v=Double.parseDouble(value.replace(",","").trim());if(Double.isNaN(v)||Double.isInfinite(v))throw new NumberFormatException();return v;}
 public static String format(double value){if(Math.abs(value)<0.000000001)value=0;return BigDecimal.valueOf(value).stripTrailingZeros().toPlainString();}
 public static boolean equal(double a,double b){return Math.abs(a-b)<0.0000001;}
}''')

# Database: SQLite already stores numeric values dynamically; read/write them as REAL throughout.
p=Path('app/src/main/java/com/iceinventory/onhand/InventoryDb.java'); s=p.read_text()
s=s.replace('public int quantity;','public double quantity;').replace('public int quantityDelta;','public double quantityDelta;')
s=s.replace('public int unitTotal;','public double unitTotal;')
s=s.replace('quantity INTEGER NOT NULL DEFAULT 0','quantity REAL NOT NULL DEFAULT 0').replace('quantity_delta INTEGER NOT NULL DEFAULT 0','quantity_delta REAL NOT NULL DEFAULT 0')
s=s.replace('public int quantityForBarcode(', 'public double quantityForBarcode(').replace('c.getInt(0):0','c.getDouble(0):0')
s=re.sub(r'(String description, String price, )int quantity',r'\1double quantity',s)
s=re.sub(r'(String description, )int quantity',r'\1double quantity',s)
s=s.replace('c.getInt(1) + quantity','c.getDouble(1) + quantity')
s=s.replace('long targetId=-1L;int targetQty=0;','long targetId=-1L;double targetQty=0;').replace('targetQty=c.getInt(1)','targetQty=c.getDouble(1)')
s=s.replace('setQuantity(long id, int quantity)','setQuantity(long id, double quantity)').replace('incrementQuantity(long id, int delta)','incrementQuantity(long id, double delta)').replace('String price, int quantity, String location)','String price, double quantity, String location)')
s=s.replace('r.quantity=c.getInt(5)','r.quantity=c.getDouble(5)').replace('String description,int quantityDelta,','String description,double quantityDelta,').replace('h.quantityDelta=c.getInt(4)','h.quantityDelta=c.getDouble(4)')
s=s.replace('int lines=0,units=0;','int lines=0;double units=0;').replace('units=c.getInt(1)','units=c.getDouble(1)').replace('x.unitTotal=c.getInt(5)','x.unitTotal=c.getDouble(5)')
s=s.replace('int delta=c.getInt(3)','double delta=c.getDouble(3)')
p.write_text(s)

# Quantity calculator: decimal key, decimal parsing and double result extras.
p=Path('app/src/main/java/com/iceinventory/onhand/QuantityActivity.java'); s=p.read_text()
s=s.replace('private int total;','private double total;').replace('int current=getIntent().getIntExtra(EXTRA_CURRENT_QTY,0);','double current=getIntent().getDoubleExtra(EXTRA_CURRENT_QTY,0);')
s=s.replace('String.format(Locale.US,"Current Qty: %d",current)','"Current Qty: "+QuantityMath.format(current)')
s=s.replace('TYPE_CLASS_NUMBER);','TYPE_CLASS_NUMBER|android.text.InputType.TYPE_NUMBER_FLAG_DECIMAL);')
s=s.replace('"0","00","=",""','"0","00",".","="')
s=s.replace('private int value(EditText e){','private double value(EditText e){').replace('return s.isEmpty()?0:Integer.parseInt(s);','return s.isEmpty()?0:QuantityMath.parse(s);')
s=s.replace('int a=value(perUnit);\n        int b=value(cases);\n        long result=b>0?(long)a*b:a;\n        if(result>999999999L)result=999999999L;\n        total=(int)result;\n        totalText.setText(String.valueOf(total));\n        addButton.setText("ADD COUNT ("+total+")");','double a=value(perUnit);\n        double b=value(cases);\n        double result=b>0?a*b:a;\n        if(result>999999999d)result=999999999d;\n        total=result;\n        totalText.setText(QuantityMath.format(total));\n        addButton.setText("ADD COUNT ("+QuantityMath.format(total)+")");')
s=s.replace('||"9".equals(key))&&current.length()<9','||"9".equals(key)||".".equals(key))&&current.length()<9')
s=s.replace('target.setText(current+key);','if(".".equals(key)&&current.contains("."))return;\n            target.setText(current+key);')
p.write_text(s)

# Main count entry, confirmation, summaries, editing and exports.
p=Path('app/src/main/java/com/iceinventory/onhand/MainActivity.java'); s=p.read_text()
s=s.replace('qty.setInputType(InputType.TYPE_CLASS_NUMBER);','qty.setInputType(InputType.TYPE_CLASS_NUMBER|InputType.TYPE_NUMBER_FLAG_DECIMAL|InputType.TYPE_NUMBER_FLAG_SIGNED);',1)
s=s.replace('int q;\n        try{q=Integer.parseInt(qText);}', 'double q;\n        try{q=QuantityMath.parse(qText);}')
s=s.replace('int current=db.quantityForBarcode(sessionId,code);','double current=db.quantityForBarcode(sessionId,code);')
old='''        String loc=confirmedLocation;
        db.addLocation(loc);
        db.addOrIncrement(sessionId,code,description.getText().toString(),currentPrice,q,loc);
        lastBarcode=code;
        barcode.setText("");description.setText("");qty.setText("");currentPrice="";
        refreshList();'''
new='''        String loc=confirmedLocation;
        if(Math.abs(q)>300){
            final double entered=q,existing=current;final String saveCode=code,saveLoc=loc,saveDescription=description.getText().toString(),savePrice=currentPrice;
            new AlertDialog.Builder(this).setTitle("VERIFY LARGE QUANTITY")
                .setMessage("You entered "+QuantityMath.format(entered)+" units.\\n\\nBarcode: "+saveCode+"\\nLocation: "+saveLoc+"\\nCurrent total: "+QuantityMath.format(existing)+"\\nNew total: "+QuantityMath.format(existing+entered)+"\\n\\nPlease verify this count before saving.")
                .setNegativeButton("GO BACK",null).setPositiveButton("VERIFY & SAVE",(d,w)->saveEnteredCount(saveCode,saveDescription,savePrice,entered,saveLoc)).show();return;
        }
        saveEnteredCount(code,description.getText().toString(),currentPrice,q,loc);return;'''
if old not in s: raise SystemExit('main save block missing')
s=s.replace(old,new,1)
anchor='    private void refreshLocations() {'
helper='''    private void saveEnteredCount(String code,String desc,String price,double amount,String loc){
        db.addLocation(loc);db.addOrIncrement(sessionId,code,desc,price,amount,loc);lastBarcode=code;
        barcode.setText("");description.setText("");qty.setText("");currentPrice="";refreshList();
        if(continuousPhoneScan){hideKeyboard();barcode.postDelayed(this::scanBarcode,180);}else focusBarcodeWithoutKeyboard();
        noteCountForSafety();setCountingKeyboardMode(false);
    }

'''
s=s.replace(anchor,helper+anchor,1)
# remove now-unreachable old tail left after replaced block
s=s.replace('''        if(continuousPhoneScan){
            hideKeyboard();
            barcode.postDelayed(this::scanBarcode,180);
        } else {
            focusBarcodeWithoutKeyboard();
        }
        noteCountForSafety();
        setCountingKeyboardMode(false);
    }

    private void refreshLocations() {''','''    }

    private void refreshLocations() {''',1)
s=s.replace('int units=0;for(InventoryDb.Row r:allRows)units+=r.quantity;','double units=0;for(InventoryDb.Row r:allRows)units+=r.quantity;').replace('summary.setText(allRows.size()+" item lines  •  "+units+" total units")','summary.setText(allRows.size()+" item lines  •  "+QuantityMath.format(units)+" total units")')
s=s.replace('Integer.compare(b.quantity,a.quantity)','Double.compare(b.quantity,a.quantity)').replace('Integer.compare(a.quantity,b.quantity)','Double.compare(a.quantity,b.quantity)')
s=s.replace('int amount=data.getIntExtra(QuantityActivity.EXTRA_QUANTITY,0);','double amount=data.getDoubleExtra(QuantityActivity.EXTRA_QUANTITY,0);')
s=s.replace('int amount=0;try{amount=Integer.parseInt(String.valueOf(x).trim());}','double amount=0;try{amount=QuantityMath.parse(String.valueOf(x).trim());}').replace('String raw=adjustment.getText().toString().trim();int amount=0;try{amount=Integer.parseInt(raw);}','String raw=adjustment.getText().toString().trim();double amount=0;try{amount=QuantityMath.parse(raw);}')
s=s.replace('int next=r.quantity+amount','double next=r.quantity+amount')
s=s.replace('int qty=r.quantity;','double qty=r.quantity;').replace('int amount;long when;try{amount=Integer.parseInt(c[3].trim());}','double amount;long when;try{amount=QuantityMath.parse(c[3].trim());}')
s=s.replace('int units=0;for(InventoryDb.Row r:rows)units+=r.quantity;','double units=0;for(InventoryDb.Row r:rows)units+=r.quantity;')
s=s.replace('class Area {String name;int total;LinkedHashMap<String,Integer> parts=new LinkedHashMap<>();','class Area {String name;double total;LinkedHashMap<String,Double> parts=new LinkedHashMap<>();').replace('LinkedHashMap<String,Area> areas=new LinkedHashMap<>();int grand=0;','LinkedHashMap<String,Area> areas=new LinkedHashMap<>();double grand=0;')
s=s.replace('java.util.TreeMap<String,Integer> totals=new java.util.TreeMap<>(String.CASE_INSENSITIVE_ORDER);','java.util.TreeMap<String,Double> totals=new java.util.TreeMap<>(String.CASE_INSENSITIVE_ORDER);').replace('int grandTotal=0;','double grandTotal=0;')
s=s.replace('area.parts.getOrDefault(display,0)+r.quantity','area.parts.getOrDefault(display,0d)+r.quantity').replace('totals.getOrDefault(loc,0)+r.quantity','totals.getOrDefault(loc,0d)+r.quantity')
s=s.replace('adjustment.setInputType(InputType.TYPE_CLASS_NUMBER|InputType.TYPE_NUMBER_FLAG_SIGNED);','adjustment.setInputType(InputType.TYPE_CLASS_NUMBER|InputType.TYPE_NUMBER_FLAG_SIGNED|InputType.TYPE_NUMBER_FLAG_DECIMAL);')
s=s.replace('for(Map.Entry<String,Integer> e:area.parts.entrySet())','for(Map.Entry<String,Double> e:area.parts.entrySet())').replace('for(Map.Entry<String,Integer> e:totals.entrySet())','for(Map.Entry<String,Double> e:totals.entrySet())').replace('for(java.util.Map.Entry<String,Integer> e:totals.entrySet())','for(java.util.Map.Entry<String,Double> e:totals.entrySet())').replace('Integer v=totals.get(loc);','Double v=totals.get(loc);')
p.write_text(s)

# Mechanical quantity propagation through adapters, text and Excel reports.
files=['InventoryAdapter.java','TabTextUtils.java','BatchExportText.java','CsvUtils.java']
for f in files:
 p=Path('app/src/main/java/com/iceinventory/onhand/'+f); x=p.read_text()
 x=x.replace('String.format(Locale.US,"Qty: %d",r.quantity)','"Qty: "+QuantityMath.format(r.quantity)')
 x=x.replace('b.append(r.quantity)','b.append(QuantityMath.format(r.quantity))').replace('.append(r.quantity)', '.append(QuantityMath.format(r.quantity))')
 x=x.replace('qty=Integer.parseInt(q.replace(",","").trim())','qty=QuantityMath.parse(q)')
 x=x.replace('int qty=0','double qty=0')
 p.write_text(x)

p=Path('app/src/main/java/com/iceinventory/onhand/SimpleXlsxWriter.java'); s=p.read_text().replace('numberCell(StringBuilder x,String ref,int value)','numberCell(StringBuilder x,String ref,double value)'); p.write_text(s)

# Combined reports and monthly exports use doubles and tolerant total verification.
for name in ['BatchMergeActivity.java','MonthlyInventoryActivity.java','MonthlyClientXlsxWriter.java','MonthlyCategoryXlsxWriter.java','ProfessionalCombinedXlsxWriter.java']:
 p=Path('app/src/main/java/com/iceinventory/onhand/'+name); s=p.read_text()
 s=re.sub(r'\blong quantity\b','double quantity',s)
 s=s.replace('Long.parseLong(', 'QuantityMath.parse(').replace('Long.compare(', 'Double.compare(')
 s=s.replace('Math.addExact(total.quantity,row.quantity)','total.quantity+row.quantity').replace('Math.addExact(grand,total.quantity)','grand+total.quantity').replace('Math.addExact(total,row.quantity)','total+row.quantity')
 s=s.replace('Math.addExact(row.quantity,e.getValue())','row.quantity+e.getValue()').replace('Math.addExact(clientTotal,r.quantity)','clientTotal+r.quantity').replace('Math.addExact(combinedTotal,e.getValue())','combinedTotal+e.getValue()')
 s=s.replace('Map.Entry<String,Long>','Map.Entry<String,Double>').replace('LinkedHashMap<String,Long>','LinkedHashMap<String,Double>').replace('HashMap<String,Long>','HashMap<String,Double>')
 s=s.replace('long sourceGrandTotal=0,outputTotal=0','double sourceGrandTotal=0,outputTotal=0').replace('long sourceTotal=0,combinedTotal=0,clientTotal=0','double sourceTotal=0,combinedTotal=0,clientTotal=0')
 s=s.replace('long q;try{q=QuantityMath.parse(raw);','double q;try{q=QuantityMath.parse(raw);').replace('long q;try{q=QuantityMath.parse(v[qi].replace(",","").trim());','double q;try{q=QuantityMath.parse(v[qi]);')
 s=s.replace('Math.addExact(t.quantity,q)','t.quantity+q').replace('Math.addExact(sourceGrandTotal,q)','sourceGrandTotal+q').replace('Math.addExact(stat.quantity,q)','stat.quantity+q').replace('Math.addExact(sourceTotal,q)','sourceTotal+q')
 s=s.replace('Math.addExact(old==null?0:old,q)','(old==null?0:old)+q').replace('Long old=combined.get(code)','Double old=combined.get(code)')
 s=s.replace('getOrDefault(key,0L)','getOrDefault(key,0d)').replace('getOrDefault(location,0L)','getOrDefault(location,0d)').replace('Math.addExact(userLocationTotals.getOrDefault(key,0d),q)','userLocationTotals.getOrDefault(key,0d)+q').replace('Math.addExact(locationSums.getOrDefault(location,0d),q)','locationSums.getOrDefault(location,0d)+q')
 s=s.replace('Math.addExact(outputTotal,t.quantity)','outputTotal+t.quantity')
 s=s.replace('sourceGrandTotal==outputTotal','QuantityMath.equal(sourceGrandTotal,outputTotal)').replace('sourceTotal==combinedTotal&&combinedTotal==clientTotal','QuantityMath.equal(sourceTotal,combinedTotal)&&QuantityMath.equal(combinedTotal,clientTotal)')
 s=s.replace('public ClientRow(Product product,long quantity)','public ClientRow(Product product,double quantity)').replace('CombinedRow(String a,String b,String c,long d)','CombinedRow(String a,String b,String c,double d)').replace('SourceRow(String a,String b,String c,int d,long e)','SourceRow(String a,String b,String c,int d,double e)')
 s=s.replace('private static void number(StringBuilder b,int c,int r,long value,int style)','private static void number(StringBuilder b,int c,int r,double value,int style)')
 s=s.replace('private static void number(StringBuilder x,int c,int r,long v,int style)','private static void number(StringBuilder x,int c,int r,double v,int style)')
 s=s.replace('private long sourceGrandTotal,outputTotal','private double sourceGrandTotal,outputTotal').replace('private long sourceTotal,combinedTotal,clientTotal','private double sourceTotal,combinedTotal,clientTotal')
 s=s.replace('long sum=0;','double sum=0;').replace('sum=Math.addExact(sum,e.getValue())','sum+=e.getValue()')
 s=s.replace('s.quantity=Math.addExact(s.quantity,q)','s.quantity+=q')
 s=s.replace('int r=1;long grand=0;','int r=1;double grand=0;').replace('int r=1;long total=0;','int r=1;double total=0;')
 s=s.replace('List<CombinedRow> rows,long sourceTotal,long combinedTotal','List<CombinedRow> rows,double sourceTotal,double combinedTotal').replace('sources,int unique,long sourceTotal,long combinedTotal','sources,int unique,double sourceTotal,double combinedTotal')
 s=s.replace('public final long quantity;','public final double quantity;').replace('int rows,long quantity','int rows,double quantity').replace('String price,long quantity','String price,double quantity')
 s=s.replace('List<CombinedRow> combined,\n                             long sourceTotal,long combinedTotal','List<CombinedRow> combined,\n                             double sourceTotal,double combinedTotal').replace('int uniqueBarcodes,long sourceTotal,long combinedTotal','int uniqueBarcodes,double sourceTotal,double combinedTotal')
 s=s.replace('long difference=combinedTotal-sourceTotal','double difference=combinedTotal-sourceTotal').replace('numberCell(StringBuilder x,String ref,long value,int style)','numberCell(StringBuilder x,String ref,double value,int style)')
 p.write_text(s)

checks=['QuantityMath.java','InventoryDb.java','MainActivity.java','QuantityActivity.java']
for f in checks:
 if not Path('app/src/main/java/com/iceinventory/onhand/'+f).exists():raise SystemExit('missing '+f)
print('Prepared iCE OnHand 3.0.162: decimal quantities end-to-end and over-300 verification')
