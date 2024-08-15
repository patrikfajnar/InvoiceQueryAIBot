# %% 
# init

import os
from langchain_community.llms import Ollama
from langchain_core.output_parsers import StrOutputParser
from langchain.prompts import PromptTemplate
from operator import itemgetter


MODEL = "llama2"
model = Ollama(model=MODEL)
parser = StrOutputParser()

# %%
# Create documents var
from langchain.docstore.document import Document
import json

documents = []

for i in range(1,4):
    path = f'./InvoiceFiles/invoice_data{i}.json'
    with open(path, "r", encoding='utf-8') as f:
        json_data = json.load(f)
    json_string = json.dumps(json_data, ensure_ascii=False)
    page = Document(page_content=json_string, metadata={"source": path})
    documents.append(page)

# %%
# Document retrieval with DocArrayInMemorySearch
# from langchain_community.embeddings import OllamaEmbeddings
# from langchain_community.vectorstores import DocArrayInMemorySearch


# vectorstore = DocArrayInMemorySearch.from_documents(documents, embedding=OllamaEmbeddings(model=MODEL))
# retriever = vectorstore.as_retriever()

#retriever.invoke("Sum all invoice item amount")

# %%
# Document retrieval with Chroma

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

# %%
#template

template = """
I provide json documents, extracted from invoice pdf-s. Answear the question based on the json filess briefly.

Context: {context}

Question: {question}
"""
prompt = PromptTemplate.from_template(template)


# %% 
# init
chain = (
    {
        "context": itemgetter("question") | retriever,
        "question": itemgetter("question"),
    }
    | prompt
    | model
    | parser
)



print(chain.invoke({'question': 'Sum the amount of all invoice item by invoices.'}))
print()
# %%
