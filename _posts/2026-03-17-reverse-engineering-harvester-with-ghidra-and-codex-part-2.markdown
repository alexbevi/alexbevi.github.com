---
layout: post
title: "Reverse Engineering Harvester with Ghidra and Codex - Part 2"
date: 2026-03-17 19:22:34 -0400
comments: true
categories: Programming
tags: [programming, reverse-engineering, scummvm, ghidra]
image: /images/ghidra1/harvester_reverse_engineering_banner_1200x600.png 
series: reverse_engineering_harvester
---
{% series_nav %}

According to the [Harvester manual](https://harvester.telepedia.net/wiki/Manual), your health is represented by a picture of Steve in the inventory that gets bloodier the more damage you take. Since we're using a Ghidra disassembly and Codex to build out our ScummVM engine, let's have a look at how easy adding this functionality can be.

![](/images/ghidra2/SCR-20260318-gkwu.png)

First let's confirm that our implementation doesn't support this functionality just yet. This is easy enough to do as we've already started working on the inventory system, so clicking on Steve should bring up the expected view - missing photo and all.

![](/images/ghidra2/SCR-20260317-quvr.png)

Comparing this with the original via DOSBox (left) and our current engine (right), we not only can clearly see what the expected outcome should be. The prompt we're going to use is as follows:

> when you click on the inventory view, Steve has his health tracked in the photo in the bottom left. Check back in Ghidra to trace health management, and if there are any unnamed functions or data structures that apply, rename them once you have high confidence. Implement these changes engine-side and commit changes when ready.

![](/images/ghidra2/SCR-20260317-qwys.png)

Just like magic, after about 13 minutes of processing Codex will revisit our existing disassembly in Ghidra, clarify any gaps there first, carry that logic back to Visual Studio Code and propose engine changes to implement the requested functionality.

![](/images/ghidra2/SCR-20260317-qvjx.png)

The first pass is honestly pretty impressive, as other than a visual anomaly in the form or a black box seemingly being rendered out of place, the health indicator is working already!

Since we're taking side-by-side screenshots of a reference implementation (the original running in DOSBox) to compare our re-implementation with, we can actually attach that screenshot as context to steer our next prompt:

> you can see from the attached screenshot of dosbox (left) and our engine (right) that the health indicator photo is correctly placed, but there's a black box under it that appears to be either an incorrect transparency or a misrotated container element. Revist Ghidra for inventory and health drawing and determine how to fix this

![](/images/ghidra2/SCR-20260317-qxoa.png)

Codex is making a number of tool calls, so I've got [`rtk`](https://www.rtk-ai.app/) installed to compress some of the output to extend my context window slightly. It only takes a couple minutes, but the model is able to determine the cause of the issue based on the state of our reversed engineered executable in Ghidra.

![](/images/ghidra2/SCR-20260317-qxzk.png)

Having invested the time to map out the data structures and function calls in Ghidra really makes it a lot more efficient to work with it to reimplement game logic, and the Ghidra MCP bridge allows us to keep doing this quickly and effectively in Visual Studio Code.

![](/images/ghidra2/SCR-20260317-qyip.png)

What this practically translates to is a fairly good implementation (see full [commit](https://github.com/alexbevi/scummvm/commit/df15ab715792ba0a26f12430ac489619f9be2857)).

Ten years ago while I was still muddling my way through [`asylum` engine updates]({% post_url 2015-04-08-asylum-engine-update %}) in IDA Pro, making this type of progress would have taken me weeks. Now, in about 30 minutes I can achieve exponentially more!