import urllib.request
import socket
import requests
import os
import shutil
import yaml
import time
import logging
import argparse
from PIL import Image, ImageDraw, ImageFont, ImageFile
from PIL import UnidentifiedImageError
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
import asyncio

# Connect to sqlite database
con = sqlite3.connect('data.db', isolation_level=None)
cur = con.cursor()

async def insert_row(object, confidence, ymin, ymax, xmin, xmax, camera_friendly, now, filename):
  await cur.execute('INSERT INTO ' + camera_friendly +'(LABEL, CONFIDENCE, Y_MIN, Y_MAX, X_MIN, X_MAX, CAMERA_ID, TIMESTAMP, FILENAME) VALUES (?,?,?,?,?,?,?,?,?)', (object, confidence, ymin, ymax, xmin, xmax, camera_friendly, now, filename))
  con.commit()

async def main():
  
  ## Get variables from yaml config file
  with open('vars.yaml') as f:
    data = yaml.load(f, Loader=yaml.FullLoader)
  api_key = data["api_key"]
  directory = data["directory"]
  user_id = data["user_id"]
  group_key = data["group_key"]
  shinobi_ip = data["shinobi_ip"]
  log_level = data["log"]
  model = data["model"]
  labels = data["labels"]
  deepstack_url = data["deepstack_url"]
  logging.basicConfig()
  logging.getLogger().setLevel(log_level)
  reset_directories(directory)
  try: bypass_mode = data["bypass_mode"]
  except KeyError: bypass_mode = False
  try: bypass_image = data["bypass_image"]
  except KeyError: bypass_image = "null"    
  try: add_labels = data["add_labels"]
  except KeyError: bypass_image = "null"
  cameras_list = []
  for camera in data["cameras"]:
    camera_friendly = camera
    cameras_list.append(camera)

  logging.debug(f"cameras are {cameras_list}")
  create_db_sqlite(cameras_list, log_level)
  for camera in data["cameras"]:
    camera_friendly = camera
    camera_id = data["cameras"][camera]["camera_id"]
    object = data["cameras"][camera]["object"]
    threshold = data["cameras"][camera]["threshold"]
    count = data["cameras"][camera]["count"]
    interval = data["cameras"][camera]["interval"]
    method = data["cameras"][camera]["method"]
    
  # Bypass mode allows you to use a static jpeg file instead of getting them from shinobi.
  # Useful for testing, not really useful for detecting actual objects
    if bypass_mode == True and bypass_image != "null":
      now = timestamp.now()
      bypass_image_temp = f"{directory}tmp/tmp-{now}"
      shutil.copyfile(bypass_image, bypass_image_temp)
      filename = (directory + camera_friendly + now + '.jpeg')
      shinobi_image =  [filename, bypass_image_temp, now]
    else:
      shinobi_image = await grab_jpeg(directory,camera_friendly,shinobi_ip,api_key,group_key,camera_id,log_level)
    if method == "coral":
      detection = await detect_object_coral(labels, model, shinobi_image, count, threshold, object, add_labels)
      logging.debug(f"time is {timestamp.now()}")
    elif method == "deepstack":
      detection = await detect_object_deepstack(deepstack_url, shinobi_image, object, add_labels)
    try:
      object, confidence, ymin, ymax, xmin, xmax, now, filename, success = detection[0], detection[1], detection[2], detection[3], detection[4], detection[5], detection[6], detection[7], detection[8]  
      if success == True:
        await insert_row(object, confidence, ymin, ymax, xmin, xmax, camera_friendly, now, filename)

      
    except TypeError:
      logging.debug(f"unable to load detection details, restarting")
      reset_directories(directory)
 
while True:
  if __name__ == '__main__':
    asyncio.run(main())

## todo
# set up confidence variable
# create error page for web ui when there are no rows in database
# nest config items under categories
# test multi camera setup
