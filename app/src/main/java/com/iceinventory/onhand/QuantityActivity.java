package com.iceinventory.onhand;

import android.app.Activity;
import android.content.Intent;
import android.graphics.Color;
import android.graphics.Typeface;
import android.os.Bundle;
import android.text.Editable;
import android.text.TextWatcher;
import android.view.Gravity;
import android.view.View;
import android.view.ViewGroup;
import android.widget.Button;
import android.widget.EditText;
import android.widget.GridLayout;
import android.widget.LinearLayout;
import android.widget.ScrollView;
import android.widget.TextView;

import java.util.Locale;

public class QuantityActivity extends Activity {
    public static final String EXTRA_BARCODE="barcode";
    public static final String EXTRA_DESCRIPTION="description";
    public static final String EXTRA_CURRENT_QTY="current_qty";
    public static final String EXTRA_QUANTITY="quantity";

    private EditText perUnit, cases;
    private EditText active;
    private TextView totalText;
    private Button addButton;
    private int total;

    private int dp(int n){return Math.round(n*getResources().getDisplayMetrics().density);}

    private TextView text(String s,float size,int color,boolean bold){
        TextView t=new TextView(this);
        t.setText(s);
        t.setTextSize(size);
        t.setTextColor(color);
        if(bold)t.setTypeface(Typeface.DEFAULT,Typeface.BOLD);
        return t;
    }

    @Override public void onCreate(Bundle savedInstanceState){
        super.onCreate(savedInstanceState);
        buildUi();
    }

    private void buildUi(){
        String barcode=getIntent().getStringExtra(EXTRA_BARCODE);
        String description=getIntent().getStringExtra(EXTRA_DESCRIPTION);
        int current=getIntent().getIntExtra(EXTRA_CURRENT_QTY,0);
        if(barcode==null)barcode="";
        if(description==null)description="";

        LinearLayout outer=new LinearLayout(this);
        outer.setOrientation(LinearLayout.VERTICAL);
        outer.setBackgroundColor(Color.WHITE);

        LinearLayout bar=new LinearLayout(this);
        bar.setOrientation(LinearLayout.HORIZONTAL);
        bar.setGravity(Gravity.CENTER_VERTICAL);
        bar.setPadding(dp(8),dp(8),dp(8),dp(8));
        bar.setBackgroundColor(Color.rgb(25,25,25));
        Button back=new Button(this);
        back.setText("‹");
        back.setTextSize(28);
        back.setTextColor(Color.WHITE);
        back.setBackgroundColor(Color.TRANSPARENT);
        back.setOnClickListener(v->finish());
        bar.addView(back,new LinearLayout.LayoutParams(dp(58),dp(54)));
        TextView title=text("Add Quantity",22,Color.WHITE,true);
        bar.addView(title,new LinearLayout.LayoutParams(0,ViewGroup.LayoutParams.WRAP_CONTENT,1));
        outer.addView(bar);

        ScrollView scroll=new ScrollView(this);
        LinearLayout body=new LinearLayout(this);
        body.setOrientation(LinearLayout.VERTICAL);
        body.setPadding(dp(14),dp(10),dp(14),dp(16));

        LinearLayout card=new LinearLayout(this);
        card.setOrientation(LinearLayout.VERTICAL);
        card.setGravity(Gravity.CENTER);
        card.setPadding(dp(12),dp(10),dp(12),dp(10));
        android.graphics.drawable.GradientDrawable cardBg=new android.graphics.drawable.GradientDrawable();
        cardBg.setColor(Color.rgb(255,247,205));
        cardBg.setStroke(dp(1),Color.rgb(220,170,0));
        cardBg.setCornerRadius(dp(8));
        card.setBackground(cardBg);
        TextView bc=text(barcode,18,Color.BLACK,true);bc.setGravity(Gravity.CENTER);card.addView(bc);
        if(!description.trim().isEmpty()){
            TextView ds=text(description.trim(),20,Color.BLACK,true);ds.setGravity(Gravity.CENTER);card.addView(ds);
        }
        TextView cq=text(String.format(Locale.US,"Current Qty: %d",current),17,Color.BLACK,true);cq.setGravity(Gravity.CENTER);card.addView(cq);
        body.addView(card,new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT,ViewGroup.LayoutParams.WRAP_CONTENT));

