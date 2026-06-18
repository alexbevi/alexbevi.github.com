---
layout: post
title: "Two Lineages, One Framework: How AutoGen and Semantic Kernel Became the Microsoft Agent Framework"
date: 2026-06-18 15:14:48 -0400
comments: true
categories: AI
tags: [ai, frameworks]
image: /images/maf-post.webp
---

Microsoft's agent framework story is really a story about two teams solving different problems, a community-led spin-off of one lineage, and a packaging hazard that will silently break your code if you're not paying attention. If you've been watching this space — or just trying to pick a framework for a new project — here's the full arc.

## The Fork in the Road: Two Problems, Two Projects

By early 2023, the practical challenge of building LLM-powered applications had split into two distinct problems that nobody had cleanly solved.

The first was **enterprise integration**: how do you embed an LLM into an existing application with proper dependency injection, logging, telemetry, and reusable tool abstractions? The second was **multi-agent coordination**: how do you get several specialized agents to collaborate, argue, hand off work, and converge on a goal without you writing all the orchestration logic by hand?

Microsoft ended up with two separate projects, built by two separate teams, each solving one of these problems. They developed in parallel, later aligned, and eventually converged into one successor framework.

## Semantic Kernel (March 2023): The Enterprise SDK

[Semantic Kernel launched publicly on March 17, 2023](https://devblogs.microsoft.com/semantic-kernel/hello-world/), with C#/.NET as the primary supported path and Python already available in an experimental preview branch. Java support followed later. Its central abstraction was the `Kernel` object — a hub that wired together plugins, planners, memory, and model connectors.

**Plugins** (originally called "skills") were collections of native functions and prompt templates that an LLM could invoke. **Planners** asked the model to choose which plugin functions to compose in order to satisfy a user goal — though as [Microsoft's own documentation notes](https://learn.microsoft.com/en-us/semantic-kernel/concepts/planning), the framework has since moved away from prompt-based planning toward native function calling. Around this core sat the plumbing enterprise .NET teams expected: dependency injection, filters, telemetry hooks, and extensive connector support for vector stores and embedding services.

This was genuinely useful. If you had an existing enterprise application and wanted to add LLM capabilities without throwing away your architecture, Semantic Kernel gave you a structured, testable way to do it.

What early Semantic Kernel didn't give you was any first-class concept of multiple agents. A `Kernel` plus a planner could compose tools, but it did not originally model agents negotiating with each other, a coding agent handing a result to a review agent, or a team of agents coordinating around a shared task.

That changed over time. Microsoft introduced agent abstractions and multi-agent support in Semantic Kernel during 2024, and Semantic Kernel Agents became generally available in April 2025. By then, Semantic Kernel had sequential, concurrent, group-chat, handoff, and Magentic-style orchestration patterns. The better historical claim is not that Semantic Kernel never supported agents, but that its original center of gravity was enterprise application integration rather than conversational multi-agent orchestration.

## AutoGen (August 2023): Conversation as a Programming Model

AutoGen came from a completely different direction. The foundational paper — ["AutoGen: Enabling Next-Gen LLM Applications via Multi-Agent Conversation"](https://arxiv.org/abs/2308.08155) by Qingyun Wu, Gagan Bansal, Chi Wang, and eleven co-authors — landed on arXiv on August 16, 2023. Its documented proposition was flexible programming of multi-agent conversation patterns and reusable infrastructure for building LLM applications. In practice, the big idea felt simple: conversation could become a powerful programming model.

Instead of writing imperative orchestration logic, you defined agents (`AssistantAgent`, `UserProxyAgent`) with system prompts and tools, dropped them into a `GroupChat` with a `GroupChatManager`, and let them reach a goal by exchanging messages. Code execution was first-class: a `UserProxyAgent` could run model-generated Python in a Docker sandbox and feed the results back into the conversation. The pattern was surprisingly expressive — two-agent debate, critic-and-coder loops, and tool-use chains all fell out naturally from the same model.

AutoGen spread fast in the research community precisely because it was easy to prototype with. But it had real production weaknesses: the `GroupChat` manager's speaker-selection logic was opaque, the synchronous execution model didn't scale, and the architecture made it hard to add proper observability or async workflows.

## The Fork: AG2 Splits from AutoGen

By late 2024, the original AutoGen lineage had split. **AG2**, led by Chi Wang and Qingyun Wu, the paper's primary authors, positioned itself as a spin-off and evolution of AutoGen with an independent organization and open governance. It lives at [ag2ai/ag2](https://github.com/ag2ai/ag2) on GitHub. Its modifications and additions are Apache 2.0, while inherited AutoGen code remains under the original MIT license.

Meanwhile, Microsoft shipped **AutoGen v0.4** in January 2025 as a complete rewrite. The new architecture was built around an asynchronous, event-driven actor model with a clean three-layer API:

- **`autogen-core`** — the async runtime, message passing, and actor primitives
- **`autogen-agentchat`** — the high-level `AssistantAgent`, `GroupChat`, and team abstractions familiar from v0.2
- **`autogen-ext`** — extensions for specific models, tools, and integrations

The layered design let you drop down to `autogen-core` for fine-grained control or stay at `autogen-agentchat` for the familiar conversational API. But it was a breaking change from v0.2, and teams that had built on the original AutoGen now had to choose: follow Microsoft to v0.4, or follow the original authors to AG2.

## ⚠️ The `pip install autogen` Packaging Hazard

Before going further, there is a concrete gotcha you will hit if you're not careful.

The PyPI package name `autogen` is **not** Microsoft's current AutoGen. The name existed years before the split, but as of June 2026 it is controlled and used as an alias for AG2. Installing it silently gives you AG2's API, not Microsoft's rewritten AutoGen packages, with no error or warning. If you're following Microsoft's docs, you'll get an API mismatch that can be genuinely confusing to debug.

The correct install commands are:

```bash
# Microsoft AutoGen v0.4 (AgentChat plus OpenAI extension)
pip install -U "autogen-agentchat" "autogen-ext[openai]"

# AG2 (the community fork, maintained by the original authors)
pip install ag2

# Microsoft Agent Framework (the current successor to both)
pip install agent-framework
```

This has caught real developers. If your imports are failing or the API doesn't match the docs, check `pip show autogen` first — there's a good chance you have the wrong package entirely. The [AG2 migration guide](https://ag2ai.github.io/ag2/docs/migration-guide) and [AutoGen v0.4 docs](https://microsoft.github.io/autogen/stable/user-guide/agentchat-user-guide/quickstart.html) both call this out explicitly, but it's easy to miss if you're moving fast.

## The Microsoft Agent Framework (October 2025 to April 2026): The Merger

On October 1–2, 2025, Microsoft announced the public preview of the **Microsoft Agent Framework** — `agent-framework` on PyPI, `Microsoft.Agents.AI` on NuGet. On April 3, 2026, [Microsoft released Agent Framework 1.0 for both Python and .NET](https://devblogs.microsoft.com/agent-framework/microsoft-agent-framework-version-1-0/), describing it as production-ready, with stable APIs and a commitment to long-term support. [Microsoft's own documentation](https://learn.microsoft.com/en-us/agent-framework/overview/) is explicit about what this is: "the direct successor" to *both* Semantic Kernel and AutoGen, "created by the same teams."

The merger is architectural, not just organizational. The Agent Framework takes Semantic Kernel's enterprise plumbing — session-based state management, type safety, filters, telemetry, and the full connector ecosystem — and combines it with AutoGen's multi-agent orchestration patterns. On top of that foundation it unifies, productizes, and stabilizes capabilities that had previously been scattered across the predecessor projects:

**Graph-based workflows with type-safe routing.** Workflows connect executors and edges. Executors may wrap agents, ordinary functions, or deterministic business logic. Transitions are typed, so the compiler (in .NET) or runtime (in Python) can catch routing errors before they surface as mysterious failures at 2am.

**Checkpointing and resumability.** Long-running workflows can be persisted and resumed. This is the feature that makes human-in-the-loop genuinely practical — a workflow can pause, wait for human input or approval, and pick up where it left off.

**First-class human-in-the-loop.** Rather than relying only on a `UserProxyAgent`-style workaround, the framework supports human interaction through request/response mechanisms such as `RequestPort`, `ctx.request_info()`, response handlers, and approval-required tools that can suspend and later resume a workflow.

**Unified observability.** Semantic Kernel's telemetry hooks and AutoGen's tracing capabilities are merged into a single instrumentation layer, with OpenTelemetry support throughout.

Agent Framework 1.0 is available for both Python and .NET. Some adjacent features remain preview, but the core agent and workflow APIs are now the production path Microsoft is supporting.

## What Should You Use Today?

The landscape has four real options. Here's the honest breakdown:

**Microsoft Agent Framework 1.0** — Use this for new production projects, especially if you're in a Microsoft/Azure ecosystem or need stable APIs, Microsoft support, graph workflows, telemetry, checkpointing, or .NET/Python parity. It reached 1.0 on April 3, 2026 and is now the production-ready, long-term-supported successor to Semantic Kernel and AutoGen. The [quickstart](https://learn.microsoft.com/en-us/agent-framework/quickstart) is the right place to start.

**AG2** — Use this if you want to stay on the conversational `ConversableAgent` model, you have existing AutoGen 0.2.x-style code, or you want a framework governed outside Microsoft's roadmap. It is actively maintained and the community is engaged, but do not treat the current API as a fully settled 1.0 surface: AG2's own roadmap says the project is on the path to v1.0, the current framework will go through deprecations and move into maintenance mode, and the beta framework will become the official v1.0 API. You can install it as either `pip install ag2` or `pip install autogen` — both resolve to the same package — but `ag2` is the canonical name.

**Microsoft AutoGen v0.4** — The async rewrite is solid engineering, but the Microsoft AutoGen repository now says the project is in maintenance mode, will receive no new features or enhancements, and is community-managed going forward. Existing deployments can keep running, and the concepts map cleanly to the Agent Framework, but new strategic projects should start with Agent Framework and existing users should plan migration.

**Semantic Kernel 1.x standalone** — Still supported and still useful for existing applications, especially plugin-heavy .NET systems. But Microsoft has said most new agent-development investment will go into Agent Framework, so new multi-agent development should usually start there rather than in Semantic Kernel directly.

---

*Sources: [Semantic Kernel launch post](https://devblogs.microsoft.com/semantic-kernel/hello-world/) · [Semantic Kernel agents announcement](https://devblogs.microsoft.com/agent-framework/introducing-agents-in-semantic-kernel/) · [AutoGen arXiv paper](https://arxiv.org/abs/2308.08155) · [AutoGen v0.4 announcement](https://www.microsoft.com/en-us/research/blog/autogen-v0-4-reimagining-the-foundation-of-agentic-ai-for-scale-extensibility-and-robustness/) · [Microsoft Agent Framework overview](https://learn.microsoft.com/en-us/agent-framework/overview/) · [Microsoft Agent Framework 1.0 announcement](https://devblogs.microsoft.com/agent-framework/microsoft-agent-framework-version-1-0/) · [Agent Framework workflows](https://learn.microsoft.com/en-us/agent-framework/workflows/) · [Agent Framework human-in-the-loop docs](https://learn.microsoft.com/en-us/agent-framework/workflows/human-in-the-loop) · [Microsoft AutoGen repository](https://github.com/microsoft/autogen) · [AG2 repository](https://github.com/ag2ai/ag2) · [PyPI autogen package](https://pypi.org/project/autogen/) · [PyPI autogen 0.1.0](https://pypi.org/project/autogen/0.1.0/)*
