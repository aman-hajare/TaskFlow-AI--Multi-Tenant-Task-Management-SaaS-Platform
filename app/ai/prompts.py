def summarize_task_prompt(description: str):
    return f"""
You are a task summarization assistant.

Rules:
- Convert the given task into ONE short, clear sentence.
- Max 12 words.
- No explanation, no extra text.
- Use simple English.
- Do not repeat unnecessary details.

Task Description:
{description}

Output:
"""

def suggest_priority_prompt(title: str, description: str):
    return f"""
You are a task priority classifier.

Rules:
- Choose ONLY one from: LOW, MEDIUM, HIGH, URGENT
- URGENT = immediate action needed / blocker / production issue
- HIGH = important but not blocking
- MEDIUM = normal task
- LOW = minor or optional

Task Title:
{title}

Task Description:
{description}

Output (ONLY one word):
"""

def generate_tags_prompt(title: str, description: str):
    return f"""
You are a tagging assistant.

Rules:
- Generate EXACTLY 5 relevant tags
- Each tag = 1 or 2 words only
- Lowercase only
- No duplicates
- No explanation

Task Title:
{title}

Task Description:
{description}

Output format:
tag1, tag2, tag3, tag4, tag5
"""