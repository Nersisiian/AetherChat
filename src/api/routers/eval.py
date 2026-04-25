from fastapi import APIRouter
from ...evaluation.run_eval import run_evaluation
router = APIRouter()

@router.get("/run")
async def run_eval_endpoint():
    results = run_evaluation()
    return results