---
layout: post
title: "Pipe Command Output to Logentries"
date: 2014-07-16 12:06:55 -0400
comments: true
categories: [Linux]
tags: [linux, logentries]
---

I've been using [Logentries](https://logentries.com/) for a couple of months now to manage variou project logs and have found it to be extremely convenient.

If you want to retrofit a crontab or any other process to use the Logentries Token-TCP type log, just do the following:

    COMMAND | while read -r line; do echo "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee $line" > /dev/tcp/data.logentries.com/80; done

Where `aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee` is your log token, and `COMMAND` is whatever your like.

For example:

    lsblk | while read -r line; do echo "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee $line" > /dev/tcp/data.logentries.com/80; done


{% picture left /images/20140716-logentries.png %}

Hopefully this helps someone other than myself :)