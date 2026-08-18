from sqlalchemy import Column, String, Float, Integer, JSON, ForeignKey, Enum
from sqlalchemy.orm import relationship
from database.models.base import BaseModel
from sqlalchemy.dialects.postgresql import UUID
import uuid
import enum

class ZoningType(str, enum.Enum):
    RESIDENTIAL = "residential"
    COMMERCIAL = "commercial"
    MIXED = "mixed_use"
    INDUSTRIAL = "industrial"

class ComplianceStatus(str, enum.Enum):
    PASS = "pass"
    WARNING = "warning"
    FAIL = "fail"

class GenerativeDesign(BaseModel):
    __tablename__ = "generative_designs"
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"))
    name = Column(String)
    iterations = Column(Integer)
    objective = Column(String)
    population = Column(Integer)
    results = Column(JSON)  # store generated options

class Zoning(BaseModel):
    __tablename__ = "zonings"
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"))
    zone_type = Column(Enum(ZoningType))
    max_height = Column(Float)
    coverage = Column(Float)
    setback = Column(Float)
    description = Column(String)

class SitePlan(BaseModel):
    __tablename__ = "site_plans"
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"))
    area = Column(Float)
    slope = Column(Float)
    soil_type = Column(String)
    orientation = Column(String)
    layout_data = Column(JSON)  # store coordinates, shapes

class FloorPlan(BaseModel):
    __tablename__ = "floor_plans"
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"))
    building_type = Column(String)
    floors = Column(Integer)
    plan_data = Column(JSON)

class RoomProgram(BaseModel):
    __tablename__ = "room_programs"
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"))
    room_name = Column(String)
    area = Column(Float)
    quantity = Column(Integer)
    adjacency = Column(String)

class ComplianceCheck(BaseModel):
    __tablename__ = "compliance_checks"
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"))
    code = Column(String)  # e.g., "Uganda National Building Code"
    rule = Column(String)
    required = Column(String)
    actual = Column(String)
    status = Column(Enum(ComplianceStatus))
    comments = Column(String)