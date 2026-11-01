#!/usr/bin/env python3
"""Prepare OnHand 3.0.251 with inventory regression protections."""
from pathlib import Path
import base64
import io
import tarfile

root = Path(__file__).resolve().parents[1]
# Include legacy numeric shelf-location prefixes in the live cigarette total.
# Rebuild step remains here so this branch runs the corrected verifier.
archive_path = root / ".github/onhand-30248-source.tgz.b64"
raw = base64.b64decode("".join(archive_path.read_text().split()), validate=True)
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

app = root / "app"
main = app / "src/main/java/com/iceinventory/onhand/MainActivity.java"
batch = app / "src/main/java/com/iceinventory/onhand/BatchQuantityReportActivity.java"
qty = app / "src/main/java/com/iceinventory/onhand/QuantityMath.java"

replace_once(app / "build.gradle", "versionCode 30245", "versionCode 30251", "Gradle version code")
replace_once(app / "build.gradle", "versionName '3.0.245'", "versionName '3.0.251'", "Gradle version name")
replace_once(app / "src/main/AndroidManifest.xml", "iCE Onhand 3.0.245", "iCE Onhand 3.0.251", "App label")
replace_once(main, "Onhand Inventory 3.0.245", "Onhand Inventory 3.0.251", "Main screen version")

location_map = '''package com.iceinventory.onhand;

import java.util.Locale;

/** Store-scoped location UPCs. Preserve the entire scanned code and show its label. */
public final class LocationBarcodeMap {
    private LocationBarcodeMap() {}
    private static final String[][] CHEV2620 = {
        {"50-50","COOLER DOORS"}, {"50-01","COOLER DOORS FRONT"},
        {"70-70","COOLER-INSIDE"}, {"221-221","CIG SHELF-1"},
        {"222-222","CIG SHELF-2"}, {"223-223","CIG SHELF-3"},
        {"224-224","CIG SHELF-4"}, {"225-225","CIG SHELF-5"},
        {"225-226","CIG SHELF-6"}, {"225-227","CIG SHELF-7"},
        {"225-228","CIG SHELF-8"}, {"11-11","AISLE-1"},
        {"45-44","BACKWALL-BEVERAGE"}, {"91-11","CHECKOUT-FRONT"},
        {"91-22","CHECKOUT-912LEFT"}, {"91-33","CHECKOUT-913BACK"},
        {"91-44","CHECKOUT-914RIGHT"}, {"91-55","CHECKOUT-915CENTER"},
        {"91-1010","CHECKOUT-9110MAIN LOC"}, {"91-1111","CHECKOUT-9111OVER HEAD"},
        {"91-1313","CHECKOUT-9113UNDER STOCK"}, {"5110","DISPLAY-FLOOR"}
    };
    public static boolean isChevron2620(String store) {
        String s=store==null?"":store.toUpperCase(Locale.US).replaceAll("[^A-Z0-9]", "");
        return s.contains("CHEV2620") || s.contains("CHEVRON2620");
    }
    public static String description(String store,String code) {
        if(!isChevron2620(store)||code==null)return "";
        String c=code.trim();
        for(String[] m:CHEV2620)if(m[0].equalsIgnoreCase(c))return m[1];
        return "";
    }
    public static String barcode(String store,String description) {
        if(!isChevron2620(store)||description==null)return "";
        for(String[] m:CHEV2620)if(m[1].equalsIgnoreCase(description.trim()))return m[0];
        return "";
    }
    public static boolean isTruncatedCode(String store,String code) {
        if(!isChevron2620(store)||code==null)return false;
        String c=code.trim();
        if(c.isEmpty())return false;
        for(String[] m:CHEV2620)if(m[0].startsWith(c+"-"))return true;
        return false;
    }
}
'''
(app / "src/main/java/com/iceinventory/onhand/LocationBarcodeMap.java").write_text(location_map)

