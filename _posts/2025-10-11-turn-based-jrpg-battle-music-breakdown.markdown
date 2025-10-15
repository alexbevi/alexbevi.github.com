---
layout: post
title: "Turn-based JRPG Battle Music Breakdown"
date: 2025-10-11 21:06:53 -0400
comments: true
categories: ["Battle Music Breakdown"]
tags: [series, jrpg_music]
image: /images/jrpg_music/banner.png
math: true
pin: true
---

I've been a huge fan of traditional, turn-based Japanese role playing games since I first played [Dragon Quest]({% post_url 2016-06-23-just-finished-dragon-quest-i %}) many, many years ago. I started getting back into these 8/16-bit JRPGs when I decided I wanted to do a series of game reviews for that genre, but that effort sort of petered out. During this time though there was something about the grind in these JRPGs that really appealed to me, but the main hook - even on the Nintendo Entertainment System - was the music.

These games all tended to have great intros, overworld themes, dungeon and town themes and varied battle tracks. The latter has always stuck in my head the most, likely since you spent so much time getting into random battles to level your characters up so you'd be presented with the same songs over and over again. When you found your way to a boss and the song changed to something slightly more intense it really got your heart pumping.

Having played through many of these games over the past 30 odd years I can definitely say there's a bit of a formula to how these songs progress, which I wanted to explore in more detail and try to rank to determine which games have the best battle music. I'm not really musically inclined, so this is really just an exercise in categorization based on some arbitrary aspects of the soundtracks I think sound good.

Turn based JRPGs all tend to follow a similar formula that includes:

* one to many general battle themes
* one to many boss battle themes
* possibly one or more special encounter themes
* a final battle theme

What I'll be attempting to do is to break down each game's tracks from these categories based on the following pseudo-"scientific" methodology.

## Scoring Methodology

What I'm going to do is listen to the various battle themes from as a number of turn-based JRPGs and score them as consistently as possible. Since not all games have the same number of songs, and the quality can vary greatly based on what the sound chips of each system were capable of, the scores will largely be based on my opinion of what I think sounds good and why.

### What I score (per track)

Each battle track is rated on five simple, listen-first criteria on a scale of 0–5:

1. **Hook & Identity** — Is there a memorable idea you can hum?\
   *0: none • 3: clear hook • 5: unforgettable, with small variations.*

2. **Energy & Drive** — Does the groove push turns along without clutter?\
   *0: sluggish • 3: steady • 5: propulsive yet controlled.*

3. **Color & Suspense** — Do you feel mood shifts and push→release moments?\
   *0: flat • 3: some ebb/flow • 5: gripping builds and payoffs.*

4. **Clarity & Loop** — Clean mix, readable parts, invisible loop, low fatigue.\
   *0: muddy/annoying • 3: fine for a few loops • 5: polished, long, fresh.*

5. **Situational Fit** — Does it match encounter stakes and turn-based cadence/UI tempo?\
   *0: mismatch • 3: broadly fits • 5: feels designed for the moment.*

**Track score**: $$ (S_{\text{track}})$$ is the average of those five (0–5).

## How multiple tracks are handled

Games can have several **Normal** and **Boss** tracks. Some games may have **Special** encounter tracks, which would be considered as part of the overall **Boss** score. If the **Final** battle track has multiple phases, each will be scored as a separate track. Once each track is  scored, I'll then compute a **role average**:

* $(R_{\text{Normal}} = \text{mean of all Normal } S_{\text{track}})$
* $(R_{\text{Boss/Special}} = \text{mean of all Boss/Special } S_{\text{track}})$
* $(R_{\text{Final}} = \text{mean of all Final } S_{\text{track}})$

> This doesn’t penalize games with fewer tracks; quality matters more than quantity.

### Suite checks (game-level)

I also score three suite-level items on a 0–5 scale:

