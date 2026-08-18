from sqlalchemy import Column, String, Float, Integer, JSON, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from database.models.base import BaseModel
from sqlalchemy.dialects.postgresql import UUID
import uuid

class Building(BaseModel):
    __tablename__ = "buildings"
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"))
    name = Column(String)
    storeys = Column(Integer)
    area = Column(Float)
    ifc_version = Column(String)
    description = Column(String)

    storeys_rel = relationship("Storey", back_populates="building")
    spaces = relationship("Space", back_populates="building")
    elements = relationship("Element", back_populates="building")

class Storey(BaseModel):
    __tablename__ = "storeys"
    building_id = Column(UUID(as_uuid=True), ForeignKey("buildings.id"))
    level = Column(String)
    height = Column(Float)
    area = Column(Float)

    building = relationship("Building", back_populates="storeys_rel")
    spaces = relationship("Space", back_populates="storey")

class Space(BaseModel):
    __tablename__ = "spaces"
    building_id = Column(UUID(as_uuid=True), ForeignKey("buildings.id"))
    storey_id = Column(UUID(as_uuid=True), ForeignKey("storeys.id"))
    name = Column(String)
    area = Column(Float)
    height = Column(Float)
    space_type = Column(String)  # office, conference, etc.

    building = relationship("Building", back_populates="spaces")
    storey = relationship("Storey", back_populates="spaces")

class Element(BaseModel):
    __tablename__ = "elements"
    building_id = Column(UUID(as_uuid=True), ForeignKey("buildings.id"))
    name = Column(String)
    material = Column(String)
    quantity = Column(Float)
    unit = Column(String)
    element_type = Column(String)  # wall, slab, column, etc.

    building = relationship("Building", back_populates="elements")

class IfcModel(BaseModel):
    __tablename__ = "ifc_models"
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"))
    filename = Column(String)
    version = Column(String)
    file_path = Column(String)
    upload_date = Column(DateTime)

class CobieAsset(BaseModel):
    __tablename__ = "cobie_assets"
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"))
    asset_name = Column(String)
    serial_number = Column(String)
    manufacturer = Column(String)
    warranty_years = Column(Integer)
    installation_date = Column(DateTime)

class DigitalTwin(BaseModel):
    __tablename__ = "digital_twins"
    building_id = Column(UUID(as_uuid=True), ForeignKey("buildings.id"))
    sensor_data = Column(JSON)  # live telemetry
    energy_usage = Column(Float)
    occupancy = Column(Integer)
    temperature = Column(Float)
    humidity = Column(Float)
    last_updated = Column(DateTime)