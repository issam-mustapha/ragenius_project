from langchain.tools import tool, ToolRuntime
from app.agent.context import Context

@tool
def fetch_user_email_preferences(runtime: ToolRuntime[Context]) -> str:
    """Fetch user preferences"""
    user_id = runtime.context.user_id

    if runtime.store:
        if memory := runtime.store.get(("users",), user_id):
            return memory.value.get("preferences", "No preferences found")

    return "The user prefers detailed responses."
