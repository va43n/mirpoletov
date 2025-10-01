# Модуль для занесения записей о регинах в БД
import sys
import logging
import os
import time

import geopandas as gpd
from sqlalchemy import create_engine
from sqlalchemy.engine import URL
import psycopg


logging.basicConfig(level=logging.INFO)
file = open("../../../../stuff")
stuff = file.read().strip("\n\r ")
start = time.time()

params = {"drivername": "postgresql", "host": "192.168.0.200", "port": "5433", "database": "regions", "username": "drones", "password": stuff}
conn_string = f"postgresql+psycopg://drones:{stuff}@192.168.0.200:5433/regions"
eng = create_engine(conn_string)
with eng.connect() as conn:
    with conn.begin() as trans:
        conn_made_time = time.time()
        logging.info("Connection made in {} sec.".format(conn_made_time - start))

        gdf = gpd.read_file("regions/regions.gpkg")
        gdf = gdf.rename_geometry("geom")
        gdf = gdf.rename(columns={"ref": "data_code"})
        file_read_time = time.time()    
        logging.info("File read in {} sec.".format(file_read_time - conn_made_time))

        try:
            gdf.to_postgis("regions", conn, if_exists="append")
        except Exception as e:
            print(e)
            trans.rollback()
            exit(-1)
        trans.commit()
        information_sent_time = time.time()
        logging.info("Information sent in {} sec.".format(information_sent_time - file_read_time))
    

