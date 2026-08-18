from sqlalchemy import Column, String, Float, Integer, ForeignKey, Enum, JSON
from database.models.base import BaseModel
from sqlalchemy.dialects.postgresql import UUID
import enum

class EurocodePart(str, enum.Enum):
    EN1990 = "en1990"
    EN1991 = "en1991"
    EN1992 = "en1992"
    EN1993 = "en1993"
    EN1995 = "en1995"
    EN1997 = "en1997"
    EN1998 = "en1998"

class BeamDesign(BaseModel):
    __tablename__ = "beam_designs"
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"))
    beam_id = Column(String)
    span = Column(Float)
    load = Column(Float)
    material = Column(String)
    status = Column(String)  # OK, Overstressed, etc.
    design_data = Column(JSON)

class ColumnDesign(BaseModel):
    __tablename__ = "column_designs"
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"))
    column_id = Column(String)
    axial_load = Column(Float)
    section = Column(String)
    reinforcement_ratio = Column(Float)
    design_data = Column(JSON)

class SlabDesign(BaseModel):
    __tablename__ = "slab_designs"
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"))
    slab_id = Column(String)
    thickness = Column(Float)
    span = Column(Float)
    load = Column(Float)
    design_data = Column(JSON)

class FoundationDesign(BaseModel):
    __tablename__ = "foundation_designs"
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"))
    foundation_type = Column(String)  # pad, strip, pile
    capacity = Column(Float)
    depth = Column(Float)
    design_data = Column(JSON)

class RetainingWall(BaseModel):
    __tablename__ = "retaining_walls"
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"))
    wall_id = Column(String)
    height = Column(Float)
    thickness = Column(Float)
    stability = Column(String)

class SteelConnection(BaseModel):
    __tablename__ = "steel_connections"
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"))
    connection_type = Column(String)  # moment, shear, base plate
    bolts = Column(String)
    capacity = Column(Float)
    design_data = Column(JSON)

class FEAnalysis(BaseModel):
    __tablename__ = "fe_analyses"
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"))
    analysis_type = Column(String)  # linear, nonlinear, modal, pushover
    results = Column(JSON)
    status = Column(String)

class EurocodeModel(BaseModel):
    __tablename__ = "eurocodes"
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"))
    part = Column(Enum(EurocodePart))
    parameters = Column(JSON)  # store specific load combos, factors