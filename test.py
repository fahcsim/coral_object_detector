import urllib.request
import socket
import requests
import os
import shutil
import yaml
import time


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
try: bypass_mode = data["bypass_mode"]
except KeyError: bypass_mode = False
try: bypass_image = data["bypass_image"]
except KeyError: bypass_image = "null"    
for camera in data["cameras"]:
      camera_friendly = camera
      camera_id = data["cameras"][camera]["camera_id"]
      object = data["cameras"][camera]["object"]
      threshold = data["cameras"][camera]["threshold"]
      count = data["cameras"][camera]["count"]
      interval = data["cameras"][camera]["interval"]
      method = data["cameras"][camera]["method"]
