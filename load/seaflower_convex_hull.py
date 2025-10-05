# pip install geopandas shapely pyproj fiona (si no los tienes)
import pandas as pd
import geopandas as gpd

# ==== 1) Coordenadas reales dadas (lat, lon) ====
SW_lat, SW_lon = 12.00284, -81.99937
NE_lat, NE_lon = 14.98947, -79.83031

# Derivadas
NW_lat, NW_lon = NE_lat, SW_lon
SE_lat, SE_lon = SW_lat, NE_lon

# ==== 2) Construir DataFrame con los puntos ====
df = pd.DataFrame([
    {"name": "SW", "lat": SW_lat, "lon": SW_lon},
    {"name": "NW", "lat": NW_lat, "lon": NW_lon},
    {"name": "NE", "lat": NE_lat, "lon": NE_lon},
    {"name": "SE", "lat": SE_lat, "lon": SE_lon},
])

# ==== 3) Convertir a GeoDataFrame (EPSG:4326 -> lon/lat) ====
gdf = gpd.GeoDataFrame(
    df,
    geometry=gpd.points_from_xy(df["lon"], df["lat"]),
    crs="EPSG:4326"
)

# ==== 4) Exportar a GeoJSON (FeatureCollection de PUNTOS) ====
out_path = "load/data/seaflower_convexhull.geojson"
gdf.to_file(out_path, driver="GeoJSON")
print(f"GeoJSON de puntos escrito en: {out_path}")

# (Opcional) obtener el GeoJSON como dict/string sin escribir a disco:
geojson_dict = gdf.to_json()          # string JSON del FeatureCollection
# import json; print(json.dumps(json.loads(geojson_dict), indent=2))
