import datetime
import functools
import os
import dotenv

import aiofiles
import uvicorn
from fastapi import FastAPI, UploadFile, Depends
from fastapi.staticfiles import StaticFiles
from typing import Annotated

from ultralytics import YOLO

import sqlalchemy as db

"""
Global variables
"""
dotenv.load_dotenv()

app = FastAPI()
if "DATABASE_URL" in os.environ:
    engine = db.create_engine(os.environ["DATABASE_URL"])
    # TODO: user should send classroom_id along with image
    classroom = "AB1-201"
else:
    raise EnvironmentError("DATABASE_URL not available")

"""
Utility functions
"""


def get_model():
    return YOLO("weights/facialv1.pt")


def get_connection():
    return engine.connect()


# For now, its fixed
@functools.lru_cache()
def get_annotation():
    conn = get_connection()
    query = db.text(
        "SELECT * FROM seat WHERE classroom_id=:id").bindparams(id=classroom)

    res = conn.execute(query)
    annotate = {}
    for row in res:
        annotate[row[0]] = []
        for i in range(1, 9, 2):
            annotate[row[0]].append((row[i], row[i+1]))

    return annotate


def get_uploaded_images():
    return os.listdir('uploads')


@functools.lru_cache(maxsize=16)
def get_image_name(year: int, month: str, day: int, time: str):
    image_names = get_uploaded_images()
    month_names = (
        "January", "February", "March",
        "April", "May", "June",
        "July", "August", "September",
        "October", "November", "December"
    )

    try:
        hour, minutes = map(int, time.split(' ')[0].split(':'))
        hour = (hour if hour < 12 else 0) if time.split(
            ' ')[-1] == "AM" else (hour + 12 if hour < 12 else 12)
        date = datetime.datetime(
            year, month_names.index(month) + 1, day, hour, minutes)
        name = date.strftime("%Y-%m-%d-%H-%M")
        image_name = list(filter(lambda n: n.split('.')
                          [0] == name, image_names))[0]
        return image_name
    except IndexError | TypeError:
        return None


def check_image_info(image_name: str):
    conn = get_connection()
    query = db.text("SELECT count(seat_id) FROM image_seat\
                     WHERE image_id=:image_id").bindparams(image_id=image_name)

    res = conn.execute(query)
    row = res.fetchone()
    return row is not None and row[0] > 0


def get_image_info(image_name: str):
    conn = get_connection()
    query = db.text("SELECT student.id, student.name, image_seat.present\
                     FROM image_seat\
                     JOIN student_seat ON image_seat.seat_id = student_seat.seat_id\
                     JOIN student ON student_seat.student_id = student.id\
                     WHERE image_seat.image_id = :image_id").bindparams(image_id=image_name)
    res = conn.execute(query)
    info = [{"id": row[0], "name": row[1], "isPresent": row[2] == 1}
            for row in res]
    return sorted(info, key=lambda row: row["id"])


def post_image_info(id: str, present: set[str], absent: set[str]):
    conn = get_connection()
    query = db.text("INSERT INTO image\
                     VALUE (:image_id, :width, :height, :classroom_id)").bindparams(
        image_id=id, width=1024, height=768, classroom_id=classroom)
    # width, height, classrom_id should be know at upload
    conn.execute(query)
    # conn.commit()

    for seat_id in present:
        query = db.text("INSERT INTO image_seat\
                         VALUE (:image_id, :seat_id, :present)").bindparams(
            image_id=id, seat_id=seat_id, present=True)
        conn.execute(query)

    for seat_id in absent:
        query = db.text("INSERT INTO image_seat\
                         VALUE (:image_id, :seat_id, :present)").bindparams(
            image_id=id, seat_id=seat_id, present=False)
        conn.execute(query)

    conn.commit()


"""
Router handlers
"""


@app.get("/")
async def root(image_name: Annotated[list[str], Depends(get_uploaded_images)]):
    year_dict = {}
    calendar = []

    for name in image_name:
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
                calendar[-1]["months"][-1]["dates"].append({
                    "date": date,
                    "times": sorted(
                        times, key=lambda time: time.split(' ')[::-1])
                })

    return {"message": "success", "calendar": calendar}


@app.get("/attendance")
def fetch_attendance(
        year: int,
        month: str,
        date: int,
        time: str,
        model: Annotated[YOLO, Depends(get_model, use_cache=True)],
        annotates: Annotated[dict, Depends(get_annotation, use_cache=True)]):
    image_name = get_image_name(year, month, date, time)
    if image_name is None:
        return {"message": "not found"}

    if not check_image_info(image_name):
        predicts = model(f"uploads/{image_name}")
        xywh = predicts[0].boxes.xywh.numpy()

        found = set()
        total = set(annotates.keys())
        for xy in xywh:
            c = (xy[0], xy[1])
            for id, box in annotates.items():
                cuts = 0
                if box[0][1] <= c[1] <= box[3][1]:
                    if c[0] <= min(box[0][0], box[3][0]):
                        cuts += 1
                    if c[0] <= min(box[1][0], box[2][0]):
                        cuts += 1
                if cuts == 1:
                    found.add(id)
                    break
        post_image_info(image_name, found, total - found)

    image_info = get_image_info(image_name)
    return {
        "message": "success",
        "attendance": image_info,
        "imageUri": f"/uploads/{image_name}"
    }

@app.patch("/attendance")
def update_attendance(
        year: int,
        month: str,
        date: int,
        time: str,
        student_id: str,
        is_present: bool):
    image_name = get_image_name(year, month, date, time)
    conn = get_connection()
    query = db.text("update image_seat set present=:present\
                     where seat_id=(select seat_id from student_seat where student_id = :student_id)\
                     and image_id=:image_id; ").bindparams(
        present=is_present, student_id=student_id, image_id=image_name)
    conn.execute(query)
    conn.commit()
    pass

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

if not os.path.exists('uploads'):
    os.makedirs('uploads')
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")


"""
Startup
"""
if __name__ == "__main__":
    host = os.environ.get("API_HOST",  "127.0.0.1")
    port = int(os.environ.get("API_PORT", 8000))
    uvicorn.run("main:app", host=host, port=port, reload=True)
