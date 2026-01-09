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
    answer_based_on_image,
    summarize_user_pdf,
    summarize_text
)
from app.agent.middleware.pii_ux_mask import PIIMaskUXMiddleware
from app.agent.response_validator import response_validator_middleware
from app.agent.answer_scorer import answer_quality_scorer_middleware

def _build_pii_middleware():
    return [
        PIIMiddleware(pii_type="email", strategy="mask", apply_to_input=True),
        PIIMiddleware(pii_type="credit_card", strategy="mask", apply_to_input=True),
        PIIMiddleware(pii_type="ip", strategy="hash", apply_to_input=True),
        PIIMiddleware(pii_type="api_key", detector=r"sk-[a-zA-Z0-9]{32,}", strategy="block", apply_to_input=True),
    ]

def build_agent():
    """
    Build the professional LLM agent:
    - PII protection
    - Short-term & long-term memory
    - RAG integration
    - Image, PDF, text handling
    - Response validation & scoring
    """
    return create_agent(
        model=get_llm(),
        tools=[
            answer_based_on_image,
            summarize_user_pdf,
            summarize_text,
        ],
        middleware=[
            *_build_pii_middleware(),
            dynamic_system_prompt,
            get_summarizer(),
            log_before_model,
            log_after_model,
            long_term_memory_middleware,
            PIIMaskUXMiddleware(),
            response_validator_middleware,
            answer_quality_scorer_middleware,
        ],
        context_schema=Context,
        checkpointer=get_checkpointer()
    )
