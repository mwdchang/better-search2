import os
from os.path import join, dirname
from dotenv import load_dotenv
import sys
import uuid
import hashlib
import chromadb
from openai import OpenAI
import textwrap


# Suppress index not existing messages
import logging
logging.getLogger("chromadb").setLevel(logging.ERROR)

dotenv_path = join(dirname(__file__), 'env')
load_dotenv(dotenv_path)

# Chromadb config
db_path = os.environ.get("db_path")
collection_name = os.environ.get("collection_name")

# OpenAI config
token = os.environ.get("token")
endpoint = os.environ.get("endpoint")


chroma_client = chromadb.PersistentClient(
    path = db_path
)
chroma_collection = chroma_client.get_or_create_collection(
    name=collection_name,
    metadata={"hnsw:space": "cosine"}
)

openai_client = OpenAI(
    base_url=endpoint,
    api_key=token,
)


def text_2_topics(text):
    model_name = "gpt-4o-mini"
    prompt = f"""
Here is a piece of text:

{text}

Extract up to 5 topics associated with the text, return it as a comma delimited list.
    """

    response = openai_client.chat.completions.create(
        messages = [
            {
                "role": "system",
                "content": "You are a helpful assistant with expertise in a large array of topics with expertize in information retrieval"
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature = 1.0,
        top_p = 1.0,
        max_tokens = 1000,
        model = model_name
    )
    return response.choices[0].message.content
    # topics = response.choices[0].message.content.split(",")
    # return list(map(lambda x: x.strip(), topics))


def texts_2_embeddings(text_list):
    model_name = "text-embedding-3-small"
    response = openai_client.embeddings.create(
        input = text_list,
        model=model_name,
    )
    return response.data


def read_file(filepath):
    text = ""
    with open(filepath, "r") as FH:
        text = FH.read()
    return text



def get_embedding(id):
    result = chroma_collection.get(ids=[id], include=["embeddings"])
    embedding = result["embeddings"][0]
    return embedding


# https://stackoverflow.com/questions/287871/how-do-i-print-colored-text-to-the-terminal
def yellow(s):
    return "\033[93m" + str(s) + "\033[0m"


def green(s):
    return "\033[92m" + str(s) + "\033[0m"


# See
# - https://stackoverflow.com/questions/78589963/insert-thousands-of-documents-into-a-chroma-db
def index_text(text, metadata):
    document_id = str(uuid.uuid4())
    if metadata is None:
        metadata = {}

    # Get topics
    document_topics = text_2_topics(text)

    # Chunk
    paragraphs = text.split("\n")
    paragraphs = list(filter(lambda x: x != "", paragraphs))

    chunk_ids = []
    metadatas = []
    for idx in range(len(paragraphs)):
        text_chunk = paragraphs[idx]
        hash_object = hashlib.sha256(text_chunk.encode())
        hash_hex = hash_object.hexdigest()

        # chunk_ids.append(str(uuid.uuid4()))
        chunk_ids.append(str(hash_hex))

        metadatas.append({
            "document_id": document_id,
            "chunk_id": hash_hex,
            "chunk_no": idx,
            "document_topics": document_topics,
            "part": idx,
            "text": text_chunk,
            # has filename
            **metadata
        })
    print(f"Number of paragraphs = {len(paragraphs)}")

    embedding_data = texts_2_embeddings(paragraphs)
    embeddings = list(map(lambda x: x.embedding, embedding_data))  # embedding_data[0].embedding

    # Do upsert so we can re-index
    print(f">>> {chunk_ids}")
    chroma_collection.delete(ids=chunk_ids)

    chroma_collection.add(
        embeddings = embeddings,
        ids = chunk_ids,
        metadatas = metadatas
    )


NUM_RESULTS = 3


def indent_wrap(text, width=120, indent=4):
    indentation = " " * indent  # Create an indent of 4 spaces
    wrapped_text = textwrap.fill(text, width=width, initial_indent=indentation, subsequent_indent=indentation)
    print(wrapped_text)


def query_text_3(text):
    embeddings = texts_2_embeddings([text])
    document_ids = []

    results = []

    # Search for the initial matching chunks
    raw_results = chroma_collection.query(
        query_embeddings = [embeddings[0].embedding],
        n_results = NUM_RESULTS,
    )


    initial_results = []
    processed_documents = []

    # Collect documents
    results_len = len(raw_results["ids"][0])
    print(f">> raw length {results_len}")

    for idx in range(results_len):
        chunk_id = raw_results["ids"][0][idx]
        dist = raw_results["distances"][0][idx]
        metadata = raw_results["metadatas"][0][idx]

        document_id = metadata["document_id"]
        chunk_no = metadata["chunk_no"]
        text = metadata["text"]
        filename = metadata["filename"]

        if document_id in processed_documents:
            continue

        initial_results.append({
            "document_id": document_id,
            "filename": filename,
            "chunk_id": chunk_id,
            "chunk_no": chunk_no,
            "dist": dist,
            "text": text
        })

        processed_documents.append(document_id)
        document_ids.append(document_id)


    # Do a secondary search
    l = len(initial_results)
    print(f">> filetered length {l}")

    for idx in range(l):
        item = initial_results[idx]

        print(f"[{yellow(item['filename'])}:{yellow(item['chunk_no'])}] {green(item['dist'])}")
        print(f"{item['text']}")

        result = {
            "document_id": item["document_id"],
            "chunk_id": item["chunk_id"],
            "filename": item["filename"],
            "related": []
        }


        # Get any other embeddings in the matched document that is not the chunk itself
        match_doc_embeddings = chroma_collection.get(
            where = {
                "$and": [
                    { "document_id": { "$in": [item["document_id"]] } },
                    { "chunk_id": { "$ne": item["chunk_id"] } }
                ]
            },
            include=["embeddings"]
        )

        embeddings = match_doc_embeddings["embeddings"]

        # print(len(embeddings))
        if len(embeddings) == 0:
            continue

        # Search for neighbours
        raw_results = chroma_collection.query(
            query_embeddings = embeddings,
            n_results = 4,
            where = {
                "document_id": {
                    "$nin": document_ids
                }
            }
        )
        secondary_results = []

        # Collect relevant matches
        relevant_results_len = len(raw_results["ids"][0])
        relevant_document_ids = []
        for idx in range(relevant_results_len):
            chunk_id = raw_results["ids"][0][idx]
            dist = raw_results["distances"][0][idx]

            metadata = raw_results["metadatas"][0][idx]
            document_id = metadata["document_id"]
            filename = metadata["filename"]
            chunk_no = metadata["chunk_no"]
            text = metadata["text"]

            secondary_results.append({
                "document_id": document_id,
                "filename": filename,
                "chunk_id": chunk_id,
                "chunk_no": chunk_no,
                "dist": dist,
                "text": text
            })

            relevant_document_ids.append(document_id)
            # indent_wrap(f"[{yellow(filename)}:{yellow(chunk_no)}] {green(dist)}")
            # indent_wrap(f"{text}")

            result["related"].append({
                "document_id": document_id,
                "chunk_id": chunk_id,
                "filename": filename
            })

        results.append(result)

        # Sort secondary
        secondary_results.sort(key=lambda x: x["filename"] + str(x["chunk_no"]))
        for idx in range(len(secondary_results)):
            item = secondary_results[idx]

            indent_wrap(f"[{yellow(item['filename'])}:{yellow(item['chunk_no'])}] {green(item['dist'])}")
            indent_wrap(f"{item['text']}")

        # print("")
        # print(results)
        # print("")


def rag(text):
    embedding_data = texts_2_embeddings([text])
    embeddings = list(map(lambda x: x.embedding, embedding_data))

    raw_results = chroma_collection.query(
        query_embeddings = embeddings,
        n_results = 4
    )

    results_len = len(raw_results["ids"][0])
    str_buffer = ""
    sources = []
    for idx in range(results_len):
        metadata = raw_results["metadatas"][0][idx]
        # print(metadata["text"])
        str_buffer = str_buffer + metadata["text"]
        str_buffer = str_buffer + "\n"

        chunk_no = metadata["chunk_no"]
        filename = metadata["filename"]

        sources.append(f"{filename} / {chunk_no} ")

    prompt = f"""
    Use the following statements/text to answer the question:

    {str_buffer}

    The question is:

    {text}

    if you do not know the anwer, return "I don't know the answer.".
    """

    model_name = "gpt-4o-mini"
    response = openai_client.chat.completions.create(
        messages = [
            {
                "role": "system",
                "content": "You are a helpful assistant with expertise in a large array of topics with expertize in information retrieval", 
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature = 1.0,
        top_p = 1.0,
        max_tokens = 1000,
        model = model_name
    )

    answer = response.choices[0].message.content
    print(f"The answer is:\n\n {answer}")
    print(f"Sources {sources}")



def stats():
    collections = chroma_client.list_collections()

    for collection in collections:
        name = collection.name
        col = chroma_client.get_or_create_collection(name=name)
        size = col.count()
        print(f"Collection '{name}' has {size} items.")


################################################################################
# main
################################################################################
args = sys.argv

if len(args) < 2:
    print("""
Usage:
    python chroma_db.py clear
    python chroma_db.py add <filepath>
    python chroma_db.py query <querystring>
    python chroma_db.py rag <querystring>
    python chroma_db.py stats
    """)
    exit(-1)

command = args[1]

if command == "add":
    file = args[2]
    print(f"Indexing ... {file}")
    text = read_file(file)
    index_text(text, { "filename": file } )
elif command == "query":
    text = args[2]
    print("Querying ... ")
    query_text_3(text)
elif command == "rag":
    text = args[2]
    print("RAG query...")
    rag(text)
elif command == "clear":
    print("Deleting collection ... ")
    chroma_client.delete_collection(name=collection_name)
else:
    print("Finding statistics")
    stats()
