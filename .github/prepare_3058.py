from pathlib import Path
import runpy

# Preserve every approved 3.0.57 behavior first.
runpy.run_path('.github/prepare_3057.py', run_name='__main__')

p=Path('app/src/main/java/com/iceinventory/onhand/MainActivity.java')
s=p.read_text()

# Samsung IME scanner updates can report the whole edited field rather than just the
# newly typed suffix. Compute the true inserted delta from the previous and current
# values so an existing barcode is never treated as part of the new scan.
old='''                int length=text==null?0:text.length();\n                int end=Math.min(length,st+count);\n                if(st<0||end<=st)return;\n                String inserted=text.subSequence(st,end).toString().replace("\\r","").replace("\\n","").replace("\\t","").trim();\n                if(inserted.isEmpty())return;\n'''
new='''                String current=text==null?"":text.toString();\n                String beforeValue=prior==null?"":prior;\n                int prefix=0;\n                int maxPrefix=Math.min(beforeValue.length(),current.length());\n                while(prefix<maxPrefix&&beforeValue.charAt(prefix)==current.charAt(prefix))prefix++;\n                int suffix=0;\n                int maxSuffix=Math.min(beforeValue.length()-prefix,current.length()-prefix);\n                while(suffix<maxSuffix&&beforeValue.charAt(beforeValue.length()-1-suffix)==current.charAt(current.length()-1-suffix))suffix++;\n                int insertedEnd=current.length()-suffix;\n                String inserted=(insertedEnd>prefix?current.substring(prefix,insertedEnd):"")\n                        .replace("\\r","").replace("\\n","").replace("\\t","").trim();\n                if(inserted.isEmpty()&&count>0&&st>=0&&st<current.length()) {\n                    int fallbackEnd=Math.min(current.length(),st+count);\n                    if(fallbackEnd>st)inserted=current.substring(st,fallbackEnd).replace("\\r","").replace("\\n","").replace("\\t","").trim();\n                }\n                if(inserted.isEmpty())return;\n'''
if old not in s: raise SystemExit('3.0.58 target missing: IME inserted-text calculation')
s=s.replace(old,new,1)

# Some Bluetooth wedges type more slowly than a phone keyboard. Keep the complete scan
# burst together for up to 900 ms between characters instead of resetting at 180 ms.
old='''                boolean newBurst=field!=scannerImeSource || scannerImeLastMs==0L || now-scannerImeLastMs>180L;\n'''
new='''                boolean newBurst=field!=scannerImeSource || scannerImeLastMs==0L || now-scannerImeLastMs>900L;\n'''
if old not in s: raise SystemExit('3.0.58 target missing: IME burst gap')
s=s.replace(old,new,1)

# Full-string scanner commits can be accepted quickly. Character-by-character scans wait
# briefly for the final digit, with each later character invalidating the earlier timer.
old='''                if(candidate.length()>=8&&(wholeCommit||rapidBurst)){\n                    final int token=++scannerImeGeneration;\n                    field.postDelayed(()->commitScannerImeBurst(token),220);\n                }\n'''
new='''                if(candidate.length()>=8&&(wholeCommit||rapidBurst)){\n                    final int token=++scannerImeGeneration;\n                    field.postDelayed(()->commitScannerImeBurst(token),wholeCommit?90L:450L);\n                }\n'''
if old not in s: raise SystemExit('3.0.58 target missing: IME commit delay')
s=s.replace(old,new,1)

# Many wedges send Enter/Done immediately after the barcode. If that happens before the
# delayed IME commit, never submit the visible old+new Barcode field. Submit only the
# pending scanner buffer, which contains the newly inserted barcode.
old='''                handleScannedBarcode(barcode.getText().toString().trim());\n'''
new='''                String pendingScanner=scannerImeBuffer.toString().trim();\n                if(scannerImeSource==barcode&&pendingScanner.length()>=8)\n                    commitScannerImeBurst(scannerImeGeneration);\n                else\n                    handleScannedBarcode(barcode.getText().toString().trim());\n'''
if old not in s: raise SystemExit('3.0.58 target missing: barcode editor submit')
s=s.replace(old,new,1)

p.write_text(s)
print('Prepared iCE Onhand 3.0.58: Samsung IME delta scan + slower Bluetooth burst support + Enter uses new scan only')
