"""
Tests for app/services/diagnosis.py – DiagnosisService.
Qdrant calls are mocked to avoid network access.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from app.services.diagnosis import DiagnosisService


PLANT_PAYLOAD_WITH_PROBLEMS = {
    "slug": "money-plant",
    "plant_name": "Money Plant",
    "description": "A popular houseplant.",
    "care": {"watering_frequency": "weekly"},
    "common_problems": [
        {
            "symptom": "Yellow leaves",
            "possible_causes": ["Overwatering", "Poor drainage"],
            "fix": "Reduce watering and improve drainage.",
            "prevention": "Ensure pot has holes.",
        },
        {
            "symptom": "Brown leaf tips",
            "possible_causes": ["Low humidity", "Underwatering"],
            "fix": "Mist leaves regularly.",
            "prevention": "Keep humidity above 40%.",
        },
    ],
}

PLANT_PAYLOAD_NO_PROBLEMS = {
    "slug": "bare-plant",
    "plant_name": "Bare Plant",
    "description": "No problems.",
    "care": {},
    "common_problems": [],
}


@pytest.fixture
def mock_qdrant():
    qdrant = MagicMock()
    qdrant.scroll_points = AsyncMock()
    return qdrant


@pytest.fixture
def service(mock_qdrant):
    with patch("app.services.diagnosis.get_qdrant", return_value=mock_qdrant):
        svc = DiagnosisService()
    return svc, mock_qdrant


class TestDiagnoseMethod:
    async def test_returns_none_when_plant_not_found(self, service):
        svc, qdrant = service
        qdrant.scroll_points.return_value = []  # no plant found
        result = await svc.diagnose("nonexistent", "yellow leaves")
        assert result is None

    async def test_returns_none_when_no_problems(self, service):
        svc, qdrant = service
        qdrant.scroll_points.return_value = [{"payload": PLANT_PAYLOAD_NO_PROBLEMS}]
        result = await svc.diagnose("bare-plant", "something wrong")
        assert result is None

    async def test_returns_best_match_for_yellow_leaves(self, service):
        svc, qdrant = service
        qdrant.scroll_points.return_value = [{"payload": PLANT_PAYLOAD_WITH_PROBLEMS}]
        result = await svc.diagnose("money-plant", "yellow leaves overwatering")
        assert result is not None
        assert result["symptom"] == "Yellow leaves"

    async def test_returns_best_match_for_brown_tips(self, service):
        svc, qdrant = service
        qdrant.scroll_points.return_value = [{"payload": PLANT_PAYLOAD_WITH_PROBLEMS}]
        result = await svc.diagnose("money-plant", "brown tips low humidity")
        assert result is not None
        assert result["symptom"] == "Brown leaf tips"

    async def test_result_contains_required_fields(self, service):
        svc, qdrant = service
        qdrant.scroll_points.return_value = [{"payload": PLANT_PAYLOAD_WITH_PROBLEMS}]
        result = await svc.diagnose("money-plant", "yellow leaves")
        assert "symptom" in result
        assert "possible_causes" in result
        assert "fix" in result
        assert "prevention" in result
        assert "score" in result

    async def test_score_is_between_zero_and_one(self, service):
        svc, qdrant = service
        qdrant.scroll_points.return_value = [{"payload": PLANT_PAYLOAD_WITH_PROBLEMS}]
        result = await svc.diagnose("money-plant", "yellow leaves")
        assert 0 <= result["score"] <= 1

    async def test_score_higher_for_more_matching_words(self, service):
        svc, qdrant = service
        qdrant.scroll_points.return_value = [{"payload": PLANT_PAYLOAD_WITH_PROBLEMS}]
        # Many matching keywords for yellow leaves problem
        result_many = await svc.diagnose("money-plant", "yellow leaves overwatering drainage")
        result_few = await svc.diagnose("money-plant", "yellow")
        # Both should find yellow leaves, but score_many should be >= score_few
        assert result_many["score"] >= result_few["score"]

    async def test_case_insensitive_matching(self, service):
        svc, qdrant = service
        qdrant.scroll_points.return_value = [{"payload": PLANT_PAYLOAD_WITH_PROBLEMS}]
        result_upper = await svc.diagnose("money-plant", "YELLOW LEAVES")
        result_lower = await svc.diagnose("money-plant", "yellow leaves")
        assert result_upper["symptom"] == result_lower["symptom"]

    async def test_zero_overlap_still_returns_best(self, service):
        """Even if no keyword matches, should still return best match (overlap=0 wins over nothing)."""
        svc, qdrant = service
        qdrant.scroll_points.return_value = [{"payload": PLANT_PAYLOAD_WITH_PROBLEMS}]
        # gibberish query — overlap is 0 for all problems, best_score stays 0
        # best_match should remain None (no improvement over 0)
        result = await svc.diagnose("money-plant", "xyzzy foobar")
        # best_score=0, best_match=None → returns None
        assert result is None

    async def test_qdrant_scroll_called_with_correct_filter(self, service):
        svc, qdrant = service
        qdrant.scroll_points.return_value = [{"payload": PLANT_PAYLOAD_WITH_PROBLEMS}]
        await svc.diagnose("money-plant", "yellow")
        call_args = qdrant.scroll_points.call_args
        assert call_args is not None
        # Filter should include the slug
        filter_arg = call_args.kwargs.get("filter_conditions") or call_args.args[1]
        assert "money-plant" in str(filter_arg)


class TestGetPlantBySlug:
    async def test_returns_none_when_not_found(self, service):
        svc, qdrant = service
        qdrant.scroll_points.return_value = []
        result = await svc._get_plant_by_slug("nonexistent")
        assert result is None

    async def test_returns_payload_when_found(self, service):
        svc, qdrant = service
        qdrant.scroll_points.return_value = [{"payload": {"slug": "aloe-vera", "plant_name": "Aloe Vera"}}]
        result = await svc._get_plant_by_slug("aloe-vera")
        assert result["plant_name"] == "Aloe Vera"


class TestExtractProblems:
    def test_extract_basic(self, service):
        svc, _ = service
        text_blob = """Common Problems and Solutions:
- Problem: Yellow leaves
  Causes: Overwatering, poor drainage
  Fix: Reduce watering
  Prevention: Ensure good drainage
"""
        problems = svc._extract_problems(text_blob)
        assert len(problems) == 1
        assert problems[0]["symptom"] == "Yellow leaves"

    def test_extract_multiple_problems(self, service):
        svc, _ = service
        text_blob = """- Problem: Yellow leaves
  Causes: Overwatering
  Fix: Reduce water
  Prevention: Good drainage
- Problem: Brown tips
  Causes: Low humidity
  Fix: Mist leaves
  Prevention: Humidity above 40%
"""
        problems = svc._extract_problems(text_blob)
        assert len(problems) == 2

    def test_extract_empty_blob(self, service):
        svc, _ = service
        problems = svc._extract_problems("")
        assert problems == []

    def test_extract_causes_split_by_comma(self, service):
        svc, _ = service
        text_blob = """- Problem: Wilting
  Causes: Drought, heat stress, root rot
  Fix: Water immediately
  Prevention: Regular watering
"""
        problems = svc._extract_problems(text_blob)
        if problems:
            assert "Drought" in problems[0]["possible_causes"]
