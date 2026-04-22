OVERDUE_ANALYSIS_PROMPT = """
You are an AI project management assistant.

Analyze the overdue task and return STRICT JSON.

RULES:
- ONLY return JSON
- NO explanation
- NO text outside JSON
- DO NOT return string values for objects

FORMAT:

{{
  "insight": {{
    "summary": "short summary (5 to 10 words)",
    "risk_level": "low | medium | high"
  }},
  "tasks": [
    {{
      "task_id": 1,
      "reason": "reason for delay at least 10 words"
    }}
  ],
  "recommendation": {{
    "action": "what to do",
    "priority": "high/medium/low"
  }}
}}

Statistics:
{statistics}

Tasks:
{tasks}
"""