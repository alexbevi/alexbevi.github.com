---
layout: post
title: "Sanitarium: The ScummVM Asylum Engine Journey Concludes"
date: 2021-05-19 06:32:45 -0400
comments: true
categories: ScummVM
tags: [sanitarium, asylum, scummvm]
image:
  src: /images/scummvm-logo.png
  alt: Scummvm Logo
---

With [PR#2982 - ENGINES: Sanitarium engine](https://github.com/scummvm/scummvm/pull/2982) being recently merged into [ScummVM](https://www.scummvm.org/) I wanted to take some time to chronicle the original development efforts which began in 2009.

At the time I was looking to work on a new engine in an attempt to improve my knowledge of C++ as well as to "give something back" to the open source community. Some of the engines I was toying with at the time included one's for [Uplink: Hacker Elite](https://en.wikipedia.org/wiki/Uplink_(video_game)), the [Dynamix Game Development System](https://code.google.com/archive/p/scummvm-dgds/) as well as [Sanitarium](https://en.wikipedia.org/wiki/Sanitarium_(video_game)).

When I first played Dreamforge's Sanitarium (the [Razor 1911](https://en.wikipedia.org/wiki/Razor_1911) rip at the time ...) I was immediately drawn to the darker story and ambiance. After finishing it I ended up buying the full version and replaying it several times. Though the gameplay was linear I found myself continually drawn into the world and the story.

I began working on an [engine for Sanitarium](https://code.google.com/archive/p/asylumengine/), but soon found a [post on the ScummVM forums](https://forums.scummvm.org/viewtopic.php?f=1&t=7337) by someone trying to do the same thing. I reached out to [Alex Fontoura](https://twitter.com/xesfnet) as he had also been reverse engineering the game's executable (`sntrm.exe`) and we decided to merge our efforts.

We began collaborating on an [IDA Pro](https://www.hex-rays.com/ida-pro/) project to see how far we could get. [Filippos Karapetis](https://wiki.scummvm.org/index.php?title=Developers_Bios#Filippos_Karapetis), a veteran ScummVM developer, also joined us early on and helped correct quite a few bad C++ habits both Alex and I had at the time :P

![](/images/asylum-idapro.png)

With Filippos' help and an old [Gamasutra Postmortem article](https://www.gamasutra.com/view/feature/3299/postmortem_dreamforges_sanitarium.php) providing some insight as to the inner workings of the game, we were making rapid progress. To expedite our efforts I started digging for more "insider" information, so using the [Moby Games Credits page for Sanitarium](https://www.mobygames.com/game/windows/sanitarium/credits) I started "cold-calling" (emailing) some team members.

![](/images/asylum-chat.png)

One team member I was able to get a hold of was [Mike Breitkreutz](https://www.mobygames.com/developer/sheet/view/developerId,3583/) (via MySpace), who shared what he remembered.

![](/images/asylum-mikeemail.png)

[Benjamin Haisch](https://wiki.scummvm.org/index.php?title=Developers_Bios#Benjamin_Haisch), another ScummVM team member, had by this point provided a far superior IDA database to work from which we used until [Julian Templier](http://www.templier.info/) joined us in 2010 and essentially finished the IDA RE efforts.

Julian implemented the event processing subsystem and the save/load functionality along with cleaning up a lot of the codebase. His blog shares some of the progress from [July 2011](https://www.templier.info/2011/07/31/asylum-engine-update-july-2011/) which is shortly before he left to focus on other work (such as the [Ring engine](https://www.templier.info/2011/09/15/ring-engine-status-update/)).

Our progress stagnate from 2012 through 2015, at which point I published [a progress update]({% post_url 2015-04-08-asylum-engine-update %}) in hopes of reigniting interest .... it didn't work.

![](/images/asylum-tweet.png)

Fast forward to 2021 and we find out that [Alexander Panov](https://github.com/alxpnv) has picked up the development and completed the engine! The outstanding work left was the inventory management, encounters and a number of bugfixes, which he was able to get sorted out over the course of a few months.

Alexander is now a member of the ScummVM team, and thanks to his efforts this 12 year journey can finally conclude with a working engine merged into ScummVM that will allow countless others to enjoy Sanitarium.