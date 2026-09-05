from pathlib import Path
import runpy

# Preserve the exact verified 3.0.80 release first: working Cases calculator,
# current-item-first scan list, TXT/Excel exports, continuous phone camera,
# automatic web product lookup, Google fallback, and protected column setup.
runpy.run_path('.github/prepare_3080_release.py', run_name='__main__')

p=Path('app/src/main/java/com/iceinventory/onhand/MainActivity.java')
s=p.read_text()

def rep(old,new,label):
    global s
    if old not in s:
        raise SystemExit('3.0.81 target missing: '+label)
    s=s.replace(old,new,1)

# In an active PHONE-camera cycle only, the numeric keyboard's Done/Enter action
# saves the existing quantity through the proven addItem() method. addItem()
# already reopens the camera when continuousPhoneScan is true. Bluetooth/manual
# workflows are deliberately unchanged because this listener returns false when
# continuousPhoneScan is not active.
old='''        qty.setInputType(InputType.TYPE_CLASS_NUMBER);styleEntry(qty);installScannerImeWatcher(qty);\n'''
new='''        qty.setInputType(InputType.TYPE_CLASS_NUMBER);styleEntry(qty);installScannerImeWatcher(qty);\n        qty.setImeOptions(android.view.inputmethod.EditorInfo.IME_ACTION_DONE);\n        qty.setOnEditorActionListener((v,actionId,event)->{\n            boolean keyboardDone=actionId==android.view.inputmethod.EditorInfo.IME_ACTION_DONE;\n            boolean enterKey=event!=null&&event.getAction()==KeyEvent.ACTION_DOWN&&\n                    (event.getKeyCode()==KeyEvent.KEYCODE_ENTER||event.getKeyCode()==KeyEvent.KEYCODE_NUMPAD_ENTER);\n            if(continuousPhoneScan&&(keyboardDone||enterKey)){\n                hideKeyboard();\n                addItem();\n                return true;\n            }\n            return false;\n        });\n'''
rep(old,new,'phone quantity Done action')

rep('TextView app=text("Onhand Inventory 3.0.80",19,Color.WHITE,true);',
    'TextView app=text("Onhand Inventory 3.0.81",19,Color.WHITE,true);','visible version')
p.write_text(s)

p=Path('app/build.gradle')
s=p.read_text().replace('versionCode 30080','versionCode 30081',1).replace("versionName '3.0.80'","versionName '3.0.81'",1)
if 'versionCode 30081' not in s or "versionName '3.0.81'" not in s:
    raise SystemExit('3.0.81 target missing: Gradle version')
p.write_text(s)

p=Path('app/src/main/AndroidManifest.xml')
s=p.read_text().replace('android:label="iCE Onhand 3.0.80"','android:label="iCE Onhand 3.0.81"',1)
if 'android:label="iCE Onhand 3.0.81"' not in s:
    raise SystemExit('3.0.81 target missing: manifest version')
p.write_text(s)

print('Prepared iCE Onhand 3.0.81: phone camera quantity Done saves count and reopens scanner; Bluetooth/manual unchanged')
