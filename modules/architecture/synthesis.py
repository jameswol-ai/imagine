"""
IMAGINE Platform — Architecture Synthesis Engine
Path: modules/architecture/synthesis.py
App: imagine
"""

from typing import Any, Dict, List

# Explicit top-level constant export
STATE_KEY: str = "architecture_layouts"


class ArchitectureSynthesisEngine:
    """Generative layout generator and parametric architectural massing solver."""

    @staticmethod
    def synthesize_program(
        site_width: float,
        site_length: float,
        total_floors: int,
        target_far: float,
        building_typology: str,
    ) -> Dict[str, Any]:
        """Generates spatial zoning, room allocation, FAR utilization, and massing envelope."""
        try:
            site_area = site_width * site_length
            max_allowable_gfa = site_area * target_far
            footprint_area = site_area * 0.55
            total_gfa = min(footprint_area * total_floors, max_allowable_gfa)
            achieved_far = total_gfa / site_area if site_area > 0 else 0.0

            distributions = {
                "Residential": {"Living/Dining": 0.40, "Bedrooms": 0.30, "Circulation": 0.15, "Services/Wet": 0.15},
                "Commercial Office": {"Open Workspaces": 0.55, "Meeting Rooms": 0.15, "Circulation/Core": 0.18, "Amenities": 0.12},
                "Mixed-Use": {"Retail/Public": 0.25, "Office": 0.35, "Residential": 0.25, "Circulation/Core": 0.15},
                "Educational": {"Classrooms": 0.50, "Labs/Workshops": 0.20, "Circulation": 0.18, "Admin/Services": 0.12},
            }

            program_ratios = distributions.get(building_typology, distributions["Commercial Office"])
            spatial_program = [
                {
                    "zone": zone,
                    "target_ratio": ratio,
                    "allocated_area_m2": round(total_gfa * ratio, 2),
                }
                for zone, ratio in program_ratios.items()
            ]

            allocated_spaces = ArchitectureSynthesisEngine._layout_zones_grid(
                site_width=site_width,
                site_length=site_length,
                program_ratios=program_ratios,
            )

            return {
                "success": True,
                "site_area_m2": round(site_area, 2),
                "total_gfa_m2": round(total_gfa, 2),
                "achieved_far": round(achieved_far, 2),
                "footprint_area_m2": round(footprint_area, 2),
                "spatial_program": spatial_program,
                "layout_boxes": allocated_spaces,
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Synthesis pipeline failure: {str(e)}",
            }

    @staticmethod
    def _layout_zones_grid(
        site_width: float, site_length: float, program_ratios: Dict[str, float]
    ) -> List[Dict[str, Any]]:
        boxes = []
        curr_y = 0.0
        padding = 1.0
        usable_w = site_width - (2 * padding)
        usable_l = site_length - (2 * padding)

        for zone_name, ratio in program_ratios.items():
            zone_length = usable_l * ratio
            boxes.append(
                {
                    "zone": zone_name,
                    "x0": round(padding, 2),
                    "y0": round(curr_y + padding, 2),
                    "x1": round(padding + usable_w, 2),
                    "y1": round(curr_y + padding + zone_length, 2),
                    "area_m2": round(usable_w * zone_length, 2),
                }
            )
            curr_y += zone_length

        return boxes

