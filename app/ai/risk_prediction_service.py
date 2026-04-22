import json

from app.ai.ai_client import AIClient
from app.ai.risk_prompts import TASK_RISK_PROMPT

from app.repositories.task_repository import TaskRepository
from app.utils.logger import logger

from app.core.exceptions import AppException

from datetime import datetime

class RiskPredictionService:

    @staticmethod
    async def predict_task_risk(db, task):

        try:
            # Validate task
            if not task:
                raise AppException(
                    message="Task not found",
                    error_code="TASK_NOT_FOUND",
                    status_code=404
                )


            if task.status.lower() == "completed":
                return {
                    "risk_level": "none",
                    "risk_score": 0,
                    "reason": "Task is already completed"
                }
            
            if task.deadline and task.deadline < datetime.utcnow():
                return {
                    "risk_level": "high",
                    "risk_score": 0.95,
                    "reason": "Task is overdue and has already missed its deadline"
                }
                        

            # Safe workload calculation
            user_task_count = 0
            if task.assigned_to:
                user_task_count = TaskRepository.count_active_tasks(
                    db,
                    task.assigned_to
                )

            # Prepare data
            task_data = {
                "task_id": task.id,
                "title": task.title,
                "priority": task.priority,
                "status": task.status,
                "deadline": str(task.deadline),
                "developer_task_count": user_task_count
            }

            # Build prompt
            prompt = TASK_RISK_PROMPT.format(
                task_data=json.dumps(task_data)
            )

            # AI call
            ai_client = AIClient()
            response = await ai_client.generate(prompt, expect_json=True)

            logger.info(f"AI raw response: {response}")

            # Clean response
            response = response.strip()

            # Validate JSON format
            if not response.startswith("{"):
                raise Exception(f"Invalid AI JSON: {response}")

            # Parse JSON
            result = json.loads(response)

            # Validate structure
            if "risk_level" not in result or "risk_score" not in result:
                raise Exception(f"Incomplete AI response: {result}")

            return result

        except AppException:
            raise

        except Exception as e:
            logger.error(f"Risk prediction failed: {e}")

            return {
                "risk_level": "unknown",
                "risk_score": 0,
                "reason": "AI prediction failed"
            }