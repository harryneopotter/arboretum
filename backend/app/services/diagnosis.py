"""
Diagnosis service for plant problem matching.
"""

import re
import math
from typing import Optional
from app.services.qdrant_client import get_qdrant
from app.services.text_embeddings import get_text_embedding
from app.utils.text_blob_parser import enrich_payload


class DiagnosisService:
    """Service for diagnosing plant problems from symptoms."""

    def __init__(self):
        self.qdrant = get_qdrant()
        self.text_service = get_text_embedding()

    async def diagnose(
        self,
        plant_id: str,
        symptom: str,
        limit: int = 3,
    ) -> dict | None:
        """
        Find matching problems for a plant based on symptom.

        Args:
            plant_id: Plant identifier (slug)
            symptom: Observed symptom description

        Returns:
            Best matching problem dict or None
        """
        # Fetch the plant's full payload
        plant = await self._get_plant_by_slug(plant_id)
        if not plant:
            return None

        # Enrich payload so common_problems is populated from text_blob if needed
        plant = enrich_payload(plant)
        problems = plant.get("common_problems") or []

        if not problems:
            return None

        symptom_embedding = await self.text_service.embed(symptom)

        # Find best matching problem using semantic score + keyword overlap.
        symptom_lower = symptom.lower()
        symptom_words = set(re.findall(r'\w+', symptom_lower))

        best_match = None
        best_score = -1.0

        for problem in problems:
            problem_text = f"{problem.get('symptom', '')} {' '.join(problem.get('possible_causes', []))}"
            problem_embedding = await self.text_service.embed(problem_text)
            semantic_score = self._cosine_similarity(symptom_embedding, problem_embedding)

            problem_text = problem_text.lower()
            problem_words = set(re.findall(r'\w+', problem_text))

            overlap = len(symptom_words & problem_words) / max(len(symptom_words), 1)
            score = (semantic_score * 0.7) + (overlap * 0.3)

            if score > best_score:
                best_score = score
                best_match = problem

        if best_match:
            return {
                "score": max(best_score, 0.0),
                "symptom": best_match.get("symptom", ""),
                "possible_causes": best_match.get("possible_causes", []),
                "fix": best_match.get("fix", ""),
                "prevention": best_match.get("prevention", ""),
            }

        return None

    async def _get_plant_by_slug(self, slug: str) -> dict | None:
        """Fetch plant payload by slug using QdrantService filter."""
        from app.config import get_settings
        settings = get_settings()

        points = await self.qdrant.scroll_points(
            collection=settings.plants_collection,
            filter_conditions={
                "must": [{"key": "slug", "match": {"value": slug}}]
            },
            limit=1,
        )
        if points:
            return points[0].get("payload")
        return None

    def _cosine_similarity(self, left: list[float], right: list[float]) -> float:
        if not left or not right or len(left) != len(right):
            return 0.0
        dot = sum(a * b for a, b in zip(left, right))
        left_norm = math.sqrt(sum(a * a for a in left))
        right_norm = math.sqrt(sum(b * b for b in right))
        if left_norm == 0 or right_norm == 0:
            return 0.0
        return dot / (left_norm * right_norm)


# Singleton instance
_diagnosis_service: Optional[DiagnosisService] = None


def get_diagnosis() -> DiagnosisService:
    """Get diagnosis service singleton."""
    global _diagnosis_service
    if _diagnosis_service is None:
        _diagnosis_service = DiagnosisService()
    return _diagnosis_service
