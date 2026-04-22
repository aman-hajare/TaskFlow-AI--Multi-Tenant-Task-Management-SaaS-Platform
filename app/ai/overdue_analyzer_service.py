from sqlalchemy.orm import Session

from app.repositories.task_repository import TaskRepository
from app.ai.ai_client import AIClient
from app.ai.overdue_prompts import OVERDUE_ANALYSIS_PROMPT
from app.core.enums import SkillEnum

from app.utils.logger import logger
from app.schemas.ai_schema import OverdueAIResponse

import json

class OverdueAnalyzerService:

    @staticmethod
    async def analyze_overdue_tasks(db: Session, company_id: int):

        overdue_tasks = TaskRepository.get_overdue_tasks(db, company_id)

        if not overdue_tasks:
            return {
                "total_overdue_tasks": 0,
                "insight": "No overdue tasks."
            }

        skill_groups = {}

        for task in overdue_tasks:
            skill = task.skill if task.skill else SkillEnum.UNKNOWN.value

            if skill not in skill_groups:
                skill_groups[skill] = 0

            skill_groups[skill] += 1

        data = {
            "total_overdue_tasks": len(overdue_tasks),
            "skill_distribution": skill_groups
        }

        tasks_data = []
        for task in overdue_tasks:
            tasks_data.append({
                "task_id": task.id,
                "title": task.title,
                "skill": task.skill,
                "deadline": str(task.deadline),
                "assigned_to": task.assigned_to
            })

        # prompt = OVERDUE_ANALYSIS_PROMPT.format(data=data)
        prompt = OVERDUE_ANALYSIS_PROMPT.format(
            statistics=json.dumps(data),
            tasks=json.dumps(tasks_data)
        )

        def normalize_ai_response(ai_response: str):

            try:
                data = json.loads(ai_response)

                # validate using schema
                validated = OverdueAIResponse(**data)

                return validated.dict()

            except Exception:

                #  fallback if AI returns paragraph
                return {
                    "insight": {
                        "summary": ai_response[:150],
                        "risk_level": "unknown"
                    },
                    "reason": [ai_response],
                    "recommendation": {
                        "action": "Manual review required",
                        "priority": "medium"
                    }
                }

        client = AIClient()
        ai_response = await client.generate(prompt, expect_json=True)

        parsed_response = normalize_ai_response(ai_response)

        return {
            "statistics": data,
            "tasks": tasks_data,
            "ai_analysis": parsed_response
        }

