from langchain.agents import create_agent
from langchain.agents.middleware import PIIMiddleware
from app.agent.model import get_llm
from app.agent.context import Context
from app.agent.short_memory import get_checkpointer, get_summarizer
from app.agent.prompts import dynamic_system_prompt
from app.agent.hooks import (
    log_before_model,
    log_after_model,
    long_term_memory_middleware
)
from app.agent.tools import (
    fetch_user_email_preferences,
    answer_based_on_image
)
from app.agent.middleware.pii_ux_mask import PIIMaskUXMiddleware

def _build_pii_middleware():
    """
    PII Guardrails
    - Always executed FIRST
    - Prevents PII from reaching the model, logs, and memory
    """

    return [
        # 🔐 Email addresses → REDACT
        PIIMiddleware(
            pii_type="email",
            strategy="mask",
            apply_to_input=True,
            #apply_to_output=False,
            #apply_to_tool_results=False,
        ),

        # 🔐 Credit cards → MASK (keep last 4 digits)
        PIIMiddleware(
            pii_type="credit_card",
            strategy="mask",
            apply_to_input=True,
        ),

        # 🔐 IP addresses → HASH (safe for analytics/logs)
        PIIMiddleware(
            pii_type="ip",
            strategy="hash",
            apply_to_input=True,
        ),

        # 🚫 API keys → BLOCK (hard security stop)
        PIIMiddleware(
            pii_type="api_key",
            detector=r"sk-[a-zA-Z0-9]{32,}",
            strategy="block",
            apply_to_input=True,
        ),
    ]


def build_agent():
    """
    Builds and returns the LangChain agent with:
    - PII protection
    - Dynamic system prompt
    - Short & long-term memory
    - Logging hooks
    - Tools
    """

    return create_agent(
        model=get_llm(),

        tools=[
            fetch_user_email_preferences,
            answer_based_on_image,
        ],

        middleware=[
            # 🛡️ PII guardrails (MUST be first)
            *_build_pii_middleware(),

            # 🧠 System prompt
            dynamic_system_prompt,

            # 🧠 Short-term memory summarizer
            get_summarizer(),

            # 📝 Logging hooks (PII-safe)
            log_before_model,
            log_after_model,

            # 🧠 Long-term memory
            long_term_memory_middleware,
            PIIMaskUXMiddleware(),
        ],

        context_schema=Context,
        checkpointer=get_checkpointer(),
    )