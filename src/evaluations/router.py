"""Endpoints for the in-process POC evaluation runner."""

from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, Request

from src.evaluations.service import RUNS, EvaluationService

router = APIRouter(prefix="/evaluations", tags=["evaluations"])


async def get_evaluation_service(request: Request) -> EvaluationService:
    return request.app.state.evaluation_service


@router.get("", summary="List evaluation cases and expected answers")
async def cases(
    service: Annotated[EvaluationService, Depends(get_evaluation_service)],
) -> dict[str, Any]:
    return {
        "cases": service.cases,
        "runs": RUNS,
    }


@router.post("/run", summary="Evaluate the configured chat agent with three attempts per case")
async def run(
    service: Annotated[EvaluationService, Depends(get_evaluation_service)],
) -> dict[str, Any]:
    if not service.settings.llm_api_key:
        raise HTTPException(status_code=503, detail="Configure LLM_API_KEY first.")
    # POC: a user-triggered run makes paid model calls; no job queue or persistence.
    return await service.run()
