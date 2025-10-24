---
layout: post
title: "Martian Memorandum (Access Software) - 1991"
date: 2025-10-21 17:57:52 -0400
comments: true
tags: [adventure, "Access Software", "played:DOS", Access]
image: /images/adventure/marmem/scummvm-martian-00000.png
series: lets_adventure
---
{% series_nav %}

[Martian Memorandum](https://en.wikipedia.org/wiki/Martian_Memorandum) is a dystopian cyberpunk/noir graphic adventure game that was originally released in 1991 for MS-DOS. It was developed and published by Access Software. The game is the second in the series of Tex Murphy mysteries; its immediate sequel is Under a Killing Moon. The game is set in 2039, several years after Mean Streets.

![](/images/adventure/marmem/scummvm-martian-00031.png)

Six years have passed and we find the private investigator Tex Murphy broke, down on his luck, and seriously in need of a new case. He gets a call from Marshall Alexander, a business tycoon who owns most of the industry on Mars. It seems his daughter Alexis has run away from home, and taken "something else" with her. Marshall won't say what that something else is, but he is willing to pay handsomely to get it (and his daughter) back.

Unlike its predecessor, the game contains only adventure gameplay, removing flight simulation and action sequences. Basic gameplay mechanics are very similar to those of the first game, placing interrogation and choices above object-based puzzles. Verb commands are used to interact with the environment, while interrogating suspects usually involves selecting conversation options. Making a wrong choice may sometimes prematurely end the game or render it unwinnable.[^1]

![](/images/adventure/marmem/scummvm-martian-00028.png)
_Once again there are mutants to interact with_

With [ScummVM recently announcing support for Martian Memorandum](https://www.scummvm.org/news/20251005), it seemed like the perfect time to pick this game up for the series. Though I enjoyed much of my experience playing [Mean Streets]({% post_url 2023-01-19-mean-streets %}), there were several mechanics I could really do without so I was pleasantly surprised to see that this game was very much an improvement in almost every way.

I played through this game fully using `ScummVM 3.0.0git9072-g83957afe279 (Oct 20 2025 05:56:12)` and really only found ([and reported](https://bugs.scummvm.org/ticket/16308
)) one issue that caused a crash. There are a couple of audio tracks that don't play, but if you check the console output while the game is running there are TODOs still that indicate these are known (and will likely be addressed at some point):
```
User picked target 'martian' (engine ID 'access', game ID 'martian')...
Running Martian Memorandum (DOS/English)
r01.ap: c081daca9b0cfd710157cf946e343df6, 39352 bytes.
TODO: Push midi song?
cmdSpecial6: TODO: Store current music?
cmdSpecial6: TODO: Restore original music?
TODO: Push midi song?
```

Regardless of the above, I'd recommend ScummVM as the preferred way to experience this game.

![](/images/adventure/marmem/scummvm-martian-00019.png)
_You'll want to `MOVE` that board in the lower right hand side as well_

Martian Memorandum is a classic point and click adventure, so the interface should be very familiar. There is a menu bar at the bottom of the screen with the available actions you can take such as `LOOK`, `OPEN`, and `TALK`.

There are far fewer hotspots on each screen than Mean Streets had, and you no longer have to worry about navigating layers of nested menus to see if there's something inside something else. You will however find yourself trying to `MOVE` everything on every screen, as this is how switches are toggled, and there tend to be important items hidden behind or under things.

You'll begin in Tex's office, where you can `GET` a handful of useful items such as your gun, comlink, lockpick and more.

![](/images/adventure/marmem/scummvm-martian-00003.png)
_This - and "I'll send you the address" is basically all Stacey says_

You'll want to refer back to your comlink fairly frequently, as Stacey will give you information about the characters you've learned about, as well as new locations you can then `TRAVEL` to.

Stacey's audio (like all character audio) is heavily compressed so it doesn't sound great, but the samples are typically short so it doesn't really affect the experience all that much.

![](/images/adventure/marmem/scummvm-martian-00004.png)

When you travel to a new location you'll typically get a wall of text advancing the plot slightly. The writing is quite good though, and keeps you engaged with the story, which unfolds as follows:

> Tex Murphy is hired by business mogul Marshall Alexander, founder of TerraForm Corporation, to locate his missing daughter, Alexis. As in the first game, Tex travels between destinations and interrogates characters associated with the subject such as Alexander's attorney, his wife, and Alexis's roommate and business partners. Interrogations are menu-based and dialogues open up additional destinations and dialogue options. The investigation will reveal to Tex that the girl's disappearance is linked with an item in Alexander's possession.
>
> Alexis will be traced on planet Mars, whose exploitation is mostly owned by Alexander's company. Tex will find out that Alexander was actually Collier Stanton, a scientist and explorer of Mars, infamous for killing mutant colonists to obtain the "Oracle Stone". With this stone, Alexander foresaw the future and read antagonists' minds and built his corporate empire. Alexis's good will was used to lure her into stealing the Stone and bring it to Mars, only to fall into the hands of Thomas Dangerfield, the original discoverer of the Stone.[^2]

Gone is the coordinate system and an abysmally slow lander navigation from the previous game, which is a very welcome change this time around as you'll be moving between locations frequently.

![](/images/adventure/marmem/scummvm-martian-00016.png)

Traveling is just a matter of picking the location you want to visit from the menu. Most locations can't be explored, and just contain a single character you can interact with. This makes the game feel a lot more expansive than it really is, but given the amount of backtracking you need to do to re-ask characters about new names/locations you learn about, it's actually better this way.

![](/images/adventure/marmem/scummvm-martian-00023.png)

There are many characters to meet throughout the game, and like Mean Streets you have multiple methods to engage with them. This is much more streamlined here though as there are only 1-3 responses to choose from as you navigate a dialogue tree with a character. You'll need to "gain their trust" so that you can `ASK ABOUT` other topics and characters.

Talking to characters is one of the primary mechanisms for advancing the plot of the game, and you'll learn about new locations to visit, new characters to meet and details about your investigation this way - so ask everyone about everything.

![](/images/adventure/marmem/scummvm-martian-00009.png)
_He's not ready for me to `ASK ABOUT` anything ... yet_

If you haven't successfully answered with the right responses, you can leave/return/try again until you have, which is less frustrating as it may sound as the dialogue trees tend to not be very deep.

The "bribe" system is gone in this game, but some characters do need to be shown an item prior to allowing you to ask them about the various topics you may want to discuss. You can do this using the `OFFER` option and picking something from your inventory.

![](/images/adventure/marmem/scummvm-martian-00025.png)
_You know you're curious what that "Big Dick Card" is ..._

The inventory (accessible via `USE` from the menu) is a lot more streamlined this time around. Since you don't have to worry about money and selling random things you don't need to advance the plot, there's a lot less you need to pick up. It's important to `LOOK` at everything on screen before you `GET` it though, as once you've picked something up you can't look at it.

![](/images/adventure/marmem/scummvm-martian-00024.png)

There's no combat sequences in this game like the arcade-style side scrolling shooter in Mean Streets, but there is this hoverboard sequence near the end of the game that is plenty frustrating. You'll need to avoid these laser beams, but the hit boxes aren't alway clear, so you'll likely die often. Thankfully you can save/load anywhere during this sequence, so savescumming is a viable (and potentially necessary) strategy since you need to traverse the laser field twice.

ScummVM came to my rescue here though, as every time I would die I'd just quit the game and restart from the terminal via `scummvm --save-slot=16 martian` (since the relevant save was in slot 16). This was a life saver as every death takes forever to fade in/out, then you return to your office at the beginning of the game before you can reload a previous save.

Although the hoverboard sequence isn't nearly as bad as the [Turbo Tunnel from Battletoads](https://www.reddit.com/r/gaming/
comments/1azvg20/another_frustrating_level_from_childhood/) ... I could have done without it.

![](/images/adventure/marmem/SCR-20251020-gybk.png)

The `HINT` system in this game also makes it incredibly easy. On every screen the game will hold your hand through literally every step you need to complete to progress if you want it to. Since this is optional it's not really detracting from the experience at all.

![](/images/adventure/marmem/scummvm-martian-00013.png)

You may find those hints useful on occasion though, as there are MANY ways to die in this game. It would have been nice if there was a bit more variety to the death screens (there's maybe a handful), but the glib commentary the game gives you when you mess up and die is reminiscent of a Sierra game.

![](/images/adventure/marmem/scummvm-martian-00027.png)

Does this game have a maze ... yes. Do I hate mazes any less at this point ... no. This endgame maze thankfully gives you a minimap to show you where you need to go (sort of), and the directional arrows on screen point in what direction you're moving, so once you get your bearings it's not too bad to navigate, but it's still frustrating.

This maze is also part of the same timed sequence that includes the hoverboard and lasers, so you've got 10 minutes to get through that sequence - twice - then through the maze and out of the casino. Save early, save often 😉.

![](/images/adventure/marmem/scummvm-martian-00033.png)

You'll eventually find Alexis on Mars, rescue her, get captured by Thomas Dangerfield, recover the Oracle Stone and escape. This will bring Martian Memorandum to a close, which point Alexis and Tex end up back at the Temple and comment about how they have no idea what that was all about - and they might as well go get a hot dog and a beer from Weenie World (though that audio wasn't played via ScummVM at the time, but I'm sure those TODOs will be fixed up at some point).

Honestly, I enjoyed this game quite a bit more and I still love the dystopian future this world presents, as well as the fact that many characters are mutants. I do think this entry in the Tex Murphy series is quite a bit easier than Mean Streets, but it's definitely not on rails.

I would have liked the character interactions to be a bit deeper than they were, but given how compelling the story was and that you were learning more about the mystery, the world and the cast with each interaction the overall experience was definitely enjoyable.

If you enjoyed this review and want to learn more about the game, I'd also HIGHLY recommend you go check out The Space Quest Historian's [Magical pet rocks from an alien civilization? \| Tex Murphy: Martian Memorandum](https://www.youtube.com/watch?v=Iw08YzZ4HGk) video.

![](/images/adventure/marmem/scummvm-martian-00010.png)

PS, make sure you get Rhonda flowers for your "date" and answer her questions correctly ... she'll make it worth your while ...

## Game Information

|*Game*|Martian Memorandum|
|*Developer*|[Access Software](https://en.wikipedia.org/wiki/Access_Software)|
|*Publisher*|Access Software|
|*Release Date*|1991|
|*Systems*|DOS|
|*Game Engine*|[Access](https://wiki.scummvm.org/index.php?title=Access)|

### My Playthrough

|[How Long To Beat?](https://howlongtobeat.com/game/9729)|5.5 hours|
|*Version Played*|DOS via [ScummVM](https://www.scummvm.org/)|
|*Notes*|[Walkthrough](https://www.walkthroughking.com/text/martianmemorandum.aspx), [Manual](https://www.mocagh.org/miscgame/martianmemo-manual.pdf)|

### Score

See [here](https://www.alexbevi.com/blog/2021/07/28/adventure-games-1980-1999/#scoring) for a refresher on how we're scoring these games.

|**Graphics (15)**|11|
|**Sound (10)**|6|
|**Plot / Progression (25)**|17|
|**Characters / Development (15)**|12|
|**Gameplay / Experience (15)**|9|
|**Replayability (5)**|3|
|**Impact / Impression (10)**|6|
|**Bonus / Surprise (5)**|2|
||**66%**|

### Gallery

{% galleria %}
/images/adventure/marmem/scummvm-martian-00001.png
/images/adventure/marmem/scummvm-martian-00002.png
/images/adventure/marmem/scummvm-martian-00005.png
/images/adventure/marmem/scummvm-martian-00006.png
/images/adventure/marmem/scummvm-martian-00007.png
/images/adventure/marmem/scummvm-martian-00008.png
/images/adventure/marmem/scummvm-martian-00009.png
/images/adventure/marmem/scummvm-martian-00011.png
/images/adventure/marmem/scummvm-martian-00012.png
/images/adventure/marmem/scummvm-martian-00014.png
/images/adventure/marmem/scummvm-martian-00015.png
/images/adventure/marmem/scummvm-martian-00017.png
/images/adventure/marmem/scummvm-martian-00020.png
/images/adventure/marmem/scummvm-martian-00021.png
/images/adventure/marmem/scummvm-martian-00022.png
/images/adventure/marmem/scummvm-martian-00026.png
/images/adventure/marmem/scummvm-martian-00029.png
/images/adventure/marmem/scummvm-martian-00030.png
/images/adventure/marmem/scummvm-martian-00032.png
/images/adventure/marmem/scummvm-martian-00034.png
/images/adventure/marmem/scummvm-martian-00035.png
{% endgalleria %}

**Footnotes**

[^1]: <small>Description from [Moby Games](https://www.mobygames.com/game/222/martian-memorandum/)</small>
[^2]: <small>Plot synopsis from [Fandom](https://texmurphy.fandom.com/wiki/Martian_Memorandum)</small>
