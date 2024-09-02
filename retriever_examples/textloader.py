
# %%
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
    loaders.append(TextLoader(path, 'utf-8'))


docs = []
for loader in loaders:
    docs.extend(loader.load())

vectorstore = Chroma(
    collection_name="collection_text_json",
    embedding_function=OpenAIEmbeddings(model="text-embedding-ada-002"),
    persist_directory="./chroma_langchain_db",
)

retriever = vectorstore.as_retriever(search_kwargs={'k': 10})
#vectorstore.add_documents(documents=docs, ids=None)


# %%

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
)
