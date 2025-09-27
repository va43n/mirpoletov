# Parser module for parsing given packets

import os
import sys
import time
import re
import logging

import python_calamine


shr_start = "(SHR"
dep2025_start = "-TITLE IDEP"
arr2025_start = "-TITLE IARR"
coords_pattern = r"\d{4,6}[СЮNS]\d{5,7}[ЗВWE]"
date_pattern = r"\d{6}"
b_type_pattern = r"(\d)*(BLA|AER|SHAR)"
sid_pattern = r"\d{8,}"
time_pattern = r"\d{4}"
re_coords = re.compile(coords_pattern)
re_date = re.compile(date_pattern)
re_b_type = re.compile(b_type_pattern)
re_sid = re.compile(sid_pattern)
re_time = re.compile(time_pattern)


class ParsedData:
    def __init__(self):
        self.langd = -1000
        self.latd = -1000
        self.langa = -1000
        self.lata = -1000
        self.datetimed = -1000
        self.flight_time = -1000
        self.sid = -1000
        self.b_type = -1000

    def __repr__(self):
        return f"ParsedData object: sid: {self.sid}, b_type: {self.b_type}, datetime: {self.datetimed}, flight_time: {self.flight_time}, langd: {self.langd}, latd: {self.latd}, langa: {self.langa}, lata: {self.lata}"


class ShrInfo:
    def __init__(self):
        self.timed = ""
        self.coordd = ""
        self.flight_time = ""
        self.coorda = ""
        self.b_type = ""
        self.sid = ""
        self.date = ""

    def __repr__(self):
        return f"ShrInfo object: timed: {self.timed}, coordd: {self.coordd}, flight_time: {self.flight_time}, coorda: {self.coorda}, b_type: {self.b_type}, date: {self.date}, sid: {self.sid}"


class DepInfo:
    def __init__(self):
        self.date = ""
        self.coord = ""
        self.time = ""
        self.sid = ""

    def __repr__(self):
        return f"DepInfo object: date: {self.date}, coord: {self.coord}, time: {self.time}, sid: {self.sid}"


class ArrInfo:
    def __init__(self):
        self.date = ""
        self.coord = ""
        self.time = ""
        self.sid = ""
    
    def __repr__(self):
        return f"ArrInfo object: date: {self.date}, coord: {self.coord}, time: {self.time}, sid: {self.sid}"

class ParserInfo:
    def __init__(self):
        self.shr = ShrInfo()
        self.dep = DepInfo()
        self.arr = ArrInfo()

    def __repr__(self):
        return f"ParserInfo object: \n{repr(self.shr)}\n{repr(self.dep)}\n{repr(self.arr)}"


def read_excel_calamine(file: bytes):
    """Чтение потока байтов, обработка их как excel файла. 
    Ны выходе кортеж - (заголовки, список рядов)"""
    workbook = python_calamine.CalamineWorkbook.from_filelike(file)
    rows = workbook.get_sheet_by_index(0).to_python()
    headers = rows[0]
    return (headers, rows[1:])


def find_coords(mes: str, coords_str: str, start_search: int = 0, stop_search: int = -1):
    if stop_search == -1:
        stop_search = len(mes)
    coords_start = mes.find(coord_str, start_search, stop_search)
    if coords_start == -1:
        logging.debug("Parsing shr: no shr start")
        return 0
    
    coords_end = mes.find("E", coords_start, stop_search)
    if coords_end == -1 or not (coords_end == coords_start + 14 or coords_end == coords_start + 15):
        coordd_end = mes.find("W", coordd_start, rmk_start)
        if coords_end == -1 or not (coords_end == coords_start + 14 or coords_end == coords_start + 15):
            logging.debug("Parsing shr: invalid {}".format(coords_str))
            return 0
    return mes[coords_end - 10:coords_end + 1]

def find_info_re(mes: str, pattern, coords_str: str, start_search: int = 0, stop_search: int = -1, start_pattern_pos: int = 0,
                 stop_pattern_pos: int = -1):
    if stop_search == -1:
        stop_search = len(mes)
    coords_start = mes.find(coords_str, start_search, stop_search)
    if coords_start == -1:
        logging.debug("Parsing shr: no {}".format(coords_str))
        return 0
    if stop_pattern_pos == -1:
        stop_pattern_pos = len(mes)
    else:
        stop_pattern_pos = coords_start + stop_pattern_pos
    # print(type(coords_start + start))
    return pattern.search(mes, coords_start + start_pattern_pos, stop_pattern_pos)


