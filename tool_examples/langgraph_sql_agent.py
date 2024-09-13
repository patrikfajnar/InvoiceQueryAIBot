from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langgraph.graph import StateGraph
from langgraph.graph.message import AnyMessage, add_messages
from typing import Annotated
from langchain_openai import ChatOpenAI
from typing_extensions import TypedDict
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import ToolNode, tools_condition

db = SQLDatabase.from_uri('sqlite:///c:\\Data\\Pr\\AI\\InvoiceQueryAIBot\\InvoiceQueryAIBot\\data\\invoices.db')
db_schema = db.get_table_info(db.get_usable_table_names())

class State(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]

graph_builder = StateGraph(State)

llm = ChatOpenAI(model="gpt-4o")

toolkit = SQLDatabaseToolkit(db=db, llm=llm)
tools = toolkit.get_tools() 
sql_db_query_tool = next(tool for tool in tools if tool.name == "sql_db_query")
sql_db_query_checker_tool = next(tool for tool in tools if tool.name == "sql_db_query_checker")
llm_with_db_tools = llm.bind_tools([sql_db_query_tool, sql_db_query_checker_tool])


system_message = """System: You are an agent designed to interact with a SQL database.
Given an input question, create a syntactically correct SQLite query to run, then look at the results of the query and return the answer.
You can order the results by a relevant column to return the most interesting examples in the database.
Never query for all the columns from a specific table, only ask for the relevant columns given the question.
You have access to tools for interacting with the database.
Only use the below tools. Only use the information returned by the below tools to construct your final answer.
You MUST double check your query before executing it. If you get an error while executing a query, rewrite the query and try again.

DO NOT make any DML statements (INSERT, UPDATE, DELETE, DROP etc.) to the database.

If you search for a specific value in a column, and this column's name contains 'name', always use '%'-s in the LIKE clause.
If you want to use a field as a number, cast it to a number type.

Use the following structures to interact with the database: """ + db_schema

initial_prompt = ChatPromptTemplate.from_messages(
    [("system", system_message), ("human", "{message}")]
)

def chatbot(state: State):
    print(state)
    print('sql_agent', initial_prompt.invoke(state["messages"]))
    result = (initial_prompt | llm_with_db_tools).invoke(state["messages"])
    print("res:",result)
    return {"messages": [result]}

graph_builder.add_node("chatbot", chatbot)
tool_node = ToolNode(tools=[sql_db_query_tool, sql_db_query_checker_tool])
graph_builder.add_node("tools", tool_node)


graph_builder.add_conditional_edges(
    "chatbot",
    tools_condition,
)
graph_builder.add_edge("tools", "chatbot")
graph_builder.set_entry_point("chatbot")

memory = MemorySaver()
graph = graph_builder.compile(checkpointer=memory)

config = {"configurable": {"thread_id": "1"}}
events = graph.stream(
    {"messages": [("user", "Melyik számlán volt a legnagyobb az adó, mi volt az eladó neve?")]}, 
    config, 
    stream_mode="values")

for event in events:
    event["messages"][-1].pretty_print()