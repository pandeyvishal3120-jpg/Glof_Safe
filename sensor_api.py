from database import SessionLocal, engine
from models import Base, SensorReading

Base.metadata.create_all(bind=engine)


def save_sensor_reading(lake_id, water_level, seismic_value):
    db = SessionLocal()

    try:
        reading = SensorReading(
            lake_id=lake_id,
            water_level=water_level,
            seismic_value=seismic_value
        )

        db.add(reading)
        db.commit()
        db.refresh(reading)

        return reading

    finally:
        db.close()
