import json
import re

from app.ai.ai_client import AIClient
from app.ai.skill_prompt import SKILL_DETECTION_PROMPT
from app.utils.logger import logger


class AISkillDetectionService:

    @staticmethod
    async def detect_skill(task_description: str):

        prompt = SKILL_DETECTION_PROMPT.format(
            task_description=task_description
        )

        try:
            ai_client = AIClient()

            logger.info(" Calling AI...")
            response = await ai_client.generate(prompt, expect_json=True)

            logger.info(f" RAW AI RESPONSE: {response}")

            # CLEAN RESPONSE (handle ```json``` issue)
            cleaned = re.sub(r"```json|```", "", response).strip()

            # PARSE JSON
            data = json.loads(cleaned)

            #  EXTRACT VALUES FIRST (IMPORTANT FIX)
            skill = data.get("skill")
            priority = data.get("priority")
            tags = data.get("tags", [])

            #  HANDLE MULTIPLE SKILLS
            if skill and "|" in skill:
                skill = skill.split("|")[0].strip()

            #  NORMALIZE (lowercase)
            if skill:
                skill = skill.lower()

            if priority:
                priority = priority.lower()

            result = {
                "skill": skill or "backend",     # fallback
                "priority": priority or "medium", # fallback
                "tags": tags
            }

            return result

        except Exception as e:

            logger.error(f"AI skill detection failed: {e}")

            return {
                "skill": None,
                "priority": None,
                "tags": []
            }