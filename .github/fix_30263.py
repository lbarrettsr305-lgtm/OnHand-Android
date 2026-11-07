from pathlib import Path
helper=Path(".github/ocr/DescriptionTextChoices.java")
Path("app/src/main/java/com/iceinventory/onhand/DescriptionTextChoices.java").write_text(helper.read_text())
tests=Path(".github/ocr/DescriptionTextChoicesTest.java")
Path("app/src/test/java/com/iceinventory/onhand/DescriptionTextChoicesTest.java").write_text(tests.read_text())
p=Path("app/src/main/java/com/iceinventory/onhand/DescriptionScanActivity.java")
s=p.read_text()
marker='    private volatile java.util.ArrayList<String> latestLines=new java.util.ArrayList<>();'
assert s.count(marker)==1
s=s.replace(marker,marker+'\n    private volatile java.util.ArrayList<String> latestChoices=new java.util.ArrayList<>();',1)
old='hint.setText("Frame the label. Select separate text lines to combine them.")'
assert old in s
s=s.replace(old,'hint.setText("Frame the full label, including size. Choose the text for your description.")',1)
start=s.index("    private String suggestNameAndSize(Text result){")
end=s.index("    private java.util.ArrayList<String> extractLines(",start)
s=s[:start]+'''    private String suggestNameAndSize(Text result){
        latestLines=extractLines(result);
        java.util.ArrayList<DescriptionTextChoices.Line> candidates=new java.util.ArrayList<>();
        for(Text.TextBlock block:result.getTextBlocks()){
            boolean retailer=DescriptionTextChoices.isRetailerBlock(block.getText());
            for(Text.Line line:block.getLines()){
                float height=1;
                android.graphics.Point[] corners=line.getCornerPoints();
                if(corners!=null&&corners.length>=3){
                    height=(float)Math.min(Math.hypot(corners[1].x-corners[0].x,corners[1].y-corners[0].y),
                            Math.hypot(corners[2].x-corners[1].x,corners[2].y-corners[1].y));
                }else if(line.getBoundingBox()!=null){
                    height=Math.min(line.getBoundingBox().width(),line.getBoundingBox().height());
                }
                candidates.add(new DescriptionTextChoices.Line(line.getText(),height,retailer));
            }
        }
        latestChoices=new java.util.ArrayList<>(DescriptionTextChoices.shortlist(candidates));
        return DescriptionSuggestion.suggest(latestChoices);
    }

'''+s[end:]
start=s.index("    private void showTextAreaPicker(){")
end=s.index("    private String cleanLine(",start)
s=s[:start]+'''    private void showTextAreaPicker(){
        // Freeze this frame so live camera updates cannot replace checked choices.
        java.util.ArrayList<String> raw=new java.util.ArrayList<>(DescriptionTextChoices.allText(latestLines));
        java.util.ArrayList<String> focused=new java.util.ArrayList<>(latestChoices);
        java.util.ArrayList<String> all=new java.util.ArrayList<>(focused);
        if(raw.isEmpty()){Toast.makeText(this,"No readable text areas yet",Toast.LENGTH_SHORT).show();return;}
        for(String value:raw){
            boolean exists=false;
            for(String original:all)if(DescriptionTextChoices.key(original).equals(DescriptionTextChoices.key(value))){exists=true;break;}
            if(!exists)all.add(value);
        }
        java.util.HashSet<String> selected=new java.util.HashSet<>();
        boolean[] showAll={false};
        LinearLayout panel=new LinearLayout(this);
        panel.setOrientation(LinearLayout.VERTICAL);
        panel.setPadding(dp(16),dp(8),dp(16),dp(8));
        TextView instruction=new TextView(this);
        instruction.setText("Choose brand, product, style/color and size. Show All Text includes anything filtered out.");
        instruction.setTextSize(16);instruction.setTextColor(Color.WHITE);
        instruction.setPadding(0,0,0,dp(8));panel.addView(instruction);
        Button toggle=new Button(this);toggle.setAllCaps(false);
        panel.addView(toggle,new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT,dp(48)));
        LinearLayout choices=new LinearLayout(this);choices.setOrientation(LinearLayout.VERTICAL);
        android.widget.ScrollView scroll=new android.widget.ScrollView(this);scroll.addView(choices);
        panel.addView(scroll,new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT,(int)(getResources().getDisplayMetrics().heightPixels*0.48f)));
        Runnable render=()->{
            choices.removeAllViews();
            toggle.setText(showAll[0]?"SHOW RELEVANT TEXT":"SHOW ALL TEXT");
            java.util.List<String> visible=showAll[0]?all:focused;
            if(visible.isEmpty()){
                TextView empty=new TextView(this);
                empty.setText("No clear product details found. Tap SHOW ALL TEXT, or cancel and frame the front label again.");
                empty.setTextColor(Color.WHITE);empty.setTextSize(18);
                empty.setPadding(0,dp(12),0,dp(12));choices.addView(empty);
            }
            for(String value:visible){
                String key=DescriptionTextChoices.key(value);
                android.widget.CheckBox choice=new android.widget.CheckBox(this);
                choice.setText(value);choice.setTextSize(25);choice.setTextColor(Color.WHITE);
                choice.setMinHeight(dp(56));choice.setPadding(dp(4),dp(8),dp(4),dp(8));
                choice.setChecked(selected.contains(key));
                choice.setOnCheckedChangeListener((button,checked)->{
                    if(checked)selected.add(key);else selected.remove(key);
                });
                choices.addView(choice,new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT,ViewGroup.LayoutParams.WRAP_CONTENT));
            }
            scroll.scrollTo(0,0);
        };
        toggle.setOnClickListener(v->{showAll[0]=!showAll[0];render.run();});
        render.run();
        AlertDialog dialog=new AlertDialog.Builder(this)
            .setTitle("Choose description text")
            .setView(panel)
            .setNegativeButton("CANCEL",null)
            .setPositiveButton("USE SELECTED",null)
            .create();
        dialog.setOnShowListener(ignored->dialog.getButton(AlertDialog.BUTTON_POSITIVE).setOnClickListener(v->{
            java.util.ArrayList<String> values=new java.util.ArrayList<>();
            for(String value:all)if(selected.contains(DescriptionTextChoices.key(value)))values.add(value);
            String combined=DescriptionSuggestion.combineSelected(values);
            if(combined.isEmpty()){
                Toast.makeText(this,"Select at least one text line",Toast.LENGTH_SHORT).show();
                return;
            }
            dialog.dismiss();returnText(combined);
        }));
        dialog.show();
    }

'''+s[end:]
p.write_text(s)
p=Path("app/build.gradle");s=p.read_text()
assert "versionCode 30262" in s and "versionName '3.0.262'" in s
p.write_text(s.replace("versionCode 30262","versionCode 30263").replace("versionName '3.0.262'","versionName '3.0.263'"))
print("Applied 3.0.263: focused OCR choices, size detection, geometry ranking and reversible Show All Text.")
