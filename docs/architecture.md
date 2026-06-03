# SkyScore Architecture

Last updated: 2026-06-03

## Project Layout (Current)
SkyScore/
1. src/python/sky_score/: Django project configuration
2. src/python/common/: authentication, shared context, global utilities, OSM tile proxy
3. src/python/season/: season selection and active-season flows
4. src/python/competition/: competition domain models and season auto-linking
5. src/python/database/: CRUD management for Country, Airfield, User, and Competitor
6. src/python/templates/: shared and app templates
7. src/python/static/css/: base styles and menu/database styles

## Active Django Apps
Configured in settings:
1. common
2. season
3. competition
4. database

## URL Routing (Current)
1. / -> common app routes
2. /season/ -> season app routes
3. /database/ -> database app routes
4. /admin/ -> Django admin
5. /osm-tiles/<z>/<x>/<y>.png -> OSM tile proxy (common)
6. /profile/settings/ -> user profile self-service settings

## Key Functional Architecture
1. Email-only authentication with custom User model in common
2. Season workflow split into:
   1. Select active season
   2. View active season
   3. View other seasons
3. Database module:
   1. Country list + form in aside panel
   2. Airfield list + form in aside panel
   3. User list + form with role management and password update
   4. Competitor list + form with aircraft domain and crew logic
   3. Inline delete with popup confirmation
4. Competitor domain rules:
   1. Aircraft Type: Paramotor or Microlight
   2. Aircraft Class constrained by aircraft type
   3. Crew allowed only for class `*2`, forbidden for class `*1`
   4. Crew pairs only Pilot/Navigator and same aircraft type
   5. Conditional equipment blocks by aircraft type and class
   6. Navigator cannot carry equipment data
5. Competition competitor eligibility:
   1. Aircraft type must match competition type
   2. Insurance must be valid
   3. Medical certificate must be valid
4. Maps are centralized in common utilities:
   1. Shared tile layers
   2. Shared map generation helpers
   3. Shared OSM proxy endpoint

## Notes on Modularity
1. Country and Airfield models are maintained by database app.
2. Competition app references these models and database Competitor model.
3. UI keeps a consistent split: mainContent for lists, asideContent for forms.
4. Profile settings in `common` and management forms in `database` are synchronized for shared user/competitor attributes.

## Planned Extensions
1. Country-specific validation for registration and radio callsign
2. Competitor dashboard and scoring views
3. Master-data import strategy for manufacturers and equipment models