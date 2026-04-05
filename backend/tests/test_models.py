"""
Tests for app/models.py – Pydantic schema validation.
"""

import pytest
from pydantic import ValidationError
from app.models import (
    IdentifyRequest,
    SearchRequest,
    DiagnoseRequest,
    PlantMatch,
    IdentifyMatch,
    IdentifyResponse,
    SearchResponseItem,
    ProblemEntry,
    DiagnoseResponse,
    PlantResponse,
    ErrorResponse,
)


class TestIdentifyRequest:
    def test_valid(self):
        req = IdentifyRequest(image="base64string==")
        assert req.image == "base64string=="

    def test_missing_image_raises(self):
        with pytest.raises(ValidationError):
            IdentifyRequest()


class TestSearchRequest:
    def test_valid_defaults(self):
        req = SearchRequest(query="fern")
        assert req.query == "fern"
        assert req.limit == 5  # default

    def test_custom_limit(self):
        req = SearchRequest(query="cactus", limit=10)
        assert req.limit == 10

    def test_limit_min_boundary(self):
        req = SearchRequest(query="x", limit=1)
        assert req.limit == 1

    def test_limit_max_boundary(self):
        req = SearchRequest(query="x", limit=20)
        assert req.limit == 20

    def test_limit_too_low(self):
        with pytest.raises(ValidationError):
            SearchRequest(query="x", limit=0)

    def test_limit_too_high(self):
        with pytest.raises(ValidationError):
            SearchRequest(query="x", limit=21)

    def test_empty_query_raises(self):
        with pytest.raises(ValidationError):
            SearchRequest(query="")

    def test_query_too_long_raises(self):
        with pytest.raises(ValidationError):
            SearchRequest(query="x" * 1001)

    def test_missing_query_raises(self):
        with pytest.raises(ValidationError):
            SearchRequest()


class TestDiagnoseRequest:
    def test_valid(self):
        req = DiagnoseRequest(plant_id="money-plant", symptom="yellow leaves")
        assert req.plant_id == "money-plant"
        assert req.symptom == "yellow leaves"

    def test_missing_plant_id_raises(self):
        with pytest.raises(ValidationError):
            DiagnoseRequest(symptom="yellow leaves")

    def test_missing_symptom_raises(self):
        with pytest.raises(ValidationError):
            DiagnoseRequest(plant_id="money-plant")

    def test_empty_symptom_raises(self):
        with pytest.raises(ValidationError):
            DiagnoseRequest(plant_id="money-plant", symptom="")

    def test_symptom_too_long_raises(self):
        with pytest.raises(ValidationError):
            DiagnoseRequest(plant_id="x", symptom="y" * 501)


class TestPlantMatch:
    def test_valid(self):
        m = PlantMatch(slug="aloe-vera", plant_name="Aloe Vera", score=0.95)
        assert m.slug == "aloe-vera"
        assert m.plant_name == "Aloe Vera"
        assert m.score == 0.95


class TestIdentifyMatch:
    def test_with_image_url(self):
        m = IdentifyMatch(slug="aloe-vera", plant_name="Aloe Vera", score=0.9, image_url="http://img.jpg")
        assert m.image_url == "http://img.jpg"

    def test_without_image_url(self):
        m = IdentifyMatch(slug="aloe-vera", plant_name="Aloe Vera", score=0.9)
        assert m.image_url is None


class TestIdentifyResponse:
    def test_empty_response(self):
        r = IdentifyResponse(matches=[], plant=None, message="No matches found")
        assert r.matches == []
        assert r.message == "No matches found"

    def test_with_matches(self):
        match = IdentifyMatch(slug="fern", plant_name="Fern", score=0.8)
        r = IdentifyResponse(matches=[match], plant={"name": "Fern"})
        assert len(r.matches) == 1
        assert r.plant == {"name": "Fern"}


class TestSearchResponseItem:
    def test_all_fields(self):
        item = SearchResponseItem(
            slug="money-plant",
            plant_name="Money Plant",
            score=0.87,
            category="Indoor",
            description="A beautiful plant",
        )
        assert item.slug == "money-plant"
        assert item.category == "Indoor"

    def test_optional_fields_default(self):
        item = SearchResponseItem(plant_name="Fern", score=0.5)
        assert item.slug == ""
        assert item.category is None
        assert item.description is None


class TestProblemEntry:
    def test_valid(self):
        p = ProblemEntry(
            symptom="Yellow leaves",
            possible_causes=["Overwatering"],
            fix="Reduce water",
            prevention="Good drainage",
        )
        assert p.symptom == "Yellow leaves"
        assert p.possible_causes == ["Overwatering"]


class TestDiagnoseResponse:
    def test_with_problem(self):
        problem = ProblemEntry(
            symptom="Yellow leaves",
            possible_causes=["Overwatering"],
            fix="Reduce water",
            prevention="Good drainage",
        )
        r = DiagnoseResponse(problem=problem)
        assert r.problem is not None
        assert r.message is None

    def test_no_problem(self):
        r = DiagnoseResponse(problem=None, message="No match found")
        assert r.problem is None
        assert r.message == "No match found"


class TestPlantResponse:
    def test_valid(self):
        p = PlantResponse(
            plant_name="Aloe Vera",
            alternate_names=["Aloe"],
            category="Succulent",
            description="A succulent plant",
            care={"watering_frequency": "Weekly"},
            common_problems=[],
            reference_images=[],
        )
        assert p.plant_name == "Aloe Vera"

    def test_extra_fields_allowed(self):
        # PlantResponse has extra="allow"
        p = PlantResponse(
            plant_name="Aloe",
            alternate_names=[],
            category="Succulent",
            description="A plant",
            care={},
            common_problems=[],
            reference_images=[],
            custom_field="extra_value",
        )
        assert p.custom_field == "extra_value"


class TestErrorResponse:
    def test_valid(self):
        e = ErrorResponse(detail="Something went wrong")
        assert e.detail == "Something went wrong"
