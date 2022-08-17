import logging
import urllib.request
import socket
import requests
import timestamp
import asyncio
async def grab_jpeg(directory,camera_friendly,shinobi_ip,api_key,group_key,camera_id,log_level):
  now = timestamp.now()
  filename = (directory + camera_friendly + now + '.jpeg')
  filename_tmp = (directory + 'tmp/' + camera_friendly + now + '.jpeg')
  logging.debug(f"Getting temporary jpeg from shinobi: {filename_tmp}")
  imgURL = ('http://' + shinobi_ip + '/' + api_key + '/jpeg/' + group_key + '/' + camera_id + '/s.jpg')
  logging.debug(f"image URL is {imgURL}")
  try:
      urllib.request.urlretrieve(imgURL, filename_tmp)
      return filename, filename_tmp, now
  except:
      logging.warning("no response from Shinobi, waiting 1 second. If the app is just starting up, this is fine to ignore")
      sleep(1)
      self.now = timestamp.now()
      filename = (directory + camera_friendly + now + '.jpeg')
      filename_tmp = (directory + '/tmp/' + camera_friendly + now + '.jpeg')
      urllib.request.urlretrieve(imgURL, filename)
      print(filename)
      return filename, filename_tmp, now