import logging
from io import BytesIO

import psycopg as pg

from parser import read_excel_calamine, parse_rows
from db_work import insert_data_db, select_data_db
from metrics import (number_of_flights,
                     mean_duration_of_flights,
                     empty_days,
                     peak_flights_an_hour,
                     flights_per_hour,
                     mean_days_dynamic,
                     top_regions,
                     flights_per_month)
from preparing_data import (make_regions_dict,
                            make_db_data_into_data,
                            turn_regions_to_abbrs,
                            turn_abbrs_to_regions,
                            get_parsed_by_datetime_data,
                            find_duplicates,
                            find_minmax_datetime,
                            compute_regions_types,
                            translate_to_abbrs_dict)
from config_vars import (file_setting,
                         mean_setting,
                         upload_setting,
                         top_regs_string,
                         flights_string,
                         mean_duration_string,
                         rise_fall_string,
                         day_act_string,
                         peak_load_string,
                         mean_dynamic_string,
                         empty_days_string,
                         failed_string,
                         mean_string)

metrics_funcs = {flights_string: number_of_flights,
                 mean_duration_string: mean_duration_of_flights,
                 top_regs_string: top_regions,
                 peak_load_string: peak_flights_an_hour,
                 mean_dynamic_string: mean_days_dynamic,
                 rise_fall_string: flights_per_month,
                 day_act_string: flights_per_hour,
                 empty_days_string: empty_days}


def process_metric(metric_name, data, all_regions, min_datetime, max_datetime, regions_dict):
    if metric_name in metrics_funcs:
        if metric_name == flights_string:
            result = metrics_funcs[metric_name](data)
        elif metric_name == mean_duration_string:
            result = metrics_funcs[metric_name](data)
        elif metric_name == peak_load_string:
            result = metrics_funcs[metric_name](data, max_datetime)
        elif metric_name == mean_dynamic_string:
            result = metrics_funcs[metric_name](data, min_datetime, max_datetime)
        elif metric_name == rise_fall_string:
            result = []
            ret = metrics_funcs[metric_name](data, result, min_datetime, max_datetime)
            if ret != 0:
                result = -1
        elif metric_name == day_act_string:
            result = metrics_funcs[metric_name](data, min_datetime, max_datetime)
        elif metric_name == empty_days_string:
            result = metrics_funcs[metric_name](data, min_datetime, max_datetime)
        elif metric_name == top_regs_string:
            result = []
            ret = metrics_funcs[metric_name](regions_dict, result)
            if ret != 0:
                result = -1
        else:
            result = -1
            logging.info("Processing metrics: not realized metric: {}".format(metric_name))
    else:
        logging.info("Processing metrics: unsupported metric: {}".format(metric_name))
        result = -1
    return result

def process_metrics(all_data, settings, metrics, regions, all_regions, min_datetime, max_datetime):
    mean_regions = {mean_string: all_data}
    regions_dict = {}
    ret = make_regions_dict(all_data, regions, regions_dict)
    if ret == -1:
        logging.info("Processing metrics: couldn't make regions dict")
        return {failed_string: "Возникла ошбика при вычислении метрик"}
    ret = translate_to_abbrs_dict(regions_dict, all_regions)
    if ret != 0:
        logging.info("Processing metrics: couldn't translate regions to abbrs")
        return {failed_string: "Возникла ошибка при обработке выбранных регионов"}
    metrics_dict = {}
    for metric in metrics:
        if metric in metrics_funcs:
            metrics_dict[metric] = {}
    if top_regs_string in metrics:
        ret = process_metric(top_regs_string, 0, 0, 0, 0, regions_dict)
        if isinstance(ret, int) and ret == -1:
            logging.info("Processing metrics: something went wrong during processing {}".format(top_regs_string))
            return {failed_strig: "Возникла ошибка при вычислении выбранных метрик"}
        metrics_dict[top_regs_string] = ret
    if mean_setting in settings:
        cur_regions = mean_regions
    else:
        cur_regions = regions_dict
    for metric in metrics:
        if metric == top_regs_string:
            continue
        for region in cur_regions:
            ret = process_metric(metric, cur_regions[region], all_regions, min_datetime, max_datetime, 0)
            if isinstance(ret, int) and ret == -1:
                logging.info("Processing metrics: something went wrong during processing {} in {}".format(metric, region))
                return {failed_string: f"Возникла ошибка при вычислении выбранной метрики: {metric}"}
            metrics_dict[metric][region] = ret
    return metrics_dict

