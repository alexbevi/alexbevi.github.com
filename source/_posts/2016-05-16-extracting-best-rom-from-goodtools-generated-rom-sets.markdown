---
layout: post
title: "Extracting Best ROM from GoodTools Generated ROM Sets"
date: 2016-05-16 15:17:38 -0400
comments: true
categories: [linux, roms]
published: false
---

As a kid of the 80's, I have fond memories of all the old 8-bit and 16-bit consoles that I grew up with.

Although it's easy enough to find ROMs, I tend to find myself going for the [GoodTools](https://en.wikipedia.org/wiki/GoodTools) generated sets more often than not as they're considered "complete".

This is kind of ridiculous as I don't speak Japanese, which constitutes the vast majority of the contents of these sets.

Even though most emulators support compressed ROM sets, I'd prefer to just have the English ROMs available on their own in one place.

As a programmer, I thought "How can I do this in Linux?", but more specifically, "how do I do this from the command line directly?".

```
# extract best rom to directory
# best contains !
7z e "*.7z" -o../../ *[!]*.* -r

# purge all non US/European
find . -type f ! -name '*(U)*' ! -name '*(E)*' -delete

# purge duplicates where a (U) exists alongiside an (E)
for f in *"(E)"*; do us=`echo $f | sed -r 's/\(E\)+/\(U\)/g'`; if [ -e "$us" ]; then echo "FOUND $us - removing $f"; rm "$f"; fi; done
```

If you find yourself with compressed ROM sets and you want to just grab the English ones, this might just come in handy ;)

