# %%
from langchain.retrievers import ParentDocumentRetriever
from langchain.storage import InMemoryStore, LocalFileStore
from langchain_chroma import Chroma
from langchain_community.document_loaders import TextLoader, JSONLoader
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveJsonSplitter, RecursiveCharacterTextSplitter
from langchain.docstore.document import Document
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain.storage._lc_store import create_kv_docstore
from operator import itemgetter
from langchain_openai import ChatOpenAI
import os
import json 

loaders = []

json_dir = r'c:\Data\OneDrive - kryonet.hu\PythonAI\számlák\program\json'
for filename in os.listdir(json_dir):
    path = os.path.join(json_dir, filename)
    with open(path, "r", encoding='utf-8') as f:
        json_data = json.load(f)
        loaders.append(JSONLoader(path, jq_schema=".", text_content=False)),

documents = []
for loader in loaders:
    documents.extend(loader.load())

child_splitter = RecursiveCharacterTextSplitter(chunk_size=200)
vectorstore = Chroma(
    collection_name="parent_docs_retriver3_json", embedding_function=OpenAIEmbeddings(), persist_directory="./chroma_langchain_db"
)

local_file_store = LocalFileStore("./store_location_json")
store = create_kv_docstore(local_file_store)
retriever = ParentDocumentRetriever(
    vectorstore=vectorstore,
    docstore=store,
    child_splitter=child_splitter,
    search_kwargs={ 'k': 9,}
)


# %% Add documents to the retriever
#retriever.add_documents(documents, ids=None)

# %%
# Create template and model

template = """
I provide json documents, extracted from invoice pdf-s. 
Answear the question based on the json files.

Context: {context}

Question: {question}
"""
prompt = PromptTemplate.from_template(template)

model = ChatOpenAI(model='gpt-4o')

# %% 
# Call the model
#question =  'List the descriptions of invoices where the payment term is bankkártya (or any resembling) and group them by invoice ID.'
question =  'Listázd azokat az elemeket, ahol a fizetés típusa (payment term) bankkártya (vagy bármi hasonló) és csoportosítsd őket számla azonosító szerint.'
#question =  'List every item where the unit is db'

r = retriever.invoke(question)
p = prompt.invoke({'question': question, 'context': r})
print(r)
print()
print(p)
print()

# a = model.invoke(p)

chain = (
    {
        "context": itemgetter("question") | retriever,
        "question": itemgetter("question"),
    }
    | prompt
    | model
    | StrOutputParser()
)


print(question)
print(chain.invoke({'question': question}))
print()
# %%
