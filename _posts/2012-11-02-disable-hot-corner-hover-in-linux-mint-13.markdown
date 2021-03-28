---
layout: post
title: "Disable Hot Corner Hover in Linux Mint"
date: 2012-11-02 08:01
comments: true
categories:  [Linux, Configuration]
tags:  [linux, mint, cinnamon]
---

**UPDATE** For Linux Mint 16, the `hotCorner` settings have been moved to `/usr/share/cinnamon/js/ui/hotCorner.js`.

I use [Synergy](http://www.synergy-foss.org) on all my computers to share a common mouse and keyboard, but I've found that with Gnome 3 based distributions, the hot corner was causing me some grief.

The beauty of using a Linux-based system though is that you can pretty much change anything you're unhappy with, so that's what I'm here to do.

<!-- more -->

By default, [Linux Mint](http://linuxmint.com) uses the [Cinnamon](http://cinnamon.linuxmint.com) desktop, so the configuration file we're looking for is at `/usr/share/cinammon/js/ui/layout.js`.

For Linux Mint 12, which still used [Gnome Shell](https://live.gnome.org/GnomeShell), the file was at `/usr/share/gnome-shell/js/ui/layout.js`.

Edit the appropriate file

    $ sudo nano /usr/share/cinammon/js/ui/layout.js

Locate the following section (I just searched for _hot-corner_)

``` javascript
this._corner = new Clutter.Rectangle({ name: 'hot-corner',
                                       width: 1,
                                       height: 1,
                                       opacity: 0,
                                       reactive: true });
```

And change the value of `reactive` from _true_ to _false_:

``` javascript
this._corner = new Clutter.Rectangle({ name: 'hot-corner',
                                       width: 1,
                                       height: 1,
                                       opacity: 0,
                                       reactive: false });
```

Log off, then back on. Booya!