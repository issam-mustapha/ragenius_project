from langchain.agents import create_agent
from app.agent.model import get_llm
from app.agent.context import Context
from app.agent.memory import get_checkpointer, get_summarizer
from app.agent.prompts import dynamic_system_prompt
from app.agent.hooks import log_before_model, log_after_model ,long_term_memory_middleware
from app.agent.tools import fetch_user_email_preferences 

def build_agent():
    return create_agent(
        model=get_llm(),
        tools=[fetch_user_email_preferences],
        middleware=[
            dynamic_system_prompt,
            get_summarizer(),
            log_before_model,
            log_after_model,
            long_term_memory_middleware
        ],
        context_schema=Context,
        checkpointer=get_checkpointer()
    )
