import urllib.request
import socket
import requests
import os
import shutil
import yaml
import time
import logging
import timestamp
import argparse
from PIL import Image
from PIL import ImageDraw
from pycoral.adapters import common
from pycoral.adapters import detect
from pycoral.utils.dataset import read_label_file
from pycoral.utils.edgetpu import make_interpreter
import sqlite3
from create_db_sqlite import create_db_sqlite

# Connect to sqlite database
con = sqlite3.connect('data.db', isolation_level=None)
cur = con.cursor()

def reset_directories(directory):
  if not os.path.exists(directory):
    os.mkdir(directory)
  if not os.path.exists(f"{directory}tmp"):
    os.mkdir(f"{directory}tmp")
  elif os.path.exists(f"{directory}tmp"):
    # remove tmp directory and its contents, then recreate it
    shutil.rmtree(f"{directory}tmp")
    os.mkdir(f"{directory}tmp")

def grab_jpeg(directory,camera_friendly,shinobi_ip,api_key,group_key,camera_id,log_level):
  now = timestamp.now()
  filename = (directory + camera_friendly + now + '.jpeg')
  filename_tmp = (directory + 'tmp/' + camera_friendly + now + '.jpeg')
  logging.debug(f"Getting temporary jpeg from shinobi: {filename_tmp}")
  imgURL = ('http://' + shinobi_ip + '/' + api_key + '/jpeg/' + group_key + '/' + camera_id + '/s.jpg')
  try:
      urllib.request.urlretrieve(imgURL, filename_tmp)
      return filename, filename_tmp, now
  except:
      logging.warning("no response from Shinobi, waiting 10 seconds. If the app is just starting up, this is fine to ignore")
      sleep(10)
      self.now = timestamp.now()
      filename = (directory + camera_friendly + now + '.jpeg')
      filename_tmp = (directory + '/tmp/' + camera_friendly + now + '.jpeg')
      urllib.request.urlretrieve(imgURL, filename)
      print(filename)
      return filename, filename_tmp, now

def draw_objects(draw, objs, labels):
  """Draws the bounding box and label for each object."""
  for obj in objs:
    bbox = obj.bbox
    draw.rectangle([(bbox.xmin, bbox.ymin), (bbox.xmax, bbox.ymax)],
                   outline='yellow')
    draw.text((bbox.xmin + 10, bbox.ymin + 10),
              '%s\n%.2f' % (labels.get(obj.id, obj.id), obj.score),
              fill='yellow')

def detect_object_coral(labels, model, shinobi_image, count, threshold, thing):
  labels = read_label_file(labels) if labels else {}
  interpreter = make_interpreter(model)
  interpreter.allocate_tensors()
  image = Image.open(shinobi_image[1])
  _, scale = common.set_resized_input(
      interpreter, image.size, lambda size: image.resize(size, Image.ANTIALIAS))
  for _ in range(count):
    start = time.perf_counter()
    interpreter.invoke()
    inference_time = time.perf_counter() - start
    objs = detect.get_objects(interpreter, threshold, scale)  
  print('-------RESULTS--------')
  if not objs:
    success = False
    logging.debug(f"No objects detected, deleting {shinobi_image[1]}")
    os.remove(shinobi_image[1])
  else:
    success = True
    for obj in objs:
      confidence = round((obj.score * 100))
      xmax = obj.bbox.xmax
      xmin = obj.bbox.xmin
      ymax =  obj.bbox.ymax
      ymin = obj.bbox.ymin
      label = (labels.get(obj.id))
      filename = shinobi_image[0]
      filename_tmp = shinobi_image[1]
      now = shinobi_image[2]
      detection = {'predictions': [{'x_max': xmax, 'x_min': xmin, 'y_max': ymax,  'y_min': ymin, 'label': label, 'confidence': confidence }], 'success': success}
      logging.debug(f"Object Detected! File saved as {shinobi_image[0]}")
      logging.debug(f"Detection details: {detection}")
      image = image.convert('RGB')
      draw_objects(ImageDraw.Draw(image), objs, labels)
      image.save(filename)
      os.remove(filename_tmp)
      return thing, confidence, ymin, ymax, xmin, xmax, now, filename, success
def insert_row(thing, confidence, ymin, ymax, xmin, xmax, camera_friendly, now, filename):
    ## Insert values into database
      cur.execute("INSERT INTO DETECTIONS(LABEL, CONFIDENCE, Y_MIN, Y_MAX, X_MIN, X_MAX, CAMERA_ID, TIMESTAMP, FILENAME) VALUES (?,?,?,?,?,?,?,?,?)", (thing, confidence, ymin, ymax, xmin, xmax, camera_friendly, now, filename))
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
      thing = data["object"]
      log_level = data["log"]
      interval = data["interval"]
      model = data["model"]
      labels = data["labels"]
      threshold = data["threshold"]
      count = data["count"]
      logging.basicConfig()
      logging.getLogger().setLevel(log_level)
  reset_directories(directory)
  shinobi_image = grab_jpeg(directory,camera_friendly,shinobi_ip,api_key,group_key,camera_id,log_level)
  detection = detect_object_coral(labels, model, shinobi_image, count, threshold, thing)
  print(detection)
  try:
    thing, confidence, ymin, ymax, xmin, xmax, now, filename, success = detection[0], detection[1], detection[2], detection[3], detection[4], detection[5], detection[6], detection[7], detection[8]  
    if success == True:
       insert_row(thing, confidence, ymin, ymax, xmin, xmax, camera_friendly, now, filename)
  except TypeError:
    logging.debug(f"unable to load detection details, restarting")
 






while True:
  if __name__ == '__main__':
    main()
    time.sleep(5)

## todo
# create error page for web ui when there are no rows in database
# nest config items under categories