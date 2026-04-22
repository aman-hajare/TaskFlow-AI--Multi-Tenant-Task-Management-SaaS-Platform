from app.ai.ai_client import AIClient
from app.ai.prompts import(
    summarize_task_prompt,
    suggest_priority_prompt,
    generate_tags_prompt
)

class AIServices:

    def __init__(self):
        self.client = AIClient()

    async def summarize_task(self, description: str,user):

        prompt = summarize_task_prompt(description) 

        return await self.client.generate(prompt)



    async def suggest_priority(self, title: str, description: str,user):

        prompt = suggest_priority_prompt(title, description)

        return await self.client.generate(prompt)



    async def generate_tags(self, title: str, description: str,user):

        prompt = generate_tags_prompt(title, description)

        return await self.client.generate(prompt)  