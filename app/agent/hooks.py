from langchain.agents import AgentState
from langgraph.runtime import Runtime
from app.agent.context import Context
from langchain.agents.middleware import before_model, after_model
from app.agent.long_memory import update_profile_if_needed, store

@before_model
def log_before_model(state: AgentState, runtime: Runtime[Context]):
    print(f"[BEFORE MODEL] user_id={runtime.context.user_id}")
    
@before_model
def long_term_memory_middleware(state, runtime: Runtime[Context]):
    user_id = runtime.context.user_id  # <-- récupération de l'ID utilisateur
    if not user_id.startswith("guest-"):
        config = {"configurable": {"user_id": user_id, "thread_id": f"user-{user_id}"}}
        # Appeler le nœud de mise à jour mémoire
        update_profile_if_needed(state, store=store, config=config)


@after_model
def log_after_model(state: AgentState, runtime: Runtime[Context]):
    print(f"[AFTER MODEL] user_id={runtime.context.user_id}")
