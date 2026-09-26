from pathlib import Path

base = Path('.github/prepare_30168.py')
exec(compile(base.read_text(), str(base), 'exec'), {'__name__': '__main__', '__file__': str(base)})


def rep(path, old, new, label):
    p = Path(path); s = p.read_text()
    if s.count(old) != 1: raise SystemExit('3.0.169 target ' + label + ' count ' + str(s.count(old)))
    p.write_text(s.replace(old, new, 1))


rep('app/build.gradle', 'versionCode 30168', 'versionCode 30169', 'code')
rep('app/build.gradle', "versionName '3.0.168'", "versionName '3.0.169'", 'name')
rep('app/src/main/AndroidManifest.xml', 'iCE Onhand 3.0.168', 'iCE Onhand 3.0.169', 'manifest')
rep('app/src/main/java/com/iceinventory/onhand/MainActivity.java', 'Onhand Inventory 3.0.168', 'Onhand Inventory 3.0.169', 'header')

m='app/src/main/java/com/iceinventory/onhand/MonthlyInventoryActivity.java'
rep(m,
    'private TextView importSummary,status,nextStep;',
    'private TextView importSummary,status,nextStep,afterCountsGuide;\n    private ScrollView workflowScroll;',
    'guide fields')
rep(m,
    'ScrollView scroll=new ScrollView(this);',
    'workflowScroll=new ScrollView(this);ScrollView scroll=workflowScroll;',
    'workflow scroll field')

old='''        chooseCounts=button("5. Select All User Count Files");chooseCounts.setOnClickListener(v->pickCounts());root.addView(chooseCounts,params(58));
        approveExceptions=button("APPROVE MISSING ITEMS & COMPLETE INVENTORY");approveExceptions.setTextColor(Color.BLACK);approveExceptions.setBackgroundTintList(android.content.res.ColorStateList.valueOf(Color.rgb(255,193,7)));approveExceptions.setOnClickListener(v->approveMissingItems());root.addView(approveExceptions,params(62));
        saveUnmatched=button("EXPORT MISSING / NEW ITEMS — EXCEL");saveUnmatched.setTextColor(Color.BLACK);saveUnmatched.setBackgroundTintList(android.content.res.ColorStateList.valueOf(Color.rgb(255,193,7)));saveUnmatched.setOnClickListener(v->create(SAVE_UNMATCHED,"application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",base()+" MISSING NEW ITEMS-"+day()+".xlsx"));root.addView(saveUnmatched,params(58));
        saveCombined=button("6. Export Verified Combined TXT");saveCombined.setOnClickListener(v->create(SAVE_COMBINED,"text/plain",base()+" ALL-INVENTORY-"+day()+".txt"));root.addView(saveCombined,params(54));
        saveClient=button("7. CUSTOMER IMPORT REPORT");saveClient.setTypeface(android.graphics.Typeface.DEFAULT,android.graphics.Typeface.BOLD);saveClient.setTextColor(Color.BLACK);saveClient.setBackgroundTintList(android.content.res.ColorStateList.valueOf(Color.rgb(255,215,0)));saveClient.setOnClickListener(v->create(SAVE_CLIENT,"application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",base()+" CUSTOMER IMPORT REPORT-"+day()+".xlsx"));root.addView(saveClient,params(62));
        saveCombinedXlsx=button("COMPLETE COMBINED INVENTORY — EXCEL");saveCombinedXlsx.setTypeface(android.graphics.Typeface.DEFAULT,android.graphics.Typeface.BOLD);saveCombinedXlsx.setTextColor(Color.BLACK);saveCombinedXlsx.setBackgroundTintList(android.content.res.ColorStateList.valueOf(Color.rgb(0,190,90)));saveCombinedXlsx.setSingleLine(false);saveCombinedXlsx.setMaxLines(2);saveCombinedXlsx.setOnClickListener(v->create(SAVE_COMBINED_XLSX,"application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",base()+" COMPLETE COMBINED INVENTORY-"+day()+".xlsx"));root.addView(saveCombinedXlsx,params(70));'''
