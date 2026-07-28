import geopandas as gpd
import psycopg
from shapely import to_wkb
from dotenv import load_dotenv
import os


mo_rf_gran = gpd.read_file(r'c:\maps\general_layers\mo_multi_fed_actual.gpkg')

# Загружаем переменные из файла .env в окружение
load_dotenv()

# Собираем конфиг напрямую из os.getenv
DB_CONFIG = {
    "host": os.getenv("DB_HOST"),
    "port": os.getenv("DB_PORT"),
    "dbname": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASSWORD"),
}

# для проверки структуры таблицы в PostgreSQL
def execute_query(query, params=None):
    with psycopg.connect(**DB_CONFIG) as conn:
        with conn.cursor() as cur:
            cur.execute(query, params)
            if cur.description:  # Check if the query returns rows
                return cur.fetchall()
            else:
                return None

# для проверки структуры таблицы в PostgreSQL
def get_columns(schema, table):
    query = """
    SELECT column_name
    FROM information_schema.columns
    WHERE table_schema = %s
      AND table_name = %s
    ORDER BY ordinal_position;
    """

    rows = execute_query(query, (schema, table))
    return [r[0] for r in rows]


columns = get_columns("boundaries", "gran_mo_fo_rf")

print(columns, '-  postgres')


work_columns = mo_rf_gran.columns.str.lower().tolist()

print(work_columns, '-  gpd')



'''
print('очищаем таблицу перед загрузкой данных...')
execute_query("TRUNCATE TABLE boundaries.gran_mo_fo_rf")


with psycopg.connect(**DB_CONFIG) as conn:

    with conn.cursor() as cur:

        for _, row in mo_rf_gran.iterrows():
            cur.execute(
                """
                INSERT INTO boundaries.gran_mo_fo_rf
                (mo, fo, geom)
                VALUES (%s, %s, ST_GeomFromWKB(%s, 4326))
                """,
                (
                    row["MO"],
                    row["FO"],
                    to_wkb(row.geometry)
                )
            )

    #conn.commit()
    print("Data inserted successfully into boundaries.gran_mo_fo_rf table.")
'''


query = """
SELECT count(*) FROM boundaries.gran_mo_fo_rf
"""


print(query, '-  postgres, запрос')
rows = execute_query(query)
print(f'{rows} -  postgres, количество записей в boundaries.gran_mo_fo_rf')
