---
layout: post
title: "Turn-based JRGP Battle Music Breakdown Sorted by Score"
date: 2025-10-15 06:03:45 -0400
comments: true
categories: ["Battle Music Breakdown"]
tags: [series, jrpg_music]
image: /images/jrpg_music/banner.png
math: true
---

This page is a list of the battle music scores from the ["Turn-based JRGP Battle Music Breakdown"]({% post_url 2025-10-11-turn-based-jrpg-battle-music-breakdown %}) series, sorted by rating. See the _["Battle Music Breakdown"](https://www.alexbevi.com/categories/battle-music-breakdown/) category page_ for a list of content by date of publication.

## Scoring Criteria

$$
\text{Final} \;=\;
20\left[
0.75\cdot
\frac{\displaystyle \sum_{r\in\{N,B,F\}} w_r\,\mathbf{1}_{|T_r|>0}\!\left(\frac{1}{|T_r|}\sum_{t\in T_r}\frac{\mathrm{Hook}_t+\mathrm{Energy}_t+\mathrm{Color}_t+\mathrm{Clarity}_t+\mathrm{Fit}_t}{5}\right)}
{\displaystyle \sum_{r\in\{N,B,F\}} w_r\,\mathbf{1}_{|T_r|>0}}
\;+\;0.125\,TC \;+\;0.125\,ESC \;+\;0.05\,SC
\right]
$$

**Where**

- $r \in \{N,B,F\}$ are roles: Normal ($N$), Boss (incl. Special; $B$), Final ($F$)
- $T_r$ is the set of tracks for role $r$ and $\|T_r\|$ is the count
- $\mathbf{1}_{\|T_r\|>0}$ is an indicator (1 if the role has ≥1 track, else 0) so the $BQ$ denominator uses only roles that exist.
- Track score: $S_t=\dfrac{\mathrm{Hook}_t+\mathrm{Energy}_t+\mathrm{Color}_t+\mathrm{Clarity}_t+\mathrm{Fit}_t}{5}$
- Weights: $w_N=0.45,\; w_B=0.30,\; w_F=0.25$
- ~75% reflects how good the battle tracks sound and function moment-to-moment; the rest rewards cohesion ($TC$), escalation ($ESC$), and meeting the expected suite ($SC$).


## Scores

1. **38%** [Dragon Quest (NES) - 1986]({% post_url 2025-10-13-dragon-quest %})



