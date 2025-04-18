---
layout: post
title: "Space Quest 6: The Spinal Frontier (Sierra On-Line) - 1995"
date: 2024-10-08 08:18:09 -0400
comments: true
categories: ["Let's Adventure!"]
tags: [adventure, "Sierra On-Line", SCI]
image: /images/adventure/sq6/scummvm-sq6-00000.png
series: lets_adventure
---
{% series_nav %}

[Space Quest 6: Roger Wilco in the Spinal Frontier](https://en.wikipedia.org/wiki/Space_Quest_6) is a point-and-click adventure game developed and published by Sierra On-Line in 1995. It is the sixth and final game in the Space Quest series, though (spoiler) the game ends on a cliffhanger that will ultimately never be resolved.

![](/images/adventure/sq6/scummvm-sq6-00005.png)

Roger Wilco, the brave interstellar janitor who has already saved the universe from many great dangers, is now in a very embarrassing position. His commanders show no respect for his courageous actions in the previous game. Instead, he is being accused of all kinds of violations against the galactic law, is deprived of all the honors he got in the previous game, and as a token of mercy, is allowed to return to his old job - cleaning closets... But those unfortunate events are just the beginning of much bigger troubles Roger will get into. Once again, the future of galaxy depends on him![^1]

![](/images/adventure/sq6/scummvm-sq6-00022.png)

This final entry in the series runs on the later SCI32 engine Rev 2.100.002 (aka [SCI2.1 (middle)](http://sciwiki.sierrahelp.com/index.php/Sierra_SCI_Release_List#SCI2.1_.28middle.29)), which allowed it to use SVGA graphics with 256 colors at 640×480 resolution. Unlike other SCI games, it did not have the interface in a pull down bar at the top of the screen, but instead used a "verb bar" window along the bottom of the screen, similar to LucasArts' SCUMM engine. The graphics style was also more cartoonish than in previous games, as well as incorporating an ample amount of 3-D rendered images.

![](/images/adventure/sq6/scummvm-sq6-00021.png)
_I don't love the visual style of the human characters..._

I appreciated the updated visual style of the backgrounds and the UI, but honestly the closeup shots of any humanoid character just looked ... off. Though there was clearly a lot of work put into the character design, I miss the pixel art of [Space Quest V]({% post_url 2024-08-21-space-quest-v %}).

An increased colour palette and next-gen SCI game engine sort of left everything looking "flat" in my opinion.

![](/images/adventure/sq6/scummvm-sq6-00020.png)

The cutscenes have not aged well, and are reminiscent of basically all 3-D rendered scenes of the early to mid 90s. I can't really fault Sierra for this as this is just an artifact of the games of that era.

Most cutscenes felt more like filler than substance, and were just there to eat up some time. They could occasionally become repetitive and tedious if they were triggered every time you needed to backtrack (like with the "riding the tapeworm" sequence near the end).

![](/images/adventure/sq6/scummvm00054.2.bmp)
_Roger is really trying to push both buttons at once - and is - but it doesn't look like it in ScummVM_

While playing through the game I thought I hit some weird visual bug, but apparently it's well known and only present in ScummVM ([#9749 - SCI: SQ6: Shuttle Bay Entrance bug](https://bugs.scummvm.org/ticket/9749)). ScummVM's developers have included many, many improvements to SCI engine games (including [script patches for SQ6](https://github.com/scummvm/scummvm/blob/master/engines/sci/engine/script_patches.cpp#L25289-L25318)), however apparently the issue here is a little different.

Sierra actually [patented](https://patents.google.com/patent/US5287446A) their [pathfinding algorithm](http://sciwiki.sierrahelp.com/index.php/ToDo/Pathfinding/Patent), so the ScummVM engineers had to do their own version of it instead. This can result in some visual anomalies like in the screenshot above.

![](/images/adventure/sq6/scummvm-sq6-00008.png)

As with most Sierra adventure games, you run around picking stuff up in hopes of using it later to solve some puzzle. The inventory puzzles in this game weren't all that challenging, and it was actually pretty clever how the fish kept ending up in your possession as you progressed.

I assumed this was being set up as ["red herring"](https://en.wikipedia.org/wiki/Red_herring) gag, but this fish would actually end up being the solution to the final puzzle in the game (spoiler), so several times when you were about to leave an area permanently, a character threw it to you so you'd have it again.

![](/images/adventure/sq6/scummvm-sq6-00012.png)

Overall, the voice acting is not great. I couldn't bring myself to disable speech altogether though because [Gary Owens](https://en.wikipedia.org/wiki/Gary_Owens) as the narrator just crushes it. If it weren't for his dry, sarcastic delivery throughout the game I'd likely knock several more points off the _Sound_ score.

![](/images/adventure/sq6/scummvm-sq6-00024.png)
_By far, this is my favourite scene in the game_

Whereas the previous game was a parody of Star Trek, Space Quest 6 is a mishmash of various science fiction properties that were popular at the time the game came out. Almost every name and location is a parody or pun - which if you're in on the joke adds to the experience. I'm not sure how accessible the writing of the game is to a modern audience as a result.

The overarching plot involves Roger initially being targeted for "Project Immortality", but instead his colleague Stellar Santiago is taken (after she saves Roger's life). He then needs to rescue her by first finding her, then being shrunk down to enter her digestive system and destroy some nanobots.

![](/images/adventure/sq6/scummvm-sq6-00029.png)

I really didn't find the story to be all that interesting and it was mostly forgettable. The puzzles aren't overly difficult, and typically just involve fetch quests and backtracking. The game's locations aren't that expansive, so searching everywhere doesn't take all that long, and though there's a bit of [pixel-hunting](https://en.wiktionary.org/wiki/pixel_hunting) on certain screens, key items are typically out in the open.

![](/images/adventure/sq6/scummvm-sq6-00017.png)

Unfortunately, I didn't find nearly as many interesting ways to die as I would have in previous games, and the message you're prompted with is fairly generic. This was part of the fun of the Space Quest series, and I found after about an hour of playing the game I didn't bother messing around to see how I might die as it just wasn't proving to be all that entertaining.

For new gamers it's appreciated that you get a "Try Again" option, which just rewinds back to right before you made a mistake and doesn't force you to rely on an earlier save. It's fairly obvious most of the time though what the "right" choice is, so you likely won't die too often.

![](/images/adventure/sq6/scummvm-sq6-00033.png)

Space Quest 6 ends on a cliffhanger, but since there was never a sequel made this is effectively where the series concludes. The game doesn't have the same feel as the previous 5 entries in the series, and this is likely due to it not actually being made by the "Two Guys from Andromeda", but instead [Josh Mandel](https://en.wikipedia.org/wiki/Josh_Mandel_(video_game_designer)).

Mandel designed the game, but left near the end of production and Scott Murphy (on of the "Two Guys") came in to finish it off. This is likely why some of the gameplay feels uneven, which is confirmed in a 2006 interview with Josh Mandel:

> _"One of the inventory items cut was a comic book CD in Nigel's room that was fully readable and had all the hints to the Datacorder puzzle. From a writing and design standpoint, it was fully finished, and I know that Barry Smith had started the artwork. I don't understand why it was cut. But the comic book content was something I'd worked on for months, and it was something that I was uncharacteristically proud of ... I think it would've been one of the greatest parody sequences in the SQ series. So not only was I very upset not to see it in the game, but the fact that they had to put the Datacorder hints in the manual, leading player to think it was meant to be copy protection, disturbed me greatly."_

![](/images/adventure/sq6/scummvm-sq6-00011.png)
_I guess this wasn't meant to be copy protection_

The Datacorder puzzle did feel like copy protection, so I feel Josh's frustration and am genuinely curious as to what the comic book CD experience would have been like. I guess we'll never know, just like we'll never know what Stellar Santiago meant when she said we were "going to like the next mission" ...

Space Quest 6 isn't great, but it's good enough to play through at least once. If you're only going to play one game in the series though, I'd recommend either [Space Quest III]({% post_url 2024-02-16-space-quest-iii %}) or [Space Quest V]({% post_url 2024-08-21-space-quest-v %}).

## Game Information

|*Game*|Space Quest 6: The Spinal Frontier|
|*Developer*|[Sierra On-Line](https://en.wikipedia.org/wiki/Sierra_Entertainment)|
|*Publisher*|Sierra On-Line|
|*Release Date*|July 11, 1995|
|*Systems*|DOS, Windows, Macintosh|
|*Game Engine*|[SCI](https://wiki.scummvm.org/index.php?title=SCI)|

### My Playthrough

|[How Long To Beat?](https://howlongtobeat.com/game/8862)|5.5 hours|
|*Version Played*|DOS via [ScummVM](https://www.scummvm.org/)|
|*Notes*|[Walkthrough](https://www.wiw.org/~jess/sq6.html), [Manual](https://spacequest.net/sq6/manual/)|

### Score

See [here](https://www.alexbevi.com/blog/2021/07/28/adventure-games-1980-1999/#scoring) for a refresher on how we're scoring these games.

|**Graphics (15)**|9|
|**Sound (10)**|6|
|**Plot / Progression (25)**|15|
|**Characters / Development (15)**|8|
|**Gameplay / Experience (15)**|9|
|**Replayability (5)**|2|
|**Impact / Impression (10)**|5|
|**Bonus / Surprise (5)**|1|
||**55%**|

### Gallery

{% galleria %}
/images/adventure/sq6/scummvm-sq6-00001.png
/images/adventure/sq6/scummvm-sq6-00002.png
/images/adventure/sq6/scummvm-sq6-00003.png
/images/adventure/sq6/scummvm-sq6-00004.png
/images/adventure/sq6/scummvm-sq6-00006.png
/images/adventure/sq6/scummvm-sq6-00007.png
/images/adventure/sq6/scummvm-sq6-00009.png
/images/adventure/sq6/scummvm-sq6-00010.png
/images/adventure/sq6/scummvm-sq6-00013.png
/images/adventure/sq6/scummvm-sq6-00014.png
/images/adventure/sq6/scummvm-sq6-00015.png
/images/adventure/sq6/scummvm-sq6-00016.png
/images/adventure/sq6/scummvm-sq6-00018.png
/images/adventure/sq6/scummvm-sq6-00019.png
/images/adventure/sq6/scummvm-sq6-00023.png
/images/adventure/sq6/scummvm-sq6-00025.png
/images/adventure/sq6/scummvm-sq6-00026.png
/images/adventure/sq6/scummvm-sq6-00027.png
/images/adventure/sq6/scummvm-sq6-00028.png
/images/adventure/sq6/scummvm-sq6-00030.png
/images/adventure/sq6/scummvm-sq6-00031.png
/images/adventure/sq6/scummvm-sq6-00032.png
{% endgalleria %}

**Footnotes**

[^1]: <small>Description from [Moby Games](https://www.mobygames.com/game/145/space-quest-6-roger-wilco-in-the-spinal-frontier/)</small>