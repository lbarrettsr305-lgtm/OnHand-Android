from pathlib import Path
import re

# Preserve the validated 3.0.103 Excel compatibility rebuild first.
base=Path('.github/prepare_30103.py')
exec(compile(base.read_text(),str(base),'exec'),{'__name__':'__main__','__file__':str(base)})

p=Path('app/src/main/java/com/iceinventory/onhand/ProfessionalCombinedXlsxWriter.java')
s=p.read_text()

# Compact Verification sheet: two columns, short labeled rows, and one file row per source.
verification='''    private static String verification(String report,String master,List<SourceRow> sources,int unique,long sourceTotal,long combinedTotal,boolean verified,Date when){
        String t=fmt(when); StringBuilder x=open(2);
        row(x,1,tc("A1","Ice Inventory LLC",1));
        row(x,2,tc("A2","Combined Batch Verification Report",1));
        row(x,4,tc("A4","Report / Inventory",1)+tc("B4",report,0));
        row(x,5,tc("A5","Master Report User",1)+tc("B5",master,0));
        row(x,6,tc("A6","Created At",1)+tc("B6",t,0));
        row(x,7,tc("A7","Verification Status",1)+tc("B7",verified?"PASS - VERIFIED":"FAIL - NOT VERIFIED",1));
        int totalRows=0; for(SourceRow a:sources) totalRows+=a.rows;
        row(x,9,tc("A9","Selected Source Files",1)+nc("B9",sources.size(),0));
        row(x,10,tc("A10","Source Rows",1)+nc("B10",totalRows,0));
        row(x,11,tc("A11","Unique Barcodes",1)+nc("B11",unique,0));
        row(x,12,tc("A12","Source Grand Total",1)+nc("B12",sourceTotal,0));
        row(x,13,tc("A13","Combined Grand Total",1)+nc("B13",combinedTotal,0));
        row(x,14,tc("A14","Difference",1)+nc("B14",combinedTotal-sourceTotal,0));
        int r=16; row(x,r++,tc("A16","SOURCE FILE AUDIT",1));
        int n=1; for(SourceRow a:sources){
            row(x,r++,tc("A"+(r-1),"Source "+n,1)+tc("B"+(r-1),(a.userName.isEmpty()?a.sourceType:a.userName)+" | Qty "+a.quantity+" | Rows "+a.rows,0));
            row(x,r++,tc("A"+(r-1),"File",1)+tc("B"+(r-1),a.fileName,0));
            n++;
        }
        r++; row(x,r++,tc("A"+(r-1),"Verification",1)+tc("B"+(r-1),"PASS means every selected source loaded and source and combined totals match exactly.",0));
        row(x,r++,tc("A"+(r-1),"File Rules",1)+tc("B"+(r-1),"Tab-delimited files may use recognized headers or headerless Quantity | Barcode | Description | Price order.",0));
        row(x,r++,tc("A"+(r-1),"Scope",1)+tc("B"+(r-1),"Computational reconciliation only; physical count accuracy is not independently certified.",0));
        r++; row(x,r,tc("A"+r,"FINAL RESULT",1)+tc("B"+r,verified?"PASS - ALL SELECTED QUANTITIES INCLUDED":"FAIL - RECONCILIATION NOT VERIFIED",1));
        return close(x,null);
    }
'''
pat=r'''    private static String verification\(String report,String master,List<SourceRow> sources,int unique,long sourceTotal,long combinedTotal,boolean verified,Date when\)\{.*?\n    \}\n\n(?=    private static String combined)'''
s,n=re.subn(pat,lambda m:verification,s,count=1,flags=re.S)
if n!=1: raise SystemExit('3.0.104 target missing: verification method')

# Compact Combined Inventory metadata so phone users do not have to pan across a long title row.
combined='''    private static String combined(String report,String master,List<CombinedRow> rows,Date when){
        StringBuilder x=open(4); row(x,1,tc("A1","Ice Inventory LLC - Combined Inventory",1));
        row(x,2,tc("A2","Report",1)+tc("B2",report,0));
        row(x,3,tc("A3","Master User",1)+tc("B3",master,0));
        row(x,4,tc("A4","Created",1)+tc("B4",fmt(when),0));
        row(x,6,tc("A6","Quantity",1)+tc("B6","Barcode",1)+tc("C6","Description",1)+tc("D6","Price",1));
        int r=7; for(CombinedRow a:rows){double p=money(a.price); row(x,r,nc("A"+r,a.quantity,0)+tc("B"+r,a.barcode,0)+tc("C"+r,a.description,0)+(Double.isNaN(p)?tc("D"+r,a.price,0):dc("D"+r,p,2))); r++;}
        return close(x,"A6:D"+Math.max(6,r-1));
    }
'''
pat=r'''    private static String combined\(String report,String master,List<CombinedRow> rows,Date when\)\{.*?\n    \}\n\n(?=    private static String valuation)'''
s,n=re.subn(pat,lambda m:combined,s,count=1,flags=re.S)
if n!=1: raise SystemExit('3.0.104 target missing: combined method')

