from pathlib import Path

p=Path('app/src/main/java/com/iceinventory/onhand/MainActivity.java')
s=p.read_text()
old='Button add=button("Add Count"); add.setOnClickListener(v->addItem());'
new='Button add=button("Add Count"); add.setTextColor(Color.WHITE); add.setTypeface(Typeface.create("sans-serif",Typeface.BOLD)); add.setTextSize(17); add.setBackgroundColor(Color.rgb(25,118,210)); add.setPadding(dp(12),dp(10),dp(12),dp(10)); add.setOnClickListener(v->addItem());'
if old not in s: raise SystemExit('Add Count button block not found')
s=s.replace(old,new,1)
p.write_text(s)

b=Path('app/build.gradle')
g=b.read_text().replace('versionCode 30031','versionCode 30032').replace("versionName '3.0.31'","versionName '3.0.32'")
b.write_text(g)
