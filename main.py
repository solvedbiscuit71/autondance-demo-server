import datetime
import json
import os
import dotenv

import aiofiles
import uvicorn
from fastapi import FastAPI, UploadFile, Response
from fastapi.staticfiles import StaticFiles

app = FastAPI()

@app.get("/")
async def root():
    image_names = os.listdir('uploads')
    year_dict = {}
    calendar = []

    for name in image_names:
        date = datetime.datetime(*map(int, name.split('.')[0].split('-')))
        year, month, day = date.year, date.strftime("%B"), date.day

        if year not in year_dict:
            year_dict[year] = {}
        if month not in year_dict[year]:
            year_dict[year][month] = {}
        if day not in year_dict[year][month]:
            year_dict[year][month][day] = []
        year_dict[year][month][day].append(date.strftime("%I:%M %p"))

    for year, month_dict in year_dict.items():
        calendar.append({"year": year, "months": []})

        for month, date_dict in month_dict.items():
            calendar[-1]["months"].append({"month": month, "dates": []})

            for date, times in date_dict.items():
                calendar[-1]["months"][-1]["dates"].append({"date": date, "times": times})

    return {"message": "success", "calendar": calendar}
            

@app.post("/upload")
async def upload_file(file: UploadFile):
    os.makedirs("uploads", exist_ok=True)

    timestamp = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M")
    file_extension = file.filename.split('.')[-1]
    file_name = f"{timestamp}.{file_extension}"
    path = os.path.join("uploads", file_name)

    async with aiofiles.open(path, "wb") as f:
        while chunk := await file.read(8192):
            await f.write(chunk)

    return {"message": "success", "imageUri": f"/{path}"}


app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")


if __name__ == "__main__":
    dotenv.load_dotenv()

    host = os.environ.get("API_HOST",  "127.0.0.1")
    port = int(os.environ.get("API_PORT", 8000))
    uvicorn.run("main:app", host=host, port=port, reload=True)
