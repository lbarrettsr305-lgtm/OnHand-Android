#!/usr/bin/env python3
from pathlib import Path
import runpy

script_dir = Path(__file__).resolve().parent
root = script_dir.parent if script_dir.name == ".github" else script_dir
workflow = root / ".github/workflows/build-apk.yml"

# Run the completed 3.0.211 preparation first.
w = workflow.read_text()
for new, old in [
    ("Prepare and verify 3.0.212 Fleet Feet import format", "Prepare and verify 3.0.211 automatic increment count"),
    (".github/prepare_30212.py", ".github/prepare_30211.py"),
    ("iCE-Onhand-Inventory-3.0.212", "iCE-Onhand-Inventory-3.0.211"),
]:
    if new not in w:
        raise SystemExit("3.0.212 workflow seed missing: " + new)
    w = w.replace(new, old)
workflow.write_text(w)
runpy.run_path(str(root / ".github/prepare_30211.py"), run_name="__main__")

w = workflow.read_text()
for old, new in [
    ("Prepare and verify 3.0.211 automatic increment count", "Prepare and verify 3.0.212 Fleet Feet import format"),
    (".github/prepare_30211.py", ".github/prepare_30212.py"),
    ("iCE-Onhand-Inventory-3.0.211", "iCE-Onhand-Inventory-3.0.212"),
]:
    if old not in w:
        raise SystemExit("3.0.211 workflow marker missing: " + old)
    w = w.replace(old, new)
workflow.write_text(w)

gradle = root / "app/build.gradle"
g = gradle.read_text()
if "versionCode 30211" not in g or "versionName '3.0.211'" not in g:
    raise SystemExit("3.0.211 Gradle version missing")
g = g.replace("versionCode 30211", "versionCode 30212", 1).replace("versionName '3.0.211'", "versionName '3.0.212'", 1)
gradle.write_text(g)

manifest = root / "app/src/main/AndroidManifest.xml"
m = manifest.read_text()
if m.count("iCE Onhand 3.0.211") != 1:
    raise SystemExit("3.0.211 app label missing")
manifest.write_text(m.replace("iCE Onhand 3.0.211", "iCE Onhand 3.0.212", 1))

main = root / "app/src/main/java/com/iceinventory/onhand/MainActivity.java"
s = main.read_text()
if s.count("Onhand Inventory 3.0.211") != 1:
    raise SystemExit("3.0.211 main screen label missing")
s = s.replace("Onhand Inventory 3.0.211", "Onhand Inventory 3.0.212", 1)

# Expose the import format screen in Settings and route actual imports through
# the configured mapper (which handles both the old tab-delimited files and CSV).
options_start = s.find("    private void showOptions() {")
options_end = s.find("    private String friendlyUnknownMode()", options_start)
if options_start < 0 or options_end < 0:
    raise SystemExit("Options method boundaries missing")
options = s[options_start:options_end]
options_anchor = '        new AlertDialog.Builder(this).setTitle("Options")'
if options.count(options_anchor) != 1:
    raise SystemExit("Options dialog insertion point missing")
options_controls = '''        TextView importExport=text("Import / Export",16,gold(),true);importExport.setPadding(dp(6),dp(10),0,dp(2));box.addView(importExport);
        Button importFormat=button("Configure Import Format",0);
        importFormat.setOnClickListener(v->{Intent intent=new Intent(this,FormatConfigActivity.class);intent.putExtra(FormatConfigActivity.EXTRA_MODE,FormatConfigActivity.MODE_IMPORT);startActivity(intent);});
        box.addView(importFormat,new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT,dp(52)));
'''
options = options.replace(options_anchor, options_controls + options_anchor, 1)
s = s[:options_start] + options + s[options_end:]

read_start = s.find("    private void readImport(Uri uri) {")
if read_start < 0:
    raise SystemExit("Import method missing")
brace = s.find("{", read_start); depth=0; read_end=None
for i in range(brace,len(s)):
    if s[i]=="{": depth+=1
    elif s[i]=="}":
        depth-=1
        if depth==0:
            read_end=i+1;break
if read_end is None:
    raise SystemExit("Import method end missing")
