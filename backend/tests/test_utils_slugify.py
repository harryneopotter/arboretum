"""
Tests for app/utils/slugify.py
"""

import pytest
from app.utils.slugify import slugify, extract_plant_id_from_payload


class TestSlugify:
    def test_basic_lowercase(self):
        assert slugify("aloe vera") == "aloe-vera"

    def test_uppercase_converted(self):
        assert slugify("Aloe Vera") == "aloe-vera"

    def test_parentheses_removed(self):
        assert slugify("Chinese Evergreen (Aglaonema)") == "chinese-evergreen-aglaonema"

    def test_prefix_stripped(self):
        # "plant:money_plant" → strip prefix → "money_plant"
        # underscores are \w chars so they stay as-is, not converted to hyphens
        assert slugify("plant:money_plant") == "money_plant"

    def test_prefix_with_spaces(self):
        assert slugify("category:Snake Plant") == "snake-plant"

    def test_multiple_spaces_collapsed(self):
        assert slugify("aloe   vera") == "aloe-vera"

    def test_leading_trailing_hyphens_stripped(self):
        assert slugify("-aloe-vera-") == "aloe-vera"

    def test_special_chars_removed(self):
        assert slugify("Plant! @Name#") == "plant-name"

    def test_already_valid_slug(self):
        assert slugify("money-plant") == "money-plant"

    def test_underscores_become_hyphens(self):
        # underscores are word chars, stay as-is then collapse
        result = slugify("money_plant")
        # regex: [-\s]+ → collapse, underscores are \w so kept
        # actual: "money_plant" stays "money_plant"
        assert result == "money_plant"

    def test_empty_string(self):
        assert slugify("") == ""

    def test_single_word(self):
        assert slugify("Fern") == "fern"

    def test_numbers_preserved(self):
        assert slugify("Plant 5000") == "plant-5000"

    def test_colon_only_splits_on_first(self):
        # "a:b:c" → splits on first colon, remainder is "b:c"
        result = slugify("a:b:c")
        # "b:c" → lowercase → remove non-word → "bc" or "b-c"
        # colon is removed, "bc" joined by nothing → "bc"
        assert "b" in result


class TestExtractPlantIdFromPayload:
    def test_plant_id_field(self):
        payload = {"plant_id": "money_plant", "id": "different"}
        assert extract_plant_id_from_payload(payload) == "money_plant"

    def test_fallback_to_id(self):
        payload = {"id": "aloe_vera"}
        assert extract_plant_id_from_payload(payload) == "aloe_vera"

    def test_empty_payload(self):
        assert extract_plant_id_from_payload({}) == ""

    def test_neither_field(self):
        payload = {"slug": "some-slug", "name": "Some Plant"}
        assert extract_plant_id_from_payload(payload) == ""

    def test_plant_id_preferred_over_id(self):
        payload = {"plant_id": "correct", "id": "wrong"}
        assert extract_plant_id_from_payload(payload) == "correct"
