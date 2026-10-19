# Victoria Coffee — Warehouse and Showroom Count Locations (OnHand 3.0.238)

This location template is intended **only for active inventories named Victoria** in OnHand. Other customer workflows are unchanged. The first map is **schematic, not to scale**; actual rack position and aisle orientation must be verified onsite before attaching printed labels.

## Location hierarchy and exact scannable text

| Count area | Main location | Exact location labels |
| --- | --- | --- |
| Walls | Each wall standalone | `Front-Wall`, `Left-Wall`, `Right-Wall`, `Back-Wall` |
| Aisles | Each aisle standalone | `Aisle-01` … `Aisle-10` |
| Overhead | `Overhead` | `Overhead-01` … `Overhead-10` (first four correspond to the photographed four-item overhead map; the remaining six to the second area, pending physical label placement) |
| Pallet racking | `Bay-XX` | `Bay-XX-T1-P1`, `Bay-XX-T1-P2`, `Bay-XX-T2-P1`, `Bay-XX-T2-P2`, `Bay-XX-T3-P1`, `Bay-XX-T3-P2` (T1 bottom; T3 top; P1/P2 should be assigned consistently left/right when facing the bay) |
| Under staircase | `Under-Stair` | `Under-Stair-Left`, `Under-Stair-Center`, `Under-Stair-Right`, `Under-Stair-Pallet-01`, `Under-Stair-Pallet-02`, `Under-Stair-Shelf` |
| Supply shelves | `Supply-Shelves` | `Supply-Shelves-White`, `Supply-Shelves-Metal-01`, `Supply-Shelves-Metal-02`, `Supply-Shelves-Top`, `Supply-Shelves-Bottom` |
| Utility | `Utility-Area` | `Utility-Fridge`, `Utility-Table`, `Utility-Boxes`, `Utility-Floor` |
| Floor stock | `Floor-Pallets` | `Floor-Pallet-01` … `Floor-Pallet-05` |
| Equipment rack | `Equipment-Rack` | `Equipment-Rack-Bottom`, `Equipment-Rack-Middle`, `Equipment-Rack-Top`, `Equipment-Rack-Front`, `Equipment-Rack-Side` |
| Staging | `Equipment-Staging` | `Equipment-Staging-Cart-01`, `Equipment-Staging-Cart-02`, `Equipment-Staging-Floor-01`, `Equipment-Staging-Floor-02` |
| Showroom | `Showroom` | `Showroom-Front`, `Showroom-Back`, `Showroom-Left`, `Showroom-Right`, `Showroom-Center` |
| Display shelving | `Display-Shelves` | `Display-Shelves-Left`, `Display-Shelves-Center`, `Display-Shelves-Right`, `Display-Shelves-Top`, `Display-Shelves-Bottom` |
| Demo floor | `Demo-Floor` | `Demo-Floor-01` … `Demo-Floor-05` |

## Schematic map

The in-app **VICTORIA COFFEE — VISUAL FLOOR PLAN** shows quantity tiles grouped in conceptual areas, not purported physical orientation.

```text
VICTORIA COFFEE — WAREHOUSE / SHOWROOM
                 NOT TO SCALE
┌───────────────── WAREHOUSE — STRUCTURE ─────────────────┐
│ Walls             Aisles             Rack Bays          │
│ Overhead (10 distinct positions)                        │
├────────────────── WAREHOUSE — STOCK ────────────────────┤
│ Floor Pallets     Under Stair         Supply Shelves    │
│ Utility                                                │
├──────────────── WAREHOUSE — EQUIPMENT ──────────────────┤
│ Equipment Rack                     Staging              │
├────────────────── SHOWROOM / OFFICE ────────────────────┤
│ Showroom          Display Shelves    Demo Floor         │
├────────────────── RECONCILIATION ───────────────────────┤
│ Other / Unmapped                                        │
│ Overall grand quantity = sum of all counted locations   │
└─────────────────────────────────────────────────────────┘
```

## Counting and audit flow

1. Open a Victoria Coffee inventory and tap **Change Location** → **Victoria Coffee — Visual Floor Plan**. Tap a conceptual area, then tap the exact location.
2. Or scan a printed location barcode into the Bluetooth location input. Scanning an exact `Overhead-04` or `Bay-01-T2-P1` keeps the exact position rather than reducing to a parent.
3. Scan item barcodes and enter quantities. For every item row, keep the exact location code in the stored record.
4. Map tiles sum the counted quantity for each area; the **Other / Unmapped** area preserves visibility of counts that do not match the new area names. The grand quantity is the sum of all item rows for the active Victoria inventory.
5. Configure physical Bay numbers from **Add / Set Up Warehouse Bays**. Actual bay count, positions, and printable label placement require onsite verification; do not infer them from photos.
6. For barcode labels, encode the location text exactly. Use a Code 128-compatible format for names containing letters and hyphens. Verify scanning using the external laser scanner before installing labels overhead.
7. Batch/user reconciliation remains a separate mandatory final-count check; the visual map is an additional spatial audit rather than a replacement for import/export checks.

## Safety and scope

- Adding locations must never reset, replace, append, or mutate inventory counts.
- Existing Petrosoft, Fleet Feet, Victoria customer reports and other templates are preserved.
- Previous counting-location persistence remains intact.
- No physical survey measurements have been claimed.