cig_rules = '''package com.iceinventory.onhand;

import java.util.Locale;

/** Classification shared by the live Cigarettes counter and regression tests. */
public final class CigaretteCountRules {
    private CigaretteCountRules() {}
    public static boolean isCigarette(String category,String location) {
        String c=category==null?"":category.trim().toUpperCase(Locale.US);
        String l=location==null?"":location.trim().toUpperCase(Locale.US);
        // Older builds saved shelf UPCs as their first numeric segment (e.g. 221-221 -> 221).
        // Every listed 221-225 prefix identifies one of the cigarette shelf locations.
        boolean legacyCigShelf = l.matches("(?i)^(221|222|223|224|225)$")
                || l.matches("(?i)^22[1-5]-22[1-8]$");
        return c.contains("CIGARETTE") || c.equals("CIG") || c.startsWith("CIG ")
                || l.startsWith("CIG SHELF") || l.startsWith("CIGARETTE SHELF")
                || legacyCigShelf;
    }
}
'''
(app / "src/main/java/com/iceinventory/onhand/CigaretteCountRules.java").write_text(cig_rules)

batch_name = '''package com.iceinventory.onhand;

import java.util.regex.Matcher;
import java.util.regex.Pattern;

/** Stable counter extraction for names such as Store_Date_JoseFad-01.txt. */
public final class BatchFilename {
    private BatchFilename() {}
    public static String user(String file) {
        String n=file==null?"":file.replaceFirst("(?i)\\\\.(txt|csv|xlsx)$","");
        Matcher legacy=Pattern.compile("(?i)^count(.+?)[-_]?batch[- ]*\\\\d+$").matcher(n);
        if(legacy.matches())return legacy.group(1);
        Matcher m=Pattern.compile("(?i).*[-_]([a-z][a-z0-9]*)[-_](?:batch[- ]*)?\\\\d{1,3}$").matcher(n);
        if(m.matches())return m.group(1);
        return n;
    }
}
'''
(app / "src/main/java/com/iceinventory/onhand/BatchFilename.java").write_text(batch_name)

# Keep the current case-entry flow, but centralize the calculation so it is tested.
replace_once(qty, " public static boolean equal(double a,double b){return Math.abs(a-b)<0.0000001;}\n", " public static double multiplyCases(double unitsPerCase,double cases){\n  if(!Double.isFinite(unitsPerCase)||!Double.isFinite(cases)||unitsPerCase<0||cases<0)throw new IllegalArgumentException(\"Case quantities must be finite and nonnegative\");\n  return unitsPerCase*cases;\n }\n public static boolean equal(double a,double b){return Math.abs(a-b)<0.0000001;}\n", "Case calculation helper")
replace_once(app / "src/main/java/com/iceinventory/onhand/QuantityActivity.java", "double result=b>0?a*b:a;", "double result=b>0?QuantityMath.multiplyCases(a,b):a;", "Case entry calculation")

# Resolve mapped locations before item lookup, and show the barcode with its description.
replace_once(main, "String mappedLocation=victoriaLocationDescription(rawCode);", "String mappedLocation=locationDescriptionForBarcode(rawCode);", "Scanned location lookup")
replace_once(main, """        String value=raw==null?"":raw.trim();
        if(value.isEmpty()||value.matches("(?i)^Aisle\\\\s*$"))return "";""", """        String value=raw==null?"":raw.trim();
        if(value.isEmpty()||value.matches("(?i)^Aisle\\\\s*$"))return "";
        String mapped=locationDescriptionForBarcode(value);
        if(!mapped.isEmpty())return mapped;""", "Main location normalization")
replace_once(main, """    private void submitCountingLocation(String name){
        String n=name==null?"":name.trim();
        if(n.isEmpty()){toast("Choose or scan a location first");return;}""", """    private void submitCountingLocation(String name){
        String n=name==null?"":name.trim();
        String mapped=locationDescriptionForBarcode(n);
        if(!mapped.isEmpty())n=mapped;
        if(n.isEmpty()){toast("Choose or scan a location first");return;}""", "Exact location scan mapping")
replace_once(main, """        if(isVictoriaCoffeeInventory()){
            String mapped=victoriaLocationDescription(scanned);
            if(!mapped.isEmpty()){
                submitCountingLocation(mapped);return;
            }
            String exact=canonicalVictoriaSpecialLocation(scanned);""", """        String mapped=locationDescriptionForBarcode(scanned);
        if(!mapped.isEmpty()){
            submitCountingLocation(mapped);return;
        }
        if(isVictoriaCoffeeInventory()){
            String exact=canonicalVictoriaSpecialLocation(scanned);""", "Main location barcode submission")
