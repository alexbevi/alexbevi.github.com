---
layout: post
title: "Reverse Engineering a DOS Game with Ghidra and Codex"
date: 2026-03-14 06:13:05 -0400
comments: true
categories: Programming
tags: [programming, reverse-engineering, scummvm, ghidra]
image: /images/ghidra1/harvester_reverse_engineering_banner_1200x600.png
series: reverse_engineering_harvester
---
{% series_nav %}

As part of my series called ["Let's Adventure!"]({% post_url 2021-07-28-adventure-games-1980-1999 %}) I had a chance to revisit a lot of classic adventure games I loved growing up, but also experience some I'd missed or never heard of. One of those games was [Harvester]({% post_url 2024-02-23-harvester %}), which was just the right mix of weird characters and settings with a bizarre plot tieing everything together.

![](/images/adventure/harvester/harvest_012.png)

Though I wouldn't say the game was great, it was interesting enough to keep me engaged and even after playing through it still remains top of mind.

With the advent of agentic development tools like [Claude Code](https://claude.com/product/claude-code) or [Codex](https://openai.com/codex/), I figured I'd take a crack at reverse engineering Harvester with the goal of eventually reimplementing it as a game engine in [ScummVM](https://www.scummvm.org/).

## Tools

* [Visual Studio Code](https://code.visualstudio.com/)
* Codex (used via Visual Studio Code)
* [Ghidra](https://github.com/nationalsecurityagency/ghidra)
* [Ghidra MCP](https://github.com/bethington/ghidra-mcp)
* [Ghidra Loader for the LX/LE executable file format](https://github.com/yetmorecode/ghidra-lx-loader)

## Getting Started

The first step is almost always to just load the EXE into Ghidra and kicking off an initial analysis. Once the analysis is complete, I like to get a sense of what types of string constants are exposed that I may be able to anchor some logic to by inspecting. the [Defined Strings](https://www.ghidradocs.com/12.0.4_PUBLIC/help/Base/help/topics/ViewStringsPlugin/ViewStringsPlugin.htm).

What I'm looking for on a first pass is:

* resource filenames as constants (ex: `HARVEST.DAT`) as these can help point to where file I/O routines are
* error messages
* inventory item labels
* dialogue text
* names that might identify internal data structures
* character names

Since I didn't see any of these, I tried to decompress the executable in DOSBox using [`UNP.EXE`](https://bencastricum.nl/unp/). This didn't do anything as compression wasn't what was obfuscating the strings, but what I could see looked like memory management details - which lead me to believe the game was using a [DOS extender](https://en.wikipedia.org/wiki/DOS_extender) like `DOS/4GW`.

![](/images/ghidra1/ghidra-exe-extended.png)

`DOS/4GW` was the Watcom-packaged subset of Tenberry’s `DOS/4G`: a [32-bit DOS extender customized for the Watcom toolchain](https://openwatcom.org/ftp/manuals/current/pguide.pdf). Its job was to let a DOS program run in 386 protected mode with a flat, zero-based memory model, so developers could stop fighting 16-bit segmented memory and work with much larger address spaces. Just as importantly for games, `DOS/4GW` still mapped the first megabyte of physical memory into a shared linear address space, which meant code could still reach things like video RAM and BIOS data when needed.

## Unbinding the Extended EXE

To be able to make any meaningful progress, we need Ghidra to be able to analyze teh un-exetended EXE. After looking around I found a blog describing how to ["Disassemble DOS/4GW"](https://blog.torh.net/2015/10/30/disassemble-dos4gw/) which hinted at being able to use the SUNSYS Bind Utility to extract a [Linear Executable](https://en.wikipedia.org/wiki/Linear_Executable) from the extended EXE.

You can find a copy of the bind utility (`SB.EXE`) with the open source [DOS32A](https://web.archive.org/web/20210726190857/https://dos32a.narechk.net/index_en.html) DOS extender. Once downloaded, you can use this directly via [DOSBox](https://www.dosbox.com/) to unbind the EXE.

![](/images/ghidra1/dosbox-sb32a.png)

When running this against `HARVEST.EXE` it will produce a `HARVEST.LE`, which is the linear executable. Once we have this the next logical step would be to try and load it in Ghidra, but doing this doesn't quite work as Ghidra thinks the LE file is raw data.

## Decompiling a Linear Executable

To successfully start analyzing `HARVEST.LE`, we'll first need to install the [Ultimate Ghidra Loader for the LX/LE executable file format](https://github.com/yetmorecode/ghidra-lx-loader) extension. 

![](/images/ghidra1/ghidra-import-le.png)

After doing this and restarting Ghidra, the LE EXE format should be properly detected, and we can load this and begin our analysis. Since the goal is to develop a working [ScummVM game engine](https://wiki.scummvm.org/index.php/Engines), we'll be working on a [`harvester` branch of a ScummVM fork](https://github.com/alexbevi/scummvm/tree/harvester).

## Working with Ghidra via MCP

![](/images/ghidra1/ghidra-decompile-le.png)

The `HARVEST.LE` executable has now been analyzed and we have a much more informative listing of defined strings to anchor our reverse engineering efforts on. Since we'll be using Codex directly via Visual Studio Code, the next step is to setup Ghidra and [Ghidra MCP](https://github.com/bethington/ghidra-mcp).

This is fairly straightforward:

* Download Ghidra and unzip
* In vscode install the `openai.chatgpt` extension
* Open the Codex panel and just start chatting: 
    ```
    I've installed Ghidra at /path/to/extracted/ghidra and I want to work with it using 
    MCP. Download GhidraMCP from https://github.com/bethington/ghidra-mcp and install 
    it. Verify this is working once complete.
    ```
![](/images/ghidra1/vscode-01.png)

With GhidraMCP installed and working, we can dig into our initial reverse engineering attempt. I started off by developing an [`AGENTS.md`](https://gist.github.com/alexbevi/07560b7e82dd73527f4fc59ce1ed9972) I could use specifically for this initiative.

To make it easier to port logic from the original game EXE to a ScummVM engine we'll need to identify functions, data structures, subsystems, state management, resource handling and many other components that made up the game - so we kick things off with:
```
Read the AGENTS.md file, start at the application entry point in Ghidra and begin 
scanning the available functions (FUN_*). Based on the xrefs to those functions, 
as well as how defined strings are being used and where DOS interrupts are being 
invoked, when you have high confidence in a function's purpose, rename it with a 
meaningful name.
```

The `AGENTS.md` file outlines operating parameters such as keeping track of our findings in an `ARCHITECTURE.md` file and ongoing progress in a `TRACKER.md` file. As we progress with subsequent prompts, more of the linear executable in Ghidra will be decompiled, making it easier to work with as a source of truth for our re-implementation efforts.

![](/images/ghidra1/ghidra-naming.png)

Using Ghidra via the Ghidra MCP bridge makes it very easy to incrementally analyze the game executable and start piecing together how it works.

## Scaffolding a Game Engine

Once we've made sufficient progress unwinding some of the original main game loop and resource handling, we can start wiring up an engine using additional prompts. The `ARCHITECTURE.md` we're evolving along with direct access to Ghidra via MCP can be used to first:

* create a skeletal engine (based on ScummVM's [HOWTO-Engines](https://wiki.scummvm.org/index.php/HOWTO-Engines) guidance)
* add basic resource handling
* add basic audio/video decoding
* play our first video resources

[The Cutting Room Floor](https://tcrf.net/Harvester) has an entry on Harvester, as well as some [additional notes](https://tcrf.net/Notes:Harvester) that can be shared with Codex to inform file format disassembly and re-implementation.

I was actually pleasantly surprised with how easy it was to make progress using this configuration, as targeted prompts more often than not produced positive, actionable results. Within a day of starting this project I was able to get the intro videos playing, the first scene to render and the background music and sound effects working.

![](/images/ghidra1/scummvm-early.png)

Plenty more to do (such as fixing the palette), the main thing to highlight here is that understanding assembly language doesn't need to be a barrier to undertaking these types of reverse engineering initiatives anymore.

<!-- 
https://github.com/david-offord/harvester-bm-converter/tree/master
https://www.polygon.com/fmv-harvester-brilliantly-and-brutally-critiques-censorship/ -->