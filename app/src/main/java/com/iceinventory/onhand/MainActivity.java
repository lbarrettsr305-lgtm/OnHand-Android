package com.iceinventory.onhand;

import android.app.Activity;
import android.app.AlertDialog;
import android.content.Intent;
import android.content.SharedPreferences;
import android.graphics.Typeface;
import android.net.Uri;
import android.os.Bundle;
import android.text.InputType;
import android.util.Log;
import android.view.Gravity;
import android.view.KeyEvent;
import android.view.ViewGroup;
import android.widget.ArrayAdapter;
import android.widget.Button;
import android.widget.EditText;
import android.widget.LinearLayout;
import android.widget.ListView;
import android.widget.Spinner;
import android.widget.TextView;
import android.widget.Toast;

import java.io.BufferedReader;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.io.OutputStream;
import java.nio.charset.StandardCharsets;
import java.text.SimpleDateFormat;
import java.util.ArrayList;
import java.util.Date;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Locale;
import java.util.Map;

import com.google.mlkit.vision.codescanner.GmsBarcodeScanner;
import com.google.mlkit.vision.codescanner.GmsBarcodeScanning;

public class MainActivity extends Activity {
    private static final String TAG="OnHand";
    private static final int REQ_EXPORT=1002, REQ_IMPORT=1003;
    private static final String SETTINGS="onhand_settings";
    private static final String KEY_UNKNOWN_MODE="unknown_barcode_mode";
    private InventoryDb db;
    private long sessionId;
    private String sessionName="Default Inventory";
    private EditText barcode, description, qty;
    private Spinner location;
    private ListView list;
    private TextView title, summary;
    private ArrayAdapter<String> listAdapter;
    private final ArrayList<InventoryDb.Row> visibleRows = new ArrayList<>();

