---
layout: post
title: "Gallery Tag for Octopress"
date: 2014-10-07 08:31:08 -0400
comments: true
categories: [Ruby]
categories: [octopress, jekyll]
---

While working on my post about finishing [Robotrek](http://en.wikipedia.org/wiki/Robotrek), I found that I had taken a lot more screenshots than would fit nicely with the amount of copy I intended to write.

<small>I hope to be done the *just finished ...* article soon-ish ...</small>

Since I didn't really want to discard any, I figured I'd just throw the execss screenshots into a carousel or gallery.

I found [an excellent example](https://gist.github.com/kyv/5667902), but it didn't quite produce the results I was looking for.

<!-- more -->

I ended up forking the gist in order to implement a Gallery tag for Jekyll/Octopress that could work with the [Galleria](http://galleria.io/) jQuery plugin.

Now I can build a gallery from my extra screenshots by simply adding

{% raw %}
```
{% galleria %}
/images/robotrek/Robotrek_(USA).000.png
/images/robotrek/Robotrek_(USA).001.png
/images/robotrek/Robotrek_(USA).002.png
/images/robotrek/Robotrek_(USA).003.png
/images/robotrek/Robotrek_(USA).004.png
/images/robotrek/Robotrek_(USA).005.png
/images/robotrek/Robotrek_(USA).006.png
/images/robotrek/Robotrek_(USA).007.png
/images/robotrek/Robotrek_(USA).008.png
/images/robotrek/Robotrek_(USA).009.png
/images/robotrek/Robotrek_(USA).010.png
{% endgalleria %}
```
{% endraw %}

to my post, which will produce the following gallery:

{% galleria %}
/images/robotrek/Robotrek_(USA).000.png
/images/robotrek/Robotrek_(USA).001.png
/images/robotrek/Robotrek_(USA).002.png
/images/robotrek/Robotrek_(USA).003.png
/images/robotrek/Robotrek_(USA).004.png
/images/robotrek/Robotrek_(USA).005.png
/images/robotrek/Robotrek_(USA).006.png
/images/robotrek/Robotrek_(USA).007.png
/images/robotrek/Robotrek_(USA).008.png
/images/robotrek/Robotrek_(USA).009.png
/images/robotrek/Robotrek_(USA).010.png
{% endgalleria %}

I've included the gist below. If you want to download and install this yourself, just download the gist to `/path/to/octopress/plugins`.

{% gist alexbevi/1c185c6a037d63f6aec7 %}