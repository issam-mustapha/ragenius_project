import json, re, logging
from datetime import datetime
from typing import List, Dict, Optional
from pydantic import BaseModel, ValidationError
from langgraph.graph import StateGraph, MessagesState, START
from langgraph.store.postgres import PostgresStore
from langchain_ollama import ChatOllama, OllamaEmbeddings
from app.connexion_db import getUrl
from app.agent.model import get_llm

EMBED_MODEL_NAME = "nomic-embed-text"

llm = get_llm()
embeddings = OllamaEmbeddings(model=EMBED_MODEL_NAME)


DB_URI = getUrl()
store_cm = PostgresStore.from_conn_string(DB_URI)
store = store_cm.__enter__()
store.index = {"embed": embeddings, "dims": 1536}


class UserProfile(BaseModel):
    name: Optional[str] = None
    profession: Optional[str] = None
    years_experience: List[str] = []
    hobbies: List[str] = []
    languages: List[str] = []
    learning_methods: List[str] = []
    communication_style: List[str] = []
    preferences: Dict[str, str] = {}
    last_update: Optional[datetime] = None


def load_profile(store, user_id: str) -> UserProfile:
    docs = store.search(("users", str(user_id), "profile"))
    if docs:
        try:
            return UserProfile(**docs[0].value)
        except ValidationError as e:
            logging.warning(f"Profile in DB invalid, resetting: {e}")
    return UserProfile()

def save_profile(store, user_id: str, profile: UserProfile):
    profile_json = profile.model_dump_json()
    store.put(("users", str(user_id), "profile"), "main", json.loads(profile_json))

def merge_profiles(existing: UserProfile, new: UserProfile) -> UserProfile:
    updated = existing.model_copy()
    for field in existing.model_fields:
        old_value = getattr(existing, field)
        new_value = getattr(new, field)
        if isinstance(old_value, list) and isinstance(new_value, list):
            setattr(updated, field, list(set(old_value + new_value)))
        elif isinstance(old_value, dict) and isinstance(new_value, dict):
            setattr(updated, field, {**old_value, **new_value})
        elif new_value is not None:
            setattr(updated, field, new_value)
    updated.last_update = datetime.utcnow()
    return updated

def extract_and_validate_json(llm_text: str) -> Optional[UserProfile]:
    try:
        match = re.search(r"\{.*\}", llm_text, re.DOTALL)
        if match:
            data = json.loads(match.group(0))
            return UserProfile(**data)
    except (json.JSONDecodeError, ValidationError) as e:
        logging.error("Extraction or validation failed", exc_info=e)
    return None


def update_profile_if_needed(state: MessagesState, *, store, config):
    user_id = config["configurable"]["user_id"]
    user_message = state["messages"][-1].content
    profile = load_profile(store, user_id)

    prompt = f"""
You are a memory manager.
Current user profile:
{profile.model_dump_json(indent=2)}
New user message:
"{user_message}"
Rules:
- Update profile ONLY if new personal info is present
- Keep all existing data
- Do NOT invent data
- Include: name, profession, years_experience, hobbies, languages, learning_methods, communication_style, preferences
- Return ONLY a valid JSON object
"""
    llm_output = llm.invoke(prompt).content
    updated_profile = extract_and_validate_json(llm_output)
    if updated_profile:
        merged_profile = merge_profiles(profile, updated_profile)
        save_profile(store, user_id, merged_profile)
    return state

def call_model(state: MessagesState, *, store, config):
    user_id = config["configurable"]["user_id"]
    user_message = state["messages"][-1].content
    profile = load_profile(store, user_id)
    facts = store.search(("users", user_id, "facts"), query=user_message)
    facts_text = "\n".join([f.value["data"] for f in facts])
    system_prompt = f"""
You are a helpful assistant.
User profile:
{profile.model_dump_json(indent=2)}
Relevant facts:
{facts_text}
"""
    response = llm.invoke([{"role": "system", "content": system_prompt}] + state["messages"])
    return {"messages": response}

def build_long_memory_graph():
    builder = StateGraph(MessagesState)
    builder.add_node("update_memory", update_profile_if_needed)
    builder.add_node("chat", call_model)
    builder.add_edge(START, "update_memory")
    builder.add_edge("update_memory", "chat")
    return builder.compile(store=store)
