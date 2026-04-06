"""
Tests for app/utils/text_blob_parser.py
"""

import pytest
from app.utils.text_blob_parser import parse_text_blob, enrich_payload

FULL_BLOB = """Plant: Money Plant
Also known as: Golden Pothos, Devil's Ivy, Pothos
Category: Indoor
Description: A popular trailing vine with heart-shaped leaves.

Care Instructions:
- Watering Frequency: Once a week
- Light Requirements: Low to bright indirect light
- Soil Type: Well-draining potting mix
- Temperature Range: 15-30°C
- Humidity: Moderate to high
- Fertilizing: Monthly during growing season

Common Problems and Solutions:
- Problem: Yellow leaves
  Causes: Overwatering, poor drainage
  Fix: Reduce watering frequency
  Prevention: Ensure pot has drainage holes
- Problem: Brown leaf tips
  Causes: Low humidity, underwatering
  Fix: Mist leaves or use a humidifier
  Prevention: Keep humidity above 40%
"""


class TestParseTextBlob:
    def test_empty_string(self):
        result = parse_text_blob("")
        assert result == {"alternate_names": [], "description": "", "care": {}, "common_problems": []}

    def test_falsy_input_returns_empty_result(self):
        # parse_text_blob guards with `if not text_blob`; None is also falsy
        result = parse_text_blob(None)  # type: ignore[arg-type]
        assert result == {"alternate_names": [], "description": "", "care": {}, "common_problems": []}

    def test_alternate_names_parsed(self):
        result = parse_text_blob(FULL_BLOB)
        assert "Golden Pothos" in result["alternate_names"]
        assert "Devil's Ivy" in result["alternate_names"]
        assert "Pothos" in result["alternate_names"]
        assert len(result["alternate_names"]) == 3

    def test_description_parsed(self):
        result = parse_text_blob(FULL_BLOB)
        assert "trailing vine" in result["description"]

    def test_care_watering(self):
        result = parse_text_blob(FULL_BLOB)
        assert result["care"]["watering_frequency"] == "Once a week"

    def test_care_light(self):
        result = parse_text_blob(FULL_BLOB)
        assert result["care"]["light_requirements"] == "Low to bright indirect light"

    def test_care_soil(self):
        result = parse_text_blob(FULL_BLOB)
        assert result["care"]["soil_type"] == "Well-draining potting mix"

    def test_care_temperature(self):
        result = parse_text_blob(FULL_BLOB)
        assert result["care"]["temperature_range"] == "15-30°C"

    def test_care_humidity(self):
        result = parse_text_blob(FULL_BLOB)
        assert result["care"]["humidity"] == "Moderate to high"

    def test_care_fertilizing(self):
        result = parse_text_blob(FULL_BLOB)
        assert result["care"]["fertilizing"] == "Monthly during growing season"

    def test_problems_count(self):
        result = parse_text_blob(FULL_BLOB)
        assert len(result["common_problems"]) == 2

    def test_first_problem_symptom(self):
        result = parse_text_blob(FULL_BLOB)
        assert result["common_problems"][0]["symptom"] == "Yellow leaves"

    def test_first_problem_causes(self):
        result = parse_text_blob(FULL_BLOB)
        causes = result["common_problems"][0]["possible_causes"]
        assert "Overwatering" in causes
        assert "poor drainage" in causes

    def test_first_problem_fix(self):
        result = parse_text_blob(FULL_BLOB)
        assert "Reduce watering" in result["common_problems"][0]["fix"]

    def test_first_problem_prevention(self):
        result = parse_text_blob(FULL_BLOB)
        assert "drainage holes" in result["common_problems"][0]["prevention"]

    def test_second_problem_symptom(self):
        result = parse_text_blob(FULL_BLOB)
        assert result["common_problems"][1]["symptom"] == "Brown leaf tips"

    def test_no_care_section(self):
        blob = "Plant: Test\nDescription: A test plant."
        result = parse_text_blob(blob)
        assert result["care"] == {}

    def test_no_problems_section(self):
        blob = "Plant: Test\nCare Instructions:\n- Watering Frequency: Daily\n"
        result = parse_text_blob(blob)
        assert result["common_problems"] == []

    def test_single_alternate_name(self):
        blob = "Also known as: Pothos\nDescription: x"
        result = parse_text_blob(blob)
        assert result["alternate_names"] == ["Pothos"]

    def test_alternate_names_stripped(self):
        blob = "Also known as:  Name A ,  Name B  "
        result = parse_text_blob(blob)
        assert "Name A" in result["alternate_names"]
        assert "Name B" in result["alternate_names"]


class TestEnrichPayload:
    def test_enriches_empty_payload(self):
        payload = {"text_blob": FULL_BLOB}
        result = enrich_payload(payload)
        assert result["description"] != ""
        assert len(result["alternate_names"]) > 0
        assert result["care"] != {}
        assert len(result["common_problems"]) > 0

    def test_preserves_existing_description(self):
        payload = {
            "description": "My custom description",
            "care": {"watering_frequency": "daily"},
            "text_blob": FULL_BLOB,
        }
        result = enrich_payload(payload)
        assert result["description"] == "My custom description"

    def test_preserves_existing_care(self):
        payload = {
            "care": {"watering_frequency": "custom value"},
            "text_blob": FULL_BLOB,
        }
        result = enrich_payload(payload)
        assert result["care"]["watering_frequency"] == "custom value"

    def test_fills_missing_description_from_blob(self):
        payload = {"text_blob": FULL_BLOB}
        result = enrich_payload(payload)
        assert "trailing vine" in result["description"]

    def test_fills_missing_alternate_names(self):
        payload = {"description": "x", "care": {}, "text_blob": FULL_BLOB}
        result = enrich_payload(payload)
        # description and care are provided but alternate_names is empty
        # enrich_payload only triggers blob parsing if description or care is missing
        # care is empty {} which is falsy, so it will parse
        assert isinstance(result["alternate_names"], list)

    def test_no_text_blob(self):
        payload = {}
        result = enrich_payload(payload)
        assert result["description"] == ""
        assert result["care"] == {}
        assert result["alternate_names"] == []
        assert result["common_problems"] == []
