---
layout: page
comments: true
sharing: true
footer: true
---

### About Sanitarium

<a href="https://github.com/alexbevi/scummvm">{% img right /images/github_logo.png %}</a>

Sanitarium is a point-and-click adventure game released in 1998 by ASC Games. A psychological thriller often praised for its atmosphere and originality, Sanitarium tells the story of a man named Max Laughton who is suffering from amnesia due to a car accident as he frantically tries to unveil the details of his institutionalization inside a bizarre medieval-styled asylum. The search for his own identity - and "the truth" - takes place within the grounds of the sanitarium and inside his own delusions and flashbacks, as he confronts the ghosts of his past. The dark mood and graphics of the game are matched by an equally ominous musical background.

The game uses a bird's-eye view perspective and a non-tiled 2D navigational system. Each world and setting carries a distinct atmosphere that presents either the real world, the imaginary world, or a mix of both of the main protagonist. In many cases, it is unclear to the player if the world the character is currently in is real or a product of Max's own imagination. This indistinction underlines much of the horror portrayed in the game.

Gamasutra's [postmortem](http://www.gamasutra.com/view/feature/3299/postmortem_dreamforges_sanitarium.php) provides some interesting insight into the game's development.

### Development

The following is just a copy of what was available on the old [Google Code](http://code.google.com/p/asylumengine/) project page.

#### October 16, 2009

Quite a bit of work was done over the summer. Sadly though, progress has ground to a halt for the moment. I'm going to be unavailable to the project for a while now as I've got very little free time any more due to changes in my "real" life (family issues, new contract .. etc).

Figured I'd update everyone here, as I'll still be available, but sadly, won't be contributing for the next few months :(

Hopefully someone else can pick up the slack while I fulfil my other obligations.

#### July 8, 2009

Several changes have been made, so it's high time to make an update here :)

There is code for scrolling and showing up objects and actors (properly clipped)
We now have a preliminary script interpreter, so game scripts are read and partially parsed, actors are now drawn in the scene, and there is some interaction with the environment (e.g. "examine" actions).
The movie subtitles (from the vids.cap file) are now working correctly, so the movie code is pretty much complete.
Scene information is partially read, and the scene hotspots are created correctly.
The mouse cursor is now initialized and animated properly
Game texts and game fonts are read correctly (can be seen in the menu)
There is preliminary code for walking around with the mouse.
Some of the menu screens are now working (like, for example, the credits screen)

{% img center /images/sntrm3.png %}

#### June 16, 2009

The guys have figured out the text options in the menu screen so other than those that require interaction (Save/Load/Settings/Cinematics), we're done with the menu. The Credits screen works, as does quit confirmation. The main actor format implementation is starting to take shape.

We've moved beyond the main menu to the first scene (The Tower Cells). The scene is slowly being parsed, as we're pulling the background from the parsed scene, as well as the animations.

The main actor format is also underway. We've deduced the contents and have placed a test loop of the actor walking over the background.

{% img center /images/sntrm2.png %}

#### June 6, 2009

Resource loading is job one, scene implementation is job two. The various formats (graphics, sounds, music, curors, palettes) are more or less in place.

We've also got the menu up and running, but no event code associated with it (so you can't click on anything).

{% img center /images/sntrm1.png %}
