package com.iceinventory.onhand;

import android.content.SharedPreferences;

import java.text.SimpleDateFormat;
import java.util.Date;
import java.util.List;
import java.util.Locale;

/**
 * Batch-only TXT writer.
 *
 * Unlike the normal exporter, batch files must preserve negative quantity
 * adjustments so a sequence of batches can always reconcile to the live count.
 */
public final class BatchExportText {
    private BatchExportText(){}

    public static String exportRows(List<InventoryDb.Row> rows, SharedPreferences prefs) {
        List<String> order=TabTextUtils.getOrder(prefs,true);
        StringBuilder b=new StringBuilder();

        for(int i=0;i<order.size();i++) {
            if(i>0)b.append('\t');
            b.append(TabTextUtils.exportHeader(order.get(i)));
        }
        b.append("\r\n");

        SimpleDateFormat dateFmt=new SimpleDateFormat("yyyy-MM-dd",Locale.US);
        SimpleDateFormat timeFmt=new SimpleDateFormat("HH:mm:ss",Locale.US);

        for(InventoryDb.Row r:rows) {
            if(r==null||r.quantity==0)continue;
            Date when=new Date(r.updatedAt>0?r.updatedAt:System.currentTimeMillis());
            for(int i=0;i<order.size();i++) {
                if(i>0)b.append('\t');
                String f=order.get(i);
                if("barcode".equals(f))b.append(clean(r.barcode));
                else if("description".equals(f))b.append(clean(r.description));
                else if("price".equals(f))b.append(clean(r.price));
                else if("quantity".equals(f))b.append(r.quantity);
                else if("location".equals(f))b.append(clean(r.location));
                else if("scan_date".equals(f))b.append(dateFmt.format(when));
                else if("scan_time".equals(f))b.append(timeFmt.format(when));
            }
            b.append("\r\n");
        }
        return b.toString();
    }

    private static String clean(String s) {
        if(s==null)return "";
        return s.replace('\t',' ').replace('\r',' ').replace('\n',' ').trim();
    }
}
