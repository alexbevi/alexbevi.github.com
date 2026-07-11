---
layout: post
title: "Reverse Engineering Harvester with Ghidra and Codex - Part 7: Demo Support"
date: 2026-07-11 07:17:43 -0400
comments: true
categories: Programming
tags: [programming, reverse-engineering, scummvm, ghidra]
image: /images/ghidra1/harvester_reverse_engineering_banner_1200x600.png 
series: reverse_engineering_harvester
---
{% series_nav %}

<style>
.content pre, .content pre code {
white-space: pre-wrap !important;
word-break: break-word !important;
overflow-wrap: break-word !important;
overflow-x: hidden !important;
}

.highlight {
overflow-x: visible !important;
}
</style>

Until recently, the ScummVM [`harvester`](https://github.com/alexbevi/scummvm/tree/harvester/engines/harvester) engine had been developed against the retail DOS release. That was enough to recover the resource formats, room system, script interpreter, dialogue, combat, timers, and most of the surrounding game flow. It did not tell me whether the earlier playable demo was simply a smaller data set or a meaningfully different build of the engine.

Supporting the demo gave me a useful way to answer that question. I loaded the retail `HARVEST.LE` and demo `HARVEST.EXE` into separate Ghidra projects, exposed both through Ghidra MCP, and used Codex to compare the two programs while working through the demo in ScummVM.

## Establishing the comparison baseline

The first result was that the demo is much closer to retail than its different executable name suggests.

Ghidra recovered 745 functions from the demo and 928 from retail. After normalizing the opcode streams, 672 demo functions had an exact hash match in the retail executable. That left 73 without an immediate match, but 43 of those were dialogue handlers whose embedded dialogue identifiers differed between builds. The instructions around those identifiers were otherwise equivalent.

| Comparison | Demo | Retail |
| --- | ---: | ---: |
| Recovered functions | 745 | 928 |
| Demo functions with an exact normalized retail match | 672 | 672 |
| Demo functions without an exact match | 73 | n/a |
| Non-matches attributable to dialogue identifiers | 43 | n/a |

The resource layer tells the same story. The demo uses the same XFile archive format described in [part 3]({% post_url 2026-03-23-reverse-engineering-harvester-with-ghidra-and-codex-part-3-file-formats %}). Its first two archive sets contain 354 entries, and the missing third set is a normal consequence of shipping a smaller slice of the game. ScummVM's `ResourceManager` already tolerated that absent set.

This gave me a practical implementation rule: keep one Harvester engine and introduce demo-specific behavior only where the binaries or data demonstrate a real boundary. A single `isDemo()` query, backed by the detector flags, became the gate for those cases.

The detector entry itself uses the demo executable's size and MD5:

```text
HARVEST.EXE
size: 1,167,247 bytes
first 5,000 bytes MD5: 787e43b868ebfaca614010af3ab66b6d
full-file MD5: 4990e3cfffe190285500b9d297948a3e
```

Once detected, the variant is marked with [Advanced Detector game entry flags](https://wiki.scummvm.org/index.php/Advanced_Detector#Game_Entry_flags_ADGameFlags) `ADGF_DEMO | ADGF_UNSTABLE`. The retail detector entry remains separate, which lets the engine expose different configuration options without adding checks throughout the runtime. For example, the retail build can ask whether CD-change prompts should be displayed, while that option is hidden for the single-disc demo.

![](/images/ghidra7/screenshot1.png)

## The menu is compiled into the demo

The first visible difference appears before entering a room. Retail Harvester loads its menu labels from `MENU.INI`. The demo does not contain that file because the equivalent strings are built into `HARVEST.EXE`:

```text
NEW GAME
SAVE GAME
LOAD GAME
OPTIONS
HELP
QUIT GAME
```

Treating the missing file as a generic resource failure produced an empty or unusable menu. The fix was small: if `MENU.INI` is absent and `isDemo()` is true, populate those six confirmed labels. Retail continues to use its data file.

The same distinction applies to several prompts. The demo executable supplies labels such as `Click`, `START A NEW GAME?`, and `QUIT HARVESTER?`. These are details, but they are also exactly the sort of details that disappear if demo support is reduced to “make the first room load.”

## Similar files can still have different layouts

Dialogue exposed a less obvious variant boundary. The demo includes `DIALOG.RSP`, just as retail does, but the two files do not have the same layout.

The engine already had recovery logic for an awkward retail response layout associated with Hank's dialogue. If the expected structure was missing, it searched the game path for a better candidate. That was useful while developing against retail files, but it was actively harmful when a demo directory lived below a retail installation: valid demo data could be replaced by a parent-directory retail `DIALOG.RSP`.

Comparing the two builds showed that the demo layout was intentional. Its only active scripted conversation is `LODGE_CHEF`, and the shared `CLOAK_ATND` handler is already represented by the engine. The correction was therefore to keep the retail recovery search away from demo data rather than trying to force both files into the same shape.

## Comparing the script surface

The demo's world script is `HARVDEMO.SCR`. Like the retail `HARVEST.SCR` covered in [part 4]({% post_url 2026-03-23-reverse-engineering-harvester-with-ghidra-and-codex-part-4-command-opcodes %}), it is XOR-obfuscated text made up of records and named command chains.

After decoding it, I found 359 live `COMMAND` records using 27 opcodes. ScummVM already implemented 26 of them. All active command branches, flags, and resource paths resolved. The single missing opcode was `END_DEMO`.

That is a much narrower problem than implementing a second script interpreter. In the native parser, `END_DEMO` maps to opcode `0x34`. It appears at the end of the demo's final interaction, after `SHOW_TEXT ART_STEF_SCREAM`. The interpreter needs to preserve that continuation, turn `END_DEMO` into a terminal request, and stop walking the command chain.

I carried that request through the same `InteractionResult` structure used for room changes, cutscenes, modal text, and other deferred actions. This keeps the script layer responsible for interpreting the opcode while the flow layer owns the presentation and shutdown sequence.

```text
HARVDEMO.SCR
359 live COMMAND records
27 distinct opcodes
26 already implemented
1 demo-specific opcode: END_DEMO
```

## Restoring the native introduction

Getting to the first room is not the start of the native demo. Before `START`, the original executable presents a short sequence built from ordinary demo resources.

It displays the confirmed `DEMOTEXT` paragraph over `MAINMENU.BM` using `MAINMENU.PAL`, with `LODGERB.CMP` playing underneath. The native code waits for 1,700 centiseconds, or 17 seconds, while allowing the player to skip. It then plays `GRAPHIC/FST/PCFALL.FST` before entering the initial room.

This sequence belongs behind `isDemo()` because retail has its own startup flow. The input handling is also important. A player should be able to skip the text using the same keyboard or mouse inputs expected by the original without accidentally bypassing later game input.

![](/images/ghidra7/scummvm-harvester-demo-00001.png)

## Restoring the native ending

`END_DEMO` does more than quit the executable. The room presentation stops, the cursor is hidden, and `SOUND/MUSIC/ROCKFITE.CMP` begins playing. The demo then displays five bitmap and palette pairs in this order:

```text
SCREEN1
SCREEN2
SCREEN3
SCREEN4
SCREEN6
```

The numbering is worth calling out because it is easy to “correct” it into a consecutive sequence that the native executable never uses. Each screen remains visible for up to 1,000 centiseconds, or 10 seconds. Space, Escape, Enter, or a primary mouse click advances to the next image. The screens fade between one another, the music fades during the final screen, resources are released, and the engine terminates cleanly.

This is the largest demo-only flow added for parity, but it still reuses the existing bitmap, palette, audio, event, and fade machinery. The special behavior is mostly the confirmed ordering and timing.

![](/images/ghidra7/scummvm-harvester-demo-00000.png)

## What a complete play-through found

Static comparison established that the demo did not need a separate engine. Runtime progression still mattered because matching functions and resolving script paths cannot prove that every deferred action is applied at the right point in the room loop.

The demo is particularly good at exercising those edges. Its opening route uses timer-based player locking in `BOWLSNTRY1`. Later sequences depend on room-entry actions after leaving closeups, region and lighting continuations, monster activation, scripted weapon changes, entity depth alignment, and player movement along the Z axis.

Working through those scenarios exposed several missing or incomplete shared behaviors:

- `PAUSE_PC` and `RESUME_PC` had to control player input for the full scripted interval.
- Room-entry actions had to run after returning from a closeup.
- `PC_CHANGE_WEAPON` had to update the scripted weapon state.
- `MOVE_BM2PCZ` had to align a scripted entity with the player's depth.
- `PC_GOTO_Z` had to move the player along Z while preserving the current X position.

These are not reasons to fork demo behavior. They are parts of the common script model that the shorter demo happens to reach quickly and predictably. Once corrected, the same semantics are available to retail scripts.

This was also a good continuation of the timer work from [part 6]({% post_url 2026-04-14-reverse-engineering-harvester-with-ghidra-and-codex-part-6-timers %}). With the `resources`, `scene`, `dialogue`, and `combat` debug channels enabled, I could follow each transition from decoded command record to live runtime state and compare the result against the original demo.

## Keeping the variants honest

The main risk in adding demo support was not the amount of missing code. It was letting a handful of confirmed differences turn into broad `isDemo()` branches that would be difficult to verify later.

The current split is intentionally small:

- detection identifies the demo as its own variant;
- built-in menu labels and prompts replace files the demo does not ship;
- dialogue recovery respects the demo's valid response layout;
- the introduction and ending reproduce demo-only presentation flows;
- the CD-change prompt option remains retail-only;
- shared script and room behavior stays shared.

The remaining parity work is scenario-driven. Save and load need round-trip checks during demo progression. Lodge Chef dialogue, lighting continuations, monster activation, and the final `TO_ART_GAL2` route need to remain reproducible. Any additional divergence should start with the same test: compare the demo and retail binaries in Ghidra, reproduce the behavior in a specific runtime scenario, and only then decide whether it belongs behind `isDemo()`.

Supporting the demo turned out to be a compact audit of the engine as a whole. The binary comparison showed that most of the original implementation was shared. The places that differed were concrete and explainable: compiled-in menu text, a distinct dialogue response layout, an introductory sequence, one terminal script opcode, and an ending slideshow. Everything else became a test of whether the common Harvester model had been implemented faithfully enough to run a second build of the game.
