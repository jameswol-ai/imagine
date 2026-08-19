"""
Tests for the Site Planning Streamlit registry adapter.

These tests verify the zero-argument Site Planning renderer
contract used by the IMAGINE application shell.

The tests intentionally exercise Python's real import mechanism
instead of patching already-imported module attributes.

The import-failure test specifically verifies that:

    architecture.site_planning.repository

is the only blocked import.

The service and UI imports are allowed to continue through
Python's normal import mechanism.

The tests also verify the exact Streamlit error and traceback
behavior exposed by the application shell.
"""

from __future__ import annotations

import builtins
import inspect
from unittest.mock import MagicMock, patch

import pytest

import streamlit_app


# ============================================================
# CONSTANTS
# ============================================================

SITE_PLANNING_REPOSITORY_MODULE = (
    "architecture.site_planning.repository"
)

SITE_PLANNING_SERVICE_MODULE = (
    "architecture.site_planning.service"
)

SITE_PLANNING_UI_MODULE = (
    "architecture.site_planning.ui"
)

IMPORT_ERROR_MESSAGE = (
    "The Site Planning module could not be loaded."
)

RENDER_ERROR_MESSAGE = (
    "Site Planning could not be rendered."
)


# ============================================================
# HELPERS
# ============================================================


def _mock_streamlit_error_ui() -> tuple[
    MagicMock,
    MagicMock,
    MagicMock,
]:
    """
    Create mocks for the Streamlit error reporting path.

    The adapter uses:

        st.error(...)
        st.expander(...)
        st.exception(...)

    The expander mock behaves as a context manager so the
    production renderer can execute normally.
    """

    error = MagicMock(
        name="streamlit_error"
    )

    expander = MagicMock(
        name="streamlit_expander"
    )

    exception = MagicMock(
        name="streamlit_exception"
    )

    expander_context = MagicMock(
        name="streamlit_expander_context"
    )

    expander_context.__enter__.return_value = (
        expander_context
    )

    expander_context.__exit__.return_value = (
        False
    )

    expander.return_value = expander_context

    return (
        error,
        expander,
        exception,
    )


# ============================================================
# ZERO-ARGUMENT CONTRACT
# ============================================================


def test_render_site_planning_registered_is_zero_argument():
    """
    The Streamlit application shell must be able to call:

        render_site_planning_registered()

    without passing a repository, service, request, or other
    dependency.
    """

    signature = inspect.signature(
        streamlit_app.render_site_planning_registered
    )

    assert list(
        signature.parameters
    ) == []


# ============================================================
# REGISTRY WIRING
# ============================================================


def test_site_planning_registry_uses_zero_argument_adapter():
    """
    Verify that the application registry points Site Planning
    at the zero-argument adapter.

    This test supports both the older dictionary-based registry
    and the newer ModuleDefinition registry shape used during
    the transition.
    """

    if hasattr(
        streamlit_app,
        "MODULES_BY_ROUTE",
    ):

        registry = (
            streamlit_app.MODULES_BY_ROUTE
        )

        # ----------------------------------------------------
        # Older registry shape:
        #
        # {
        #     "site_planning": {
        #         "renderer": ...
        #     }
        # }
        # ----------------------------------------------------

        if "site_planning" in registry:

            module = registry[
                "site_planning"
            ]

            renderer = (
                module.get("renderer")
                if isinstance(
                    module,
                    dict,
                )
                else None
            )

            if renderer is not None:

                assert (
                    renderer
                    is streamlit_app.render_site_planning_registered
                )

                return

        # ----------------------------------------------------
        # Newer registry shape:
        #
        # "architecture_site_planning"
        # ----------------------------------------------------

        if (
            "architecture_site_planning"
            in registry
        ):

            module = registry[
                "architecture_site_planning"
            ]

            special_renderers = getattr(
                streamlit_app,
                "SPECIAL_RENDERERS",
                {},
            )

            if (
                "architecture_site_planning"
                in special_renderers
            ):

                assert (
                    special_renderers[
                        "architecture_site_planning"
                    ]
                    is streamlit_app.render_site_planning_registered
                )

                return

            # If the module itself exposes a
            # renderer property, validate it.
            renderer = getattr(
                module,
                "renderer",
                None,
            )

            if renderer is not None:

                assert (
                    renderer
                    is streamlit_app.render_site_planning_registered
                )

                return

    pytest.fail(
        "Could not find Site Planning registry wiring."
    )


