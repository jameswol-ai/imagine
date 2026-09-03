"""IMAGINE Streamlit module package."""

from modules.ui_sanitizer import install_emoji_free_ui

install_emoji_free_ui()

# Preload and normalize the enterprise registry before streamlit_app imports it.
# Specialist renderers remain untouched. Routes without a specialist renderer
# receive the shared persistent workspace so no registered route is dead.
from modules import enterprise_registry as _enterprise_registry
from modules.enterprise_registry import ModuleSpec


_NORMALIZED_SPECS = []
for _spec in _enterprise_registry.MODULE_SPECS:
    if _spec.implemented and _spec.module_path:
        _NORMALIZED_SPECS.append(_spec)
    else:
        _NORMALIZED_SPECS.append(
            ModuleSpec(
                route=_spec.route,
                label=_spec.label,
                section=_spec.section,
                module_path="modules.enterprise_runtime",
                renderer_name="render_module",
                implemented=True,
            )
        )

_enterprise_registry.MODULE_SPECS = tuple(_NORMALIZED_SPECS)
_enterprise_registry.MODULES_BY_ROUTE = {
    spec.route: spec for spec in _enterprise_registry.MODULE_SPECS
}

__all__ = ["install_emoji_free_ui"]
