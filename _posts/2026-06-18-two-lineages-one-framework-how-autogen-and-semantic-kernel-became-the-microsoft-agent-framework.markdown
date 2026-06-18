---
layout: post
title: "Two Lineages, One Framework: How AutoGen and Semantic Kernel Became the Microsoft Agent Framework"
date: 2026-06-18 15:14:48 -0400
comments: true
categories: AI
tags: [ai, frameworks]
image: /images/maf-post.webp
---

Microsoft's agent framework story is really a story about two teams solving different problems, a community fork born from disagreement, and a packaging hazard that will silently break your code if you're not paying attention. If you've been watching this space — or just trying to pick a framework for a new project — here's the full arc.

## The Fork in the Road: Two Problems, Two Projects

By early 2023, the practical challenge of building LLM-powered applications had split into two distinct problems that nobody had cleanly solved.

The first was **enterprise integration**: how do you embed an LLM into an existing application with proper dependency injection, logging, telemetry, and reusable tool abstractions? The second was **multi-agent coordination**: how do you get several specialized agents to collaborate, argue, hand off work, and converge on a goal without you writing all the orchestration logic by hand?

Microsoft ended up with two separate projects, built by two separate teams, each solving one of these problems. They would compete internally for years before eventually merging.

## Semantic Kernel (March 2023): The Enterprise SDK

