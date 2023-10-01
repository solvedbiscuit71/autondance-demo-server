import os
import datetime
from fastapi import FastAPI, UploadFile
import aiofiles

app = FastAPI()


@app.post("/upload")
async def upload_file(file: UploadFile):
    os.makedirs("uploads", exist_ok=True)

    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    name = f"{timestamp}_{file.filename}"
    path = os.path.join("uploads", name)

    async with aiofiles.open(path, "wb") as f:
        while chunk := await file.read(8192):
            await f.write(chunk)

    return {"message": f"uploaded {name}"}
