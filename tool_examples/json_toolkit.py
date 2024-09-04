# %%

import json
from langchain.agents import (
    create_json_agent,
    AgentExecutor
)
from langchain.agents.agent_toolkits import JsonToolkit
from langchain.chains import LLMChain
from langchain.llms.openai import OpenAI
from langchain.requests import TextRequestsWrapper
from langchain.tools.json.tool import JsonSpec

merged_json_file_path = r'c:\Data\OneDrive - kryonet.hu\PythonAI\számlák\program\merged_invoices.json'

with open(merged_json_file_path, 'r', encoding='utf-8') as reader:
    data = json.load(reader)

json_spec = JsonSpec(dict_= data, max_value_length=4000, jq_schema=".data")
json_toolkit = JsonToolkit(spec=json_spec)

json_agent_executor = create_json_agent(
    llm=OpenAI(temperature=0),
    toolkit=json_toolkit,
    verbose=True
)

question =  'How many descriptions are there where the payment term is bankkártya (or any resembling)'

json_agent_executor.run(question)
