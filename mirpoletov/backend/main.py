# Файл запуска
from typing import Optional
import json
import logging
# from io import BytesIO
import multiprocessing as mp
import datetime

from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, Form, UploadFile, File
from fastapi.responses import JSONResponse
import psycopg as pg

from parser import read_excel_calamine
from db_work import open_regions, open_types
from process import process_data
from config_vars import (file_setting,
                         upload_setting,
                         mean_setting,
                         json_setting,
                         graphs_setting,
                         flights_string,
                         mean_duration_string,
                         peak_load_string,
                         mean_dynamic_string,
                         rise_fall_string,
                         day_act_string,
                         empty_days_string,
                         top_regs_string,
                         failed_string)
from config_vars_safe import (_dbname,
                              _user,
                              _host,
                              _port,
                              pass_info) 


logging.basicConfig(level=logging.INFO)
all_settings = [file_setting, mean_setting, graphs_setting, json_setting, upload_setting]
# Можео добавить flight density
all_metrics = [flights_string, mean_duration_string, top_regs_string, peak_load_string, mean_dynamic_string, day_act_string, empty_days_string]
all_regions = open_regions()
types = open_types()
regions_len = len(all_regions)

file = open(pass_info)
stuff = file.read().strip("\n\r ")
conninfo = f"dbname={_dbname} user={_user} password={stuff} host={_host} port={_port}"
del stuff
del _dbname
del _user
del _host
del _port

# conn = pg.connect(conninfo)
processes_pool = mp.Pool(8)

message_string = "message"
unexpected_error_string = "Возникла непредвиденная ошибка"

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
    global processes_pool
    if processes_pool:
        processes_pool.terminate()
        logging.info("Process pool terminated") 

