---
layout: post
title: "Start With Context: Building the Retrieval Core for Agentic Apps"
date: 2026-04-29 06:47:47 -0400
comments: true
categories: AI
tags: [mongodb, ai, langchain, haystack, llamaindex, voyage]
image: /images/mongodb-ai-banner.png
---

*Before you add planners, crews, or graph-shaped orchestration, build the part that decides what the model should actually see. In this first post, we’ll start an enterprise support copilot and give it the one capability every future agent depends on: retrieval that doesn’t fall apart in production.*

In a recent post I made the case that MongoDB can serve as [the "brain" of a modern AI application](https://alexbevi.com/blog/2026/04/15/mongodb-as-the-brain-of-modern-ai-applications/) by combining durable state, retrieval, and application data in one place. That framing still holds, but brains are only useful if they can recall the right thing at the right time. I wanted to dig into agentic application development in more detail in a series of posts, so for the first real entry in this series, I want to start one layer below "agents" and one layer above raw storage: the context layer. 

That might sound slightly less glamorous than "multi-agent orchestration," which is exactly why it matters. Most enterprise AI systems do not fail because they lack a clever planner. They fail because the model sees the wrong document, too much irrelevant text, or none of the operational data that actually matters.

To make this concrete, the application thread for this series will be an **enterprise support escalation copilot** for a B2B SaaS team. By the end of the series, it should be able to answer questions about incidents, remember previous escalations, pull account context, and coordinate specialized agents when needed. Today, though, we’re giving it its first useful skill: finding the right context for the job.

Think about the kind of question a real support engineer asks:

> "Acme’s enterprise tenant started seeing `INV-4421` after upgrading to `3.8`. Did we see this before, is there a known workaround, and does it affect EU clusters only?"

That is not a pure semantic search problem. It is part natural language, part exact identifier lookup, part metadata filtering, and part ranking problem. Error codes matter. Version numbers matter. Tenant boundaries matter. Timing matters. That’s why this is such a good place to start - and to solve this problem we'll dig in with [MongoDB](https://www.mongodb.com/products/platform/atlas-database) and [Voyage AI](https://www.mongodb.com/docs/voyageai/).

[MongoDB Vector Search](https://www.mongodb.com/docs/atlas/atlas-vector-search/vector-search-overview) is built to search vector data alongside the rest of your operational data, supports filtering on other fields in the collection, and can be combined with full-text search for hybrid retrieval. MongoDB’s hybrid search documentation explicitly describes combining semantic and full-text search results with Reciprocal Rank Fusion, which is exactly what you want when a query mixes fuzzy intent with exact strings like issue IDs, SKUs, or feature flags.

On the retrieval-model side, Voyage provides high-accuracy embedding and reranking models, including newer capabilities like contextualized chunk embeddings, multimodal embeddings, and rerankers designed to refine the top candidate set after initial retrieval. MongoDB Atlas now also exposes Voyage models through its Embedding and Reranking API, currently in preview, which means you can either call Voyage models directly or keep retrieval models, vector search, and operational data closer together under Atlas.

So what does the retrieval core for our support copilot actually do?

First, it stores source material in MongoDB: runbooks, release notes, KB articles, previous incident reviews, ticket summaries, and whatever structured account data the support flow needs. Then it chunks the long-form content, embeds it with Voyage, and stores the vectors with the source text and metadata. At query time, it narrows scope using metadata like tenant, product, region, or severity; retrieves candidates semantically and lexically; reranks the best matches; and only then hands a compact, relevant context window to the LLM. In other words: don’t ask the model to be psychic when the database can be specific. 

There are a lot of AI frameworks right now, and they absolutely do not all feel the same. But this is the first important pattern in the series: **the framework should shape the developer experience, not force you to redesign the data layer every six months**. The retrieval architecture is the stable part. MongoDB and Voyage AI are the stable parts. LangChain, LlamaIndex, Haystack, LangGraph, CrewAI, or whatever comes next should be able to sit on top of that foundation. 

## A framework-agnostic mental model

Before jumping into code, here is the mental model I’d keep fixed no matter which framework you prefer:

1. Put source documents and operational records in MongoDB.
2. Generate embeddings with Voyage.
3. Index vector fields and filter fields in MongoDB.
4. Use semantic retrieval for meaning.
5. Use full-text retrieval for exact strings.
6. Rerank the candidate set before generation.
7. Return only the context the model actually needs.

That shape maps cleanly to both MongoDB Vector Search and Voyage’s model stack. MongoDB handles vector indexes, full-text search, filterable metadata, and live application data; Voyage handles embeddings and reranking; the framework becomes the control surface. 

## Approach 1: LangChain for the shortest path from data to grounded answers

If the goal is to get a retrieval-backed application running quickly, LangChain remains a very practical starting point. [MongoDB’s LangChain integration](https://www.mongodb.com/docs/atlas/ai-integrations/langchain/) supports vector search, full-text search, and a hybrid retriever that combines both with Reciprocal Rank Fusion. It also supports pre-filtering with MQL expressions, which matters immediately for tenant scoping and product boundaries.

An illustrative version for our support copilot looks like this:

```python
import os

from langchain_voyageai import VoyageAIEmbeddings
from langchain_mongodb.vectorstores import MongoDBAtlasVectorSearch
from langchain_mongodb.retrievers.hybrid_search import MongoDBAtlasHybridSearchRetriever

embeddings = VoyageAIEmbeddings(
    api_key=os.environ["VOYAGE_API_KEY"],
    model="voyage-4",
)

vector_store = MongoDBAtlasVectorSearch.from_connection_string(
    connection_string=os.environ["MONGODB_URI"],
    namespace="support.context",
    embedding=embeddings,
    index_name="support_vector_index",
)

retriever = MongoDBAtlasHybridSearchRetriever(
    vectorstore=vector_store,
    search_index_name="support_search_index",
    k=8,
    fulltext_penalty=60.0,
    vector_penalty=60.0,
)

docs = retriever.invoke(
    "Acme tenant seeing INV-4421 after upgrading to 3.8"
)
```

In a production version, I’d pair that with metadata filters on fields like `tenant_id`, `product`, `region`, and `severity`, then pass the top candidates through a Voyage reranker before generation. The point is not that LangChain is magical. The point is that the MongoDB + Voyage retrieval story already fits the way LangChain applications are commonly assembled. 

## Approach 2: LlamaIndex when the center of gravity is the data itself

If LangChain often feels application-first, LlamaIndex tends to feel data-first. That makes it a very natural fit when you want to spend more time shaping ingestion, chunking, metadata, and query behavior.

Using [MongoDB’s LlamaIndex integration](https://www.mongodb.com/docs/atlas/atlas-vector-search/ai-integrations/llamaindex/) we can use `VoyageEmbedding` alongside `MongoDBAtlasVectorSearch` to make metadata filters very explicit, which is helpful for real enterprise retrieval where "give me the right answer" usually means "give me the right answer for *this tenant*, *this region*, and *this product line*." 

The shape is roughly:

```python
import os

from pymongo import MongoClient
from llama_index.embeddings.voyageai import VoyageEmbedding
from llama_index.vector_stores.mongodb import MongoDBAtlasVectorSearch
from llama_index.core import StorageContext, VectorStoreIndex
from llama_index.core.retrievers import VectorIndexRetriever
from llama_index.core.vector_stores import MetadataFilters, ExactMatchFilter

embed_model = VoyageEmbedding(
    voyage_api_key=os.environ["VOYAGE_API_KEY"],
    model_name="voyage-4",
)

mongo_client = MongoClient(os.environ["MONGODB_URI"])
vector_store = MongoDBAtlasVectorSearch(
    mongo_client,
    db_name="support",
    collection_name="context",
    vector_index_name="support_vector_index",
)

storage_context = StorageContext.from_defaults(vector_store=vector_store)

# docs is your loaded support corpus, such as runbooks, incident reviews,
# release notes, and ticket summaries.
vector_index = VectorStoreIndex.from_documents(
    docs,
    storage_context=storage_context,
    embed_model=embed_model,
)

filters = MetadataFilters(
    filters=[ExactMatchFilter(key="tenant_id", value="acme")]
)

retriever = VectorIndexRetriever(
    index=vector_index,
    filters=filters,
    similarity_top_k=10,
)

nodes = retriever.retrieve("Known workaround for INV-4421?")
```

What I like about this path is that it keeps the retrieval pipeline honest. You can see the data model. You can see the filter model. You can see how chunking choices affect what comes back. For article one in a series like this, that clarity is useful because it keeps us focused on context quality before we get distracted by agent loops.

## Approach 3: Haystack when you want explicit, composable pipelines

Haystack is a nice fit for teams that prefer explicit components over higher-level abstractions. [MongoDB’s Haystack integration](https://www.mongodb.com/docs/atlas/atlas-vector-search/ai-integrations/haystack/) uses a `MongoDBAtlasDocumentStore` with MongoDB retrievers, and the official tutorial pairs that with Voyage embedders. Haystack’s MongoDB integration also has separate semantic and full-text retrievers, which is useful when you want to make the retrieval strategy itself a first-class part of the pipeline.

A trimmed-down version looks like this:

```python
from haystack import Pipeline
from haystack.utils import Secret
from haystack_integrations.components.embedders.voyage_embedders import VoyageTextEmbedder
from haystack_integrations.document_stores.mongodb_atlas import MongoDBAtlasDocumentStore
from haystack_integrations.components.retrievers.mongodb_atlas import MongoDBAtlasEmbeddingRetriever

document_store = MongoDBAtlasDocumentStore(
    mongo_connection_string=Secret.from_env_var("MONGODB_URI"),
    database_name="support",
    collection_name="context",
    vector_search_index="support_vector_index",
    full_text_search_index="support_search_index",
)

pipeline = Pipeline()
pipeline.add_component("query_embedder", VoyageTextEmbedder(model="voyage-4"))
pipeline.add_component(
    "retriever",
    MongoDBAtlasEmbeddingRetriever(document_store=document_store, top_k=10),
)
pipeline.connect("query_embedder.embedding", "retriever.query_embedding")

result = pipeline.run(
    {"query_embedder": {"text": "Known workaround for INV-4421?"}}
)
```

This is probably the most "pipe and fitting" version of the three, and that is a compliment. For enterprise teams, explicit systems are often easier to debug, evaluate, and explain. And once again, the interesting part is not that the framework is different. It is that the same MongoDB + Voyage retrieval core still fits.

## Why MongoDB

The support copilot does not just need chunks in a vector store. It needs chunks, source documents, tenant metadata, ticket references, account records, release versions, and eventually execution state. MongoDB Vector Search lets you search semantic meaning alongside that operational data, pre-filter the search space using indexed fields, and combine vector and full-text retrieval when exact terms matter. Change streams then give you a way to react to new or updated records in real time, which is exactly what you want when incidents, tickets, or KB articles change during the workday. 

And if you want an even tighter platform story, MongoDB Atlas now exposes Voyage models directly through the [Embedding and Reranking API](https://www.mongodb.com/docs/voyageai/api-reference/overview/). That API is database-agnostic, but it pairs especially well with Atlas because it reduces the number of moving pieces needed to stand up a modern retrieval pipeline. Fewer services, fewer credentials, less trying to debug "why is this top result here?". 

This is also where the framework story becomes easier to reason about. LangChain, LlamaIndex, and Haystack all give you different ergonomics. MongoDB stays the system where the data lives. Voyage stays the retrieval layer that improves what gets surfaced. That is a much more durable architecture than betting everything on whichever orchestration framework happens to be loudest this quarter.

## What next?

Once the retrieval core is solid, adding agents becomes a lot more interesting.

In the next post, I’d take this same support copilot and add **short-term execution state** and **long-term memory**. LangGraph is a natural next step as it [separates persistence](https://docs.langchain.com/oss/python/langgraph/persistence) into checkpoints for thread state and stores for long-term memory, and MongoDB already has first-class integrations for both the LangGraph checkpointer and the long-term store. That is where the earlier "brain" idea becomes concrete: not just retrieval, but retrieval plus memory plus durable execution. 

The broader trend line is pretty clear, too. Agent frameworks are converging on durable state and memory. Retrieval models are getting richer with [contextualized chunk embeddings](https://docs.voyageai.com/docs/contextualized-chunk-embeddings), multimodal embeddings, and better rerankers. MongoDB Atlas is moving retrieval models and database capabilities closer together. The winning application architecture is the one that can absorb those changes without forcing you to rebuild your data layer every few months. MongoDB and Voyage AI fit that direction unusually well. 




