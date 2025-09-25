# Parser module for parsing given packets

import os
import sys
import time

import python_calamine


def read_excel_calamine(file: bytes):
    workbook = python_calamine.CalamineWorkbook.from_filelike(file)
    rows = workbook.get_sheet_by_index(0).to_python()
    headers = rows[0]
    return (headers, rows[1:])

def parse:wq


if __name__ == "__main__":
    filepath = "/2025.xlsx"
    fullpath = os.path.expanduser("~") + filepath
    print(os.path.exists(fullpath))
    try:
        r = open(fullpath, "rb")
    except Exception as e:
        print("Reading file: exception occured: ", {e})
        exit(1)

    try:
        start = time.time()
        headers, rows = read_excel_calamine(r)
        elapsed = time.time() - start
        print("Processing excel file: done")
        print(f"Excel headers:\n{headers}")
        first_show = 2
        print(f"Number of rows: {len(rows)}")
        print(f"Time on processing: {elapsed} sec.")
        print(f"Size of rows: {sys.getsizeof(rows)} bytes")
        print(f"Excel first {first_show} rows:\n{rows[:first_show]}")
    except Exception as e:
        print("Processing excel file: exception occured: ", {e})
    finally:
        r.close()



