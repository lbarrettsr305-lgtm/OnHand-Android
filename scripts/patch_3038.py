from pathlib import Path

p=Path('app/src/main/java/com/iceinventory/onhand/MainActivity.java')
s=p.read_text()
changed=False

# Keep the activity resized when the Samsung numeric keyboard opens, and bring the
# highlighted inventory row into view whenever Quantity receives focus.
set_content='        setContentView(root);'
if 'private void scrollHighlightedIntoView()' not in s:
    build_start=s.find('    private void buildUi() {')
    build_end=s.find('\n    private ', build_start+10)
    if build_start>=0 and build_end>build_start:
        block=s[build_start:build_end]
        pos=block.rfind(set_content)
        if pos>=0:
            replacement='''        qty.setOnFocusChangeListener((v,hasFocus)->{
            if(hasFocus){
                qty.postDelayed(this::scrollHighlightedIntoView,180);
                qty.postDelayed(this::scrollHighlightedIntoView,420);
                qty.postDelayed(this::scrollHighlightedIntoView,700);
            }
        });
        getWindow().setSoftInputMode(android.view.WindowManager.LayoutParams.SOFT_INPUT_ADJUST_RESIZE);
        setContentView(root);'''
            block=block[:pos]+block[pos:].replace(set_content,replacement,1)
            s=s[:build_start]+block+s[build_end:]
            changed=True

helper_anchor='    private SharedPreferences prefs(){'
if helper_anchor in s and 'private void scrollHighlightedIntoView()' not in s:
    helper='''    private void scrollHighlightedIntoView() {
        if(list==null || highlightedRowId<0 || visibleRows.isEmpty()) return;
        for(int i=0;i<visibleRows.size();i++){
            if(visibleRows.get(i).id==highlightedRowId){
                final int position=i;
                list.post(() -> list.setSelectionFromTop(Math.max(0,position),0));
                return;
            }
        }
    }

'''
    s=s.replace(helper_anchor,helper+helper_anchor,1)
    changed=True

if not changed or 'private void scrollHighlightedIntoView()' not in s:
    raise SystemExit('3.0.38 keyboard visibility patch could not be applied')

p.write_text(s)

b=Path('app/build.gradle')
g=b.read_text().replace('versionCode 30037','versionCode 30038').replace("versionName '3.0.37'","versionName '3.0.38'")
b.write_text(g)