read_method = '''    private void readImport(Uri uri) {
        if(uri==null)return;
        try(InputStream is=getContentResolver().openInputStream(uri);
            BufferedReader br=new BufferedReader(new InputStreamReader(is,StandardCharsets.UTF_8))) {
            if(br==null)throw new Exception("Could not read selected file");
            int imported=TabTextUtils.importRows(br,db,sessionId,prefs(),prefs().getBoolean(KEY_AUTO_GTIN,false));
            refreshLocations();refreshList();toast("Imported "+imported+" rows");
        } catch(Exception e){showError("Import failed",e);}
    }'''
s = s[:read_start] + read_method + s[read_end:]
main.write_text(s)

# Add a reusable import preset matching the customer's headerless CSV:
# Barcode, Item Number, Description, Size, followed by a blank fifth column.
format_path = root / "app/src/main/java/com/iceinventory/onhand/FormatConfigActivity.java"
f = format_path.read_text()
all_fields = 'private static final String[] ALL={"quantity","barcode","description","item_number","price","location","scan_date","scan_time"};'
if f.count(all_fields) != 1:
    raise SystemExit("Format field list missing or unexpected")
f = f.replace(all_fields, 'private static final String[] ALL={"quantity","barcode","description","item_number","size","price","location","scan_date","scan_time"};', 1)
item_label = '        if("item_number".equals(f))return "ITEM NUMBER";'
if f.count(item_label) != 1:
    raise SystemExit("Item Number format label missing")
f = f.replace(item_label, item_label + '\n        if("size".equals(f))return "Size";', 1)

generic_button = '        LinearLayout.LayoutParams gp=new LinearLayout.LayoutParams(0,dp(48),1);gp.setMargins(dp(6),0,0,0);presets.addView(generic,gp);'
if f.count(generic_button) != 1:
    raise SystemExit("Generic preset button missing")
fleet_button = generic_button + '''
        if(MODE_IMPORT.equals(mode)){
            victoria.setTextSize(14);generic.setTextSize(14);
            Button fleetFeet=button("Fleet Feet");fleetFeet.setTextSize(14);
            fleetFeet.setOnClickListener(v->applyFleetFeetPreset());
            LinearLayout.LayoutParams fp=new LinearLayout.LayoutParams(0,dp(48),1);fp.setMargins(dp(6),0,0,0);presets.addView(fleetFeet,fp);
        }'''
f = f.replace(generic_button, fleet_button, 1)
render_anchor = '    private void renderRows(){'
if f.count(render_anchor) != 1:
    raise SystemExit("Format row renderer missing")
fleet_method = '''    private void applyFleetFeetPreset(){
        order.clear();enabled.clear();
        String[] fields={"barcode","item_number","description","size"};
        for(String f:ALL){order.add(f);enabled.put(f,false);}
        for(String f:fields)enabled.put(f,true);
        selectedIndex=Math.max(0,order.indexOf("barcode"));renderRows();
    }

'''
f = f.replace(render_anchor, fleet_method + render_anchor, 1)
format_path.write_text(f)

text_path = root / "app/src/main/java/com/iceinventory/onhand/TabTextUtils.java"
t = text_path.read_text()
label = '        if("item_number".equals(field))return "ITEM NUMBER";'
if t.count(label) != 1:
    raise SystemExit("Tab import Item Number header recognition missing")
t = t.replace(label, label + '\n        if("size".equals(field))return "SIZE";', 1)

split_old = '    private static String[] split(String line){return line.split("\\\\t",-1);}'
split_new = '''    private static String[] split(String line){
        if(line.indexOf('\\t')>=0)return line.split("\\\\t",-1);
        ArrayList<String> fields=new ArrayList<>();StringBuilder value=new StringBuilder();boolean quoted=false;
        for(int i=0;i<line.length();i++){
            char c=line.charAt(i);
            if(c=='"'){
                if(quoted&&i+1<line.length()&&line.charAt(i+1)=='"'){value.append('"');i++;}
                else quoted=!quoted;
            }else if(c==','&&!quoted){fields.add(value.toString());value.setLength(0);}
            else value.append(c);
        }
        fields.add(value.toString());return fields.toArray(new String[0]);
    }'''
if t.count(split_old) != 1:
    raise SystemExit("Tab/CSV row splitter missing")
