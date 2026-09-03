package com.iceinventory.onhand;

import android.app.Activity;
import android.content.SharedPreferences;
import android.graphics.Color;
import android.graphics.Typeface;
import android.os.Bundle;
import android.view.Gravity;
import android.view.View;
import android.view.ViewGroup;
import android.widget.Button;
import android.widget.CheckBox;
import android.widget.LinearLayout;
import android.widget.ScrollView;
import android.widget.TextView;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.Locale;
import java.util.Map;

public class FormatConfigActivity extends Activity {
    public static final String EXTRA_MODE="mode";
    public static final String MODE_IMPORT="import";
    public static final String MODE_EXPORT="export";

    private static final String SETTINGS="onhand_settings";
    private static final String KEY_IMPORT="import_field_order";
    private static final String KEY_EXPORT="export_field_order";
    private static final String[] ALL={"barcode","description","price","quantity","location"};

    private final ArrayList<String> order=new ArrayList<>();
    private final Map<String,Boolean> enabled=new HashMap<>();
    private LinearLayout rows;
    private TextView preview;
    private String mode;

    private int dp(int n){return Math.round(n*getResources().getDisplayMetrics().density);}
    private int gold(){return Color.rgb(255,210,0);}
    private int green(){return Color.rgb(0,175,55);}

    @Override public void onCreate(Bundle savedInstanceState){
        super.onCreate(savedInstanceState);
        mode=getIntent().getStringExtra(EXTRA_MODE);
        if(!MODE_EXPORT.equals(mode))mode=MODE_IMPORT;
        load();
        buildUi();
    }

    private SharedPreferences prefs(){return getSharedPreferences(SETTINGS,MODE_PRIVATE);}

    private void load(){
        String key=MODE_EXPORT.equals(mode)?KEY_EXPORT:KEY_IMPORT;
        String saved=prefs().getString(key,"barcode,description,price,quantity,location");
        for(String part:saved.split(",")){
            String f=part.trim().toLowerCase(Locale.US);
            if(valid(f)&&!order.contains(f)){
                order.add(f);
                enabled.put(f,true);
            }
        }
        for(String f:ALL){
            if(!order.contains(f))order.add(f);
            if(!enabled.containsKey(f))enabled.put(f,false);
        }
        enabled.put("barcode",true);
    }

    private boolean valid(String f){
        for(String a:ALL)if(a.equals(f))return true;
        return false;
    }

    private String label(String f){
        if("barcode".equals(f))return "Barcode / UPC / GTIN";
        if("description".equals(f))return "Description";
        if("price".equals(f))return "Price";
        if("quantity".equals(f))return "Quantity";
        return "Location";
    }

    private TextView text(String s,float size,int color,boolean bold){
        TextView t=new TextView(this);t.setText(s);t.setTextSize(size);t.setTextColor(color);
        if(bold)t.setTypeface(Typeface.DEFAULT,Typeface.BOLD);
        return t;
    }

    private Button button(String s){
        Button b=new Button(this);b.setText(s);b.setAllCaps(false);b.setTextSize(16);b.setMinHeight(0);b.setMinimumHeight(0);
        return b;
    }