replace_once(main, """    private String victoriaLocationUpc(String description){
        if(!isVictoriaCoffeeInventory()||description==null)return "";
        for(String[] mapping:victoriaLocationMappings())
            if(mapping[1].equalsIgnoreCase(description.trim()))return mapping[0];
        return "";
    }
""", """    private String victoriaLocationUpc(String description){
        if(!isVictoriaCoffeeInventory()||description==null)return "";
        for(String[] mapping:victoriaLocationMappings())
            if(mapping[1].equalsIgnoreCase(description.trim()))return mapping[0];
        return "";
    }

    private String locationDescriptionForBarcode(String code){
        String victoria=victoriaLocationDescription(code);
        if(!victoria.isEmpty())return victoria;
        return LocationBarcodeMap.description(sessionName,code);
    }

    private String locationBarcodeForDescription(String description){
        String victoria=victoriaLocationUpc(description);
        if(!victoria.isEmpty())return victoria;
        return LocationBarcodeMap.barcode(sessionName,description);
    }
""", "Shared location barcode helpers")
replace_once(main, """        if(currentLocationBanner!=null)currentLocationBanner.setText("CURRENT LOCATION\\n"+
                (confirmedLocationSession==sessionId&&!confirmedLocation.isEmpty()?(isMainOnlyLocation(confirmedLocation)?"MAIN ONLY — ":"")+confirmedLocation.toUpperCase(java.util.Locale.US):"NOT SET"));""", """        if(currentLocationBanner!=null){
            String label="NOT SET";
            if(confirmedLocationSession==sessionId&&!confirmedLocation.isEmpty()){
                String code=locationBarcodeForDescription(confirmedLocation);
                String description=confirmedLocation.toUpperCase(java.util.Locale.US);
                label=(isMainOnlyLocation(confirmedLocation)?"MAIN ONLY — ":"")+(code.isEmpty()?description:code+" — "+description);
            }
            currentLocationBanner.setText("CURRENT LOCATION\\n"+label);
        }""", "Location screen label")
replace_once(main, "if(category.contains(\"CIGARETTE\")||(category.isEmpty()&&rowLocation.startsWith(\"CIG SHELF\")))cigarettes+=r.quantity;", "if(CigaretteCountRules.isCigarette(category,rowLocation))cigarettes+=r.quantity;", "Cigarette quantity classification")

# The exported counter filename ends in -01, not always -Batch01; recover the actual counter name.
replace_once(batch, """    private static String userFromName(String file){
        String n=file.replaceFirst("(?i)\\\\.(txt|csv)$","");
        java.util.regex.Matcher m=java.util.regex.Pattern.compile("(?i).*[-_]([a-z0-9]+)[-_]batch[ -]*\\\\d+$").matcher(n);
        if(m.matches())return m.group(1);
        m=java.util.regex.Pattern.compile("(?i)^count(.+?)[-_]?batch[ -]*\\\\d+$").matcher(n);
        if(m.matches())return m.group(1);
        return n;
    }""", """    static String userFromName(String file){return BatchFilename.user(file);}""", "Batch filename user parsing")
replace_once(batch, """                    String loc=field(f,li);
                    if(loc.isEmpty()){loc="MISSING LOCATION";b.missing++;}
                    b.rows++;b.qty+=quantity;""", """                    String loc=field(f,li);
                    if(loc.isEmpty()){loc="MISSING LOCATION";b.missing++;}
                    else {
                        String mapped=LocationBarcodeMap.description(store,loc);
                        if(!mapped.isEmpty())loc=mapped;
                        else if(LocationBarcodeMap.isTruncatedCode(store,loc)){
                            loc="UNRESOLVED LOCATION CODE "+loc;
                            b.missing++;
                        }
                    }
                    b.rows++;b.qty+=quantity;""", "Batch location audit mapping")

