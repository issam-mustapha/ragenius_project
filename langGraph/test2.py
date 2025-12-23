from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import InMemorySaver
from typing_extensions import TypedDict
from operator import add
import uuid

# -----------------------
# Définition du state
# -----------------------
class State(TypedDict):
    foo: int
    bar: list[str]

# -----------------------
# Définition des nodes
# -----------------------
def node_a(state: State):
    new_state = {"foo": state["foo"] + 1, "bar": state["bar"] + ["a"]}
    print("Node A executed:", new_state)
    return new_state

def node_b(state: State):
    new_state = {"foo": state["foo"] + 1, "bar": state["bar"] + ["b"]}
    print("Node B executed:", new_state)
    return new_state

# -----------------------
# Création du graph
# -----------------------
workflow = StateGraph(State)
workflow.add_node(node_a)
workflow.add_node(node_b)
workflow.add_edge(START, "node_a")
workflow.add_edge("node_a", "node_b")
workflow.add_edge("node_b", END)

# -----------------------
# Checkpointer
# -----------------------
checkpointer = InMemorySaver()
graph = workflow.compile(checkpointer=checkpointer)

# -----------------------
# Invocation du graph
# -----------------------
thread_id = "1"
config = {"configurable": {"thread_id": thread_id}}

initial_state = {"foo": 0, "bar": []}
graph.invoke(initial_state, config)

# -----------------------
# Afficher le dernier état
# -----------------------
state_snapshot = graph.get_state(config)
print("\nDernier état du thread :", state_snapshot.values)

# -----------------------
# Afficher tout l'historique
# -----------------------
history = list(graph.get_state_history(config))
print("\nHistorique des checkpoints :")
for i, snap in enumerate(history):
    print(f"Checkpoint {i} :", snap.values)

# -----------------------
# Mettre à jour l'état
# -----------------------
print("\n--- Mise à jour de l'état ---")
graph.update_state(config, {"foo": 10, "bar": ["update"]})

state_snapshot = graph.get_state(config)
print("État après update :", state_snapshot.values)
