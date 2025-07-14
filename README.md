## Better Search 2
Provides search and question/answer capabilities over documents.

This project was originally developed as a way to search and extract sibling threads from documents based on semantic similarities. Imagine a paragraph that mentions topic X and topic Y, when the paragraph is retrieved, it not only shows topic X but also pulls out relevant information about topic Y across the entire collection.

In practice, this is useful for cue-based recalls and associative memory triggers. For example:
- There is something important on day X, but I can't remember what it was.
- The authors made a few interesting points in their literature review; I can't recall what they are.

In spirit this is not unlike various RAG/GraphRAG techniques that aimed to expose relationships within the corpus. So the scope of the project has expanded to incorporate and to cover general QA techniques as well.


### Setup
Rename `env.sample` to `env` and fill out all variables.


### Run
```
Usage:
    python chroma_db.py clear
    python chroma_db.py add <filepath>
    python chroma_db.py query <querystring>
    python chroma_db.py rag <querystring>
    python chroma_db.py stats
```
