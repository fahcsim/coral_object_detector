import urllib.request
import socket
import requests
import os
import yaml
import time
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

def check_directories(directory):
  if not os.path.exists(directory):
    os.mkdir(directory)
  if not os.path.exists(f"{directory}/tmp"):
    os.mkdir(f"{directory}/tmp")

def grab_jpeg(directory,camera_friendly,shinobi_ip,api_key,group_key,camera_id):
  now = timestamp.now()
  filename = (directory + camera_friendly + now + '.jpeg')
  filename_tmp = (directory + 'tmp/' + camera_friendly + now + '.jpeg')
  imgURL = ('http://' + shinobi_ip + '/' + api_key + '/jpeg/' + group_key + '/' + camera_id + '/s.jpg')
  try:
      urllib.request.urlretrieve(imgURL, filename_tmp)
      return filename, filename_tmp, now
  except:
      logging.info("no response from Shinobi, waiting 10 seconds. If the app is just starting up, this is fine to ignore")
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
  check_directories(directory)
  shinobi_image = grab_jpeg(directory,camera_friendly,shinobi_ip,api_key,group_key,camera_id)
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
    print('No objects detected')
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
      
      print(detection)
      image = image.convert('RGB')
      draw_objects(ImageDraw.Draw(image), objs, labels)
      image.save(filename)
      os.remove(filename_tmp)
    ## Insert values into database
      cur.execute("INSERT INTO DETECTIONS(LABEL, CONFIDENCE, Y_MIN, Y_MAX, X_MIN, X_MAX, CAMERA_ID, TIMESTAMP, FILENAME) VALUES (?,?,?,?,?,?,?,?,?)", (thing, confidence, ymin, ymax, xmin, xmax, camera_friendly, now, filename))
      con.commit()
      
while True:
  if __name__ == '__main__':
    main()
    time.sleep(5)

## todo
# make sure photo/tmp is added automatically