---
layout: post
title: "Combine GoPro Files with FFmpeg"
date: 2023-12-21 09:14:28 -0500
comments: true
categories: [video]
tags: [ffmpeg, video, scripting]
image: /images/camera-banner.jpg
---

I have a [HERO10 Black](https://gopro.com/en/ca/shop/cameras/hero10-black/CHDHX-101-master.html) that I use to record video from my kids hockey games ([such as this one](https://youtu.be/nvAMBfcpHJY)), but since I typically move around with the camera between periods, the videos end up being "chaptered", or multiple single videos. Though you'd think you could just sort these files by filename, GoPro's [file naming convention](https://community.gopro.com/s/article/GoPro-Camera-File-Naming-Convention?language=en_US) doesn't actually lend itself well to this, and doing so results in out of sequence video.

For example, a recent video that I took had a directory listing like the following:

```
$ ll

-rwx------  1 alex  staff   265M 20 Dec 19:14 GL010118.LRV
-rwx------  1 alex  staff   265M 20 Dec 19:35 GL010119.LRV
-rwx------  1 alex  staff   265M 20 Dec 20:08 GL010120.LRV
-rwx------  1 alex  staff   194M 20 Dec 19:22 GL020118.LRV
-rwx------  1 alex  staff   234M 20 Dec 19:46 GL020119.LRV
-rwx------  1 alex  staff   265M 20 Dec 20:20 GL020120.LRV
-rwx------  1 alex  staff    48M 20 Dec 20:22 GL030120.LRV
-rwx------  1 alex  staff   3.7G 20 Dec 19:14 GX010118.MP4
-rwx------  1 alex  staff    10K 20 Dec 19:02 GX010118.THM
-rwx------  1 alex  staff   3.7G 20 Dec 19:35 GX010119.MP4
-rwx------  1 alex  staff    10K 20 Dec 19:24 GX010119.THM
-rwx------  1 alex  staff   3.7G 20 Dec 20:08 GX010120.MP4
-rwx------  1 alex  staff    10K 20 Dec 19:56 GX010120.THM
-rwx------  1 alex  staff   2.7G 20 Dec 19:22 GX020118.MP4
-rwx------  1 alex  staff    10K 20 Dec 19:14 GX020118.THM
-rwx------  1 alex  staff   3.3G 20 Dec 19:46 GX020119.MP4
-rwx------  1 alex  staff    10K 20 Dec 19:35 GX020119.THM
-rwx------  1 alex  staff   3.7G 20 Dec 20:20 GX020120.MP4
-rwx------  1 alex  staff    10K 20 Dec 20:08 GX020120.THM
-rwx------  1 alex  staff   696M 20 Dec 20:22 GX030120.MP4
-rwx------  1 alex  staff    10K 20 Dec 20:20 GX030120.THM
```

GoPro creates additional [`LRV` and `THM` files](https://community.gopro.com/s/article/What-are-thm-and-lrv-files?language=en_US) when recording video so that you can quickly preview thumbnails and video on the camera itself. If we filter these out and just view the `MP4` files you'll see these aren't necessarily in order:

```
$ ls *.MP4

-rwx------  1 alex  staff   3.7G 20 Dec 19:14 GX010118.MP4
-rwx------  1 alex  staff   3.7G 20 Dec 19:35 GX010119.MP4
-rwx------  1 alex  staff   3.7G 20 Dec 20:08 GX010120.MP4
-rwx------  1 alex  staff   2.7G 20 Dec 19:22 GX020118.MP4
-rwx------  1 alex  staff   3.3G 20 Dec 19:46 GX020119.MP4
-rwx------  1 alex  staff   3.7G 20 Dec 20:20 GX020120.MP4
-rwx------  1 alex  staff   696M 20 Dec 20:22 GX030120.MP4
```

An easy way to get the videos into a "correct" order would be to sort them chronologically by create date:

```
$ ll -tr *.MP4

-rwx------  1 alex  staff   3.7G 20 Dec 19:14 GX010118.MP4
-rwx------  1 alex  staff   2.7G 20 Dec 19:22 GX020118.MP4
-rwx------  1 alex  staff   3.7G 20 Dec 19:35 GX010119.MP4
-rwx------  1 alex  staff   3.3G 20 Dec 19:46 GX020119.MP4
-rwx------  1 alex  staff   3.7G 20 Dec 20:08 GX010120.MP4
-rwx------  1 alex  staff   3.7G 20 Dec 20:20 GX020120.MP4
-rwx------  1 alex  staff   696M 20 Dec 20:22 GX030120.MP4
```

Since I want to upload these videos to YouTube for the team to review, I need a single video file. After hunting around for scripts that could do this for me, I did find a few that looked promising - such as [GoPro-Concat-Automation](https://github.com/scuc/GoPro-Concat-Automation) and [gopro-linux](https://github.com/KonradIT/gopro-linu). Ultimately I wanted to be able to just do this myself with a single command, so though these tools got me most of the way there, I ended up opting for my own script instead:

```bash
# run from the directory where your videos are located
# ex: /Volumes/SDCARD/DCIM/100GOPRO/
ffmpeg -f concat -safe 0 \
    -i <(for f in `ls -tr *.MP4`; do echo "file '$PWD/$f'"; done) \
    -c copy output.mp4
```

This uses [FFmpeg](https://ffmpeg.org/) to concatenate the videos and copy them to a new file called `output.mp4`. The input list for the videos is just a bash command to generate a list of MP4 files with the full path to the file in chronological order by create date.

Note that `safe` mode is disabled (see [`ffmpeg` options](https://www.ffmpeg.org/ffmpeg-formats.html#Options)) as having it enabled can result in the video creation failing for file-naming reasons. Why is this enabled by default and not disabled you might ask ... [#5558 _concat protocol should run in "-safe 0" mode by default_](https://trac.ffmpeg.org/ticket/5558) has more info on that topic.