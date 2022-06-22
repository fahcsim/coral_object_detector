import urllib.request
import socket
import requests
import os
import yaml
import time
import timestamp

def grab_jpeg(directory,camera_friendly,shinobi_ip,api_key,group_key,camera_id):
  now = timestamp.now()
  filename = (directory + camera_friendly + now + '.jpeg')
  imgURL = ('http://' + shinobi_ip + '/' + api_key + '/jpeg/' + group_key + '/' + camera_id + '/s.jpg')
  try:
      urllib.request.urlretrieve(imgURL, filename)
  except:
      logging.info("no response from Shinobi, waiting 10 seconds. If the app is just starting up, this is fine to ignore")
      sleep(10)
      self.now = timestamp.now()
      filename = (directory + camera_friendly + now + '.jpeg')
      urllib.request.urlretrieve(imgURL, filename)

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
  image = grab_jpeg(directory,camera_friendly,shinobi_ip,api_key,group_key,camera_id)

if __name__ == '__main__':
  main()
