
# %%
import json
import os
from langchain_chroma import Chroma
from langchain_community.document_loaders import TextLoader, JSONLoader
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveJsonSplitter, RecursiveCharacterTextSplitter
from langchain.docstore.document import Document
from langchain.prompts import PromptTemplate

loaders = []
documents = []

json_splitter = RecursiveJsonSplitter(max_chunk_size=250)

json_dir = r'c:\Data\OneDrive - kryonet.hu\PythonAI\számlák\program\json'
for filename in os.listdir(json_dir):
    path = os.path.join(json_dir, filename)
    with open(path, "r", encoding='utf-8') as f:
        json_data = json.load(f)
        documents.extend(json_splitter.create_documents(texts=[json_data]))


vectorstore = Chroma(
    collection_name="collection_jsonsplit",
    embedding_function=OpenAIEmbeddings(model="text-embedding-ada-002"),
    persist_directory="./chroma_langchain_db",
)

retriever = vectorstore.as_retriever(search_kwargs={'k': 7})
# vectorstore.add_documents(documents=documents, ids=None)
