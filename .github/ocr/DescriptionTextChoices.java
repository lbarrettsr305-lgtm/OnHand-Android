package com.iceinventory.onhand;

import java.util.ArrayList;
import java.util.Collections;
import java.util.Comparator;
import java.util.List;
import java.util.Locale;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

/** Ranks actual OCR text; never fills in a missing brand, style, color or size. */
public final class DescriptionTextChoices {
    public static final int MAX_CHOICES=8;
    private static final Pattern SIZE=Pattern.compile("(?i)(?:\\b\\d+\\s*[/x×]\\s*)?\\d+(?:[.,]\\d+)?\\s*(?:fl\\.?\\s*)?(?:fluid\\s+ounces?|oz|lbs?|pounds?|kg|g|ml|milliliters?|liters?|litres?|l|ct|count|packs?|pk|gal|qt|quarts?|inches|inch|in\\.?|feet|foot|ft\\.?)\\b|\\b\\d+(?:\\.\\d+)?\\s*[\"″”]|\\b\\d+\\s*[x×]\\s*\\d+(?:\\.\\d+)?\\b");
    private static final Pattern NOISE=Pattern.compile("(?i)\\b(?:ingredients?|maintenance|directions?|instructions?|warnings?|caution|nutrition|serving|calories|manufactured|distributed|imported|registro|copyright|recycle|patented|technology)\\b|washing\\s*&?\\s*care|made\\s+in|powered\\s+by|designed\\s+for|vibrant\\s+color\\s*&?\\s*bonding|no\\s+animal|no\\s+ppd|hyaluronic\\s+acid|\\bvegan\\b|long[- ]lasting|\\b(?:rinse|immerse|swish|gently|brush|shampoo\\s+for|do\\s+not|keep\\s+out)\\b|https?[:/]|www\\.|@");
    private static final Pattern DETAIL=Pattern.compile("(?i)\\b(?:style|color|colour|shade|size|model|item|yaki|bob|lace|remi|wig|human\\s+hair)\\b|^#\\s*[A-Z0-9-]+$");
    private DescriptionTextChoices(){}

    public static final class Line {
        public final String text;
        public final float height;
        public final boolean retailerBlock;
        public Line(String text,float height){this(text,height,false);}
        public Line(String text,float height,boolean retailerBlock){
            this.text=text;this.height=height;this.retailerBlock=retailerBlock;
        }
    }

    private static final class Candidate {
        String text;double score;int order;
        Candidate(String text,double score,int order){this.text=text;this.score=score;this.order=order;}
    }

    /** A price or phone in the same OCR block usually identifies a retailer sticker. */
    public static boolean isRetailerBlock(String text){
        String value=clean(text);
        return value.matches("(?s).*[\\$£€]\\s*\\d.*")
            ||value.matches("(?s).*\\b\\d{3}[- .]\\d{3}[- .]\\d{4}\\b.*");
    }

