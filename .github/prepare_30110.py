from pathlib import Path

# Preserve the signed 3.0.109 Excel audit reports.
base=Path('.github/prepare_30109.py')
exec(compile(base.read_text(),str(base),'exec'),{'__name__':'__main__','__file__':str(base)})

p=Path('app/src/main/java/com/iceinventory/onhand/MainActivity.java')
s=p.read_text()

# Replace the long plain-text export list with grouped, full-width buttons.
start=s.find('        String[] choices={"Export New Counts Only')
end_marker='        }).setNegativeButton("Cancel",null).show();'
end=s.find(end_marker,start)
if start<0 or end<0: raise SystemExit('3.0.110 target missing: Export Items list')
end+=len(end_marker)
buttons='''        final AlertDialog[] exportDialog=new AlertDialog[1];
        ScrollView exportScroll=new ScrollView(this);
        LinearLayout exportPanel=new LinearLayout(this);
        exportPanel.setOrientation(LinearLayout.VERTICAL);
        exportPanel.setPadding(dp(14),dp(8),dp(14),dp(8));
        exportScroll.addView(exportPanel);

        addExportSection(exportPanel,"INVENTORY EXPORTS");
        addExportButton(exportPanel,exportDialog,"Export New Counts — Batch "+batch,0);
        addExportButton(exportPanel,exportDialog,"Complete Inventory — TXT",1);
        addExportButton(exportPanel,exportDialog,"Complete Inventory — Excel",2);
        addExportButton(exportPanel,exportDialog,"Re-export Previous Batch",3);

        addExportSection(exportPanel,"COMBINE & SPECIAL REPORTS");
        addExportButton(exportPanel,exportDialog,"Combine & Verify User Batches",4);
        addExportButton(exportPanel,exportDialog,"Internet Items With Pictures",5);
        addExportButton(exportPanel,exportDialog,"Location Quantity Report",6);
        addExportButton(exportPanel,exportDialog,"Location Detail — TXT (Scan Order)",7);
        addExportButton(exportPanel,exportDialog,"Location Detail — Excel",8);

        addExportSection(exportPanel,"AUDIT VERIFICATION — COUNTED ITEMS ONLY");
        addExportButton(exportPanel,exportDialog,"Highest Unit Price — Excel",9);
        addExportButton(exportPanel,exportDialog,"Highest Extended Value — Excel",10);
        addExportButton(exportPanel,exportDialog,"Highest Quantity — Excel",11);

        exportDialog[0]=new AlertDialog.Builder(this).setTitle("Export Reports")
                .setView(exportScroll).setNegativeButton("Cancel",null).create();
        exportDialog[0].show();'''
s=s[:start]+buttons+s[end:]

marker_text='private void showExportScopeDialog'
marker_pos=s.find(marker_text)
if marker_pos<0: raise SystemExit('3.0.110 target missing: export method marker')
marker_start=s.rfind('\n',0,marker_pos)+1
marker=s[marker_start:marker_pos]+marker_text
helpers='''    private void addExportSection(LinearLayout panel,String title){
        TextView heading=new TextView(this);
        heading.setText(title);
        heading.setTextColor(Color.rgb(255,193,7));
        heading.setTextSize(14);
        heading.setTypeface(Typeface.DEFAULT,Typeface.BOLD);
        heading.setPadding(dp(4),dp(14),dp(4),dp(5));
        panel.addView(heading);
    }

    private void addExportButton(LinearLayout panel,final AlertDialog[] dialog,String title,int which){
        Button action=new Button(this);
        action.setText(title);
        action.setTextSize(16);
        action.setAllCaps(false);
        action.setGravity(Gravity.LEFT|Gravity.CENTER_VERTICAL);
        action.setOnClickListener(v->{if(dialog[0]!=null)dialog[0].dismiss();handleExportChoice(which);});
        LinearLayout.LayoutParams lp=new LinearLayout.LayoutParams(LinearLayout.LayoutParams.MATCH_PARENT,dp(54));
        lp.setMargins(0,0,0,dp(6));
        panel.addView(action,lp);
    }

    private void handleExportChoice(int which){
        pendingAuditSort=0;
        if(which==0){pendingExportExcel=false;pendingExportInternetOnly=false;pendingExportLocationQuantityReport=false;pendingExportLocationDetailReport=false;beginNewBatchExport();return;}
        if(which==1){pendingExportExcel=false;pendingExportInternetOnly=false;pendingExportLocationQuantityReport=false;pendingExportLocationDetailReport=false;beginCompleteInventoryExport();return;}
        if(which==2){pendingExportExcel=true;pendingExportInternetOnly=false;pendingExportLocationQuantityReport=false;pendingExportLocationDetailReport=false;beginCompleteInventoryExport();return;}
        if(which==3){pendingExportExcel=false;pendingExportInternetOnly=false;pendingExportLocationQuantityReport=false;pendingExportLocationDetailReport=false;showBatchReExportDialog();return;}
        if(which==4){pendingExportLocationDetailReport=false;resetBatchExportState();openBatchMergeForMaster();return;}
        resetBatchExportState();
        if(which==5){pendingExportExcel=false;pendingExportInternetOnly=true;pendingExportLocationQuantityReport=false;pendingExportLocationDetailReport=false;if(internetItemCount()==0){toast("No internet items to export");return;}startExportFormatFlow();return;}
        pendingExportExcel=false;pendingExportInternetOnly=false;
        if(which==6){pendingExportLocationQuantityReport=true;pendingExportLocationDetailReport=false;startExportFormatFlow();return;}
        if(which==7||which==8){pendingExportLocationQuantityReport=false;pendingExportLocationDetailReport=true;pendingExportExcel=(which==8);startExportFormatFlow();return;}
        pendingExportLocationQuantityReport=false;pendingExportLocationDetailReport=false;pendingExportExcel=true;
        pendingAuditSort=which==9?1:(which==10?2:3);startExportFormatFlow();
    }

'''+marker
s=s[:marker_start]+helpers+s[marker_start+len(marker):]

