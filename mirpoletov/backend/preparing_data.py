# Модуль для подготовки данных к вставки в БД, рассчету метрик и т.д.
import os
import time
import logging
import uuid
from bisect import bisect_left, bisect_right
import datetime

import geopandas as gpd
from shapely.geometry import Point
import psycopg as pg
import numpy as np

from parser import read_excel_calamine, parse_rows, ParsedData


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

def get_parsed_by_datetime_data(completed_data: list, result_data: list, min_datetime, max_datetime):
    if not isinstance(min_datetime, datetime.datetime) or not isinstance(max_datetime, datetime.datetime) or not min_datetime < max_datetime:
        logging.info("Parsing by datetime: some values are not of thought types")
        return -1
    not_in_datetime = 0
    start = time.time()

    #completed_data.sort(key=lambda x: x.datetimed)

    #left_index = bisect_left(completed_data, min_datetime, key=lambda x: x.datetimed)
    #right_index = bisect_right(completed_data, max_datetime, key=lambda x: x.datetimed)

    #for i in range(left_index, right_index):
    #    result_data.append(completed_data[i])
    for data in completed_data:
        if min_datetime <= data.datetimed <= max_datetime:
            result_data.append(data)
    logging.info("Parsing by datetime: done in {} sec.".format(time.time() - start))
    logging.info("Parsing by datetime: found values not in right datetime: {}".format(len(completed_data) - len(result_data)))
    return len(completed_data) - len(result_data)

def make_regions_dict(all_data: list, regions: list, regions_dict: dict):
    if not isinstance(all_data, list) or not isinstance(regions, list) or not isinstance(regions_dict, dict):
        logging.info("Making regions dict: got wrong data type")
        return -1
    start = time.time()
    for region in regions:
        if not isinstance(region, int):
            logging.info("Making regions dict: got wrong region data type")
            return -1
        regions_dict[region] = []
    summ_len = 0
    for data in all_data:
        if not isinstance(data, ParsedData):
            logging.info("Making regions dict: got not ParsedData")
            return -1
        if data.region in regions_dict:
            regions_dict[data.region].append(data)
            summ_len += 1
    logging.info("Making regions dict: done in {} sec.".format(time.time() - start))
    return summ_len

def make_db_data_into_data(all_data: list, db_data: list):
    if not isinstance(all_data, list) or not isinstance(db_data, list):
        logging.info("Making db_data in data: got wrong type")
        return -1
    start = time.time()
    for db_row in db_data:
        data = ParsedData()
        data.sid = db_row[0]
        data.datetimed = db_row[2]
        data.flight_time_min = db_row[3]
        data.region = db_ros[1]
        all_data.append(data)
    logging.info("Making db_data in data: done in {} sec.".format(time.time() - start))
    return 0

def turn_regions_to_abbrs(regions, metrics_list: list):
    if not isinstance(metrics_list, list):
        logging.info("Turn regions to abbrs: got wrong data type")
        return -1
    start = time.time()
    data_codes = regions["data_code"]
    for region_metric in metrics_list:
        if not isinstance(region_metric, list) or not len(region_metric) == 2 or not isinstance(region_metric[0], int) or region_metric[0] >= len(regions):
            logging.info("Turn regions to abbrs: got wrong region type")
            return -1
        region_metric[0] = data_codes[region_metric[0]]
    logging.info("Turn regions to abbrs: done in {} sec.".format(time.time() - start))
    return 0

def turn_abbrs_to_regions(abbrs: list, regions, list_regions: list):
    if not isinstance(abbrs, list) or not isinstance(list_regions, list):
        logging.info("Turn abbrs to regions: got wrong data type")
        return -1
    start = time.time()
    wrong = 0
    data_codes = regions["data_code"]
    for abbr in abbrs:
        if not isinstance(abbr, str):
            logging.info("Turn abbrs to regions: gor wrong abbr type")
            return -1
        for i in range(len(data_codes)):
            if data_codes[i] == abbr:
                list_regions.append(i)
                break
        else:
            wrong += 1
    logging.info("Turn abbrs to regions: done in {} sec.".format(time.time() - start))
    return wrong
            
    
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
