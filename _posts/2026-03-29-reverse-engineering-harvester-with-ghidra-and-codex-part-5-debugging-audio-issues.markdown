---
layout: post
title: "Reverse Engineering Harvester with Ghidra and Codex - Part 5: Debugging Audio Issues"
date: 2026-03-29 20:41:11 -0400
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

An issue I've noticed with the [`harvester` engine](https://github.com/alexbevi/scummvm/tree/harvester) implementation is that every time there's an audio sample played, it starts with a distinct "popping" sound. I thought this could be an issue with how I'd approached the re-implementation or disassembly, but after a few passes at decompiling the audio code I'd always end up with the same result.

<video width="640" height="480" controls>
    <source src="/images/ghidra5/harvester-popping.mp4" type="video/mp4">
    Your browser does not support the video tag
</video>

While doing some unrelated research I stumbled on [Kostya's Boring Codec World](https://codecs.multimedia.cx/) and a post he'd made on [FutureVision formats](https://codecs.multimedia.cx/2021/01/a-look-on-futurevision-formats/), discussing Harvester audio/video specifically:

> _"Music format is based on IMA ADPCM with minimalistic file header and the default predictor. Which means it needs some time to adapt to the actual coming signal amplitudes. In result the old format description based on reverse engineering recommends skipping first 7-57 bytes right after the header because of the garbage sound it produces. When I looked into the binary reference (an adventure that will be described in an upcoming post), it turned out that in certain cases they simply zero out the first 50 decoded samples."_

Since our approach to do everything with Ghidra/Codex, I thought this would be a good opportunity to try just prompting GPT-5.4 with a bit more context to see what it would come back with. I tried feeding the following prompt as a result:

```
based on https://codecs.multimedia.cx/2021/01/a-look-on-futurevision-formats/ "Music format is based on IMA ADPCM with minimalistic file header and the default predictor. Which means it needs some time to adapt to the actual coming signal amplitudes. In result the old format description based on reverse engineering recommends skipping first 7-57 bytes right after the header because of the garbage sound it produces. When I looked into the binary reference (an adventure that will be described in an upcoming post), it turned out that in certain cases they simply zero out the first 50 decoded samples."

Can we look into how realistic this may be based on what's in ghidra? The audio still produces a popping sound on each sample being played, so maybe this might help address that
```

After processing for a few minutes, the response back was promising:

```
Yes. Based on live Ghidra, the article is not just plausible, it matches what HARVEST.LE actually does.

start_music_stream at 0x1bfc0 decodes the first FCMP chunk and then zeroes the first 0x64 decoded bytes before queueing it. On the common 16-bit streams, that is 50 samples.

load_sound_sample at 0x18470 and load_dialogue_voice_sample at 0x191d0 are even more aggressive: they queue from decoded_pcm + 0x1f4, so they discard the first 500 decoded bytes of one-shot/dialogue FCMP playback.
The current ScummVM Harvester decoder was doing neither, so a clip-start pop on CMP-backed audio is consistent with that mismatch.

I patched media_manager.cpp (line 127) to mirror the native split: music now mutes the first 100 decoded bytes, while startup speech/other FCMP playback trims the first 500 decoded bytes. WAV handling is unchanged. 
```

The `applyStartupFcmpWarmup` function that this prompt resulted in effectively addressed the issue we were experiencing. 

<video width="640" height="480" controls>
    <source src="/images/ghidra5/harvester-less-popping.mp4" type="video/mp4">
    Your browser does not support the video tag
</video>

There's still a slight pop on the first FST video being loaded, but all scene sound effects and dialogue interactions are now pop-free.

The patch is below to show how this was incorporated into the engine's media manager.

```diff
diff --git a/engines/harvester/media_manager.cpp b/engines/harvester/media_manager.cpp
index 691863468fa6..e953c0226cba 100644
--- a/engines/harvester/media_manager.cpp
+++ b/engines/harvester/media_manager.cpp
@@ -41,6 +41,11 @@ namespace Harvester {
 
 namespace {
 
+enum class FcmpWarmupMode {
+	kMusic,
+	kSample
+};
+
 static const int8 kHarvesterImaIndexAdjustTable[16] = {
 	-1, -1, -1, -1, 2, 4, 6, 8,
 	-1, -1, -1, -1, 2, 4, 6, 8
@@ -119,7 +124,29 @@ static uint32 decodeHarvesterFcmp(byte *dest, const byte *src, uint32 srcSize, u
 	return decodedSize;
 }
 
-static Audio::SeekableAudioStream *decodeStartupAudioStream(Common::SeekableReadStream *stream) {
+static void applyStartupFcmpWarmup(byte *decodedPcm, uint32 &decodedSize, FcmpWarmupMode warmupMode) {
+	if (!decodedPcm || decodedSize == 0)
+		return;
+
+	if (warmupMode == FcmpWarmupMode::kMusic) {
+		// Native start_music_stream zeros the first 0x64 decoded bytes of the first FCMP chunk.
+		memset(decodedPcm, 0, MIN<uint32>(decodedSize, 100));
+		return;
+	}
+
+	// Native load_sound_sample/load_dialogue_voice_sample queue from decoded_pcm + 0x1f4.
+	const uint32 trimBytes = MIN<uint32>(decodedSize, 500);
+	if (trimBytes == decodedSize) {
+		memset(decodedPcm, 0, decodedSize);
+		return;
+	}
+
+	memmove(decodedPcm, decodedPcm + trimBytes, decodedSize - trimBytes);
+	decodedSize -= trimBytes;
+}
+
+static Audio::SeekableAudioStream *decodeStartupAudioStream(Common::SeekableReadStream *stream,
+		FcmpWarmupMode warmupMode) {
 	if (!stream)
 		return nullptr;
 
@@ -156,7 +183,7 @@ static Audio::SeekableAudioStream *decodeStartupAudioStream(Common::SeekableRead
 				return nullptr;
 			}
 
-			const uint32 decodedSize = payloadSize * (bitsPerSample >> 2);
+			uint32 decodedSize = payloadSize * (bitsPerSample >> 2);
 			byte *decodedPcm = (byte *)malloc(decodedSize);
 			if (!decodedPcm) {
 				free(compressedPayload);
@@ -165,6 +192,7 @@ static Audio::SeekableAudioStream *decodeStartupAudioStream(Common::SeekableRead
 			}
 
 			decodeHarvesterFcmp(decodedPcm, compressedPayload, payloadSize, bitsPerSample);
+			applyStartupFcmpWarmup(decodedPcm, decodedSize, warmupMode);
 			free(compressedPayload);
 			delete stream;
 			return Audio::makeRawStream(decodedPcm, decodedSize, sampleRate,
@@ -177,8 +205,9 @@ static Audio::SeekableAudioStream *decodeStartupAudioStream(Common::SeekableRead
 	return Audio::makeWAVStream(stream, DisposeAfterUse::YES);
 }
 
-static Audio::SeekableAudioStream *openStartupAudioStream(ResourceManager &resources, const Common::String &path) {
-	return decodeStartupAudioStream(resources.openFile(path));
+static Audio::SeekableAudioStream *openStartupAudioStream(ResourceManager &resources,
+		const Common::String &path, FcmpWarmupMode warmupMode) {
+	return decodeStartupAudioStream(resources.openFile(path), warmupMode);
 }
 
 } // End of anonymous namespace
@@ -268,7 +297,8 @@ bool MediaManager::playMusic(const Common::String &path) {
 		return true;
 	}
 
-	Audio::SeekableAudioStream *audioStream = openStartupAudioStream(_resources, path);
+	Audio::SeekableAudioStream *audioStream =
+		openStartupAudioStream(_resources, path, FcmpWarmupMode::kMusic);
 	if (!audioStream) {
 		warning("Harvester: unable to decode startup music '%s'", path.c_str());
 		return false;
@@ -323,7 +353,8 @@ bool MediaManager::playSound(const Common::String &path) {
 	_soundSlotIndex = (_soundSlotIndex + 1) % ARRAYSIZE(_soundHandles);
 	stopSoundHandle(_soundHandles[_soundSlotIndex]);
 
-	Audio::SeekableAudioStream *audioStream = openStartupAudioStream(_resources, path);
+	Audio::SeekableAudioStream *audioStream =
+		openStartupAudioStream(_resources, path, FcmpWarmupMode::kSample);
 	if (!audioStream) {
 		warning("Harvester: unable to decode startup sound '%s'", path.c_str());
 		return false;
@@ -340,7 +371,8 @@ bool MediaManager::playSingleSound(const Common::String &path) {
 		return false;
 
 	stopSoundHandle(_singleSoundHandle);
-	Audio::SeekableAudioStream *audioStream = openStartupAudioStream(_resources, path);
+	Audio::SeekableAudioStream *audioStream =
+		openStartupAudioStream(_resources, path, FcmpWarmupMode::kSample);
 	if (!audioStream) {
 		warning("Harvester: unable to decode startup sound '%s'", path.c_str());
 		return false;
@@ -364,7 +396,8 @@ bool MediaManager::playSpeech(const Common::String &path) {
 		return false;
 
 	stopSoundHandle(_speechHandle);
-	Audio::SeekableAudioStream *audioStream = openStartupAudioStream(_resources, path);
+	Audio::SeekableAudioStream *audioStream =
+		openStartupAudioStream(_resources, path, FcmpWarmupMode::kSample);
 	if (!audioStream) {
 		warning("Harvester: unable to decode startup speech '%s'", path.c_str());
 		return false;
@@ -410,7 +443,7 @@ bool MediaManager::playLoadedSound(int slot) {
 
 	Common::SeekableReadStream *stream = new Common::MemoryReadStream(
 		_loadedSoundData[slot].data(), _loadedSoundData[slot].size(), DisposeAfterUse::NO);
-	Audio::SeekableAudioStream *audioStream = decodeStartupAudioStream(stream);
+	Audio::SeekableAudioStream *audioStream = decodeStartupAudioStream(stream, FcmpWarmupMode::kSample);
 	if (!audioStream) {
 		warning("Harvester: unable to decode startup sound slot %d ('%s')",
 			slot, _loadedSoundPaths[slot].c_str());
```            