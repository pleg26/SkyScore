from decimal import Decimal, InvalidOperation

import folium

FRANCE_MAP_CENTER = (46.603354, 1.888334)  # Geographic center of France
FRANCE_MAP_ZOOM = 6
AIRFIELD_MAP_ZOOM = 12


def _float_or_none(value):
    if value in (None, ''):
        return None
    try:
        return float(Decimal(str(value)))
    except (InvalidOperation, TypeError, ValueError):
        return None


def _has_valid_coordinates(lat, lon):
    if lat is None or lon is None:
        return False
    if not (-90 <= lat <= 90 and -180 <= lon <= 180):
        return False
    # 0,0 is the model default and should not be treated as a real airfield location.
    if lat == 0 and lon == 0:
        return False
    return True


def default_tile_url():
    return '/osm-tiles/{z}/{x}/{y}.png'


def add_default_tiles(base_map):
    folium.TileLayer(
        tiles='https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png',
        name='CartoDB Positron',
        attr='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors, &copy; <a href="https://carto.com/attributions">CARTO</a>',
        show=False,
    ).add_to(base_map)

    folium.TileLayer(
        tiles=default_tile_url(),
        name='OpenStreetMap',
        attr='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
        show=True,
    ).add_to(base_map)

    folium.TileLayer(
        tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
        name='Satellite',
        attr='Tiles &copy; Esri &mdash; Source: Esri, i-cubed, USDA, USGS, AEX, GeoEye, Getmapping, Aerogrid, IGN, IGP, UPR-EGP, and the GIS User Community',
        show=False,
    ).add_to(base_map)

    folium.TileLayer(
        tiles='https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png',
        name='OpenTopoMap',
        attr='Map data: &copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors, <a href="http://viewfinderpanoramas.org">SRTM</a> | Map style: &copy; <a href="https://opentopomap.org">OpenTopoMap</a> (<a href="https://creativecommons.org/licenses/by-sa/3.0/">CC-BY-SA</a>)',
        show=False,
    ).add_to(base_map)

    base_map.add_child(folium.LayerControl())
    return base_map


def airfield_map_html(lat=None, lon=None, title='Airfield'):
    has_coordinates = _has_valid_coordinates(lat, lon)
    location = [lat, lon] if has_coordinates else list(FRANCE_MAP_CENTER)
    zoom_start = AIRFIELD_MAP_ZOOM if has_coordinates else FRANCE_MAP_ZOOM

    base_map = folium.Map(
        location=location,
        height='320px',
        width='100%',
        zoom_start=zoom_start,
        control_scale=True,
        tiles=None,
    )
    add_default_tiles(base_map)

    if has_coordinates:
        folium.Marker(location=location, popup=title, tooltip=title).add_to(base_map)

    return base_map._repr_html_()


def airfield_map_from_form(form):
    lat = _float_or_none(form['lat'].value())
    lon = _float_or_none(form['lon'].value())
    if lat == 0 and lon == 0:
        lat = None
        lon = None
    code = (form['code'].value() or '').strip()
    name = (form['name'].value() or '').strip()
    title = ' - '.join(part for part in [code, name] if part) or 'Airfield'
    return airfield_map_html(lat=lat, lon=lon, title=title)
