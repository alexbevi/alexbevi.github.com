---
layout: post
title: "Reverse Engineering Harvester with Ghidra and Codex - Part 4: Command Opcodes"
date: 2026-03-23 19:35:39 -0400
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

Harvester's startup / world script is not bytecode. It is XOR-obfuscated text, and opcode dispatch happens through `COMMAND` records in `HARVEST.SCR`:

```text
COMMAND triggerTag opcodeName arg1 arg2 arg3 [arg4]
```

In the original game and in ScummVM, these opcode names come from the data pipeline, not from a compiled bytecode table:

- In ScummVM, [`Script::load()`](https://github.com/alexbevi/scummvm/blob/0add95aa7714a90f1db930ad47609188775c7db9/engines/harvester/script.cpp#L408-L463) reads `HARVEST.SCR`, [`decode()`](https://github.com/alexbevi/scummvm/blob/0add95aa7714a90f1db930ad47609188775c7db9/engines/harvester/script.cpp#L589-L596) XOR-deobfuscates it, and [`parseTownRecords()`](https://github.com/alexbevi/scummvm/blob/0add95aa7714a90f1db930ad47609188775c7db9/engines/harvester/script.cpp#L598-L755) turns it into typed startup records.
- Within [`parseTownRecords()`](https://github.com/alexbevi/scummvm/blob/0add95aa7714a90f1db930ad47609188775c7db9/engines/harvester/script.cpp#L598-L755), [`COMMAND` lines are parsed into `StartupCommandRecord` entries](https://github.com/alexbevi/scummvm/blob/0add95aa7714a90f1db930ad47609188775c7db9/engines/harvester/script.cpp#L654-L676) alongside `ROOM`, `OBJECT`, `REGION`, `TIMER`, `USEITEM`, and related world records.
- Those other records provide the entry labels for command chains through room setup/exit, interactions, and timers.
- [`findCommandRecord()`](https://github.com/alexbevi/scummvm/blob/0add95aa7714a90f1db930ad47609188775c7db9/engines/harvester/script.cpp#L1635-L1644) and [`executeCommandChain()`](https://github.com/alexbevi/scummvm/blob/0add95aa7714a90f1db930ad47609188775c7db9/engines/harvester/script.cpp#L2091-L2528) resolve the current label to a `COMMAND` record, decode the opcode name on that line, and dispatch into engine handlers for room flow, media, inventory, actor state, and other subsystems.


## Command Labels

### `triggerTag`

`triggerTag` is the label attached to one `COMMAND` record. It is the string used to find that record later.

- The parser stores it from the token immediately after `COMMAND` in [`parseTownRecords()`](https://github.com/alexbevi/scummvm/blob/0add95aa7714a90f1db930ad47609188775c7db9/engines/harvester/script.cpp#L654-L676).
- [`Script::findCommandRecord()`](https://github.com/alexbevi/scummvm/blob/0add95aa7714a90f1db930ad47609188775c7db9/engines/harvester/script.cpp#L1635-L1644) resolves a command by comparing the requested tag string against `command.triggerTag`.

So `triggerTag` is not a condition and not an opcode argument in the behavioral sense. It is the command node's name.

### `currentTag`

`currentTag` is the interpreter's working variable while it walks a command chain.

- [`executeCommandChain()`](https://github.com/alexbevi/scummvm/blob/0add95aa7714a90f1db930ad47609188775c7db9/engines/harvester/script.cpp#L2091-L2528) initializes `currentTag` from the caller-supplied starting tag.
- It then resolves the current command with [`findCommandRecord(currentTag)`](https://github.com/alexbevi/scummvm/blob/0add95aa7714a90f1db930ad47609188775c7db9/engines/harvester/script.cpp#L1635-L1644).
- After each opcode runs, `currentTag` is updated to the next label:
  - branch opcodes like `CHECK_FLAG` and `CHECK_PERC` set it from `arg2` or `arg3`
  - most linear opcodes continue to `arg4`
  - deferred opcodes may stash `arg4` as a continuation tag and return to the caller instead of immediately continuing

If you think of the script as a graph, `triggerTag` is the node name stored in the file, and `currentTag` is the interpreter's current node pointer.

## Where Starting Tags Come From

The interpreter does not enter command chains automatically just because a `COMMAND` record exists. Some other game record must point at its label.

Common entry points in the current engine:

- object interaction uses [`object.actionTag`](https://github.com/alexbevi/scummvm/blob/0add95aa7714a90f1db930ad47609188775c7db9/engines/harvester/script.cpp#L1386-L1413)
- region interaction uses [`region.actionTag`](https://github.com/alexbevi/scummvm/blob/0add95aa7714a90f1db930ad47609188775c7db9/engines/harvester/script.cpp#L1416-L1432)
- use-item interaction uses [`useItem.actionTag`](https://github.com/alexbevi/scummvm/blob/0add95aa7714a90f1db930ad47609188775c7db9/engines/harvester/script.cpp#L1435-L1450)
- room enter / exit uses [`room->onEnterCommand`](https://github.com/alexbevi/scummvm/blob/0add95aa7714a90f1db930ad47609188775c7db9/engines/harvester/script.cpp#L1048-L1061) and [`room->onExitCommand`](https://github.com/alexbevi/scummvm/blob/0add95aa7714a90f1db930ad47609188775c7db9/engines/harvester/script.cpp#L1369-L1383)
- timer execution starts from [`timer->arg2`](https://github.com/alexbevi/scummvm/blob/0add95aa7714a90f1db930ad47609188775c7db9/engines/harvester/script.cpp#L1474-L1502)

That means a more precise reading of the format is:

```text
COMMAND label opcodeName arg1 arg2 arg3 [nextLabel]
```

with the caveat that `arg2`, `arg3`, and `arg4` are opcode-specific, so only some of them are actually labels for a given opcode.

## Examples

### Example 1: straight-line chain

```text
COMMAND "OPEN_GATE" "SET_FLAG" "GATE_OPEN" "T" "" "OPEN_GATE_TEXT"
COMMAND "OPEN_GATE_TEXT" "SHOW_TEXT" "Gate_Is_Open" "" "" ""
```

If an object's `actionTag` is `"OPEN_GATE"`:

1. `executeCommandChain()` starts with `currentTag = "OPEN_GATE"`.
2. `findCommandRecord("OPEN_GATE")` resolves the first line because its `triggerTag` is `"OPEN_GATE"`.
3. `SET_FLAG` runs and then sets `currentTag = arg4`, which is `"OPEN_GATE_TEXT"`.
4. `findCommandRecord("OPEN_GATE_TEXT")` resolves the second line.
5. `SHOW_TEXT` runs. Because it is deferred, the interpreter returns control to the caller instead of continuing immediately.

### Example 2: branch on a flag

```text
COMMAND "TRY_SHED" "CHECK_FLAG" "HAS_SHED_KEY" "SHED_OPEN" "SHED_LOCKED"
COMMAND "SHED_OPEN" "CHANGE_ROOM" "SHED_INT" "" "" ""
COMMAND "SHED_LOCKED" "SHOW_TEXT" "Need_A_Key" "" "" ""
```

If the chain starts at `"TRY_SHED"`:

1. `currentTag` starts as `"TRY_SHED"`.
2. `CHECK_FLAG` looks up `HAS_SHED_KEY`.
3. If the flag is true, `currentTag` becomes `arg2`, so the next lookup is `"SHED_OPEN"`.
4. If the flag is false, `currentTag` becomes `arg3`, so the next lookup is `"SHED_LOCKED"`.

So here the first `COMMAND` line is acting like a named branch node.

### Example 3: deferred opcode with continuation

```text
COMMAND "POTTS_EVENT" "GOFLIC" "GRAPHIC/FST/C001B.FST" "" "" "POTTS_AFTER_MOVIE"
COMMAND "POTTS_AFTER_MOVIE" "SET_FLAG" "STEPH_MIDGAME_PLAYED" "T" "" ""
```

When `currentTag` reaches `"POTTS_EVENT"`:

1. `GOFLIC` does not immediately jump to `"POTTS_AFTER_MOVIE"`.
2. Instead, it stores `arg4` as a continuation tag and returns the movie request to the caller.
3. After the cutscene finishes, room/dialogue code can resume by starting another command-chain execution at `"POTTS_AFTER_MOVIE"`.

That is why `arg4` is often best read as "the next tag after this opcode completes", not just "the next line".

Most of the opcode recognition below lives in [`Script::executeCommandChain()`](https://github.com/alexbevi/scummvm/blob/0add95aa7714a90f1db930ad47609188775c7db9/engines/harvester/script.cpp#L2091-L2528), while deferred outputs such as modal text, dialogue continuations, lighting changes, player moves, and follow-up tags are consumed by the room interaction processor in [`room.cpp`](https://github.com/alexbevi/scummvm/blob/0add95aa7714a90f1db930ad47609188775c7db9/engines/harvester/room.cpp#L922-L1236).

## Control Flow And Transitions

| Opcode | Args used | Effect | Status / notes |
| --- | --- | --- | --- |
| `CHANGE_CD` | `arg1=cdNumber` | Change CD | Not Implemented |
| `CHECK_FLAG` | `arg1=flagName`, `arg2=trueTag`, `arg3=falseTag` | Branches on the current runtime value of a flag. Missing flags read as false. | Implemented |
| `CHECK_PERC` | `arg1=threshold`, `arg2=trueTag`, `arg3=falseTag` | Rolls `0..99` and branches on `roll < threshold`. Threshold is clamped to `0..100`. | Implemented |
| `EXEC_LIST` | `arg1=listName`, `arg4=nextTag` | Runs each entry tag in an `EXEC_LIST` record until one produces deferred output, then stops. Otherwise continues to `arg4`. | Implemented |
| `START_DIALOG` | `arg1=npcName`, `arg4=continuationTag` | Defers into the room/dialogue system and resumes at `arg4` after the dialogue finishes. | Implemented with caveat: if no dialogue context is supplied, the interpreter logs an unsupported-command message and aborts the current chain. |
| `GOFLIC` | `arg1=cutscenePath`, `arg4=continuationTag` | Defers a cutscene and stores `arg4` as the continuation tag to run after the movie. | Implemented with caveat: if no cutscene output slot is provided, the interpreter logs and continues to `arg4` without playing a movie. |
| `GODEATHFLIC` | `arg1=cutscenePath` | Defers a death movie and requests a return to the main menu. | Implemented with caveat: requires menu-exit context. Without it, the interpreter logs an unsupported-command message and aborts the current chain. If transitions are disabled, it logs a skipped transition and returns. |
| `CLOSEUP` | `arg1=targetName` | Requests a nested room / closeup transition. | Implemented with caveat: if transitions are disabled, the opcode is skipped and the chain ends immediately. |
| `CHANGE_ROOM` | `arg1=targetName` | Requests a room handoff. In room gameplay, this queues the next room instead of nesting immediately. | Implemented with caveat: if transitions are disabled, the opcode is skipped and the chain ends immediately. |

## World And Runtime State

| Opcode | Args used | Effect | Status / notes |
| --- | --- | --- | --- |
| `SET_FLAG` | `arg1=flagName`, `arg2=value`, `arg4=nextTag` | Creates or updates a runtime flag, then continues to `arg4`. | Implemented |
| `SPOOL_MUSIC` | `arg1=musicPath`, `arg4=nextTag` | Defers a startup music change. | Implemented |
| `ADD` | `arg1=ownerOrRoom`, `arg2=objectName`, `arg4=nextTag` | Makes an object visible by setting `visible` and `runtimeVisible` true. | Implemented. This is a visibility toggle, not an ownership transfer. |
| `DELETE` | `arg1=ownerOrRoom`, `arg2=objectName`, `arg4=nextTag` | Makes an object invisible by setting `visible` and `runtimeVisible` false. | Implemented |
| `ADD2INV` | `arg1=objectName`, `arg4=nextTag` | Moves an object into `INVENTORY`, makes it visible, and marks it identified. | Implemented |
| `SET_ANIM` | `arg1=animName`, `arg2=active`, `arg3=visible`, `arg4=nextTag` | Updates a runtime animation's active / visible state. | Implemented |
| `SET_REGION` | `arg1=regionName`, `arg2=enabledFlag`, `arg4=nextTag` | Toggles `startEnabled` on a region. Any `arg2` other than `F` enables the region. | Implemented with caveat: this does not touch `cursorEnabled`. |
| `SET_NPC` | `arg1=npcName`, `arg2=active`, `arg3=visible`, `arg4=nextTag` | Updates a runtime NPC's active / visible state. | Implemented |
| `SET_MONSTER` | `arg1=monsterName`, `arg2=active`, `arg3=visible`, `arg4=nextTag` | Updates a runtime monster's active / visible state. | Implemented with nuance: activating a monster forces visibility on and restores HP if the monster was dead. |
| `SET_TIMER` | `arg1=timerName`, `arg2=ON/OFF`, `arg4=nextTag` | Enables or disables a timer. When enabling, resets `currentValue` to `initialValue`. | Implemented |
| `KILL_TIMER` | `arg1=timerName`, `arg4=nextTag` | Disables a timer. | Implemented |
| `KILL_NPC` | `arg1=npcName`, `arg2=damageType`, `arg4=nextTag` | Marks an NPC as dead / removed and optionally records damage type `BLUDGE`, `SLASH`, or `PROJ`. | Implemented |
| `MONSTERFY` | `arg1=npcName`, `arg2=damageType`, `arg4=nextTag` | Uses the same death/monsterfy flagging path as `KILL_NPC`, and also activates the NPC's linked monster target when one exists. | Implemented |

## Player And UI

| Opcode | Args used | Effect | Status / notes |
| --- | --- | --- | --- |
| `SHOW_TEXT` | `arg1=textKey`, `arg4=continuationTag` | Resolves a `TEXT` record and defers modal text display. | Implemented with caveat: rendering currently requires `BOX1..BOX4`. Unknown text boxes log and do not display. |
| `HEAL_PC` | `arg1=delta`, `arg4=nextTag` | Adds `arg1` to current player HP, clamped to `0..30`. | Implemented. Current code treats this as the same operation as `ADJ_HP`. |
| `ADJ_HP` | `arg1=delta`, `arg4=nextTag` | Adds `arg1` to current player HP, clamped to `0..30`. | Implemented |
| `KILL_PC` | `arg4=nextTag` | Sets player HP to `0`. | Implemented |
| `PAUSE_PC` | `arg4=nextTag` | Sets the runtime player-control-paused flag. | Implemented |
| `RESUME_PC` | `arg4=nextTag` | Clears the runtime player-control-paused flag. | Implemented |
| `PC_GOTO_XZ` | `arg1=x`, `arg2=z`, `arg4=continuationTag` | Defers a player reposition request in room space. | Implemented with caveat: if no player-move consumer is present, the interpreter logs and continues to `arg4` without moving the player. |
| `CHANGE_LIGHTING` | `arg1=mode`, `arg4=continuationTag` | Defers a lighting command. Supported parsed modes are `DIM`, `NORMAL`, `NONE`, and `FADE_IN`. | Implemented with caveats: `NONE` maps to a black-screen command, not a no-op. `FADE_IN` is recognized but has no direct room-side effect yet. If no lighting consumer is present, the interpreter logs and continues. |

## Audio

The audio opcodes all share the same queueing path through [`appendStartupAudioCommand()`](https://github.com/alexbevi/scummvm/blob/0add95aa7714a90f1db930ad47609188775c7db9/engines/harvester/script.cpp#L309-L352) and are later handed off to [`Flow::executeStartupAudioCommands()`](https://github.com/alexbevi/scummvm/blob/0add95aa7714a90f1db930ad47609188775c7db9/engines/harvester/flow.cpp#L1896-L1899).

| Opcode | Args used | Effect | Status / notes |
| --- | --- | --- | --- |
| `START_WAV` | `arg1=path`, `arg4=nextTag` | Plays a sound effect on one of eight rotating SFX handles. | Implemented |
| `START_SINGLE_WAV` | `arg1=path`, `arg4=nextTag` | Plays a sound effect on one dedicated "single" SFX handle, replacing the prior one. | Implemented |
| `LOAD_WAV` | `arg1=path`, `arg2=slot`, `arg4=nextTag` | Loads a sound into a persistent slot for later playback. | Implemented. Valid loaded-sound slots are `0..3`. |
| `PLAY_WAV` | `arg1=slot`, `arg4=nextTag` | Plays a sound previously loaded by `LOAD_WAV`. | Implemented |
| `DELETE_WAV` | `arg1=slot`, `arg4=nextTag` | Deletes a sound previously loaded by `LOAD_WAV`. | Implemented |

## Observed Engine-Side Aliases And Shared Paths

- `HEAL_PC` and `ADJ_HP` currently share the exact same implementation.
- `KILL_NPC` and `MONSTERFY` share the same base handler; `MONSTERFY` additionally activates the linked monster target when present.
- `CLOSEUP` and `CHANGE_ROOM` share the same transition-output path, differing only in the transition kind reported to room logic.