    public static List<String> shortlist(List<Line> lines){
        ArrayList<Candidate> candidates=new ArrayList<>();
        if(lines==null)return new ArrayList<>();
        float largest=1;
        for(Line line:lines)if(line!=null&&!line.retailerBlock&&!noise(line.text))largest=Math.max(largest,line.height);
        int order=0;
        String previous="";
        for(Line line:lines){
            if(line==null)continue;
            String value=clean(line.text);
            int position=order++*10;
            if(value.isEmpty()||line.retailerBlock){previous=value;continue;}
            boolean rejected=noise(value)||previous.matches("(?i)powered by|designed for");
            Matcher sizes=SIZE.matcher(value);
            int sizeOrder=5;
            int foundSizes=0;
            while(sizes.find()){
                foundSizes++;
                // Instructions and addresses can contain misleading measurements.
                if(!rejected||value.toLowerCase(Locale.US).matches(".*\\b(?:net\\s*wt|net\\s*weight|content|volume)\\b.*"))
                    add(candidates,normalizeSize(sizes.group()),95,position+sizeOrder++);
            }
            if(rejected){previous=value;continue;}
            String name=clean(SIZE.matcher(value).replaceAll(" "))
                .replaceAll("(?i)\\b(?:net\\s*wt\\.?|net\\s*weight|weight|contents?)\\b"," ").trim();
            name=clean(name.replaceAll("^[\\s/(),;:.-]+|[\\s/(),;:.-]+$",""));
            if(name.matches("(?i)[0-9]{1,3}[A-Z]?")&&previous.matches("(?i)colou?r|shade"))
                name="Color "+name;
            else if(previous.matches("(?i)style|model|item")&&!name.isEmpty()&&name.length()<=24)
                name="Style "+name;
            if(name.matches("(?i)colou?r|shade|style|size|model|item")){previous=value;continue;}
            boolean detail=DETAIL.matcher(name).find();
            if(foundSizes>=2&&!detail){previous=value;continue;}
            boolean code=name.matches("(?i)#[A-Z0-9-]+|[0-9]{1,3}[A-Z]?|[A-Z]{1,3}[0-9]{1,3}(?:/[A-Z0-9]+)*");
            if(!detail&&!code&&line.height>0&&line.height<largest*0.25f){previous=value;continue;}
            int letters=0;for(int i=0;i<name.length();i++)if(Character.isLetter(name.charAt(i)))letters++;
            if(name.length()<=72&&(letters>=3||detail||code)){
                double prominence=40*Math.min(1,Math.max(0,line.height)/largest);
                add(candidates,name,20+prominence+(detail?50:0)+(code?55:0),position);
            }
            previous=value;
        }
        // Collapse identical and near-identical OCR repeats, preserving distinct digits.
        ArrayList<Candidate> unique=new ArrayList<>();
        for(Candidate candidate:candidates){
            Candidate duplicate=null;
            for(Candidate prior:unique)if(sameChoice(prior.text,candidate.text)){duplicate=prior;break;}
            if(duplicate==null)unique.add(candidate);
            else{
                if(wordCount(candidate.text)>wordCount(duplicate.text)||candidate.score>duplicate.score+10)
                    duplicate.text=candidate.text;
                duplicate.score=Math.max(duplicate.score,candidate.score);
                duplicate.order=Math.min(duplicate.order,candidate.order);
            }
        }
        // Suppress isolated fragments when a complete recognized line contains them.
        ArrayList<Candidate> complete=new ArrayList<>();
        for(Candidate candidate:unique){
            boolean fragment=false;
            String key=key(candidate.text);
            if(!SIZE.matcher(candidate.text).find()&&!candidate.text.matches(".*\\d.*")){
                for(Candidate other:unique)if(other!=candidate&&wordCount(other.text)>wordCount(candidate.text)
                        &&key.length()>=3&&(" "+words(other.text)+" ").contains(" "+words(candidate.text)+" ")){
                    fragment=true;break;
                }
            }
            if(!fragment)complete.add(candidate);
        }
        Collections.sort(complete,(a,b)->{
            int score=Double.compare(b.score,a.score);
            return score!=0?score:Integer.compare(a.order,b.order);
        });
        if(complete.size()>MAX_CHOICES)complete=new ArrayList<>(complete.subList(0,MAX_CHOICES));
        Collections.sort(complete,Comparator.comparingInt(a->a.order));
        ArrayList<String> out=new ArrayList<>();
        for(Candidate candidate:complete)out.add(candidate.text);
        return out;
    }

    /** Keep all recognized lines available, removing only exact punctuation/case repeats. */
    public static List<String> allText(List<String> lines){
        ArrayList<String> out=new ArrayList<>();
        if(lines!=null)for(String line:lines){
            String value=clean(line);
            if(value.isEmpty())continue;
            boolean duplicate=false;
            for(String existing:out)if(key(existing).equals(key(value))){duplicate=true;break;}
            if(!duplicate)out.add(value);
        }
        return out;
    }

    public static String key(String text){
        String value=clean(text).toUpperCase(Locale.US);
        StringBuilder out=new StringBuilder();
        for(int i=0;i<value.length();i++){
            char c=value.charAt(i);
            if(Character.isLetterOrDigit(c))out.append(c);
            else if((c=='.'||c==','||c=='/')&&i>0&&i+1<value.length()
                    &&Character.isDigit(value.charAt(i-1))&&Character.isDigit(value.charAt(i+1)))
                out.append(c==','?'.':c);
        }
        return out.toString();
    }
    private static String words(String text){return clean(text).toUpperCase(Locale.US).replaceAll("[^\\p{L}\\p{N}]+"," ").trim();}
    private static int wordCount(String text){String value=words(text);return value.isEmpty()?0:value.split(" ").length;}
    private static boolean noise(String text){return NOISE.matcher(clean(text)).find()||isRetailerBlock(text);}
    private static void add(List<Candidate> out,String text,double score,int order){if(!clean(text).isEmpty())out.add(new Candidate(clean(text),score,order));}
    private static String clean(String text){return text==null?"":text.replaceAll("\\s+"," ").trim();}
    private static String normalizeSize(String text){
        String value=clean(text).toUpperCase(Locale.US).replaceAll("[\"″”]"," IN");
        return clean(value.replaceAll("\\bFL\\.?\\s*OZ\\b","FL OZ").replaceAll("\\bINCHES?\\b","IN"));
    }
    private static boolean sameChoice(String a,String b){
        String x=key(a),y=key(b);
        if(x.equals(y))return true;
        if(wordCount(a)==wordCount(b))return false;
        if(a.matches(".*[0-9].*")||b.matches(".*[0-9].*"))return false;
        if(Math.min(x.length(),y.length())<6||Math.abs(x.length()-y.length())>1)return false;
        int i=0,j=0,edits=0;
        while(i<x.length()&&j<y.length()){
            if(x.charAt(i)==y.charAt(j)){i++;j++;continue;}
            if(++edits>1)return false;
            if(x.length()>y.length())i++;
            else if(y.length()>x.length())j++;
            else{i++;j++;}
        }
        return edits+(x.length()-i)+(y.length()-j)<=1;
    }
}
