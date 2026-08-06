---
layout: post
title: "Reconstructing Ripper's IAVF Media Pipeline"
date: 2026-07-15 17:44:27 -0400
comments: true
categories: Programming
tags: [programming, reverse-engineering, scummvm, ghidra, video]
image: /images/ripper/ripper-banner.png
---

While building a ScummVM engine for Ripper, one of the first milestones was playing the introductory movies. The game ships files named `PROINT.AVI` and `PROLOG1.AVI`, so the obvious starting assumption was that they were ordinary AVI containers.

They are not.

A [RIFF AVI](https://learn.microsoft.com/en-us/windows/win32/directshow/avi-riff-file-reference) file begins with a `RIFF` header; these files begin with `IAVF2.00`.

The extension describes the role of the file, not its format. What looks like a video file is actually a packet stream containing audio data, video setup records, compressed video frames, presentation coordinates, timing gates, and display commands.

Getting these files to play correctly required more than identifying a codec. I had to recover the container's packet language, determine which clock controlled presentation timing, reconstruct standard Smacker streams from fragmented payloads, and reproduce display operations that occurred between segments.

The result is an engine-local demultiplexer that translates the [IAVF format](https://wiki.multimedia.cx/index.php/IAVF) into services ScummVM already provides. The engine's [media format detector](https://github.com/alexbevi/scummvm/blob/ripper/engines/ripper/media/plan.cpp) now makes the initial routing decision from the stream signature, distinguishing `IAVF2.00` from `SMK2` and `SMK4` without trusting the filename extension.

![An IAVF presentation playing through the RIPPER engine in ScummVM](/images/ripper/SCR-20260715-saou.png)

## Prior work provided the map

I did not arrive at the IAVF model entirely from scratch. Three earlier investigations supplied important starting points.

[Kostya's "Ripper: Smackered AVIs"](https://codecs.multimedia.cx/2022/09/ripper-smackered-avis/) first highlighted that RIPPER's `.AVI` files are not Microsoft AVI containers. The post identified the stream as a sequence of commands with 14-byte headers and observed that one command carries a complete Smacker header. That suggested the central model used here: IAVF does not merely contain a movie; it contains instructions for constructing and playing one.

[IAVFExtract](https://github.com/itsmattkc/IAVFExtract) turned that observation into a practical extractor capable of producing Smacker video and PCM audio from IAVF assets. It provided a useful executable reference for the container layout, demonstrated that a single IAVF file can contain multiple media segments, and confirmed that the embedded streams can be reconstructed into conventional `.SMK` and `.WAV` files.

The [MultimediaWiki IAVF page](https://wiki.multimedia.cx/index.php/IAVF) provided a third map. It documented the 145-byte file header, the 14-byte command descriptors, and a broader opcode inventory that included both FLIC and Smacker paths. Several fields and commands were deliberately left tentative. That made the page useful not only as a reference, but also as a list of questions to take back to the executable.

Just as importantly, IAVFExtract documented an unresolved problem: extracted video could drift out of sync with its audio even when the expected frames appeared to be present. That observation helped focus the reverse-engineering work on timing rather than decoding. The Ghidra analysis described below builds on that question, recovering the packet scheduler, the distinct timing semantics of audio commands `0x66` and `0x67`, and the use of audio playback as the master clock.

These projects provided the conceptual model and a practical proof of extraction. The ScummVM implementation then independently checked the runtime behavior against `RIPPER.EXE` and the original assets, filling in the scheduling, silence-padding, display-reset, palette, and scene-restoration behavior needed for in-engine playback.

## Finding the player in Ghidra

The main packet processing function in `RIPPER.EXE` is now identified in Ghidra as:

```text
RunPacketizedMediaPlaybackCore @ 0x5b592
```

Its callers eventually lead back to the game's higher-level presentation wrapper:

```text
RunMediaPresentation @ 0x168af
```

The core function opens a packet stream, validates an `IAVF` header with version `2.00`, configures audio and display state, then enters an opcode dispatch loop.

The decompiled function is large because it supports more than one presentation path. Its branches include audio submission, audio control, display resets, FLIC setup and decoding, custom packet setup, palette processing, queued payloads, and stream prebuffering.

That was an important constraint on the re-implementation. The goal was not to declare that every IAVF command had been understood. It was to isolate the commands exercised by the files needed for the current game path and give those commands the narrowest meanings supported by the executable and the assets.

![The packetized media playback function open in Ghidra](/images/ripper/SCR-20260715-sshk.png)

## IAVF is a packet program

After the initial header, the observed stream is made up of 14-byte descriptors:

```cpp
struct IavfDescriptor {
	uint16 opcode;
	uint32 arg0;
	uint32 arg1;
	uint32 arg2;
};
```

Some descriptors are followed by a variable-sized payload. The three arguments change meaning according to the opcode.

For the Smacker-backed files currently handled by the engine, the useful subset looks like this:

| Opcode | Observed role |
| --- | --- |
| `0x66` | Append an audio chunk to the presentation timeline |
| `0x67` | Wait on a tagged position in the managed-audio timeline |
| `0x68` | Clear the active display page at a presentation boundary |
| `0x6a` | Begin a video segment and establish its position and setup data |
| `0x6c` | Load the next compressed custom-packet frame state |
| `0x70` | Stop packet dispatch; managed audio may continue |
| `0x75` | Prebuffer the packet stream and arm managed-audio control |
| `0x77` | Render the custom packet loaded by `0x6c` |
| `0x78` | Queue a reusable Smacker setup payload by key |

This is not intended to be a complete public specification for IAVF. It is the behavior confirmed for the assets exercised by the current ScummVM implementation.

The parser first reads a `0x91`-byte header. An exhaustive scan of the 475 IAVF files in the retail data set clarified several fields:

```text
0x10  number of opcode 0x67 playback gates
0x1c  sample rate
0x1e  channel count
0x1f  bits per sample
0x20  audio bytes per second
0x24  audio block alignment
0x2f  presentation height
0x31  presentation width
```

The value at `0x10` is especially easy to misread as a video frame count. It exactly matches the number of `0x67` commands in every file in the corpus, including gates used around setup and shutdown rather than frame rendering. For example, `LOGO.AVI` declares 378 gates but contains 369 rendered frames.

The corpus also confirmed that the dimension order is height followed by width. `PROINT.AVI` stores `200` at `0x2f` and `320` at `0x31`. One field remains a useful warning against overfitting: the 32-bit value at `0x14` is zero in 474 files but contains `22050` in `PROINT.AVI`. Its purpose is still unresolved.

The 16-bit value at `0x2d` also looks like a nominal frame rate because the observed values are 10, 20, and 30. The original player does not use it to schedule video, however. Ghidra shows it being passed into `InitializePacketizedManagedAudioSession` as audio-session context, while the no-audio pacing path reads its rate from each `0x67` command. The field may still describe a nominal media rate, but it is not the clock that controls normal playback.

The startup movies use mono, 16-bit PCM. Their video data is more interesting because a complete Smacker file does not appear contiguously anywhere in the container.

The executable contains additional branches for FLIC setup at `0x69`, custom packet loading at `0x6b`, and FLIC frame decoding at `0x76`. None of the 475 files in this data set uses those commands. They are confirmed capabilities of the original player, but not yet justified implementation targets for the ScummVM engine.

There is also data after the logical end of many files. All 475 files in the corpus contain `0x70`, which stops the original dispatch loop. In 425 files it is followed by a `0x79` record and a variable-sized payload; the other 50 end immediately. Ghidra confirms that `0x79` is never dispatched because packet processing has already stopped. In every observed trailer, `arg1` is the remaining payload size and `arg2` is `arg1 - arg0`, but the payload's purpose remains unknown.

## Rebuilding Smacker instead of replacing it

Smacker is already supported by ScummVM through `Video::SmackerDecoder`. Writing another Smacker decoder inside the RIPPER engine would duplicate mature shared code and create another implementation to maintain.

The better boundary was to reconstruct the stream expected by the existing decoder.

An IAVF segment contains enough information to do that:

```cpp
struct IavfSegment {
	Common::Array<byte> setup;
	Common::Array<uint32> frameSizes;
	Common::Array<Common::Array<byte> > framePayloads;
	Common::Array<uint32> frameAudioOffsets;
	uint32 expectedFrames;
	int x;
	int y;
	bool clearDisplayBefore;
};
```

The setup data begins with `SMK2` and contains the normal 104-byte Smacker header, frame-type information, and Huffman tree data. IAVF stores the frame sizes and compressed frame bodies separately.

The engine rebuilds a conventional stream in this order:

```text
Smacker header
frame-size table
frame-type and tree data
compressed frame 0
compressed frame 1
...
compressed frame N
```

That reconstructed stream is placed in a `Common::MemoryReadStream` and handed through the RIPPER media player to `Video::SmackerDecoder`.

Conceptually, the adapter is small:

```cpp
Common::SeekableReadStream *smacker = rebuildSmackerStream(segment);

Video::SmackerDecoder decoder;
decoder.loadStream(smacker);
decoder.start();

while (!decoder.endOfVideo()) {
	const Graphics::Surface *frame = decoder.decodeNextFrame();
	// Present the decoded frame using RIPPER's position and timing rules.
}
```

Most of the difficult work stays outside the codec. The RIPPER engine is responsible for determining when a frame is due, where it belongs on the display, which palette rules apply, and what must happen between segments.

### Loading a frame is not presenting it

The wider opcode survey exposed a subtle mistake in the first parser. It treated `0x6c` as the complete frame command and ignored `0x77`. The resulting movies still played because every observed `0x6c` is immediately followed by one `0x77`, but that collapsed two operations that the original player keeps separate.

Ghidra shows the actual dispatch boundary:

```text
0x6c -> LoadCustomPacketPaletteStateBlock @ 0x6c430
0x77 -> RenderCustomPacketFrameAndOverlays @ 0x6c486
```

The engine now retains the compressed payload as pending state when it encounters `0x6c`. It commits that payload as a reconstructed Smacker frame only when the matching `0x77` arrives. Across the retail corpus there are 155,486 load/render pairs with no mismatches.

This distinction does not change the pixels produced by the current assets, but it restores an important property of the packet language: decoding state may be prepared before the command that makes it visible.

The current implementation separates [IAVF parsing and Smacker reconstruction](https://github.com/alexbevi/scummvm/blob/ripper/engines/ripper/iavf.cpp) from [presentation, input, display, and timing](https://github.com/alexbevi/scummvm/blob/ripper/engines/ripper/media/video.cpp).

![IAVF media pipeline splitting packetized audio and video into a PCM timeline and reconstructed Smacker streams for ScummVM](/images/ripper/iavf-pipeline-diagram.png)

## The video frame rate was the wrong clock

IAVFExtract had already demonstrated that the embedded Smacker and PCM streams could be extracted, but it also reported persistent A/V drift. That was an important clue: the remaining problem was probably not missing media data, but timing information encoded in the IAVF command stream.

Reconstructing the Smacker streams made the pictures appear, but it did not make the presentation correct.

The first implementation allowed each reconstructed segment to advance according to its embedded Smacker timing. That is the natural behavior for an ordinary `.SMK` file. In IAVF, however, the audio stream controls the presentation.

The important evidence came from commands `0x66` and `0x67`.

### Audio command `0x66`

For the observed files, the arguments describe:

```text
arg0 = descriptor tag
arg1 = number of bytes represented on the presentation timeline
arg2 = number of bytes physically stored after the descriptor
```

Those last two values are not always equal.

When `arg1` is larger than `arg2`, the original player still advances the audio timeline by `arg1` bytes. The missing portion represents silence. Reading only the stored payload would produce a shorter audio stream and cause every later frame boundary to arrive early.

The reimplementation therefore appends the stored bytes and fills the remainder with zeroes:

```cpp
append(payload, arg2);
appendSilence(arg1 - arg2);
```

The complete PCM buffer now has the same duration as the original presentation timeline.

### Audio gate `0x67`

Command `0x67` refers back to a tagged audio descriptor and supplies its cumulative effective byte offset. It is a playback gate, not inherently a video-frame command. Some gates surround segment setup or the end of a presentation, which is why the header's gate count can be larger than the number of rendered frames.

Ghidra shows the original player servicing this through:

```text
ServiceManagedAudioTriggerEntry840ControlLoop @ 0x48ad3
```

The loop waits for the managed-audio state to advance far enough before allowing the corresponding presentation work to continue.

When a gate precedes a custom frame packet, it establishes the scheduling relationship: the frame is due when audio playback reaches the recorded byte offset.

The third argument also describes fallback pacing when managed audio is unavailable. The original code interprets the low byte as the integer rate and the high byte as hundredths. A value of `0x3207`, for example, represents 7.50 updates per second. Normal playback still follows the tagged audio descriptors rather than this fallback clock.

The ScummVM implementation converts the byte offset into milliseconds:

```text
audioByteRate =
    sampleRate * channels * bitsPerSample / 8

targetMilliseconds =
    frameAudioOffset * 1000 / audioByteRate
```

During playback it compares that target against the mixer's elapsed time:

```cpp
audioElapsedMs = mixer->getSoundElapsedTime(audioHandle);
frameDue = audioElapsedMs >= targetAudioMs;
```

If audio could not be started, the engine falls back to a system timer using the same target offsets. Under normal conditions, the mixer is authoritative.

This fixed a class of errors that could not be solved by adjusting the Smacker frame rate. The video segments did not own independent clocks. They were visual events attached to positions in one continuous audio timeline.

### The final packet is not the end of playback

A later scene exposed one more timing boundary. Opcode `0x70` exits the packet dispatch loop, but the original player continues polling `GetManagedAudioTriggerActiveDescriptor` until the final managed-audio descriptor completes. `KA_BOOK.AVI`, for example, has several seconds of audio after its last custom-video frame.

The ScummVM implementation therefore retains the terminal decoded frame while the remaining PCM plays. Escape and Space remain active during that wait. Only after the audio tail completes, or the player skips it, does the presentation release its media state. In other words, `0x70` marks the end of the packet program, not necessarily the end of the visible and audible presentation.

High-verbosity logging made the result measurable:

```text
Ripper: Smacker 'PROINT.AVI#7'
        frame=...
        audioTargetMs=...
        audioElapsedMs=...
        driftMs=...
```

Per-frame diagnostics are intentionally kept out of normal debug levels, but they were useful while establishing the clock relationship.

## One file can contain several movies

`PROINT.AVI` is not one Smacker stream. It contains 16 segments. `PROLOG1.AVI` contains two.

Segments can have different dimensions and positions. The scale decision is made separately for each embedded Smacker branch, matching the behavior selected by:

```text
InitializeMediaPresentationDisplayModeCallback @ 0x163a8
```

`PreparePacketizedMediaPlaybackBranchSetup` invokes that callback for every branch. A branch smaller than 321×201 receives a 2:1 display descriptor, and its effective scaled extents are centered. This allows a 320×200 segment to occupy the full 640×400 presentation surface while preserving its original aspect ratio.

This distinction matters for `PROLOG2.AVI`: its IAVF canvas declares 640×400, but its embedded Smacker branches are 320×200 and must still be doubled. Full-sized branches switch to the full display context rather than inheriting the scene viewport's 50-pixel vertical origin.

The segment boundaries also explain another visible defect from the early implementation. A smaller segment could be drawn over a larger preceding segment while leaving old pixels around its edges.

The video decoder was working correctly. The display state was not.

## Display commands are part of the format

IAVF command `0x68` reaches two display services in the original executable:

```text
DispatchDisplayServiceCommand(0x1d)
DispatchDisplayServiceCommand(0x14)
```

The second command resolves to:

```text
ClearGenericVideoLogicalPage @ 0x45ed8
```

In `PROINT.AVI`, command `0x68` appears before transitions between several differently sized segments. The active logical page must be cleared before the next segment's palette and pixels are presented.

Without that operation, pixels from the previous segment remain visible. Because the new segment may also install a different palette, those leftover pixel indices can change colour even though their values in the framebuffer never changed.

The reimplementation records the display boundary on the following segment:

```cpp
segment.clearDisplayBefore = pendingDisplayClear;
```

Before presenting that segment, it clears the ScummVM surface and submits the update. If `0x68` is followed by `0x70` instead of another segment, the engine records a final display clear and applies it after the presentation and any managed-audio tail complete.

Palette handling required similar care. RIPPER has another Smacker path that preserves palette ranges used by the toolbar and other interface elements. IAVF does not use that same path. The original packet renderer installs the packet's active palette directly, so applying the interface patch universally would modify the introductory movies incorrectly.

This produced a useful rule:

```text
Direct scene Smacker:
    apply the shared interface palette bands

Reconstructed IAVF segment:
    preserve the complete decoded packet palette
```

The distinction is based on two separate original call paths, not on a general preference about how palettes should behave.

## Returning control to the scene

Playing the movie was not the final boundary.

Some IAVF presentations are launched from scene scripts. On the keyboard-controlled path, the original `RunMediaPresentation` wrapper preserves the logical display state while the packetized presentation temporarily owns the screen. When playback ends, it restores the previous page, submits a full display update, restores the palette, and reactivates selection presentation.

ScummVM has one active framebuffer rather than the original display-page arrangement. The engine therefore snapshots both indexed pixels and all 256 palette entries before keyboard-controlled IAVF playback.

After the movie finishes, it restores them together:

```text
capture indexed framebuffer
capture 256-colour palette
play IAVF presentation
restore indexed framebuffer
restore palette
update screen
```

Restoring only the pixels is insufficient because the same byte values can represent entirely different colours under the movie's final palette.

This became especially important once dialogue response videos and other scripted presentations began returning directly to interactive scenes. The transition had to restore the scene the player left, not retain the last frame or palette from the movie.

That restoration is a property of the presentation route, not a universal IAVF rule. An uncontrolled presentation intentionally leaves its final page visible. The Virtual Herald path depends on this behavior: after `VH_1.AVI` completes, the game enters its interface frame using the movie's retained display rather than restoring the black pre-roll page.

## Controls and explicit extensions

The original controlled-presentation callback recognizes Escape and Space. Escape stops the whole presentation, Space pauses or resumes both video and managed audio, and mouse buttons do not skip the packetized path.

To make initial debugging and play-testing easier, I added Right Arrow handling as an explicit convenience for segmented IAVF files. It leaves the current Smacker branch, seeks the shared PCM stream to the next branch's first absolute audio offset, and rebases that branch's frame gates to the restarted mixer clock. Right Arrow on the final or only branch reports successful completion so the surrounding script still performs its normal played-state update. 

Escape also needs a deliberate translation at the engine boundary. ScummVM rebuilds and presents the terminal Smacker frame before returning through the normal completion path, ensuring later script commands still run and delta-coded surface or palette state is complete. Retail stops the presentation instead of visibly decoding forward, so this is completion behavior rather than a claim of literal input fidelity.

## Keeping the implementation narrow

There were several opportunities to solve a local problem in the wrong layer:

- teach the shared Smacker decoder about IAVF;
- add RIPPER palette rules to generic video code;
- change shared display behavior to accommodate one game's page model;
- implement a new codec rather than reconstruct a standard stream;
- assume every branch in the original packet engine had the same semantics as the observed assets.

The current design avoids those shortcuts.

```text
Media format detector
    identifies IAVF2.00, SMK2, and SMK4 by signature
    preserves the stream position before dispatch

IAVF adapter
    parses IAVF descriptors
    constructs the PCM timeline
    records segment and frame-gate boundaries
    rebuilds Smacker streams

RIPPER MediaPlayer
    maps audio offsets to frame deadlines
    applies placement, input, palette, and display rules
    restores or retains the final display for the active route

ScummVM services
    decode Smacker frames
    play PCM audio
    manage surfaces and palettes
    provide events and timing
```

This boundary keeps the proprietary behavior auditable against `RIPPER.EXE` while leaving shared ScummVM components game-agnostic.

Each route now expresses its decoder policy through a `SmackerPlaybackPlan`, grouping placement, input, timeline, palette, frame range, looping, callbacks, and rendering. The player emits one stable trace of that plan before playback, and controlled IAVF routes use the engine's shared `IndexedDisplaySnapshot` service for pixels and palette state. These are structural changes rather than new IAVF semantics, but they make later refactoring easier to compare with the original call paths.

It also leaves room for future work. Ghidra shows FLIC and other custom packet branches in `RunPacketizedMediaPlaybackCore`, but the complete scan of this retail data set found no IAVF file that exercises them. The current engine does not claim to implement every branch merely because it exists in the executable. Those paths should be added when an asset or reachable scene supplies enough data to verify them.

## What this work established

Reconstructing IAVF produced several broader lessons for the RIPPER engine:

1. File extensions are weak evidence. Inspect the bytes and follow the native dispatch path.
2. A proprietary container may wrap a standard codec rather than replace it.
3. Stored payload length and presentation duration are separate concepts.
4. A header's count may describe scheduler gates rather than decoded frames.
5. Loading decoder state and presenting it may be separate commands.
6. The correct clock may live outside the video stream.
7. Display clears and palette changes are part of media semantics.
8. Framebuffer state and palette state must be restored together.
9. The end of packet dispatch may precede the end of the presentation timeline.
10. Shared codecs should remain shared; game-specific scheduling belongs in the engine.

The same pipeline now supports startup movies and later scene, dialogue, WAC, inventory, and puzzle presentations. It preserves the original packet ordering, reconstructed Smacker segments, continuous PCM timeline, audio-master frame scheduling, segment display boundaries, and route-specific palette and display behavior.

Prior work established the essential breakthrough: RIPPER's misleadingly named `.AVI` files are command streams around standard Smacker and PCM data. Reconstructing the original player in Ghidra supplied the remaining piece: how those commands schedule, synchronize, reset, and restore playback inside the game.

What initially looked like an unsupported AVI codec turned out to be a custom multimedia scheduler built around familiar components. Once that distinction was clear, the reimplementation became less about decoding video and more about recovering the rules that connected audio, frames, palettes, and display state.
