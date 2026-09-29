from database import SessionLocal, engine
from models import Base, GlacialLake


sample_lakes = [
    {
        "name": "Lake Alpha",
        "latitude": 30.4200,
        "longitude": 79.9000,
        "area_km2": 1.20,
        "water_level_m": 42.5,
        "risk_level": "Low",
    },
    {
        "name": "Lake Beta",
        "latitude": 30.5100,
        "longitude": 80.1200,
        "area_km2": 2.80,
        "water_level_m": 56.3,
        "risk_level": "Medium",
    },
    {
        "name": "Lake Gamma",
        "latitude": 30.6500,
        "longitude": 80.3500,
        "area_km2": 4.50,
        "water_level_m": 71.8,
        "risk_level": "High",
    },
    {
        "name": "Lake Delta",
        "latitude": 30.7800,
        "longitude": 80.5000,
        "area_km2": 6.20,
        "water_level_m": 89.4,
        "risk_level": "Critical",
    },
]


def seed_database():
    # Create all database tables first
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()

    try:
        existing_count = db.query(GlacialLake).count()

        if existing_count > 0:
            print("Database already contains lake data.")
            return

        for lake_data in sample_lakes:
            lake = GlacialLake(**lake_data)
            db.add(lake)

        db.commit()

        print(f"{len(sample_lakes)} sample lakes added successfully.")

    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
