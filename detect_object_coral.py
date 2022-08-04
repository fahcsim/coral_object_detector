from PIL import Image
from PIL import ImageDraw
from pycoral.adapters import common
from pycoral.adapters import detect
from pycoral.utils.dataset import read_label_file
from pycoral.utils.edgetpu import make_interpreter
import time
import logging 
import os
from draw_objects import draw_objects
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