* **(TC) Thematic Cohesion (12.5%)** — Shared DNA (motif/palette/rhythm) across Normal→Boss/Special→Final.
* **(ESC) Escalation (12.5%)** — Clear rise in energy/suspense from Normal→Boss/Special→Final; motif/orchestration grow.
* **(SC) Suite Completeness (5%)** — Expectation met: ≥2 battle tracks (Normal+Boss combined) **and** a Final.\
  *0 none • 3 one battle + final • 5 ≥2 battle + final.*

For `SC` my expectation is just that there's enough of a variety to the soundtrack for there to be a bare minimum of 1 normal battle track, 1 boss track and a final battle track.

### From tracks to a single game score

First, combine roles into a **Battle Quality (BQ)** score (0–5) using encounter weights:

* Weights: Normal **0.45**, Boss **0.30**, Final **0.25**.
* $( \text{BQ} = \dfrac{0.45 R_N + 0.30 R_B + 0.25 R_F}{\text{sum of weights for roles present}} )$

Then convert to a 100-point scale:

* **Final Score (/100)**
  $(= 20 \times \big(0.75 \cdot \text{BQ} + 0.125 \cdot TC + 0.125 \cdot ESC + 0.05 \cdot SC\big))$

> Intuition for weights: ~75% reflects how good the **battle tracks** sound and function moment-to-moment; the rest rewards **cohesion**, **escalation**, and **meeting the expected suite**.

### Consistency notes

* I normalize playback loudness so volume doesn’t bias "energy."
* I use **in-game versions** (arranges mentioned separately).
* Older hardware isn’t penalized for fidelity; clarity and function are judged **within constraints**.
* When a Final has phases, I score each phase and average them into $(R_{\text{Final}})$.