# Unit tests lock the previously working case multiply and the new location/user parsing.
build = app / "build.gradle"
g=build.read_text()
if "testImplementation 'junit:junit:4.13.2'" not in g:
    g=g.replace("    implementation 'androidx.camera:camera-view:1.4.2'\n", "    implementation 'androidx.camera:camera-view:1.4.2'\n    testImplementation 'junit:junit:4.13.2'\n")
    build.write_text(g)
tests = app / "src/test/java/com/iceinventory/onhand/InventoryRegressionTest.java"
tests.parent.mkdir(parents=True,exist_ok=True)
tests.write_text('''package com.iceinventory.onhand;\n\nimport org.junit.Test;\nimport static org.junit.Assert.*;\n\npublic class InventoryRegressionTest {\n    @Test public void caseMultiplierKeepsWorkingCalculation(){\n        assertEquals(200d,QuantityMath.multiplyCases(10d,20d),0.000001);\n        assertEquals(240d,QuantityMath.multiplyCases(24d,10d),0.000001);\n    }\n    @Test public void fiveDigitLocationSuffixIsPreservedAndMapped(){\n        assertEquals("COOLER DOORS",LocationBarcodeMap.description("CHEV2620","50-50"));\n        assertEquals("50-50",LocationBarcodeMap.barcode("CHEV2620","COOLER DOORS"));\n        assertEquals("CHECKOUT-9110MAIN LOC",LocationBarcodeMap.description("CHEV2620","91-1010"));\n        assertTrue(LocationBarcodeMap.isTruncatedCode("CHEV2620","91"));\n    }\n    @Test public void cigaretteShelfCountsEvenWhenCategoryIsPopulated(){\n        assertTrue(CigaretteCountRules.isCigarette("Tobacco","Cig Shelf-3"));\n        assertTrue(CigaretteCountRules.isCigarette("Cigarettes","Checkout"));\n        assertTrue(CigaretteCountRules.isCigarette("","221"));\n        assertTrue(CigaretteCountRules.isCigarette("","224"));\n        assertTrue(CigaretteCountRules.isCigarette("","225"));\n        assertTrue(CigaretteCountRules.isCigarette("","225-228"));\n        assertFalse(CigaretteCountRules.isCigarette("","50"));\n        assertFalse(CigaretteCountRules.isCigarette("Beverages","Cooler Doors"));\n    }\n    @Test public void batchFilenameReportsCounterName(){\n        assertEquals("JoseFad",BatchFilename.user("ONHAND CHEV2620_10-30-2026-JoseFad-01.txt"));\n        assertEquals("Lbsr",BatchFilename.user("CHEV2620 10-31-2026-Lbsr-01.txt"));\n        assertEquals("Robert",BatchFilename.user("ON HAND VICTORIA-10-29-2026-Robert-Batch01.txt"));\n    }\n}\n''')

# Add Quick Share support for generated exports.
# Keep the original Downloads and Google Drive export choices in the dialog.
main = app / "src/main/java/com/iceinventory/onhand/MainActivity.java"
dialog_old = """        new AlertDialog.Builder(this).setTitle(exportTitle).setMessage(exportMessage).setView(name)
                .setPositiveButton("Save to Downloads",(d,w)->saveToDownloads(pendingExportExcel?cleanExcelName(name.getText().toString()):(pendingExportInternetOnly?cleanInternetReportName(name.getText().toString()):cleanTextName(name.getText().toString()))))
                .setNeutralButton("Save to Google Drive",(d,w)->startDocumentExport(pendingExportExcel?cleanExcelName(name.getText().toString()):(pendingExportInternetOnly?cleanInternetReportName(name.getText().toString()):cleanTextName(name.getText().toString()))))
                .setNegativeButton("Cancel",null).show();"""
