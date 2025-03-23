## Better Search 2
Provices search and question/answer capabilities.

The general idea is this: Sometimes I don't exactly remember what I am looking for, but I know whatever it is had been mentioned beside a specific event that I _do_ remember, say event-X. So we can instead search for event-X, then try to construct topical thread by examining surrounding text around event-X and reconstruct story threads from the indexed corpus.


To give a concrete example: Say we are trying to recall a conversation about ElasticSearch queries, but this is difficult to find because there are a lot of conversations about ES already. But if we remember there was also a conversation about about a very specific server-error near by, we can use the server-error as an anchor point, and reconstruct the neary threads, one of which will be the ES queries we are looking for.
 

This also provides a basic RAG question and answer capability for kicks and giggles.


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
