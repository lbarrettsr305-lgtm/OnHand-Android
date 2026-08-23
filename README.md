# On Hand 3.0.1 — clean Android rebuild

This is a fresh implementation of the On Hand inventory workflow. It does not reuse the legacy APK code, Dropbox SDK, Apache HTTP stack, or old external-storage permissions.

## Included
- Multiple saved inventory sessions
- Barcode/manual entry
- Bluetooth/USB scanner friendly: focus the Barcode field and scanner Enter submits a count
- Built-in camera barcode scanner via ZXing Embedded
- Item description
- Quantity incrementing by barcode + location
- Locations
- Edit/delete count lines
- SQLite local persistence
- CSV import/export through Android's Storage Access Framework (no broad storage permission)
- Android 7+ minimum, target/compile SDK 36

## Build
Open this folder in Android Studio Quail 3 / current Android Studio with Android SDK 36 installed, then build the `app` module. Or run `gradle :app:assembleDebug` with a compatible Gradle/Android SDK setup.

Expected debug APK path:
`app/build/outputs/apk/debug/app-debug.apk`

The application ID is `com.iceinventory.onhand`, so it installs separately from the legacy On Hand APK.

## Automated APK build
The included `.github/workflows/build-apk.yml` builds a debug APK on every push to `main` and also supports manual runs from GitHub Actions. The resulting artifact is named `OnHand-3.0.1-debug-apk`.
