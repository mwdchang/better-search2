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

test_file = "/Users/dchang/workspace/better-search2/2406.02030v2.pdf"
doc_extractor = DocumentExtractor()

chunks, metadatas, ids = doc_extractor.extract(test_file, {
    "filename": "2406.02030v2.pdf"
})
embeddings = ai_client.get_embeddings(chunks)

num_chunks = len(chunks)
cnt = 0
for embedding, metadata, id in zip(embeddings, metadatas, ids):
    cnt = cnt + 1
    chromadb.add_document_embedding(id, embedding, metadata)
    print(f"indexing {cnt} of {num_chunks} chunks")