new='''        chooseCounts=button("5. SELECT ALL USER COUNT FILES");chooseCounts.setSingleLine(false);chooseCounts.setMaxLines(2);chooseCounts.setOnClickListener(v->pickCounts());root.addView(chooseCounts,params(68));
        afterCountsGuide=text("",16,Color.BLACK);afterCountsGuide.setTypeface(android.graphics.Typeface.DEFAULT,android.graphics.Typeface.BOLD);afterCountsGuide.setPadding(dp(14),dp(12),dp(14),dp(12));afterCountsGuide.setBackgroundColor(Color.rgb(255,215,0));afterCountsGuide.setVisibility(View.GONE);root.addView(afterCountsGuide);
        approveExceptions=button("6. REVIEW & APPROVE MISSING ITEMS");approveExceptions.setSingleLine(false);approveExceptions.setMaxLines(3);approveExceptions.setTextColor(Color.BLACK);approveExceptions.setBackgroundTintList(android.content.res.ColorStateList.valueOf(Color.rgb(255,193,7)));approveExceptions.setOnClickListener(v->approveMissingItems());root.addView(approveExceptions,params(76));
        saveClient=button("7. EXPORT CUSTOMER IMPORT — EXCEL");saveClient.setSingleLine(false);saveClient.setMaxLines(2);saveClient.setTypeface(android.graphics.Typeface.DEFAULT,android.graphics.Typeface.BOLD);saveClient.setTextColor(Color.BLACK);saveClient.setBackgroundTintList(android.content.res.ColorStateList.valueOf(Color.rgb(255,215,0)));saveClient.setOnClickListener(v->create(SAVE_CLIENT,"application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",base()+" CUSTOMER IMPORT REPORT-"+day()+".xlsx"));root.addView(saveClient,params(72));
        saveUnmatched=button("8. EXPORT MISSING / NEW ITEMS — EXCEL");saveUnmatched.setSingleLine(false);saveUnmatched.setMaxLines(3);saveUnmatched.setTextColor(Color.BLACK);saveUnmatched.setBackgroundTintList(android.content.res.ColorStateList.valueOf(Color.rgb(255,193,7)));saveUnmatched.setOnClickListener(v->create(SAVE_UNMATCHED,"application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",base()+" MISSING NEW ITEMS-"+day()+".xlsx"));root.addView(saveUnmatched,params(78));
        saveCombinedXlsx=button("9. COMPLETE COMBINED INVENTORY — EXCEL");saveCombinedXlsx.setTypeface(android.graphics.Typeface.DEFAULT,android.graphics.Typeface.BOLD);saveCombinedXlsx.setTextColor(Color.BLACK);saveCombinedXlsx.setBackgroundTintList(android.content.res.ColorStateList.valueOf(Color.rgb(0,190,90)));saveCombinedXlsx.setSingleLine(false);saveCombinedXlsx.setMaxLines(3);saveCombinedXlsx.setOnClickListener(v->create(SAVE_COMBINED_XLSX,"application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",base()+" COMPLETE COMBINED INVENTORY-"+day()+".xlsx"));root.addView(saveCombinedXlsx,params(78));
        saveCombined=button("10. EXPORT VERIFIED COMBINED — TXT");saveCombined.setSingleLine(false);saveCombined.setMaxLines(2);saveCombined.setOnClickListener(v->create(SAVE_COMBINED,"text/plain",base()+" ALL-INVENTORY-"+day()+".txt"));root.addView(saveCombined,params(68));'''
rep(m,old,new,'ordered post-count workflow')

rep(m,
    'saveAudit=button("Export Monthly Verification Report");saveAudit.setOnClickListener(v->create(SAVE_AUDIT,"text/plain",base()+" MONTHLY VERIFICATION-"+day()+".txt"));root.addView(saveAudit,params(54));',
    'saveAudit=button("11. EXPORT MONTHLY VERIFICATION — TXT");saveAudit.setSingleLine(false);saveAudit.setMaxLines(2);saveAudit.setOnClickListener(v->create(SAVE_AUDIT,"text/plain",base()+" MONTHLY VERIFICATION-"+day()+".txt"));root.addView(saveAudit,params(68));',
    'verification label')
rep(m,
    'closeProject=button("8. Close Monthly Project");',
    'closeProject=button("12. CLOSE MONTHLY PROJECT");',
    'close label')

old_end='''validated=countFiles.size()==uris.size()&&QuantityMath.equal(sourceTotal,combinedTotal)&&QuantityMath.equal(combinedTotal,clientTotal)&&unmatched.isEmpty();exceptionsApproved=unmatched.isEmpty();missingItemsExported=unmatched.isEmpty();countsReady=true;showValidation();setEnabledState();'''
new_end='''validated=countFiles.size()==uris.size()&&QuantityMath.equal(sourceTotal,combinedTotal)&&QuantityMath.equal(combinedTotal,clientTotal)&&unmatched.isEmpty();exceptionsApproved=unmatched.isEmpty();missingItemsExported=unmatched.isEmpty();countsReady=true;showValidation();showAfterCountsGuide();setEnabledState();'''
rep(m,old_end,new_end,'show next step after selection')

anchor='    private void showValidation(){'
method='''    private void showAfterCountsGuide(){if(afterCountsGuide==null)return;String message;if(unmatched.isEmpty())message="✓ VALIDATION PASSED\\n"+countFiles.size()+" user files • "+QuantityMath.format(combinedTotal)+" total units\\n\\nNEXT: Press 7. EXPORT CUSTOMER IMPORT — EXCEL";else message="VALIDATION COMPLETE — "+unmatched.size()+" MISSING / NEW ITEMS\\nFull audit total: "+QuantityMath.format(combinedTotal)+" • Missing quantity: "+QuantityMath.format(unmatchedQuantity())+"\\n\\nNEXT: Press 6. REVIEW & APPROVE MISSING ITEMS";afterCountsGuide.setText(message);afterCountsGuide.setVisibility(View.VISIBLE);afterCountsGuide.postDelayed(()->{if(workflowScroll!=null)workflowScroll.smoothScrollTo(0,Math.max(0,afterCountsGuide.getTop()-dp(24)));},200);}

'''
if anchor not in Path(m).read_text():raise SystemExit('3.0.169 guide anchor missing')
rep(m,anchor,method+anchor,'guide method')

s=Path(m).read_text()
checks={'version':"versionName '3.0.169'" in Path('app/build.gradle').read_text(),'guide':'showAfterCountsGuide();setEnabledState();' in s,'auto scroll':'workflowScroll.smoothScrollTo' in s,'ordered customer':s.find('7. EXPORT CUSTOMER')<s.find('8. EXPORT MISSING'),'no clipping':'params(78)' in s,'close':'12. CLOSE MONTHLY PROJECT' in s,'combined xlsx retained':'9. COMPLETE COMBINED INVENTORY' in s}
bad=[k for k,v in checks.items() if not v]
if bad:raise SystemExit('3.0.169 checks failed: '+', '.join(bad))
print('Prepared iCE OnHand 3.0.169: guided post-count workflow with readable action buttons')