t = t.replace(split_old, split_new, 1)

item_field = '        if(f.equals("item number")||f.equals("item no")||f.equals("item #")||f.equals("itemnumber"))return "item_number";'
if t.count(item_field) != 1:
    raise SystemExit("Item Number field normalization missing")
t = t.replace(item_field, item_field + '\n        if(f.equals("size")||f.contains("size"))return "size";', 1)

desc_line = '        String desc=value(m,"description");'
size_logic = '''        String desc=value(m,"description");
        String size=value(m,"size").trim();
        if(!size.isEmpty())desc=(desc==null?"":desc.trim())+" [Size: "+size+"]";'''
if t.count(desc_line) != 1:
    raise SystemExit("Import description assignment missing")
t = t.replace(desc_line, size_logic, 1)

item_number_line = '        String itemNumber=value(m,"item_number");'
duplicate_description = '''        String itemNumber=value(m,"item_number");
        if(order.contains("size")&&order.contains("item_number")){
            InventoryDb.Row prior=db.latestForBarcode(sessionId,code);
            String oldItem=prior==null||prior.itemNumber==null?"":prior.itemNumber.trim();
            if(prior!=null&&oldItem.equals(itemNumber.trim())&&prior.description!=null&&prior.description.length()>desc.length())desc=prior.description;
        }'''
if t.count(item_number_line) != 1:
    raise SystemExit("Item Number import assignment missing")
t = t.replace(item_number_line, duplicate_description, 1)

export_description = '                else if("description".equals(f))b.append(clean(r.description));'
if t.count(export_description) != 1:
    raise SystemExit("Description export mapping missing")
t = t.replace(export_description, '                else if("description".equals(f))b.append(clean(order.contains("size")?descriptionWithoutSize(r.description):r.description));\n                else if("size".equals(f))b.append(clean(sizeFromDescription(r.description)));', 1)

export_header = '        if("item_number".equals(field))return "ITEM NUMBER";\n        if("size".equals(field))return "SIZE";'
# The previous replacement inserted this header block; confirm it now appears once.
if t.count(export_header) != 1:
    raise SystemExit("Size header mapping missing")

clean_marker = '    private static String clean(String s){'
if t.count(clean_marker) != 1:
    raise SystemExit("Text cleaning helper missing")
size_helpers = '''    private static String sizeFromDescription(String description){
        if(description==null)return "";int start=description.lastIndexOf(" [Size: ");
        if(start<0||!description.endsWith("]"))return "";
        return description.substring(start+8,description.length()-1).trim();
    }

    private static String descriptionWithoutSize(String description){
        if(description==null)return "";int start=description.lastIndexOf(" [Size: ");
        if(start<0||!description.endsWith("]"))return description;
        return description.substring(0,start).trim();
    }

'''
t = t.replace(clean_marker, size_helpers + clean_marker, 1)
text_path.write_text(t)

checks = {
    "version labels": "versionName '3.0.212'" in gradle.read_text() and "iCE Onhand 3.0.212" in manifest.read_text() and "Onhand Inventory 3.0.212" in main.read_text(),
    "Fleet Feet import preset": 'Button fleetFeet=button("Fleet Feet")' in f and 'String[] fields={"barcode","item_number","description","size"};' in f,
    "import format is reachable": 'button("Configure Import Format",0)' in s and 'FormatConfigActivity.MODE_IMPORT' in s,
    "imports use configured mapping": 'TabTextUtils.importRows(br,db,sessionId,prefs(),prefs().getBoolean(KEY_AUTO_GTIN,false))' in s,
    "CSV parsing": "if(line.indexOf(',')" in t or "else if(c==','&&!quoted)" in t,
    "size retained with description": '[Size: "+size+"]' in t,
    "item number retained": 'String itemNumber=value(m,"item_number");' in t and 'item_number' in t,
    "format workflow updated": ".github/prepare_30212.py" in workflow.read_text() and "3.0.212" in workflow.read_text(),
}
failed=[name for name,passed in checks.items() if not passed]
if failed:
    raise SystemExit("3.0.212 validation failed: "+", ".join(failed))
print("Prepared iCE OnHand 3.0.212 with Fleet Feet CSV import, item numbers, and size-aware descriptions.")
