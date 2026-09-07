from pathlib import Path

base=Path('.github/prepare_3091.py')
exec(compile(base.read_text(),str(base),'exec'),{'__name__':'__main__','__file__':str(base)})

p=Path('app/src/main/java/com/iceinventory/onhand/MainActivity.java')
s=p.read_text()
old='''        View optionsBottomSpacer=new View(this);
        box.addView(optionsBottomSpacer,new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT,dp(16)));
'''
new='''        TextView batchesTitle=text("Multiple User Batches",16,gold(),true);batchesTitle.setPadding(dp(6),dp(8),0,dp(2));box.addView(batchesTitle);
        Button combineBatches=button("Combine and Verify User Batches",0);
        combineBatches.setOnClickListener(v->startActivity(new Intent(this,BatchMergeActivity.class)));
        box.addView(combineBatches,new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT,dp(52)));
        View optionsBottomSpacer=new View(this);
        box.addView(optionsBottomSpacer,new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT,dp(16)));
'''
if old not in s:raise SystemExit('3.0.92 target missing: Options bottom spacer')
s=s.replace(old,new,1).replace('Onhand Inventory 3.0.91','Onhand Inventory 3.0.92')
p.write_text(s)

p=Path('app/build.gradle');s=p.read_text().replace('versionCode 30091','versionCode 30092',1).replace("versionName '3.0.91'","versionName '3.0.92'",1);p.write_text(s)
p=Path('app/src/main/AndroidManifest.xml');s=p.read_text().replace('iCE Onhand 3.0.91','iCE Onhand 3.0.92');p.write_text(s)

main=Path('app/src/main/java/com/iceinventory/onhand/MainActivity.java').read_text()
merge=Path('app/src/main/java/com/iceinventory/onhand/BatchMergeActivity.java').read_text()
checks={'merge entry point':'Combine and Verify User Batches' in main,'multi-file selection':'Intent.EXTRA_ALLOW_MULTIPLE' in merge,'barcode sum':'Math.addExact(t.quantity,q)' in merge,'grand-total verification':'sourceGrandTotal==outputTotal' in merge,'blocked unverified export':'save.setEnabled(verified)' in merge,'tab output':'Quantity\\tBarcode' in merge}
missing=[k for k,v in checks.items() if not v]
if missing:raise SystemExit('3.0.92 verification failed: '+', '.join(missing))
print('Prepared iCE Onhand 3.0.92: verified multi-user batch consolidation')
