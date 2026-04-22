from fastapi import APIRouter,Request,Depends
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user, require_role
from app.core.database import get_db
from app.utils.responses import success_response 

from app.repositories.task_repository import TaskRepository
from app.ai.risk_prediction_service import RiskPredictionService
from app.ai.overdue_analyzer_service import OverdueAnalyzerService

from app.ai.ai_service import AIServices

from app.core.rate_limiter import limiter

router = APIRouter(prefix="/ai", tags=["AI"])

ai_service = AIServices()


@router.get("/task-risk/{task_id}")
async def predict_task_risk(
    task_id: int,
    db=Depends(get_db),
    current_user=Depends(require_role(["admin","manager"]))
):

    task = TaskRepository.get_task_by_id(
        db,
        task_id,
        current_user.company_id
    )

    result = await RiskPredictionService.predict_task_risk(
        db,
        task
    )

    return result

@router.get("/overdue-analysis")
async def analyze_overdue_tasks(
    db: Session = Depends(get_db),
    user=Depends(require_role(["admin","manager"]))
):

    result = await OverdueAnalyzerService.analyze_overdue_tasks(
        db,
        user.company_id
    )

    return success_response(
        current_user=user,
        message="Overdue task analysis completed",
        data=result
    )


@router.post("/summarize-task",
             summary="Generate task using AI")
@limiter.limit("10/minute")
async def summarize_task(request: Request, 
                         description: str,
                         user=Depends(require_role(["admin","manager","employee"]))):

    summary = await ai_service.summarize_task(description,user)

    return {"summary": summary}

@router.post("/suggest-priority",
             summary="Generate task using AI")
@limiter.limit("10/minute")
async def suggest_priority(request: Request,
                           title: str, 
                           description: str,
                           user=Depends(require_role(["admin","manager","employee"]))):

    priority = await ai_service.suggest_priority(title, description,user)

    return {"priority": priority}

@router.post("/generate-tags",
             summary="Generate task using AI")
@limiter.limit("10/minute")
async def generate_tags(request: Request,
                        title: str, 
                        description: str,
                        user=Depends(require_role(["admin","manager","employee"]))):

    tags = await ai_service.generate_tags(title, description,user)

    return {"tags": tags}
