import logging

import psycopg


logging.basicConfig(level=logging.INFO)
file = open("../../../../stuff")
stuff = file.read().strip("\n\r ")
conninfo = f"dbname=regions user=drones password={stuff} host=192.168.0.200 port=5433"

with psycopg.connect(conninfo) as conn:
    with conn.cursor() as cur:
        values = [("BLA",), ("AER",), ("SHAR",)]
        sql_string = "INSERT INTO bpla_types (name) values (%s);"
        cur.executemany(sql_string, values)
        conn.commit()
print("Done")
