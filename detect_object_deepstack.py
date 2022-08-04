import logging
import urllib.request
import socket
import requests
import timestamp
from PIL import Image, ImageDraw, ImageFont
import os

def detect_object_deepstack(deepstack_url, shinobi_image, object):
  image_data = open(shinobi_image[1],"rb").read()
  response = requests.post(f"http://{deepstack_url}:5000/v1/vision/detection",files={"image":image_data}).json()
  label_index = -1
  try: 
      pred = iter(response['predictions'])
  except KeyError:
      logging.warning("deepstack error, waiting 10 seconds and trying again")
      sleep(10)
      response = requests.post(f"http://{deepstack_url}:5000/v1/vision/detection",files={"image":image_data}).json()
      pred = iter(response['predictions'])
  while True:
    try:
      element = next(pred)
      if object not in element['label']:
        label_index += 1
        success = False
      elif object  in element['label']:
        label_index += 1
        confidence = element['confidence']
        logging.debug(f"confidence is {confidence}")
        # create variables for square boundaries
        xmin = response['predictions'][label_index]['x_min']
        xmax = response['predictions'][label_index]['x_max']
        ymin = response['predictions'][label_index]['y_min']
        ymax = response['predictions'][label_index]['y_max']
        # define shape of square with values from deepstack
        top = [(xmin, ymin), (xmax, ymin)]
        left = [(xmin, ymin), (xmin, ymax)]
        right = [(xmax, ymin), (xmax, ymax)]
        bottom = [(xmin, ymax), (xmax, ymax)]
        # open image for processing
        img = Image.open(shinobi_image[1])
        # draw square shape on image
        img1 = ImageDraw.Draw(img)
        img1.line(top, fill ="yellow", width = 5)
        img1.line(left, fill ="yellow", width = 5)
        img1.line(right, fill ="yellow", width = 5)
        img1.line(bottom, fill ="yellow", width = 5)
        font = ImageFont.truetype("qaz.ttf", 35)
        img1.text((xmax - 100, ymax - 200), response['predictions'][label_index]['label'], (155, 250, 0), font)
        img.save(shinobi_image[0])
        os.remove(shinobi_image[1])
        object = response['predictions'][label_index]['label']
        logging.debug(f"Detection from deepstack is: {object}")
        success = True
        now = shinobi_image[2]
        return object, confidence, ymin, ymax, xmin, xmax, now, shinobi_image[1], success
        break
    except StopIteration:
      break
  