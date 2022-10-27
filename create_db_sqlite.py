import sqlite3
import os
import logging


def create_db_sqlite(cameras_list, log_level):
  logging.basicConfig()
  logging.getLogger().setLevel(log_level)
  if os.path.exists('data.db') == False:
    con = sqlite3.connect('data.db')
    cur = con.cursor()
    logging.debug(cameras_list)
    for camera in cameras_list:
      cur.execute('CREATE TABLE ' + camera + '( label text, confidence integer, y_min integer, y_max integer, x_min integer, x_max integer, camera_id text, timestamp text, filename text)')
                        
    con.commit()
  else:
    print("database already exists")
log_level = "DEBUG"
cameras_list = ['front_door', 'garage_1', 'garage_2', 'bay_window', 'chimney', 'gate', 'my_office']
create_db_sqlite(cameras_list, log_level)