    @Override public void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        installCrashRecorder();
        try {
            initializeApp(false);
            showPreviousCrashIfAny();
        } catch (Throwable first) {
            Log.e(TAG, "Startup failed; attempting database recovery", first);
            try {
                if (db != null) db.close();
                deleteDatabase(InventoryDb.DB_NAME);
                initializeApp(true);
                new AlertDialog.Builder(this)
                        .setTitle("On Hand repaired its local data")
                        .setMessage("The previous local test database could not be opened, so On Hand created a fresh database. The app should now remain stable.")
                        .setPositiveButton("OK", null).show();
            } catch (Throwable second) {
                Log.e(TAG, "Startup recovery failed", second);
                showFatalStartup(first, second);
            }
        }
    }

    private void initializeApp(boolean recovered) {
        db = new InventoryDb(this);
        db.verifyReady();
        List<InventoryDb.Session> sessions = db.sessions();
        if (sessions.isEmpty()) {
            sessionId = db.createSession("Default Inventory");
            sessionName = "Default Inventory";
        } else {
            sessionId = sessions.get(0).id;
            sessionName = sessions.get(0).name;
        }
        buildUi();
        refreshLocations();
        refreshList();
    }

    private void installCrashRecorder() {
        final Thread.UncaughtExceptionHandler prior = Thread.getDefaultUncaughtExceptionHandler();
        Thread.setDefaultUncaughtExceptionHandler((thread, error) -> {
            try {
                getSharedPreferences("onhand_diag", MODE_PRIVATE).edit()
                        .putString("last_crash", Log.getStackTraceString(error)).apply();
            } catch (Throwable ignored) {}
            if (prior != null) prior.uncaughtException(thread, error);
        });
    }

    private void showPreviousCrashIfAny() {
        SharedPreferences p = getSharedPreferences("onhand_diag", MODE_PRIVATE);
        String crash = p.getString("last_crash", null);
        if (crash == null || crash.trim().isEmpty()) return;
        p.edit().remove("last_crash").apply();
        String shortCrash = crash.length() > 3500 ? crash.substring(0, 3500) : crash;
        new AlertDialog.Builder(this).setTitle("Previous crash details")
                .setMessage(shortCrash).setPositiveButton("OK", null).show();
    }

    private void showFatalStartup(Throwable first, Throwable second) {
        LinearLayout root = new LinearLayout(this);
        root.setOrientation(LinearLayout.VERTICAL);
        root.setPadding(dp(20), dp(20), dp(20), dp(20));
        TextView heading = new TextView(this);
        heading.setText("On Hand could not start");
        heading.setTextSize(22);
        heading.setTypeface(Typeface.DEFAULT, Typeface.BOLD);
        root.addView(heading);
        TextView detail = new TextView(this);
        detail.setText("Startup error:\n" + first + "\n\nRecovery error:\n" + second);
        detail.setTextIsSelectable(true);
        root.addView(detail, new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT, 0, 1));
        Button reset = button("Reset local database and retry");
        reset.setOnClickListener(v -> { deleteDatabase(InventoryDb.DB_NAME); recreate(); });
        root.addView(reset);
        setContentView(root);
    }

    private int dp(int n) { return Math.round(n * getResources().getDisplayMetrics().density); }
    private Button button(String text) { Button b=new Button(this); b.setText(text); b.setAllCaps(false); return b; }
    private TextView label(String text) { TextView t=new TextView(this); t.setText(text); t.setTextSize(14); return t; }

    private void buildUi() {
        LinearLayout root=new LinearLayout(this); root.setOrientation(LinearLayout.VERTICAL); root.setPadding(dp(12),dp(10),dp(12),0);
        title=new TextView(this); title.setTextSize(24); title.setTypeface(Typeface.DEFAULT, Typeface.BOLD); root.addView(title);

        LinearLayout sessionBar=new LinearLayout(this); sessionBar.setOrientation(LinearLayout.HORIZONTAL);
        Button choose=button("Inventories"); choose.setOnClickListener(v->chooseSession());
        Button fresh=button("New"); fresh.setOnClickListener(v->newSession());
        Button options=button("Options"); options.setOnClickListener(v->showUnknownBarcodeOptions());
        sessionBar.addView(choose,new LinearLayout.LayoutParams(0,ViewGroup.LayoutParams.WRAP_CONTENT,1));
        sessionBar.addView(fresh,new LinearLayout.LayoutParams(0,ViewGroup.LayoutParams.WRAP_CONTENT,1));
        sessionBar.addView(options,new LinearLayout.LayoutParams(0,ViewGroup.LayoutParams.WRAP_CONTENT,1));
        root.addView(sessionBar);

        root.addView(label("Barcode"));
        LinearLayout scanBar=new LinearLayout(this); scanBar.setOrientation(LinearLayout.HORIZONTAL);
        barcode=new EditText(this); barcode.setSingleLine(true); barcode.setTextSize(20); barcode.setHint("Scan or type barcode"); barcode.setInputType(InputType.TYPE_CLASS_TEXT);
        barcode.setOnEditorActionListener((v,action,event)->{
            if(event!=null && event.getKeyCode()==KeyEvent.KEYCODE_ENTER){
                handleScannedBarcode(barcode.getText().toString().trim());
                return true;
            }
            return false;
        });
        Button scan=button("Scan"); scan.setOnClickListener(v->scanBarcode());
        scanBar.addView(barcode,new LinearLayout.LayoutParams(0,ViewGroup.LayoutParams.WRAP_CONTENT,1)); scanBar.addView(scan); root.addView(scanBar);

        root.addView(label("Description")); description=new EditText(this); description.setSingleLine(true); description.setHint("Optional item description"); root.addView(description);
        LinearLayout ql=new LinearLayout(this); ql.setOrientation(LinearLayout.HORIZONTAL);
        LinearLayout qbox=new LinearLayout(this); qbox.setOrientation(LinearLayout.VERTICAL); qbox.addView(label("Quantity")); qty=new EditText(this); qty.setSingleLine(true); qty.setText(""); qty.setTextSize(20); qty.setGravity(Gravity.CENTER); qty.setInputType(InputType.TYPE_CLASS_NUMBER|InputType.TYPE_NUMBER_FLAG_SIGNED); qbox.addView(qty);
        LinearLayout lbox=new LinearLayout(this); lbox.setOrientation(LinearLayout.VERTICAL); lbox.addView(label("Location")); location=new Spinner(this); lbox.addView(location);
        ql.addView(qbox,new LinearLayout.LayoutParams(0,ViewGroup.LayoutParams.WRAP_CONTENT,1)); ql.addView(lbox,new LinearLayout.LayoutParams(0,ViewGroup.LayoutParams.WRAP_CONTENT,2)); root.addView(ql);

        LinearLayout actionBar=new LinearLayout(this); actionBar.setOrientation(LinearLayout.HORIZONTAL);
        Button add=button("Add Count"); add.setOnClickListener(v->addItem());
        Button loc=button("+ Location"); loc.setOnClickListener(v->addLocation());
        actionBar.addView(add,new LinearLayout.LayoutParams(0,ViewGroup.LayoutParams.WRAP_CONTENT,2)); actionBar.addView(loc,new LinearLayout.LayoutParams(0,ViewGroup.LayoutParams.WRAP_CONTENT,1)); root.addView(actionBar);

        summary=new TextView(this); summary.setPadding(0,dp(8),0,dp(4)); summary.setTypeface(Typeface.DEFAULT,Typeface.BOLD); root.addView(summary);
        Button locationTotals=button("Location Totals"); locationTotals.setOnClickListener(v->showLocationTotals()); root.addView(locationTotals);
        list=new ListView(this); listAdapter=new ArrayAdapter<>(this,android.R.layout.simple_list_item_2,android.R.id.text1,new ArrayList<>()); list.setAdapter(listAdapter); list.setOnItemClickListener((p,v,pos,id)->editRow(pos)); root.addView(list,new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT,0,1));

        LinearLayout io=new LinearLayout(this); io.setOrientation(LinearLayout.HORIZONTAL);
        Button imp=button("Import CSV"); imp.setOnClickListener(v->importCsv());
        Button exp=button("Export CSV"); exp.setOnClickListener(v->exportCsv());
        io.addView(imp,new LinearLayout.LayoutParams(0,ViewGroup.LayoutParams.WRAP_CONTENT,1)); io.addView(exp,new LinearLayout.LayoutParams(0,ViewGroup.LayoutParams.WRAP_CONTENT,1));
        io.setTranslationY(dp(-32));
        root.addView(io);
        setContentView(root);
    }

    private String getUnknownBarcodeMode() {
        return getSharedPreferences(SETTINGS, MODE_PRIVATE).getString(KEY_UNKNOWN_MODE, "add");
    }

    private void showUnknownBarcodeOptions() {
        String[] choices={"Add unknown barcode", "Ignore unknown barcode", "Search internet and add"};
        String mode=getUnknownBarcodeMode();
        int checked="ignore".equals(mode)?1:("search".equals(mode)?2:0);
        new AlertDialog.Builder(this)
                .setTitle("Unknown barcode behavior")
                .setSingleChoiceItems(choices, checked, (dialog, which) -> {
                    String selected=which==1?"ignore":(which==2?"search":"add");
                    getSharedPreferences(SETTINGS, MODE_PRIVATE).edit().putString(KEY_UNKNOWN_MODE, selected).apply();
                    dialog.dismiss();
                    toast("Unknown barcode option saved");
                })
                .setNegativeButton("Cancel", null)
                .show();
    }

    private void handleScannedBarcode(String code) {
        if (code == null) code = "";
        code = code.trim();
        if (code.isEmpty()) { toast("No barcode detected"); barcode.requestFocus(); return; }
        barcode.setText(code);
        barcode.setSelection(code.length());
        qty.setText("");

        if (db.barcodeExists(sessionId, code)) {
            String savedDescription=db.descriptionForBarcode(sessionId, code);
            if (savedDescription != null && !savedDescription.trim().isEmpty()) description.setText(savedDescription);
            qty.requestFocus();
            return;
        }

        String mode=getUnknownBarcodeMode();
        if ("ignore".equals(mode)) {
            barcode.setText("");
            description.setText("");
            qty.setText("");
            toast("Unknown barcode ignored");
            barcode.requestFocus();
            return;
        }
        if (!"search".equals(mode)) {
            description.setText("");
            qty.requestFocus();
            return;
        }

        description.setText("");
        toast("Searching for barcode description...");
        final String lookupCode=code;
        new Thread(() -> {
            try {
                String found=BarcodeLookup.lookupDescription(lookupCode);
                runOnUiThread(() -> {
                    if (!lookupCode.equals(barcode.getText().toString().trim())) return;
                    if (found != null && !found.trim().isEmpty()) {
                        description.setText(found.trim());
                        toast("Description found");
                    } else {
                        toast("No internet description found");
                    }
                    qty.requestFocus();
                });
            } catch (Exception e) {
                runOnUiThread(() -> {
                    if (!lookupCode.equals(barcode.getText().toString().trim())) return;
                    toast(e.getMessage()==null?"Internet lookup failed":e.getMessage());
                    qty.requestFocus();
                });
            }
        }).start();
    }

    private void refreshLocations() { List<String> locs=db.locations(); ArrayAdapter<String> a=new ArrayAdapter<>(this,android.R.layout.simple_spinner_dropdown_item,locs); location.setAdapter(a); }

    private void refreshList() {
        title.setText("On Hand — "+sessionName);
        visibleRows.clear(); visibleRows.addAll(db.items(sessionId));
        ArrayList<String> lines=new ArrayList<>(); int units=0;
        for (InventoryDb.Row r:visibleRows){ units+=r.quantity; String d=r.description==null||r.description.isEmpty()?"":(" — "+r.description); lines.add(r.barcode+"   Qty "+r.quantity+d+"\n"+r.location); }
        listAdapter.clear(); listAdapter.addAll(lines); listAdapter.notifyDataSetChanged(); summary.setText(visibleRows.size()+" item lines • "+units+" total units");
    }

    private void showLocationTotals() {
        Map<String,Integer> totals=new LinkedHashMap<>();
        int grandTotal=0;
        for (InventoryDb.Row r:visibleRows) {
            String loc=(r.location==null||r.location.trim().isEmpty())?"Main":r.location.trim();
            int value=totals.containsKey(loc)?totals.get(loc):0;
            totals.put(loc,value+r.quantity);
            grandTotal+=r.quantity;
        }
        if(totals.isEmpty()){ toast("No counts to total yet"); return; }
        StringBuilder message=new StringBuilder();
        for(Map.Entry<String,Integer> entry:totals.entrySet()) {
            if(message.length()>0) message.append("\n");
            message.append(entry.getKey()).append(": ").append(entry.getValue());
        }
        message.append("\n\nGrand Total: ").append(grandTotal);
        new AlertDialog.Builder(this)
                .setTitle("Quantity Totals by Location")
                .setMessage(message.toString())
                .setPositiveButton("OK",null)
                .show();
    }

    private void addItem() {
        String code=barcode.getText().toString().trim();
        if(code.isEmpty()){ toast("Enter or scan a barcode"); barcode.requestFocus(); return; }
        String qtyText=qty.getText().toString().trim();
        if(qtyText.isEmpty()){ toast("Enter quantity"); qty.requestFocus(); return; }
        int q;
        try { q=Integer.parseInt(qtyText); }
        catch(Exception ignored){ toast("Enter a valid quantity"); qty.requestFocus(); return; }
        if(q==0){toast("Quantity cannot be zero");qty.requestFocus();return;}
        String loc=location.getSelectedItem()==null?"Main":location.getSelectedItem().toString();
        db.addOrIncrement(sessionId,code,description.getText().toString(),q,loc);
        barcode.setText(""); description.setText(""); qty.setText(""); barcode.requestFocus(); refreshList();
    }

    private void scanBarcode() {
        try {
            GmsBarcodeScanner scanner = GmsBarcodeScanning.getClient(this);
            scanner.startScan()
                    .addOnSuccessListener(result -> handleScannedBarcode(result.getRawValue()))
                    .addOnFailureListener(e -> showError("Scanner could not start", e instanceof Exception ? (Exception)e : new Exception(e)));
        } catch (Throwable e) {
            showError("Scanner could not start", e instanceof Exception ? (Exception)e : new Exception(e));
        }
    }

    private void addLocation() { EditText e=new EditText(this); e.setHint("Location name"); new AlertDialog.Builder(this).setTitle("Add location").setView(e).setPositiveButton("Add",(d,w)->{String s=e.getText().toString().trim();if(!s.isEmpty()){db.addLocation(s);refreshLocations();}}).setNegativeButton("Cancel",null).show(); }

    private void newSession() { EditText e=new EditText(this); e.setHint("Inventory name"); new AlertDialog.Builder(this).setTitle("New inventory").setView(e).setPositiveButton("Create",(d,w)->{String n=e.getText().toString().trim();if(n.isEmpty())n="Inventory "+new SimpleDateFormat("yyyy-MM-dd HH:mm",Locale.US).format(new Date());sessionId=db.createSession(n);sessionName=n;refreshList();}).setNegativeButton("Cancel",null).show(); }

    private void chooseSession() { List<InventoryDb.Session> s=db.sessions(); String[] names=new String[s.size()]; for(int i=0;i<s.size();i++)names[i]=s.get(i).name; new AlertDialog.Builder(this).setTitle("Inventories").setItems(names,(d,which)->{sessionId=s.get(which).id;sessionName=s.get(which).name;refreshList();}).setNegativeButton("Cancel",null).show(); }

    private void editRow(int pos) { if(pos<0||pos>=visibleRows.size())return; InventoryDb.Row r=visibleRows.get(pos); LinearLayout box=new LinearLayout(this);box.setOrientation(LinearLayout.VERTICAL);box.setPadding(dp(24),0,dp(24),0); TextView info=new TextView(this); info.setText(r.barcode+"\n"+r.description+"\n"+r.location); box.addView(info); EditText q=new EditText(this);q.setInputType(InputType.TYPE_CLASS_NUMBER|InputType.TYPE_NUMBER_FLAG_SIGNED);q.setText(String.valueOf(r.quantity));box.addView(q); new AlertDialog.Builder(this).setTitle("Edit count").setView(box).setPositiveButton("Save",(d,w)->{try{db.setQuantity(r.id,Integer.parseInt(q.getText().toString()));}catch(Exception ignored){}refreshList();}).setNeutralButton("Delete",(d,w)->{db.deleteItem(r.id);refreshList();}).setNegativeButton("Cancel",null).show(); }

    private void exportCsv() { Intent i=new Intent(Intent.ACTION_CREATE_DOCUMENT);i.addCategory(Intent.CATEGORY_OPENABLE);i.setType("text/csv");i.putExtra(Intent.EXTRA_TITLE,safeFileName(sessionName)+".csv");startActivityForResult(i,REQ_EXPORT); }
    private void importCsv() { Intent i=new Intent(Intent.ACTION_OPEN_DOCUMENT);i.addCategory(Intent.CATEGORY_OPENABLE);i.setType("text/*");startActivityForResult(i,REQ_IMPORT); }
    private String safeFileName(String s){return s.replaceAll("[^A-Za-z0-9._-]+","_");}

    @Override protected void onActivityResult(int requestCode,int resultCode,Intent data){
        super.onActivityResult(requestCode,resultCode,data);
        if(resultCode!=RESULT_OK||data==null)return;
        if(requestCode==REQ_EXPORT){writeExport(data.getData());} else if(requestCode==REQ_IMPORT){readImport(data.getData());}
    }

    private void writeExport(Uri uri){ if(uri==null)return; try(OutputStream os=getContentResolver().openOutputStream(uri)){ if(os==null)throw new Exception("No output stream"); os.write(CsvUtils.exportRows(db.items(sessionId)).getBytes(StandardCharsets.UTF_8));toast("CSV exported"); }catch(Exception e){showError("Export failed",e);} }

    private void readImport(Uri uri){ if(uri==null)return; int imported=0; try(InputStream is=getContentResolver().openInputStream(uri); BufferedReader br=new BufferedReader(new InputStreamReader(is,StandardCharsets.UTF_8))){ String line;boolean first=true;while((line=br.readLine())!=null){if(line.trim().isEmpty())continue;List<String> f=CsvUtils.parseLine(line);if(first){first=false;if(!f.isEmpty()&&f.get(0).toLowerCase(Locale.US).contains("barcode"))continue;}if(f.size()<1)continue;String code=f.get(0).trim();if(code.isEmpty())continue;String desc=f.size()>1?f.get(1):"";int q=1;try{if(f.size()>2)q=Integer.parseInt(f.get(2).trim());}catch(Exception ignored){}String loc=f.size()>3&&!f.get(3).trim().isEmpty()?f.get(3).trim():"Main";db.addLocation(loc);db.addOrIncrement(sessionId,code,desc,q,loc);imported++;}refreshLocations();refreshList();toast("Imported "+imported+" rows");}catch(Exception e){showError("Import failed",e);} }

    private void showError(String title,Exception e){new AlertDialog.Builder(this).setTitle(title).setMessage(e.getMessage()==null?e.toString():e.getMessage()).setPositiveButton("OK",null).show();}
    private void toast(String s){Toast.makeText(this,s,Toast.LENGTH_SHORT).show();}
}
