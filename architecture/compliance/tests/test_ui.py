from unittest.mock import MagicMock, patch

from architecture.compliance import ui


def test_render_function_exists():
    assert callable(ui.render)


def test_render_compliance_function_exists():
    assert callable(ui.render_compliance)


def test_ui_uses_session_local_database():
    assert hasattr(ui, "_get_db")


@patch("architecture.compliance.ui.SessionLocal")
def test_get_db(mock_session_local):
    expected = MagicMock()

    mock_session_local.return_value = expected

    result = ui._get_db()

    assert result is expected
    mock_session_local.assert_called_once()