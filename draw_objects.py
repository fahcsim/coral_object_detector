from PIL import Image, ImageDraw, ImageFont
import logging
def draw_objects_coral(objs, shinobi_image, label): # fix this up so that we're passing in a set of coordinates instead of obj
  """Draws the bounding box and label for each object."""
  for obj in objs:
    xmax = obj.bbox.xmax
    xmin = obj.bbox.xmin
    ymax =  obj.bbox.ymax
    ymin = obj.bbox.ymin
    top = [(xmin, ymin), (xmax, ymin)]
    left = [(xmin, ymin), (xmin, ymax)]
    right = [(xmax, ymin), (xmax, ymax)]
    bottom = [(xmin, ymax), (xmax, ymax)]
    img = Image.open(shinobi_image[1])
    img1 = ImageDraw.Draw(img)
    img1.line(top, fill ="yellow", width = 5)
    img1.line(left, fill ="yellow", width = 5)
    img1.line(right, fill ="yellow", width = 5)
    img1.line(bottom, fill ="yellow", width = 5)
    font = ImageFont.truetype("qaz.ttf", 35)
    logging.debug(f"object is {label}")
    img1.text((xmax - 100, ymax - 200), label, (155, 250, 0), font)
    img.save(shinobi_image[0])


def draw_objects_deepstack(response, shinobi_image, label_index):
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
 