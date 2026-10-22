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

I developed ScummVM's [`harvester`](https://github.com/alexbevi/scummvm/tree/harvester/engines/harvester) engine against the retail DOS release. Adding support for the earlier playable demo meant finding which behaviors it shared with retail and which differed.

I loaded retail `HARVEST.LE` and demo `HARVEST.EXE` into separate Ghidra projects, exposed both through Ghidra MCP, and used Codex to compare them while playing through the demo in ScummVM.

## Comparing the executables

After normalizing opcode streams, I compared function hashes:

| Comparison | Demo | Retail |
| --- | ---: | ---: |
| Recovered functions | 745 | 928 |
| Demo functions with an exact normalized retail match | 672 | 672 |
| Demo functions without an exact match | 73 | n/a |
| Non-matches attributable to dialogue identifiers | 43 | n/a |

The 43 dialogue-handler mismatches came from embedded dialogue identifiers. The surrounding instructions were equivalent between builds.

The demo uses the XFile archive format described in [part 3]({% post_url 2026-03-23-reverse-engineering-harvester-with-ghidra-and-codex-part-3-file-formats %}). Its two archive sets contain 354 entries. ScummVM's `ResourceManager` already tolerated the absent third set.

These results supported keeping one engine, with `isDemo()` checks only where the binaries or data showed different behavior.

The detector identifies the demo by its executable size and MD5:

```text
HARVEST.EXE
size: 1,167,247 bytes
first 5,000 bytes MD5: 787e43b868ebfaca614010af3ab66b6d
full-file MD5: 4990e3cfffe190285500b9d297948a3e
```

The detector sets [game entry flags](https://wiki.scummvm.org/index.php/Advanced_Detector#Game_Entry_flags_ADGameFlags) `ADGF_DEMO | ADGF_UNSTABLE`, which back the `isDemo()` query. Separate detector entries also let retail expose a CD-change prompt option that the single-disc demo hides.

![](/images/ghidra7/screenshot1.png)

## The menu is compiled into the demo

Retail loads menu labels from `MENU.INI`. The demo has no such file. Its labels are built into `HARVEST.EXE`:

```text
NEW GAME
SAVE GAME
LOAD GAME
OPTIONS
HELP
QUIT GAME
```

The missing file produced an empty or unusable menu. If `MENU.INI` is absent and `isDemo()` is true, the engine now supplies those six labels. Retail still uses its data file.

The demo executable also supplies prompts such as `Click`, `START A NEW GAME?`, and `QUIT HARVESTER?`.

## Handling the demo's dialogue layout

Both versions include `DIALOG.RSP`, but their layouts differ.

The engine's recovery logic for Hank's retail dialogue searched the game path for another `DIALOG.RSP` if the expected structure was missing. When a demo directory sat below a retail installation, that search could replace valid demo data with the parent directory's retail file.

Comparing the builds confirmed the demo's layout. Its only active scripted conversation is `LODGE_CHEF`, and the engine already has the shared `CLOAK_ATND` handler. I disabled the retail recovery search for demo data.

## Comparing script commands

The demo's world script is `HARVDEMO.SCR`. Like the retail `HARVEST.SCR` covered in [part 4]({% post_url 2026-03-23-reverse-engineering-harvester-with-ghidra-and-codex-part-4-command-opcodes %}), it is XOR-obfuscated text made up of records and named command chains.

Decoding it gave these counts:

```text
HARVDEMO.SCR
359 live COMMAND records
27 distinct opcodes
26 already implemented
1 demo-specific opcode: END_DEMO
```

All active command branches, flags, and resource paths resolved. In the native parser, `END_DEMO` maps to opcode `0x34`. It follows `SHOW_TEXT ART_STEF_SCREAM` in the final interaction. The interpreter must preserve the text continuation, then request termination and stop walking the command chain.

I carried that request through `InteractionResult`, which already handles room changes, cutscenes, modal text, and other deferred actions. The script layer interprets the opcode. The flow layer handles presentation and shutdown.

## Restoring the native introduction

Before `START`, the original demo displays `DEMOTEXT` over `MAINMENU.BM` using `MAINMENU.PAL`, with `LODGERB.CMP` playing. It waits up to 17 seconds, allowing keyboard or mouse input to skip, then plays `GRAPHIC/FST/PCFALL.FST` before entering the first room.

An `isDemo()` check selects this startup sequence. Skip input must match the original and must not carry into later game input.

![](/images/ghidra7/scummvm-harvester-demo-00001.png)

## Restoring the native ending

`END_DEMO` stops the room presentation, hides the cursor, and starts `SOUND/MUSIC/ROCKFITE.CMP`. It then displays five bitmap and palette pairs:

```text
SCREEN1
SCREEN2
SCREEN3
SCREEN4
SCREEN6
```

The native sequence skips `SCREEN5`. Each screen stays visible for up to 10 seconds. Space, Escape, Enter, or a primary mouse click advances to the next image. The screens fade between one another, and the music fades during the final screen. The engine then releases resources and exits.

This sequence reuses the engine's bitmap, palette, audio, event, and fade code.

![](/images/ghidra7/scummvm-harvester-demo-00000.png)

## Fixing shared runtime behavior

Matching functions and resolving script paths could not verify when the room loop applied deferred actions. Playing through the demo exposed missing shared behavior.

The opening route uses timer-based player locking in `BOWLSNTRY1`. Later sequences exposed other gaps:

- `PAUSE_PC` and `RESUME_PC` had to control player input for the full scripted interval.
- Room-entry actions had to run after returning from a closeup.
- `PC_CHANGE_WEAPON` had to update the scripted weapon state.
- `MOVE_BM2PCZ` had to align a scripted entity with the player's depth.
- `PC_GOTO_Z` had to move the player along Z while preserving the current X position.

These fixes belong to the shared script runtime, so they also apply to retail scripts.

Using the `resources`, `scene`, `dialogue`, and `combat` debug channels, I traced decoded commands through runtime state and compared the results with the original demo. This extended the timer investigation from [part 6]({% post_url 2026-04-14-reverse-engineering-harvester-with-ghidra-and-codex-part-6-timers %}).

## Remaining checks

Save and load still need round-trip checks during demo progression. Lodge Chef dialogue, region and lighting continuations, monster activation, and the final `TO_ART_GAL2` route need to remain reproducible.

Before adding another `isDemo()` branch, I need to compare the binaries in Ghidra and reproduce the difference in the game.
