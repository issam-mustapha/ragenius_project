from typing import Annotated , Sequence , TypedDict
from langchain_core.messages import BaseMessage,HumanMessage, AIMessage, ToolMessage,SystemMessage
from langchain_core.tools import tool
from langgraph.graph.message import add_messages
from langgraph.graph import StateGraph , END ,START
from langgraph.prebuilt import ToolNode
from langchain_ollama import ChatOllama

# def get_llm():
#     return ChatOllama(
#         model="mistral",
#         base_url=
#     )


document_content=""
class AgentState(TypedDict):
    messages : Annotated[Sequence[BaseMessage],add_messages]
@tool
def update(content:str)->str:
    """Update the document with the provided content."""
    global document_content
    document_content=content
    return f"Document has been updated successfully! The current content is \n {document_content}"


@tool
def save(filename : str)->str:
    """Save the current document to a text and finish the process.
    
    Args:
         filename :name for the text file.
    """
    global document_content
    if not filename.endswith('.txt'):
        filename=f"{filename}.txt"
    try :
        with open(filename,'w') as file:
            file.write(document_content)
        print(f"\n ☑️ Document has been saved successfuly to {filename}.")
        return f"Document has been saved successfully to {filename}."
    except Exception as e:
        return f"Error saving document :{str(e)}"


tools= [update , save]

llm = ChatOllama(model="mistral", base_url="http://localhost:11434").bind_tools(tools=tools)

def our_agent(state :AgentState)->AgentState:
    system_prompt=SystemMessage(content=f"""
       You are a drafer , a helpful writting assistant you are going to help the usr update and save and modify documents.

       - if the user wants to update or modify content use the 'update' tool woth the complete updated content.
       - if the user wants to save and finish you need to use 'save tool.
       - make sure to always show the current document state after modifications.

The current document content is :{document_content}                       
""")
    print("here you excuted the methode our agent be careful")
    if not state["messages"]:
        user_input="i'm rady to help you to update a document ,What would you like to create?"
        user_message=HumanMessage(content=user_input)
    else :
        user_input= input("\n What would you like to do with the document?")
        print(f"\n USER : {user_input}")
        user_message = HumanMessage(content=user_input)
    all_messages=[system_prompt]+list(state["messages"])+[user_input]
    response= llm.invoke(all_messages)
    print(f"\n AI : {response.content}")
    if hasattr(response,"tool_calls")and response.tool_calls:
        print(f"using tools: {[tc['name'] for tc in response.tool_calls]}")
    return {"messages": list(state["messages"])+[user_message,response]}

def should_continue(state:AgentState)->str:
    """Determine if we should continue or end the conversation ."""
    messages=state["messages"]
    if not messages:
        return "continue"
    for message in reversed(messages):
        if (isinstance(message,ToolMessage) and "saved" in message.content.lower() and "document" in message.content.lower()):
            return "end"
    return "continue"


def print_messages(messages):
    """function i made to print the message in a more readable format"""
    if not messages:
        return
    for message in messages[-3:]:
        if isinstance(message,ToolMessage):
            print(f"\n TOOL RESULT :{message.content}")



graph=StateGraph(AgentState)
#graph.add_node(START , "agent" )
graph.add_node("agent",our_agent)
graph.add_node("tools",ToolNode(tools=tools))
graph.set_entry_point("agent")
graph.add_edge("agent","tools")
graph.add_conditional_edges(
    "tools",
    should_continue,
    {
        "continue":"agent",
        "end":END
    }
)

app = graph.compile()

def run_document_agent():
    print("\n ================== DRAFTER ================")
    state={"messages":[]}
    for step in app.stream(state ,stream_mode="values"):
        if "messages" in step:
            print_messages(step["messages"])
    print("\n ============== DRAFTER FINISHED==========")

if __name__ == "__main__":
    run_document_agent()

