[Semantic Kernel launched publicly on March 17, 2023](https://devblogs.microsoft.com/semantic-kernel/hello-world/), initially in C#/.NET, then Python and Java. Its central abstraction was the `Kernel` object — a hub that wired together plugins, planners, memory, and model connectors.

**Plugins** (originally called "skills") were collections of native functions and prompt templates that an LLM could invoke. **Planners** asked the model to choose which plugin functions to compose in order to satisfy a user goal — though as [Microsoft's own documentation notes](https://learn.microsoft.com/en-us/semantic-kernel/concepts/planning), the framework has since moved away from prompt-based planning toward native function calling. Around this core sat the plumbing enterprise .NET teams expected: dependency injection, filters, telemetry hooks, and extensive connector support for vector stores and embedding services.

This was genuinely useful. If you had an existing enterprise application and wanted to add LLM capabilities without throwing away your architecture, Semantic Kernel gave you a structured, testable way to do it.

What it didn't give you was any first-class concept of multiple agents. A `Kernel` plus a planner could compose tools, but it had no abstraction for agents negotiating with each other, a human approving a step mid-run, or a coding agent handing a result to a review agent. As [Microsoft's Agent Framework overview](https://learn.microsoft.com/en-us/agent-framework/overview/agent-framework-overview) later conceded: Semantic Kernel _"provided connectors and telemetry but lacked multi-agent flexibility."_

## AutoGen (August 2023): Conversation as a Programming Model

AutoGen came from a completely different direction. The foundational paper — ["AutoGen: Enabling Next-Gen LLM Applications via Multi-Agent Conversation"](https://arxiv.org/abs/2308.08155) by Qingyun Wu, Gagan Bansal, Chi Wang, and eleven co-authors — landed on arXiv on August 16, 2023. Its thesis was direct: treat *conversation* as the universal programming abstraction.

Instead of writing imperative orchestration logic, you defined agents (`AssistantAgent`, `UserProxyAgent`) with system prompts and tools, dropped them into a `GroupChat` with a `GroupChatManager`, and let them reach a goal by exchanging messages. Code execution was first-class: a `UserProxyAgent` could run model-generated Python in a Docker sandbox and feed the results back into the conversation. The pattern was surprisingly expressive — two-agent debate, critic-and-coder loops, and tool-use chains all fell out naturally from the same model.

AutoGen spread fast in the research community precisely because it was easy to prototype with. But it had real production weaknesses: the `GroupChat` manager's speaker-selection logic was opaque, the synchronous execution model didn't scale, and the architecture made it hard to add proper observability or async workflows.

## The Fork: AG2 Splits from AutoGen

By late 2024, tension between the original AutoGen research authors and Microsoft's product direction had reached a breaking point. The community fork that resulted — led by Chi Wang and Qingyun Wu, the paper's primary authors — became **AG2**, initially positioned as the continuation of the AutoGen 0.2.x lineage. It lives at [ag2ai/ag2](https://github.com/ag2ai/ag2) on GitHub and is governed independently under Apache 2.0.

Meanwhile, Microsoft shipped **AutoGen v0.4** in January 2025 as a complete rewrite. The new architecture was built around an asynchronous, event-driven actor model with a clean three-layer API:

- **`autogen-core`** — the async runtime, message passing, and actor primitives
- **`autogen-agentchat`** — the high-level `AssistantAgent`, `GroupChat`, and team abstractions familiar from v0.2
- **`autogen-ext`** — extensions for specific models, tools, and integrations

The layered design let you drop down to `autogen-core` for fine-grained control or stay at `autogen-agentchat` for the familiar conversational API. But it was a breaking change from v0.2, and teams that had built on the original AutoGen now had to choose: follow Microsoft to v0.4, or follow the original authors to AG2.

## ⚠️ The `pip install autogen` Packaging Hazard

Before going further, there is a concrete gotcha you will hit if you're not careful.

The PyPI package name `autogen` is **not** Microsoft's AutoGen. It is an alias for AG2 — the community fork — registered by the AG2 maintainers after the split. Installing it silently gives you AG2's API, not Microsoft's, with no error or warning. If you're following Microsoft's docs, you'll get an API mismatch that can be genuinely confusing to debug.

The correct install commands are:

```bash
# Microsoft AutoGen v0.4 (agentchat layer)
pip install autogen-agentchat

# AG2 (the community fork, maintained by the original authors)
pip install ag2

# Microsoft Agent Framework (the current successor to both)
pip install agent-framework
```

This has caught real developers. If your imports are failing or the API doesn't match the docs, check `pip show autogen` first — there's a good chance you have the wrong package entirely. The [AG2 migration guide](https://ag2ai.github.io/ag2/docs/migration-guide) and [AutoGen v0.4 docs](https://microsoft.github.io/autogen/stable/user-guide/agentchat-user-guide/quickstart.html) both call this out explicitly, but it's easy to miss if you're moving fast.

## The Microsoft Agent Framework (October 2025): The Merger

On October 1–2, 2025, Microsoft announced the public preview of the **Microsoft Agent Framework** — `agent-framework` on PyPI, `Microsoft.Agents.AI` on NuGet. [Microsoft's own documentation](https://learn.microsoft.com/en-us/agent-framework/overview/agent-framework-overview) is explicit about what this is: "the direct successor" to *both* Semantic Kernel and AutoGen, "created by the same teams."

The merger is architectural, not just organizational. The Agent Framework takes Semantic Kernel's enterprise plumbing — session-based state management, type safety, filters, telemetry, and the full connector ecosystem — and combines it with AutoGen's multi-agent orchestration patterns. On top of that foundation it adds capabilities neither predecessor had:

**Graph-based workflows with type-safe routing.** Agents are nodes in a directed graph. Transitions between nodes are typed, so the compiler (in .NET) or runtime (in Python) can catch routing errors before they surface as mysterious failures at 2am.

**Checkpointing and resumability.** Long-running workflows can be persisted and resumed. This is the feature that makes human-in-the-loop genuinely practical — a workflow can pause, wait for a human approval, and pick up exactly where it left off.

**First-class human-in-the-loop.** Rather than bolting on a `UserProxyAgent` workaround, the framework has explicit `HumanInTheLoop` nodes with configurable approval and intervention patterns.

**Unified observability.** Semantic Kernel's telemetry hooks and AutoGen's tracing capabilities are merged into a single instrumentation layer, with OpenTelemetry support throughout.

The Python SDK is available now in preview. The .NET SDK (`Microsoft.Agents.AI`) targets the same concepts with idiomatic C# APIs.

## What Should You Use Today?

The landscape has three real options. Here's the honest breakdown:

**Microsoft Agent Framework** — Use this for new production projects, especially if you're in a Microsoft/Azure ecosystem or need enterprise features (telemetry, DI, type-safe routing, checkpointing). It's in public preview as of October 2025, so expect some API churn, but it's the direction Microsoft is investing in. The [quickstart](https://learn.microsoft.com/en-us/agent-framework/quickstart) is the right place to start.

**AG2** — Use this if you want to stay on the conversational `ConversableAgent` model, you have existing AutoGen 0.2.x code, or you want a framework governed outside Microsoft's roadmap. It's actively maintained by the original AutoGen authors under Apache 2.0, the API is stable, and the community is engaged. You can install it as either `pip install ag2` or `pip install autogen` — both resolve to the same package — but `ag2` is the canonical name.

**AutoGen v0.4** — The async rewrite is solid engineering, but with the Agent Framework now positioned as the official successor, new projects should probably start there instead. If you're already on v0.4, you're not in a bad place — the concepts map cleanly to the Agent Framework — but the migration path is the direction of travel.

**Semantic Kernel standalone** — Still maintained and still useful for single-agent, plugin-heavy applications, particularly in .NET. But new multi-agent development should go to the Agent Framework, not Semantic Kernel directly.

---

*Sources: [Semantic Kernel launch post](https://devblogs.microsoft.com/semantic-kernel/hello-world/) · [AutoGen arXiv paper](https://arxiv.org/abs/2308.08155) · [Microsoft Agent Framework overview](https://learn.microsoft.com/en-us/agent-framework/overview/agent-framework-overview) · [AutoGen v0.4 quickstart](https://microsoft.github.io/autogen/stable/user-guide/agentchat-user-guide/quickstart.html) · [AG2 migration guide](https://ag2ai.github.io/ag2/docs/migration-guide) · [Medium first-look](https://medium.com/@info_90506/microsoft-agent-framework-a-comprehensive-first-look-d1319c0d72fd)*
