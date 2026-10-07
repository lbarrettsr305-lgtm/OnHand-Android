#!/usr/bin/env python3
from pathlib import Path
import runpy

script_dir = Path(__file__).resolve().parent
root = script_dir.parent if script_dir.name == ".github" else script_dir
workflow = root / ".github/workflows/build-apk.yml"
seed = workflow.read_text()
for new, old in [
    ("Prepare and verify 3.0.210 bundled barcode scanner", "Prepare and verify 3.0.209 Scanning settings transfer"),
    (".github/prepare_30210.py", ".github/prepare_30209.py"),
    ("iCE-Onhand-Inventory-3.0.210", "iCE-Onhand-Inventory-3.0.209"),
]:
    if new not in seed:
        raise SystemExit("3.0.210 workflow seed missing: " + new)
    seed = seed.replace(new, old)
workflow.write_text(seed)
runpy.run_path(str(root / ".github/prepare_30209.py"), run_name="__main__")

w = workflow.read_text()
for old, new in [
    ("Prepare and verify 3.0.209 Scanning settings transfer", "Prepare and verify 3.0.210 bundled barcode scanner"),
    (".github/prepare_30209.py", ".github/prepare_30210.py"),
    ("iCE-Onhand-Inventory-3.0.209", "iCE-Onhand-Inventory-3.0.210"),
]:
    if old not in w:
        raise SystemExit("3.0.209 workflow marker missing: " + old)
    w = w.replace(old, new)
workflow.write_text(w)

gradle = root / "app/build.gradle"
s = gradle.read_text()
if "versionCode 30209" not in s or "versionName '3.0.209'" not in s:
    raise SystemExit("3.0.209 Gradle version missing")
s = s.replace("versionCode 30209", "versionCode 30210", 1).replace("versionName '3.0.209'", "versionName '3.0.210'", 1)
old_dep = "    implementation 'com.google.android.gms:play-services-code-scanner:16.1.0'"
new_deps = """    implementation 'com.google.mlkit:barcode-scanning:17.3.0'
    implementation 'androidx.activity:activity:1.10.1'
    def cameraxVersion = '1.4.2'
    implementation "androidx.camera:camera-camera2:${cameraxVersion}"
    implementation "androidx.camera:camera-lifecycle:${cameraxVersion}"
    implementation "androidx.camera:camera-view:${cameraxVersion}"""
if s.count(old_dep) != 1:
    raise SystemExit("Code Scanner dependency marker missing")
gradle.write_text(s.replace(old_dep, new_deps, 1))

manifest = root / "app/src/main/AndroidManifest.xml"
m = manifest.read_text()
activity_marker = '        <activity\n            android:name=".BatchMergeActivity"'
activity_entry = '        <activity android:name=".ScanActivity" android:exported="false" />\n'
if m.count(activity_marker) != 1 or ".ScanActivity" in m:
    raise SystemExit("Manifest scan activity insertion point unexpected")
manifest.write_text(m.replace(activity_marker, activity_entry + activity_marker, 1))

main = root / "app/src/main/java/com/iceinventory/onhand/MainActivity.java"
s = main.read_text()
if 'import com.google.mlkit.vision.codescanner.GmsBarcodeScanner;' not in s or 'import com.google.mlkit.vision.codescanner.GmsBarcodeScanning;' not in s:
    raise SystemExit("Old Code Scanner imports missing")
s = s.replace('import com.google.mlkit.vision.codescanner.GmsBarcodeScanner;\nimport com.google.mlkit.vision.codescanner.GmsBarcodeScanning;\n', '', 1)
s = s.replace('    private static final int REQ_QUANTITY=1004;\n', '    private static final int REQ_QUANTITY=1004;\n    private static final int REQ_SCAN=1005;\n', 1)
start = s.find("    private void scanBarcode() {")
if start < 0:
    raise SystemExit("scanBarcode method missing")
brace = s.find("{", start)
depth = 0
end = None
for i in range(brace, len(s)):
    if s[i] == "{": depth += 1
    elif s[i] == "}":
        depth -= 1
        if depth == 0:
            end = i + 1
            break
if end is None:
    raise SystemExit("Could not find end of scanBarcode method")
new_scan = '''    private void scanBarcode() {
        startActivityForResult(new Intent(this,ScanActivity.class),REQ_SCAN);
    }'''
