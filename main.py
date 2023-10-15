import os
import datetime
from fastapi import FastAPI, UploadFile, Response
import aiofiles
import json

app = FastAPI()

data = json.load(open(r"data/calendar.json", "r"))
record = json.load(open(r"data/records.json", "r"))


async def process_image():
    async with aiofiles.open("demo.json", "r") as f:
        data = await f.read()
        return json.loads(data)


@app.post("/upload")
async def upload_file(file: UploadFile):
    os.makedirs("uploads", exist_ok=True)

    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    name = f"{timestamp}_{file.filename}"
    path = os.path.join("uploads", name)

    async with aiofiles.open(path, "wb") as f:
        while chunk := await file.read(8192):
            await f.write(chunk)

    data = await process_image()  # dummy api call

    return {"message": "success", "data": data}


@app.get("/records")
def get_records(year: str, month: str, date: str, response: Response, time: str | None = None):
    response.status_code = 404
    if year not in record:
        return {"message": "year not found"}

    if month not in record[year]:
        return {"message": "month not found"}

    if date not in record[year][month]:
        return {"message": "date not found"}

    if time is None:
        response.status_code = 200
        return {"message": "success", "data": list(record[year][month][date].keys())}

    if time in record[year][month][date]:
        response.status_code = 200
        return {"message": "success", "data": record[year][month][date][time]}
    return {"message": "time not found"}


@app.get("/")
def root():
    return data
