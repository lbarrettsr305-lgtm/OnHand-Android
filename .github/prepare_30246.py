#!/usr/bin/env python3
"""Prepare the signed 3.0.246 Petrosoft counter-export release."""
from pathlib import Path
import base64
import io
import tarfile

root = Path(__file__).resolve().parents[1]
archive_path = root / ".github/onhand-30246-source.tgz.b64"
raw = base64.b64decode(archive_path.read_text().strip(), validate=True)
with tarfile.open(fileobj=io.BytesIO(raw), mode="r:gz") as archive:
    members = [m for m in archive.getmembers() if m.name.startswith("app/")]
    if not members or any(Path(m.name).is_absolute() or ".." in Path(m.name).parts for m in members):
        raise SystemExit("Invalid bundled app source")
    archive.extractall(root, members=members, filter="data")

def replace_once(path, old, new, label):
    data = path.read_text()
    count = data.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected one anchor, found {count}")
    path.write_text(data.replace(old, new, 1))

replace_once(root / "app/build.gradle", "versionCode 30245", "versionCode 30246", "Gradle version code")
replace_once(root / "app/build.gradle", "versionName '3.0.245'", "versionName '3.0.246'", "Gradle version name")
replace_once(root / "app/src/main/AndroidManifest.xml", "iCE Onhand 3.0.245", "iCE Onhand 3.0.246", "App label")
replace_once(root / "app/src/main/java/com/iceinventory/onhand/MainActivity.java",
             "Onhand Inventory 3.0.245", "Onhand Inventory 3.0.246", "Main screen version")
activity = (root / "app/src/main/java/com/iceinventory/onhand/MonthlyInventoryActivity.java").read_text()
if "3. CREATE COUNT FILE FOR COUNTERS" not in activity or "EXPORT / SHARE COUNT FILE TO COUNTERS" not in activity:
    raise SystemExit("Petrosoft direct counter export flow is missing")
if "Test Scan on This Device" in activity or "confirmTestScan()" in activity:
    raise SystemExit("Obsolete Petrosoft test-scan flow remains")
print("Prepared iCE Onhand 3.0.246 Petrosoft counter export")
