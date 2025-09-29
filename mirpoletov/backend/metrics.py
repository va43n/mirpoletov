# Файл с функциями подсчета метрик
import logging
import datetime
import time
import os

from parser import ParsedData


def number_of_flights(all_data: list):
    if not isinstance(all_data, list):
        logging.info("Metrics: number of flights got not list")
        return -1
    return len(all_data)

def mean_duration_of_flights(all_data: list):
    if not isinstance(all_data, list):
        logging.info("Metrics: mean duration of flights got not list")
        return -1
    start = time.time()
    dur_sum = 0
    for data in all_data:
        if not isinstance(data, ParsedData):
            logging.info("Metrics: mean duration of flights got not ParsedData")
            return -1
        dur_sum += data.flight_time_min
    logging.info("Metrics: mean duration of flights: done in {} sec.".format(time.time() - start))
    return dur_sum / len(all_data)

def empty_days(all_data: list, datetime_min, datetime_max):
    if not isinstance(all_data, list) or not isinstance(datetime_min, datetime.datetime) or not isinstance(datetime_max, datetime.datetime):
        logging.info("Metrics: empty_days got wrong type of data")
        return -1
    start = time.time()
    date_min = datetime_min.date()
    date_max = datetime_max.date()
    all_days = (date_max - date_min).days
    set_date = set()
    for data in all_data:
        if not isinstance(data, ParsedData):
            logging.info("Metrics: empty days got not ParsedData")
            return -1
        if date_min < data.datetimed.date() < date_max:
            set_date.add(data.datetimed.date())

    logging.info("Metrics: empty days: done in {} sec.".format(time.time() - start))
    return all_days - len(set_date)

def peak_flights_an_hour(all_data: list, max_datetime):
    if not isinstance(all_data, list) or not isinstance(max_datetime, datetime.datetime) or len(all_data) == 0:
        logging.info("Metrics: peak flights an hour got wrong type of data")
        return -1
    start = time.time()
    min_datetime = all_data[0].datetimed
    for data in all_data:
        if not isinstance(data, ParsedData):
            logging.info("Metrics: peak flights an hour got not ParsedData")
        if  data.datetimed < min_datetime:
            min_datetime = data.datetimed

    min_hour_datetime = datetime.datetime(year=min_datetime.year, month=min_datetime.month, day=min_datetime.day, hour=min_datetime.hour)
    all_hours = {}
    for data in all_data:
        start_hour = (data.datetimed - min_hour_datetime).total_seconds() // 3600
        if data.datetimed + datetime.timedelta(hours=data.flight_time_min // 60, minutes = data.flight_time_min % 60) > max_datetime:
            end_hour = (max_datetime - min_hour_datetime + datetime.timedelta(data.flight_time_min)).total_seconds() // 3600 + 1
        else: 
            end_hour = (data.datetimed - min_hour_datetime + datetime.timedelta(data.flight_time_min)).total_seconds() // 3600 + 1
        if start_hour not in all_hours:
            all_hours[start_hour] = 0
        if end_hour not in all_hours:
            all_hours[end_hour] = 0
        all_hours[start_hour] += 1
        all_hours[end_hour] -= 1

    maxx = 0
    s = 0
    max_idxes = []

    sorted_times = sorted(all_hours)
    for idx, key in enumerate(sorted_times):
        s += all_hours[key]
        if maxx < s:
            maxx = s
            max_idxes = [idx]
        elif maxx == s:
            max_idxes.append(idx)   
    full_idxes = [[max_idxes[0], max_idxes[0]]]
    for i in range(1, len(max_idxes)):
        if max_idxes[i] == max_idxes[i - 1] + 1:
            full_idxes[-1][-1] += 1
        else:
            full_idxes.append([max_idxes[i], max_idxes[i]])
    peak_hours = [] 
    for peak_idxes in full_idxes:
        peak_hours.append([min_hour_datetime + datetime.timedelta(hours=sorted_times[peak_idxes[0]]), min_hour_datetime + datetime.timedelta(hours=sorted_times[peak_idxes[1] + 1])])
    logging.info("Metrics: peak flights an hour: done in {} sec.".format(time.time() - start))

    return peak_hours, maxx
    

if __name__ == "__main__":
    from parser import read_excel_calamine, parse_rows
    from preparing_data import compute_regions_types, find_duplicates, get_parsed_by_datetime_data
    from db_work import open_regions, open_types
    
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
    all_data = []
    dup, self_dup = find_duplicates(completed_data, [], all_data)
    logging.info("All data length: {}".format(len(all_data)))
    result_data = []
    today = datetime.datetime.today()
    longago = today - datetime.timedelta(days=180)
    wrong = get_parsed_by_datetime_data(all_data, result_data, datetime.datetime.today() - datetime.timedelta(days=180), datetime.datetime.today())
    logging.info("Metrics: number of flights: {}".format(number_of_flights(result_data)))
    logging.info("Metrics: mean duration of flights: {}".format(mean_duration_of_flights(result_data)))
    logging.info("Metrics: empty days: {}".format(empty_days(result_data, longago, today)))
    logging.info("Metrics: peak flights: {}".format(peak_flights_an_hour(result_data, today)))




