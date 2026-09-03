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
    private static final String KEY_EXPORT_POSITIVE_ONLY="export_quantity_above_zero_only";
    private static final String DEFAULT_ORDER="quantity,barcode,description,price";
    private static final String OLD_DEFAULT="barcode,description,price,quantity,location";
    private static final String[] ALL={"quantity","barcode","description","price","location","scan_date","scan_time"};

    private final ArrayList<String> order=new ArrayList<>();
    private final Map<String,Boolean> enabled=new HashMap<>();
    private LinearLayout rows;
    private TextView preview;
    private Button moveUp;
    private Button moveDown;
    private CheckBox positiveOnly;
    private String mode;
    private int selectedIndex=0;

    private int dp(int n){return Math.round(n*getResources().getDisplayMetrics().density);}
    private int gold(){return Color.rgb(255,210,0);}
    private int green(){return Color.rgb(0,175,55);}
    private int dark(){return Color.rgb(8,18,20);}
    private int rowDark(){return Color.rgb(18,42,35);}

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
        String saved=prefs().getString(key,DEFAULT_ORDER);
        if(saved==null||saved.trim().isEmpty()||OLD_DEFAULT.equals(saved.trim())){
            saved=DEFAULT_ORDER;
            prefs().edit().putString(key,DEFAULT_ORDER).apply();
        }
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
        if("quantity".equals(f))return "Quantity";
        if("barcode".equals(f))return "Barcode / UPC / GTIN";
        if("description".equals(f))return "Description";
        if("price".equals(f))return "Price";
        if("location".equals(f))return "Location";
        if("scan_date".equals(f))return "Scan Date";
        if("scan_time".equals(f))return "Scan Time";
        return f;
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
        LinearLayout root=new LinearLayout(this);root.setOrientation(LinearLayout.VERTICAL);root.setBackgroundColor(dark());

        LinearLayout top=new LinearLayout(this);top.setOrientation(LinearLayout.HORIZONTAL);top.setGravity(Gravity.CENTER_VERTICAL);top.setPadding(dp(8),dp(8),dp(8),dp(8));top.setBackgroundColor(Color.BLACK);
        Button back=button("‹");back.setTextSize(28);back.setTextColor(Color.WHITE);back.setBackgroundColor(Color.TRANSPARENT);back.setOnClickListener(v->finish());
        top.addView(back,new LinearLayout.LayoutParams(dp(58),dp(50)));
        top.addView(text(MODE_EXPORT.equals(mode)?"Configure Output Format":"Configure Import Format",21,Color.WHITE,true),new LinearLayout.LayoutParams(0,ViewGroup.LayoutParams.WRAP_CONTENT,1));
        root.addView(top);

        ScrollView scroll=new ScrollView(this);
        LinearLayout body=new LinearLayout(this);body.setOrientation(LinearLayout.VERTICAL);body.setPadding(dp(12),dp(10),dp(12),dp(14));
        body.addView(text("TXT file • TAB delimited",18,gold(),true));

        String helpText=MODE_EXPORT.equals(mode)
                ?"Standard order is Quantity, Barcode, Description, Price. Check Location, Scan Date or Scan Time only when you need them. Tap a row and use Move Up / Move Down to change its column position."
                :"Standard incoming order is Quantity, Barcode, Description, Price. Check optional fields only when they exist in the file, then use Move Up / Move Down to match the file. Barcode must remain included.";
        TextView help=text(helpText,14,Color.WHITE,false);help.setPadding(0,dp(5),0,dp(10));body.addView(help);

        rows=new LinearLayout(this);rows.setOrientation(LinearLayout.VERTICAL);body.addView(rows);

        LinearLayout moves=new LinearLayout(this);moves.setOrientation(LinearLayout.HORIZONTAL);moves.setPadding(0,dp(8),0,0);
        moveUp=button("↑ Move Up");moveDown=button("↓ Move Down");
        moveUp.setOnClickListener(v->moveSelected(-1));moveDown.setOnClickListener(v->moveSelected(1));
        moves.addView(moveUp,new LinearLayout.LayoutParams(0,dp(50),1));
        LinearLayout.LayoutParams mdp=new LinearLayout.LayoutParams(0,dp(50),1);mdp.setMargins(dp(6),0,0,0);moves.addView(moveDown,mdp);
        body.addView(moves);

        preview=text("",14,Color.WHITE,true);preview.setPadding(dp(8),dp(10),dp(8),dp(10));preview.setBackgroundColor(Color.rgb(22,50,36));
        LinearLayout.LayoutParams pp=new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT,ViewGroup.LayoutParams.WRAP_CONTENT);pp.setMargins(0,dp(8),0,0);body.addView(preview,pp);

        if(MODE_EXPORT.equals(mode)){
            positiveOnly=new CheckBox(this);
            positiveOnly.setText("Export only items with Quantity > 0");
            positiveOnly.setTextColor(Color.WHITE);
            positiveOnly.setTextSize(16);
            positiveOnly.setChecked(prefs().getBoolean(KEY_EXPORT_POSITIVE_ONLY,false));
            positiveOnly.setPadding(dp(6),dp(8),dp(6),dp(4));
            body.addView(positiveOnly,new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT,ViewGroup.LayoutParams.WRAP_CONTENT));
        }

        Button save=button(MODE_EXPORT.equals(mode)?"CONTINUE TO SAVE":"CONTINUE TO FILE");save.setTextColor(Color.WHITE);save.setTypeface(Typeface.DEFAULT,Typeface.BOLD);save.setBackgroundColor(green());save.setOnClickListener(v->saveAndFinish());
        LinearLayout.LayoutParams sp=new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT,dp(54));sp.setMargins(0,dp(12),0,0);body.addView(save,sp);

        Button defaults=button("Reset standard order");defaults.setOnClickListener(v->resetDefaults());
        LinearLayout.LayoutParams dpv=new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT,dp(50));dpv.setMargins(0,dp(6),0,0);body.addView(defaults,dpv);

        scroll.addView(body);root.addView(scroll,new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT,0,1));setContentView(root);
        renderRows();
    }

    private void renderRows(){
        rows.removeAllViews();
        if(selectedIndex<0)selectedIndex=0;
        if(selectedIndex>=order.size())selectedIndex=order.size()-1;

        for(int i=0;i<order.size();i++){
            final int index=i;
            final String field=order.get(i);
            final boolean selected=index==selectedIndex;

            LinearLayout row=new LinearLayout(this);row.setOrientation(LinearLayout.HORIZONTAL);row.setGravity(Gravity.CENTER_VERTICAL);row.setPadding(dp(10),dp(3),dp(8),dp(3));
            row.setBackgroundColor(selected?gold():rowDark());

            TextView number=text(String.valueOf(i+1)+".",17,selected?Color.BLACK:Color.WHITE,true);
            number.setGravity(Gravity.CENTER_VERTICAL);row.addView(number,new LinearLayout.LayoutParams(dp(34),dp(50)));

            TextView name=text(label(field),17,selected?Color.BLACK:Color.WHITE,true);
            name.setGravity(Gravity.CENTER_VERTICAL);row.addView(name,new LinearLayout.LayoutParams(0,dp(50),1));

            CheckBox use=new CheckBox(this);use.setChecked(Boolean.TRUE.equals(enabled.get(field))||"barcode".equals(field));
            use.setEnabled(!"barcode".equals(field));
            use.setContentDescription("Include "+label(field));
            use.setOnCheckedChangeListener((b,checked)->{enabled.put(field,checked);updatePreview();});
            row.addView(use,new LinearLayout.LayoutParams(dp(56),dp(50)));

            View.OnClickListener select=v->{selectedIndex=index;renderRows();};
            row.setOnClickListener(select);number.setOnClickListener(select);name.setOnClickListener(select);

            LinearLayout.LayoutParams rp=new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT,dp(54));rp.setMargins(0,0,0,dp(4));rows.addView(row,rp);
        }
        moveUp.setEnabled(selectedIndex>0);
        moveDown.setEnabled(selectedIndex>=0&&selectedIndex<order.size()-1);
        updatePreview();
    }

    private void moveSelected(int direction){
        int to=selectedIndex+direction;
        if(selectedIndex<0||to<0||to>=order.size())return;
        String field=order.remove(selectedIndex);order.add(to,field);selectedIndex=to;renderRows();
    }

    private void updatePreview(){
        StringBuilder b=new StringBuilder("File columns: ");int n=0;
        for(String f:order){
            if(!Boolean.TRUE.equals(enabled.get(f))&&!"barcode".equals(f))continue;
            if(n++>0)b.append("  →  ");b.append(label(f));
        }
        preview.setText(b.toString());
    }

    private void resetDefaults(){
        order.clear();enabled.clear();
        for(String f:ALL){order.add(f);enabled.put(f,false);}
        enabled.put("quantity",true);
        enabled.put("barcode",true);
        enabled.put("description",true);
        enabled.put("price",true);
        selectedIndex=0;renderRows();
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
        SharedPreferences.Editor editor=prefs().edit().putString(key,b.toString());
        if(MODE_EXPORT.equals(mode)&&positiveOnly!=null)editor.putBoolean(KEY_EXPORT_POSITIVE_ONLY,positiveOnly.isChecked());
        editor.apply();
        setResult(RESULT_OK);
        finish();
    }
}
