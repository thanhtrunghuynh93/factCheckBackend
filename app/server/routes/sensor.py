from fastapi import APIRouter, Body
from fastapi.encoders import jsonable_encoder

from server.dms.sensor import (
    add_sensor,
    delete_sensor,
    retrieve_sensor,
    retrieve_sensors,
    update_sensor,
)
from server.utils.response import (
    ErrorResponseModel,
    ResponseModel,
)
from server.models.sensor import SensorSchema

router = APIRouter()

@router.get("/get_sensors/", response_description="sensors retrieved")
async def get_sensors():
    sensors = await retrieve_sensors()
    if sensors:
        return ResponseModel(sensors, "sensors data retrieved successfully")
    return ResponseModel(sensors, "Empty list returned")


@router.get("/get_sensor_by_id/{device_id}", response_description="sensor data retrieved")
async def get_sensor_data(device_id):
    sensors = await retrieve_sensor(device_id)
    if sensors:
        return ResponseModel(sensors, "sensor data retrieved successfully")
    return ErrorResponseModel("An error occurred.", 404, "sensor doesn't exist.")


@router.post("/add_sensor", response_description="sensor data added into the database")
async def add_sensor_data(sensor: SensorSchema = Body(...)):
    sensor = jsonable_encoder(sensor)
    new_sensor = await add_sensor(sensor)
    return ResponseModel(new_sensor, "sensor added successfully.")

@router.post("/update_sensor_by_id", response_description="update device")
async def update_sensor_by_id(sensor: SensorSchema = Body(...)):
    sensor = jsonable_encoder(sensor)
    updated_sensor = await update_sensor(sensor["_id"], sensor)
    if sensor:
        return ResponseModel(updated_sensor, "sensor updated successfully.")
    return ErrorResponseModel(
        "An error occurred", 404, "sensor with _id {0} doesn't exist".format(sensor["_id"])
    )

@router.delete("/delete_sensor_by_id/{device_id}", response_description="sensor data deleted from the database")
async def delete_sensor_data(device_id: str):
    deleted_sensor = await delete_sensor(device_id)
    if deleted_sensor:
        return ResponseModel(
            "sensor with ID: {} removed".format(device_id), "sensor deleted successfully"
        )
    return ErrorResponseModel(
        "An error occurred", 404, "sensor with device_id {0} doesn't exist".format(device_id)
    )
