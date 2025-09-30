# Модуль работы с базой данных
import sys
import logging
import os
import time
import uuid
import datetime

import geopandas as gpd
from sqlalchemy import create_engine
from sqlalchemy.engine import URL
import psycopg

from parser import read_excel_calamine, parse_rows
from preparing_data import compute_regions_types, find_duplicates, get_parsed_by_datetime_data, make_regions_dict


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


def insert_data_db(completed_data: list, conn):
        cur = conn.cursor()
        start = time.time()
        tupled_data = [(uuid.uuid4(), data.sid, data.datetimed, data.flight_time_min, data.b_type, data.region, data.longd, data.latd, data.longa, data.lata) for data in completed_data]
        formatted_data_time = time.time()
        logging.info("Inserting flights: made tuples: {} sec.".format(formatted_data_time - start))
        insert_sqlstring = """INSERT INTO flights (id, sid, datetime_dep, flight_time_min, type, region, longitude_dep, latitude_dep, longitude_arr, latitude_arr) values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s) ON CONFLICT (sid) DO NOTHING;"""
        count = -1
        try:
            cur.executemany(insert_sqlstring, tupled_data)
            count = cur.rowcount
            logging.info("Inserting flights: inserted rows: {} sec., {} failed".format(time.time() - formatted_data_time, len(completed_data) - count))
        except Exception as e:
            logging.info("Inserting flights: trouble occured while inserting: {}".format(e))
        finally:
            cur.close()
        return count

def select_data_db(conn, datetime_min, datetime_max, regions, need_sid=False):
    if not isinstance(datetime_min, datetime.datetime) or not isinstance(datetime_max, datetime.datetime) or not isinstance(need_sid, bool) or not datetime_min <= datetime_max:
        logging.info("Selecting fields: some values are not of thought types")
        return -1
    for region in regions:
        if not isinstance(region, int):
            logging.info("Selecting fileds: one of modules if not integer")
            return -1
    cur = conn.cursor()
    start = time.time()
    if need_sid:
        select_sqlstring = "SELECT sid, region, datetime_dep, flight_time_min FROM flights WHERE (datetime_dep between %s and %s) and (region = ANY(%s)) ORDER BY sid;"
    else:
        select_sqlstring = "SELECT sid, region, datetime_dep, flight_time_min FROM flights WHERE (datetime_dep between %s and %s) and (region = ANY(%s));"
    
    data = -1
    try:
        cur.execute(select_sqlstring, (datetime_min, datetime_max, regions))
        logging.info("Selecting flights: in {} sec.".format(time.time() - start))
        data = cur.fetchall()
    except Exception as e:
        logging.info("Selecting flights: trouble occured: {}".format(e))
    finally:
        cur.close()
    return data

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    regions = open_regions()
    print(regions)
    types = open_types()
    print(types)
    filepath = "/2025.xlsx"
    fullpath = os.path.expanduser("~") + filepath
    r = open(fullpath, "rb")
    headers, rows = read_excel_calamine(r)
    parsed_data = parse_rows(rows)
    completed_data = []
    wrong_completed = compute_regions_types(parsed_data, regions, types, completed_data)
    logging.info("Completing data: wrong completed: {}".format(wrong_completed))

    logging.info("Completing data: got records: {}".format(len(completed_data)))
    file = open("../../../../../stuff")
    stuff = file.read().strip("\n\r ")
    conninfo = f"dbname=regions user=drones password={stuff} host=192.168.0.200 port=5433"
    data = []
    with psycopg.connect(conninfo) as conn:
        count = insert_data_db(completed_data, conn)
        logging.info("Inserting flights: got {} inserted".format(count))

        data = select_data_db(conn, datetime.datetime.today() - datetime.timedelta(days=90), datetime.datetime.today(), [0, 5, 77], need_sid=True)
        if isinstance(data, int) and data == -1:
            exit(-1)
        logging.info("Selecting flights: got {} rows".format(len(data)))
        logging.info(data[:5])
    # print(len(data))
    all_data = []
    dup, self_dup = find_duplicates(completed_data, data, all_data)
    logging.info("All data length: {}".format(len(all_data)))
    result_data = []
    wrong = get_parsed_by_datetime_data(all_data, result_data, datetime.datetime.today() - datetime.timedelta(days=90), datetime.datetime.today())
    #regions = [1, 2, 3, 55, 54]
    #regions_dict = {}
    #make_regions_dict()
    # logging.info(result_data[:5])



