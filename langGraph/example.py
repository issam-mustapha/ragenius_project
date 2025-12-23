from typing import TypedDict
from langgraph.graph import StateGraph, START, END

class State(TypedDict):
    topic: str
    joke: str

def refine_topic(state: State):
    return {"topic": state["topic"] + " and cats"}

def generate_joke(state: State):
    return {"joke": f"This is a joke about {state['topic']}"}

graph = (
    StateGraph(State)
    .add_node(refine_topic)
    .add_node(generate_joke)
    .add_edge(START, "refine_topic")
    .add_edge("refine_topic", "generate_joke")
    .add_edge("generate_joke", END)
    .compile()
)

# The stream() method returns an iterator that yields streamed outputs
for chunk in graph.stream(  
    {"topic": "ice cream"},
    # Set stream_mode="updates" to stream only the updates to the graph state after each node
    # Other stream modes are also available. See supported stream modes for details
    stream_mode="updates",  
):
    print(chunk)