# ============================================================
# IMPORT FAILURE
# ============================================================


def test_site_planning_repository_import_failure_is_handled():
    """
    Verify the Site Planning import-failure path.

    The test intercepts Python's actual __import__ mechanism.

    Only:

        architecture.site_planning.repository

    is blocked.

    No module attribute is patched.

    This is important because patching:

        architecture.site_planning.repository.SitePlanningRepository

    would not test the real import statement used by the
    application shell.
    """

    original_import = builtins.__import__

    attempted_imports: list[str] = []

    repository_error = ModuleNotFoundError(
        "No module named "
        "'architecture.site_planning.repository'"
    )

    def controlled_import(
        name,
        globals=None,
        locals=None,
        fromlist=(),
        level=0,
    ):
        """
        Intercept Python package/module imports.

        The repository module is the only module deliberately
        blocked.

        Everything else is delegated to Python's original
        import implementation.
        """

        attempted_imports.append(
            name
        )

        if name == SITE_PLANNING_REPOSITORY_MODULE:

            raise repository_error

        return original_import(
            name,
            globals,
            locals,
            fromlist,
            level,
        )

    (
        st_error,
        st_expander,
        st_exception,
    ) = _mock_streamlit_error_ui()

    with (
        patch(
            "builtins.__import__",
            side_effect=controlled_import,
        ),
        patch.object(
            streamlit_app.st,
            "error",
            st_error,
        ),
        patch.object(
            streamlit_app.st,
            "expander",
            st_expander,
        ),
        patch.object(
            streamlit_app.st,
            "exception",
            st_exception,
        ),
    ):

        streamlit_app.render_site_planning_registered()

    # --------------------------------------------------------
    # The repository import must have been attempted.
    # --------------------------------------------------------

    assert (
        SITE_PLANNING_REPOSITORY_MODULE
        in attempted_imports
    )

    # --------------------------------------------------------
    # The exact Streamlit import error must be displayed.
    # --------------------------------------------------------

    st_error.assert_called_once_with(
        IMPORT_ERROR_MESSAGE
    )

    # --------------------------------------------------------
    # The traceback expander must be created.
    # --------------------------------------------------------

    st_expander.assert_called_once_with(
        "Complete import traceback",
        expanded=True,
    )

    # --------------------------------------------------------
    # The actual exception must be passed to Streamlit.
    # --------------------------------------------------------

    st_exception.assert_called_once_with(
        repository_error
    )


# ============================================================
# IMPORT FAILURE MUST NOT BREAK APPLICATION SHELL
# ============================================================


def test_site_planning_repository_import_failure_returns_cleanly():
    """
    A Site Planning repository import failure must be isolated
    to Site Planning.

    The adapter must return instead of propagating the import
    exception into the application shell.
    """

    original_import = builtins.__import__

    def controlled_import(
        name,
        globals=None,
        locals=None,
        fromlist=(),
        level=0,
    ):
        if name == SITE_PLANNING_REPOSITORY_MODULE:

            raise ModuleNotFoundError(
                "No module named "
                "'architecture.site_planning.repository'"
            )

        return original_import(
            name,
            globals,
            locals,
            fromlist,
            level,
        )

    (
        st_error,
        st_expander,
        st_exception,
    ) = _mock_streamlit_error_ui()

    with (
        patch(
            "builtins.__import__",
            side_effect=controlled_import,
        ),
        patch.object(
            streamlit_app.st,
            "error",
            st_error,
        ),
        patch.object(
            streamlit_app.st,
            "expander",
            st_expander,
        ),
        patch.object(
            streamlit_app.st,
            "exception",
            st_exception,
        ),
    ):

        result = (
            streamlit_app
            .render_site_planning_registered()
        )

    # --------------------------------------------------------
    # The renderer must terminate normally.
    # --------------------------------------------------------

    assert result is None

    st_error.assert_called_once_with(
        IMPORT_ERROR_MESSAGE
    )

    st_expander.assert_called_once()

    st_exception.assert_called_once()


