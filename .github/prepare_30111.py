from pathlib import Path

# Preserve all 3.0.110 functionality, then correct audit filenames.
base=Path('.github/prepare_30110.py')
exec(compile(base.read_text(),str(base),'exec'),{'__name__':'__main__','__file__':str(base)})

p=Path('app/src/main/java/com/iceinventory/onhand/MainActivity.java')
s=p.read_text()

old='''    private String auditExportFileName(String ignored) {
        String n=sessionName==null||sessionName.trim().isEmpty()?"Inventory":sessionName.trim();
        String lower=n.toLowerCase(Locale.US);
        if(lower.endsWith(".xlsx"))n=n.substring(0,n.length()-5);
        else if(lower.endsWith(".txt"))n=n.substring(0,n.length()-4);
        String suffix=pendingAuditSort==1?" - Audit Highest Unit Price":(pendingAuditSort==2?" - Audit Highest Extended Value":" - Audit Highest Quantity");
        return cleanExcelName(n+suffix+".xlsx");
    }
'''
new='''    private String auditExportFileName(String ignored) {
        String inventory=sessionName==null||sessionName.trim().isEmpty()?"Inventory":sessionName.trim();
        String lower=inventory.toLowerCase(Locale.US);
        if(lower.endsWith(".xlsx"))inventory=inventory.substring(0,inventory.length()-5);
        else if(lower.endsWith(".txt"))inventory=inventory.substring(0,inventory.length()-4);
        String report=pendingAuditSort==1?"Highest Unit Price":(pendingAuditSort==2?"Highest Extended Value":"Highest Quantity");
        return cleanExcelName(report+" - "+inventory+".xlsx");
    }
'''
if old not in s: raise SystemExit('3.0.111 target missing: audit filename')
s=s.replace(old,new,1)
s=s.replace('Onhand Inventory 3.0.110','Onhand Inventory 3.0.111',1)
if 'Onhand Inventory 3.0.111' not in s: raise SystemExit('3.0.111 visible version target missing')
p.write_text(s)

p=Path('app/build.gradle')
g=p.read_text().replace('versionCode 30110','versionCode 30111',1).replace("versionName '3.0.110'","versionName '3.0.111'",1)
if 'versionCode 30111' not in g or "versionName '3.0.111'" not in g: raise SystemExit('3.0.111 Gradle version target missing')
p.write_text(g)

p=Path('app/src/main/AndroidManifest.xml')
m=p.read_text().replace('iCE Onhand 3.0.110','iCE Onhand 3.0.111',1)
if 'iCE Onhand 3.0.111' not in m: raise SystemExit('3.0.111 manifest version target missing')
p.write_text(m)

main=Path('app/src/main/java/com/iceinventory/onhand/MainActivity.java').read_text()
checks={
    'report title first':'return cleanExcelName(report+" - "+inventory+".xlsx")' in main,
    'highest unit price filename':'"Highest Unit Price"' in main,
    'highest extended value filename':'"Highest Extended Value"' in main,
    'highest quantity filename':'"Highest Quantity"' in main,
    'counted only':'if(row.quantity>0)sorted.add(row)' in Path('app/src/main/java/com/iceinventory/onhand/SimpleXlsxWriter.java').read_text(),
}
missing=[k for k,v in checks.items() if not v]
if missing: raise SystemExit('3.0.111 verification failed: '+', '.join(missing))
print('Prepared iCE Onhand 3.0.111: audit report title is first in every Excel filename')
