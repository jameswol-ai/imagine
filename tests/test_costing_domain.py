from modules.costing.boq import BOQItem, BoQEngine
from modules.costing.escalation import EscalationService
from modules.costing.forex import ForexService
from modules.costing.risk_analysis import RiskAnalysisService


def test_boq_calculates_amounts_and_zero_items() -> None:
    result = BoQEngine().run([BOQItem("Concrete", 10, "m3", 25)])
    assert result["subtotal"] == 250
    assert BoQEngine().run([])["subtotal"] == 0


def test_escalation_compounds() -> None:
    result = EscalationService.escalate_cost(1000, 0.10, 2)
    assert result["future_cost"] == 1210


def test_forex_conversion_uses_selected_rate() -> None:
    result = ForexService.convert_usd(100, "UGX")
    assert result["amount_local"] == 370000


def test_risk_contingency_and_rating() -> None:
    result = RiskAnalysisService.contingency(1000, 0.15)
    assert result["contingency"] == 150
    assert result["recommended_budget"] == 1150
    assert RiskAnalysisService.risk_rating(0.15) == "High"
