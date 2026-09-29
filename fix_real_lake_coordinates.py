import json

from pyproj import Transformer

from database import SessionLocal
from models import GlacialLake


SOURCE = "data/lakes/glacial_lake.geojson"

transformer = Transformer.from_crs(
    "EPSG:7755",
    "EPSG:4326",
    always_xy=True
)


def fix_coordinates():
    with open(SOURCE, "r", encoding="utf-8") as f:
        data = json.load(f)

    db = SessionLocal()

    updated = 0
    skipped = 0

    try:
        features = data.get("features", [])

        db_lakes = db.query(GlacialLake).order_by(
            GlacialLake.id
        ).all()

        if len(db_lakes) != len(features):
            raise RuntimeError(
                f"Database lakes ({len(db_lakes)}) != "
                f"GeoJSON features ({len(features)})"
            )

        for db_lake, feature in zip(db_lakes, features):
            geometry = feature.get("geometry")

            if not geometry:
                skipped += 1
                continue

            coords = []

            def collect_points(obj):
                if (
                    isinstance(obj, list)
                    and len(obj) >= 2
                    and isinstance(obj[0], (int, float))
                    and isinstance(obj[1], (int, float))
                ):
                    coords.append((float(obj[0]), float(obj[1])))
                    return

                if isinstance(obj, list):
                    for item in obj:
                        collect_points(item)

            collect_points(geometry.get("coordinates", []))

            if not coords:
                skipped += 1
                continue

            x = sum(p[0] for p in coords) / len(coords)
            y = sum(p[1] for p in coords) / len(coords)

            longitude, latitude = transformer.transform(x, y)

            db_lake.latitude = latitude
            db_lake.longitude = longitude

            updated += 1

        db.commit()

        print("COORDINATE FIX COMPLETE")
        print("Updated:", updated)
        print("Skipped:", skipped)

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


if __name__ == "__main__":
    fix_coordinates()