dialog_new = """        LinearLayout exportContent=new LinearLayout(this);exportContent.setOrientation(LinearLayout.VERTICAL);exportContent.setPadding(dp(18),dp(4),dp(18),dp(4));
        exportContent.addView(name,new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT,dp(54)));
        Button shareExport=button("SHARE FILE — QUICK SHARE",2);shareExport.setTypeface(Typeface.DEFAULT,Typeface.BOLD);shareExport.setTextSize(15);
        exportContent.addView(shareExport,new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT,dp(56)));
        AlertDialog exportAlert=new AlertDialog.Builder(this).setTitle(exportTitle).setMessage(exportMessage).setView(exportContent)
                .setPositiveButton("Save to Downloads",(d,w)->saveToDownloads(pendingExportExcel?cleanExcelName(name.getText().toString()):(pendingExportInternetOnly?cleanInternetReportName(name.getText().toString()):cleanTextName(name.getText().toString()))))
                .setNeutralButton("Save to Google Drive",(d,w)->startDocumentExport(pendingExportExcel?cleanExcelName(name.getText().toString()):(pendingExportInternetOnly?cleanInternetReportName(name.getText().toString()):cleanTextName(name.getText().toString()))))
                .setNegativeButton("Cancel",null).create();
        shareExport.setOnClickListener(v->{
            String filename=pendingExportExcel?cleanExcelName(name.getText().toString()):(pendingExportInternetOnly?cleanInternetReportName(name.getText().toString()):cleanTextName(name.getText().toString()));
            exportAlert.dismiss();shareExportFile(filename);
        });
        exportAlert.show();"""
replace_once(main, dialog_old, dialog_new, "Quick Share export dialog")
share_method = """
    private void shareExportFile(String filename){
        try{
            java.io.File dir=new java.io.File(getCacheDir(),"shared");
            if(!dir.exists()&&!dir.mkdirs())throw new Exception("Could not prepare the export for sharing");
            java.io.File file=new java.io.File(dir,filename);
            String root=dir.getCanonicalPath()+java.io.File.separator;
            if(!file.getCanonicalPath().startsWith(root))throw new Exception("Invalid export filename");
            if(file.exists()&&!file.delete())throw new Exception("Could not replace the previous share copy");
            pendingExportFileName=filename;
            writeExport(sharedUri(file));
            if(!file.isFile()||file.length()==0)return;
            sendSharedFile(file,ExportMimeType.forName(filename),"Share export — Quick Share or another app");
        }catch(Exception e){showError("Could not share export",e);}
    }
"""
share_anchor="    private void shareInstalledApk(){"
if main.read_text().count(share_anchor)!=1: raise SystemExit("Quick Share helper anchor missing")
main.write_text(main.read_text().replace(share_anchor,share_method+"\n"+share_anchor,1))
provider = """package com.iceinventory.onhand;

import android.content.ContentProvider;
import android.content.ContentValues;
import android.database.Cursor;
import android.database.MatrixCursor;
import android.net.Uri;
import android.os.ParcelFileDescriptor;
import android.provider.OpenableColumns;

import java.io.File;
import java.io.FileNotFoundException;
import java.io.IOException;

/** Private provider for internally prepared OnHand sharing and export files. */
public final class ShareFileProvider extends ContentProvider {
    @Override public boolean onCreate(){return true;}
    private File resolve(Uri uri,boolean create)throws FileNotFoundException{
        if(uri==null||uri.getPathSegments().size()!=2||!"onhand".equals(uri.getPathSegments().get(0)))throw new FileNotFoundException("Invalid share URI");
        File dir=new File(getContext().getCacheDir(),"shared");
        File file=new File(dir,uri.getLastPathSegment());
        try{
            if(create&&!dir.exists()&&!dir.mkdirs())throw new FileNotFoundException("Could not prepare sharing folder");
            String root=dir.getCanonicalPath()+File.separator;
            String target=file.getCanonicalPath();
            if(!target.startsWith(root)||(!create&&!file.isFile()))throw new FileNotFoundException("Shared file not found");
            return file;
        }catch(IOException e){throw new FileNotFoundException(e.getMessage());}
    }
    @Override public String getType(Uri uri){return uri==null?"application/octet-stream":ExportMimeType.forName(uri.getLastPathSegment());}
    @Override public ParcelFileDescriptor openFile(Uri uri,String mode)throws FileNotFoundException{
        if("r".equals(mode))return ParcelFileDescriptor.open(resolve(uri,false),ParcelFileDescriptor.MODE_READ_ONLY);
        if("w".equals(mode)||"wt".equals(mode))return ParcelFileDescriptor.open(resolve(uri,true),ParcelFileDescriptor.MODE_CREATE|ParcelFileDescriptor.MODE_TRUNCATE|ParcelFileDescriptor.MODE_WRITE_ONLY);
        throw new FileNotFoundException("Unsupported sharing mode");
    }
    @Override public Cursor query(Uri uri,String[] projection,String selection,String[] selectionArgs,String sortOrder){
        try{
            File f=resolve(uri,false);String[] cols=projection==null?new String[]{OpenableColumns.DISPLAY_NAME,OpenableColumns.SIZE}:projection;
            MatrixCursor cursor=new MatrixCursor(cols,1);MatrixCursor.RowBuilder row=cursor.newRow();
            for(String col:cols){if(OpenableColumns.DISPLAY_NAME.equals(col))row.add(f.getName());else if(OpenableColumns.SIZE.equals(col))row.add(f.length());else row.add(null);}
            return cursor;
        }catch(Exception e){return null;}
    }
    @Override public Uri insert(Uri uri,ContentValues values){throw new UnsupportedOperationException("Private file provider");}
    @Override public int delete(Uri uri,String selection,String[] selectionArgs){throw new UnsupportedOperationException("Private file provider");}
    @Override public int update(Uri uri,ContentValues values,String selection,String[] selectionArgs){throw new UnsupportedOperationException("Private file provider");}
}
"""
(app / "src/main/java/com/iceinventory/onhand/ShareFileProvider.java").write_text(provider)
mime = """package com.iceinventory.onhand;

import java.util.Locale;

/** MIME types used by Android's system share sheet for exported files. */
public final class ExportMimeType {
    private ExportMimeType() {}
    public static String forName(String filename) {
        String name=filename==null?"":filename.toLowerCase(Locale.US);
        if(name.endsWith(".apk"))return "application/vnd.android.package-archive";
        if(name.endsWith(".zip"))return "application/zip";
        if(name.endsWith(".xlsx"))return "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet";
        if(name.endsWith(".html")||name.endsWith(".htm"))return "text/html";
        if(name.endsWith(".txt")||name.endsWith(".csv"))return "text/plain";
        return "application/octet-stream";
    }
}
"""
(app / "src/main/java/com/iceinventory/onhand/ExportMimeType.java").write_text(mime)
test_text = tests.read_text()
test_anchor = '    @Test public void caseMultiplierKeepsWorkingCalculation(){'
if test_text.count(test_anchor)!=1: raise SystemExit("Quick Share test insertion point missing")
test_text=test_text.replace(test_anchor,'''    @Test public void shareUsesCorrectMimeTypesForExportFormats(){
        assertEquals("text/plain",ExportMimeType.forName("batch.txt"));
        assertEquals("text/html",ExportMimeType.forName("items.html"));
        assertEquals("application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",ExportMimeType.forName("inventory.xlsx"));
    }
'''+test_anchor,1)
tests.write_text(test_text)

