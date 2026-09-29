import json
from pathlib import Path

from shapely.geometry import shape

from database import SessionLocal
from models import GlacialLake


SOURCE = Path("data/lakes/glacial_lake.geojson")


def load_real_lakes():
    with open(SOURCE, "r", encoding="utf-8") as f:
        data = json.load(f)

    features = data.get("features", [])

    lakes = []

    for feature in features:
        props = feature.get("properties", {})
        geometry = feature.get("geometry")

        if not geometry:
            continue

        official_id = str(props.get("lake_id") or "").strip()

        if not official_id:
            continue

        lake_name = str(props.get("name") or "").strip()

        if not lake_name:
            lake_name = f"Glacial Lake {official_id}"

        area_ha = float(props.get("wsa_ha") or 0)
        area_km2 = area_ha / 100.0

        geom = shape(geometry)
        centroid = geom.centroid

        lakes.append(
            GlacialLake(
                name=lake_name,
                latitude=float(centroid.y),
                longitude=float(centroid.x),
                area_km2=area_km2,
                water_level_m=0.0,
                risk_level="Low"
            )
        )

    db = SessionLocal()

    try:
        db.query(GlacialLake).delete()

        db.add_all(lakes)
        db.commit()

        print("REAL LAKE IMPORT COMPLETE")
        print("Imported lakes:", len(lakes))

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


if __name__ == "__main__":
    load_real_lakes()
