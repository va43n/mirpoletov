import logging

import psycopg

from config_vars_safe import pass_info, _dbname, _host, _port, _user

logging.basicConfig(level=logging.INFO)
file = open(pass_info)
del pass_info
stuff = file.read().strip("\n\r ")
conninfo = f"dbname={_dbname} user={_user} password={stuff} host={_host} port={_port}"
del _dbname, _host, _port, _user, stuff

with psycopg.connect(conninfo) as conn:
    with conn.cursor() as cur:
        values = [("BLA",), ("AER",), ("SHAR",)]
        sql_string = "INSERT INTO bpla_types (name) values (%s);"
        cur.executemany(sql_string, values)
        conn.commit()
print("Done")
