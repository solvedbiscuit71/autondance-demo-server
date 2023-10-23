import datetime
import json
import os
import dotenv

import aiofiles
import uvicorn
from fastapi import FastAPI, UploadFile, Response
from fastapi.staticfiles import StaticFiles

app = FastAPI()

def fetch_image_name(year: int, month: str, day: int, time: str):
    """
    year: int
    month: str
    day: int [1-31]
    time: str (format: '%H:%M %p')
    """

    image_names = os.listdir('uploads')
    month_names = ("January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December")

    try:
        hour, minutes = map(int, time.split(' ')[0].split(':'))
        loc = time.split(' ')[-1]

        if loc == 'AM':
            hour = hour if hour < 12 else 0
        else:
            hour = hour + 12 if hour < 12 else 12
        date = datetime.datetime(year, month_names.index(month) + 1, day, hour, minutes)
        name = date.strftime("%Y-%m-%d-%H-%M")
        image_name = list(filter(lambda n: n.split('.')[0] == name, image_names))[0]
        return image_name
    except:  # If something goes wrong return None
        return None


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
                calendar[-1]["months"][-1]["dates"].append({"date": date, "times": sorted(times, key=lambda time: time.split(' ')[::-1])})

    return {"message": "success", "calendar": calendar}


@app.get("/attendance")
def fetch_attendance(year: int, month: str, date: int, time: str):
    image_name = fetch_image_name(year, month, date, time)
    if image_name is None:
        return {"message": "not found"}
    else:
        return {"message": "success", "imageUri": f"/uploads/{image_name}"}
            

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
