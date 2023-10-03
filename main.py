import datetime
import json
import os
from typing import Annotated

import aiofiles
from fastapi import FastAPI, Form, File


app = FastAPI()


async def process_image():
    async with aiofiles.open("demo.json", "r") as f:
        data = await f.read()
        return json.loads(data)


@app.post("/upload")
async def upload_file(filename: Annotated[str, Form()], filestream: Annotated[bytes, File()]):
    os.makedirs("uploads", exist_ok=True)

    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    name = f"{timestamp}_{filename}"
    path = os.path.join("uploads", name)

    async with aiofiles.open(path, "wb") as f:
        await f.write(filestream)

    response = await process_image()  # dummy api call

    return {"message": "success", "body": response}


@app.get("/")
def root():
    return {"message": "hello from fastapi"}
