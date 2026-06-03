# Actors and Roles - SkyScore

Last updated: 2026-06-03

## Roles Defined in the Current User Model
1. ADM (Administrator)
2. ORG (Organizer)
3. COMP (Competitor)
4. JUD (Judge)
5. PUB (Public)

## Currently Implemented Access in the UI
1. ADM:
   1. Full season management, including active-season switch
   2. Database menu (Country, Airfield, User, Competitor CRUD)
2. ORG:
   1. Season consultation flows (select/active/others)
   2. No database CRUD access
3. COMP:
   1. Login and home access
   2. Profile settings page (personal and licence fields)
4. JUD, PUB:
   1. Roles exist in the model
   2. Dedicated functional modules are not exposed yet in navigation

## Notes
1. Authentication is email-only.
2. Legacy `PIL` code is normalized to `COMP` in user role handling.
3. User and competitor shared profile fields are synchronized bidirectionally in management forms.