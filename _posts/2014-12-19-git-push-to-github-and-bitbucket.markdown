---
layout: post
title: "Git Push to GitHub and Bitbucket"
date: 2014-12-19 13:05:35 -0500
comments: true
categories: [Scripting]
tags: [git, github, bitbucket]
---

I just want to start off by saying how much I LOVE [Git](http://git-scm.com). I've been working with it for a number of years now (coming from [Subversion](https://subversion.apache.org) and sharing code on [Google Code](https://code.google.com) and [SourceForge](http://sourceforge.net)) and have fully embraced [GitHub](https://github.com) as the "victor" (IMHO) for both online source control and collaborative development.

The one "downside" to GitHub though is that you don't have the ability to manage a private repository for free. They do offer reasonable hosting plans, but I generally use private repos for client work or other professional backups.

[Bitbucket](https://bitbucket.org) on the other hand offers unlimited private repositories. They limit the collaborative features you have access to, but if you're strictly mirroring or backing up, that's not an issue.

In order to configure your repository to push to both, all you need to do is:

**1)** create a new repository on Bitbucket

**2a)** edit the `.git/config` of your local repository

**2b)** add a second `url` entry under the same **remote** as you're already pushing to

![](/images/20141219-git-001.png)

**3)** now to initialze the Bitbucket remote execute `git push origin -u --all`.

![](/images/20141219-git-002.png)

This will attempt to push all branches to the remote named *origin*. Since the version on GitHub is already up to date, the Bitbucket version will be initialized and all changes will be pushed.

Now, whenever you issue a `git push` command, both remote repositories will receive the changesets!
