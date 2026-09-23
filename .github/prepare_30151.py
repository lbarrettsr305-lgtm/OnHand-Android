from pathlib import Path

base=Path('.github/prepare_30150.py')
exec(compile(base.read_text(),str(base),'exec'),{'__name__':'__main__','__file__':str(base)})

def rep(path,old,new):
    p=Path(path);s=p.read_text()
    if s.count(old)!=1:raise SystemExit('3.0.151 expected one target: '+old[:110])
    p.write_text(s.replace(old,new,1))

rep('app/build.gradle','versionCode 30150','versionCode 30151')
rep('app/build.gradle',"versionName '3.0.150'","versionName '3.0.151'")
rep('app/src/main/AndroidManifest.xml','iCE Onhand 3.0.150','iCE Onhand 3.0.151')
m='app/src/main/java/com/iceinventory/onhand/MainActivity.java'
rep(m,'Onhand Inventory 3.0.150','Onhand Inventory 3.0.151')
rep(m,'private Spinner location;','private Spinner location;\n    private long confirmedLocationSession=-1L;\n    private String confirmedLocation="";\n    private AlertDialog locationDialog;\n    private EditText locationScanInput;')
rep(m,'barcode.postDelayed(this::focusBarcodeWithoutKeyboard,120);',
    'barcode.postDelayed(this::showLocationStepIfNeeded,650);')
rep(m,'addLoc.setOnClickListener(v->addLocation());',
    'addLoc.setOnClickListener(v->showLocationStep());')
rep(m,'Button addLoc=button("＋ New\\nLocation",0);',
    'Button addLoc=button("Set\\nLocation",0);')
rep(m,'private void startPhoneScanCycle(){\n        continuousPhoneScan=true;',
    'private void startPhoneScanCycle(){\n        if(!ensureCountingLocation())return;\n        continuousPhoneScan=true;')
rep(m,'private void addItem() {\n        if(!requireCurrentCount())return;',
    'private void addItem() {\n        if(!requireCurrentCount()||!ensureCountingLocation())return;')
rep(m,'String loc=location.getSelectedItem()==null?"Main":location.getSelectedItem().toString();',
    'String loc=confirmedLocation;')
