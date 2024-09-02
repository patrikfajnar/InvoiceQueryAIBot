# %%
# init

import os
from langchain_community.llms import Ollama
from langchain_core.output_parsers import StrOutputParser
from langchain.prompts import PromptTemplate
from operator import itemgetter
from langchain_community.embeddings import OllamaEmbeddings
from langchain_chroma import Chroma
from langchain.docstore.document import Document
import json
import os
from uuid import uuid4
from langchain.text_splitter import RecursiveCharacterTextSplitter

MODEL = "llama2"
model = Ollama(model=MODEL)
parser = StrOutputParser()

documents = []

json_dir = r'c:\Data\OneDrive - kryonet.hu\PythonAI\számlák\program\json'
for filename in os.listdir(json_dir):
    path = os.path.join(json_dir, filename)
    with open(path, "r", encoding='utf-8') as f:
        json_data = json.load(f)
        json_string = json.dumps(json_data, ensure_ascii=False)
        page = Document(page_content=json_string, metadata={"source": path})
        documents.append(page)

vectorstore = Chroma(
    collection_name="collection_1",
    embedding_function=OllamaEmbeddings(model=MODEL),
    persist_directory="./chroma_langchain_db",
)
retriever = vectorstore.as_retriever()

text_splitter = RecursiveCharacterTextSplitter(chunk_size=512, chunk_overlap=20)
split_docs = text_splitter.split_documents(documents)

uuids = [str(uuid4()) for _ in range(len(split_docs))]
vectorstore.add_documents(documents=split_docs, ids=uuids)

template = """
I provide json documents, extracted from invoice pdf-s. Answear the question based on the json filess briefly.

Context: {context}

Question: {question}
"""
prompt = PromptTemplate.from_template(template)



# %%
# run retriver

question = 'Show me the invoices where the payment term is "Bankkártya"'

retriever = vectorstore.as_retriever(
        search_type="mmr",
        search_kwargs={'k': 7}
    )

retriever.invoke(question)

# %%
# run chain

chain = (
    {
        "context": itemgetter("question") | retriever,
        "question": itemgetter("question"),
    }
    | prompt
)

chain.invoke({'question': question})

# %%
