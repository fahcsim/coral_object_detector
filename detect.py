import urllib.request
import socket
import requests
import os
import shutil
import yaml
import time
import logging
import argparse
from PIL import Image, ImageDraw, ImageFont
from pycoral.adapters import common
from pycoral.adapters import detect
from pycoral.utils.dataset import read_label_file
from pycoral.utils.edgetpu import make_interpreter
import sqlite3
# import local modules
import timestamp
from detect_object import detect_object_deepstack, detect_object_coral
from create_db_sqlite import create_db_sqlite
from grab_jpeg import grab_jpeg
from reset_directories import reset_directories

# Connect to sqlite database
con = sqlite3.connect('data.db', isolation_level=None)
cur = con.cursor()

def insert_row(object, confidence, ymin, ymax, xmin, xmax, camera_friendly, now, filename):
  cur.execute("INSERT INTO DETECTIONS(LABEL, CONFIDENCE, Y_MIN, Y_MAX, X_MIN, X_MAX, CAMERA_ID, TIMESTAMP, FILENAME) VALUES (?,?,?,?,?,?,?,?,?)", (object, confidence, ymin, ymax, xmin, xmax, camera_friendly, now, filename))
  con.commit()

def main():
  create_db_sqlite()
  with open('vars.yaml') as f:
      data = yaml.load(f, Loader=yaml.FullLoader)
      api_key = data["api_key"]
      directory = data["directory"]
      user_id = data["user_id"]
      group_key = data["group_key"]
      camera_id = data["camera_id"]
      camera_friendly = data["camera_friendly"]
      shinobi_ip = data["shinobi_ip"]
      object = data["object"]
      log_level = data["log"]
      interval = data["interval"]
      model = data["model"]
      labels = data["labels"]
      threshold = data["threshold"]
      count = data["count"]
      deepstack_url = data["deepstack_url"]
      method = data["method"]
      try: bypass_mode = data["bypass_mode"]
      except NameError: bypass_mode = False
      try: bypass_image = data["bypass_image"]
      except NameError: bypass_image = null    
      logging.basicConfig()
      logging.getLogger().setLevel(log_level)
  reset_directories(directory)

  if bypass_mode == True and bypass_image != "null":
    now = timestamp.now()
    bypass_image_temp = f"{directory}tmp/tmp-{now}"
    shutil.copyfile(bypass_image, bypass_image_temp)
    filename = (directory + camera_friendly + now + '.jpeg')
    shinobi_image =  [filename, bypass_image_temp, now]
    
  else:
    shinobi_image = grab_jpeg(directory,camera_friendly,shinobi_ip,api_key,group_key,camera_id,log_level)
  if method == "coral":
    detection = detect_object_coral(labels, model, shinobi_image, count, threshold, object)
  elif method == "deepstack":
    detection = detect_object_deepstack(deepstack_url, shinobi_image, object)
  print(detection)
  try:
    object, confidence, ymin, ymax, xmin, xmax, now, filename, success = detection[0], detection[1], detection[2], detection[3], detection[4], detection[5], detection[6], detection[7], detection[8]  
    if success == True:
       insert_row(object, confidence, ymin, ymax, xmin, xmax, camera_friendly, now, filename)
  except TypeError:
    logging.debug(f"unable to load detection details, restarting")
 
while True:
  if __name__ == '__main__':
    main()
    time.sleep(5)

## todo
# create error page for web ui when there are no rows in database
# nest config items under categories
# test mode with local jpeg