# ============================================================
# ONLY REPOSITORY IMPORT IS BLOCKED
# ============================================================


def test_repository_is_only_blocked_import():
    """
    Verify that the import hook blocks exactly the repository
    module and delegates every other import to Python's real
    import mechanism.

    This specifically protects against an overly broad import
    interceptor such as:

        if name.startswith("architecture.site_planning"):
            raise ...

    which would incorrectly block service and UI imports too.
    """

    original_import = builtins.__import__

    attempted_imports: list[str] = []

    def controlled_import(
        name,
        globals=None,
        locals=None,
        fromlist=(),
        level=0,
    ):
        attempted_imports.append(
            name
        )

        if name == SITE_PLANNING_REPOSITORY_MODULE:

            raise ModuleNotFoundError(
                "repository intentionally blocked"
            )

        return original_import(
            name,
            globals,
            locals,
            fromlist,
            level,
        )

    try:

        with patch(
            "builtins.__import__",
            side_effect=controlled_import,
        ):

            try:

                __import__(
                    SITE_PLANNING_REPOSITORY_MODULE,
                    fromlist=[
                        "SitePlanningRepository"
                    ],
                )

            except ModuleNotFoundError:
                pass

            # ------------------------------------------------
            # These must continue through the real importer.
            # ------------------------------------------------

            service_module = __import__(
                SITE_PLANNING_SERVICE_MODULE,
                fromlist=[
                    "SitePlanningService"
                ],
            )

            ui_module = __import__(
                SITE_PLANNING_UI_MODULE,
                fromlist=[
                    "render_site_planning"
                ],
            )

    finally:

        # Nothing required here. The patch context restores
        # Python's import implementation.
        pass

    # --------------------------------------------------------
    # Repository import was blocked.
    # --------------------------------------------------------

    assert (
        SITE_PLANNING_REPOSITORY_MODULE
        in attempted_imports
    )

    # --------------------------------------------------------
    # Service import reached the real importer.
    # --------------------------------------------------------

    assert (
        SITE_PLANNING_SERVICE_MODULE
        in attempted_imports
    )

    assert hasattr(
        service_module,
        "SitePlanningService",
    )

    # --------------------------------------------------------
    # UI import reached the real importer.
    # --------------------------------------------------------

    assert (
        SITE_PLANNING_UI_MODULE
        in attempted_imports
    )

    assert hasattr(
        ui_module,
        "render_site_planning",
    )


# ============================================================
# SERVICE AND UI USE REAL IMPORT MECHANISM
# ============================================================


def test_service_and_ui_imports_are_not_attribute_patched():
    """
    Verify that the service and UI modules are imported normally.

    This deliberately avoids patching:

        architecture.site_planning.service.SitePlanningService

    or:

        architecture.site_planning.ui.render_site_planning

    The purpose is to ensure that the import path itself remains
    valid.
    """

    original_import = builtins.__import__

    imports: list[str] = []

    def tracking_import(
        name,
        globals=None,
        locals=None,
        fromlist=(),
        level=0,
    ):
        imports.append(
            name
        )

        return original_import(
            name,
            globals,
            locals,
            fromlist,
            level,
        )

    with patch(
        "builtins.__import__",
        side_effect=tracking_import,
    ):

        service_module = __import__(
            SITE_PLANNING_SERVICE_MODULE,
            fromlist=[
                "SitePlanningService"
            ],
        )

        ui_module = __import__(
            SITE_PLANNING_UI_MODULE,
            fromlist=[
                "render_site_planning"
            ],
        )

    assert (
        SITE_PLANNING_SERVICE_MODULE
        in imports
    )

    assert (
        SITE_PLANNING_UI_MODULE
        in imports
    )

    assert callable(
        getattr(
            service_module,
            "SitePlanningService",
        )
    )

    assert callable(
        getattr(
            ui_module,
            "render_site_planning",
        )
    )


# ============================================================
# RENDERER FAILURE
# ============================================================


