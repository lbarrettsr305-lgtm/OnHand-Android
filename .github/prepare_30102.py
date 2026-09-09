from pathlib import Path
import re

# Preserve every current 3.0.101 feature first.
base=Path('.github/prepare_30101.py')
exec(compile(base.read_text(),str(base),'exec'),{'__name__':'__main__','__file__':str(base)})

# -----------------------------------------------------------------------------
# 3.0.102 Excel repair
# Fixes the workbook repair warning seen in Microsoft Excel.
# 1) OOXML schema order: autoFilter must appear before mergeCells.
# 2) Strip XML 1.0-invalid control/surrogate characters from workbook text.
# -----------------------------------------------------------------------------
p=Path('app/src/main/java/com/iceinventory/onhand/ProfessionalCombinedXlsxWriter.java')
s=p.read_text()

# Reorder the affected worksheet children generically for both data sheets.
# Existing generated code writes: </sheetData><mergeCells...>...</mergeCells> then autoFilter.
# Excel requires autoFilter before mergeCells.
pat=r'''        x\.append\("</sheetData><mergeCells count=\\\"(\d+)\\\">(.*?)</mergeCells>"\);\n        x\.append\("<autoFilter ref=\\\"([^\"]+)"\)\.append\((.*?)\)\.append\("\\\"/>"\);'''

def swap(m):
    count=m.group(1)
    merges=m.group(2)
    prefix=m.group(3)
    expr=m.group(4)
    return ('        x.append("</sheetData>");\n'
            '        x.append("<autoFilter ref=\\\"'+prefix+'").append('+expr+').append("\\\"/>");\n'
            '        x.append("<mergeCells count=\\\"'+count+'\\\">'+merges+'</mergeCells>");')

s,n=re.subn(pat,swap,s,flags=re.S)
if n!=2:raise SystemExit('3.0.102 expected to repair exactly 2 worksheet autoFilter/mergeCells blocks, found '+str(n))

# Harden every workbook string for XML 1.0 validity and Excel's cell string limit.
old='''    private static String clean(String s){return s==null?"":s.replace('\\t',' ').replace('\\r',' ').replace('\\n',' ').trim();}\n    private static String xml(String s){String v=s==null?"":s;return v.replace("&","&amp;").replace("<","&lt;").replace(">","&gt;").replace("\\\"","&quot;").replace("'","&apos;");}\n'''
new='''    private static String clean(String s){\n        if(s==null)return "";\n        StringBuilder out=new StringBuilder(Math.min(s.length(),32767));\n        for(int i=0;i<s.length() && out.length()<32767;){\n            int cp=s.codePointAt(i);i+=Character.charCount(cp);\n            if(cp=='\\t'||cp=='\\r'||cp=='\\n'){out.append(' ');continue;}\n            if(validXml10(cp))out.appendCodePoint(cp);\n        }\n        return out.toString().trim();\n    }\n    private static boolean validXml10(int cp){\n        return cp==0x9||cp==0xA||cp==0xD||\n                (cp>=0x20&&cp<=0xD7FF)||\n                (cp>=0xE000&&cp<=0xFFFD)||\n                (cp>=0x10000&&cp<=0x10FFFF);\n    }\n    private static String xml(String s){\n        String v=clean(s);\n        return v.replace("&","&amp;").replace("<","&lt;").replace(">","&gt;").replace("\\\"","&quot;").replace("'","&apos;");\n    }\n'''
if old not in s:raise SystemExit('3.0.102 target missing: workbook clean/xml helpers')
s=s.replace(old,new,1)
p.write_text(s)

# Version package and visible labels.
p=Path('app/src/main/java/com/iceinventory/onhand/MainActivity.java')
m=p.read_text().replace('Onhand Inventory 3.0.101','Onhand Inventory 3.0.102')
if 'Onhand Inventory 3.0.102' not in m:raise SystemExit('3.0.102 target missing: visible version')
p.write_text(m)

p=Path('app/build.gradle')
g=p.read_text().replace('versionCode 30101','versionCode 30102',1).replace("versionName '3.0.101'","versionName '3.0.102'",1)
if 'versionCode 30102' not in g or "versionName '3.0.102'" not in g:raise SystemExit('3.0.102 target missing: Gradle version')
p.write_text(g)

p=Path('app/src/main/AndroidManifest.xml')
a=p.read_text().replace('iCE Onhand 3.0.101','iCE Onhand 3.0.102')
if 'iCE Onhand 3.0.102' not in a:raise SystemExit('3.0.102 target missing: manifest version')
p.write_text(a)

# Static regression checks on final generated writer/source.
x=Path('app/src/main/java/com/iceinventory/onhand/ProfessionalCombinedXlsxWriter.java').read_text()
main=Path('app/src/main/java/com/iceinventory/onhand/MainActivity.java').read_text()
merge=Path('app/src/main/java/com/iceinventory/onhand/BatchMergeActivity.java').read_text()

# The bad pattern must be fully gone.
bad_order=re.findall(r'''</sheetData><mergeCells.*?</mergeCells>"\);\n\s*x\.append\("<autoFilter''',x,flags=re.S)
# Both data sheets must still have filters and merged headers.
checks={
    'no invalid worksheet element order':len(bad_order)==0,
    'combined filter preserved':'autoFilter ref=\\\"A4:D' in x,
    'valuation filter preserved':'autoFilter ref=\\\"A4:E' in x,
    'combined merge preserved':'mergeCells count=\\\"2' in x,
    'valuation merge preserved':'mergeCells count=\\\"3' in x,
    'XML sanitizer present':'validXml10' in x and '0xD7FF' in x and '0xFFFD' in x,
    'Excel text length guard':'out.length()<32767' in x,
    'valuation preserved':'Inventory Valuation' in x and 'Grand Total Inventory Value' in x,
    'verified logo preserved':'ice_inventory_master_3070' in x,
    'master user preserved':'MASTER REPORT USER' in main and 'MASTER REPORT USER:' in merge,
    'combined output prefix preserved':'combinedOutputName' in merge and 'COMBINED - ' in merge,
    'headerless sources preserved':'looksLikeHeaderlessStandard' in merge,
}
missing=[k for k,v in checks.items() if not v]
if missing:raise SystemExit('3.0.102 verification failed: '+', '.join(missing))
print('Prepared iCE Onhand 3.0.102: Excel worksheet schema order fixed + XML text sanitized')
