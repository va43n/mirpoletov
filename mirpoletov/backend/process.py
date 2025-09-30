import logging
from io import BytesIO

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

file_setting = "file"
upload_setting = "upload"
mean_setting = "mean"
top_regions_string = "top_regs"

metrics_funcs = {"flights": number_of_flights,
                 "mean_duration": mean_duration_of_flights,
                 "top_regs": top_regions,
                 "peak_load": peak_flights_an_hour,
                 "mean_dynamic": mean_days_dynamic,
                 "rise_fall": flights_per_month,
                 "day_act": flights_per_hour,
                 "empty_days": empty_days}


def process_metric(metric_name, data, all_regions, min_datetime, max_datetime, regions_dict):
    if metric_name in metrics_funcs:
        if metric_name == "flights":
            result = metrics_funcs[metric_name](data)
        elif metric_name == "mean_duration":
            result = metrics_funcs[metric_name](data)
        elif metric_name == "peak_load":
            result = metrics_funcs[metric_name](data, max_datetime)
        elif metric_name == "mean_dynamic":
            result = metrics_funcs[metric_name](data, min_datetime, max_datetime)
        elif metric_name == "rise_fall":
            result = []
            ret = metrics_funcs[metric_name](data, result, min_datetime, max_datetime)
            if ret != 0:
                result = -1
        elif metric_name == "day_act":
            result = metrics_funcs[metric_name](data, min_datetime, max_datetime)
        elif metric_name == "empty_days":
            result = metrics_funcs[metric_name](data, min_datetime, max_datetime)
        elif metric_name == "top_regs":
            result = []
            ret = metrics_funcs[metric_name](regions_dict, result)
            if ret != 0:
                result = -1
        else:
            result = -1
            logging.info("Not very clever")
    else:
        logging.info("very unclever")
        result = -1
    return result

def process_metrics(all_data, settings, metrics, regions, all_regions, min_datetime, max_datetime):
    mean_regions = {"mean": all_data}
    regions_dict = {}
    ret = make_regions_dict(all_data, regions, regions_dict)
    if ret == -1:
        logging.info("make regs1")
        return {"failed": "make regs1"}
    ret = translate_to_abbrs_dict(regions_dict, all_regions)
    if ret != 0:
        logging.info("make regs2")
        return {"failed": "make regs2"}
    metrics_dict = {}
    for metric in metrics:
        if metric in metrics_funcs:
            metrics_dict[metric] = {}
    if top_regions_string in metrics:
        ret = process_metric(top_regions_string, 0, 0, 0, 0, regions_dict)
        if isinstance(ret, int) and ret == -1:
            logging.info("Something went wrong during processing {}".format(top_regions_string))
            return {"failed": "metrics"}
        metrics_dict[top_regions_string]["mean"] = ret
    if mean_setting in settings:
        cur_regions = mean_regions
    else:
        cur_regions = regions_dict
    for metric in metrics:
        if metric == top_regions_string:
            continue
        for region in cur_regions:
            ret = process_metric(metric, cur_regions[region], all_regions, min_datetime, max_datetime, 0)
            if isinstance(ret, int) and ret == -1:
                logging.info("Something went wrong during processing {} in {}".format(metric, region))
                return {"failed": "metrics"}
            metrics_dict[metric][region] = ret
    return metrics_dict

