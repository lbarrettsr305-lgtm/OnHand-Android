# iCE Onhand Inventory — Locked Baseline

## Approved reference
The approved working baseline is **OnHand 3.0.34**.

Reference APK SHA-256:
`a55f1138d00e9c2b22133314238369c2f0f4cbaa9c6079b5dbfaf2cf76f969b6`

## Rule for all future versions
Do **not** redesign, reorganize, simplify, modernize, or replace screens that already worked in the 3.0.34 user flow unless the user explicitly asks for that exact change.

Future versions must preserve the familiar 3.0.34 layout, button placement, counting flow, visual hierarchy, and simple operation. New work should be implemented as the smallest possible patch on top of the approved behavior.

## Features that must remain
- iCE Onhand Inventory branding and approved black / green / gold visual identity.
- Inventories / New / Options workflow.
- Barcode scanning and manual barcode entry.
- Quantity blank by default after a scan.
- Scan moves focus to quantity.
- Add Count returns ready for the next scan without unnecessarily opening the full alphabetic keyboard.
- Location workflow.
- Item list and last-scanned visibility/highlight behavior.
- Simple multiplication count entry, e.g. `12 units × 10 cases = 120`.
- Import and export controls in the familiar location/order.

## Import / Export requirements requested after the baseline
These are the only format changes to carry forward unless explicitly changed later:
- File extension: `.txt`
- Delimiter: TAB
- Field/column order must be simple to understand and configure.
- Prefer the earlier simple format-selection interaction over a technical configuration screen.
- Barcode is required.
- Optional fields may include Description, Price, Quantity, and Location.

## Change discipline
Before modifying a future version:
1. Compare requested change against this baseline.
2. Keep every unrelated working feature unchanged.
3. Never replace the whole activity/UI to solve a small issue.
4. Build on a new versionCode/versionName so Android can update in place.
5. Use the permanent iCE signing key.
6. Verify the release APK signature before handoff.
