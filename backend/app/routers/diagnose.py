"""
Plant diagnosis router.
"""

from fastapi import APIRouter, HTTPException, status
from app.models import DiagnoseRequest, DiagnoseResponse, ProblemEntry
from app.services.diagnosis import get_diagnosis

router = APIRouter(prefix="/diagnose", tags=["Plant Diagnosis"])


@router.post("", response_model=DiagnoseResponse)
async def diagnose_plant(request: DiagnoseRequest):
    """
    Diagnose a plant problem from symptoms.

    Steps:
    1. Embed symptom (dense + sparse)
    2. Search only problem-level entries for the plant
    3. Return best matching problem with causes, fix, prevention
    """
    try:
        diagnosis_service = get_diagnosis()

        result = await diagnosis_service.diagnose(
            plant_id=request.plant_id,
            symptom=request.symptom,
        )

        if result is None:
            return DiagnoseResponse(
                problem=None,
                message="No matching problems found for this symptom"
            )

        return DiagnoseResponse(
            problem=ProblemEntry(
                symptom=result.get("symptom", ""),
                possible_causes=result.get("possible_causes", []),
                fix=result.get("fix", ""),
                prevention=result.get("prevention", ""),
            )
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Diagnosis failed: {str(e)}"
        )
