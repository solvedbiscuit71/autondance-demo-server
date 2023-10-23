import datetime
import json
import os
import dotenv

import aiofiles
import uvicorn
from fastapi import FastAPI, UploadFile, Response
from fastapi.staticfiles import StaticFiles


app = FastAPI()


@app.post("/upload")
async def upload_file(file: UploadFile):
    os.makedirs("uploads", exist_ok=True)

    timestamp = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M")
    file_extension = file.filename.split('.')[-1]
    name = f"{timestamp}.{file_extension}"
    path = os.path.join("uploads", name)

    async with aiofiles.open(path, "wb") as f:
        while chunk := await file.read(8192):
            await f.write(chunk)

    print(path)
    return {"message": "success", "path": f"/{path}"}


app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

if __name__ == "__main__":
    dotenv.load_dotenv()

    host = os.environ.get("API_HOST",  "127.0.0.1")
    port = int(os.environ.get("API_PORT", 8000))
    uvicorn.run("main:app", host=host, port=port, reload=True)
