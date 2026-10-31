#!/usr/bin/env python3
"""Prepare signed 3.0.248 with Master package import and activation fixes."""
from pathlib import Path
import base64
import io
import tarfile

root = Path(__file__).resolve().parents[1]
archive_path = root / ".github/onhand-30248-source.tgz.b64"
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

replace_once(root / "app/build.gradle", "versionCode 30245", "versionCode 30248", "Gradle version code")
replace_once(root / "app/build.gradle", "versionName '3.0.245'", "versionName '3.0.248'", "Gradle version name")
replace_once(root / "app/src/main/AndroidManifest.xml", "iCE Onhand 3.0.245", "iCE Onhand 3.0.248", "App label")
main = root / "app/src/main/java/com/iceinventory/onhand/MainActivity.java"
replace_once(main, "Onhand Inventory 3.0.245", "Onhand Inventory 3.0.248", "Main screen version")
source = main.read_text()
if source.count("offerMasterCandidateActivation();") != 1:
    raise SystemExit("Master activation prompt is not called after import")
if 'if(firstLine.startsWith("#ICE_ONHAND_PROJECT\\t"))' not in source:
    raise SystemExit("Project metadata line is not skipped during import")
print("Prepared iCE Onhand 3.0.248 Master recovery")