def test_site_planning_renderer_failure_is_handled_by_shell():
    """
    Verify the application shell's renderer-level error path.

    The Site Planning UI import itself is allowed to use the real
    import mechanism.

    Only the imported renderer function is replaced at the
    streamlit_app boundary for this specific failure test.
    """

    renderer_error = RuntimeError(
        "site planning renderer failed"
    )

    (
        st_error,
        st_expander,
        st_exception,
    ) = _mock_streamlit_error_ui()

    def failing_renderer():
        raise renderer_error

    with (
        patch(
            "architecture.site_planning.ui.render_site_planning",
            side_effect=failing_renderer,
        ),
        patch.object(
            streamlit_app.st,
            "error",
            st_error,
        ),
        patch.object(
            streamlit_app.st,
            "expander",
            st_expander,
        ),
        patch.object(
            streamlit_app.st,
            "exception",
            st_exception,
        ),
    ):

        streamlit_app.render_site_planning_registered()

    st_error.assert_called_once_with(
        RENDER_ERROR_MESSAGE
    )

    st_expander.assert_called_once_with(
        "Complete renderer traceback",
        expanded=True,
    )

    st_exception.assert_called_once_with(
        renderer_error
    )


# ============================================================
# RENDERER FAILURE DOES NOT PROPAGATE
# ============================================================


def test_renderer_failure_does_not_break_application_shell():
    """
    The Streamlit adapter must contain renderer exceptions.

    A renderer failure should result in the Streamlit error UI
    rather than raising into the application shell.
    """

    renderer_error = RuntimeError(
        "renderer exploded"
    )

    (
        st_error,
        st_expander,
        st_exception,
    ) = _mock_streamlit_error_ui()

    with (
        patch(
            "architecture.site_planning.ui.render_site_planning",
            side_effect=renderer_error,
        ),
        patch.object(
            streamlit_app.st,
            "error",
            st_error,
        ),
        patch.object(
            streamlit_app.st,
            "expander",
            st_expander,
        ),
        patch.object(
            streamlit_app.st,
            "exception",
            st_exception,
        ),
    ):

        # ----------------------------------------------------
        # This must NOT raise.
        # ----------------------------------------------------

        result = (
            streamlit_app
            .render_site_planning_registered()
        )

    assert result is None

    st_error.assert_called_once_with(
        RENDER_ERROR_MESSAGE
    )

    st_exception.assert_called_once_with(
        renderer_error
    )


# ============================================================
# ROUTE REACHABILITY
# ============================================================


def test_render_route_reaches_site_planning_adapter():
    """
    Verify that the application shell routes:

        architecture_site_planning

    into the zero-argument Site Planning adapter.

    This test does not execute the real Site Planning renderer.
    """

    adapter = MagicMock(
        name="site_planning_adapter"
    )

    with patch.object(
        streamlit_app,
        "render_site_planning_registered",
        adapter,
    ):

        streamlit_app.render_route(
            "architecture_site_planning"
        )

    adapter.assert_called_once_with()


# ============================================================
# ROUTE DOES NOT PASS SERVICE ARGUMENTS
# ============================================================


def test_render_route_calls_site_planning_with_zero_arguments():
    """
    The application route must call the adapter as:

        render_site_planning_registered()

    and never as:

        render_site_planning_registered(service)

    This protects the registry/controller contract.
    """

    received_arguments: list[tuple] = []

    def adapter(*args, **kwargs):
        received_arguments.append(
            (
                args,
                kwargs,
            )
        )

    with patch.object(
        streamlit_app,
        "render_site_planning_registered",
        side_effect=adapter,
    ):

        streamlit_app.render_route(
            "architecture_site_planning"
        )

    assert received_arguments == [
        (
            (),
            {},
        )
    ]


# ============================================================
# SUMMARY
# ============================================================


def test_site_planning_adapter_contract_summary():
    """
    High-level contract test documenting the intended design.

    The application shell owns:

        route
            ↓
        zero-argument adapter

    The Site Planning module owns:

        UI
            ↓
        synchronous service adapter
            ↓
        async service/repository layer
    """

    signature = inspect.signature(
        streamlit_app.render_site_planning_registered
    )

    assert list(
        signature.parameters
    ) == []

    assert callable(
        streamlit_app.render_site_planning_registered
    )

    assert callable(
        streamlit_app.render_route
    )