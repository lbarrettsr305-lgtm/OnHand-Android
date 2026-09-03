package com.iceinventory.onhand;

import android.app.Activity;
import android.app.AlertDialog;
import android.content.ContentValues;
import android.content.Context;
import android.content.Intent;
import android.content.SharedPreferences;
import android.graphics.Bitmap;
import android.graphics.BitmapFactory;
import android.graphics.Color;
import android.graphics.Typeface;
import android.media.AudioManager;
import android.media.ToneGenerator;
import android.net.Uri;
import android.os.Build;
import android.os.Bundle;
import android.os.VibrationEffect;
import android.os.Vibrator;
import android.provider.MediaStore;
import android.text.Editable;
import android.text.InputType;
import android.text.TextWatcher;
import android.util.Log;
import android.view.Gravity;
import android.view.KeyEvent;
import android.view.MotionEvent;
import android.view.View;
import android.view.ViewGroup;
import android.view.WindowInsets;
import android.view.inputmethod.InputMethodManager;
import android.widget.ArrayAdapter;
import android.widget.Button;
import android.widget.EditText;
import android.widget.ImageView;
import android.widget.LinearLayout;
import android.widget.ListView;
import android.widget.Spinner;
import android.widget.Switch;
import android.widget.TextView;
import android.widget.Toast;

import com.google.mlkit.vision.codescanner.GmsBarcodeScanner;
import com.google.mlkit.vision.codescanner.GmsBarcodeScanning;

import java.io.BufferedReader;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.io.OutputStream;
import java.net.HttpURLConnection;
import java.net.URL;
import java.nio.charset.StandardCharsets;
import java.text.SimpleDateFormat;
import java.util.ArrayList;
import java.util.Date;
import java.util.HashMap;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Locale;
import java.util.Map;

public class MainActivity extends Activity implements InventoryAdapter.Listener {
    private static final String TAG="iCE-Onhand";
    private static final int REQ_EXPORT=1002;
    private static final int REQ_IMPORT=1003;
    private static final int REQ_QUANTITY=1004;

    private static final String SETTINGS="onhand_settings";
    private static final String KEY_UNKNOWN_MODE="unknown_barcode_mode";
    private static final String KEY_AUTO_GTIN="auto_gtin14";
    private static final String KEY_BEEP="beep_on_scan";
    private static final String KEY_VIBRATE="vibrate_on_scan";
    private static final String KEY_SHOW_IMAGES="show_internet_images";
    private static final String KEY_HIGHLIGHT="highlight_last_scan";
    private static final String KEY_COMPACT="compact_list";
    private static final String INTERNET_PREFIX="iCE-";
    private static final String IMAGE_KEY_PREFIX="internet_image_";

    private InventoryDb db;
    private long sessionId;
    private String sessionName="Default Inventory";

    private EditText barcode;
    private EditText description;
    private EditText qty;
    private EditText search;
    private Spinner location;
    private TextView titleSession;
    private TextView summary;
    private ListView list;
    private InventoryAdapter adapter;

    private final ArrayList<InventoryDb.Row> allRows=new ArrayList<>();
    private final ArrayList<InventoryDb.Row> visibleRows=new ArrayList<>();
    private final Map<String,Bitmap> imageCache=new HashMap<>();

    private String currentPrice="";
    private String lastBarcode="";
    private int filterMode=0;
    private long pendingQuantityRowId=-1L;
    private String pendingQuantityBarcode="";
    private String pendingExportFileName="";

