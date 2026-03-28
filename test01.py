from app.agent.model import get_llm

llm = get_llm()

user_message = "my father name is mustapha he is a doctor"

prompt = f"""
SYSTEM:
You are a memory extractor.
From the user's message, identify if there is any information that should be stored in long term memory like personal details , perferebces,
habits , relationships , important events, etc.
rules:
- if there is a question or request for any information, do not answer question it or give advice.
Return a single line text **only important personal info**:
- If there is important info about user, summarize in a short natural and clear phrase not complicated phrase like inform user about here informations
for example : "User's name is johne doe and he likes football....
- If nothing important like Temporary feelings, moods, or physical states (e.g., tired, happy, sick) , return: "NO_MEMORY".
Do NOT return JSON or anything else.



USER MESSAGE:
'{user_message}'
"""

# Obtenir la réponse du LLM
response = llm.invoke(prompt)
print(response.content)
