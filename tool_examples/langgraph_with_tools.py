# %%
# 

from typing import Annotated
from langchain_core.messages import BaseMessage
from typing_extensions import TypedDict
from langgraph.graph import StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_openai import ChatOpenAI
from invoice_tools import invoice_tools_list, tools_by_name
from langgraph.checkpoint.memory import MemorySaver

memory = MemorySaver()

class State(TypedDict):
    messages: Annotated[list, add_messages]
graph_builder = StateGraph(State)

llm = ChatOpenAI(model="gpt-4o")
llm_with_tools = llm.bind_tools(tools=invoice_tools_list)


def chatbot(state: State):
    return {"messages": [llm_with_tools.invoke(state["messages"])]}


graph_builder.add_node("chatbot", chatbot)
tool_node = ToolNode(tools=invoice_tools_list)
graph_builder.add_node("tools", tool_node)

graph_builder.add_conditional_edges(
    "chatbot",
    tools_condition,
)
graph_builder.add_edge("tools", "chatbot")
graph_builder.set_entry_point("chatbot")
graph = graph_builder.compile(checkpointer=memory)

config = {"configurable": {"thread_id": "1"}}

user_input = "How many invoices are there in 2023 december, 2024 january and 2024 february? What is the sum of the total amounts in december 2023?"
events = graph.stream(
    {"messages": [("user", user_input)]}, config, stream_mode="values"
)
for event in events:
    event["messages"][-1].pretty_print()
# %%

from IPython.display import Image, display
display(Image(graph.get_graph().draw_mermaid_png()))
# %%
