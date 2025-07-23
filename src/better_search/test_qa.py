import os
from dotenv import load_dotenv
from .openai import AIClient
from .chroma import ChromaDB
from .document import DocumentExtractor
from .util import print_hex_color

load_dotenv()

API_TOKEN = os.getenv("API_TOKEN")
API_URL = os.getenv("API_URL")

ai_client = AIClient(
    base_url = API_URL,
    token = API_TOKEN
)
chromadb = ChromaDB("/Users/dchang/workspace/better-search2/db")
chromadb.load_collection("v1536")


question = "What are the ethnical considerations in the paper 2406.02030v2.pdf?" 
embeddings = ai_client.get_embeddings([question])

neighbours = chromadb.search(embeddings[0], num_results = 10)
metadatas = neighbours["metadatas"][0]
texts = list(map(lambda x: x["text"], metadatas))
texts = "\n\n".join(texts)


print_hex_color(texts, "#22bb88")


prompt = f"""
Use the following knowledge chunks as additional knoledge to answer the question, if you cannot answer the question,
return the string 'I do not have the answer'.

{texts}


The question is:

{question}
"""

answer = ai_client.get_completion(prompt)
print("===")
print_hex_color(answer, "#FF8800")

