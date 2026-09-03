from pathlib import Path

p=Path('app/src/main/java/com/iceinventory/onhand/MainActivity.java')
s=p.read_text()

# Main-screen keyboard fix: resize the activity and keep the highlighted item visible
# by temporarily freeing space and scrolling that row to the top while Quantity is focused.
marker='''        io.addView(imp,new LinearLayout.LayoutParams(0,ViewGroup.LayoutParams.WRAP_CONTENT,1)); io.addView(exp,new LinearLayout.LayoutParams(0,ViewGroup.LayoutParams.WRAP_CONTENT,1)); io.setTranslationY(dp(-36)); root.addView(io);\n        setContentView(root);'''
replacement='''        io.addView(imp,new LinearLayout.LayoutParams(0,ViewGroup.LayoutParams.WRAP_CONTENT,1)); io.addView(exp,new LinearLayout.LayoutParams(0,ViewGroup.LayoutParams.WRAP_CONTENT,1)); io.setTranslationY(dp(-36)); root.addView(io);\n\n        getWindow().setSoftInputMode(android.view.WindowManager.LayoutParams.SOFT_INPUT_ADJUST_RESIZE);\n        qty.setOnFocusChangeListener((v,hasFocus)->{\n            reportBar.setVisibility(hasFocus?View.GONE:View.VISIBLE);\n            io.setVisibility(hasFocus?View.GONE:View.VISIBLE);\n            if(hasFocus){\n                list.postDelayed(()->{\n                    int target=-1;\n                    for(int i=0;i<visibleRows.size();i++){ if(visibleRows.get(i).id==highlightedRowId){ target=i; break; } }\n                    if(target>=0) list.setSelectionFromTop(target,0);\n                },220);\n            }\n        });\n        setContentView(root);'''
if marker not in s:
    raise SystemExit('main keyboard/list marker not found')
s=s.replace(marker,replacement,1)
p.write_text(s)

b=Path('app/build.gradle')
g=b.read_text().replace('versionCode 30037','versionCode 30038').replace("versionName '3.0.37'","versionName '3.0.38'")
b.write_text(g)
