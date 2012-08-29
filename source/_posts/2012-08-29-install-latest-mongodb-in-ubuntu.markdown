---
layout: post
title: "Install Latest MongoDB in Ubuntu"
date: 2012-08-29 13:46
comments: true
categories: [Ubuntu, MongoDB, Bash]
---

A couple projects I work on use [MongoDB](http://www.mongodb.org/) as the database, and I'm generally not satisfied to use the (often outdated) version that ships with Ubuntu.

As a result, I wrote this script to automate fetching, extracting and linking the latest version.

<!-- more -->

To configure the script, just replace the `PKG` information with whatever value is most relevant for your configuration at [http://www.mongodb.org/downloads](http://www.mongodb.org/downloads).

{% gist 3516100 %}

Note that this script pulls `mongod` from a gist which I created. This script is originally from [Ijonas Kisselbach](https://github.com/ijonas)'s [dotfiles](https://raw.github.com/ijonas/dotfiles/master/etc/init.d/mongod).