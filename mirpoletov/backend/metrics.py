# Файл с функциями подсчета метрик
import logging
import datetime
import time
import os
from collections import defaultdict

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
    if len(all_data) == 0:
        return 0
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
    if not isinstance(all_data, list) or not isinstance(datetime_min, datetime.datetime) or not isinstance(datetime_max, datetime.datetime) or not datetime_min <= datetime_max:
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

def process_hours_dict(all_data, hours, min_hour_datetime, max_datetime):
    for data in all_data:
        start_hour = (data.datetimed - min_hour_datetime).total_seconds() // 3600
        if data.datetimed + datetime.timedelta(hours=data.flight_time_min // 60, minutes = data.flight_time_min % 60) > max_datetime:
            end_hour = (max_datetime - min_hour_datetime).total_seconds() // 3600 + 1
        else: 
            end_hour = (data.datetimed - min_hour_datetime + datetime.timedelta(minutes=data.flight_time_min)).total_seconds() // 3600 + 1
        # if start_hour not in all_hours:
        #     all_hours[start_hour] = 0
        # if end_hour not in all_hours:
        #     all_hours[end_hour] = 0
        # logging.info("Metrics: peak flights: start hour: {}, end hour: {}, flight_time: {}".format(start_hour, end_hour, data.flight_time_min))
        hours[int(start_hour)] += 1
        hours[int(end_hour)] -= 1

def process_days_dict(all_data, days, min_day_datetime, max_datetime):
    for data in all_data:
        start_day = (data.datetimed - min_day_datetime).days
        if data.datetimed + datetime.timedelta(minutes=data.flight_time_min) > max_datetime:
            end_day = (max_datetime - min_day_datetime).days + 1
        else:
            end_day = (data.datetimed - min_day_datetime + datetime.timedelta(minutes=data.flight_time_min)).days + 1
        days[start_day] += 1
        days[end_day] += 1

def peak_flights_an_hour(all_data: list, max_datetime):
    if not isinstance(all_data, list) or not isinstance(max_datetime, datetime.datetime) or len(all_data) == 0:
        logging.info("Metrics: peak flights an hour got wrong type of data")
        return -1
    start = time.time()
    min_datetime = all_data[0].datetimed
    for data in all_data:
        if not isinstance(data, ParsedData):
            logging.info("Metrics: peak flights an hour got not ParsedData")
            return -1
        if  data.datetimed < min_datetime:
            min_datetime = data.datetimed

    min_hour_datetime = datetime.datetime(year=min_datetime.year, month=min_datetime.month, day=min_datetime.day, hour=min_datetime.hour)
    all_hours = defaultdict(int)
    process_hours_dict(all_data, all_hours, min_hour_datetime, max_datetime)

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

def flights_per_hour(all_data: list, min_datetime, max_datetime):
    if not isinstance(all_data, list) or not isinstance(max_datetime, datetime.datetime) or not isinstance(min_datetime, datetime.datetime) or not min_datetime <= max_datetime or len(all_data) == 0:
        logging.info("Metrics: flights per hour got wrong type of data")
        return -1
    start = time.time()
    for data in all_data:
        if not isinstance(data, ParsedData):
            logging.info("Metrics: flights per hour got not ParsedData")
            return -1

    min_hour_datetime = datetime.datetime(year=min_datetime.year, month=min_datetime.month, day=min_datetime.day, hour=min_datetime.hour)
    all_hours = {}
    end_hour = int((max_datetime - min_hour_datetime).total_seconds() // 3600 + 1)
    # print((max_datetime - min_hour_datetime + datetime.timedelta(minutes=data.flight_time_min)).total_seconds() // 3600) 
    # print(end_hour, type(end_hour))
    for hour in range(end_hour):
        all_hours[hour] = 0

    process_hours_dict(all_data, all_hours, min_hour_datetime, max_datetime)

    s = 0
    flights = []

    sorted_times = sorted(all_hours)
    for idx, key in enumerate(sorted_times[:-1]):
        s += all_hours[key]
        flights.append(s)
    logging.info("Metrics: flights per hour: done in {}".format(time.time() - start))

    return flights

def mean_days_dynamic(all_data, min_datetime, max_datetime):
    if not isinstance(all_data, list) or not isinstance(max_datetime, datetime.datetime) or not isinstance(min_datetime, datetime.datetime) or not min_datetime <= max_datetime or len(all_data) == 0:
        logging.info("Metrics: mean days dynamic got wrong type of data")
        return -1
    start = time.time()
    for data in all_data:
        if not isinstance(data, ParsedData):
            logging.info("Metrics: mean days dynamic got not ParsedData")
            return -1

    min_day_datetime = datetime.datetime(year=min_datetime.year, month=min_datetime.month, day=min_datetime.day)
    all_days = {}
    end_day = (max_datetime - min_day_datetime).days + 1

    for day in range(end_day):
        all_days[day] = 0

    process_days_dict(all_data, all_days, min_day_datetime, max_datetime)
    
    days_flights = sorted(list(all_days.values()))
    if len(days_flights) == 0:
        logging.info("Metrics: mean days dynamic zero length array")
        return -1
    summ = 0
    for flights in days_flights:
        summ += flights

    if len(days_flights) % 2 == 0:
        mediann = (days_flights[len(days_flights)//2 - 1] + days_flights[len(days_flights) // 2]) / 2
    else:
        mediann = days_flights[len(days_flights) // 2]
    logging.info("Metrics: mean days dynamic: done in {} sec.".format(time.time() - start))

    return (summ / len(days_flights), mediann)

def top_regions(regions: dict, flights: list):
    if not isinstance(regions, dict) or not isinstance(flights, list):
        logging.info("Metrics: top_regions got wrong type of data")
        return -1

    for region in regions:
        if not isinstance(regions[region], list):
            logging.info("Metrics: top_regions got wrong type of data")
            return -1
        flights.append([region, number_of_flights(regions[region])])
    flights.sort(reverse=True, key=lambda x: x[1])
    return 0

def flights_per_month(all_data: list, monthly_flights: list, min_datetime, max_datetime):
    if not isinstance(all_data, list) or not isinstance(max_datetime, datetime.datetime) or not isinstance(min_datetime, datetime.datetime) or not min_datetime <= max_datetime or len(all_data) == 0 or not isinstance(monthly_flights, list):
        logging.info("Metrics: flights per month got wrong type of data")
        return -1
    start = time.time()
    min_month = min_datetime.year * 12 + min_datetime.month
    
    all_months = {}
    end_month = (max_datetime.year * 12 + max_datetime.month) - min_month + 1
    for month in range(end_month):
        all_months[month] = 0

    for data in all_data:
        if not isinstance(data, ParsedData):
            logging.info("Metrics: flights per month got not ParsedData")
            return -1
        all_months[data.datetimed.year * 12 + data.datetimed.month - min_month] += 1
    
    for key in sorted(all_months):
        monthly_flights.append(all_months[key])
    logging.info("Metrics: flights per month: done in {} sec.".format(time.time() - start))
    return 0
    

if __name__ == "__main__":
    from parser import read_excel_calamine, parse_rows
    from preparing_data import compute_regions_types, find_duplicates, get_parsed_by_datetime_data, make_regions_dict, turn_regions_to_abbrs
    from db_work import open_regions, open_types
    
    logging.basicConfig(level=logging.INFO)
    regions = open_regions()
    print(regions)
    types = open_types()
    print(types)
    start = time.time()
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
    flights_hour = flights_per_hour(result_data, longago, today)
    logging.info("Metrics: flights per hour len: {}".format(len(flights_hour)))
    logging.info("Metrics: mean days dynamic: {}".format(mean_days_dynamic(result_data, longago, today)))
    monthly_flights = []
    ret = flights_per_month(result_data, monthly_flights, longago, today)
    logging.info("Metrics: flights per month: {}, ret: {}".format(monthly_flights, ret))
    regions_list = [1, 2, 3, 54, 55, 0]
    regions_dict = {}
    ret = make_regions_dict(result_data, regions_list, regions_dict)
    logging.info("Metrics: making regions dict: ret: {}".format(ret))
    flights_top = []
    ret = top_regions(regions_dict, flights_top)
    logging.info("Metrics: top regions: regions: {}, ret: {}".format(flights_top, ret))
    ret = turn_regions_to_abbrs(regions, flights_top)
    logging.info("Turning regions into abbrs: regions: {}, ret: {}".format(flights_top, ret))
    
    logging.info("All time: {} sec.".format(time.time() - start))