s = s[:start] + new_scan + s[end:]
activity_marker = '        super.onActivityResult(requestCode,resultCode,data);\n'
scan_result = '''        if(requestCode==REQ_SCAN){
            if(resultCode==RESULT_OK&&data!=null){
                String value=data.getStringExtra(ScanActivity.EXTRA_BARCODE);
                if(value!=null&&!value.trim().isEmpty())handleScannedBarcode(value.trim());
            }
            return;
        }
'''
if s.count(activity_marker) != 1:
    raise SystemExit("onActivityResult insertion point missing")
s = s.replace(activity_marker, activity_marker + scan_result, 1)
main.write_text(s)

scanner = root / "app/src/main/java/com/iceinventory/onhand/ScanActivity.java"
scanner.write_text(r'''package com.iceinventory.onhand;

import android.Manifest;
import android.app.AlertDialog;
import android.content.Intent;
import android.content.pm.PackageManager;
import android.graphics.Color;
import android.os.Bundle;
import android.view.Gravity;
import android.view.ViewGroup;
import android.widget.Button;
import android.widget.FrameLayout;
import android.widget.TextView;
import android.widget.Toast;

import androidx.activity.ComponentActivity;
import androidx.camera.core.CameraSelector;
import androidx.camera.core.ImageAnalysis;
import androidx.camera.core.ImageProxy;
import androidx.camera.core.Preview;
import androidx.camera.lifecycle.ProcessCameraProvider;
import androidx.camera.view.PreviewView;
import androidx.core.app.ActivityCompat;
import androidx.core.content.ContextCompat;

import com.google.common.util.concurrent.ListenableFuture;
import com.google.mlkit.vision.barcode.BarcodeScanner;
import com.google.mlkit.vision.barcode.BarcodeScannerOptions;
import com.google.mlkit.vision.barcode.BarcodeScanning;
import com.google.mlkit.vision.barcode.common.Barcode;
import com.google.mlkit.vision.common.InputImage;

import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.atomic.AtomicBoolean;

public class ScanActivity extends ComponentActivity {
    public static final String EXTRA_BARCODE = "barcode";
    private static final int CAMERA_PERMISSION_REQUEST = 701;
    private final AtomicBoolean processingFrame = new AtomicBoolean(false);
    private final AtomicBoolean barcodeFound = new AtomicBoolean(false);
    private ExecutorService cameraExecutor;
    private BarcodeScanner scanner;
    private PreviewView previewView;

    @Override protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        cameraExecutor = Executors.newSingleThreadExecutor();
        BarcodeScannerOptions options = new BarcodeScannerOptions.Builder()
                .setBarcodeFormats(Barcode.FORMAT_ALL_FORMATS)
                .build();
        scanner = BarcodeScanning.getClient(options);
        buildScreen();
        if (ContextCompat.checkSelfPermission(this, Manifest.permission.CAMERA) == PackageManager.PERMISSION_GRANTED) {
            startCamera();
        } else {
            ActivityCompat.requestPermissions(this, new String[]{Manifest.permission.CAMERA}, CAMERA_PERMISSION_REQUEST);
        }
    }

    private void buildScreen() {
        FrameLayout root = new FrameLayout(this);
        previewView = new PreviewView(this);
        previewView.setScaleType(PreviewView.ScaleType.FILL_CENTER);
        root.addView(previewView, new FrameLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.MATCH_PARENT));

        TextView hint = new TextView(this);
        hint.setText("Point the camera at a barcode");
        hint.setTextColor(Color.WHITE);
        hint.setTextSize(18);
        hint.setGravity(Gravity.CENTER);
        hint.setBackgroundColor(0x99000000);
        FrameLayout.LayoutParams hp = new FrameLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT, dp(58), Gravity.BOTTOM);
        root.addView(hint, hp);

        Button cancel = new Button(this);
        cancel.setText("Cancel");
        cancel.setAllCaps(false);
        cancel.setOnClickListener(v -> finish());
        FrameLayout.LayoutParams cp = new FrameLayout.LayoutParams(dp(112), dp(52), Gravity.TOP | Gravity.END);
        cp.setMargins(dp(8), dp(18), dp(8), 0);
        root.addView(cancel, cp);
        setContentView(root);
    }

    private int dp(int value) { return Math.round(value * getResources().getDisplayMetrics().density); }

    private void startCamera() {
        ListenableFuture<ProcessCameraProvider> providerFuture = ProcessCameraProvider.getInstance(this);
        providerFuture.addListener(() -> {
            try {
                ProcessCameraProvider provider = providerFuture.get();
                Preview preview = new Preview.Builder().build();
                preview.setSurfaceProvider(previewView.getSurfaceProvider());
                ImageAnalysis analysis = new ImageAnalysis.Builder()
                        .setBackpressureStrategy(ImageAnalysis.STRATEGY_KEEP_ONLY_LATEST)
                        .build();
                analysis.setAnalyzer(cameraExecutor, this::analyzeFrame);
                provider.unbindAll();
                provider.bindToLifecycle(this, CameraSelector.DEFAULT_BACK_CAMERA, preview, analysis);
            } catch (Exception e) {
                showCameraError("Could not start camera: " + e.getMessage());
            }
        }, ContextCompat.getMainExecutor(this));
    }

    private void analyzeFrame(ImageProxy proxy) {
        if (barcodeFound.get() || !processingFrame.compareAndSet(false, true)) {
            proxy.close();
            return;
        }
        android.media.Image mediaImage = proxy.getImage();
        if (mediaImage == null) {
            processingFrame.set(false);
            proxy.close();
            return;
        }
        InputImage image = InputImage.fromMediaImage(mediaImage, proxy.getImageInfo().getRotationDegrees());
        scanner.process(image)
                .addOnSuccessListener(cameraExecutor, codes -> {
                    if (codes != null && !codes.isEmpty() && barcodeFound.compareAndSet(false, true)) {
                        String raw = codes.get(0).getRawValue();
                        if (raw != null && !raw.trim().isEmpty()) {
                            runOnUiThread(() -> {
                                Intent result = new Intent();
                                result.putExtra(EXTRA_BARCODE, raw.trim());
                                setResult(RESULT_OK, result);
                                finish();
                            });
                        } else {
                            barcodeFound.set(false);
                        }
                    }
                })
                .addOnFailureListener(cameraExecutor, e -> android.util.Log.w("OnHandScanner", "Barcode frame failed", e))
                .addOnCompleteListener(cameraExecutor, task -> {
                    proxy.close();
                    processingFrame.set(false);
                });
    }

    private void showCameraError(String message) {
        if (isFinishing()) return;
        new AlertDialog.Builder(this).setTitle("Scanner unavailable").setMessage(message)
                .setPositiveButton("OK", (dialog, which) -> finish()).show();
    }

    @Override public void onRequestPermissionsResult(int requestCode, String[] permissions, int[] grantResults) {
        super.onRequestPermissionsResult(requestCode, permissions, grantResults);
        if (requestCode == CAMERA_PERMISSION_REQUEST) {
            if (grantResults.length > 0 && grantResults[0] == PackageManager.PERMISSION_GRANTED) startCamera();
            else {
                Toast.makeText(this, "Camera permission is needed to scan barcodes", Toast.LENGTH_LONG).show();
                finish();
            }
        }
    }

    @Override protected void onDestroy() {
        if (scanner != null) scanner.close();
        if (cameraExecutor != null) cameraExecutor.shutdown();
        super.onDestroy();
    }
}
''')

manifest_text = manifest.read_text()
checks = {
    "bundled model dependency": "com.google.mlkit:barcode-scanning:17.3.0" in gradle.read_text(),
    "old Play Services Code Scanner dependency removed": "play-services-code-scanner" not in gradle.read_text(),
    "camera permission already declared": 'android.permission.CAMERA' in manifest_text,
    "scanner activity registered": '.ScanActivity' in manifest_text,
    "scanner result returns to count workflow": 'handleScannedBarcode(value.trim())' in main.read_text(),
    "version set to 3.0.210": "versionCode 30210" in gradle.read_text() and "versionName '3.0.210'" in gradle.read_text(),
}
failed = [key for key, passed in checks.items() if not passed]
if failed:
    raise SystemExit("3.0.210 validation failed: " + ", ".join(failed))
print("Prepared 3.0.210 with the bundled ML Kit barcode model and CameraX scanner UI.")
