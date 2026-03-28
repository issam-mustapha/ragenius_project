from typing import TypedDict ,Annotated ,Sequence
from langchain_core.messages import SystemMessage ,BaseMessage
from langchain_core.tools import tool
from langgraph.graph.message import add_messages
from langgraph.graph import StateGraph , START , END
from langgraph.prebuilt import ToolNode
from langchain_ollama import ChatOllama


class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage],add_messages]


@tool
def update_age(age:int):
    """update age """
    return age+1
@tool
def update_nom(nom:str):
    """update name"""
    return f"your name is {nom} adoch"

@tool
def equation_degre_1(a:int , b:int):
    """solve a first degree-(linear) equation of the form ax+b=0.
    Parameters:
         - a: coefficient pf x
         - b : constant term
         returns solution for x or a message if no infinite solution exist
    
    """
    if a==0 and b==0:
        return "The equation has infinity many solutions."
    if a==0 and b!=0:
        return "the equation has no solution"
    return f"the solution is {-b/a}"
    
@tool
def add(a: int , b:int):
    """sum of a and b 
    
    args:
     a: first number
     b : second number
    """
    return  a+b

@tool
def multiply(a : float , b:float):
    """multiply two numbers 
    a: first number
    b:second number
    
    """


    return a*b

@tool
def update_master(master:str):
    """
    use this tool when user want to update master
    
    args:
       master : name of master
    """
    return f"your master {master} in beni mellal you can find issam adoch here and he will give you some advice to be prefessionelle"
tools=[update_age,update_nom, add , multiply, equation_degre_1,update_master]
llm = ChatOllama(model="mistral", base_url="http://localhost:11434" ,temperature=0).bind_tools(tools=tools)


def agent(state:AgentState)->AgentState:
    system_prompt=SystemMessage(content="you are ai assistant answer to query to the best of your ability, you can use all tools you have" 

)
    response=llm.invoke([system_prompt]+state["messages"])
    #print(f"\n AI : {response.content}")
    return {"messages" : [response]}

def should_continue(state:AgentState):
    messages=state["messages"]
    last_messages=messages[-1]
    if not last_messages.tool_calls:
        return "end"
    else :
        return "continue"
    
graph= StateGraph(AgentState)
graph.add_node("agent",agent)
tool_node=ToolNode(tools=tools)
graph.add_node("tools", tool_node)
graph.set_entry_point("agent")

graph.add_conditional_edges(

"agent",
should_continue,
{
    "continue":"tools",
    "end":END,
},
)

graph.add_edge("tools","agent")

app = graph.compile()

def print_stream(stream):
    for s in stream:
        message = s["messages"][-1]
        if isinstance(message,tuple):
            print("the answer is instance of tuple")
            print(message)
        else:
            print("the answer is instance of tool")
            message.pretty_print()

input = {"messages":[("user","my name is issam so update my name")]}
print_stream(app.stream(input , stream_mode="values"))


























