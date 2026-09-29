from fastapi import APIRouter
from sensor_flow import process_sensor_flow

router = APIRouter(
    prefix="/sensor-flow",
    tags=["Sensor Flow"]
)


@router.get("")
def get_sensor_flow():
    return process_sensor_flow()
