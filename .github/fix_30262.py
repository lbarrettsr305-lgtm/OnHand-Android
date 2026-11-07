"""Restore automatic internet lookup before the description fallback."""
from pathlib import Path
p=Path("app/src/main/java/com/iceinventory/onhand/MainActivity.java")
s=p.read_text()
old='String mode=isStoreSetupMode()?"manual":getUnknownBarcodeMode();'
assert s.count(old)==1,"Unexpected unknown-item routing"
p.write_text(s.replace(old,'String mode=isStoreSetupMode()?"search":getUnknownBarcodeMode();',1))
p=Path("app/build.gradle")
s=p.read_text()
assert "versionCode 30261" in s and "versionName '3.0.261'" in s
p.write_text(s.replace("versionCode 30261","versionCode 30262").replace("versionName '3.0.261'","versionName '3.0.262'"))
print("Applied 3.0.262: unknown setup items search online automatically; no-match fallback opens Description.")
