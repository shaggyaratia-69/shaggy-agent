from pathlib import Path

import yaml


REPO = Path(__file__).resolve().parents[1]
SKILLS = REPO / "skills" / "productivity"
FUEL_SKILLS = [
    "fuel-station-operator",
    "fuel-wfs-pricing",
    "fuel-inventory-ordering",
    "fuel-predictions",
    "fuel-data-extraction",
    "fuel-competitor-prices",
]
FORBIDDEN = [
    "Somebody78",
    "myoffice701@gmail.com",
    "rahim@",
    "shaggyaratia@",
    "sixtynineinvestment",
    "[LOCAL_USER_HOME]",
    "1gclWurmB7Ns_r3U4Uiir2UNd92CZtf5PKiGydiqyL_I",
    "1365kSRx6OyL5yMSNP-rqH5NlS7xiQNk6QY4jJk-2SKM",
]


def _frontmatter(text: str) -> dict:
    assert text.startswith("---\n")
    _, raw, _ = text.split("---", 2)
    return yaml.safe_load(raw) or {}


def test_fuel_station_skills_are_bundled_and_customer_safe():
    for name in FUEL_SKILLS:
        skill = SKILLS / name / "SKILL.md"
        assert skill.exists(), name
        text = skill.read_text(encoding="utf-8")
        meta = _frontmatter(text)
        assert meta["name"] == name
        assert "description" in meta and "fuel" in meta["description"].lower()
        lowered = text.lower()
        for forbidden in FORBIDDEN:
            assert forbidden.lower() not in lowered, f"{forbidden} leaked in {name}"


def test_fuel_station_operator_has_action_and_confirmation_policy():
    text = (SKILLS / "fuel-station-operator" / "SKILL.md").read_text(encoding="utf-8")
    assert "Do **not** ask generic permission" in text
    assert "For side effects, get clear confirmation" in text
    assert "Firecrawl" in text
    assert "Never mix WFS prices" in text
    assert "/fuel-wfs-pricing" in text


def test_fuel_specialty_skills_cover_required_workflows():
    required = {
        "fuel-wfs-pricing": ["TOTAL", "pump", "spreadsheet"],
        "fuel-inventory-ordering": ["tank", "dispatch", "gallons"],
        "fuel-predictions": ["crude", "Prediction", "probabilities"],
        "fuel-data-extraction": ["Firecrawl", "PDF", "normalized"],
        "fuel-competitor-prices": ["competitor", "margin", "recommendation"],
    }
    for skill, needles in required.items():
        text = (SKILLS / skill / "SKILL.md").read_text(encoding="utf-8")
        for needle in needles:
            assert needle in text, f"{needle} missing from {skill}"
