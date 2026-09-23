from pathlib import Path

base = Path('.github/prepare_30152.py')
exec(compile(base.read_text(), str(base), 'exec'), {'__name__': '__main__', '__file__': str(base)})


def rep(path, old, new):
    p = Path(path)
    s = p.read_text()
    if s.count(old) != 1:
        raise SystemExit('3.0.153 expected one target: ' + old[:120])
    p.write_text(s.replace(old, new, 1))


rep('app/build.gradle', 'versionCode 30152', 'versionCode 30153')
rep('app/build.gradle', "versionName '3.0.152'", "versionName '3.0.153'")
rep('app/src/main/AndroidManifest.xml', 'iCE Onhand 3.0.152', 'iCE Onhand 3.0.153')
rep(
    'app/src/main/AndroidManifest.xml',
    '''        <activity
            android:name=".MainActivity"
            android:exported="true"
            android:screenOrientation="unspecified">''',
    '''        <activity
            android:name=".MainActivity"
            android:exported="true"
            android:screenOrientation="unspecified"
            android:windowSoftInputMode="stateAlwaysHidden|adjustResize">''')

m = 'app/src/main/java/com/iceinventory/onhand/MainActivity.java'
rep(m, 'Onhand Inventory 3.0.152', 'Onhand Inventory 3.0.153')
rep(
    m,
    '''    private void setCountingKeyboardMode(boolean active){
        if(bottomIoBar!=null)bottomIoBar.setVisibility(active?View.GONE:View.VISIBLE);
        if(active&&countActionBar!=null)countActionBar.postDelayed(()->countActionBar.requestRectangleOnScreen(new android.graphics.Rect(0,0,countActionBar.getWidth(),countActionBar.getHeight()),true),100);
    }''',
    '''    private void revealCountActionBar(){
        if(countActionBar==null)return;
        countActionBar.requestRectangleOnScreen(
                new android.graphics.Rect(0,0,countActionBar.getWidth(),countActionBar.getHeight()),true);
    }

    private void setCountingKeyboardMode(boolean active){
        if(bottomIoBar!=null)bottomIoBar.setVisibility(active?View.GONE:View.VISIBLE);
        if(active&&countActionBar!=null){
            // Samsung keyboards finish resizing after their toolbar and number pad animate in.
            // Re-request the ADD QTY row after each stage so it stays fully above the keyboard.
            countActionBar.postDelayed(this::revealCountActionBar,120);
            countActionBar.postDelayed(this::revealCountActionBar,350);
            countActionBar.postDelayed(this::revealCountActionBar,700);
        }
    }''')

print('Prepared iCE OnHand 3.0.153: keep ADD QTY visible after Samsung keyboard finishes opening')