# Compact Valuation metadata while preserving all requested value columns and totals.
valuation='''    private static String valuation(String report,String master,List<CombinedRow> rows,Date when){
        StringBuilder x=open(5); row(x,1,tc("A1","Ice Inventory LLC - Inventory Valuation",1));
        row(x,2,tc("A2","Report",1)+tc("B2",report,0));
        row(x,3,tc("A3","Master User",1)+tc("B3",master,0));
        row(x,4,tc("A4","Created",1)+tc("B4",fmt(when),0));
        row(x,5,tc("A5","Value Rule",1)+tc("B5","Extended Value = Quantity x Price. Missing prices are $0.00 and counted for review.",0));
        row(x,7,tc("A7","Quantity",1)+tc("B7","Barcode",1)+tc("C7","Description",1)+tc("D7","Price",1)+tc("E7","Extended Value",1));
        int r=8,missing=0; double grand=0; for(CombinedRow a:rows){double p=money(a.price); if(Double.isNaN(p)){p=0;missing++;} double ext=a.quantity*p; grand+=ext; row(x,r,nc("A"+r,a.quantity,0)+tc("B"+r,a.barcode,0)+tc("C"+r,a.description,0)+dc("D"+r,p,2)+dc("E"+r,ext,2)); r++;}
        int last=r-1; r++; row(x,r,tc("D"+r,"Grand Total",1)+dc("E"+r,grand,3)); r++; row(x,r,tc("D"+r,"Price Review Lines",1)+nc("E"+r,missing,0));
        return close(x,"A7:E"+Math.max(7,last));
    }
'''
pat=r'''    private static String valuation\(String report,String master,List<CombinedRow> rows,Date when\)\{.*?\n    \}\n\n(?=    private static StringBuilder open)'''
s,n=re.subn(pat,lambda m:valuation,s,count=1,flags=re.S)
if n!=1: raise SystemExit('3.0.104 target missing: valuation method')

# Reduce widths substantially. Verification uses only A:B; inventory sheets remain complete.
old='''    private static StringBuilder open(int cols){StringBuilder x=new StringBuilder(12000);x.append("<?xml version=\\"1.0\\" encoding=\\"UTF-8\\" standalone=\\"yes\\"?><worksheet xmlns=\\"http://schemas.openxmlformats.org/spreadsheetml/2006/main\\"><sheetViews><sheetView workbookViewId=\\"0\\"/></sheetViews><cols>");double[] w={14,22,48,16,20};for(int i=0;i<cols;i++)x.append("<col min=\\"").append(i+1).append("\\" max=\\"").append(i+1).append("\\" width=\\"").append(w[i]).append("\\" customWidth=\\"1\\"/>");x.append("</cols><sheetData>");return x;}'''
new='''    private static StringBuilder open(int cols){StringBuilder x=new StringBuilder(12000);x.append("<?xml version=\\"1.0\\" encoding=\\"UTF-8\\" standalone=\\"yes\\"?><worksheet xmlns=\\"http://schemas.openxmlformats.org/spreadsheetml/2006/main\\"><sheetViews><sheetView workbookViewId=\\"0\\"/></sheetViews><cols>");double[] w={11,20,30,12,16};for(int i=0;i<cols;i++)x.append("<col min=\\"").append(i+1).append("\\" max=\\"").append(i+1).append("\\" width=\\"").append(w[i]).append("\\" customWidth=\\"1\\"/>");x.append("</cols><sheetData>");return x;}'''
if old not in s: raise SystemExit('3.0.104 target missing: column widths')
s=s.replace(old,new,1)
p.write_text(s)

# Version bump only; all app behavior remains inherited from 3.0.103.
p=Path('app/src/main/java/com/iceinventory/onhand/MainActivity.java')
m=p.read_text().replace('Onhand Inventory 3.0.103','Onhand Inventory 3.0.104')
if 'Onhand Inventory 3.0.104' not in m: raise SystemExit('3.0.104 visible version target missing')
p.write_text(m)

p=Path('app/build.gradle')
g=p.read_text().replace('versionCode 30103','versionCode 30104',1).replace("versionName '3.0.103'","versionName '3.0.104'",1)
if 'versionCode 30104' not in g or "versionName '3.0.104'" not in g: raise SystemExit('3.0.104 Gradle version target missing')
p.write_text(g)

p=Path('app/src/main/AndroidManifest.xml')
a=p.read_text().replace('iCE Onhand 3.0.103','iCE Onhand 3.0.104')
if 'iCE Onhand 3.0.104' not in a: raise SystemExit('3.0.104 manifest version target missing')
p.write_text(a)

x=Path('app/src/main/java/com/iceinventory/onhand/ProfessionalCombinedXlsxWriter.java').read_text()
main=Path('app/src/main/java/com/iceinventory/onhand/MainActivity.java').read_text()
merge=Path('app/src/main/java/com/iceinventory/onhand/BatchMergeActivity.java').read_text()
checks={
 'compact verification':'StringBuilder x=open(2)' in x and 'SOURCE FILE AUDIT' in x,
 'short verification labels':'File Rules' in x and 'Computational reconciliation only' in x,
 'compact widths':'double[] w={11,20,30,12,16}' in x,
 'combined metadata compact':'tc("A2","Report",1)' in x and 'tc("A3","Master User",1)' in x,
 'valuation preserved':'Extended Value' in x and 'Grand Total' in x and 'Price Review Lines' in x,
 'currency preserved':'$#,##0.00' in x,
 'drawing-free preserved':'drawing1.xml' not in x and 'image1.png' not in x and '<drawing ' not in x,
 'XML sanitizer preserved':'0xD7FF' in x and '0xFFFD' in x and '32767' in x,
 'master user preserved':'MASTER REPORT USER' in main and 'MASTER REPORT USER:' in merge,
 'headerless sources preserved':'looksLikeHeaderlessStandard' in merge,
}
missing=[k for k,v in checks.items() if not v]
if missing: raise SystemExit('3.0.104 verification failed: '+', '.join(missing))
print('Prepared iCE Onhand 3.0.104: compact phone-friendly professional Excel workbook')
