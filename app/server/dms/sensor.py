import motor.motor_asyncio
from bson import ObjectId
from decouple import config
from typing import Optional
from server.database.mongo import database

sensor_collection = database.get_collection("sensor")

# helpers
def sensor_helper(sensor) -> dict:
    return {
        "id": str(sensor["_id"]),
        "device_id": sensor["device_id"],
        "datetime": sensor["datetime"],
        "PM2_5": sensor["PM2_5"],
        "PM10": sensor["PM10"],
        "PM1_0": sensor["PM1_0"],
        "temperature": sensor["temperature"],
        "humidity": sensor["humidity"],
        "CO": sensor["CO"],
        "CO2": sensor["CO2"],
        "NO2": sensor["NO2"],
        "O3": sensor["O3"],
        "SO2": sensor["SO2"],
    }


async def retrieve_sensors():
    sensors = []
    async for sensor in sensor_collection.find().limit(20):
        sensors.append(sensor_helper(sensor))
    return sensors

async def add_sensor(sensor_data: dict) -> dict:
    sensor = await sensor_collection.insert_one(sensor_data)
    new_sensor = await sensor_collection.find_one({"_id": sensor.inserted_id})
    return sensor_helper(new_sensor)

async def retrieve_sensor(device_id: str) -> dict:
    sensors = []
    async for sensor in sensor_collection.find({"device_id": device_id}):
        sensors.append(sensor_helper(sensor))
    return sensors

async def update_sensor(_id: str, data: dict):
    if len(data) < 1:
        return False
    sensor = await sensor_collection.find_one({"_id": _id})
    if sensor:
        updated_sensor = await sensor_collection.update_one(
            {"_id": _id}, {"$set": data}
        )
        if updated_sensor:
            return True
        return False

async def delete_sensor(_id: str):
    sensor = await sensor_collection.find_one({"_id": id})
    if sensor:
        await sensor_collection.delete_one({"_id": id})
        return True