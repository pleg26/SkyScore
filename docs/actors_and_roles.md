# Actors and Roles - SkyScore

Last updated: 2026-06-02

## Roles Defined in the Current User Model
1. ADM (Administrator)
2. ORG (Organizer)
3. PIL (Pilot)
4. JUD (Judge)
5. PUB (Public)

## Currently Implemented Access in the UI
1. ADM:
   1. Full season management, including active-season switch
   2. Database menu (Country, Airfield CRUD)
2. ORG:
   1. Season consultation flows (select/active/others)
   2. No database CRUD access
3. PIL, JUD, PUB:
   1. Roles exist in the model
   2. Dedicated functional modules are not exposed yet in navigation

## Notes
1. Authentication is email-only.
2. Fine-grained role-based features beyond season/database are planned but not yet implemented.