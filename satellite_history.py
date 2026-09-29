from datetime import datetime
from sqlalchemy import Table, Column, Integer, String, Float, DateTime, MetaData

from database import engine


metadata = MetaData()

satellite_history = Table(
    "satellite_history",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("lake_id", Integer, nullable=False),
    Column("scene_id", String),
    Column("acquisition_date", DateTime),
    Column("water_area_km2", Float),
    Column("cloud_cover", Float),
    Column("source", String),
    Column("created_at", DateTime, default=datetime.utcnow),
)

metadata.create_all(engine)


def save_satellite_history(
    lake_id,
    scene_id=None,
    acquisition_date=None,
    water_area_km2=None,
    cloud_cover=None,
    source="Copernicus Sentinel-2 L2A",
):
    with engine.begin() as conn:
        conn.execute(
            satellite_history.insert().values(
                lake_id=lake_id,
                scene_id=scene_id,
                acquisition_date=acquisition_date,
                water_area_km2=water_area_km2,
                cloud_cover=cloud_cover,
                source=source,
                created_at=datetime.utcnow(),
            )
        )


def get_satellite_history(lake_id):
    with engine.connect() as conn:
        rows = conn.execute(
            satellite_history.select()
            .where(satellite_history.c.lake_id == lake_id)
            .order_by(satellite_history.c.acquisition_date.desc())
        ).mappings().all()

    return [dict(row) for row in rows]
