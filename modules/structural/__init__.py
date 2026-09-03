"""Structural calculation package.

UI modules can import these deterministic engines without depending on
Streamlit. All calculations are preliminary screening tools unless explicitly
validated for a project's adopted design standards and National Annex.
"""

from modules.structural.ec3 import BoltGroup, SteelSection, bolt_shear_resistance_kn, preliminary_slenderness
from modules.structural.ec7 import Soil, bearing_utilisation, rankine_active_coefficient, ultimate_bearing_capacity_kpa
from modules.structural.ec8 import SeismicInput, base_shear_kn, distribute_storey_forces_kn
from modules.structural.fea_engine import BeamAnalysisResult, SimplySupportedBeamInput, analyse_simply_supported_beam
from modules.structural.punching_engine import PunchingShearInput, PunchingShearResult, verify_punching_shear
from modules.structural.rc_foundation import PadFootingInput, PadFootingResult, RCPadFootingDesignEngine
from modules.structural.rc_slab import RCSLabDesignEngine, SlabDesignInput, SlabDesignResult

__all__ = [
    "BoltGroup", "SteelSection", "bolt_shear_resistance_kn", "preliminary_slenderness",
    "Soil", "bearing_utilisation", "rankine_active_coefficient", "ultimate_bearing_capacity_kpa",
    "SeismicInput", "base_shear_kn", "distribute_storey_forces_kn",
    "BeamAnalysisResult", "SimplySupportedBeamInput", "analyse_simply_supported_beam",
    "PunchingShearInput", "PunchingShearResult", "verify_punching_shear",
    "PadFootingInput", "PadFootingResult", "RCPadFootingDesignEngine",
    "RCSLabDesignEngine", "SlabDesignInput", "SlabDesignResult",
]
