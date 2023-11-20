from typing import Union

from fastapi import FastAPI

app = FastAPI()


@app.get("/")
async def read_root():
    return {"Message": "FPI-BitkubBot V3"}

@app.get("/hc")
async def root():
    return {"Message": "Healthy"}


