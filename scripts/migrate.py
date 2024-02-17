import sqlalchemy as db
from sqlalchemy.exc import IntegrityError

import dotenv
import os
import json

dotenv.load_dotenv(".env")

meta = db.MetaData()
engine = db.create_engine(os.environ["DATABASE_URL"])

classrooms = db.Table(
    "classroom",
    meta,
    db.Column("id", db.String(10), primary_key=True),
)

seats = db.Table(
    "seat",
    meta,
    db.Column("id", db.String(6), primary_key=True),
    db.Column("x1", db.Integer, nullable=False),
    db.Column("y1", db.Integer, nullable=False),
    db.Column("x2", db.Integer, nullable=False),
    db.Column("y2", db.Integer, nullable=False),
    db.Column("x3", db.Integer, nullable=False),
    db.Column("y3", db.Integer, nullable=False),
    db.Column("x4", db.Integer, nullable=False),
    db.Column("y4", db.Integer, nullable=False),
    db.Column("classroom_id", db.String(10), db.ForeignKey("classroom.id")),
)

students = db.Table(
    "student",
    meta,
    db.Column("id", db.String(16), primary_key=True),
    db.Column("name", db.String(40), nullable=False),
)


images = db.Table(
    "image",
    meta,
    db.Column("id", db.String(24), primary_key=True),
    db.Column("width", db.Integer),
    db.Column("height", db.Integer),
    db.Column("classroom_id", db.String(10), db.ForeignKey("classroom.id")),
)

student_seat = db.Table(
    "student_seat",
    meta,
    db.Column("student_id", db.String(16), db.ForeignKey("student.id")),
    db.Column("seat_id", db.String(6), db.ForeignKey("seat.id")),
)

image_seat = db.Table(
    "image_seat",
    meta,
    db.Column("image_id", db.String(24), db.ForeignKey("image.id")),
    db.Column("seat_id", db.String(6), db.ForeignKey("seat.id")),
    db.Column("present", db.Boolean, nullable=False)
)

meta.create_all(engine)

classrooms_json = json.load(open("scripts/classrooms.json"))
students_json = json.load(open("scripts/students.json"))
seats_json = json.load(open("scripts/new_seats.json"))
student_seat_json = json.load(open("scripts/student_seats.json"))

conn = engine.connect()
flag = True

try:
    query = db.insert(classrooms).values(classrooms_json)
    conn.execute(query)
    conn.commit()
except IntegrityError:
    print("classroom already exists")

try:
    query = db.insert(students).values(students_json)
    conn.execute(query)
    conn.commit()
except IntegrityError:
    flag = False
    print("students already exists")

try:
    query = db.insert(seats).values(seats_json)
    conn.execute(query)
    conn.commit()
except IntegrityError:
    flag = False
    print("seats already exists")

if flag:
    query = db.insert(student_seat).values(student_seat_json)
    conn.execute(query)
    conn.commit()

conn.close()
