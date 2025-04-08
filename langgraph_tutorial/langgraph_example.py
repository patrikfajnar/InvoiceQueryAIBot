from typing import Annotated
from typing_extensions import TypedDict
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import AnyMessage, add_messages

class EntryGraphState(TypedDict):
    request: str
    settlements: list
    diagram : str
    total_tran : str

def export_settlements(state : EntryGraphState):
    print('export...', state)
    return {"settlements" : ["customer1: 1000 tran", "customer2: 2000 tran"]}

def create_diagram(state : EntryGraphState):
    print('diagram creation...', state)
    return {"diagram" : 'bar chart'}

def calculate_total_tran(state : EntryGraphState):
    print('calculation...', state)
    return {"total_tran" : '3000'}

def summarization(state : EntryGraphState):
    print('summarization:')
    print('request: ', state['request'])
    print('settlements: ', state['settlements'])
    print('diagram: ', state['diagram'])
    print('total_tran: ', state['total_tran'])
    return None

entry_builder = StateGraph(EntryGraphState)
entry_builder.add_node("export_settlements", export_settlements)
entry_builder.add_node("create_diagram", create_diagram)
entry_builder.add_node("calculate_total_tran", calculate_total_tran)
entry_builder.add_node("summarization", summarization)

entry_builder.add_edge(START, "export_settlements")
entry_builder.add_edge("export_settlements", "calculate_total_tran")
entry_builder.add_edge("export_settlements", "create_diagram")
entry_builder.add_edge("create_diagram", "summarization")
entry_builder.add_edge("calculate_total_tran", "summarization")
entry_builder.add_edge("summarization", END)

m = MemorySaver()
graph = entry_builder.compile(checkpointer=m)
config = {"configurable": {"thread_id": "1"}, "settlements" : []}


graph.invoke({'request' : 'req'},config=config, stream_mode="values")  

# snap  = graph.get_state(config=config)
# print(snap)


from IPython.display import Image, display
display(Image(graph.get_graph().draw_mermaid_png()))
