"""
Parse a plant's stored text_blob string into structured fields.

The text_blob format written by ingest_plants.py:

    Plant: <name>
    Also known as: <name1>, <name2>
    Category: <category>
    Description: <text>
    Care Instructions:
    - Watering Frequency: <value>
    - Light Requirements: <value>
    - Soil Type: <value>
    - Temperature Range: <value>
    - Humidity: <value>
    - Fertilizing: <value>
    - Potting & Repotting: <value>
    Common Problems and Solutions:
    - Problem: <symptom>
      Causes: <cause1>, <cause2>
      Fix: <fix text>
      Prevention: <prevention text>
"""

import re
from typing import Optional


def parse_text_blob(text_blob: str) -> dict:
    """
    Extract structured fields from a text_blob string.

    Returns a dict with keys: alternate_names, description, care, common_problems.
    Any section not found is returned as an empty value of the appropriate type.
    """
    result: dict = {
        "alternate_names": [],
        "description": "",
        "care": {},
        "common_problems": [],
    }

    if not text_blob:
        return result

    # ---- alternate_names ------------------------------------------------
    alt_match = re.search(r"Also known as:\s*(.+)", text_blob)
    if alt_match:
        result["alternate_names"] = [n.strip() for n in alt_match.group(1).split(",") if n.strip()]

    # ---- description ----------------------------------------------------
    desc_match = re.search(r"Description:\s*(.+?)(?=\nCare Instructions:|\nCommon Problems|$)", text_blob, re.DOTALL)
    if desc_match:
        result["description"] = desc_match.group(1).strip()

    # ---- care -----------------------------------------------------------
    care_section = re.search(r"Care Instructions:(.*?)(?=\nCommon Problems|$)", text_blob, re.DOTALL)
    if care_section:
        care_text = care_section.group(1)
        care_map = {
            "watering_frequency": r"-\s*Watering Frequency:\s*(.+)",
            "light_requirements": r"-\s*Light Requirements:\s*(.+)",
            "soil_type": r"-\s*Soil Type:\s*(.+)",
            "temperature_range": r"-\s*Temperature Range:\s*(.+)",
            "humidity": r"-\s*Humidity:\s*(.+)",
            "fertilizing": r"-\s*Fertilizing:\s*(.+)",
        }
        for key, pattern in care_map.items():
            m = re.search(pattern, care_text)
            if m:
                result["care"][key] = m.group(1).strip()

    # ---- common_problems ------------------------------------------------
    problems_section = re.search(r"Common Problems and Solutions:(.*?)$", text_blob, re.DOTALL)
    if problems_section:
        prob_text = problems_section.group(1)
        pattern = (
            r"-\s*Problem:\s*(.+?)\n"
            r"\s*Causes:\s*(.+?)\n"
            r"\s*Fix:\s*(.+?)\n"
            r"\s*Prevention:\s*(.+?)(?=\n-\s*Problem:|\s*$)"
        )
        for m in re.finditer(pattern, prob_text, re.DOTALL):
            symptom, causes, fix, prevention = m.groups()
            result["common_problems"].append({
                "symptom": symptom.strip(),
                "possible_causes": [c.strip() for c in causes.split(",") if c.strip()],
                "fix": fix.strip(),
                "prevention": prevention.strip(),
            })

    return result


def enrich_payload(payload: dict) -> dict:
    """
    Add missing structured fields to a Qdrant plant payload by parsing text_blob.

    Fields are only added when absent in the payload; existing fields are preserved.
    """
    if not payload.get("description") or not payload.get("care"):
        parsed = parse_text_blob(payload.get("text_blob", ""))
        if not payload.get("description"):
            payload["description"] = parsed["description"]
        if not payload.get("care"):
            payload["care"] = parsed["care"]
        if not payload.get("alternate_names"):
            payload["alternate_names"] = parsed["alternate_names"]
        if not payload.get("common_problems"):
            payload["common_problems"] = parsed["common_problems"]
    return payload
