# Модуль для подготовки данных к вставки в БД, рассчету метрик и т.д.
import os
import time
import logging
import uuid

import geopandas as gpd
from shapely.geometry import Point
import psycopg as pg
import numpy as np

from db_work import open_regions
from parser import read_excel_calamine, parse_rows


def compute_regions_types(parsed_data: list, regions, types: dict, completed_data: list):
    points = []
    indexes = []
    wrong_data = 0
    start = time.time()
    for i, data in enumerate(parsed_data):
        if data.b_type not in types:
            wrong_data += 1
            logging.debug("Completing data: no supported b_type")
            continue
        data.b_type = types[data.b_type]
        if not isinstance(data.b_type, int):
            wrong_data += 1
            logging.debug("Completing data: no supported b_type")
            continue
        if data.longd != -1000 and data.latd != -1000:
            points.append(Point(data.longd, data.latd))
            indexes.append(i)
        elif data.longa != -1000 and data.lata != -1000:
            points.append(Point(data.longa, data.lata))
            indexes.append(i)
        else:
            wrong_data += 1
            logging.debug("Completing data: no coordinates")
            continue
    got_points_time = time.time()
    logging.info("Completing data: making points: {} sec.".format(got_points_time - start))
    points_data = {'geometry': points, 'id': indexes}
    points_gdf = gpd.GeoDataFrame(points_data, crs="EPSG:4326")
    converter_time = time.time()
    logging.info("Completing data: converted into p_gdf: {} sec.".format(converter_time - got_points_time))

    joined_regions = gpd.sjoin(regions, points_gdf, how="inner")
    join_time = time.time()
    logging.info("Completing data: joined data: {} sec.".format(join_time - converter_time))
    ids_left = joined_regions.index.array
    ids_right = joined_regions["index_right"].array
    for i in range(len(ids_left)):
        if not isinstance(ids_left[i], np.int64):
            wrong_data += 1
            continue
        completed_data.append(parsed_data[ids_right[i]])
        completed_data[-1].region = int(ids_left[i])
    logging.info("Completing data: completed last step: {} sec.".format(time.time() - join_time))
    return wrong_data


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
        conn.commit()
    except Exception as e:
        logging.info("Inserting flights: trouble occured while inserting: {}".format(e))
        conn.rollback()
    finally:
        cur.close()
    return count
    
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    regions = open_regions()
    types = {"BLA": 0, "SHAR": 2, "AER": 1}
    filepath = "/2025.xlsx"
    fullpath = os.path.expanduser("~") + filepath
    r = open(fullpath, "rb")
    headers, rows = read_excel_calamine(r)
    parsed_data = parse_rows(rows)
    completed_data = []
    wrong_completed = compute_regions_types(parsed_data, regions, types, completed_data)
    logging.info("Completing data: wrong completed: {}".format(wrong_completed))

    logging.info("Completing data: got records: {}".format(len(completed_data)))
