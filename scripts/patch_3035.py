from pathlib import Path

p=Path('app/src/main/java/com/iceinventory/onhand/MainActivity.java')
s=p.read_text()

# Add built-in installation/update guidance so users can quickly fix Android APK handler issues.
old='''        group.check("ignore".equals(mode)?501:("search".equals(mode)?502:500)); box.addView(group);'''
new='''        group.check("ignore".equals(mode)?501:("search".equals(mode)?502:500)); box.addView(group);
        Button installHelp=button("Installation / Update Help"); installHelp.setPadding(dp(10),dp(8),dp(10),dp(8));
        installHelp.setOnClickListener(v->new AlertDialog.Builder(this)
                .setTitle("Install or update iCE Onhand")
                .setMessage("1. Open the downloaded .apk file with Android Package Installer.\\n\\n2. If Files, My Files, Chrome, or another app opens it incorrectly, go to Settings > Apps > that app > Set as default and clear its defaults, then tap the APK again.\\n\\n3. If Android blocks installation, allow 'Install unknown apps' for the file manager or browser you used to download it.\\n\\n4. For normal updates, install the new APK directly over the existing iCE Onhand app. Do not uninstall first unless specifically instructed, so your local inventory data stays in place.\\n\\nAll official iCE Onhand updates use the same permanent signing identity.")
                .setPositiveButton("OK",null).show());
        box.addView(installHelp);'''
if old not in s: raise SystemExit('Options group insertion point not found')
s=s.replace(old,new,1)
p.write_text(s)

b=Path('app/build.gradle')
g=b.read_text().replace('versionCode 30034','versionCode 30035').replace("versionName '3.0.34'","versionName '3.0.35'")
b.write_text(g)
