package com.iceinventory.onhand;

import android.util.Xml;

import org.xmlpull.v1.XmlPullParser;

import java.io.ByteArrayInputStream;
import java.io.ByteArrayOutputStream;
import java.io.InputStream;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.zip.ZipEntry;
import java.util.zip.ZipInputStream;

/** Small dependency-free reader for the first worksheet in an XLSX file. */
public final class XlsxTableReader {
    private XlsxTableReader(){}

    public static List<Map<Integer,String>> readFirstSheet(InputStream input) throws Exception {
        Map<String,byte[]> parts=new HashMap<>();
        try(ZipInputStream zip=new ZipInputStream(input)){
            ZipEntry entry;
            byte[] buffer=new byte[16384];
            while((entry=zip.getNextEntry())!=null){
                if(entry.isDirectory())continue;
                String name=entry.getName();
                if(!"xl/sharedStrings.xml".equals(name)&&!"xl/worksheets/sheet1.xml".equals(name))continue;
                ByteArrayOutputStream out=new ByteArrayOutputStream();
                int n;while((n=zip.read(buffer))>0)out.write(buffer,0,n);
                parts.put(name,out.toByteArray());
            }
        }
        byte[] sheet=parts.get("xl/worksheets/sheet1.xml");
        if(sheet==null)throw new Exception("The Excel file does not contain a readable first worksheet");
        List<String> shared=readShared(parts.get("xl/sharedStrings.xml"));
        return readSheet(sheet,shared);
    }

    private static List<String> readShared(byte[] xml) throws Exception {
        ArrayList<String> values=new ArrayList<>();
        if(xml==null)return values;
        XmlPullParser p=Xml.newPullParser();
        p.setInput(new ByteArrayInputStream(xml),"UTF-8");
        StringBuilder current=null;
        int event;
        while((event=p.next())!=XmlPullParser.END_DOCUMENT){
            if(event==XmlPullParser.START_TAG&&"si".equals(p.getName()))current=new StringBuilder();
            else if(event==XmlPullParser.START_TAG&&"t".equals(p.getName())&&current!=null)current.append(p.nextText());
            else if(event==XmlPullParser.END_TAG&&"si".equals(p.getName())){values.add(current==null?"":current.toString());current=null;}
        }
        return values;
    }

    private static List<Map<Integer,String>> readSheet(byte[] xml,List<String> shared) throws Exception {
        ArrayList<Map<Integer,String>> rows=new ArrayList<>();
        XmlPullParser p=Xml.newPullParser();
        p.setInput(new ByteArrayInputStream(xml),"UTF-8");
        Map<Integer,String> row=null;
        int column=-1;
        String type="",value="";
        int event;
        while((event=p.next())!=XmlPullParser.END_DOCUMENT){
            if(event==XmlPullParser.START_TAG){
                String tag=p.getName();
                if("row".equals(tag))row=new HashMap<>();
                else if("c".equals(tag)){
                    column=columnIndex(p.getAttributeValue(null,"r"));
                    type=p.getAttributeValue(null,"t");if(type==null)type="";value="";
                }else if(("v".equals(tag)||"t".equals(tag))&&row!=null&&column>=0)value=p.nextText();
            }else if(event==XmlPullParser.END_TAG){
                String tag=p.getName();
                if("c".equals(tag)&&row!=null&&column>=0){
                    String resolved=value==null?"":value;
                    if("s".equals(type)&&!resolved.isEmpty()){
                        try{int i=Integer.parseInt(resolved);resolved=i>=0&&i<shared.size()?shared.get(i):"";}catch(Exception ignored){}
                    }
                    row.put(column,resolved);
                    column=-1;type="";value="";
                }else if("row".equals(tag)&&row!=null){rows.add(row);row=null;}
            }
        }
        return rows;
    }

    private static int columnIndex(String ref){
        if(ref==null)return -1;int n=0;
        for(int i=0;i<ref.length();i++){
            char c=ref.charAt(i);if(c<'A'||c>'Z')break;n=n*26+(c-'A'+1);
        }
        return n-1;
    }
}
