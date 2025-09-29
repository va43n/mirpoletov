# Модуль для подготовки данных к вставки в БД, рассчету метрик и т.д.
import os
import time
import logging
import uuid
from bisect import bisect_left

import geopandas as gpd
from shapely.geometry import Point
import psycopg as pg
import numpy as np

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

def binary_search(a, x, lo=0, hi=None, key=None):
    if hi is None: hi = len(a)
    pos = bisect_left(a, x, lo, hi, key=key)                 
    return pos if pos != hi and key(a[pos]) == x else -1  

def find_duplicates(completed_data: list, data_from_db: list, resulting_data: list):
    duplicated = 0
    mid_result = []
    if data_from_db:
        start_db = time.time()
        for data in completed_data:
            # cur_duplicated = 0
            if binary_search(data_from_db, data.sid, key=lambda x: x[0]) == -1:
                # for res_data in resulting_data:
                #if res_data.sid == data.sid:
                       # duplicated += 1
                        #cur_duplicated = 1
                        #break
                #if cur_duplicated != 1:
                mid_result.append(data)
            else:
                duplicated += 1
        logging.info("Finding duplicates: db: {} sec.".format(time.time() - start_db))
    else: mid_result = completed_data
    start_self = time.time()
    mid_result.sort(key=lambda x: x.sid)
    self_duplicated = 0
    for i, data in enumerate(mid_result):
        if binary_search(resulting_data, data.sid, key=lambda x: x.sid) == -1:
            resulting_data.append(data)

        #cur_duplicated = 0
        #for res_data in resulting_data:
        #    if data.sid == res_data.sid:
        #        cur_duplicated = 1
        #        break
        #if cur_duplicated:
        #    seld_duplicated += 1
        else:
            self_duplicated += 1
    logging.info("Finding duplicates: self: {} sec.".format(time.time() - start_self))
    logging.info("Finding duplicates: dup: {}, self: {}".format(duplicated, self_duplicated))
    return (duplicated, self_duplicated)
            
    
if __name__ == "__main__":
    from db_work import open_regions
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
