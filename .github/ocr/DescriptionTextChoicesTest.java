package com.iceinventory.onhand;

import org.junit.Test;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import static org.junit.Assert.*;

public class DescriptionTextChoicesTest {
    private DescriptionTextChoices.Line line(String text,float height){return new DescriptionTextChoices.Line(text,height);}

    @Test public void wigChoicesKeepStyleLengthAndActualColorAndRemoveRepeats(){
        List<String> choices=DescriptionTextChoices.shortlist(Arrays.asList(
            new DescriptionTextChoices.Line("BEAUTY TIME",16,true),
            line("Destiny",22),line("Green WIG",50),line("Green",45),line("WIG",30),
            line("Destiny",20),line("Green WiG",48),line("100% Remi Human Hair",18),
            line("HH YAKI BOB 18″",16),line("Color",12),line("1",14),
            line("MAINTENANCE",18),line("Immerse the wig in cold water",9)));
        assertTrue(choices.contains("Destiny"));
        assertTrue(choices.contains("Green WIG"));
        assertTrue(choices.contains("HH YAKI BOB"));
        assertTrue(choices.contains("18 IN"));
        assertTrue(choices.contains("Color 1"));
        assertFalse(choices.contains("BEAUTY TIME"));
        assertFalse(choices.contains("Green"));
        assertFalse(choices.contains("WIG"));
        assertEquals(1,java.util.Collections.frequency(choices,"Destiny"));
        assertTrue(choices.size()<=DescriptionTextChoices.MAX_CHOICES);
    }

    @Test public void sizeIsCollectedBelowIngredientsAndSmallPrintDoesNotHideIt(){
        List<String> choices=DescriptionTextChoices.shortlist(Arrays.asList(
            line("ALFAPARF",24),line("EVOLUTION",60),line("INGREDIENTS: AQUA ALCOHOL",8),
            line("PATENTED COLOR GUARD TECHNOLOGY",18),line("75 ml",6),line("NET WT. 2.3 OZ / CONT. 65 g",6)));
        assertTrue(choices.contains("ALFAPARF"));
        assertTrue(choices.contains("EVOLUTION"));
        assertTrue(choices.contains("75 ML"));
        assertTrue(choices.contains("2.3 OZ"));
        assertTrue(choices.contains("65 G"));
        for(String choice:choices)assertFalse(choice.contains("INGREDIENTS")||choice.contains("PATENTED"));
    }

    @Test public void priceStickerBlockIsDetectedWithoutGuessingBrandNames(){
        assertTrue(DescriptionTextChoices.isRetailerBlock("BEAUTY TIME $79.99 305-233-3338"));
        assertFalse(DescriptionTextChoices.isRetailerBlock("Destiny Green WIG"));
    }

    @Test public void hiddenTextRemainsAvailableAndDistinctColorsAreNotMerged(){
        List<String> raw=Arrays.asList("Destiny","DESTINY","Maintenance","Rinse with cold water","Color 1","Color 1B","18 IN","16 IN");
        List<String> all=DescriptionTextChoices.allText(raw);
        assertEquals(7,all.size());
        assertTrue(all.contains("Maintenance"));
        assertTrue(all.contains("Rinse with cold water"));
        List<DescriptionTextChoices.Line> lines=new ArrayList<>();
        for(String text:raw)lines.add(line(text,20));
        List<String> focused=DescriptionTextChoices.shortlist(lines);
        assertTrue(focused.contains("Color 1"));
        assertTrue(focused.contains("Color 1B"));
        assertTrue(focused.contains("18 IN"));
        assertTrue(focused.contains("16 IN"));
    }

    @Test public void smallExplicitStyleAndSizeSurviveManyLargeUnrelatedNames(){
        List<DescriptionTextChoices.Line> lines=new ArrayList<>();
        for(int i=10;i<25;i++)lines.add(line("Label "+i,40));
        lines.add(line("Style TD",4));lines.add(line("60 ml",4));
        List<String> choices=DescriptionTextChoices.shortlist(lines);
        assertEquals(8,choices.size());
        assertTrue(choices.contains("Style TD"));
        assertTrue(choices.contains("60 ML"));
    }

    @Test public void missingFieldsAreNeverInventedAndSplitStyleIsRetained(){
        List<String> choices=DescriptionTextChoices.shortlist(Arrays.asList(line("Destiny",40),line("STYLE",12),line("TD",12),line("#871",10)));
        assertTrue(choices.contains("Style TD"));
        assertTrue(choices.contains("#871"));
        assertFalse(choices.toString().contains("18 IN"));
        assertFalse(choices.toString().contains("Color 1"));
    }

    @Test public void decimalSizesAndMultipacksAreNotCollapsed(){
        List<String> values=Arrays.asList("2.3 OZ","23 OZ","6/2LB","62LB");
        assertEquals(4,DescriptionTextChoices.allText(values).size());
        List<String> choices=DescriptionTextChoices.shortlist(Arrays.asList(
            line("2.3 OZ",12),line("23 OZ",12),line("6/2LB",12),line("62LB",12)));
        assertEquals(4,choices.size());
        assertTrue(choices.contains("2.3 OZ"));
        assertTrue(choices.contains("23 OZ"));
        assertTrue(choices.contains("6/2LB"));
        assertTrue(choices.contains("62LB"));
    }

    @Test public void ingredientPromotionAndServingMeasurementsAreFiltered(){
        List<String> choices=DescriptionTextChoices.shortlist(Arrays.asList(
            line("POWERED BY",20),line("ARGAN OIL & ALOETRIX",22),line("ALFAPARF",24),
            line("SERVING SIZE 30g",10),line("NET WT 100g",10)));
        assertFalse(choices.contains("ARGAN OIL & ALOETRIX"));
        assertFalse(choices.contains("30G"));
        assertTrue(choices.contains("100G"));
        assertTrue(choices.contains("ALFAPARF"));
    }

    @Test public void foldedDuplicateCanPreferCompleteWordsButDistinctNamesRemain(){
        List<String> choices=DescriptionTextChoices.shortlist(Arrays.asList(
            line("GreenWG",30),line("Green WIG",30),line("BrandA",24),line("BrandB",24)));
        assertTrue(choices.contains("Green WIG"));
        assertFalse(choices.contains("GreenWG"));
        assertTrue(choices.contains("BrandA"));
        assertTrue(choices.contains("BrandB"));
    }
}
