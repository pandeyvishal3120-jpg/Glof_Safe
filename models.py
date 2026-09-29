from sqlalchemy import Column, Integer, String, Float, DateTime
from datetime import datetime

from database import Base


class GlacialLake(Base):
    __tablename__ = "glacial_lakes"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    area_km2 = Column(Float, default=0.0)
    water_level_m = Column(Float, default=0.0)
    risk_level = Column(String, default="Low")


class SensorReading(Base):
    __tablename__ = "sensor_readings"

    id = Column(Integer, primary_key=True, index=True)
    lake_id = Column(Integer, nullable=False)
    water_level = Column(Float, nullable=False)
    seismic_value = Column(Float, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)


class RiskAssessment(Base):
    __tablename__ = "risk_assessments"

    id = Column(Integer, primary_key=True, index=True)
    lake_id = Column(Integer, nullable=False)
    risk_score = Column(Float, nullable=False)
    risk_level = Column(String, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)


class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    lake_id = Column(Integer, nullable=False)
    alert_level = Column(String, nullable=False)
    message = Column(String, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)


class CrowdReport(Base):
    __tablename__ = "crowd_reports"

    id = Column(Integer, primary_key=True, index=True)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    message = Column(String, nullable=False)
    has_photo = Column(Integer, default=0)
    hazard_tags = Column(String, default="")
    severity_score = Column(Float, default=0.0)
    severity_level = Column(String, default="LOW")
    timestamp = Column(DateTime, default=datetime.utcnow)
