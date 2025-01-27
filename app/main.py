from fastapi import FastAPI, UploadFile, File, Form, APIRouter, Request
from fastapi.middleware.cors import CORSMiddleware
from databases import Database
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy import Column, Integer, MetaData, String, Table, select
import os
import logging
logging.basicConfig()
logging.getLogger().setLevel("INFO")
import re
templates = Jinja2Templates(directory="templates")
database = Database("sqlite:///data.db")
app = FastAPI()
app = FastAPI()
app.mount("/photos", StaticFiles(directory="photos"), name="photos")
app.mount("/templates", StaticFiles(directory="templates"), name="templates")
api_router = APIRouter()


@app.on_event("startup")
async def database_connect():
    await database.connect()

async def fetch_data(camera):
    query = 'SELECT oid,timestamp,label,confidence,filename FROM ' + camera + ' ORDER BY timestamp DESC LIMIT 0,1'
    results = await database.fetch_all(query=query)
    return results

async def get_cameras():
    query = "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
    results = await database.fetch_all(query=query)
    return results


@app.on_event("shutdown")
async def database_disconnect():
    await database.disconnect()

@app.get("/{camera}/detection/latest", response_class=HTMLResponse)

async def latest(request: Request, camera: str):
################################
# clean up list of cameras
################################
    cameras_list = await get_cameras()
    camera_names = []
    for name in cameras_list:
        camera_name = re.sub(r'\'\,\)', '', re.sub(r'\(\'', '', str(name)))
        logging.debug(camera_name)
        camera_names.append(camera_name)
####################################
# Get data from sqlite
################################
    fetch_data_response = await fetch_data(camera)
    oid = fetch_data_response[0][0]
    timestamp = fetch_data_response[0][1]
    label = fetch_data_response[0][2]
    confidence = "{:.0%}".format(fetch_data_response[0][3])
    filename = fetch_data_response[0][4].lstrip(".")
    next = await get_next(oid, camera)
    next_oid = int(next[0])
    camera = camera
##################################
    if str(next[1]) == "none":
        next_filename = filename.lstrip("./photos")
    else:
        next_filename = str(next[1])
    previous_oid = int(next[2])
    if str(next[3]) == "none":
        previous_filename = filename
    else:
        previous_filename = str(next[3])
    return templates.TemplateResponse("detection_template.html", {"request": request, "filename": filename, "label": label, "confidence": confidence, "timestamp": timestamp, "oid": oid, "next_filename": next_filename, "previous_oid": previous_oid, "previous_filename": previous_filename, "camera": camera, "cameras_list": cameras_list})

async def get_next(oid, camera):

    id = oid
    await database.connect()
    METADATA = MetaData()
    camera_table = Table(
        camera,
        METADATA,
        Column("oid", Integer, primary_key=True),
        Column("label", String),
        Column("confidence", String),
        Column("y_min", Integer),
        Column("y_max", Integer),
        Column("x_min", Integer),
        Column("x_max", Integer),
        Column("camera_id", String),
        Column("timestamp", String),
        Column("filename", String),
    )
    next_query = camera_table.select().where(camera_table.c.oid == (id + 1))
    previous_query = camera_table.select().where(camera_table.c.oid == (id - 1))
    rows = await database.fetch_all(next_query)
    try: 
        next_oid = rows[0][0]
    except:
        next_oid = 0
    try:
        next_filename = rows[0][9].lstrip("./photos")
    except:
        next_filename = "none"
    rows2 = await database.fetch_all(previous_query)
    try:
        previous_oid = rows2[0][0]
    except:
        previous_oid = 0
    try:
        previous_filename = rows2[0][9].lstrip("./photos")    
    except:
        previous_filename = "none"
    return next_oid, next_filename, previous_oid, previous_filename

@app.get("/{camera}/detection/{filename}", response_class=HTMLResponse)

async def read_item(request: Request, filename: str, camera: str):
################################
# clean up list of cameras
################################
    cameras_list = await get_cameras()
    camera_names = []
    for name in cameras_list:
        camera_name = re.sub(r'\'\,\)', '', re.sub(r'\(\'', '', str(name)))
        logging.debug(camera_name)
        camera_names.append(camera_name)
    await database.connect()
    METADATA = MetaData()
    camera_table = Table(
        camera,
        METADATA,
        Column("oid", Integer, primary_key=True),
        Column("label", String),
        Column("confidence", String),
        Column("y_min", Integer),
        Column("y_max", Integer),
        Column("x_min", Integer),
        Column("x_max", Integer),
        Column("camera_id", String),
        Column("timestamp", String),
        Column("filename", String),
    )
    query = camera_table.select().where(camera_table.c.filename == ('./photos/' + filename))
    rows = await database.fetch_all(query)
    oid = int(rows[0][0])
    timestamp = str(rows[0][8])
    label = str(rows[0][2])
    confidence = str("{:.0%}".format(rows[0][2]))
    filename = str(rows[0][9].lstrip("."))
    next = await get_next(oid, camera)
    next_oid = int(next[0])
    if str(next[1]) == "none":
        next_filename = filename.lstrip("./photos")
    else:
        next_filename = str(next[1])
    previous_oid = int(next[2])
    if str(next[3]) == "none":
        previous_filename = filename
    else:
        previous_filename = str(next[3])
    return templates.TemplateResponse("detection_template.html", {"request": request, "filename": filename, "label": label, "confidence": confidence, "timestamp": timestamp, "oid": oid, "next_filename": next_filename, "previous_oid": previous_oid, "previous_filename": previous_filename, "camera": camera, "cameras_list": cameras_list})

#@app.get("/test",  response_class=HTMLResponse)


@app.get("/url-list")
def get_all_urls():
    url_list = (os.listdir('photos'))
    next = url_list[(len(url_list)-1)]
    return next
