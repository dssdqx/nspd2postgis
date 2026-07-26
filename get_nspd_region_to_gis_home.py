import os 
import geopandas as gpd
from pynspd import Nspd, NspdFeature
import json
import psycopg
from psycopg.types.json import Jsonb
import pandas as pd

# ---------- загрузка данных ----------

output_file = r'c:\Dev\postgis_etl\gran_nas_punkt_perm.geojson'


nspd = Nspd(
    client_timeout=20,
    client_retries=5,
    cache_folder_path=r"c:\maps\geocoder\nspd_cache",
    cache_ttl=None
)


fields_from_nspd = {
    "cad_num": "Кадастровый номер",
    "readable_address": "Адрес",
    "status": "Статус",
    "land_record_category_type": "Категория земель",
    "permitted_use_established_by_document": "Назначение",
    "ownership_type": "Собственность",
    "cost_value": "Кадастровая стоимость",
    "determination_couse": "Основание оценки",
    "land_record_subtype": "Подкатегория землепользования",
    "land_record_reg_date": "Дата постановки на учёт"
}



# ---------- загрузка региона ----------
region = gpd.read_file(r"c:\maps\general_layers\perm_krai_gran.geojson")

# если там мультиполигон — объединяем в один
contour = region.geometry.union_all()

layer = NspdFeature.by_title("Населённые пункты (полигоны)")

# ---------- запрос ----------
feats = nspd.search_in_contour(contour, layer)


print(f"Найдено {len(feats)} объектов")

'''for feat in feats[:1]:
    print(feat.properties.options)
    print(feat.properties.model_dump().keys())
    print(feat.properties.label)'''


rows = []

for f in feats:
    props = f.properties.model_dump()

    # ВАЖНО: geometry приводим в shapely
    geom = f.geometry.to_shape()

    # раскладываем options внутрь верхнего уровня
    options = props.pop("options", {})
    if hasattr(options, "model_dump"):
        options = options.model_dump()

    row = {
        **props,
        **options,
        "geometry": geom
    }

    rows.append(row)

gdf = gpd.GeoDataFrame(rows, crs="EPSG:4326")

#gdf.to_file(output_file, driver="GeoJSON", encoding="utf-8")



DB_CONFIG = {
    "host": "localhost",
    "dbname": "gis_home",
    "user": "postgres",
    "password": "21194",
}

def execute_query(query, params=None):
    with psycopg.connect(**DB_CONFIG) as conn:
        with conn.cursor() as cur:
            cur.execute(query, params)
            if cur.description:  # Check if the query returns rows
                #return cur.fetchall()
                return cur.fetchone()
            else:
                return None


# только если есть объекты — очищаем таблицу
if len(feats) > 0:
    execute_query("TRUNCATE TABLE boundaries.nas_poly_nspd")
    print("Таблица boundaries.nas_poly_nspd очищена")



sql = """
INSERT INTO boundaries.nas_poly_nspd (
    name,
    name_locality,
    category,
    category_name,
    system_info,
    cadastral_districts_code,
    description,
    external_key,
    interaction_id,
    label,
    subcategory,
    registration_date,
    reg_code,
    document_name,
    document_date,
    document_issuer,
    code,
    date_cr,
    guid,
    geom
)
VALUES (
    %(name)s,
    %(name_locality)s,
    %(category)s,
    %(category_name)s,
    %(system_info)s,
    %(cadastral_districts_code)s,
    %(description)s,
    %(external_key)s,
    %(interaction_id)s,
    %(label)s,
    %(subcategory)s,
    %(registration_date)s,
    %(reg_code)s,
    %(document_name)s,
    %(document_date)s,
    %(document_issuer)s,
    %(code)s,
    %(date_cr)s,
    %(guid)s,
    ST_GeomFromText(%(wkt)s,4326)
)
ON CONFLICT (guid)
DO UPDATE SET
    name = EXCLUDED.name,
    name_locality = EXCLUDED.name_locality,
    geom = EXCLUDED.geom;
"""

with psycopg.connect(**DB_CONFIG) as conn:
    with conn.cursor() as cur:

        for _, row in gdf.iterrows():

            data = row.drop("geometry").to_dict()
            for key, value in data.items():
                if pd.isna(value):
                    data[key] = None

            data["wkt"] = row.geometry.wkt

            if data.get("system_info") is not None:
                #data["system_info"] = Jsonb(data["system_info"])
                data["system_info"] = None
            cur.execute(sql, data)

    conn.commit()
    print(f"✅ Загружено {len(gdf)} объектов в boundaries.nas_poly_nspd")


query = """
SELECT count(*) FROM boundaries.nas_poly_nspd
"""


print(query)
rows = execute_query(query)
print(f'{rows} -  postgres, количество записей в boundaries.nas_poly_nspd')
