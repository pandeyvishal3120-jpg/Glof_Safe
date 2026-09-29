import requests
from datetime import datetime, timedelta, timezone
from sqlalchemy import Table, Column, Integer, String, Float, DateTime, MetaData, Text
from database import engine, SessionLocal
from models import GlacialLake

STAC_URL = "https://stac.dataspace.copernicus.eu/v1/search"

metadata = MetaData()

satellite_observations = Table(
    "satellite_observations",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("lake_id", Integer, nullable=False),
    Column("product_id", String),
    Column("acquisition_date", DateTime),
    Column("cloud_cover", Float),
    Column("platform", String),
    Column("collection", String),
    Column("thumbnail_url", Text),
    Column("product_url", Text),
    Column("created_at", DateTime, default=datetime.utcnow),
)

metadata.create_all(engine)


def search_sentinel2(lat, lon):
    now = datetime.now(timezone.utc)
    start = now - timedelta(days=180)

    delta = 0.08

    payload = {
        "collections": ["sentinel-2-l2a"],
        "bbox": [
            lon - delta,
            lat - delta,
            lon + delta,
            lat + delta,
        ],
        "datetime": (
            start.strftime("%Y-%m-%dT%H:%M:%SZ")
            + "/"
            + now.strftime("%Y-%m-%dT%H:%M:%SZ")
        ),
        "limit": 20,
        "query": {
            "eo:cloud_cover": {
                "lte": 30
            }
        },
        "sortby": [
            {
                "field": "datetime",
                "direction": "desc"
            }
        ]
    }

    response = requests.post(
        STAC_URL,
        json=payload,
        timeout=60
    )

    response.raise_for_status()

    data = response.json()
    features = data.get("features", [])

    if not features:
        return None

    item = features[0]
    props = item.get("properties", {})
    assets = item.get("assets", {})

    thumbnail = None

    if "thumbnail" in assets:
        thumbnail = assets["thumbnail"].get("href")

    product_url = None

    if "product" in assets:
        product_url = assets["product"].get("href")

    acquisition = props.get("datetime")

    if acquisition:
        acquisition_dt = datetime.fromisoformat(
            acquisition.replace("Z", "+00:00")
        ).replace(tzinfo=None)
    else:
        acquisition_dt = None

    return {
        "product_id": item.get("id"),
        "acquisition_date": acquisition_dt,
        "cloud_cover": props.get("eo:cloud_cover"),
        "platform": props.get("platform"),
        "collection": item.get("collection"),
        "thumbnail_url": thumbnail,
        "product_url": product_url,
    }


def save_observation(lake_id, observation):
    if not observation:
        return None

    with engine.begin() as conn:
        conn.execute(
            satellite_observations.insert().values(
                lake_id=lake_id,
                product_id=observation["product_id"],
                acquisition_date=observation["acquisition_date"],
                cloud_cover=observation["cloud_cover"],
                platform=observation["platform"],
                collection=observation["collection"],
                thumbnail_url=observation["thumbnail_url"],
                product_url=observation["product_url"],
                created_at=datetime.utcnow(),
            )
        )

    return observation


def get_all_satellite_observations():
    lakes = SessionLocal().query(GlacialLake).all()

    results = []

    for lake in lakes:
        try:
            observation = search_sentinel2(
                lake.latitude,
                lake.longitude
            )

            if observation:
                save_observation(lake.id, observation)

                results.append({
                    "lake_id": lake.id,
                    "lake_name": lake.name,
                    "latitude": lake.latitude,
                    "longitude": lake.longitude,
                    **observation,
                })

            else:
                results.append({
                    "lake_id": lake.id,
                    "lake_name": lake.name,
                    "latitude": lake.latitude,
                    "longitude": lake.longitude,
                    "status": "NO_RECENT_SATELLITE_OBSERVATION"
                })

        except Exception as error:
            results.append({
                "lake_id": lake.id,
                "lake_name": lake.name,
                "latitude": lake.latitude,
                "longitude": lake.longitude,
                "status": "ERROR",
                "error": str(error),
            })

    return results
