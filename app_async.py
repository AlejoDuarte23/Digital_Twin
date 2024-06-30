import json
from fastapi.staticfiles import StaticFiles
from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, StreamingResponse, JSONResponse
import asyncio

templates = Jinja2Templates(directory="templates")

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/preprocesing", StaticFiles(directory="preprocesing"), name="preprocesing")

def load_json(file_path):
    with open(file_path, 'r') as file:
        data = json.load(file)
    return data

def get_cords_from_geojson(file_path:str):
    geo_data = load_json(file_path)
    cords = []
    for inner_dicts in geo_data["features"]:
        cords.append(inner_dicts['geometry']['coordinates'])
    return cords

cords2stream_truck1 = get_cords_from_geojson('preprocesing/gps_04_02.geojson')
cords2stream_truck2 = get_cords_from_geojson('preprocesing/gps_03_23.geojson')
cords2stream_truck3 = get_cords_from_geojson('preprocesing/gps_03_25.geojson')

min_len = min(len(cords2stream_truck1), len(cords2stream_truck2), len(cords2stream_truck3))
current_index = 0

async def background_stream(min_len=min_len):
    global current_index
    while True:
        await asyncio.sleep(1)
        current_index = (current_index + 1) % min_len

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(background_stream())

async def stream_cords():
    global current_index
    while True:
        await asyncio.sleep(2)
        yield f"data: {json.dumps({'truck_1': cords2stream_truck1[current_index], 'truck_2': cords2stream_truck2[current_index], 'truck_3': cords2stream_truck3[current_index]})}\n\n"

@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("gps_temp.html", {"request": request})

@app.get("/stream-cords")   
async def stream():
    return StreamingResponse(stream_cords(), media_type="text/event-stream")

@app.get("/data")
async def gps_data():
    data2 = get_cords_from_geojson()
    return JSONResponse(content=data2)

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8888)