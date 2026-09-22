from pathlib import Path

base=Path('.github/prepare_30151.py')
exec(compile(base.read_text(),str(base),'exec'),{'__name__':'__main__','__file__':str(base)})

def rep(path,old,new):
    p=Path(path);s=p.read_text()
    if s.count(old)!=1:raise SystemExit('3.0.152 expected one target: '+old[:120])
    p.write_text(s.replace(old,new,1))

rep('app/build.gradle','versionCode 30151','versionCode 30152')
rep('app/build.gradle',"versionName '3.0.151'","versionName '3.0.152'")
rep('app/src/main/AndroidManifest.xml','iCE Onhand 3.0.151','iCE Onhand 3.0.152')
m='app/src/main/java/com/iceinventory/onhand/MainActivity.java'
rep(m,'Onhand Inventory 3.0.151','Onhand Inventory 3.0.152')
rep(m,'private Spinner location;','private Spinner location;\n    private LinearLayout bottomIoBar;\n    private View countActionBar;')
rep(m,
'''            if(continuousPhoneScan&&(keyboardDone||enterKey)){
                hideKeyboard();
                addItem();
                return true;
            }''',
'''            if(keyboardDone||enterKey){
                hideKeyboard();
                addItem();
                return true;
            }''')
rep(m,
'''        qty.setOnTouchListener((v,event)->{
            if(event.getAction()==MotionEvent.ACTION_DOWN){qty.setShowSoftInputOnFocus(true);qty.postDelayed(()->showKeyboard(qty),60);}
            return false;
        });
        qty.setOnFocusChangeListener((v,has)->{if(!has)qty.setShowSoftInputOnFocus(false);});''',
'''        qty.setOnTouchListener((v,event)->{
            if(event.getAction()==MotionEvent.ACTION_DOWN){
                qty.setShowSoftInputOnFocus(true);
                setCountingKeyboardMode(true);
                qty.postDelayed(()->showKeyboard(qty),60);
            }
            return false;
        });
        qty.setOnFocusChangeListener((v,has)->{
            if(!has){qty.setShowSoftInputOnFocus(false);qty.postDelayed(()->setCountingKeyboardMode(false),180);}
        });''')
rep(m,'root.addView(actionBar);','root.addView(actionBar);\n        countActionBar=actionBar;')
rep(m,'LinearLayout io=new LinearLayout(this);io.setOrientation(LinearLayout.HORIZONTAL);io.setPadding(0,dp(4),0,0);',
    'LinearLayout io=new LinearLayout(this);bottomIoBar=io;io.setOrientation(LinearLayout.HORIZONTAL);io.setPadding(0,dp(4),0,0);')
rep(m,'private void adjustQty(int delta) {',
'''private void setCountingKeyboardMode(boolean active){
        if(bottomIoBar!=null)bottomIoBar.setVisibility(active?View.GONE:View.VISIBLE);
        if(active&&countActionBar!=null)countActionBar.postDelayed(()->countActionBar.requestRectangleOnScreen(new android.graphics.Rect(0,0,countActionBar.getWidth(),countActionBar.getHeight()),true),100);
    }

    private void adjustQty(int delta) {''')
rep(m,
'''        } else {
            focusBarcodeWithoutKeyboard();
        }
        noteCountForSafety();
    }''',
'''        } else {
            focusBarcodeWithoutKeyboard();
        }
        noteCountForSafety();
        setCountingKeyboardMode(false);
    }''')
print('Prepared iCE OnHand 3.0.152: keep Add Qty visible above numeric keyboard')
