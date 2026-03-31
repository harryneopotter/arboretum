"""
Diagnosis service for plant problem matching.
"""

import re
from typing import Optional
from app.services.qdrant_client import get_qdrant
from app.services.text_embeddings import get_text_embedding, get_sparse_embedding


class DiagnosisService:
    """Service for diagnosing plant problems from symptoms."""

    def __init__(self):
        self.qdrant = get_qdrant()
        self.text_embed = get_text_embedding()
        self.sparse_embed = get_sparse_embedding()

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

        # Parse problems from text_blob
        text_blob = plant.get("text_blob", "")
        problems = self._extract_problems(text_blob)

        if not problems:
            return None

        # Find best matching problem based on symptom keywords
        symptom_lower = symptom.lower()
        symptom_words = set(re.findall(r'\w+', symptom_lower))
        
        best_match = None
        best_score = 0

        for problem in problems:
            problem_text = f"{problem.get('symptom', '')} {' '.join(problem.get('possible_causes', []))}".lower()
            problem_words = set(re.findall(r'\w+', problem_text))
            
            # Calculate keyword overlap
            overlap = len(symptom_words & problem_words)
            if overlap > best_score:
                best_score = overlap
                best_match = problem

        if best_match:
            return {
                "score": best_score / max(len(symptom_words), 1),
                "symptom": best_match.get("symptom", ""),
                "possible_causes": best_match.get("possible_causes", []),
                "fix": best_match.get("fix", ""),
                "prevention": best_match.get("prevention", ""),
            }

        return None

    async def _get_plant_by_slug(self, slug: str) -> dict | None:
        """Fetch plant payload by slug using scroll."""
        import requests
        from app.config import get_settings
        settings = get_settings()

        offset = None
        while True:
            body = {"limit": 100, "with_payload": True, "with_vectors": False}
            if offset:
                body["offset"] = offset

            resp = requests.post(
                f"{settings.qdrant_url}/collections/{settings.plants_collection}/points/scroll",
                headers={"api-key": settings.qdrant_api_key, "Content-Type": "application/json"},
                json=body,
            )
            if resp.status_code != 200:
                break

            data = resp.json().get("result", {})
            points = data.get("points", [])

            for point in points:
                payload = point.get("payload", {})
                if payload.get("slug") == slug:
                    return payload

            next_page = data.get("next_page_offset")
            if not next_page:
                break
            offset = next_page

        return None

    def _extract_problems(self, text_blob: str) -> list[dict]:
        """Extract problem entries from text_blob."""
        problems = []
        
        # Pattern to match "- Problem: X\n  Causes: ...\n  Fix: ...\n  Prevention: ..."
        # Matches until next "- Problem:" or end of string
        pattern = r'-\s*Problem:\s*(.+?)\n\s*Causes:\s*(.+?)\n\s*Fix:\s*(.+?)\n\s*Prevention:\s*(.+?)(?=\n-\s*Problem:|$)'
        matches = re.findall(pattern, text_blob, re.DOTALL)
        
        for match in matches:
            symptom, causes, fix, prevention = match
            problems.append({
                "symptom": symptom.strip(),
                "possible_causes": [c.strip() for c in causes.split(',')],
                "fix": fix.strip(),
                "prevention": prevention.strip(),
            })
        
        return problems


# Singleton instance
_diagnosis_service: Optional[DiagnosisService] = None


def get_diagnosis() -> DiagnosisService:
    """Get diagnosis service singleton."""
    global _diagnosis_service
    if _diagnosis_service is None:
        _diagnosis_service = DiagnosisService()
    return _diagnosis_service