def process_data(settings, metrics, conn, regions, all_regions, types, min_datetime, max_datetime, filebytes):
    # Основная фугкция обработки
    
    if filebytes and file_setting in settings:
        try:
            bytes_real = BytesIO(filebytes)
            headers, rows = read_excel_calamine(bytes_real)
        except Exception as e:
            logging.info("Trouble with processing file, {}".format(e))
            return {"failed": "Troubles with file"}
        try:
            all_length = len(rows)
            parsed_data = parse_rows(rows)
            if isinstance(parsed_data, int) and parsed_data == -1:
                logging.info("Trouble with parsing info")
                return {"failed": "Troubles with parsing"}
        except Exception as e:
            logging.info("Trouble with parsing info, {}".format(e))
            return {"failed": "Troubles with parsing"}
        try: 
            parsed_length = len(parsed_data)
            completed_data = []
            wrong_completed = compute_regions_types(parsed_data, all_regions, types, completed_data)
            if isinstance(wrong_completed, int) and wrong_completed == -1:
                logging.info("Trouble with computing types")
                return {"failed": "trouble with computing types"}
        except Exception as e:
            logging.info("Trouble with computing types, {}".format(e))
            return {"failed": "trouble with computing types"}
        if upload_setting in settings:
            try:
                count_inserted = insert_data_db(completed_data, conn)
                if isinstance(count_inserted, int) and count_inserted == -1:
                    logging.info("Trouble with inserting into db")
                    return {"failed": "Trouble with inserting into db"}
            except Exception as e:
                logging.info("Trouble with inserting into db: {}".format(e))
                return {"failed": "Trouble with inserting into db"}
        try:
            all_data = []
            duplicates, self_duplicates = find_duplicates(completed_data, [], all_data)
        except Exception as e:
            logging.info("Trouble with finding duplicated, {}".format(e))
            return {"failed": "Trouble with finding duplicates"}
        try:
            datetimes = find_minmax_datetime(all_data)
            if isinstance(datetimes, int):
                logging.info("Trouble with finding min and max datetimes")
                return {"failed": "Trouble with finding min and max datetimes"}
            datetime_min = datetimes[0]
            datetime_max = datetimes[1]
        except Exception as e:
            logging.info("Trouble with finding min and max datetimes: {}".format(e))
            return {"failed": "Trouble with finding min and max datetimes"}
        # Это для отсеивания даты - если все данные из файла делать не нужно
        """
        try:
            result_data = []
            not_in_date = get_parsed_by_datetime_data(all_data, result_data, min_datetime, max_datetime)
            if isinstance(not_in_date, int) and not_in_date == -1:
                logging.info("Trouble with parsing by date")
                return {"failed": "Trouble with parsing by date"}
        except Exception as e:
            logging.info("Trouble with parsing by date: {}".format(e))
            return {"failed": "Trouble with parsing by date"}
        """
        try:
            regions_ints = []
            wrong_regions = turn_abbrs_to_regions(regions, all_regions, regions_ints)
            if wrong_regions != 0:
                logging.info("Trouble with making regions out of abbrs: {}".format(wrong_regions))
                return {"failed": "Trouble with making regions out of abbrs"}
        except Exception as e:
            logging.info("Trouble with making regions out of abbrs: {}".format(e))
            return {"failed": "Trouble with making regions out of abbrs"}
        result_data = all_data

    elif file_setting in settings and not filebytes:
        return {"failed": "No file for making data"}
    else:
        try:
            regions_ints = []
            wrong_regions = turn_abbrs_to_regions(regions, all_regions, regions_ints)
            if wrong_regions != 0:
                logging.info("Trouble with making regions out of abbrs: {}".format(wrong_regions))
                return {"failed": "Trouble with making regions out of abbrs"}
        except Exception as e:
            logging.info("Trouble with making regions out of abbrs: {}".format(e))
            return {"failed": "Trouble with making regions out of abbrs"}
        try:
            # print(min_datetime, max_datetime, min_datetime < max_datetime)
            db_data = select_data_db(conn, min_datetime, max_datetime, regions_ints)
            if isinstance(db_data, int):
                logging.info("Trouble with selecting from db")
                return {"failed": "Trouble with selecting from db"}
        except Exception as e:
            logging.info("Trouble with selecting from db, {}".format(e))
            return {"failed": "Trouble with selecting from db"}
        try:
            result_data = []
            ret = make_db_data_into_data(result_data, db_data)
            if ret != 0:
                logging.info("Trouble with making data from db data")
                return {"failed": "Trouble with making data from db data"}
        except Exception as e:
            logging.info("Trouble with making data from db data: {}".format(e))
            return {"failed": "Trouble with making data from db data"}
    try:
        metrics = process_metrics(result_data, settings, metrics, regions_ints, all_regions, min_datetime, max_datetime)
        if "failed" in metrics:
            logging.info("Failed")
            return metrics
        return metrics
    except Exception as e:
        logging.info("Mistake metrics: {}".format(e))
        return {"failed": "in metrics"}


