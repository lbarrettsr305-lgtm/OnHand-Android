package com.iceinventory.onhand;

import android.graphics.Color;
import android.graphics.Typeface;
import android.view.Gravity;
import android.view.View;
import android.view.ViewGroup;
import android.widget.BaseAdapter;
import android.widget.Button;
import android.widget.ImageView;
import android.widget.LinearLayout;
import android.widget.TextView;

import java.util.ArrayList;
import java.util.List;
import java.util.Locale;

public final class InventoryAdapter extends BaseAdapter {
    public interface Listener {
        void onAddOne(InventoryDb.Row row);
        void onSubtractOne(InventoryDb.Row row);
        void onEdit(InventoryDb.Row row);
        String imageUrlFor(String barcode);
        void loadImageInto(String url, ImageView image, String expectedBarcode);
    }

    private final MainActivity context;
    private final Listener listener;
    private final ArrayList<InventoryDb.Row> rows = new ArrayList<>();
    private boolean compact;
    private boolean showImages;
    private boolean highlightLast;
    private String lastBarcode = "";

    public InventoryAdapter(MainActivity context, Listener listener) {
        this.context=context;
        this.listener=listener;
    }

    public void setRows(List<InventoryDb.Row> newRows) {
        rows.clear();
        if (newRows!=null) rows.addAll(newRows);
        notifyDataSetChanged();
    }

    public void setDisplayOptions(boolean compact, boolean showImages, boolean highlightLast, String lastBarcode) {
        this.compact=compact;
        this.showImages=showImages;
        this.highlightLast=highlightLast;
        this.lastBarcode=lastBarcode==null?"":lastBarcode;
        notifyDataSetChanged();
    }

    @Override public int getCount() { return rows.size(); }
    @Override public InventoryDb.Row getItem(int position) { return rows.get(position); }
    @Override public long getItemId(int position) { return rows.get(position).id; }

    private int dp(int n) { return Math.round(n * context.getResources().getDisplayMetrics().density); }

    private TextView text(String s, float size, int color, boolean bold) {
        TextView t=new TextView(context);
        t.setText(s);
        t.setTextSize(size);
        t.setTextColor(color);
        if (bold) t.setTypeface(Typeface.DEFAULT, Typeface.BOLD);
        return t;
    }

    private Button mini(String s) {
        Button b=new Button(context);
        b.setText(s);
        b.setAllCaps(false);
        b.setTextSize(compact?12:14);
        b.setMinHeight(0);
        b.setMinimumHeight(0);
        b.setMinWidth(0);
        b.setMinimumWidth(0);
        b.setPadding(dp(7),0,dp(7),0);
        b.setTextColor(Color.WHITE);
        b.setBackgroundResource(R.drawable.ice_button_green);
        return b;
    }

    @Override public View getView(int position, View convertView, ViewGroup parent) {
        InventoryDb.Row r=getItem(position);
        boolean active=highlightLast && r.barcode!=null && r.barcode.equals(lastBarcode);
        int bg=active?Color.rgb(255,215,0):Color.rgb(4,43,24);
        int primary=active?Color.BLACK:Color.WHITE;
        int secondary=active?Color.rgb(40,40,40):Color.rgb(205,220,210);

        LinearLayout root=new LinearLayout(context);
        root.setOrientation(LinearLayout.HORIZONTAL);
        root.setGravity(Gravity.CENTER_VERTICAL);
        root.setPadding(dp(compact?6:8),dp(compact?3:6),dp(compact?6:8),dp(compact?3:6));
        root.setBackgroundColor(bg);

        String imageUrl=showImages?listener.imageUrlFor(r.barcode):"";
        if (showImages && imageUrl!=null && !imageUrl.isEmpty()) {
            ImageView image=new ImageView(context);
            image.setTag(r.barcode);
            image.setScaleType(ImageView.ScaleType.CENTER_INSIDE);
            LinearLayout.LayoutParams ip=new LinearLayout.LayoutParams(dp(compact?34:46),dp(compact?34:46));
            ip.setMargins(0,0,dp(8),0);
            root.addView(image,ip);
            listener.loadImageInto(imageUrl,image,r.barcode);
        }

        LinearLayout center=new LinearLayout(context);
        center.setOrientation(LinearLayout.VERTICAL);
        center.setPadding(0,0,dp(6),0);

        String desc=r.description==null?"":r.description.trim();
        TextView description=text(desc.isEmpty()?r.barcode:desc, compact?13:15, primary, true);
        description.setSingleLine(false);
        description.setOnClickListener(v->listener.onAddOne(r));
        center.addView(description);

        String price=(r.price==null||r.price.trim().isEmpty())?"":"  •  $"+r.price.trim();
        String barcodeLine=(desc.isEmpty()?"":r.barcode)+price;
        if (!barcodeLine.isEmpty()) center.addView(text(barcodeLine,compact?11:12,secondary,false));

        root.addView(center,new LinearLayout.LayoutParams(0,ViewGroup.LayoutParams.WRAP_CONTENT,1));

        LinearLayout right=new LinearLayout(context);
        right.setOrientation(LinearLayout.VERTICAL);
        right.setGravity(Gravity.END);

        TextView q=text(String.format(Locale.US,"Qty: %d",r.quantity),compact?12:14,primary,true);
        q.setGravity(Gravity.END);
        right.addView(q);
        TextView loc=text(r.location==null?"Main":r.location,compact?11:12,secondary,false);
        loc.setGravity(Gravity.END);
        right.addView(loc);

        LinearLayout adjust=new LinearLayout(context);
        adjust.setOrientation(LinearLayout.HORIZONTAL);
        adjust.setGravity(Gravity.END);
        Button minus=mini("−");
        Button plus=mini("+");
        minus.setOnClickListener(v->listener.onSubtractOne(r));
        plus.setOnClickListener(v->listener.onAddOne(r));
        adjust.addView(minus,new LinearLayout.LayoutParams(dp(38),dp(compact?30:34)));
        LinearLayout.LayoutParams pp=new LinearLayout.LayoutParams(dp(38),dp(compact?30:34));
        pp.setMargins(dp(4),0,0,0);
        adjust.addView(plus,pp);
        if (!compact) right.addView(adjust);

        root.addView(right);
        root.setOnClickListener(v->listener.onEdit(r));
        return root;
    }
}
