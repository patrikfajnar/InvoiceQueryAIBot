# %%
from langchain.retrievers import ParentDocumentRetriever
from langchain.storage import InMemoryStore, LocalFileStore
from langchain_chroma import Chroma
from langchain_community.document_loaders import TextLoader, JSONLoader
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveJsonSplitter, RecursiveCharacterTextSplitter
from langchain.docstore.document import Document
from langchain.prompts import PromptTemplate
from langchain.storage._lc_store import create_kv_docstore
from operator import itemgetter
from langchain_openai import OpenAI
import os
import json 

documents = []

json_dir = r'c:\Data\OneDrive - kryonet.hu\PythonAI\számlák\program\json'
for filename in os.listdir(json_dir):
    path = os.path.join(json_dir, filename)
    with open(path, "r", encoding='utf-8') as f:
        json_data = json.load(f)
        json_string = json.dumps(json_data, ensure_ascii=False)
        page = Document(page_content=json_string, metadata={"source": path})
        documents.append(page)

child_splitter = RecursiveCharacterTextSplitter(chunk_size=200)
vectorstore = Chroma(
    collection_name="parent_docs_retriver", embedding_function=OpenAIEmbeddings(), persist_directory="./chroma_langchain_db"
)

local_file_store = LocalFileStore("./store_location")
store = create_kv_docstore(local_file_store)
retriever = ParentDocumentRetriever(
    vectorstore=vectorstore,
    docstore=store,
    child_splitter=child_splitter,
    search_kwargs={'k': 7}
)

# %% Add documents to the retriever
# retriever.add_documents(documents, ids=None)

# %%
# Invoke tests

retriever.invoke('Show me the invoices where the payment term is "Bankkártya"')
retriever.invoke('Show me the invoices where the due date is this year january (2024-01)')
