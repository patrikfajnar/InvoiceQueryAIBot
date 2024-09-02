import json
import os
from langchain_chroma import Chroma
from langchain_community.document_loaders import TextLoader, JSONLoader
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveJsonSplitter, RecursiveCharacterTextSplitter

loaders = []
json_dir = r'c:\Data\OneDrive - kryonet.hu\PythonAI\számlák\program\json'
for filename in os.listdir(json_dir):
    path = os.path.join(json_dir, filename)
    loaders.append(JSONLoader(path, jq_schema=".", text_content=False)),

docs = []
for loader in loaders:
    docs.extend(loader.load())

vectorstore = Chroma(
    collection_name="collection",
    embedding_function=OpenAIEmbeddings(model="text-embedding-ada-002"),
    persist_directory="./chroma_langchain_db",
)

retriever = vectorstore.as_retriever(search_kwargs={'k': 10})

#vectorstore.add_documents(documents=docs, ids=None)