        TextView info=text("ⓘ  Enter the quantity you want to add.\n     You can enter a single amount\n     or use multiply (Qty × Cases).",15,Color.rgb(0,60,180),true);
        info.setPadding(dp(12),dp(10),dp(12),dp(10));
        android.graphics.drawable.GradientDrawable infoBg=new android.graphics.drawable.GradientDrawable();
        infoBg.setColor(Color.rgb(235,244,255));infoBg.setStroke(dp(1),Color.rgb(50,110,230));infoBg.setCornerRadius(dp(7));
        info.setBackground(infoBg);
        LinearLayout.LayoutParams infoLp=new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT,ViewGroup.LayoutParams.WRAP_CONTENT);
        infoLp.setMargins(0,dp(10),0,dp(10));
        body.addView(info,infoLp);

        LinearLayout labels=new LinearLayout(this);
        labels.setOrientation(LinearLayout.HORIZONTAL);
        TextView l1=text("Quantity per Unit / Case",14,Color.rgb(0,50,170),true);
        TextView l2=text("Number of Cases",14,Color.rgb(0,50,170),true);
        labels.addView(l1,new LinearLayout.LayoutParams(0,ViewGroup.LayoutParams.WRAP_CONTENT,1));
        labels.addView(l2,new LinearLayout.LayoutParams(0,ViewGroup.LayoutParams.WRAP_CONTENT,1));
        body.addView(labels);

        LinearLayout inputs=new LinearLayout(this);
        inputs.setOrientation(LinearLayout.HORIZONTAL);
        inputs.setGravity(Gravity.CENTER_VERTICAL);
        perUnit=new EditText(this);
        perUnit.setTextSize(20);perUnit.setTextColor(Color.BLACK);perUnit.setSingleLine(true);perUnit.setGravity(Gravity.CENTER);
        perUnit.setShowSoftInputOnFocus(false);
        cases=new EditText(this);
        cases.setTextSize(20);cases.setTextColor(Color.BLACK);cases.setSingleLine(true);cases.setGravity(Gravity.CENTER);
        cases.setShowSoftInputOnFocus(false);
        TextView times=text("×",30,Color.BLACK,true);times.setGravity(Gravity.CENTER);
        inputs.addView(perUnit,new LinearLayout.LayoutParams(0,dp(54),1));
        inputs.addView(times,new LinearLayout.LayoutParams(dp(60),dp(54)));
        inputs.addView(cases,new LinearLayout.LayoutParams(0,dp(54),1));
        body.addView(inputs);

        LinearLayout hints=new LinearLayout(this);hints.setOrientation(LinearLayout.HORIZONTAL);
        hints.addView(text("(e.g. 24 bottles per case)",12,Color.DKGRAY,false),new LinearLayout.LayoutParams(0,ViewGroup.LayoutParams.WRAP_CONTENT,1));
        hints.addView(text("(e.g. 10 cases)",12,Color.DKGRAY,false),new LinearLayout.LayoutParams(0,ViewGroup.LayoutParams.WRAP_CONTENT,1));
        body.addView(hints);

        LinearLayout totalRow=new LinearLayout(this);totalRow.setOrientation(LinearLayout.HORIZONTAL);totalRow.setPadding(dp(10),dp(8),dp(10),dp(8));
        totalRow.addView(text("Total to Add",18,Color.rgb(0,60,180),true),new LinearLayout.LayoutParams(0,ViewGroup.LayoutParams.WRAP_CONTENT,1));
        totalText=text("0",28,Color.rgb(25,130,35),true);totalText.setGravity(Gravity.END);
        totalRow.addView(totalText);
        LinearLayout.LayoutParams totalLp=new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT,ViewGroup.LayoutParams.WRAP_CONTENT);
        totalLp.setMargins(0,dp(10),0,dp(4));
        body.addView(totalRow,totalLp);

        addButton=new Button(this);
        addButton.setAllCaps(true);
        addButton.setText("ADD COUNT (0)");
        addButton.setTextColor(Color.WHITE);
        addButton.setTextSize(18);
        addButton.setTypeface(Typeface.DEFAULT,Typeface.BOLD);
        addButton.setBackgroundColor(Color.rgb(15,70,205));
        addButton.setOnClickListener(v->finishWithQuantity());
        body.addView(addButton,new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT,dp(56)));

        GridLayout keypad=new GridLayout(this);
        keypad.setColumnCount(4);
        keypad.setRowCount(4);
        keypad.setPadding(0,dp(10),0,0);
        String[] keys={"1","2","3","⌫","4","5","6","Clear","7","8","9","","","0","00",""};
        for(String k:keys){
            if(k.isEmpty()){
                View spacer=new View(this);
                keypad.addView(spacer,new ViewGroup.LayoutParams(0,0));
                GridLayout.LayoutParams lp=(GridLayout.LayoutParams)spacer.getLayoutParams();
                lp.width=0;lp.height=dp(54);lp.columnSpec=GridLayout.spec(GridLayout.UNDEFINED,1f);
                spacer.setLayoutParams(lp);
                continue;
            }
            Button b=new Button(this);b.setText(k);b.setAllCaps(false);b.setTextSize(18);b.setTextColor(Color.BLACK);
            b.setOnClickListener(v->pressKey(((Button)v).getText().toString()));
            GridLayout.LayoutParams lp=new GridLayout.LayoutParams();
            lp.width=0;lp.height=dp(54);lp.columnSpec=GridLayout.spec(GridLayout.UNDEFINED,1f);
            lp.setMargins(dp(2),dp(2),dp(2),dp(2));
            keypad.addView(b,lp);
        }
        body.addView(keypad);

        perUnit.setOnFocusChangeListener((v,has)->{if(has)active=perUnit;});
        cases.setOnFocusChangeListener((v,has)->{if(has)active=cases;});
        TextWatcher watcher=new TextWatcher(){
            @Override public void beforeTextChanged(CharSequence s,int st,int c,int a){}
            @Override public void onTextChanged(CharSequence s,int st,int before,int count){recalc();}
            @Override public void afterTextChanged(Editable e){}
        };
        perUnit.addTextChangedListener(watcher);cases.addTextChangedListener(watcher);
        perUnit.requestFocus();active=perUnit;

        scroll.addView(body);
        outer.addView(scroll,new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT,0,1));
        setContentView(outer);
    }

    private int value(EditText e){
        try{
            String s=e.getText().toString().trim();
            return s.isEmpty()?0:Integer.parseInt(s);
        }catch(Exception ex){return 0;}
    }

    private void recalc(){
        int a=value(perUnit);
        int b=value(cases);
        long result=b>0?(long)a*b:a;
        if(result>999999999L)result=999999999L;
        total=(int)result;
        totalText.setText(String.valueOf(total));
        addButton.setText("ADD COUNT ("+total+")");
        addButton.setEnabled(total>0);
    }

    private void pressKey(String key){
        if(active==null)active=perUnit;
        String s=active.getText().toString();
        if("Clear".equals(key)){active.setText("");return;}
        if("⌫".equals(key)){
            if(!s.isEmpty())active.setText(s.substring(0,s.length()-1));
            return;
        }
        if(s.length()<9)active.setText(s+key);
        active.setSelection(active.getText().length());
    }

    private void finishWithQuantity(){
        if(total<=0)return;
        Intent data=new Intent();
        data.putExtra(EXTRA_QUANTITY,total);
        setResult(RESULT_OK,data);
        finish();
    }
}
