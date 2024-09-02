# %% 
# init

import os
import json

from langchain_community.llms import Ollama
from langchain_core.output_parsers import StrOutputParser
from langchain.prompts import PromptTemplate
from operator import itemgetter
from langchain.docstore.document import Document

MODEL = "llama2"
model = Ollama(model=MODEL)
parser = StrOutputParser()

documents = []

for i in range(1,4):
    path = f'./InvoiceFiles/invoice_data{i}.json'
    with open(path, "r", encoding='utf-8') as f:
        json_data = json.load(f)
        json_string = json.dumps(json_data, ensure_ascii=False)
        page = Document(page_content=json_string, metadata={"source": path})
    documents.append(page)

from langchain_community.embeddings import OllamaEmbeddings
from langchain_chroma import Chroma 

embeddings = OllamaEmbeddings(model=MODEL)

vectorstore2 = Chroma(
    collection_name="example_collection2",
    embedding_function=embeddings,
    persist_directory="./chroma_langchain_db",
)
retriever = vectorstore2.as_retriever()

# %%
# Add items to chroma persistent store

#from uuid import uuid4
# uuids = [str(uuid4()) for _ in range(len(documents))]
# vectorstore2.add_documents(documents=documents, ids=uuids)

