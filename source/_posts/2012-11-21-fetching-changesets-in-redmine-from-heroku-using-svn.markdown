---
layout: post
title: "Fetching Changesets in Redmine from Heroku using Subversion"
date: 2012-11-21 08:44
comments: true
categories: [redmine, heroku, subversion, vagrant]
---

[**NOTE**: The method described below should still work, but it's much easier to just use a Heroku buildpack (see [this post]({% post_url 2014-07-07-subversion-plus-ruby-on-heroku-via-buildpacks %}) for details)]

I manage my open source and contract development projects using [Redmine](http://www.redmine.org).

Since I'm "frugal", I tend to try to push the free hosting envelope as far as possible. As a result, I have my Redmine deployment on [Heroku](http://www.heroku.com), my files and attachments on [Dropbox](http://www.dropbox.com) and my source on [GitHub](https://github.com).

I also like to link to changesets in my projects, which is easy enough to do when you host the source and the Redmine server on the same machine.

Not so easy with Heroku+GitHub .... until now!

By the end of this tutorial, we will have:

* Setup a build system using Vagrant that matches the Heroku hosting environment
* Compiled a statically linked [Subversion](http://subversion.apache.org/) client
* Added the svn client to our Redmine repository and pushed it to Heroku
* Configured a project in Redmine to fetch changesets from GitHub using Subversion

<!-- more -->

## Overview

In 2012, [GitHub announced SVN support](https://github.com/blog/626-announcing-svn-support), which primarily opened the service up to developers who hadn't given up the centralized development model. 

As an added bonus, it gave us an alternative view into the commit logs for our projects without the need for a local copy.

In order to proceed, I'm making the following assumptions:

* You are hosting an instance of Redmine on Heroku
* You are comfortable using [Git](http://git-scm.com)
* You've used a [Debian](http://debian.org)-based Linux distribution in the past
* You've used the [GNU Build System](http://en.wikipedia.org/wiki/GNU_build_system) before
* You have [Ruby](http://www.ruby-lang.org) and [RubyGems](http://rubygems.org) configured (if not, [RVM](http://rvm.io) is a good place to start)
* You are not crazy enough to try doing this from Windows or OSX ;) 
* You have a sense of humour and realize the winky above indicates this guide was written for Linux, but could easily be adapted for any OS

## Configuring the Build Environment

Heroku (as of November, 2012 at least) deploys applications to an Ubuntu 10.04 x86_64 environment, and we're going to be statically linking for that environment, so we need to setup a build system that reflects this requirement.

The most efficient way of doing this is to use [Vagrant](http://vagrantup.com) to initialize a bare-bones [Ubuntu Lucid](http://releases.ubuntu.com/lucid) system.

Since Rubygems should already be installed, it can be used to quickly setup Vagrant:

	gem install vagrant

Now, let's fetch a pre-build lucid system (thanks Vagrant!) and initialize it in the current directory:

	vagrant box add lucid64 http://files.vagrantup.com/lucid64.box
	vagrant init

This will create a `Vagrantfile` in the current director, which contains configuration information for our build system. In order to tell Vagrant to use the _lucid64_ instace we've downloaded, the `Vagrantfile` needs to be edited and the *config.vm.box* section updated.

``` ruby
# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant::Config.run do |config|  
  # ...
  # Every Vagrant virtual environment requires a box to build off of.
  config.vm.box = "lucid64"
  # ...
```

Now that everything is ready to go, let's start the instance.

	vagrant up

Once vagrant has started the virtual machine, we can access it via ssh using:	
	
	vagrant ssh

## Building Subversion

For the purposes of this tutorial, I'm going to be using the 1.6 branch of Subversion, which still had the _subversion-deps_ packaged separately. 

> **NOTE** With the 1.7 branch, there is a script that automates the process, and I'll likely update this tutorial at some point to use this.

First, we need to get the source:
	
	wget http://subversion.tigris.org/downloads/subversion-deps-1.6.19.tar.bz2
	wget http://subversion.tigris.org/downloads/subversion-1.6.19.tar.bz2
	tar xvf subversion-deps-1.6.19.tar.bz2
	tar xvf subversion-1.6.19.tar.bz2
	cd subversion-1.6.19
	
Second, we'll install any additional components required to compile successfully:

	sudo apt-get install build-essential libxml2-dev

Finally, we'll configure the build to exclude as much as possible and to produce a static binary:

	./configure --with-ssl \
	            --without-gssapi \
	            --without-swig \
	            --without-neon \
	            --enable-all-static
	make

Once the build completes, the only file we're interested in is the `svn` client, so we'll copy that to the `/vagrant` directory of our build machine, but first we'll strip it.

	strip subversion/svn/svn
	cp subversion/svn/svn /vagrant

> **NOTE** stripping the binary reduces the overall size from ~ 12 MB to ~ 4 MB, which is important since we have limited space on Heroku.
	vagrant@lucid64:~/subversion-1.6.19$ ls -l subversion/svn/svn
	-rwxr-xr-x 1 vagrant vagrant 12060462 2012-11-21 14:37 subversion/svn/svn*
>	
	vagrant@lucid64:~/subversion-1.6.19$ strip subversion/svn/svn   
>	
	vagrant@lucid64:~/subversion-1.6.19$ ls -l subversion/svn/svn
	-rwxr-xr-x 1 vagrant vagrant 4257472 2012-11-21 14:56 subversion/svn/svn*

The `/vagrant` directory is shared between the host and the guest machine by default, so this gives us access to the Subversion client if we open a new console and access the project folder we started Vagrant in.

Since we're now done, we can end the ssh session and stop the virtual machine	

	exit
	vagrant halt

## Adding Subversion to Redmine

Go to the root of your local Redmine repository, and create a `bin` folder. Now copy the `svn` binary to this folder, add the result to your repository and push to Heroku.

	mkdir bin
	cp /path/to/static/svn bin	
	git commit -a -m "Adding a Statically Linked Subversion to Redmine"
	git push heroku master

If all went well, when you access the *Repositories* tab under *Administration -> Settings*, Subversion should be listed and the version we just uploaded displayed.

{% img center /images/heroku-svn-01.jpg %}

## Accessing Changesets from GitHub

The final step is to configure an existing project to access a project on GitHub.

First, add a new repository and point it to the GitHub url you would normally use to access the project on the web.

> **NOTE** Leave the *Login* and *Password* fields blank unless this is a private repository

{% img center /images/heroku-svn-02.jpg %}

Once configured, clicking on the *Repository* tab should fetch the changesets and show the source tree

{% img center /images/heroku-svn-03.jpg %}

> **NOTE** This can potentially time out on a larger project and require clicking on the *Repository* tab multiple times until all changesets have been fetched and parsed.

> **NOTE** Viewing changeset diffs doesn't work

I've used my personal installation as an example at [http://alexbevi-pm.herokuapp.com/projects/redmine-dropbox-attachments](http://alexbevi-pm.herokuapp.com/projects/redmine-dropbox-attachments).

This method isn't on-par with a self-hosted solution, but it's good enough if you don't have a VPS in your budget ;)

### REFERENCES

* [http://rickvanderzwet.blogspot.ca/2007/11/building-static-subversion.html](http://rickvanderzwet.blogspot.ca/2007/11/building-static-subversion.html)
* [http://bindle.me/blog/index.php/405/running-binaries-on-heroku](http://bindle.me/blog/index.php/405/running-binaries-on-heroku)