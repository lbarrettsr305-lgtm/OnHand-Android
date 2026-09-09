from pathlib import Path

# Preserve every current 3.0.102 feature first.
base=Path('.github/prepare_30102.py')
exec(compile(base.read_text(),str(base),'exec'),{'__name__':'__main__','__file__':str(base)})

# Replace only the professional workbook writer with the validated drawing-free package.
template=Path('.github/ProfessionalCombinedXlsxWriter_30103.java').read_text()
Path('app/src/main/java/com/iceinventory/onhand/ProfessionalCombinedXlsxWriter.java').write_text(template)

p=Path('app/src/main/java/com/iceinventory/onhand/MainActivity.java')
s=p.read_text().replace('Onhand Inventory 3.0.102','Onhand Inventory 3.0.103')
if 'Onhand Inventory 3.0.103' not in s: raise SystemExit('3.0.103 visible version target missing')
p.write_text(s)

p=Path('app/build.gradle')
g=p.read_text().replace('versionCode 30102','versionCode 30103',1).replace("versionName '3.0.102'","versionName '3.0.103'",1)
if 'versionCode 30103' not in g or "versionName '3.0.103'" not in g: raise SystemExit('3.0.103 Gradle version target missing')
p.write_text(g)

p=Path('app/src/main/AndroidManifest.xml')
a=p.read_text().replace('iCE Onhand 3.0.102','iCE Onhand 3.0.103')
if 'iCE Onhand 3.0.103' not in a: raise SystemExit('3.0.103 manifest version target missing')
p.write_text(a)

x=Path('app/src/main/java/com/iceinventory/onhand/ProfessionalCombinedXlsxWriter.java').read_text()
main=Path('app/src/main/java/com/iceinventory/onhand/MainActivity.java').read_text()
merge=Path('app/src/main/java/com/iceinventory/onhand/BatchMergeActivity.java').read_text()
checks={
 'three worksheets': all(v in x for v in ['Verification','Combined Inventory','Inventory Valuation']),
 'valuation': 'Extended Value' in x and 'Grand Total Inventory Value' in x,
 'branding': 'Ice Inventory LLC' in x,
 'currency': '$#,##0.00' in x,
 'drawing-free': 'drawing1.xml' not in x and 'image1.png' not in x and '<drawing ' not in x,
 'XML sanitizer': '0xD7FF' in x and '0xFFFD' in x and '32767' in x,
 'master user preserved': 'MASTER REPORT USER' in main and 'MASTER REPORT USER:' in merge,
 'headerless sources preserved': 'looksLikeHeaderlessStandard' in merge,
 'combined output naming preserved': 'combinedOutputName' in merge,
}
missing=[k for k,v in checks.items() if not v]
if missing: raise SystemExit('3.0.103 verification failed: '+', '.join(missing))
print('Prepared iCE Onhand 3.0.103: drawing-free standards-focused three-sheet Excel workbook')
