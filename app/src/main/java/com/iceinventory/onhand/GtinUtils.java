package com.iceinventory.onhand;

public final class GtinUtils {
    private GtinUtils() {}

    public static final class Result {
        public final String gtin14;
        public final String note;
        Result(String gtin14, String note) { this.gtin14 = gtin14; this.note = note; }
    }

    public static Result toGtin14(String input) {
        String digits = digitsOnly(input);
        if (digits.isEmpty()) throw new IllegalArgumentException("Barcode has no digits");
        if (digits.length() > 14) throw new IllegalArgumentException("GTIN cannot exceed 14 digits");

        // UPC-E (8 digits) can be expanded to UPC-A/GTIN-12. Prefer that interpretation
        // when the number system is 0 or 1 and the UPC-E check digit validates after expansion.
        if (digits.length() == 8 && (digits.charAt(0) == '0' || digits.charAt(0) == '1')) {
            String upca = expandUpceToUpca(digits);
            if (upca != null && hasValidCheckDigit(upca)) {
                return new Result(leftPad(upca, 14), "UPC-E expanded to GTIN-12, then padded to GTIN-14");
            }
        }

        // Existing GTIN-8, GTIN-12 (UPC-A), GTIN-13 (EAN-13), or GTIN-14.
        if ((digits.length() == 8 || digits.length() == 12 || digits.length() == 13 || digits.length() == 14)
                && hasValidCheckDigit(digits)) {
            return new Result(leftPad(digits, 14), "Existing GTIN normalized to GTIN-14");
        }

        // Common case where the source omits its check digit.
        if (digits.length() == 7 || digits.length() == 11 || digits.length() == 12 || digits.length() == 13) {
            int targetLength = digits.length() + 1;
            String completed = digits + computeCheckDigit(digits);
            return new Result(leftPad(completed, 14), "Missing check digit calculated for GTIN-" + targetLength);
        }

        // For shorter numeric client codes, create a GTIN-14 representation by left-padding
        // the data portion to 13 digits and calculating the GTIN check digit.
        if (digits.length() <= 13) {
            String body13 = leftPad(digits, 13);
            return new Result(body13 + computeCheckDigit(body13), "Numeric code converted to GTIN-14 with calculated check digit");
        }

        throw new IllegalArgumentException("Unable to convert barcode to GTIN-14");
    }

    public static boolean hasValidCheckDigit(String digits) {
        if (digits == null || digits.length() < 2 || !digits.matches("\\d+")) return false;
        String body = digits.substring(0, digits.length() - 1);
        int expected = computeCheckDigit(body);
        return expected == (digits.charAt(digits.length() - 1) - '0');
    }

    public static int computeCheckDigit(String body) {
        if (body == null || body.isEmpty() || !body.matches("\\d+"))
            throw new IllegalArgumentException("GTIN body must contain digits only");
        int sum = 0;
        boolean weight3 = true;
        for (int i = body.length() - 1; i >= 0; i--) {
            int d = body.charAt(i) - '0';
            sum += d * (weight3 ? 3 : 1);
            weight3 = !weight3;
        }
        return (10 - (sum % 10)) % 10;
    }

    private static String expandUpceToUpca(String upce) {
        if (upce == null || upce.length() != 8 || !upce.matches("\\d{8}")) return null;
        char ns = upce.charAt(0);
        String x = upce.substring(1, 7);
        char check = upce.charAt(7);
        char last = x.charAt(5);
        String body11;
        if (last == '0' || last == '1' || last == '2') {
            body11 = "" + ns + x.substring(0, 2) + last + "0000" + x.substring(2, 5);
        } else if (last == '3') {
            body11 = "" + ns + x.substring(0, 3) + "00000" + x.substring(3, 5);
        } else if (last == '4') {
            body11 = "" + ns + x.substring(0, 4) + "00000" + x.charAt(4);
        } else {
            body11 = "" + ns + x.substring(0, 5) + "0000" + last;
        }
        return body11 + check;
    }

    private static String digitsOnly(String value) {
        if (value == null) return "";
        StringBuilder out = new StringBuilder();
        for (int i = 0; i < value.length(); i++) {
            char c = value.charAt(i);
            if (Character.isDigit(c)) out.append(c);
        }
        return out.toString();
    }

    private static String leftPad(String value, int length) {
        StringBuilder out = new StringBuilder(length);
        for (int i = value.length(); i < length; i++) out.append('0');
        out.append(value);
        return out.toString();
    }
}
