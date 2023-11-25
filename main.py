import os
from fastapi import FastAPI
from BL.TradeService import *
from motor.motor_asyncio import AsyncIOMotorClient
app = FastAPI()
client = AsyncIOMotorClient(os.environ.get('ConnectionString'))
db = client.fsdatabase

@app.on_event("startup")
async def startup_event():
    print("Connecting to MongoDB...")
    await client.start_session()

@app.get("/")
async def read_root():
    return {"Message": "FPI-BitkubBot V3"}

@app.get("/hc")
async def healthcheck():
    return {"Message": "Healthy"}

@app.get("/trade")
async def trade():
    cursor = db['cryptobotconfig'].find()
    list = await cursor.to_list(length=100)
    for item in list:
        CryptoTrade(item['Name'], float(item['targetprofit']),
                float(item['targetlost']), float(item['buyprice']))
    return {"Message":"Trade Working Success!"}