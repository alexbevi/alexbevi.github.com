---
layout: post
title: "Persistent multi-agent conversations with the OpenAI Agents SDK and MongoDB"
date: 2026-04-27 12:50:00 -0400
comments: true
categories: AI
tags: [mongodb, ai, python]
image: /images/mongodb-ai.png
---

*Version 0.14.2 added a `MongoDBSession` backend; here's a working multi-agent customer-support demo that uses it, and the documents it leaves behind.*

The OpenAI Agents SDK has shipped session backends for SQLite, SQLAlchemy, Redis, and Dapr for a while now. With **0.14.2** (April 2026), [`MongoDBSession` joined that list](https://openai.github.io/openai-agents-python/sessions/), and 0.14.6 added the docs page. If you're already running MongoDB for application data, this is the moment to stop standing up a second store just to remember what the agent said three turns ago. The demo for this walkthrough is a small e-commerce support app with three handoff-connected agents and one MongoDB instance behind everything: customers, orders, support articles, **and** the conversation history. 

Repo: <https://github.com/alexbevi/mongodb-openai-agents-sdk-example>.

## What you'll build

A CLI customer-support agent that identifies the user from MongoDB, hands off between a triage agent, an order-support agent, and a knowledge-base agent, and persists every turn (user message, tool call, tool output, assistant reply, handoff) to MongoDB via `MongoDBSession`. You quit, restart the process, log in with the same email, and the agent picks up the thread — no re-explaining the return you started yesterday.

## Why MongoDB for sessions

A session backend has three jobs: store one item per turn, return them in order on the next run, and not corrupt itself when two processes write at once. The interesting part for MongoDB is how naturally each of those maps to things the database already does.

**Items in a session are heterogeneous.** A turn can be a user message, a tool call, a tool result, an assistant message, or a handoff record — each with its own shape. A document store takes those payloads as-is. There's no `messages` table you have to migrate every time the SDK adds a new run-item type, and no JSON column to parse around.

**Ordering is the hard part, and `$inc` is built for it.** `MongoDBSession` stamps each message with a monotonically increasing `seq` counter — the SDK docs call this out explicitly: it preserves ordering across concurrent writers and processes. That's a single-document atomic increment, not a distributed lock or an optimistic-retry loop. Two FastAPI workers handling the same `session_id` won't interleave.

**One store, one connection pool.** This is the angle the demo actually showcases. The `ecommerce_support` database holds `customers`, `orders`, and `support_articles` *next to* `agent_sessions` and `agent_messages`. Tools query operational data, the SDK persists turns, and they share the same `AsyncMongoClient`. Adding session memory cost zero new infrastructure.

## Walkthrough

### 1. Prerequisites

Python 3.10+, an OpenAI API key, and either a local `mongod` or a [MongoDB Atlas](https://www.mongodb.com/cloud/atlas/register) cluster. Nothing in the demo requires Atlas-only features — a 27017 on localhost is fine.

### 2. Install

`requirements.txt` pins the new extra:

```text
openai-agents[mongodb]>=0.14.2
python-dotenv>=1.0.0
pymongo>=4.13
```

```bash
pip install -r requirements.txt
```

The `[mongodb]` extra pulls in `pymongo`'s async client; the `MongoDBSession` class lives at `agents.extensions.memory.MongoDBSession`.

### 3. Connect

The demo uses one shared `AsyncMongoClient` per process (the right pattern — sessions don't own the client, they share its pool):

```python
from pymongo.asynchronous.mongo_client import AsyncMongoClient

MONGODB_URI = os.environ.get("MONGODB_URI", "mongodb://localhost:27017")
DB_NAME = "ecommerce_support"

mongo_client = AsyncMongoClient(MONGODB_URI)
db = mongo_client[DB_NAME]

try:
    await mongo_client.admin.command("ping")
except Exception as exc:
    print(f"\nCannot connect to MongoDB ({MONGODB_URI}):\n  {exc}")
    return
```

### 4. Seed and identify

`python seed_data.py` loads three demo customers, five products, five orders with embedded line items, and seven support articles indexed for `$text` search. Then `main.py` looks the customer up so the triage agent doesn't have to ask for an email it already knows.

### 5. Instantiate the session

This is the integration:

```python
session_id = f"support_{email.replace('@', '_at_').replace('.', '_')}"
session = MongoDBSession(
    session_id=session_id,
    client=mongo_client,
    database=DB_NAME,
)

if not await session.ping():
    print("Warning: MongoDB session storage is unavailable.")

existing = await session.get_items()
```

Constructing with `client=` (rather than `MongoDBSession.from_uri(...)`) means the session shares the app's connection pool and `session.close()` becomes a no-op — the lifecycle stays with you. `session.ping()` is a real round-trip against MongoDB, useful for liveness probes.

### 6. Run

Pass `session=` to the runner. Everything else is the same SDK you already know:

```python
with trace("Customer Support", group_id=conversation_id):
    result = await Runner.run(
        current_agent,
        input=user_input,
        context=ctx,
        session=session,   # MongoDB stores every turn automatically
    )
```

Have a conversation, `quit`, run `python main.py` again with the same email, and the next message gets the full prior context prepended automatically.

## What MongoDB actually stored

After a few turns with `alice@example.com`, two collections show up in the `ecommerce_support` database. The interesting one is `agent_messages`. A representative document, abridged:

```js
{
  _id: ObjectId("6620d1f4..."),
  session_id: "support_alice_at_example_com",   // partition key for this conversation
  seq: 7,                                        // monotonically increasing turn order
  message_data: {                                // the SDK's run-item, stored as-is
    type: "function_call_output",
    call_id: "call_8b2...",
    output: "Return initiated for order ORD-1001.\nReason: Not powerful enough...\nEstimated refund: $1,484.98 (includes 10% Gold loyalty bonus)"
  },
  created_at: ISODate("2026-04-26T19:14:08.221Z")
}
```

Three fields earn their keep:

- **`session_id`** is the only field every read filters on. It's the partition key for "this conversation."
- **`seq`** is the integer that makes ordering deterministic. The SDK reads with `sort({ seq: 1 })` and writes with an atomic `$inc` against the matching `agent_sessions` document, which is what makes concurrent workers safe without a distributed lock.
- **`message_data`** is the SDK's run-item — a user message, tool call, tool output, assistant message, or handoff. Different shape every time. The document model just stores it.

`agent_sessions` holds one document per `session_id` with the current high-water `seq` and timestamps — that's the counter `$inc` operates on.

The SDK creates its indexes on first use (per the [sessions docs](https://openai.github.io/openai-agents-python/sessions/)). You'll see a compound index on `(session_id, seq)` on `agent_messages` (the only access pattern the SDK has — fetch ordered history for one session) and a unique index on `session_id` in `agent_sessions`.

## Production notes

For Atlas, swap the URI for `mongodb+srv://...` — `MongoDBSession` accepts it without any other change. If abandoned conversations accumulate, add a TTL index on `agent_messages.created_at` and old turns retire on their own.

Connection lifetime matters: keep one `AsyncMongoClient` per process, construct `MongoDBSession(client=...)` per request, and let the Runner do the rest. Don't reach for `MongoDBSession.from_uri(...)` in a web handler — it builds and tears down a client every call. The session needs read/write on the two configured collections (defaults `agent_sessions` and `agent_messages`, both overridable via `sessions_collection=` and `messages_collection=`). The `seq` counter keeps concurrent writers safe, but fanning the same `session_id` across processes will interleave their turns — safe, but probably not what the user meant.

## Try it yourself

```bash
git clone https://github.com/alexbevi/mongodb-openai-agents-sdk-example
cd mongodb-openai-agents-sdk-example
pip install -r requirements.txt
cp env.example .env          # set OPENAI_API_KEY and MONGODB_URI
python seed_data.py
python main.py
```

Required env vars: `OPENAI_API_KEY`, `MONGODB_URI` (defaults to `mongodb://localhost:27017`). Demo accounts: `alice@example.com` (Gold), `bob@example.com` (Standard), `carol@example.com` (Platinum).

## Where to go next

- The full session API surface — `get_items`, `add_items`, `pop_item`, `clear_session`, `ping` — is documented in the [Sessions overview](https://openai.github.io/openai-agents-python/sessions/), including the MongoDB-specific notes on collection naming and Atlas URIs.
- Wrap your `MongoDBSession` in [`OpenAIResponsesCompactionSession`](https://openai.github.io/openai-agents-python/sessions/) once threads grow long; it summarizes old turns server-side and rewrites the underlying session.
- The natural next MongoDB feature for this demo is [Atlas Vector Search](https://www.mongodb.com/docs/atlas/atlas-vector-search/) — store embeddings on `support_articles` and replace the `$text` query in `search_knowledge_base` with `$vectorSearch`. Same database, same client, one new index.