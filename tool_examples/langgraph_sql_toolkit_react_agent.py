from langchain import hub
from langchain_community.utilities.sql_database import SQLDatabase
from langchain_community.agent_toolkits.sql.toolkit import SQLDatabaseToolkit
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent

db = SQLDatabase.from_uri('sqlite:///c:\\Data\\Pr\\AI\\InvoiceQueryAIBot\\InvoiceQueryAIBot\\data\\invoices.db')
llm = ChatOpenAI(model="gpt-4o")

toolkit = SQLDatabaseToolkit(db=db, llm=llm)

from langchain import hub

prompt_template = hub.pull("langchain-ai/sql-agent-system-prompt")

assert len(prompt_template.messages) == 1
print(prompt_template.input_variables)

system_message = prompt_template.format(dialect="SQLite", top_k=5)


agent_executor = create_react_agent(
    llm, toolkit.get_tools(), state_modifier=system_message
)

example_query = "Hány invoice item van ahol az unit értéke db? Mi a megnevezése ezeknek a tételeknek?"

events = agent_executor.stream(
    {"messages": [("user", example_query)]},
    stream_mode="values",
)
for event in events:
    event["messages"][-1].pretty_print()