"""Persistent BIM domain models for the IMAGINE platform."""
from __future__ import annotations

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, JSON, String
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID

from database.models.base import BaseModel


class Building(BaseModel):
    __tablename__ = "buildings"

    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False, index=True)
    code = Column(String, nullable=True, index=True)
    name = Column(String, nullable=False)
    storeys = Column(Integer, default=0)
    area = Column(Float, default=0.0)
    height = Column(Float, default=0.0)
    typology = Column(String, nullable=True)
    status = Column(String, default="Concept Design")
    ifc_version = Column(String, default="IFC4")
    description = Column(String, nullable=True)

    storeys_rel = relationship("Storey", back_populates="building", cascade="all, delete-orphan")
    spaces = relationship("Space", back_populates="building", cascade="all, delete-orphan")
    elements = relationship("Element", back_populates="building", cascade="all, delete-orphan")


class Storey(BaseModel):
    __tablename__ = "storeys"

    building_id = Column(UUID(as_uuid=True), ForeignKey("buildings.id"), nullable=False, index=True)
    code = Column(String, nullable=True, index=True)
    level = Column(String, nullable=False)
    elevation = Column(Float, default=0.0)
    height = Column(Float, default=0.0)
    area = Column(Float, default=0.0)
    description = Column(String, nullable=True)

    building = relationship("Building", back_populates="storeys_rel")
    spaces = relationship("Space", back_populates="storey", cascade="all, delete-orphan")
    elements = relationship("Element", back_populates="storey", cascade="all, delete-orphan")


class Space(BaseModel):
    __tablename__ = "spaces"

    building_id = Column(UUID(as_uuid=True), ForeignKey("buildings.id"), nullable=False, index=True)
    storey_id = Column(UUID(as_uuid=True), ForeignKey("storeys.id"), nullable=False, index=True)
    code = Column(String, nullable=True, index=True)
    name = Column(String, nullable=False)
    area = Column(Float, default=0.0)
    height = Column(Float, default=0.0)
    space_type = Column(String, nullable=True)
    capacity = Column(Integer, default=0)

    building = relationship("Building", back_populates="spaces")
    storey = relationship("Storey", back_populates="spaces")


class Element(BaseModel):
    __tablename__ = "elements"

    building_id = Column(UUID(as_uuid=True), ForeignKey("buildings.id"), nullable=False, index=True)
    storey_id = Column(UUID(as_uuid=True), ForeignKey("storeys.id"), nullable=True, index=True)
    code = Column(String, nullable=True, index=True)
    name = Column(String, nullable=False)
    material = Column(String, nullable=True)
    quantity = Column(Float, default=1.0)
    unit = Column(String, default="item")
    element_type = Column(String, nullable=True)
    type_name = Column(String, nullable=True)
    status = Column(String, default="Design")
    guid = Column(String, nullable=True, unique=True, index=True)

    building = relationship("Building", back_populates="elements")
    storey = relationship("Storey", back_populates="elements")


class IfcModel(BaseModel):
    __tablename__ = "ifc_models"

    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False, index=True)
    filename = Column(String, nullable=False)
    version = Column(String, default="IFC4")
    file_path = Column(String, nullable=True)
    upload_date = Column(DateTime, nullable=True)


class CobieAsset(BaseModel):
    __tablename__ = "cobie_assets"

    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False, index=True)
    asset_name = Column(String, nullable=False)
    serial_number = Column(String, nullable=True)
    manufacturer = Column(String, nullable=True)
    warranty_years = Column(Integer, nullable=True)
    installation_date = Column(DateTime, nullable=True)


class DigitalTwin(BaseModel):
    __tablename__ = "digital_twins"

    building_id = Column(UUID(as_uuid=True), ForeignKey("buildings.id"), nullable=False, index=True)
    sensor_data = Column(JSON, default=dict)
    energy_usage = Column(Float, default=0.0)
    occupancy = Column(Integer, default=0)
    temperature = Column(Float, nullable=True)
    humidity = Column(Float, nullable=True)
    last_updated = Column(DateTime, nullable=True)
