# Файл запуска
from typing import Optional
import json
import logging
from io import BytesIO
import asyncio
import datetime

from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, Form, UploadFile, File
from fastapi.responses import JSONResponse
import psycopg as pg

from parser import read_excel_calamine
from db_work import open_regions, open_types
from process import process_data, file_setting


logging.basicConfig(level=logging.INFO)
all_settings = ["file", "mean", "graphs", "json", "upload"]
# Можео добавить flight sensity
all_metrics = ["flights", "mean_duration", "top_regs", "peak_load", "mean_dynamic", "rise_fall", "flight_density", "day_act", "empty_days"]
all_regions = open_regions()
types = open_types()
regions_len = len(all_regions)

file = open("../../../../../stuff")
stuff = file.read().strip("\n\r ")
conninfo = f"dbname=regions user=drones password={stuff} host=192.168.0.200 port=5433"
conn = pg.connect(conninfo)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
@app.on_event("shutdown")
async def shutdown_event():
    conn.close()
    

@app.post("/api/calculate")
async def calculate_client_input(
        data: str = Form(...),
        uploadedData: Optional[UploadFile] = File(None)
    ):
    # logging.basicConfig(level=logging.INFO)
    request_data = json.loads(data)
    
    regions = request_data.get('regions', [])
    metrics = request_data.get('metrics', [])
    settings = request_data.get('settings', [])
    timestamp1 = request_data.get('timestamp1', {})
    timestamp2 = request_data.get('timestamp2', {})

    headers = {"Content-Language": "en-US"}

    if not isinstance(regions, list):
        logging.info("Taking data: regions is not a list")
        content = {"message": "regions is wrong type"}
        return JSONResponse(status_code=417, headers=headers, content=content)
    if len(regions) > regions_len:
        logging.info("Taking data: regions is too long")
        content = {"message": "regions are too long"}
        return JSONResponse(status_code=417, headers=headers, content=content)
    for region in regions:
        if not isinstance(region, str):
            logging.info("Taking data: one of regions is not a string")
            content = {"message": "one of regions is not a string"}
            return JSONResponse(status_code=417, headers=headers, content=content)
    
    if not isinstance(metrics, list):
        logging.info("Taking data: metrics is not list ")
        content = {"message": "metrics is not a list"}
        return JSONResponse(status_code=417, headers=headers, content=content)
    cur_metrics = []
    if len(metrics) > len(all_metrics):
        logging.info("Taking data: metrics is too long")
        content = {"message": "metrics is too long"}
        return JSONResponse(status_code=417, headers=headers, content=content)
    for metric in metrics:
        if not isinstance(metric, str):
            logging.info("Taking data: metric is not a string")
            content = {"message": "one of metrics is not a string"}
            return JSONResponse(status_code=417, headers=headers, content=content)
        if metric in all_metrics and metric not in cur_metrics:
            cur_metrics.append(metric)

    if not isinstance(settings, list):
        logging.info("Taking data: settings is not a list")
        content = {"message": "settings is not a list"}
        return JSONResponse(status_code=417, headers=headers, content=content)
    if len(settings) > len(all_settings):
        logging.info("Taking data: settings is too long")
        content = {"message": "settings is too long"}
        return JSONResponse(status_code=417, headers=headers, content=content)
    cur_settings = []
    for setting in settings:
        if not isinstance(setting, str):
            logging.info("Taking data: setting is not a string")
            content = {"message": "one of settings is not a string"}
            return JSONResponse(status_code=417, headers=headers, content=content)
        if setting in all_settings and setting not in cur_settings:
            cur_settings.append(setting)

    if not isinstance(timestamp1, dict) or not isinstance(timestamp2, dict):
        logging.info("Taking data: one of timestamps is not dict")
        content = {"message": "one of timestamps is not dict"}
        return JSONResponse(status_code=417, headers=headers, content=content)
    if len(timestamp1) > 5 or len(timestamp2) > 5:
        logging.info("Taking data: one of timestamps is too long")
        content = {"message": "one of timestamps is too long"}
        return JSONResponse(status_code=417, headers=headers, content=content)
    if ("day" not in timestamp1 or not isinstance(timestamp1["day"], int) or "day" not in timestamp2 or not isinstance(timestamp2["day"], int)
        or "month" not in timestamp1 or not isinstance(timestamp1["month"], int) or "month" not in timestamp2 or not isinstance(timestamp2["month"], int)
        or "year" not in timestamp1 or not isinstance(timestamp1["year"], int) or "year" not in timestamp2 or not isinstance(timestamp2["year"], int)
        or "hour" not in timestamp1 or not isinstance(timestamp1["hour"], int) or "hour" not in timestamp2 or not isinstance(timestamp2["hour"], int)
            or "minute" not in timestamp1 or not isinstance(timestamp1["minute"], int) or "minute" not in timestamp2 or not isinstance(timestamp2["minute"], int)):
        logging.info("Taking data: one of timestamps is not of right type")
        content = {"message": "one of timestamps is not of right type"}
        return JSONResponse(status_code=417, headers=headers, content=content)
    try:
        min_datetime = datetime.datetime(year=timestamp1["year"], month=timestamp1["month"], day=timestamp1["day"], hour=timestamp1["hour"], minute=timestamp1["minute"])
        max_datetime = datetime.datetime(year=timestamp2["year"], month=timestamp2["month"], day=timestamp2["day"], hour=timestamp2["hour"], minute=timestamp2["minute"])
    except Exception as e:
        logging.info("Taking data: couldn't make timestamps: {}".format(e))
        content = {"message": "Taking data: couldn't make timestamps"}
        return JSONResponse(status_code=417, headers=headers, content=content)
    if max_datetime < min_datetime:
        logging.info("Taking data: timestamps reversed")
        content = {"message": "Taking data: timestamps reversed"}
        return JSONResponse(status_code=417, headers=headers, content=content)
    # print(data, uploadedData)

    print("Пришли данные:", regions, metrics, settings, timestamp1, timestamp2)

    if uploadedData and file_setting in settings:
        try:
            filebytes = await uploadedData.read()
        except Exception as e:
            logging.info("Trouble with file: {}".format(e))
            content = {"failed": "Trouble with data"}
            return JSONResponse(status_code=417, headers=headers, content=content)

    else:
        filebytes = 0
    try:
        content = process_data(settings, metrics, conn, regions, all_regions, types, min_datetime, max_datetime, filebytes)    
    except Exception as e:
        logging.info("Trouble wow: {}".format(e))
        content = {"message": "imaculous mistake"}
        JSONResponse(status_code=417, headers=headers, content=content)

    logging.info(content)
    return JSONResponse(status_code=200, headers=headers, content=content)