rep(m,'private void refreshLocations() {\n        List<String> locs=db.locations();\n        ArrayAdapter<String> a=new ArrayAdapter<>(this,android.R.layout.simple_spinner_dropdown_item,locs);\n        location.setAdapter(a);\n    }',
    '''private void refreshLocations() {
        List<String> locs=db.locations();
        ArrayAdapter<String> a=new ArrayAdapter<>(this,android.R.layout.simple_spinner_dropdown_item,locs);
        location.setAdapter(a);location.setEnabled(false);
        if(confirmedLocationSession==sessionId){
            for(int i=0;i<locs.size();i++)if(locs.get(i).equalsIgnoreCase(confirmedLocation)){location.setSelection(i);break;}
        }
    }

    private boolean ensureCountingLocation(){
        if(confirmedLocationSession==sessionId&&!confirmedLocation.isEmpty())return true;
        showLocationStep();return false;
    }

    private void showLocationStepIfNeeded(){
        if(!isPreviousInventory()&&!"NO ACTIVE INVENTORY".equals(sessionName))ensureCountingLocation();
    }

    private void submitCountingLocation(String name){
        String n=name==null?"":name.trim();
        if(n.isEmpty()){toast("Choose or scan a location first");return;}
        db.addLocation(n);confirmedLocation=n;confirmedLocationSession=sessionId;
        refreshLocations();
        if(locationDialog!=null){locationDialog.dismiss();locationDialog=null;locationScanInput=null;}
        barcode.setText("");description.setText("");qty.setText("");
        toast("Counting location: "+n);
        focusBarcodeWithoutKeyboard();
    }

    private void showLocationStep(){
        if(!requireCurrentCount())return;
        if(locationDialog!=null&&locationDialog.isShowing())return;
        LinearLayout panel=new LinearLayout(this);panel.setOrientation(LinearLayout.VERTICAL);
        panel.setPadding(dp(16),dp(8),dp(16),dp(4));
        TextView instructions=text("Choose an existing short location name, type a new one, or scan its label. Submit the location before counting barcodes.",16,Color.WHITE,false);
        panel.addView(instructions);
        Spinner choices=new Spinner(this);
        List<String> names=db.locations();
        ArrayList<String> options=new ArrayList<>();options.add("Choose a location");options.addAll(names);
        ArrayAdapter<String> adapter=new ArrayAdapter<>(this,android.R.layout.simple_spinner_dropdown_item,options);
        choices.setAdapter(adapter);panel.addView(choices,new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT,dp(52)));
        EditText entry=new EditText(this);entry.setSingleLine(true);entry.setHint("Short location name / scanned label");
        entry.setTextColor(Color.WHITE);entry.setHintTextColor(Color.LTGRAY);
        panel.addView(entry,new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT,dp(56)));
        locationScanInput=entry;
        choices.setOnItemSelectedListener(new android.widget.AdapterView.OnItemSelectedListener(){
            public void onNothingSelected(android.widget.AdapterView<?> parent){}
            public void onItemSelected(android.widget.AdapterView<?> parent,android.view.View view,int pos,long id){
                if(pos>0)entry.setText(options.get(pos));
            }
        });
        Button camera=button("Scan Location Label",1);
        camera.setOnClickListener(v->GmsBarcodeScanning.getClient(this).startScan()
            .addOnSuccessListener(result->{String value=result.getRawValue();if(value!=null)entry.setText(value.trim());})
            .addOnFailureListener(e->showError("Location scanner error",e)));
        panel.addView(camera,new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT,dp(52)));
        locationDialog=new AlertDialog.Builder(this).setTitle("1  SET COUNTING LOCATION")
            .setView(panel).setPositiveButton("Submit Location",null)
            .setNegativeButton("Cancel",(d,w)->{locationDialog=null;locationScanInput=null;}).create();
        locationDialog.setOnShowListener(x->locationDialog.getButton(AlertDialog.BUTTON_POSITIVE)
            .setOnClickListener(v->submitCountingLocation(entry.getText().toString())));
        locationDialog.show();
    }''')
rep(m,'if(event!=null&&event.getDeviceId()>=0&&event.getAction()==KeyEvent.ACTION_DOWN&&barcode!=null) {',
    '''if(locationScanInput!=null&&locationDialog!=null&&locationDialog.isShowing()
                &&event!=null&&event.getDeviceId()>=0&&event.getAction()==KeyEvent.ACTION_DOWN){
            int key=event.getKeyCode();
            if(key==KeyEvent.KEYCODE_ENTER||key==KeyEvent.KEYCODE_NUMPAD_ENTER||key==KeyEvent.KEYCODE_TAB){
                submitCountingLocation(locationScanInput.getText().toString());return true;
            }
            int ch=event.getUnicodeChar();
            if(ch>0&&!Character.isISOControl(ch)){
                locationScanInput.append(String.valueOf((char)ch));return true;
            }
        }
        if(event!=null&&event.getDeviceId()>=0&&event.getAction()==KeyEvent.ACTION_DOWN&&barcode!=null) {''')
rep(m,'private void handleScannedBarcode(String rawCode) {',
    'private void handleScannedBarcode(String rawCode) {\n        if(!ensureCountingLocation())return;')
rep(m,'sessionId=s.id;sessionName=s.name;lastBarcode="";\n                    refreshList();',
    'sessionId=s.id;sessionName=s.name;lastBarcode="";\n                    refreshLocations();refreshList();showLocationStepIfNeeded();')
rep(m,'sessionId=db.createSession(n);activeSessionId=sessionId;prefs().edit().putLong(KEY_ACTIVE_SESSION,activeSessionId).apply();sessionName=n;lastBarcode="";\n                    refreshList();',
    'sessionId=db.createSession(n);activeSessionId=sessionId;prefs().edit().putLong(KEY_ACTIVE_SESSION,activeSessionId).apply();sessionName=n;lastBarcode="";\n                    refreshLocations();refreshList();showLocationStepIfNeeded();')
print('Prepared iCE OnHand 3.0.151: location-first counting flow')