# Add exact version and mandatory CI tests.
manifest=app / "src/main/AndroidManifest.xml"
if "iCE Onhand 3.0.251" not in manifest.read_text():raise SystemExit("Manifest version was not updated")
main_source=main.read_text();batch_source=batch.read_text()
checks={
    "version": "versionCode 30251" in build.read_text() and "versionName '3.0.251'" in build.read_text(),
    "scan resolves mapped location": "String mappedLocation=locationDescriptionForBarcode(rawCode);" in main_source,
    "location banner includes mapped barcode": "code+\" — \"+description" in main_source,
    "cigarette summary uses location-aware rule": "CigaretteCountRules.isCigarette(category,rowLocation)" in main_source,
    "Jose filename parsing": "BatchFilename.user(file)" in batch_source,
    "ambiguous truncated locations flagged": "UNRESOLVED LOCATION CODE " in batch_source,
    "case regression test": "caseMultiplierKeepsWorkingCalculation" in tests.read_text(),
    "location regression test": "fiveDigitLocationSuffixIsPreservedAndMapped" in tests.read_text(),
}
failed=[name for name,ok in checks.items() if not ok]
if failed:raise SystemExit("3.0.251 regression preparation failed: "+", ".join(failed))
print("Prepared OnHand 3.0.251 regression fixes and tests")