def parse_shr(mes: str, info: ParserInfo, pos_start: int = -1): 
    if pos_start == -1:
        pos_start = mes.find(shr_start)
        if pos_start == -1:
            logging.debug("Parsing shr: no start")
            return -1

    depature_start = mes.find("-", pos_start + 6)
    if depature_start == -1:
        logging.debug("Parsing shr: didn't find depature")
        return -1
    if len(mes) < depature_start + 10:
        logging.debug("Parsing shr: too small")
        return -1
    # print(mes[depature_start + 1:depature_start + 9])

    if not mes[depature_start + 1:depature_start + 5].isalpha():
        logging.debug("Parsing shr: didn't find departure")
        return -1
    if mes[depature_start + 1:depature_start + 5] == "ZZZZ":
        airport_coordd = False
    else:
        airport_coordd = True
    if not mes[depature_start + 5:depature_start + 9].isdecimal():
        logging.debug("Parsing shr: timed is not decimal")
        return -1
    info.shr.timed = mes[depature_start + 5:depature_start + 9]

    arrival_start = mes.find("-", depature_start + 12)
    if arrival_start == -1:
        logging.debug("Parsing shr: didn't find arrival")
        return -1
    if len(mes) < arrival_start + 8:
        logging.debug("Parsing shr: too small")
        return -1
    if not mes[arrival_start + 1:arrival_start + 5].isalpha():
        logging.debug("Parsing shr: no arrival")
        return -1
    if mes[arrival_start + 1:arrival_start + 5] == "ZZZZ":
        airport_coorda = False
    else:
        airport_coorda = True

    # print(mes[arrival_start:arrival_start + 9]) 
    if not mes[arrival_start + 5:arrival_start + 9].isdecimal():
        # print(mes[arrival_start + 5:arrival_start + 9]) 
        logging.debug("Parsing shr: filght_time is not decimal")
        return -1
    info.shr.flight_time = mes[arrival_start + 5:arrival_start + 9]

    rmk_start = mes.find("RMK/", arrival_start + 9)

    if rmk_start == -1:
        rmk = False
        rmk_start = len(mes)
    else:
        rmk = True
    add_info_start = mes.find("-", arrival_start + 9, rmk_start)
    if add_info_start == -1:
        logging.debug("Parsing shr: no additional info")
        return -1

    dep_coords_rmk = ""
    if not airport_coordd:
        dep_coords = find_info_re(mes, re_coords, "DEP/", add_info_start, rmk_start, 4, 22)
        if dep_coords: info.shr.coordd = dep_coords.group()
    elif rmk:
        dep_coords_rmk = find_info_re(mes, re_coords,  "RMK/", rmk_start, -1, 4, -1)
        if dep_coords_rmk: info.shr.coordd = dep_coords_rmk.group()
    
    if not airport_coorda:
        arr_coords = find_info_re(mes, re_coords, "DEST/", add_info_start, rmk_start, 4, 22)
        if arr_coords: info.shr.coorda = arr_coords.group()
    elif rmk:
        if dep_coords_rmk: info.shr.coorda = dep_coords_rmk.group()
        else:
            dep_coords_rmk = find_info_re(mes, re_coords, "RMK/", rmk_start, -1, 4, -1)
            if dep_coords_rmk: info.shr.coordd = dep_coords_rmk.group()

    date = find_info_re(mes, re_date, "DOF/", add_info_start, rmk_start, 4, 11)
    if date:
        info.shr.date = date.group()
    
    b_type = find_info_re(mes, re_b_type, "TYP/", add_info_start, rmk_start, 4, 14)
    if not b_type or isinstance(b_type, int):
        logging.debug("Parsing shr: invalid TYP/")
        return -1
    info.shr.b_type = b_type.group(2)

    sid = find_info_re(mes, re_sid, "SID/", add_info_start, -1, 4, -1)
    if sid:
        info.shr.sid = sid.group()
    return 0    

