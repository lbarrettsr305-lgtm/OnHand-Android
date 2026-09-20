from pathlib import Path

base=Path('.github/prepare_30130.py')
exec(compile(base.read_text(),str(base),'exec'),{'__name__':'__main__','__file__':str(base)})

p=Path('app/build.gradle')
g=p.read_text().replace('versionCode 30130','versionCode 30131',1).replace("versionName '3.0.130'","versionName '3.0.131'",1)
if 'versionCode 30131' not in g: raise SystemExit('3.0.131 Gradle target missing')
p.write_text(g)

p=Path('app/src/main/java/com/iceinventory/onhand/MainActivity.java')
s=p.read_text().replace('Onhand Inventory 3.0.130','Onhand Inventory 3.0.131',1)
if '↓ START HERE — IMPORT' not in s: raise SystemExit('3.0.131 Start button target missing')
s=s.replace('↓ START HERE — IMPORT','↓ START / IMPORT',1)
if 'String[] choices={"Petrosoft Monthly Inventory","LiqPOS Inventory","Standard TXT Inventory"};' not in s: raise SystemExit('3.0.131 import choices target missing')
s=s.replace('String[] choices={"Petrosoft Monthly Inventory","LiqPOS Inventory","Standard TXT Inventory"};',
'''String[] choices={"Petrosoft Monthly Inventory","LiqPOS Inventory","Shared User / Standard TXT File"};''',1)
p.write_text(s)

p=Path('app/src/main/java/com/iceinventory/onhand/MonthlyInventoryActivity.java')
s=p.read_text().replace('4. Share File With All Users','4. Share Count File to Users',1)
p.write_text(s)

p=Path('app/src/main/java/com/iceinventory/onhand/LiqPosInventoryActivity.java')
s=p.read_text().replace('4. Share File With All Users','4. Share Count File to Users',1)
p.write_text(s)

p=Path('app/src/main/java/com/iceinventory/onhand/HelpActivity.java')
s=p.read_text()
s=s.replace('tap ↓ START HERE — IMPORT.','tap ↓ START / IMPORT.',1)
s=s.replace('• Standard TXT Inventory','• Shared User / Standard TXT File',1)
old='''  section("2. Standard TXT Inventory",
   "Use this for a normal tab-delimited OnHand file. Select the file, confirm the store or session name, and verify a few barcodes before beginning the full count.");'''
new='''  section("2. Receiving a Shared Count File",
   "When another user sends you a prepared Petrosoft, LiqPOS, or standard OnHand count file:\\n\\n1. Save or download the shared TXT file on your device.\\n2. Open iCE OnHand.\\n3. Tap ↓ START / IMPORT.\\n4. Choose Shared User / Standard TXT File.\\n5. Select the shared TXT file.\\n6. Confirm the store name at the top.\\n7. Test one barcode, then begin counting.\\n\\nDo not choose Petrosoft Monthly or LiqPOS on a receiving count device. Those choices are for the person preparing the project.");'''
if old not in s: raise SystemExit('3.0.131 Help shared-file target missing')
s=s.replace(old,new,1)
p.write_text(s)

p=Path('app/src/main/AndroidManifest.xml')
m=p.read_text().replace('iCE Onhand 3.0.130','iCE Onhand 3.0.131',1)
if 'iCE Onhand 3.0.131' not in m: raise SystemExit('3.0.131 manifest version missing')
p.write_text(m)

print('Prepared iCE Onhand 3.0.131: explicit shared-user TXT import flow')
