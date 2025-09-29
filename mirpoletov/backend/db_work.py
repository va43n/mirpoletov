# Модуль работы с базой данных
import sys
import logging
import os
import time
import uuid

import geopandas as gpd
from sqlalchemy import create_engine
from sqlalchemy.engine import URL
import psycopg


def open_regions():
    # logging.basicConfig(level=logging.INFO)
    file = open("../../../../../stuff")
    stuff = file.read().strip("\n\r ")
    start = time.time()
    conn_string = f"postgresql+psycopg://drones:{stuff}@192.168.0.200:5433/regions"
    eng = create_engine(conn_string)
    with eng.connect() as conn:
        with conn.begin() as trans:
            conn_made_time = time.time()
            logging.info("Connection made in {} sec.".format(conn_made_time - start))
            sql_string = "SELECT name_ru, data_code, geom FROM regions ORDER BY id";
            try:
                gdf = gpd.GeoDataFrame.from_postgis(sql_string, conn)
            except Exception as e:
                print(e)
                trans.rollback()
                return -1
            trans.commit()
            information_sent_time = time.time()
            logging.info("Information got in {} sec.".format(information_sent_time - conn_made_time))
            return gdf

def open_types():
    file = open("../../../../../stuff")
    stuff = file.read().strip("\n\r ")
    conninfo = f"dbname=regions user=drones password={stuff} host=192.168.0.200 port=5433"
    with psycopg.connect(conninfo) as conn:
        with conn.cursor() as cur:
            sql_string = "SELECT id, name FROM bpla_types;"
            cur.execute(sql_string)
            results = cur.fetchall()
            stuff = {row[1]: row[0] for row in results}
            logging.info("Types opened")
            return stuff


def insert_data_bd(completed_data: list, conn):
        cur = conn.cursor()
        start = time.time()
        tupled_data = [(uuid.uuid4(), data.sid, data.datetimed, data.flight_time_min, data.b_type, data.region, data.longd, data.latd, data.longa, data.lata) for data in completed_data]
        formatted_data_time = time.time()
        logging.info("Inserting flights: made tuples: {} sec.".format(formatted_data_time - start))
        insert_sqlstring = """INSERT INTO flights (id, sid, datetime_dep, flight_time_min, type, region, longitude_dep, latitude_dep, longitude_arr, latitude_arr) values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s) ON CONFLICT (sid) DO NOTHING;"""
        count = -1
        try:
            cur.executemany(insert_sqlstring, tupled_data)
            count = cut.rowcount
            logging.info("Inserting flights: inserted rows: {} sec., {} failed".format(time.time() - formatted_data_time, len(completed_data) - count))
        except Exception as e:
            logging.info("Inserting flights: trouble occured while inserting: {}".format(e))
        finally:
            cur.close()
        return count

if __name__ == "__main__":
    gdf = open_regions()
    print(gdf)
    types = open_types()
    print(types)

