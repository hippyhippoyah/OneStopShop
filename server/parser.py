
from dotenv import load_dotenv
from langchain_community.document_loaders import WebBaseLoader
from langchain_openai.embeddings import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai.chat_models import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from langchain_community.document_loaders import BraveSearchLoader
import os
import chromadb
from chromadb.config import Settings
from langchain_chroma import Chroma
from uuid import uuid4
import re

def clean_text(text):
    # Replace multiple spaces/newlines with a single space
    cleaned_text = re.sub(r'\s+', ' ', text)
    return cleaned_text.strip()

def parse(query):
    load_dotenv()

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    # Gets 5 urls

    google_query = f"Top {query} in 2024"

    loader = BraveSearchLoader(
        query=google_query, api_key=os.getenv("BRAVE_API_KEY"), search_kwargs={"count": 5, "result_filter":"web"}
    )
    docs = loader.load()
    urls = [doc.metadata['link'] for doc in docs]

    # loads the docs and splits them into chunks
    print(len(docs))
    loader = WebBaseLoader(urls)
    docs = loader.load()
    for doc in docs:
        doc.page_content = clean_text(doc.page_content)
    docs = text_splitter.split_documents(docs)

    chroma_client = chromadb.HttpClient(host="chroma", port = 8000, settings=Settings(allow_reset=True, anonymized_telemetry=False))
    collection_status = False
    while collection_status != True:
        try:
            document_collection = chroma_client.get_or_create_collection(name="sample_collection")
            collection_status = True
        except Exception as e:
            pass
    
    embeddings = OpenAIEmbeddings()

    vector_store_from_client = Chroma(
        client=chroma_client,
        collection_name="sample_collection",
        embedding_function=embeddings,
    )
    uuids = [str(uuid4()) for _ in range(len(docs))]

    vector_query = f"is a great choice"

    vector_store_from_client.add_documents(documents=docs, ids=uuids)
    results = vector_store_from_client.similarity_search_by_vector(
        embedding=embeddings.embed_query(vector_query), k=3
        # , where_document= {"contains": {"text": ""}}
    )
    for doc in results:
        print(f"* {doc.page_content} [{doc.metadata}]")

    chroma_client.delete_collection(name="sample_collection")