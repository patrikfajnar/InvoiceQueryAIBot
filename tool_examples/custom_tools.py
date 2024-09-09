# %%
from typing_extensions import Annotated, TypedDict
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_core.messages import HumanMessage
import invoice_tools
from langchain_openai import ChatOpenAI
from pprint import pprint

llm = ChatOpenAI(model="gpt-4o")
llm_with_tools = llm.bind_tools(invoice_tools.invoice_tools_list)

query = "How many invoices are there in 2023 december, 2024 january and 2024 february? What is the sum of the total amounts in december 2023?"
messages = [HumanMessage(query)]
ai_msg = llm_with_tools.invoke(messages)
messages.append(ai_msg)

for tool_call in ai_msg.tool_calls:
    selected_tool = invoice_tools.tools_by_name[tool_call["name"].lower()]
    tool_msg = selected_tool.invoke(tool_call)
    messages.append(tool_msg)

ai_msg2 = llm_with_tools.invoke(messages)
messages.append(ai_msg2)

for tool_call in ai_msg2.tool_calls:
    selected_tool = invoice_tools.tools_by_name[tool_call["name"].lower()]
    tool_msg = selected_tool.invoke(tool_call)
    messages.append(tool_msg)

ai_msg3 = llm_with_tools.invoke(messages)
messages.append(ai_msg3)

pprint(messages)
# %%
