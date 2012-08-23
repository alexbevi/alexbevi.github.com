---
layout: post
title: "Keeping Pry Breakpoints out of Git"
date: 2012-08-23 07:57
comments: true
categories: [Ruby, Pry, Git]
---

My Ruby workflow as of late has almost always contained [Git](http://www.git-scm.com) for version control, and [Pry](http://pryrepl.org/) for debugging.

Although it's extremely convenient during development to add a quick breakpoint using `binding.pry`, it can be a bit frustrating to clients if you accidentally deploy with these breakpoints still intact.

After hunting around for a bit, I decided to write a pre-commit [hook](http://git-scm.com/book/en/Customizing-Git-Git-Hooks) that would check the files I was about to check in to ensure that I didn't accidentally still have breakpoints enabled.

{% gist 3436040 %}

This file just needs to be saved to `/path/to/source/.git/hooks/pre-commit` and made exectuable.

If you happen to leave a breakpoint intact, the next time you try to commit your changes, the commit will fail and indicate where these breakpoints are, and what files need to be updated to allow the commit to succeed.

{% img /images/2012-08-23-ss.png %}

Note that this is just a quick sample for Ruby source. If you wanted to search your template files `(haml|erb|rhtml ... etc)`, you could replace the `find` with a `grep -E` :)

