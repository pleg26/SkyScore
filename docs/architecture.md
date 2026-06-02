# SkyScore Architecture

Last updated: 2026-06-02

## Project Layout (Current)
SkyScore/
1. src/python/sky_score/: Django project configuration
2. src/python/common/: authentication, shared context, global utilities, OSM tile proxy
3. src/python/season/: season selection and active-season flows
4. src/python/competition/: competition domain models and season auto-linking
5. src/python/database/: CRUD management for Country and Airfield
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

## Key Functional Architecture
1. Email-only authentication with custom User model in common
2. Season workflow split into:
   1. Select active season
   2. View active season
   3. View other seasons
3. Database module:
   1. Country list + form in aside panel
   2. Airfield list + form in aside panel
   3. Inline delete with popup confirmation
4. Maps are centralized in common utilities:
   1. Shared tile layers
   2. Shared map generation helpers
   3. Shared OSM proxy endpoint

## Notes on Modularity
1. Country and Airfield models are maintained by database app.
2. Competition app references these models.
3. UI keeps a consistent split: mainContent for lists, asideContent for forms.

## Planned Extensions
1. Additional database reference models (competitor, task, nfz, deck)
2. Broader map reuse across other modules
3. Scoring app (not implemented yet)