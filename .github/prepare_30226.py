#!/usr/bin/env python3
from pathlib import Path
import runpy

root = Path(__file__).resolve().parent.parent
workflow = root / ".github/workflows/build-apk.yml"

# The preceding release script expects the workflow to name 3.0.225.
w = workflow.read_text()
for new, old, expected in [
    ("Prepare and verify 3.0.226 auto-increment scan feedback", "Prepare and verify 3.0.225 start count import label", 1),
    (".github/prepare_30226.py", ".github/prepare_30225.py", 1),
    ("iCE-Onhand-Inventory-3.0.226", "iCE-Onhand-Inventory-3.0.225", 4),
]:
    if w.count(new) != expected:
        raise SystemExit("3.0.226 workflow marker missing or ambiguous: " + new)
    w = w.replace(new, old)
workflow.write_text(w)

runpy.run_path(str(root / ".github/prepare_30225.py"), run_name="__main__")

w = workflow.read_text()
for old, new, expected in [
    ("Prepare and verify 3.0.225 start count import label", "Prepare and verify 3.0.226 auto-increment scan feedback", 1),
    (".github/prepare_30225.py", ".github/prepare_30226.py", 1),
    ("iCE-Onhand-Inventory-3.0.225", "iCE-Onhand-Inventory-3.0.226", 4),
]:
    if w.count(old) != expected:
        raise SystemExit("3.0.225 workflow marker missing or ambiguous: " + old)
    w = w.replace(old, new)
workflow.write_text(w)

gradle = root / "app/build.gradle"
g = gradle.read_text()
if g.count("versionCode 30225") != 1 or g.count("versionName '3.0.225'") != 1:
    raise SystemExit("3.0.225 Gradle version missing or ambiguous")
g = g.replace("versionCode 30225", "versionCode 30226", 1)
g = g.replace("versionName '3.0.225'", "versionName '3.0.226'", 1)
gradle.write_text(g)

manifest = root / "app/src/main/AndroidManifest.xml"
m = manifest.read_text()
if m.count("iCE Onhand 3.0.225") != 1:
    raise SystemExit("3.0.225 manifest label missing or ambiguous")
manifest.write_text(m.replace("iCE Onhand 3.0.225", "iCE Onhand 3.0.226", 1))

main = root / "app/src/main/java/com/iceinventory/onhand/MainActivity.java"
s = main.read_text()
if s.count("Onhand Inventory 3.0.225") != 1:
    raise SystemExit("3.0.225 home version label missing or ambiguous")
s = s.replace("Onhand Inventory 3.0.225", "Onhand Inventory 3.0.226", 1)

# Automatic Increment Count was added after the earlier scan-feedback fix.
# Its early-return path bypassed useSavedBarcodeMatch(), so successful auto-add
# scans did not beep or vibrate. Trigger feedback only when the increment
# actually runs, preserving the max-quantity confirmation behavior.
old = '''                Runnable increment=()->{
                    db.addOrIncrement(sessionId,code,existing.description,existing.price,1,activeLocation);
                    lastBarcode=code;'''
new = '''                Runnable increment=()->{
                    scanFeedback();
                    db.addOrIncrement(sessionId,code,existing.description,existing.price,1,activeLocation);
                    lastBarcode=code;'''
if s.count(old) != 1:
    raise SystemExit("Automatic Increment Count success block missing or ambiguous")
s = s.replace(old, new, 1)
main.write_text(s)

checks = {
    "version": "versionName '3.0.226'" in g,
    "manifest": "iCE Onhand 3.0.226" in manifest.read_text(),
    "visible version": "Onhand Inventory 3.0.226" in s,
    "auto-increment feedback": "Runnable increment=()->{\n                    scanFeedback();" in s,
    "strong beep retained": "AudioManager.STREAM_MUSIC,100" in s,
    "strong vibration retained": "new long[]{0,80,45,80}" in s,
    "vibrate permission retained": "android.permission.VIBRATE" in manifest.read_text(),
    "workflow": ".github/prepare_30226.py" in workflow.read_text() and "3.0.226" in workflow.read_text(),
}
failed = [name for name, passed in checks.items() if not passed]
if failed:
    raise SystemExit("3.0.226 validation failed: " + ", ".join(failed))
print("Prepared iCE OnHand 3.0.226: successful Automatic Increment Count scans beep and vibrate.")
