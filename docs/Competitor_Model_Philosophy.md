# Competitor Model Philosophy

Last updated: 2026-06-03

## Implementation Status

### Implemented
1. Competitor is managed in `database` app and stored in legacy-compatible table.
2. Competitor is linked one-to-one to `common.User` when explicit competitor role exists.
3. Shared identity/profile fields are synchronized between User and Competitor.
4. Aircraft domain is implemented:
   1. Aircraft type (`PARAMOTOR`, `MICROLIGHT`)
   2. Aircraft class (PF1/PL1/PF2/PL2, Trike 1/2, Multiaxis 1/2, Autogyro 1/2)
5. Crew domain is implemented:
   1. Only Pilot/Navigator pairing
   2. Same aircraft type required
   3. Crew forbidden for class `*1`, allowed for class `*2`
6. Equipment normalization models are implemented:
   1. `Manufacturer`
   2. `WingModel`
   3. `CartModel`
   4. `ULMModel`
   5. `EngineModel`
7. Conditional equipment configuration is implemented.
8. Eligibility fields are implemented on competitor:
   1. Insurance valid (default `False`)
   2. Medical certificate valid (default `False`)
9. Competition registration blocks competitors if:
   1. Aircraft type does not match competition type
   2. Insurance is not valid
   3. Medical certificate is not valid

### Remaining
1. Country-based registration/radio callsign validation.
2. Competitor dashboard for historical and live scoring views.
3. Master data seed/import strategy for equipment references.

## Core Principles

1. Avoid redundant free-text technical data.
2. Keep profile identity synchronized between authentication (`User`) and competition profile (`Competitor`).
3. Store competition eligibility explicitly and enforce at competition linking time.

## Conditional Equipment Rules

### Paramotor
Required domain block:
1. Frame manufacturer/model (stored in cart fields with paramotor labels in UI)
2. Engine manufacturer/model
3. Wing manufacturer/model
4. Wing length
5. Wing surface
6. Wing PTV
7. Crew weight

Forbidden block:
1. Aircraft manufacturer/model (`cell_manufacturer`, `cell_model`)

### Microlight Trike (Trike 1 / Trike 2)
Required domain block:
1. Cart manufacturer/model
2. Engine manufacturer/model
3. Wing manufacturer/model

Forbidden block:
1. Aircraft manufacturer/model
2. Paramotor metric fields (`wing_length`, `wing_surface`, `wing_ptv`, `crew_weight`)

### Microlight Non-Trike (Multiaxis, Autogyro)
Required domain block:
1. Aircraft manufacturer/model (`cell_manufacturer`, `cell_model`)
2. Engine manufacturer/model

Forbidden block:
1. Cart manufacturer/model
2. Wing manufacturer/model
3. Paramotor metric fields (`wing_length`, `wing_surface`, `wing_ptv`, `crew_weight`)

## Role-Based Equipment Rules

1. Pilot can have equipment fields according to aircraft rules.
2. Navigator cannot keep equipment data.

## Crew Rules

1. Crew must pair one Pilot and one Navigator.
2. Crew must share same aircraft type.
3. Class `*1`: crew must be empty.
4. Class `*2`: crew can be selected.

## Settings and Licensing

In user settings and synchronized competitor profile:
1. FAI licence number (optional)
2. National licence number (optional)
3. Club (optional)

## Notes

1. Competition app migration state has been cleaned safely using state-only migration to remove historical internal competitor model from app state.
2. Database table integrity is preserved during cleanup.