@app.post("/api/calculate")
def calculate_client_input(
        data: str = Form(...),
        uploadedData: Optional[UploadFile] = File(None)
    ):
    # logging.basicConfig(level=logging.INFO)
    try:
        global processes_pool
        request_data = json.loads(data)
        
        regions = request_data.get('regions', [])
        metrics = request_data.get('metrics', [])
        settings = request_data.get('settings', [])
        timestamp1 = request_data.get('timestamp1', {})
        timestamp2 = request_data.get('timestamp2', {})

        headers = {"Content-Language": "ru-RU"}

        if not isinstance(regions, list):
            logging.info("Taking data: regions is not a list: {}".format(type(regions)))
            content = {message_string: "Регионы переданы в неправильном виде"}
            return JSONResponse(status_code=417, headers=headers, content=content)
        if len(regions) > regions_len:
            logging.info("Taking data: regions is too long: {}".format(len(regions)))
            content = {message_string: "Регионов слишком много"}
            return JSONResponse(status_code=417, headers=headers, content=content)
        for region in regions:
            if not isinstance(region, str):
                logging.info("Taking data: one of regions is not a string: {}".format(region))
                content = {message_string: "Один из регионов не является строкой"}
                return JSONResponse(status_code=417, headers=headers, content=content)
        
        if not isinstance(metrics, list):
            logging.info("Taking data: metrics is not list: {}".format(type(metrics)))
            content = {message_string: "Метрики переданы в неправильном виде"}
            return JSONResponse(status_code=417, headers=headers, content=content)
        cur_metrics = []
        if len(metrics) > len(all_metrics):
            logging.info("Taking data: metrics is too long: {}".format(len(metrics)))
            content = {message_string: "Метрик слишком много"}
            return JSONResponse(status_code=417, headers=headers, content=content)
        for metric in metrics:
            if not isinstance(metric, str):
                logging.info("Taking data: metric is not a string: {}".format(metric))
                content = {message_string: "Одна из метрик не является строкой"}
                return JSONResponse(status_code=417, headers=headers, content=content)
            if metric in all_metrics and metric not in cur_metrics:
                cur_metrics.append(metric)

        if not isinstance(settings, list):
            logging.info("Taking data: settings is not a list: {}".format(type(settings)))
            content = {message_string: "Настройки переданы в неправильном виде"}
            return JSONResponse(status_code=417, headers=headers, content=content)
        if len(settings) > len(all_settings):
            logging.info("Taking data: settings is too long: {}".format(len(setting)))
            content = {message_string: "Слишком много настроек"}
            return JSONResponse(status_code=417, headers=headers, content=content)
        cur_settings = []
        for setting in settings:
            if not isinstance(setting, str):
                logging.info("Taking data: setting is not a string: {}".format(setting))
                content = {message_string: "Одна из настроек не является строкой"}
                return JSONResponse(status_code=417, headers=headers, content=content)
            if setting in all_settings and setting not in cur_settings:
                cur_settings.append(setting)

        if not isinstance(timestamp1, dict) or not isinstance(timestamp2, dict):
            logging.info("Taking data: one of timestamps is not dict")
            content = {message_string: "Одна из временных меток передана в неправильном формате"}
            return JSONResponse(status_code=417, headers=headers, content=content)
        if len(timestamp1) > 5 or len(timestamp2) > 5:
            logging.info("Taking data: one of timestamps is too long")
            content = {message_string: "Одна из временных меток передана в неверном виде"}
            return JSONResponse(status_code=417, headers=headers, content=content)
        if ("day" not in timestamp1 or not isinstance(timestamp1["day"], int) or "day" not in timestamp2 or not isinstance(timestamp2["day"], int)
            or "month" not in timestamp1 or not isinstance(timestamp1["month"], int) or "month" not in timestamp2 or not isinstance(timestamp2["month"], int)
            or "year" not in timestamp1 or not isinstance(timestamp1["year"], int) or "year" not in timestamp2 or not isinstance(timestamp2["year"], int)
            or "hour" not in timestamp1 or not isinstance(timestamp1["hour"], int) or "hour" not in timestamp2 or not isinstance(timestamp2["hour"], int)
                or "minute" not in timestamp1 or not isinstance(timestamp1["minute"], int) or "minute" not in timestamp2 or not isinstance(timestamp2["minute"], int)):
            logging.info("Taking data: one of timestamps is not of right type")
            content = {message_string: "Часть одной из временных метрик передана в неверном формате или не передана"}
            return JSONResponse(status_code=417, headers=headers, content=content)
        try:
            min_datetime = datetime.datetime(year=timestamp1["year"], month=timestamp1["month"], day=timestamp1["day"], hour=timestamp1["hour"], minute=timestamp1["minute"])
            max_datetime = datetime.datetime(year=timestamp2["year"], month=timestamp2["month"], day=timestamp2["day"], hour=timestamp2["hour"], minute=timestamp2["minute"])
        except Exception as e:
            logging.info("Taking data: couldn't make timestamps: {}".format(e))
            content = {message_string: "Возникла ошибка при обработке временных метрик"}
            return JSONResponse(status_code=417, headers=headers, content=content)
        if max_datetime < min_datetime:
            logging.info("Taking data: timestamps reversed")
            content = {message_string: "Раняя из переданных временных метрик боьлше поздней"}
            return JSONResponse(status_code=417, headers=headers, content=content)
        # print(data, uploadedData)

        logging.debug("Пришли данные: {}\n{}\n{}\n{}, {}".format(regions, metrics, settings, timestamp1, timestamp2))
        
        if uploadedData and file_setting in settings:
            try:
                #filebytes = uploadedData.file.read()
                filebytes = uploadedData.file.read()
            except Exception as e:
                logging.info("Trouble with file: {}".format(e))
                content = {failed_string: "Возникла ошибка при чтении переданного файла"}
                return JSONResponse(status_code=417, headers=headers, content=content)
        else:
            filebytes = 0
        
        try:
            content = processes_pool.apply(process_data, (settings, metrics, conninfo, regions, all_regions, types, min_datetime, max_datetime, filebytes))
        except Exception as e:
            logging.info("Trouble wow: {}".format(e))
            logging.info(e.args)
            logging.info(e.__traceback__)
            content = {failed_string: "Возникла ошибка при обработке данных"}
            return JSONResponse(status_code=417, headers=headers, content=content)

        if not isinstance(content, dict) or failed_string in content:
            logging.info("Mistake occured: {}".format(content))
            return JSONResponse(status_code=417, headers=headers, content=content)
        logging.debug(content)

        return JSONResponse(status_code=200, headers=headers, content=content)
    except Exception as e:
        return JSONResponse(status_code=400, content=unexpected_error_string)



