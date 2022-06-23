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


def grab_jpeg(directory,camera_friendly,shinobi_ip,api_key,group_key,camera_id):
  now = timestamp.now()
  filename = (directory + camera_friendly + now + '.jpeg')
  imgURL = ('http://' + shinobi_ip + '/' + api_key + '/jpeg/' + group_key + '/' + camera_id + '/s.jpg')
  try:
      urllib.request.urlretrieve(imgURL, filename)
      return filename
  except:
      logging.info("no response from Shinobi, waiting 10 seconds. If the app is just starting up, this is fine to ignore")
      sleep(10)
      self.now = timestamp.now()
      filename = (directory + camera_friendly + now + '.jpeg')
      urllib.request.urlretrieve(imgURL, filename)
      print(filename)
      return filename




########################################################
def draw_objects(draw, objs, labels):
  """Draws the bounding box and label for each object."""
  for obj in objs:
    bbox = obj.bbox
    draw.rectangle([(bbox.xmin, bbox.ymin), (bbox.xmax, bbox.ymax)],
                   outline='red')
    draw.text((bbox.xmin + 10, bbox.ymin + 10),
              '%s\n%.2f' % (labels.get(obj.id, obj.id), obj.score),
              fill='red')

def main():
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
  shinobi_image = grab_jpeg(directory,camera_friendly,shinobi_ip,api_key,group_key,camera_id)

  labels = read_label_file(labels) if labels else {}
  interpreter = make_interpreter(model)
  interpreter.allocate_tensors()

  image = Image.open(shinobi_image)
  _, scale = common.set_resized_input(
      interpreter, image.size, lambda size: image.resize(size, Image.ANTIALIAS))


  for _ in range(count):
    start = time.perf_counter()
    interpreter.invoke()
    inference_time = time.perf_counter() - start
    objs = detect.get_objects(interpreter, threshold, scale)  
  print('-------RESULTS--------')
  if not objs:
    print('No objects detected')

  for obj in objs:
    print(labels.get(obj.id, obj.id))
    print('  id:    ', obj.id)
    print('  score: ', obj.score)
    print('  bbox:  ', obj.bbox)

  #if args.output:
  #  image = image.convert('RGB')
  #  draw_objects(ImageDraw.Draw(image), objs, labels)
  #  image.save(args.output)
  #  image.show()
if __name__ == '__main__':
  main()