# Audit filenames now begin with the inventory/session name, never the user name.
old='''    private String auditExportFileName(String name) {
        String n=name==null?"":name.trim();
        String lower=n.toLowerCase(Locale.US);
        if(lower.endsWith(".xlsx"))n=n.substring(0,n.length()-5);
        else if(lower.endsWith(".txt"))n=n.substring(0,n.length()-4);
        String suffix=pendingAuditSort==1?" - Audit Highest Unit Price":(pendingAuditSort==2?" - Audit Highest Extended Value":" - Audit Highest Quantity");
        return cleanExcelName(n+suffix+".xlsx");
    }
'''
new='''    private String auditExportFileName(String ignored) {
        String n=sessionName==null||sessionName.trim().isEmpty()?"Inventory":sessionName.trim();
        String lower=n.toLowerCase(Locale.US);
        if(lower.endsWith(".xlsx"))n=n.substring(0,n.length()-5);
        else if(lower.endsWith(".txt"))n=n.substring(0,n.length()-4);
        String suffix=pendingAuditSort==1?" - Audit Highest Unit Price":(pendingAuditSort==2?" - Audit Highest Extended Value":" - Audit Highest Quantity");
        return cleanExcelName(n+suffix+".xlsx");
    }
'''
if old not in s: raise SystemExit('3.0.110 target missing: audit filename')
s=s.replace(old,new,1)
s=s.replace('Onhand Inventory 3.0.109','Onhand Inventory 3.0.110',1)
if 'Onhand Inventory 3.0.110' not in s: raise SystemExit('3.0.110 visible version target missing')
p.write_text(s)

# Audit reports are based only on actual positive counted quantities.
p=Path('app/src/main/java/com/iceinventory/onhand/SimpleXlsxWriter.java')
x=p.read_text()
old='''        List<InventoryDb.Row> sorted=new ArrayList<>(rows);
        Collections.sort(sorted,new Comparator<InventoryDb.Row>(){'''
new='''        List<InventoryDb.Row> sorted=new ArrayList<>();
        for(InventoryDb.Row row:rows)if(row.quantity>0)sorted.add(row);
        Collections.sort(sorted,new Comparator<InventoryDb.Row>(){'''
if old not in x: raise SystemExit('3.0.110 target missing: audit row selection')
x=x.replace(old,new,1)
p.write_text(x)

p=Path('app/build.gradle')
g=p.read_text().replace('versionCode 30109','versionCode 30110',1).replace("versionName '3.0.109'","versionName '3.0.110'",1)
if 'versionCode 30110' not in g or "versionName '3.0.110'" not in g: raise SystemExit('3.0.110 Gradle version target missing')
p.write_text(g)

p=Path('app/src/main/AndroidManifest.xml')
m=p.read_text().replace('iCE Onhand 3.0.109','iCE Onhand 3.0.110',1)
if 'iCE Onhand 3.0.110' not in m: raise SystemExit('3.0.110 manifest version target missing')
p.write_text(m)

main=Path('app/src/main/java/com/iceinventory/onhand/MainActivity.java').read_text()
xlsx=Path('app/src/main/java/com/iceinventory/onhand/SimpleXlsxWriter.java').read_text()
checks={
    'button export UI':all(v in main for v in ['Export Reports','AUDIT VERIFICATION — COUNTED ITEMS ONLY','addExportButton']),
    'counted only':'if(row.quantity>0)sorted.add(row)' in xlsx,
    'inventory first filename':'String n=sessionName==null' in main,
    'three audit reports':all(v in main for v in ['Highest Unit Price — Excel','Highest Extended Value — Excel','Highest Quantity — Excel']),
    'location reports retained':all(v in main for v in ['Location Detail — TXT (Scan Order)','Location Detail — Excel']),
}
missing=[k for k,v in checks.items() if not v]
if missing: raise SystemExit('3.0.110 verification failed: '+', '.join(missing))
print('Prepared iCE Onhand 3.0.110: counted-only audits, inventory-first names, grouped export buttons')
