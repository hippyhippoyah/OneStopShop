
from dotenv import load_dotenv
from langchain_community.document_loaders import WebBaseLoader
from langchain_openai.embeddings import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai.chat_models import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from langchain_community.document_loaders import BraveSearchLoader
from langchain.schema import Document
import os
import chromadb
from chromadb.config import Settings
import requests
import json
from langchain_chroma import Chroma
from uuid import uuid4
import re
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, VideoUnavailable
from youtube_transcript_api.formatters import TextFormatter
from urllib.parse import urlparse, parse_qs
import asyncio
import itertools
import datetime
import aiohttp

vector_store_from_client = None

def setup_chroma_client():
    chroma_client = chromadb.HttpClient(host="chroma", port = 8000, settings=Settings(allow_reset=True, anonymized_telemetry=False))
    # chroma_client.delete_collection(name="sample_collection")
    collection_status = False
    while collection_status != True:
        try:
            document_collection = chroma_client.get_or_create_collection(name="sample_collection")
            collection_status = True
        except Exception as e:
            pass
    print("Collection created")

    embeddings = OpenAIEmbeddings()
    vector_store_from_client = Chroma(
        client=chroma_client,
        collection_name="sample_collection",
        embedding_function=embeddings,
    )
    vector_store_from_client.reset_collection()
    print("Collection reset")
    return vector_store_from_client

async def fetch_google_search_results(google_query, count=3, type="search"):
    url = "https://google.serper.dev/"+type
    
    payload = {
        "q": google_query,
        "num": count
    }
    
    headers = {
        'X-API-KEY': os.getenv("SERPER_API_KEY"),
        'Content-Type': 'application/json'
    }
    
    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, json=payload) as response:
            if response.status == 200:
                response_dict = await response.json()
                if type == "videos":
                    organic_results = response_dict.get('videos', [])
                else:
                    organic_results = response_dict.get('organic', [])
                urls = [res['link'] for res in organic_results]
                return urls
            else:
                response.raise_for_status()

def clean_text(text):
    # Replace multiple spaces/newlines with a single space
    cleaned_text = re.sub(r'\s+', ' ', text)
    return cleaned_text.strip()

def extract_video_id(url):
    parsed_url = urlparse(url)
    query_params = parse_qs(parsed_url.query)
    return query_params.get('v', [None])[0]

async def get_transcript_text(video_id):
    try:
        # Fetch the transcript asynchronously
        loop = asyncio.get_event_loop()
        transcript = await loop.run_in_executor(None, YouTubeTranscriptApi.get_transcript, video_id)

        # Use the TextFormatter to format the transcript as plain text
        formatter = TextFormatter()
        transcript_text = formatter.format_transcript(transcript)

        transcript_text = transcript_text.replace('\n', ' ')

        return transcript_text
    except TranscriptsDisabled:
        return "Transcripts are disabled for this video."
    except VideoUnavailable:
        return "The video is unavailable or does not exist."
    except Exception as e:
        return f"An error occurred: {e}"

async def process_urls(youtube_urls, product):
    transcript_docs = []
    tasks = []

    for url in youtube_urls:
        video_id = extract_video_id(url)
        task = asyncio.create_task(get_transcript_text(video_id))
        tasks.append((task, url))

    for task, url in tasks:
        transcript_text = await task
        transcript_doc = Document(
            page_content=transcript_text,
            metadata={"source": url, "product": product}
        )
        transcript_docs.append(transcript_doc)

    return transcript_docs

async def fetch_website_reviews(product, count=3):
    urls = await fetch_google_search_results(f"{product} reviews", count, type="search")
    
    web_loader = WebBaseLoader(urls)
    docs = web_loader.lazy_load()
    for doc in docs:
        doc.page_content = clean_text(doc.page_content)
        doc.metadata.update({"product": product})
    return docs

async def fetch_youtube_reviews(product, count=3):
    youtube_urls = await fetch_google_search_results(f"{product} review youtube", count, type="videos")

    transcript_docs = await process_urls(youtube_urls, product)
    
    return transcript_docs

async def add_product_reviews_to_collection(vector_store_from_client, product):
    load_dotenv(override=True)
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    
    print("Starting to process ", product)
    print(datetime.datetime.now())
    
    website_reviews_task = asyncio.create_task(fetch_website_reviews(product))
    youtube_reviews_task = asyncio.create_task(fetch_youtube_reviews(product))
    
    website_reviews = await website_reviews_task
    youtube_reviews = await youtube_reviews_task
    
    for doc in website_reviews:
        doc.metadata.update({"product": product})
    
    all_docs = itertools.chain(website_reviews, youtube_reviews)
    split_docs = text_splitter.split_documents(all_docs)
    
    uuids = [str(uuid4()) for _ in range(len(split_docs))]
    vector_store_from_client.add_documents(documents=split_docs, ids=uuids)
    
    print(f"Added {len(split_docs)} documents to the collection for {product}")
    print(datetime.datetime.now())
    
def get_candidates_list(prompt):
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

    model = ChatOpenAI(openai_api_key=OPENAI_API_KEY, model="gpt-4o-mini")
    parser = StrOutputParser()
    chain = model | parser

    question = f"What are the top 5 {prompt} of 2024, give your response first as a plain text format exactly like this [p1,p2,p3,p4,p5]. Replace p1 to p5 with the product name and respond nothing else."
    # print(question)
    output = chain.invoke(question)
    # print(output)
    candidates_list = output.strip("[]").split(",")
    # print("Candidates: ", candidates_list)
    return candidates_list

def build_response(query, vector_store_from_client: Chroma, candidates):
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    context = ""
    embeddings = OpenAIEmbeddings()
    for candidate in candidates:
        print(candidate)
        responses = vector_store_from_client.similarity_search_by_vector(
            embedding=embeddings.embed_query(candidate),
            k=3,
            # filter={"product": candidate}
        )
        print("HI")
        print (responses)
        context += "\n\n".join(
            [f"Category: {result.metadata['category']}\nContent: {result.page_content}" for result in responses['documents']]
        )

    question = f""""
        Reviews: {context}
        Based on the reviews, what are the top 5 {query} of 2024?
    """
    print(question)

    # model = ChatOpenAI(openai_api_key=OPENAI_API_KEY, model="gpt-4o-mini")
    # parser = StrOutputParser()
    # chain = model | parser
    # response = chain.invoke(question)
    # print(response)

async def parse(query):
    load_dotenv(override=True)
    global vector_store_from_client
    vector_store_from_client = setup_chroma_client()
    candidates = get_candidates_list(query)
    print("Candidates: ", candidates)
    tasks = [add_product_reviews_to_collection(vector_store_from_client, candidate) for candidate in candidates]
    await asyncio.gather(*tasks)
    return candidates