    @Override public void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        installCrashRecorder();
        try {
            initializeApp();
            showPreviousCrashIfAny();
        } catch (Throwable first) {
            Log.e(TAG,"Startup failed; attempting database recovery",first);
            try {
                if(db!=null)db.close();
                initializeApp();
            } catch(Throwable second) {
                showFatalStartup(first,second);
            }
        }
    }

    private void initializeApp() {
        db=new InventoryDb(this);
        db.verifyReady();
        List<InventoryDb.Session> sessions=db.sessions();
        if(sessions.isEmpty()) {
            sessionId=db.createSession("Default Inventory");
            sessionName="Default Inventory";
        } else {
            sessionId=sessions.get(0).id;
            sessionName=sessions.get(0).name;
        }
        buildUi();
        refreshLocations();
        refreshList();
    }

    private SharedPreferences prefs(){return getSharedPreferences(SETTINGS,MODE_PRIVATE);}
    private int dp(int n){return Math.round(n*getResources().getDisplayMetrics().density);}
    private int green(){return Color.rgb(0,180,45);}
    private int gold(){return Color.rgb(255,210,0);}
    private int darkGreen(){return Color.rgb(4,43,24);}

    private TextView text(String s,float size,int color,boolean bold) {
        TextView t=new TextView(this);
        t.setText(s);t.setTextSize(size);t.setTextColor(color);
        if(bold)t.setTypeface(Typeface.DEFAULT,Typeface.BOLD);
        return t;
    }

    private TextView label(String s) {
        TextView t=text(s,13,Color.WHITE,true);
        t.setPadding(dp(2),dp(3),0,dp(2));
        return t;
    }

    private Button button(String s,int type) {
        Button b=new Button(this);
        b.setText(s);b.setAllCaps(false);b.setTextSize(14);
        b.setTextColor(type==2?Color.BLACK:Color.WHITE);
        b.setMinHeight(0);b.setMinimumHeight(0);
        if(type==1)b.setBackgroundResource(R.drawable.ice_button_green);
        else if(type==2)b.setBackgroundResource(R.drawable.ice_button_gold);
        else b.setBackgroundColor(Color.rgb(50,50,50));
        return b;
    }

    private void styleEntry(EditText e) {
        e.setTextColor(Color.WHITE);
        e.setHintTextColor(Color.rgb(160,170,170));
        e.setBackgroundColor(Color.rgb(12,31,34));
        e.setPadding(dp(9),0,dp(9),0);
    }

    private void buildUi() {
        LinearLayout root=new LinearLayout(this);
        root.setOrientation(LinearLayout.VERTICAL);
        root.setBackgroundColor(Color.BLACK);
        root.setPadding(dp(10),dp(6),dp(10),dp(6));
        root.setOnApplyWindowInsetsListener((v,insets)->{
            int bottom=Build.VERSION.SDK_INT>=20?insets.getSystemWindowInsetBottom():0;
            v.setPadding(dp(10),dp(6),dp(10),Math.max(dp(6),bottom+dp(4)));
            return insets;
        });

        LinearLayout header=new LinearLayout(this);
        header.setOrientation(LinearLayout.HORIZONTAL);
        header.setGravity(Gravity.CENTER_VERTICAL);
        ImageView logo=new ImageView(this);
        logo.setImageResource(R.drawable.ice_onhand_icon);
        logo.setScaleType(ImageView.ScaleType.CENTER_INSIDE);
        LinearLayout.LayoutParams lpLogo=new LinearLayout.LayoutParams(dp(68),dp(68));
        lpLogo.setMargins(0,0,dp(8),0);
        header.addView(logo,lpLogo);

        LinearLayout heading=new LinearLayout(this);
        heading.setOrientation(LinearLayout.VERTICAL);
        TextView ice=text("iCE",31,gold(),true);
        TextView app=text("Onhand Inventory",21,Color.WHITE,true);
        titleSession=text(sessionName,19,gold(),true);
        heading.addView(ice);heading.addView(app);heading.addView(titleSession);
        header.addView(heading,new LinearLayout.LayoutParams(0,ViewGroup.LayoutParams.WRAP_CONTENT,1));
        root.addView(header);

        LinearLayout sessionBar=new LinearLayout(this);sessionBar.setOrientation(LinearLayout.HORIZONTAL);
        Button inventories=button("📁 Inventories",0);inventories.setOnClickListener(v->chooseSession());
        Button fresh=button("＋ New",0);fresh.setOnClickListener(v->newSession());
        Button options=button("⚙ Options",0);options.setOnClickListener(v->showOptions());
        sessionBar.addView(inventories,new LinearLayout.LayoutParams(0,dp(48),1));
        LinearLayout.LayoutParams mid=new LinearLayout.LayoutParams(0,dp(48),1);mid.setMargins(dp(4),0,dp(4),0);
        sessionBar.addView(fresh,mid);
        sessionBar.addView(options,new LinearLayout.LayoutParams(0,dp(48),1));
        root.addView(sessionBar);

        root.addView(label("Barcode"));
        LinearLayout scanBar=new LinearLayout(this);scanBar.setOrientation(LinearLayout.HORIZONTAL);
        barcode=new EditText(this);
        barcode.setSingleLine(true);barcode.setTextSize(18);barcode.setHint("Scan or type barcode");
        barcode.setInputType(InputType.TYPE_CLASS_TEXT);
        styleEntry(barcode);
        barcode.setShowSoftInputOnFocus(false);
        barcode.setOnTouchListener((v,event)->{
            if(event.getAction()==MotionEvent.ACTION_DOWN) {
                barcode.setShowSoftInputOnFocus(true);
                barcode.postDelayed(()->showKeyboard(barcode),60);
            }
            return false;
        });
        barcode.setOnFocusChangeListener((v,has)->{if(!has)barcode.setShowSoftInputOnFocus(false);});
        barcode.setOnEditorActionListener((v,action,event)->{
            if((event!=null&&event.getKeyCode()==KeyEvent.KEYCODE_ENTER)||action==6||action==5) {
                handleScannedBarcode(barcode.getText().toString().trim());
                return true;
            }
            return false;
        });
        Button scan=button("📷 Scan",1);scan.setOnClickListener(v->scanBarcode());
        Button gtin=button("GTIN",0);gtin.setOnClickListener(v->applyGtinButton());
        scanBar.addView(barcode,new LinearLayout.LayoutParams(0,dp(50),1));
        LinearLayout.LayoutParams sp=new LinearLayout.LayoutParams(dp(88),dp(50));sp.setMargins(dp(5),0,dp(5),0);
        scanBar.addView(scan,sp);scanBar.addView(gtin,new LinearLayout.LayoutParams(dp(72),dp(50)));
        root.addView(scanBar);

        root.addView(label("Description"));
        description=new EditText(this);description.setSingleLine(true);description.setHint("Enter description (optional)");description.setTextSize(16);
        styleEntry(description);root.addView(description,new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT,dp(48)));

        LinearLayout labels=new LinearLayout(this);labels.setOrientation(LinearLayout.HORIZONTAL);
        labels.addView(label("Quantity"),new LinearLayout.LayoutParams(0,ViewGroup.LayoutParams.WRAP_CONTENT,1));
        labels.addView(label("Location"),new LinearLayout.LayoutParams(0,ViewGroup.LayoutParams.WRAP_CONTENT,1));
        root.addView(labels);

        LinearLayout ql=new LinearLayout(this);ql.setOrientation(LinearLayout.HORIZONTAL);
        LinearLayout qbox=new LinearLayout(this);qbox.setOrientation(LinearLayout.HORIZONTAL);
        Button minus=button("−",0);minus.setOnClickListener(v->adjustQty(-1));
        qty=new EditText(this);qty.setSingleLine(true);qty.setText("");qty.setTextSize(19);qty.setGravity(Gravity.CENTER);
        qty.setInputType(InputType.TYPE_CLASS_NUMBER);styleEntry(qty);
        Button plus=button("+",1);plus.setOnClickListener(v->adjustQty(1));
        qbox.addView(minus,new LinearLayout.LayoutParams(dp(45),dp(48)));
        qbox.addView(qty,new LinearLayout.LayoutParams(0,dp(48),1));
        qbox.addView(plus,new LinearLayout.LayoutParams(dp(45),dp(48)));
        location=new Spinner(this);
        LinearLayout.LayoutParams qlp=new LinearLayout.LayoutParams(0,dp(50),1);qlp.setMargins(0,0,dp(6),0);
        ql.addView(qbox,qlp);
        ql.addView(location,new LinearLayout.LayoutParams(0,dp(50),1));
        root.addView(ql);

        LinearLayout actionBar=new LinearLayout(this);actionBar.setOrientation(LinearLayout.HORIZONTAL);
        Button add=button("＋  Add Count",1);add.setTypeface(Typeface.DEFAULT,Typeface.BOLD);add.setOnClickListener(v->addItem());
        Button addLoc=button("＋ Location",0);addLoc.setOnClickListener(v->addLocation());
        actionBar.addView(add,new LinearLayout.LayoutParams(0,dp(52),2));
        LinearLayout.LayoutParams al=new LinearLayout.LayoutParams(0,dp(52),1);al.setMargins(dp(6),0,0,0);
        actionBar.addView(addLoc,al);
        root.addView(actionBar);

        summary=text("",13,Color.WHITE,true);summary.setPadding(dp(2),dp(5),0,dp(3));root.addView(summary);

        LinearLayout reportBar=new LinearLayout(this);reportBar.setOrientation(LinearLayout.HORIZONTAL);
        Button totals=button("▥ Location Totals",0);totals.setOnClickListener(v->showLocationTotals());
        Button internet=button("◎ Internet Items",0);internet.setOnClickListener(v->showInternetItems());
        reportBar.addView(totals,new LinearLayout.LayoutParams(0,dp(44),1));
        LinearLayout.LayoutParams rbp=new LinearLayout.LayoutParams(0,dp(44),1);rbp.setMargins(dp(5),0,0,0);
        reportBar.addView(internet,rbp);
        root.addView(reportBar);

        LinearLayout searchBar=new LinearLayout(this);searchBar.setOrientation(LinearLayout.HORIZONTAL);
        search=new EditText(this);search.setSingleLine(true);search.setHint("Search items...");search.setTextSize(15);styleEntry(search);
        search.addTextChangedListener(new TextWatcher(){
            @Override public void beforeTextChanged(CharSequence s,int st,int c,int a){}
            @Override public void onTextChanged(CharSequence s,int st,int before,int count){applyFilter();}
            @Override public void afterTextChanged(Editable e){}
        });
        Button filter=button("▼",1);filter.setOnClickListener(v->showFilter());
        searchBar.addView(search,new LinearLayout.LayoutParams(0,dp(46),1));
        LinearLayout.LayoutParams flp=new LinearLayout.LayoutParams(dp(55),dp(46));flp.setMargins(dp(5),0,0,0);
        searchBar.addView(filter,flp);
        root.addView(searchBar);

        list=new ListView(this);
        list.setBackgroundColor(darkGreen());
        list.setDividerColor(gold());
        list.setDividerHeight(dp(1));
        adapter=new InventoryAdapter(this,this);
        list.setAdapter(adapter);
        root.addView(list,new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT,0,1));

        LinearLayout io=new LinearLayout(this);io.setOrientation(LinearLayout.HORIZONTAL);io.setPadding(0,dp(4),0,0);
        Button imp=button("⬇ Import CSV",1);imp.setTypeface(Typeface.DEFAULT,Typeface.BOLD);imp.setOnClickListener(v->importCsv());
        Button exp=button("⬆ Export CSV",2);exp.setTypeface(Typeface.DEFAULT,Typeface.BOLD);exp.setOnClickListener(v->showExportDialog());
        io.addView(imp,new LinearLayout.LayoutParams(0,dp(52),1));
        LinearLayout.LayoutParams ep=new LinearLayout.LayoutParams(0,dp(52),1);ep.setMargins(dp(6),0,0,0);
        io.addView(exp,ep);
        root.addView(io);

        setContentView(root);
        root.requestApplyInsets();
    }

    private void adjustQty(int delta) {
        int q=0;
        try{String s=qty.getText().toString().trim();if(!s.isEmpty())q=Integer.parseInt(s);}catch(Exception ignored){}
        q=Math.max(0,q+delta);
        qty.setText(q==0?"":String.valueOf(q));
        qty.setSelection(qty.getText().length());
    }

    private void applyGtinButton() {
        String code=barcode.getText().toString().trim();
        if(code.isEmpty()){toast("Enter or scan a barcode first");return;}
        String converted=toGtin14(code);
        if(converted.equals(code))toast("Barcode already GTIN-14 or cannot be converted");
        else {
            barcode.setText(converted);barcode.setSelection(converted.length());
            toast("Converted to GTIN-14");
        }
    }

    private String toGtin14(String code) {
        if(code==null)return "";
        String s=code.trim();
        if(!s.matches("\\d+"))return s;
        if(s.length()>=14)return s;
        StringBuilder b=new StringBuilder(14);
        for(int i=s.length();i<14;i++)b.append('0');
        b.append(s);
        return b.toString();
    }

    private String maybeGtin(String code) {
        return prefs().getBoolean(KEY_AUTO_GTIN,false)?toGtin14(code):code;
    }

    private void scanBarcode() {
        GmsBarcodeScanner scanner=GmsBarcodeScanning.getClient(this);
        scanner.startScan()
                .addOnSuccessListener(barcodeResult->{
                    String value=barcodeResult.getRawValue();
                    if(value==null||value.trim().isEmpty())toast("No barcode detected");
                    else handleScannedBarcode(value.trim());
                })
                .addOnCanceledListener(()->{})
                .addOnFailureListener(e->showError("Scanner error",e));
    }

    private void handleScannedBarcode(String rawCode) {
        String code=maybeGtin(rawCode==null?"":rawCode.trim());
        if(code.isEmpty()){toast("No barcode detected");return;}
        scanFeedback();
        barcode.setShowSoftInputOnFocus(false);
        barcode.setText(code);barcode.setSelection(code.length());
        qty.setText("");
        currentPrice="";

        InventoryDb.Row existing=db.latestForBarcode(sessionId,code);
        if(existing!=null) {
            description.setText(existing.description==null?"":existing.description);
            currentPrice=existing.price==null?"":existing.price;
            focusQuantity();
            return;
        }

        String mode=getUnknownBarcodeMode();
        if("ignore".equals(mode)) {
            barcode.setText("");description.setText("");qty.setText("");currentPrice="";
            toast("Unknown barcode ignored");
            focusBarcodeWithoutKeyboard();
            return;
        }

        description.setText("");
        if(!"search".equals(mode)) {
            focusQuantity();
            return;
        }

        toast("Searching internet for item...");
        final String lookupCode=code;
        new Thread(()->{
            try {
                BarcodeLookup.Result found=BarcodeLookup.lookup(lookupCode);
                runOnUiThread(()->{
                    if(!lookupCode.equals(barcode.getText().toString().trim()))return;
                    if(found!=null) {
                        String d=found.description==null?"":found.description.trim();
                        if(!d.isEmpty()&&!d.startsWith(INTERNET_PREFIX))d=INTERNET_PREFIX+d;
                        description.setText(d);
                        currentPrice=found.price==null?"":found.price.trim();
                        if(found.imageUrl!=null&&!found.imageUrl.trim().isEmpty()) {
                            prefs().edit().putString(IMAGE_KEY_PREFIX+lookupCode,found.imageUrl.trim()).apply();
                        }
                        toast(d.isEmpty()?"Internet item data found":"Internet item found");
                    } else toast("No internet item found");
                    focusQuantity();
                });
            } catch(Exception e) {
                runOnUiThread(()->{
                    if(!lookupCode.equals(barcode.getText().toString().trim()))return;
                    toast(e.getMessage()==null?"Internet lookup failed":e.getMessage());
                    focusQuantity();
                });
            }
        }).start();
    }

    private void scanFeedback() {
        SharedPreferences p=prefs();
        if(p.getBoolean(KEY_BEEP,true)) {
            try {
                ToneGenerator tg=new ToneGenerator(AudioManager.STREAM_NOTIFICATION,85);
                tg.startTone(ToneGenerator.TONE_PROP_BEEP,120);
                barcode.postDelayed(tg::release,180);
            } catch(Exception ignored){}
        }
        if(p.getBoolean(KEY_VIBRATE,true)) {
            try {
                Vibrator vib=(Vibrator)getSystemService(VIBRATOR_SERVICE);
                if(vib!=null&&vib.hasVibrator()) {
                    if(Build.VERSION.SDK_INT>=26)vib.vibrate(VibrationEffect.createOneShot(60,VibrationEffect.DEFAULT_AMPLITUDE));
                    else vib.vibrate(60);
                }
            } catch(Exception ignored){}
        }
    }

    private void focusQuantity() {
        qty.requestFocus();
        qty.setSelection(qty.getText().length());
        qty.postDelayed(()->showKeyboard(qty),80);
    }

    private void focusBarcodeWithoutKeyboard() {
        barcode.setShowSoftInputOnFocus(false);
        barcode.requestFocus();
        barcode.postDelayed(this::hideKeyboard,40);
        barcode.postDelayed(this::hideKeyboard,250);
    }

    private void showKeyboard(View view) {
        InputMethodManager imm=(InputMethodManager)getSystemService(Context.INPUT_METHOD_SERVICE);
        if(imm!=null)imm.showSoftInput(view,InputMethodManager.SHOW_IMPLICIT);
    }

    private void hideKeyboard() {
        View v=getCurrentFocus();
        if(v==null)v=barcode;
        InputMethodManager imm=(InputMethodManager)getSystemService(Context.INPUT_METHOD_SERVICE);
        if(imm!=null)imm.hideSoftInputFromWindow(v.getWindowToken(),0);
    }

    private void addItem() {
        String code=maybeGtin(barcode.getText().toString().trim());
        if(code.isEmpty()){toast("Enter or scan a barcode");focusBarcodeWithoutKeyboard();return;}
        String qText=qty.getText().toString().trim();
        if(qText.isEmpty()){toast("Enter quantity");focusQuantity();return;}
        int q;
        try{q=Integer.parseInt(qText);}catch(Exception e){toast("Quantity must be a number");focusQuantity();return;}
        if(q<=0){toast("Quantity must be greater than zero");focusQuantity();return;}
        String loc=location.getSelectedItem()==null?"Main":location.getSelectedItem().toString();
        db.addLocation(loc);
        db.addOrIncrement(sessionId,code,description.getText().toString(),currentPrice,q,loc);
        lastBarcode=code;
        barcode.setText("");description.setText("");qty.setText("");currentPrice="";
        refreshList();
        focusBarcodeWithoutKeyboard();
    }

    private void refreshLocations() {
        List<String> locs=db.locations();
        ArrayAdapter<String> a=new ArrayAdapter<>(this,android.R.layout.simple_spinner_dropdown_item,locs);
        location.setAdapter(a);
    }

    private void refreshList() {
        titleSession.setText(sessionName);
        allRows.clear();allRows.addAll(db.items(sessionId));
        int units=0;for(InventoryDb.Row r:allRows)units+=r.quantity;
        summary.setText(allRows.size()+" item lines  •  "+units+" total units");
        applyFilter();
    }

    private void applyFilter() {
        if(adapter==null)return;
        String q=search==null?"":search.getText().toString().trim().toLowerCase(Locale.US);
        String selectedLoc=location!=null&&location.getSelectedItem()!=null?location.getSelectedItem().toString():"";
        visibleRows.clear();
        for(InventoryDb.Row r:allRows) {
            if(filterMode==1&&r.quantity<=0)continue;
            if(filterMode==2&&(r.description==null||!r.description.startsWith(INTERNET_PREFIX)))continue;
            if(filterMode==3&&!selectedLoc.equalsIgnoreCase(r.location==null?"":r.location))continue;
            if(!q.isEmpty()) {
                String hay=((r.barcode==null?"":r.barcode)+" "+(r.description==null?"":r.description)+" "+(r.location==null?"":r.location)+" "+(r.price==null?"":r.price)).toLowerCase(Locale.US);
                if(!hay.contains(q))continue;
            }
            visibleRows.add(r);
        }
        SharedPreferences p=prefs();
        adapter.setDisplayOptions(p.getBoolean(KEY_COMPACT,true),p.getBoolean(KEY_SHOW_IMAGES,true),p.getBoolean(KEY_HIGHLIGHT,true),lastBarcode);
        adapter.setRows(visibleRows);
    }

    private void showFilter() {
        String[] choices={"All items","Counted items only","Internet items only","Current location only"};
        new AlertDialog.Builder(this).setTitle("Filter Items")
                .setSingleChoiceItems(choices,filterMode,(d,w)->{filterMode=w;d.dismiss();applyFilter();})
                .setNegativeButton("Cancel",null).show();
    }

    private void chooseSession() {
        List<InventoryDb.Session> sessions=db.sessions();
        String[] names=new String[sessions.size()];
        for(int i=0;i<sessions.size();i++)names[i]=sessions.get(i).name;
        new AlertDialog.Builder(this).setTitle("Inventories")
                .setItems(names,(d,w)->{
                    InventoryDb.Session s=sessions.get(w);
                    sessionId=s.id;sessionName=s.name;lastBarcode="";
                    refreshList();
                }).setNegativeButton("Cancel",null).show();
    }

    private void newSession() {
        EditText input=new EditText(this);input.setHint("Inventory name");
        new AlertDialog.Builder(this).setTitle("New Inventory").setView(input)
                .setPositiveButton("Create",(d,w)->{
                    String n=input.getText().toString().trim();
                    if(n.isEmpty())n="Inventory "+new SimpleDateFormat("yyyy-MM-dd HHmm",Locale.US).format(new Date());
                    sessionId=db.createSession(n);sessionName=n;lastBarcode="";
                    refreshList();
                }).setNegativeButton("Cancel",null).show();
    }

    private void addLocation() {
        EditText input=new EditText(this);input.setHint("Location name");
        new AlertDialog.Builder(this).setTitle("Add Location").setView(input)
                .setPositiveButton("Add",(d,w)->{
                    String n=input.getText().toString().trim();
                    if(!n.isEmpty()){db.addLocation(n);refreshLocations();toast("Location added");}
                }).setNegativeButton("Cancel",null).show();
    }

    private String getUnknownBarcodeMode(){return prefs().getString(KEY_UNKNOWN_MODE,"add");}

    private void showUnknownBarcodeMode() {
        String[] choices={"Add unknown barcode","Ignore unknown barcode","Search internet and add"};
        String mode=getUnknownBarcodeMode();
        int checked="ignore".equals(mode)?1:("search".equals(mode)?2:0);
        new AlertDialog.Builder(this).setTitle("Unknown Barcode")
                .setSingleChoiceItems(choices,checked,(d,w)->{
                    prefs().edit().putString(KEY_UNKNOWN_MODE,w==1?"ignore":(w==2?"search":"add")).apply();
                    d.dismiss();
                }).setNegativeButton("Cancel",null).show();
    }

    private Switch optionSwitch(String text,String key,boolean def) {
        Switch s=new Switch(this);s.setText(text);s.setTextColor(Color.WHITE);s.setTextSize(16);
        s.setChecked(prefs().getBoolean(key,def));
        s.setPadding(dp(8),dp(7),dp(8),dp(7));
        s.setOnCheckedChangeListener((b,checked)->{
            prefs().edit().putBoolean(key,checked).apply();
            if(KEY_COMPACT.equals(key)||KEY_SHOW_IMAGES.equals(key)||KEY_HIGHLIGHT.equals(key))applyFilter();
        });
        return s;
    }

    private void showOptions() {
        LinearLayout box=new LinearLayout(this);box.setOrientation(LinearLayout.VERTICAL);box.setPadding(dp(10),dp(4),dp(10),dp(4));box.setBackgroundColor(Color.rgb(8,24,27));
        TextView scanning=text("Scanning",16,gold(),true);scanning.setPadding(dp(6),dp(6),0,dp(2));box.addView(scanning);
        box.addView(optionSwitch("Auto Convert to GTIN-14",KEY_AUTO_GTIN,false));
        box.addView(optionSwitch("Beep on Scan",KEY_BEEP,true));
        box.addView(optionSwitch("Vibrate on Scan",KEY_VIBRATE,true));
        TextView display=text("Display",16,gold(),true);display.setPadding(dp(6),dp(8),0,dp(2));box.addView(display);
        box.addView(optionSwitch("Show Images (Internet Items)",KEY_SHOW_IMAGES,true));
        box.addView(optionSwitch("Highlight Last Scanned Item",KEY_HIGHLIGHT,true));
        box.addView(optionSwitch("Compact List View",KEY_COMPACT,true));
        Button unknown=button("Unknown Barcode Behavior: "+friendlyUnknownMode(),0);
        unknown.setOnClickListener(v->showUnknownBarcodeMode());
        box.addView(unknown,new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT,dp(50)));
        new AlertDialog.Builder(this).setTitle("Options").setView(box).setPositiveButton("Done",null).show();
    }

    private String friendlyUnknownMode() {
        String m=getUnknownBarcodeMode();
        return "ignore".equals(m)?"Ignore":"search".equals(m)?"Search Internet":"Add";
    }

    private void showLocationTotals() {
        Map<String,Integer> totals=new LinkedHashMap<>();int grand=0;
        for(InventoryDb.Row r:allRows) {
            String loc=r.location==null||r.location.trim().isEmpty()?"Main":r.location.trim();
            totals.put(loc,totals.getOrDefault(loc,0)+r.quantity);grand+=r.quantity;
        }
        if(totals.isEmpty()){toast("No counts to total yet");return;}
        StringBuilder m=new StringBuilder();
        for(Map.Entry<String,Integer> e:totals.entrySet())m.append(e.getKey()).append(": ").append(e.getValue()).append("\n");
        m.append("\nGrand Total: ").append(grand);
        new AlertDialog.Builder(this).setTitle("Quantity Totals by Location").setMessage(m.toString()).setPositiveButton("OK",null).show();
    }

    private void showInternetItems() {
        ArrayList<InventoryDb.Row> rows=new ArrayList<>();ArrayList<String> labels=new ArrayList<>();
        for(InventoryDb.Row r:allRows) {
            String d=r.description==null?"":r.description.trim();
            if(d.startsWith(INTERNET_PREFIX)) {
                rows.add(r);
                labels.add(d+"\n"+r.barcode+"   Qty "+r.quantity+"   "+r.location);
            }
        }
        if(rows.isEmpty()){toast("No internet-added items yet");return;}
        new AlertDialog.Builder(this).setTitle("Internet Items ("+rows.size()+")")
                .setItems(labels.toArray(new String[0]),(d,w)->showInternetItemDetail(rows.get(w)))
                .setNegativeButton("Close",null).show();
    }

    private void showInternetItemDetail(InventoryDb.Row r) {
        LinearLayout box=new LinearLayout(this);box.setOrientation(LinearLayout.VERTICAL);box.setPadding(dp(18),dp(8),dp(18),dp(8));
        String p=r.price==null||r.price.isEmpty()?"":"\nPrice: $"+r.price;
        TextView detail=text((r.description==null?"":r.description)+"\n\nBarcode: "+r.barcode+p+"\nQuantity: "+r.quantity+"\nLocation: "+r.location,16,Color.BLACK,false);
        box.addView(detail);
        String url=imageUrlFor(r.barcode);
        if(!url.isEmpty()) {
            ImageView image=new ImageView(this);image.setTag(r.barcode);image.setAdjustViewBounds(true);image.setScaleType(ImageView.ScaleType.CENTER_INSIDE);
            box.addView(image,new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT,dp(240)));
            loadImageInto(url,image,r.barcode);
        }
        new AlertDialog.Builder(this).setTitle("Internet Item").setView(box).setPositiveButton("OK",null).show();
    }

    @Override public void onAddOne(InventoryDb.Row row) {
        db.incrementQuantity(row.id,1);lastBarcode=row.barcode;refreshList();
    }

    @Override public void onSubtractOne(InventoryDb.Row row) {
        if(row.quantity<=0)return;
        db.incrementQuantity(row.id,-1);lastBarcode=row.barcode;refreshList();
    }

    @Override public void onEdit(InventoryDb.Row r) {
        LinearLayout box=new LinearLayout(this);box.setOrientation(LinearLayout.VERTICAL);box.setPadding(dp(18),0,dp(18),0);
        TextView info=text(r.barcode,15,Color.BLACK,true);box.addView(info);
        EditText d=new EditText(this);d.setHint("Description");d.setText(r.description==null?"":r.description);box.addView(d);
        EditText price=new EditText(this);price.setHint("Price");price.setInputType(InputType.TYPE_CLASS_NUMBER|InputType.TYPE_NUMBER_FLAG_DECIMAL);price.setText(r.price==null?"":r.price);box.addView(price);
        EditText q=new EditText(this);q.setHint("Quantity");q.setInputType(InputType.TYPE_CLASS_NUMBER|InputType.TYPE_NUMBER_FLAG_SIGNED);q.setText(String.valueOf(r.quantity));box.addView(q);
        Spinner loc=new Spinner(this);loc.setAdapter(new ArrayAdapter<>(this,android.R.layout.simple_spinner_dropdown_item,db.locations()));
        List<String> locs=db.locations();int sel=Math.max(0,locs.indexOf(r.location));loc.setSelection(sel);box.addView(loc);
        Button multiply=new Button(this);multiply.setText("Add Quantity / Cases");multiply.setAllCaps(false);multiply.setBackgroundColor(Color.rgb(20,75,205));multiply.setTextColor(Color.WHITE);
        box.addView(multiply,new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT,dp(50)));

        AlertDialog dialog=new AlertDialog.Builder(this).setTitle("Edit Count").setView(box)
                .setPositiveButton("Save",(dd,w)->{
                    int nq=r.quantity;try{nq=Integer.parseInt(q.getText().toString().trim());}catch(Exception ignored){}
                    String nl=loc.getSelectedItem()==null?"Main":loc.getSelectedItem().toString();
                    db.addLocation(nl);db.updateItem(r.id,d.getText().toString(),price.getText().toString().replace("$","").trim(),nq,nl);refreshList();
                })
                .setNeutralButton("Delete",(dd,w)->{db.deleteItem(r.id);refreshList();})
                .setNegativeButton("Cancel",null).create();
        multiply.setOnClickListener(v->{dialog.dismiss();launchQuantity(r);});
        dialog.show();
    }

    private void launchQuantity(InventoryDb.Row r) {
        pendingQuantityRowId=r.id;pendingQuantityBarcode=r.barcode;
        Intent i=new Intent(this,QuantityActivity.class);
        i.putExtra(QuantityActivity.EXTRA_BARCODE,r.barcode);
        i.putExtra(QuantityActivity.EXTRA_DESCRIPTION,r.description==null?"":r.description);
        i.putExtra(QuantityActivity.EXTRA_CURRENT_QTY,db.quantityForBarcode(sessionId,r.barcode));
        startActivityForResult(i,REQ_QUANTITY);
    }

    @Override public String imageUrlFor(String code) {
        if(code==null)return "";
        return prefs().getString(IMAGE_KEY_PREFIX+code,"");
    }

    @Override public void loadImageInto(String url,ImageView image,String expectedBarcode) {
        if(url==null||url.isEmpty())return;
        Bitmap cached=imageCache.get(url);
        if(cached!=null){image.setImageBitmap(cached);return;}
        new Thread(()->{
            Bitmap b=downloadBitmap(url);
            if(b!=null) {
                imageCache.put(url,b);
                runOnUiThread(()->{
                    Object tag=image.getTag();
                    if(tag!=null&&expectedBarcode.equals(String.valueOf(tag)))image.setImageBitmap(b);
                });
            }
        }).start();
    }

    private Bitmap downloadBitmap(String url) {
        HttpURLConnection conn=null;
        try {
            conn=(HttpURLConnection)new URL(url).openConnection();conn.setConnectTimeout(7000);conn.setReadTimeout(7000);conn.setDoInput(true);conn.connect();
            try(InputStream in=conn.getInputStream()){return BitmapFactory.decodeStream(in);}
        } catch(Exception e){Log.w(TAG,"Image load failed",e);return null;}
        finally{if(conn!=null)conn.disconnect();}
    }

    private void importCsv() {
        Intent i=new Intent(Intent.ACTION_OPEN_DOCUMENT);i.addCategory(Intent.CATEGORY_OPENABLE);i.setType("text/*");startActivityForResult(i,REQ_IMPORT);
    }

    private void showExportDialog() {
        EditText name=new EditText(this);
        name.setSingleLine(true);
        name.setText(safeFileName(sessionName)+"_"+new SimpleDateFormat("yyyy-MM-dd_HHmm",Locale.US).format(new Date())+".csv");
        name.setSelection(name.getText().length());
        new AlertDialog.Builder(this).setTitle("Export CSV").setMessage("Choose export location and file name").setView(name)
                .setPositiveButton("Save to Downloads",(d,w)->saveToDownloads(cleanCsvName(name.getText().toString())))
                .setNeutralButton("Save to Google Drive",(d,w)->startDocumentExport(cleanCsvName(name.getText().toString())))
                .setNegativeButton("Cancel",null).show();
    }

    private String cleanCsvName(String s) {
        String n=s==null?"":s.trim();if(n.isEmpty())n=safeFileName(sessionName)+".csv";if(!n.toLowerCase(Locale.US).endsWith(".csv"))n+=".csv";return n;
    }

    private void saveToDownloads(String filename) {
        if(Build.VERSION.SDK_INT<29){startDocumentExport(filename);return;}
        try {
            ContentValues values=new ContentValues();
            values.put(MediaStore.Downloads.DISPLAY_NAME,filename);
            values.put(MediaStore.Downloads.MIME_TYPE,"text/csv");
            values.put(MediaStore.Downloads.RELATIVE_PATH,"Download/");
            Uri uri=getContentResolver().insert(MediaStore.Downloads.EXTERNAL_CONTENT_URI,values);
            if(uri==null)throw new Exception("Could not create file in Downloads");
            writeExport(uri);
            toast("Saved to Downloads: "+filename);
        } catch(Exception e){showError("Export failed",e);}
    }

    private void startDocumentExport(String filename) {
        pendingExportFileName=filename;
        Intent i=new Intent(Intent.ACTION_CREATE_DOCUMENT);i.addCategory(Intent.CATEGORY_OPENABLE);i.setType("text/csv");i.putExtra(Intent.EXTRA_TITLE,filename);
        startActivityForResult(i,REQ_EXPORT);
        toast("Choose Google Drive or another folder");
    }

    private String safeFileName(String s){return (s==null?"Inventory":s).replaceAll("[^A-Za-z0-9._-]+","_");}

    @Override protected void onActivityResult(int requestCode,int resultCode,Intent data) {
        super.onActivityResult(requestCode,resultCode,data);
        if(resultCode!=RESULT_OK||data==null)return;
        if(requestCode==REQ_EXPORT)writeExport(data.getData());
        else if(requestCode==REQ_IMPORT)readImport(data.getData());
        else if(requestCode==REQ_QUANTITY) {
            int amount=data.getIntExtra(QuantityActivity.EXTRA_QUANTITY,0);
            if(amount>0&&pendingQuantityRowId>0) {
                db.incrementQuantity(pendingQuantityRowId,amount);lastBarcode=pendingQuantityBarcode;refreshList();
            }
            pendingQuantityRowId=-1;pendingQuantityBarcode="";
        }
    }

    private void writeExport(Uri uri) {
        if(uri==null)return;
        try(OutputStream os=getContentResolver().openOutputStream(uri)) {
            if(os==null)throw new Exception("No output stream");
            os.write(CsvUtils.exportRows(db.items(sessionId)).getBytes(StandardCharsets.UTF_8));
            toast("CSV exported");
        } catch(Exception e){showError("Export failed",e);}
    }

    private int findHeader(List<String> fields,String... names) {
        for(int i=0;i<fields.size();i++) {
            String f=fields.get(i).trim().toLowerCase(Locale.US).replace("_"," ").replace("-"," ");
            for(String n:names)if(f.equals(n)||f.contains(n))return i;
        }
        return -1;
    }

    private String field(List<String> f,int index) {
        return index>=0&&index<f.size()?f.get(index).trim():"";
    }

    private void readImport(Uri uri) {
        if(uri==null)return;
        int imported=0;
        try(InputStream is=getContentResolver().openInputStream(uri);
            BufferedReader br=new BufferedReader(new InputStreamReader(is,StandardCharsets.UTF_8))) {
            String firstLine=null;
            while((firstLine=br.readLine())!=null&&firstLine.trim().isEmpty()){}
            if(firstLine==null){toast("CSV is empty");return;}
            List<String> first=CsvUtils.parseLine(firstLine);
            int b=findHeader(first,"barcode","upc","gtin");
            boolean header=b>=0;
            int di=header?findHeader(first,"description","item description","name"):1;
            int qi=header?findHeader(first,"quantity","qty","onhand","on hand","count"):2;
            int li=header?findHeader(first,"location","loc","area"):3;
            int pi=header?findHeader(first,"price","retail","cost"):4;
            if(!header)b=0;

            if(!header)imported+=importRow(first,b,di,qi,li,pi);
            String line;
            while((line=br.readLine())!=null) {
                if(line.trim().isEmpty())continue;
                imported+=importRow(CsvUtils.parseLine(line),b,di,qi,li,pi);
            }
            refreshLocations();refreshList();toast("Imported "+imported+" rows");
        } catch(Exception e){showError("Import failed",e);}
    }

    private int importRow(List<String> f,int bi,int di,int qi,int li,int pi) {
        String code=field(f,bi);
        if(code.isEmpty())return 0;
        code=maybeGtin(code);
        String desc=field(f,di);
        String price=field(f,pi).replace("$","").trim();
        int q=0;try{String s=field(f,qi);if(!s.isEmpty())q=Integer.parseInt(s);}catch(Exception ignored){}
        String loc=field(f,li);if(loc.isEmpty())loc="Main";
        db.addLocation(loc);db.addOrIncrement(sessionId,code,desc,price,q,loc);
        return 1;
    }

    private void showError(String title,Exception e) {
        new AlertDialog.Builder(this).setTitle(title).setMessage(e.getMessage()==null?e.toString():e.getMessage()).setPositiveButton("OK",null).show();
    }

    private void toast(String s){Toast.makeText(this,s,Toast.LENGTH_SHORT).show();}

    private void installCrashRecorder() {
        final Thread.UncaughtExceptionHandler prior=Thread.getDefaultUncaughtExceptionHandler();
        Thread.setDefaultUncaughtExceptionHandler((thread,error)->{
            try{getSharedPreferences("onhand_diag",MODE_PRIVATE).edit().putString("last_crash",Log.getStackTraceString(error)).apply();}catch(Throwable ignored){}
            if(prior!=null)prior.uncaughtException(thread,error);
        });
    }

    private void showPreviousCrashIfAny() {
        SharedPreferences p=getSharedPreferences("onhand_diag",MODE_PRIVATE);
        String crash=p.getString("last_crash",null);
        if(crash==null||crash.trim().isEmpty())return;
        p.edit().remove("last_crash").apply();
        String shortCrash=crash.length()>2200?crash.substring(0,2200):crash;
        new AlertDialog.Builder(this).setTitle("Previous crash details").setMessage(shortCrash).setPositiveButton("OK",null).show();
    }

    private void showFatalStartup(Throwable first,Throwable second) {
        LinearLayout root=new LinearLayout(this);root.setOrientation(LinearLayout.VERTICAL);root.setPadding(dp(20),dp(20),dp(20),dp(20));root.setBackgroundColor(Color.BLACK);
        TextView h=text("iCE Onhand could not start",22,gold(),true);root.addView(h);
        TextView d=text("Startup error:\n"+first+"\n\nRecovery error:\n"+second,14,Color.WHITE,false);d.setTextIsSelectable(true);
        root.addView(d,new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT,0,1));
        Button retry=button("Retry",1);retry.setOnClickListener(v->recreate());root.addView(retry);
        setContentView(root);
    }
}
