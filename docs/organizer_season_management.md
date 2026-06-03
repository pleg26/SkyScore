# Organizer - Season Management - SkyScore

Last updated: 2026-06-03

## Implemented Season Flows
The menu currently exposes three organizer/admin views:
1. Select active season
2. View active season
3. View other seasons

## Access Rules
1. Available to roles ADM and ORG
2. Activation action is restricted to ADM

## Active Season Behavior
1. Exactly one global season is marked active
2. For ADM users, active season is also stored on Administrator.active_season
3. Competition creation can auto-create missing season and activate it
4. Auto-created season uses competition type/subtype/year tuple

## Season Fields and Defaults
1. Type + subtype + year define the business identity
2. Start/end dates default to full calendar year where auto-created

## Notes
1. Season creation page is not exposed in the current navigation flow
2. The UI is focused on selection and consultation workflows
3. Competition creation remains the canonical path for season auto-creation