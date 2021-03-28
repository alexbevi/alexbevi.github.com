---
layout: post
title: "Subversion + Ruby on Heroku via Buildpacks"
date: 2014-07-07 09:28:38 -0400
comments: true
categories: [Heroku]
tags: [redmine, heroku, subversion]
---

Back in 2012, I wrote a post about [Redmine and Subversion on Heroku]({% post_url 2012-11-21-fetching-changesets-in-redmine-from-heroku-using-svn %}) that involved some funky hacks in order to build a working `svn` binary that could be uploaded as part of your Git payload.

This can be done a lot more cleanly by taking advantage of [Heroku Buildpacks](https://devcenter.heroku.com/articles/buildpacks).

<!-- more -->

All of the instructions I provided in my previous post can now be distilled into a single buildpack install command.

If we want to leverage an existing solution, we just add the [Subversion Buildpack](https://devcenter.heroku.com/articles/buildpacks) to our app.

The main "gotcha" here is that we can only have ONE buildpack defined at a time, which is problematic because our app's environment (Ruby, PHP, Node .. etc) is managed as a buildpack (see https://devcenter.heroku.com/articles/buildpacks for more details).

In order to get around this limitation though, we can leverage another buildpack, known as the [heroku-buildpack-multi](https://github.com/ddollar/heroku-buildpack-multi) buildpack which allows us to define multiple buildpacks.

For our purposes, we're going to add Subversion and Ruby to our app:

    $ cd /path/to/app

    $ heroku config:add BUILDPACK_URL=https://github.com/ddollar/heroku-buildpack-multi.git

    $ cat .buildpacks
    https://github.com/cucumber-ltd/heroku-buildpack-subversion.git
    https://github.com/heroku/heroku-buildpack-ruby.git

    $ git commit .buildpacks -m "Add Buildpacks"
    $ git push heroku master

This has helped me with my Redmine deployment on Heroku. Did it help you at all? Did I get something wrong. Let me know ;)