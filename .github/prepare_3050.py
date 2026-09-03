from pathlib import Path
import runpy

# Preserve every approved 3.0.49 behavior first.
runpy.run_path('.github/prepare_3049.py', run_name='__main__')

# --- MainActivity: distinguish Bluetooth/hardware scanner from the Android soft keyboard.
# Android virtual keyboard KeyEvents use deviceId -1. Some Bluetooth scanner profiles can
# appear as deviceId 0, so accept 0 and above while leaving normal on-screen typing alone.
p=Path('app/src/main/java/com/iceinventory/onhand/MainActivity.java')
s=p.read_text()
old='''        if(event!=null&&event.getAction()==KeyEvent.ACTION_DOWN&&barcode!=null) {\n'''
new='''        if(event!=null&&event.getDeviceId()>=0&&event.getAction()==KeyEvent.ACTION_DOWN&&barcode!=null) {\n'''
if old not in s: raise SystemExit('3.0.50 target missing: scanner condition')
s=s.replace(old,new,1)

# Restore the later approved iCE Inventory scanner logo in the app header.
s=s.replace('R.drawable.ice_onhand_icon','R.drawable.ice_onhand_approved')
p.write_text(s)

# Restore the same approved logo as the Android launcher/application icon.
p=Path('app/src/main/AndroidManifest.xml')
s=p.read_text()
s=s.replace('android:icon="@drawable/ice_onhand_icon"','android:icon="@drawable/ice_onhand_approved"')
p.write_text(s)

print('Prepared iCE Onhand 3.0.50: quantity typing restored + scanner device 0 support + approved iCE Inventory logo')