That’s the whole system: simple per-track ears-on scoring, fair handling of multiple tracks, and a transparent roll-up into one number. Is this over-engineered ... maybe (and it was excuse to incorporate [MathJax](https://www.mathjax.org/) rendering into my blog) ... but hopefully it gives me a straightforward enough approach to score some of these games across multiple generations of consoles fairly and consistently.

## Games List

To kick things off I started by taking the [Traditional Turn-Based JRPGs - Game list](https://www.reddit.com/r/JRPG/comments/ejm3az/traditional_turnbased_jrpgs_game_list/) from Reddit, turning it into a table and determining I'd use that as my source of truth moving forward.

It's very likely this is not comprehensive, and I may choose to skip games for any number of reasons - but for now this is what I'm looking to cover. For my [Let's Adventure! A Journey into Adventure Games (1980-1999)]({% post_url 2021-07-28-adventure-games-1980-1999 %}) series I added a summary like the following, so figured it would be worth doing here as well:
<hr/>
{%- assign games_finished = 1  -%}
{%- assign games_skipped  = 0  -%}
{%- assign games_total    = 301 -%}
```js
{
  "progress": {
    "finished": {{ games_finished }},
     "skipped": {{ games_skipped }},
       "total": {{ games_total }}
  },
  "completed": "{{ games_finished | plus: games_skipped | times: 100.0 | divided_by: games_total | round: 2 }}%"
}
```

As I work through these I'll update the list below with links to each game's battle music breakdown.

| Game                                                     | Original System | Released |
| -------------------------------------------------------- | --------------- | -------- |
| 7th Dragon                                               | DS              | 2009     |
| 7th Dragon 2020                                          | PSP             | 2011     |
| 7th Dragon 2020-II                                       | PSP             | 2013     |
| 7th Dragon III Code: VFD                                 | 3DS             | 2015     |
| 7th Saga                                                 | SNES            | 1993     |
| A Witch's Tale                                           | DS              | 2009     |
| Albert Odyssey: Legend of Eldean                         | SAT             | 1996     |
| Anachronox                                               | PC              | 2001     |
| Ar Nosurge                                               | PS3             | 2014     |
| Ar Tonelico 2                                            | PS2             | 2007     |
| Ar Tonelico: Melody of Elemia                            | PS2             | 2006     |
| Arabian Nights: Sabaku no Seirei Ou                      | SNES            | 1996     |
| Arc Rise Fantasia                                        | Wii             | 2009     |
| Aretha                                                   | SNES            | 1993     |
| Aretha II: Arial's Wonderful Adventure                   | SNES            | 1994     |
| Asuncia: Matsue no Jubaku                                | PS1             | 1997     |
| Atelier Ayesha: The Alchemist of Dusk                    | PS3             | 2012     |
| Atelier Elie: The Alchemist of Salburg 2                 | PS1/PS2         | 1998     |
| Atelier Escha & Logy: Alchemists of the Dusk Sky         | PS3             | 2013     |
| Atelier Firis: The Alchemist of the Mysterious Journey   | PS4             | 2016     |
| Atelier Iris 2: The Azoth of Destiny                     | PS2             | 2005     |
| Atelier Iris 3: Grand Phantasm                           | PS2             | 2006     |
| Atelier Iris: Eternal Mana                               | PS2             | 2004     |
| Atelier Marie: The Alchemist of Salburg                  | PS1/PS2         | 1997     |
| Atelier Meruru: The Apprentice of Arland                 | PS3             | 2011     |
| Atelier Rorona: The Alchemist of Arland                  | PS3             | 2009     |
| Atelier Shallie: Alchemists of the Dusk Sea              | PS3             | 2014     |
| Atelier Sophie: The Alchemist of the Mysterious Book     | PS4             | 2015     |
| Atelier Totori: The Adventurer of Arland                 | PS3             | 2010     |
| Beyond the Beyond                                        | PS1             | 1995     |
| Bishoujo Senshi Sailor Moon: Another Story               | SNES            | 1995     |
| Blade Dancer: Lineage of Light                           | PSP             | 2006     |
| Bloody Warriors: Shan-Go no Gyakushuu                    | NES             | 1990     |
| Blue Almanac                                             | MD              | 1991     |
| Blue Dragon                                              | X360            | 2006     |
| Blue Reflection                                          | PS4             | 2017     |
| Brave Story: New Traveler                                | PSP             | 2006     |
| Bravely Default                                          | 3DS             | 2012     |
| Bravely Second: End Layer                                | 3DS             | 2015     |
| Breath of Fire                                           | SNES            | 1993     |
| Breath of Fire II                                        | SNES            | 1994     |
| Breath of Fire III                                       | PS1             | 1997     |
| Breath of Fire IV                                        | PS1             | 2000     |
| Breath Of Fire: Dragon Quarter                           | PS2             | 2002     |
| Chaos World                                              | NES             | 1991     |
| Choumahou Tairiku Wozz                                   | SNES            | 1995     |
| Chrono Cross                                             | PS1             | 1999     |
| Chrono Trigger                                           | SNES            | 1995     |
| Cosmic Fantasy 2                                         | PCE             | 1992     |
| Cyber Knight                                             | PC Engine       | 1990     |
| Cyber Knight II                                          | SNES            | 1994     |
| Daikaijuu Monogatari                                     | SNES            | 1994     |
| Daikaijyuu Monogatari II                                 | SNES            | 1996     |
| Dark Half                                                | SNES            | 1996     |
| Dark Rose Valkyrie                                       | PS4             | 2016     |
| Death end re;Quest                                       | PS4             | 2018     |
| Defenders of Oasis                                       | GG              | 1992     |
| Destiny of an Emperor                                    | NES             | 1989     |
| Destiny of an Emperor 2                                  | NES             | 1991     |
| Double Moon Densetsu                                     | NES             | 1992     |
| Dragon Ball Z: Attack of the Saiyans                     | DS              | 2009     |
| Dragon Ball Z: Super Saiya Densetsu                      | SNES            | 1992     |
| [Dragon Quest]({% post_url 2025-10-13-dragon-quest%})    | NES             | 1986     |
| Dragon Quest II                                          | NES             | 1987     |
| Dragon Quest III                                         | NES             | 1988     |
| Dragon Quest IV                                          | NES             | 1990     |
| Dragon Quest V: Tenkuu no Hanayome                       | SNES            | 1992     |
| Dragon Quest VI                                          | SNES            | 1995     |
| Dragon Quest VII                                         | PS1             | 2000     |
| Dragon Quest VIII                                        | PS2             | 2004     |
| Dragon Quest XI                                          | PS4             | 2017     |
| Dragon Quest IX: Sentinels of the Starry Skies...        | DS              | 2009     |
| Dragon Slayer: The Legend of Heroes                      | PC-88           | 1989     |
| Dragon Star Varnir                                       | PS4             | 2018     |
| Dragoneer's Aria                                         | PSP             | 2007     |
| Dream Master                                             | NES             | 1992     |
| Dream Maze: Kigurumi Daibouken                           | SNES            | 1994     |
| Dual Orb 2                                               | SNES            | 1994     |
| Earthbound                                               | SNES            | 1994     |
| EarthBound Beginnings                                    | NES             | 1989     |
| Eien no Filena                                           | SNES            | 1995     |
| Eiyuu Densetsu: Ao no Kiseki                             | PSP             | 2011     |
| Eiyuu Densetsu: Zero no Kiseki                           | PSP             | 2010     |
| Enchanted Arms                                           | X360            | 2006     |
| Ephemeral Fantasia                                       | PS2             | 2000     |
| Eternal Legend                                           | GG              | 1991     |
| Final Fantasy                                            | NES             | 1987     |
| Final Fantasy II                                         | NES             | 1988     |
| Final Fantasy III                                        | NES             | 1990     |
| Final Fantasy IV                                         | SNES            | 1991     |
| Final Fantasy V                                          | SNES            | 1992     |
| Final Fantasy VI                                         | SNES            | 1994     |
| Final Fantasy VII                                        | PS1             | 1997     |
| Final Fantasy VIII                                       | PS1             | 1999     |
| Final Fantasy IX                                         | PS1             | 2000     |
| Final Fantasy X                                          | PS2             | 2001     |
| Final Fantasy X-2                                        | PS2             | 2003     |
| Final Fantasy XIII                                       | PS3             | 2009     |
| Final Fantasy XIII-2                                     | PS3             | 2011     |
| Final Fantasy Legend                                     | GB              | 1989     |
| Final Fantasy Legend II                                  | GB              | 1990     |
| Final Fantasy Legend III                                 | GB              | 1991     |
| Final Fantasy Mystic Quest                               | SNES            | 1992     |
| Fullmetal Alchemist: Stray Rondo                         | GBA             | 2004     |
| G.O.D.: Mezameyo to Yobu Koe ga Kikoe                    | SNES            | 1996     |
| Ganbare Goemon Gaiden 2: Tenka no Zaihou                 | NES             | 1992     |
| Ganbare Goemon Gaiden: Kieta Ougon Kiseru                | NES             | 1990     |
| GeGeGe no Kitaro 2                                       | NES             | 1987     |
| Ghost Lion                                               | NES             | 1989     |
| Glory of Heracles                                        | DS              | 2008     |
| God Medicine: Fantasy Sekai no Tanjou                    | GB              | 1993     |
| Golden Sun                                               | GBA             | 2001     |
| Golden Sun: Dark Dawn                                    | DS              | 2010     |
| Golden Sun: The Lost Age                                 | GBA             | 2002     |
| Grand Knights History                                    | PSP             | 2011     |
| Grandia                                                  | PS1             | 1997     |
| Grandia II                                               | DC/PC           | 2000     |
| Grandia III                                              | PS2             | 2005     |
| Grandia Xtreme                                           | PS2             | 2002     |
| Great Greed                                              | GB              | 1992     |
| Guardian's Crusade                                       | PS1             | 1998     |
| Heracles no Eikou: Tōjin Makyō Den                       | NES             | 1987     |
| Heracles no Eikou II: Titan no Metsubo                   | NES             | 1989     |
| Heracles no Eikou III: Kamigami no Chinmoku              | SNES            | 1992     |
| Heracles no Eikou IV: Kamigami Kara no Okurimono         | SNES            | 1994     |
| Hero Senki - Project Olympus                             | SNES            | 1992     |
| Hexyz Force                                              | PSP             | 2009     |
| Hoshi o Miru Hito                                        | NES             | 1987     |
| Hourai Gakuen no Bouken!: Tenkousei Scramble             | SNES            | 1996     |
| Hyperdimension Neptunia                                  | PS3             | 2010     |
| Hyperdimension Neptunia mk2                              | PS3             | 2011     |
| Hyperdimension Neptunia Victory                          | PS3             | 2012     |
| I Am Setsuna                                             | PS4             | 2016     |
| Indora no Hikari                                         | NES             | 1987     |
| Inindo: Way of the Ninja                                 | SNES            | 1992     |
| JaJaMaru Ninpouchou / Taroâ€™s Quest                     | NES             | 1989     |
| Jojo no Kimyou na Bouken                                 | SNES            | 1993     |
| Juvei Quest                                              | NES             | 1991     |
| Kaijuu Monogatari                                        | NES             | 1988     |
| Kawa no Nushi Tsuri                                      | NES             | 1990     |
| Kininkou Maroku Oni                                      | GB              | 1990     |
| Knight Quest JRPG                                        | GB              | 1991     |
| Koudelka                                                 | PS1             | 1999     |
| Kouryuu Densetsu Villgust: Kieta Shoujo                  | SNES            | 1992     |
| Lagrange Point                                           | NES             | 1991     |
| Laplace no Ma                                            | PC-88           | 1987     |
| LaSalle Ishii no Child's Quest                           | NES             | 1989     |
| Last Ranker                                              | PSP             | 2010     |
| Legaia 2: Duel Saga                                      | PS2             | 2001     |
| Legend of Legaia                                         | PS1             | 1998     |
| Lennus II: Fuuin no Shito                                | SNES            | 1996     |
| Little Princess: Maru Oukoku no Ningyou Hime 2           | PS1             | 1999     |
| Live a Live                                              | SNES            | 1994     |
| Lost Odyssey                                             | X360            | 2007     |
| Lost Sphear                                              | PS4             | 2017     |
| Lucienne's Quest                                         | 3DO             | 1995     |
| Lufia & the Fortress of Doom                             | SNES            | 1993     |
| Lufia II: Rise of the Sinistrals                         | SNES            | 1995     |
| Lufia: The Legend Returns                                | GBA             | 2001     |
| Lufia: The Ruins of Lore                                 | GBA             | 2002     |
| Lunar: Dragon Song                                       | DS              | 2005     |
| Lunar: Eternal Blue                                      | SCD             | 1994     |
| Lunar: Sanposuru Gakuen                                  | GG              | 1996     |
| Lunar: The Silver Star                                   | SCD             | 1992     |
| Madou Monogatari: Hanamaru Daiyouchi Enji                | SNES            | 1996     |
| Magic Knight Rayearth                                    | SNES            | 1995     |
| Magical Starsign                                         | DS              | 2006     |
| Magical Vacation                                         | GBA             | 2001     |
| Magna Braban: Henreki no Yuusha                          | SNES            | 1994     |
| Magna Carta: Tears of Blood                              | PS2             | 2004     |
| Mahou Kishi Rayearth                                     | GG              | 1994     |
| Mahou Kishi Rayearth 2nd: The Missing Colors             | GG              | 1995     |
| Mana Khemia 2: Fall of Alchemy                           | PS2             | 2008     |
| Mana Khemia: Alchemists of Al-Revis                      | PS2             | 2007     |
| Mario & Luigi: Bowser's Inside Story                     | DS              | 2009     |
| Mario & Luigi: Dream Team                                | 3DS             | 2013     |
| Mario & Luigi: Paper Jam                                 | 3DS             | 2015     |
| Mario & Luigi: Partners in Time                          | DS              | 2005     |
| Mario & Luigi: Superstar Saga                            | GBA             | 2003     |
| Megadimension Neptunia VII                               | PS4             | 2015     |
| Megami Tensei Gaiden: Last Bible II                      | GB              | 1993     |
| Megami Tensei Gaiden: Last Bible Special                 | GG              | 1995     |
| Metal Max                                                | NES             | 1991     |
| Metal Max 3                                              | DS              | 2010     |
| Metal Max Xeno                                           | PS4             | 2018     |
| Metal Saga                                               | PS2             | 2005     |
| Miracle Warriors: Seal of the Dark Lord                  | PC-88           | 1986     |
| Moldorian: Hikari to Yami no Sister                      | GG              | 1994     |
| Momotarou Densetsu                                       | NES             | 1987     |
| Mother 3                                                 | GBA             | 2006     |
| MS Saga: A New Dawn                                      | PS2             | 2005     |
| Musashi no Bouken                                        | NES             | 1990     |
| My World My Way                                          | DS              | 2008     |
| Mystic Ark                                               | SNES            | 1995     |
| Naruto: Path of the Ninja 2                              | DS              | 2006     |
| Nige-Ron-Pa                                              | NGPC            | 2000     |
| Niji no Silkroad                                         | NES             | 1991     |
| Ninjara Hoi!                                             | NES             | 1990     |
| Nostalgia                                                | DS              | 2008     |
| Nushi Tsuri Adventure: Kite no Bouken                    | GBC             | 2000     |
| Octopath Traveler                                        | Switch          | 2018     |
| Okage: Shadow King                                       | PS2             | 2001     |
| Omega Quintet                                            | PS4             | 2014     |
| Opoona                                                   | Wii             | 2007     |
| Oriental Blue: Ao no Tengai                              | GBA             | 2003     |
| Paladin's Quest                                          | SNES            | 1992     |
| Panzer Dragoon Saga                                      | SAT             | 1998     |
| Paper Mario                                              | N64             | 2000     |
| Paper Mario: The Thousand-Year Door                      | GC              | 2004     |
| Persona 2: Eternal Punishment                            | PS1             | 2000     |
| Persona 2: Innocent Sin                                  | PS1             | 1999     |
| Persona 3                                                | PS2             | 2006     |
| Persona 4                                                | PS2             | 2008     |
| Persona 5                                                | PS4             | 2016     |
| Phantasy Star                                            | MS              | 1987     |
| Phantasy Star Gaiden                                     | GG              | 1992     |
| Phantasy Star II                                         | MD              | 1989     |
| Phantasy Star III                                        | MD              | 1990     |
| Phantasy Star IV                                         | MD              | 1993     |
| Princess Minerva                                         | SNES            | 1995     |
| Quest 64                                                 | N64             | 1998     |
| Quest: Brian's Journey                                   | GBC             | 2000     |
| Radiant Historia                                         | DS              | 2010     |
| Ranma 1/2: Akanekodan Teki Hihou                         | SNES            | 1993     |
| Revelations: The Demon Slayer                            | GB              | 1992     |
| Riviera: The Promised Land                               | WSC             | 2002     |
| Romancing SaGa                                           | SNES            | 1992     |
| Romancing SaGa 2                                         | SNES            | 1993     |
| Romancing SaGa 3                                         | SNES            | 1995     |
| Romancing SaGa: Minstrel Song                            | PS2             | 2005     |
| Rudra no Hihou                                           | SNES            | 1996     |
| Ryuuki Heidan: Danzarb                                   | SNES            | 1993     |
| SaGa Frontier                                            | PS1             | 1997     |
| SaGa Frontier 2                                          | PS1             | 1999     |
| SaGa: Scarlet Grace                                      | Vita            | 2016     |
| Samsara Naga                                             | NES             | 1990     |
| Sands of Destruction                                     | DS              | 2008     |
| SD Gundam Gaiden Knight Gundam Story                     | NES             | 1990     |
| SD Keiji Blader                                          | NES             | 1991     |
| SD Snatcher                                              | MSX2            | 1990     |
| Secret of the Stars                                      | SNES            | 1993     |
| Septerra Core                                            | PC              | 1999     |
| Shadow Hearts                                            | PS2             | 2001     |
| Shadow Hearts: Covenant                                  | PS2             | 2004     |
| Shadow Hearts: From the New World                        | PS2             | 2005     |
| Shin Megami Tensei IV                                    | 3DS             | 2013     |
| Shin Megami Tensei IV: Apocalypse                        | 3DS             | 2016     |
| Shin Megami Tensei: Digital Devil Saga                   | PS2             | 2004     |
| Shin Megami Tensei: Digital Devil Saga 2                 | PS2             | 2005     |
| Shin Megami Tensei: Nocturne                             | PS2             | 2003     |
| Shin Seikoku: La Wares                                   | SNES            | 1995     |
| Shinsenden                                               | NES             | 1989     |
| Silva Saga                                               | NES             | 1992     |
| Silva Saga II: The Legend of Light and Darkness          | SNES            | 1993     |
| Skies of Arcadia                                         | DC              | 2000     |
| Slayers                                                  | SNES            | 1994     |
| Sol Trigger                                              | PSP             | 2012     |
| Startling Odyssey II                                     | PCE             | 1994     |
| STED: Iseki Wakusei no Yabou                             | NES             | 1990     |
| Suikoden                                                 | PS1             | 1995     |
| Suikoden II                                              | PS1             | 1998     |
| Suikoden III                                             | PS2             | 2002     |
| Suikoden IV                                              | PS2             | 2004     |
| Suikoden Tierkreis                                       | DS              | 2008     |
| Suikoden V                                               | PS2             | 2006     |
| Super Mario RPG: Legend of the Seven Stars               | SNES            | 1996     |
| Surging Aura                                             | MD              | 1995     |
| Sweet Home                                               | NES             | 1989     |
| Tao                                                      | NES             | 1989     |
| Tengai Makyou Zero                                       | SNES            | 1995     |
| Tenshi no Present: Marl Oukoku Monogatari                | PS2             | 2000     |
| Tenshi no Uta: Shiroki Tsubasa no Inori                  | SNES            | 1994     |
| The Alliance Alive                                       | 3DS             | 2017     |
| The Last Remnant                                         | X360            | 2008     |
| The Legend of Dragoon                                    | PS1             | 1999     |
| The Legend of Heroes II: Prophecy of the Moonlight Witch | PC-98           | 1994     |
| The Legend of Heroes III: Song of the Ocean              | PC              | 1999     |
| The Legend of Heroes: A Tear of Vermillion               | PSP             | 1996     |
| The Legend of Heroes: Trails in the Sky                  | PC              | 2004     |
| The Legend of Heroes: Trails in the Sky SC               | PC              | 2006     |
| The Legend of Heroes: Trails in the Sky the 3rd          | PC              | 2007     |
| The Legend of Heroes: Trails of Cold Steel               | PS3             | 2013     |
| The Legend of Heroes: Trails of Cold Steel II            | PS3             | 2014     |
| The Legend of Heroes: Trails of Cold Steel III           | PS4             | 2017     |
| The Legend of Legacy                                     | 3DS             | 2015     |
| The Lord of the Rings: The Third Age                     | PS2/Xbox/GC     | 2004     |
| Thousand Arms                                            | PS1             | 1998     |
| Tokyo Mirage Sessions #FE                                | WiiU            | 2015     |
| Trinity Universe                                         | PS3             | 2009     |
| Tsugunai: Atonement                                      | PS2             | 2001     |
| Unlimited SaGa                                           | PS2             | 2002     |
| Vay                                                      | SCD             | 1993     |
| Wild Arms                                                | PS1             | 1996     |
| Wild Arms 2                                              | PS1             | 1999     |
| Wild Arms 3                                              | PS2             | 2002     |
| Wild Arms 4                                              | PS2             | 2005     |
| Wild Arms 5                                              | PS2             | 2006     |
| Xenogears                                                | PS1             | 1998     |
| Xenosaga Episode I: Der Wille zur Macht                  | PS2             | 2002     |
| Xenosaga Episode II                                      | PS2             | 2004     |
| Xenosaga Episode III                                     | PS2             | 2006     |


