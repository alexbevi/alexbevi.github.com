---
layout: post
title: "Asylum Engine Update"
date: 2015-04-08 09:31:14 -0400
comments: true
categories: [scummvm, sanitarium, asylum]
---

It's been a number of years since I had a chance to look at this project, but recently I updated the codebase to the lastest version (sync with upstream [ScummVM](https://github.com/scummvm/scummvm)) and found that the videos no longer worked.

{% img /images/20150408-004.png %}

It turned out to be a pretty simple fix (see [commit](https://github.com/alexbevi/scummvm/commit/1ed45a5802a7ab9603aa72f8e18196e980657c23)), but it rekindled my interest in the project.

I added some additional debug output and cleaned up the script debug loop so that there wasn't as much spamming of commands that were waiting for another event.

Also, thanks to [@xesf](https://github.com/xesf), we can now actually proceed up and down stairs via fixes he made to the script processor.

{% img /images/20150408-003.png %}

## TODO

**better pathfinding**

{% img /images/20150408-001.png %}

The pathfinding in the original engine is a lot smarter and more forgiving than our implementation.

**inventory management**

{% img /images/20150408-002.png %}

We can currently pick up an item and remove the graphic from the screen, but there's no way to retrieve/use items once collected.

**clean up graphical glitches**

There are still a number of clipping issues, as well as incorrect behaviour when Max is standing still (wrong animation might play).

**fix encounters**

{% img /images/20150408-005.png %}

Encounters load, but you can't interact with keywords yet.

**save/load**

There was quite a bit of work done on this, but we still need to verify that everything is being restored properly on load.