    private void buildUi(){
        LinearLayout root=new LinearLayout(this);root.setOrientation(LinearLayout.VERTICAL);root.setBackgroundColor(Color.rgb(8,18,20));

        LinearLayout top=new LinearLayout(this);top.setOrientation(LinearLayout.HORIZONTAL);top.setGravity(Gravity.CENTER_VERTICAL);top.setPadding(dp(8),dp(8),dp(8),dp(8));top.setBackgroundColor(Color.BLACK);
        Button back=button("‹");back.setTextSize(28);back.setTextColor(Color.WHITE);back.setBackgroundColor(Color.TRANSPARENT);back.setOnClickListener(v->finish());
        top.addView(back,new LinearLayout.LayoutParams(dp(58),dp(50)));
        top.addView(text(MODE_EXPORT.equals(mode)?"Configure Export Format":"Configure Import Format",21,Color.WHITE,true),new LinearLayout.LayoutParams(0,ViewGroup.LayoutParams.WRAP_CONTENT,1));
        root.addView(top);

        ScrollView scroll=new ScrollView(this);
        LinearLayout body=new LinearLayout(this);body.setOrientation(LinearLayout.VERTICAL);body.setPadding(dp(12),dp(10),dp(12),dp(14));
        body.addView(text("TXT file • TAB delimited",18,gold(),true));
        TextView help=text("Choose which fields are used and move them into the exact column order required. Barcode is required and cannot be removed.",14,Color.WHITE,false);
        help.setPadding(0,dp(4),0,dp(10));body.addView(help);

        rows=new LinearLayout(this);rows.setOrientation(LinearLayout.VERTICAL);body.addView(rows);

        preview=text("",14,Color.WHITE,true);preview.setPadding(dp(8),dp(10),dp(8),dp(10));preview.setBackgroundColor(Color.rgb(22,50,36));body.addView(preview);

        Button save=button("SAVE FORMAT");save.setTextColor(Color.WHITE);save.setTypeface(Typeface.DEFAULT,Typeface.BOLD);save.setBackgroundColor(green());save.setOnClickListener(v->saveAndFinish());
        LinearLayout.LayoutParams sp=new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT,dp(54));sp.setMargins(0,dp(12),0,0);body.addView(save,sp);

        Button defaults=button("Reset to Barcode → Description → Price → Quantity → Location");defaults.setOnClickListener(v->resetDefaults());
        LinearLayout.LayoutParams dpv=new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT,dp(52));dpv.setMargins(0,dp(6),0,0);body.addView(defaults,dpv);

        scroll.addView(body);root.addView(scroll,new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT,0,1));setContentView(root);
        renderRows();
    }

    private void renderRows(){
        rows.removeAllViews();
        for(int i=0;i<order.size();i++){
            final String field=order.get(i);
            final int index=i;
            LinearLayout row=new LinearLayout(this);row.setOrientation(LinearLayout.HORIZONTAL);row.setGravity(Gravity.CENTER_VERTICAL);row.setPadding(dp(4),dp(3),dp(4),dp(3));
            CheckBox box=new CheckBox(this);box.setText(label(field));box.setTextColor(Color.WHITE);box.setTextSize(16);box.setChecked(Boolean.TRUE.equals(enabled.get(field))||"barcode".equals(field));
            if("barcode".equals(field))box.setEnabled(false);
            box.setOnCheckedChangeListener((v,checked)->{enabled.put(field,checked);updatePreview();});
            row.addView(box,new LinearLayout.LayoutParams(0,dp(48),1));
            Button up=button("↑");up.setEnabled(index>0);up.setOnClickListener(v->move(index,index-1));
            Button down=button("↓");down.setEnabled(index<order.size()-1);down.setOnClickListener(v->move(index,index+1));
            row.addView(up,new LinearLayout.LayoutParams(dp(52),dp(44)));row.addView(down,new LinearLayout.LayoutParams(dp(52),dp(44)));
            rows.addView(row);
        }
        updatePreview();
    }

    private void move(int from,int to){
        if(to<0||to>=order.size())return;
        String f=order.remove(from);order.add(to,f);renderRows();
    }

    private void updatePreview(){
        StringBuilder b=new StringBuilder("Column order: ");int n=0;
        for(String f:order){
            if(!Boolean.TRUE.equals(enabled.get(f))&&!"barcode".equals(f))continue;
            if(n++>0)b.append("  ⇥  ");b.append(label(f));
        }
        preview.setText(b.toString());
    }

    private void resetDefaults(){
        order.clear();enabled.clear();
        for(String f:ALL){order.add(f);enabled.put(f,true);}renderRows();
    }

    private void saveAndFinish(){
        StringBuilder b=new StringBuilder();
        for(String f:order){
            boolean use="barcode".equals(f)||Boolean.TRUE.equals(enabled.get(f));
            if(!use)continue;
            if(b.length()>0)b.append(',');b.append(f);
        }
        if(b.indexOf("barcode")<0){if(b.length()>0)b.insert(0,',');b.insert(0,"barcode");}
        String key=MODE_EXPORT.equals(mode)?KEY_EXPORT:KEY_IMPORT;
        prefs().edit().putString(key,b.toString()).apply();setResult(RESULT_OK);finish();
    }
}