def parse_dep(mes: str, info: ParserInfo, pos_start: int):
    if pos_start == -1:
        pos_start = mes.find(dep2025_start)
    if pos_start == -1:
        logging.debug("Parsing dep: no dep start")
        return -1
    pos_start += len(dep2025_start)

    sid = find_info_re(mes, re_sid, "-SID", pos_start, -1, 4, -1)
    if sid:
        info.dep.sid = sid.group()

    time = find_info_re(mes, re_time, "-ATD", pos_start, -1, 4, -1)
    if time:
        info.dep.time = time.group()

    date = find_info_re(mes, re_date, "-ADD", pos_start, -1, 4, -1)
    if date:
        info.dep.date = date.group()

    coords = find_info_re(mes, re_coords, "-ADEPZ", pos_start, -1, 4, -1)
    if coords:
        info.dep.coord = coords.group()
    return 0

def parse_arr(mes: str, info: ParserInfo, pos_start: int):
    if pos_start == -1:
        pos_start = mes.find(arr2025_start)
    if pos_start == -1:
        logging.debug("Parsing arr: no arr start")
        return -1
    pos_start += len(arr2025_start)

    sid = find_info_re(mes, re_sid, "-SID", pos_start, -1, 4, -1)
    if sid:
        info.arr.sid = sid.group()

    time = find_info_re(mes, re_time, "-ATA", pos_start, -1, 4, -1)
    if time:
        info.arr.time = time.group()

    date = find_info_re(mes, re_date, "-ADA", pos_start, -1, 4, -1)
    if date:
        info.arr.date = date.group()

    coords = find_info_re(mes, re_coords, "-ADARRZ", pos_start, -1, 4, -1)
    if coords:
        info.arr.coord = coords.group()
    return 0


def parse_row2025(row: list):
    """Парсит один ряд"""
    info = ParserInfo()
    found_shr = False
    found_dep = False
    found_arr = False
    logging.debug("Row: {}".format(row))
    for col in row:
        if not col: continue
        pos = col.find(shr_start)
        if pos != -1:
            logging.debug("Col shr: {}".format(col))
            ret = parse_shr(col, info, pos)
            continue
        pos = col.find(dep2025_start)
        if pos!= -1:
            logging.debug("Col dep: {}".format(col))
            ret = parse_dep(col, info, pos)
            continue
        pos = col.find(arr2025_start)
        if pos != -1:
            logging.debug("Col arr: {}".format(col))
            ret = parse_arr(col, info, pos)
    logging.debug(info)
    
def draw_info(info: ParserInfo, data: ParsedData):
    if info.shr.sid:
        data.sid = int(info.shr.sid)
    elif info.dep.sid:
        data.sid = int(info.dep.sid)
    elif info.arr.sid:
        data.sid = int(info.dep.sid)
    else:
        logging.debug("No sid")
        return -1

    
        

def parse_rows(rows: list[list[str]]):
    start = time.time()
    # print(rows)
    # print(len(rows))
    for row in rows:
        parse_row2025(row)
    finish = time.time()
    logging.info("Parsing rows: {} sec. Average per row: {} sec.".format(finish - start, (finish - start)/len(rows)))

                 
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    row_number = None
    start_row = None
    end_row = None
    # print(len(sys.argv))
    if len(sys.argv) == 2:
        try:
            row_number = int(sys.argv[1])
        except Exception: print("input error 2")
    elif len(sys.argv) == 3:
        try:
            start_row = int(sys.argv[1])
            end_row = int(sys.argv[2])
        except Exception: print("input error 3")
    filepath = "/2025.xlsx"
    fullpath = os.path.expanduser("~") + filepath
    # print(os.path.exists(fullpath))
    try:
        r = open(fullpath, "rb")
    except Exception as e:
        print("Reading file: exception occured: ", {e})
        exit(1)

    try:
        start = time.time()
        headers, rows = read_excel_calamine(r)
        elapsed = time.time() - start
        logging.info("Processing excel file: done")
        logging.info("Excel headers:\n{}".format(headers))
        # first_show = 2
        logging.info("Number of rows: {}".format(len(rows)))
        logging.info("Time on processing: {} sec.".format(elapsed))
        logging.info("Size of rows: {} bytes".format(sys.getsizeof(rows)))
        # print(f"Excel first {first_show} rows:\n{rows[:first_show]}")
    except Exception as e:
        print("Processing excel file: exception occured: ", e)
    finally:
        r.close()
    if len(sys.argv) == 2:
        parse_rows(rows[row_number - 2:row_number - 1])
    elif len(sys.argv) == 3:
        parse_rows(rows[start_row - 2:end_row - 1])
    else:
        parse_rows([rows[0]])




