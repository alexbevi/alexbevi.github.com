---
layout: post
title: "ScummVM Asylum Engine"
date: 2021-05-19 06:32:45 -0400
comments: true
categories:
tags:
---

I started on a reverse engineering journey to port reimplement Dreamforge's [Sanitarium](https://en.wikipedia.org/wiki/Sanitarium_(video_game)) to [ScummVM](https://www.scummvm.org/) in July of 2009. Though I loved playing this game when it first came out, what really rekindled my interest was the [Gamasutra Postmortem article](https://www.gamasutra.com/view/feature/3299/postmortem_dreamforges_sanitarium.php).

The postmortem included some interesting technical details about the development of the title that helped inform some of the early static analysis work done using [IDA Pro](https://www.hex-rays.com/ida-pro/) to disassemble the game's executable (`sntrm.exe`).

![](/images/asylum-idapro.png)

With some early progress




Reached out to [Mike Breitkreutz](https://www.mobygames.com/developer/sheet/view/developerId,3583/) in 2009 via MySpace trying to get some additional information about the project to help with our reverse engineering efforts.

![](/images/asylum-chat.png)
![](/images/asylum-mikeemail.png)


With [PR#2982 - ENGINES: Sanitarium engine](https://github.com/scummvm/scummvm/pull/2982),

[]({% post_url 2015-04-08-asylum-engine-update %})