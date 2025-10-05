#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Convierte una capa de polígonos de un File Geodatabase (.gdb) a GeoJSON.
- Lista capas disponibles.
- Carga la capa de polígonos (por defecto intenta la WDPA_WDOECM_poly_*).
- (Opcional) Filtra por nombre (e.g., "Seaflower").
- Repara geometrías inválidas y disuelve a un único polígono.
- Exporta a GeoJSON en EPSG:4326.

Requisitos:
  pip install geopandas shapely fiona pyproj

NOTA GDAL/Fiona:
- En la mayoría de instalaciones, Fiona usa el driver "OpenFileGDB" (solo lectura),
  suficiente para leer .gdb sin ArcGIS. Si tu GDAL es antiguo, actualízalo.
"""

import argparse
import sys
from pathlib import Path
import geopandas as gpd
import fiona
from shapely import unary_union
from shapely.geometry import shape

def list_layers(gdb_path: Path):
    try:
        layers = fiona.listlayers(gdb_path.as_posix())
        return list(layers)
    except Exception as e:
        print(f"[ERROR] No pude listar capas en: {gdb_path}\n{e}")
        sys.exit(1)

def pick_default_poly_layer(layers):
    """
    Heurística para escoger la capa de polígonos de WDPA.
    Ajusta si tu nombre difiere.
    """
    candidates = [ly for ly in layers if "poly" in ly.lower()]
    if candidates:
        # Si detectaste estos nombres en tu entorno, intenta el más específico primero
        # p.ej.: WDPA_WDOECM_poly_Oct2025_555636411
        candidates_sorted = sorted(candidates, key=len)  # o invierte si prefieres la más larga
        return candidates_sorted[-1]
    # si no hay "poly", devuelve la primera por defecto
    return layers[0] if layers else None

def load_layer(gdb_path: Path, layer_name: str) -> gpd.GeoDataFrame:
    print(f"[INFO] Cargando capa: {layer_name}")
    gdf = gpd.read_file(gdb_path.as_posix(), layer=layer_name)
    # Asegura CRS WGS84
    if gdf.crs is None:
        print("[WARN] La capa no tiene CRS definido. Asumiendo EPSG:4326 (lon/lat).")
        gdf.set_crs(epsg=4326, inplace=True)
    elif gdf.crs.to_epsg() != 4326:
        print(f"[INFO] Reproyectando de {gdf.crs} a EPSG:4326…")
        gdf = gdf.to_crs(epsg=4326)
    return gdf

def filter_by_name(gdf: gpd.GeoDataFrame, name_field: str, name_value: str):
    # Intento flexible: si no encuentras el campo exacto, prueba variantes típicas
    candidates = [name_field, name_field.upper(), name_field.lower(), "NAME", "name", "WDPA_NAME", "WDPA_NAME_1"]
    for field in candidates:
        if field in gdf.columns:
            print(f"[INFO] Filtrando por {field} == '{name_value}'")
            return gdf[gdf[field].astype(str).str.contains(name_value, case=False, na=False)]
    print("[WARN] No encontré un campo de nombre estándar. No se aplicará filtro por nombre.")
    return gdf

def fix_geometries(gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    # Reparar geometrías inválidas con buffer(0)
    invalid = ~gdf.geometry.is_valid
    if invalid.any():
        print(f"[INFO] Reparando {invalid.sum()} geometrías inválidas con buffer(0)…")
        gdf.loc[invalid, "geometry"] = gdf.loc[invalid, "geometry"].buffer(0)
    # Eliminar vacías
    empty = gdf.geometry.is_empty
    if empty.any():
        print(f"[INFO] Eliminando {empty.sum()} geometrías vacías…")
        gdf = gdf[~empty].copy()
    return gdf

def dissolve_to_single(gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    if len(gdf) <= 1:
        return gdf
    # Disolver todo a un único registro
    print("[INFO] Disolviendo múltiple a un único polígono…")
    dissolved = gdf.dissolve()  # disuelve todo (sin grupo)
    dissolved = dissolved.explode(index_parts=False).dissolve()  # por si quedan multiparts raros
    dissolved = dissolved.reset_index(drop=True)
    return dissolved

def main():
    parser = argparse.ArgumentParser(description="Convertir .gdb a GeoJSON")
    parser.add_argument("--gdb", required=True, help="Ruta a la carpeta .gdb")
    parser.add_argument("--layer", default=None, help="Nombre exacto de la capa dentro de la .gdb (opcional)")
    parser.add_argument("--name_field", default="NAME", help="Campo de nombre para filtrar (opcional)")
    parser.add_argument("--name_value", default="Seaflower", help="Valor a buscar en el nombre (opcional)")
    parser.add_argument("--out", default="seaflower.geojson", help="Ruta de salida GeoJSON")
    parser.add_argument("--no_filter", action="store_true", help="No filtrar por nombre; exportar todo")
    parser.add_argument("--keep_multi", action="store_true", help="No disolver a único polígono (mantener múltiples features)")
    args = parser.parse_args()

    gdb_path = Path(args.gdb)
    if not gdb_path.exists():
        print(f"[ERROR] No existe la ruta: {gdb_path}")
        sys.exit(1)

    layers = list_layers(gdb_path)
    print("[INFO] Capas encontradas en la GDB:")
    for ly in layers:
        print(f"  - {ly}")

    layer_name = args.layer or pick_default_poly_layer(layers)
    if not layer_name:
        print("[ERROR] No se pudo determinar la capa a leer. Indica --layer explícitamente.")
        sys.exit(1)

    gdf = load_layer(gdb_path, layer_name)
    print(f"[INFO] Campos disponibles: {list(gdf.columns)}")

    if not args.no_filter:
        gdf = filter_by_name(gdf, args.name_field, args.name_value)
        if gdf.empty:
            print(f"[ERROR] No se encontraron features con '{args.name_value}'. "
                  f"Prueba con --no_filter para exportar todo o ajusta --name_field/--name_value.")
            sys.exit(2)

    gdf = fix_geometries(gdf)

    if not args.keep_multi:
        gdf = dissolve_to_single(gdf)

    # Asegurar CRS correcto para GeoJSON
    if gdf.crs is None or gdf.crs.to_epsg() != 4326:
        gdf = gdf.set_crs(epsg=4326, allow_override=True)

    out_path = Path(args.out)
    print(f"[INFO] Exportando a GeoJSON: {out_path}")
    gdf.to_file(out_path.as_posix(), driver="GeoJSON")
    print("[OK] Listo.")

if __name__ == "__main__":
    main()
