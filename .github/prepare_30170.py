from pathlib import Path

base = Path('.github/prepare_30169.py')
exec(compile(base.read_text(), str(base), 'exec'), {'__name__': '__main__', '__file__': str(base)})


def rep(path, old, new, label):
    p = Path(path); s = p.read_text()
    if s.count(old) != 1:
        raise SystemExit('3.0.170 target ' + label + ' count ' + str(s.count(old)))
    p.write_text(s.replace(old, new, 1))


rep('app/build.gradle', 'versionCode 30169', 'versionCode 30170', 'code')
rep('app/build.gradle', "versionName '3.0.169'", "versionName '3.0.170'", 'name')
rep('app/src/main/AndroidManifest.xml', 'iCE Onhand 3.0.169', 'iCE Onhand 3.0.170', 'manifest')
rep('app/src/main/java/com/iceinventory/onhand/MainActivity.java',
    'Onhand Inventory 3.0.169', 'Onhand Inventory 3.0.170', 'header')

w = 'app/src/main/java/com/iceinventory/onhand/MonthlyCombinedInventoryXlsxWriter.java'
rep(w,
    'public static final class Row{public String upc="",gtin="",retail="",description="";public double quantity;}',
    'public static final class Row{public String upc="",gtin="",retail="",description="",categoryId="",categoryDescription="";public double quantity;}',
    'category row fields')
rep(w,
    'new String[]{"COMPLETE COMBINED INVENTORY","","","","",""}',
    'new String[]{"COMPLETE COMBINED INVENTORY","","","","","","",""}',
    'title columns')
rep(w,
    'new String[]{"CUSTOMER",customer,"INVENTORY DATE",date,"",""}',
    'new String[]{"CUSTOMER",customer,"INVENTORY DATE",date,"","","",""}',
    'customer columns')
rep(w,
    'new String[]{"UPC","GTIN","QTY","RETAIL","DESCRIPTION","EXTENDED VALUE"}',
    'new String[]{"UPC","GTIN","QTY","RETAIL","DESCRIPTION","CATEGORY ID","CATEGORY DESCRIPTION","EXTENDED VALUE"}',
    'report headers')
rep(w,
    'text(x,4,r,a.description,0);if(!clean(a.retail).isEmpty())formula(x,5,r,"C"+r+"*D"+r,2);else text(x,5,r,"",0);',
    'text(x,4,r,a.description,0);text(x,5,r,a.categoryId,0);text(x,6,r,a.categoryDescription,0);if(!clean(a.retail).isEmpty())formula(x,7,r,"C"+r+"*D"+r,2);else text(x,7,r,"",0);',
    'category data columns')
rep(w,
    'text(x,3,r,"",1);text(x,4,r,"",1);if(last>=first)formula(x,5,r,"SUM(F"+first+":F"+last+")",3);else number(x,5,r,0,3);',
    'text(x,3,r,"",1);text(x,4,r,"",1);text(x,5,r,"",1);text(x,6,r,"",1);if(last>=first)formula(x,7,r,"SUM(H"+first+":H"+last+")",3);else number(x,7,r,0,3);',
    'grand total columns')
old_sheet = r'''<col min=\"5\" max=\"5\" width=\"46\" customWidth=\"1\"/><col min=\"6\" max=\"6\" width=\"18\" customWidth=\"1\"/></cols><sheetData>"+x+"</sheetData><autoFilter ref=\"A4:F"+r+"\"/>'''
new_sheet = r'''<col min=\"5\" max=\"5\" width=\"46\" customWidth=\"1\"/><col min=\"6\" max=\"6\" width=\"15\" customWidth=\"1\"/><col min=\"7\" max=\"7\" width=\"32\" customWidth=\"1\"/><col min=\"8\" max=\"8\" width=\"18\" customWidth=\"1\"/></cols><sheetData>"+x+"</sheetData><autoFilter ref=\"A4:H"+r+"\"/>'''
rep(w, old_sheet, new_sheet, 'eight-column worksheet')

m = 'app/src/main/java/com/iceinventory/onhand/MonthlyInventoryActivity.java'
rep(m,
    'r.gtin=p.gtin;r.retail=p.retail;r.description=p.description;',
    'r.gtin=p.gtin;r.retail=p.retail;r.description=p.description;r.categoryId=p.category;r.categoryDescription=p.categoryName;',
    'populate categories')

ws = Path(w).read_text(); ms = Path(m).read_text()
checks = {
    'version': "versionName '3.0.170'" in Path('app/build.gradle').read_text(),
    'headers': '"CATEGORY ID","CATEGORY DESCRIPTION","EXTENDED VALUE"' in ws,
    'category id': 'r.categoryId=p.category' in ms,
    'category description': 'r.categoryDescription=p.categoryName' in ms,
    'eight columns': 'autoFilter ref=\\"A4:H' in ws,
    'extended formula': 'formula(x,7,r,"C"+r+"*D"+r,2)' in ws,
    'grand formula': '"SUM(H"+first+":H"+last+")"' in ws
}
bad = [k for k,v in checks.items() if not v]
if bad: raise SystemExit('3.0.170 checks failed: '+', '.join(bad))
print('Prepared iCE OnHand 3.0.170: category ID and description in Complete Combined Inventory Excel')