def process_data(settings, metrics, conninfo, regions, all_regions, types, min_datetime, max_datetime, filebytes):
    # Основная фугкция обработки
    print(1)
    try:
        if filebytes and file_setting in settings:
            try:
                bytes_real = BytesIO(filebytes)
                headers, rows = read_excel_calamine(bytes_real)
            except Exception as e:
                logging.info("Trouble with processing file, {}".format(e))
                return {failed_string: "Возникла ошибка при обработке переданного файла"}
            try:
                all_length = len(rows)
                parsed_data = parse_rows(rows)
                if isinstance(parsed_data, int) and parsed_data == -1:
                    logging.info("Trouble with parsing info")
                    return {failed_string: "Возникла ошибка при парсинге файла"}
            except Exception as e:
                logging.info("Trouble with parsing info, {}".format(e))
                return {failed_string: "Возникла непредвиденная ошибка при парсинге файла"}
            try: 
                parsed_length = len(parsed_data)
                completed_data = []
                wrong_completed = compute_regions_types(parsed_data, all_regions, types, completed_data)
                if isinstance(wrong_completed, int) and wrong_completed == -1:
                    logging.info("Trouble with computing types")
                    return {failed_string: "Возникла ошибка при обработке регионов"}
            except Exception as e:
                logging.info("Trouble with computing types, {}".format(e))
                return {failed_string: "Возникла непредвиденная ошибка при обработке регионов"}
            if upload_setting in settings:
                try:
                    conn = pg.connect(conninfo)
                    count_inserted = insert_data_db(completed_data, conn)
                    if isinstance(count_inserted, int) and count_inserted == -1:
                        logging.info("Trouble with inserting into db")
                        return {failed_string: "Возникла ошибка при вставке данных в базу данных"}
                except Exception as e:
                    logging.info("Trouble with inserting into db: {}".format(e))
                    return {failed_string: "Возникла непредвиденная ошибка при вставке данных в базу данных"}
            try:
                all_data = []
                duplicates, self_duplicates = find_duplicates(completed_data, [], all_data)
            except Exception as e:
                logging.info("Trouble with finding duplicated, {}".format(e))
                return {failed_string: "Возникла ошибка при поиске дубликатов в переданных данных"}
            try:
                datetimes = find_minmax_datetime(all_data)
                if isinstance(datetimes, int):
                    logging.info("Trouble with finding min and max datetimes")
                    return {failed_string: "Возникла ошибка при обработке даты"}
                datetime_min = datetimes[0]
                datetime_max = datetimes[1]
            except Exception as e:
                logging.info("Trouble with finding min and max datetimes: {}".format(e))
                return {failed_string: "Возникла непредвиденная ошибка при обработке даты"}
            # Это для отсеивания даты - если все данные из файла делать не нужно
            """
            try:
                result_data = []
                not_in_date = get_parsed_by_datetime_data(all_data, result_data, min_datetime, max_datetime)
                if isinstance(not_in_date, int) and not_in_date == -1:
                    logging.info("Trouble with parsing by date")
                    return {failed_string: "Возникла ошибка при определении данных, входящих в указанный временной промежуток"}
            except Exception as e:
                logging.info("Trouble with parsing by date: {}".format(e))
                return {failed_string: "Возникла непредвиденная ошибка при определении данных, входящих в указанный временной промежуток"}
            """
            try:
                regions_ints = []
                wrong_regions = turn_abbrs_to_regions(regions, all_regions, regions_ints)
                if wrong_regions != 0:
                    logging.info("Trouble with making regions out of abbrs: {}".format(wrong_regions))
                    return {failed_string: "Возникла ошибка при обработке регионов полетов"}
            except Exception as e:
                logging.info("Trouble with making regions out of abbrs: {}".format(e))
                return {failed_string: "Возникла непредвиденная ошибка при обработке регионов полетов"}
            result_data = all_data

        elif file_setting in settings and not filebytes:
            return {failed_string: "Не был предоставлен файл для обработки"}
        else:
            try:
                regions_ints = []
                wrong_regions = turn_abbrs_to_regions(regions, all_regions, regions_ints)
                if wrong_regions != 0:
                    logging.info("Trouble with making regions out of abbrs: {}".format(wrong_regions))
                    return {failed_string: "Возникла ошибка при обработке переданных регионов"}
            except Exception as e:
                logging.info("Trouble with making regions out of abbrs: {}".format(e))
                return {failed_string: "Возникла непредвиденная ошибка при обработке переданных регионов"}
            try:
                # print(min_datetime, max_datetime, min_datetime < max_datetime)
                conn = pg.connect(conninfo)
                db_data = select_data_db(conn, min_datetime, max_datetime, regions_ints)
                if isinstance(db_data, int):
                    logging.info("Trouble with selecting from db")
                    return {failed_string: "Возникла ошибка при выборке данных из базы данных"}
            except Exception as e:
                logging.info("Trouble with selecting from db, {}".format(e))
                return {failed_string: "Возникла ошибка при выборке данных из базы данных"}
            try:
                result_data = []
                ret = make_db_data_into_data(result_data, db_data)
                if ret != 0:
                    logging.info("Trouble with making data from db data")
                    return {failed_string: "Возникла ошибка при предобработке данных из базы данных"}
            except Exception as e:
                logging.info("Trouble with making data from db data: {}".format(e))
                return {failed_string: "Возникла непредвиденная ошибка при предобработке данных из базы данных"}
        try:
            metrics = process_metrics(result_data, settings, metrics, regions_ints, all_regions, min_datetime, max_datetime)
            if failed_string in metrics:
                logging.info("Processing metrics: failed")
                return metrics
            return metrics
        except Exception as e:
            logging.info("Processing metrics: failed: {}".format(e))
            return {failed_string: "Возникла непредвиденная ошибка при обработке метрик"}
    except Exception as e:
        logging.info("Processing failed: {}".format(e))
        return {failed_string: "Возникла непредвиденная ошибка при обработке данных"}
