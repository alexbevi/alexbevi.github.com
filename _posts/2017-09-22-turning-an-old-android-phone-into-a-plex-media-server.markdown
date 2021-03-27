---
layout: post
title: "Turning an old Android Phone into a Plex Media Server + PVR"
date: 2017-09-22 21:55:53 -0400
comments: true
categories: [android, linux, plex]
---

This is possibly a solution to a problem no one other than me has, but once in a while I like to challenge myself to see if something ridiculous is possible.

This time around I wanted to see if I could take my old [Moto X (2014)](http://www.gsmarena.com/motorola_moto_x_\(2nd_gen\)-6649.php) and use it as a [Plex Media Server](https://www.plex.tv/).

I didn't want to just see if I could install Plex though; I wanted to see if it would be possible to actually run a PMS instance along with [Sonarr](https://sonarr.tv/) to download content automatically for shows I'm interested in.

{% picture center /images/moto-plex/moto-plex-003.png %}

This introduced a couple of challenges, as Sonarr would need to be run using [Mono](http://www.mono-project.com/) (as it's a .NET project), I'd need a Bittorrent client to actually download the content, and I'd likely need to be running a [Jackett](https://github.com/Jackett/Jackett) service to allow Sonarr to process request through sites like The Pirate Bay.

Finally, as the Moto X is an ARM device, all of our software will need to be capable of running on an ARM platform.

Note that this process (with some minor changes) can be used to get a Plex + Sonarr + Jackett + Filebot + Transmission setup done on any Linux distribution. I just thought it would be fun to do it using a phone.

<!-- more -->

## Setup the Phone

This was the easiest part, as it simply required rooting the device so we could install [SuperSU](https://download.chainfire.eu/696/supersu/).

{% picture right /images/moto-plex/moto-plex-001.png %}

With a factory reset instance and root access, the next step was to install [BusyBox](https://play.google.com/store/apps/details?id=stericson.busybox&hl=en) and [Linux Deploy](https://play.google.com/store/apps/details?id=ru.meefik.linuxdeploy&hl=en).

Once both are installed from the Play Store, run Busy Box and select *Install*. You should only have to run this once, as it just installs a handful of Unix tools that Linux Deploy will need for the next step.

Linux Deploy will require a bit more configuration as you need to tweak it a bit to suit your needs.

First, select the repository you'd like. For my phone I went with **ubuntu-lxde_arm**, as this would setup an Ubuntu 16.04 LXDE distro along with VNC and SSH. Those will come into play when we want to start setting up Sonarr and Plex.

Under the properties for the repository (the settings icon in the lower right next to the *Stop* button) I set the *Installation type* to **Directory**. This setting allows use to have access to all available storage on our device. The first time I tried this I used the default of **File**, which only gave me 2GB of storage to play with. Once the base installation was done, there wasn't enough space left for me to do much. I tried tweaking the *Image Size (MB)* setting and starting over but it didn't make a difference. Your milage may vary, so feel free to try other configurations.

{% picture left /images/moto-plex/moto-plex-002.png %}

Next, from the top-right menu you need to *Install* the selected repository. This will do the basic installation of the Linux distribution you selected and pre-configure it for SSH and VNC access.

Once installed, click on the **Start** button to boot up the image. After a lot of terminal scrolling, you'll see something along the lines of `<<< start` on the last line and the text will stop. This is our signal to start setting up our software.

We've now got Linux running alongside Android on our phone. Let's SSH into it and continue. The credentials are available under the repository properties. You can change these prior to installation or just use the defaults that are generated.

## Setting Up Plex

There isn't an official ARM distribution of Plex, but thanks to some great work by [Jan Friedrich](https://github.com/uglymagoo/plexmediaserver-installer), we can easily patch the Plex NAS distribution for ARM or ARM64.

``` bash
sudo apt-get install -y fakeroot git
git clone https://github.com/uglymagoo/plexmediaserver-installer
cd plexmediaserver-installer
mkdir ../plex-installer; git archive master | tar -x -C ../plex-installer/
cd ..; fakeroot dpkg-deb --build plex-installer ./
```

This will create a Debian package that can be installed directly. For me, it produced `plexmediaserver-installer_1.9.1.4272-b207937f1-2_armhf.deb`, so installation was done using:

```
sudo dpkg -i plexmediaserver-installer_1.9.1.4272-b207937f1-2_armhf.deb
```

Then, to start up your Plex Media Server:

```
start_pms
```

You can verify it by going to http://phone-ip:32400/web/index.html.

I'm not going to set anything up here yet as we first need our media source available, which we'll be doing next.

## Setting Up Sonarr and Jackett

Sonarr can be installed from a repository list, so we'll just set that up on our phone. Sonarr will also require Mono to be installed, which luckily for us is also available from Ubuntu compiled for armhf.

```
sudo apt-get install -y libmono-cil-dev mono-devel libcurl4-openssl-dev
sudo apt-key adv --keyserver keyserver.ubuntu.com --recv-keys FDA5DFFC

sudo echo "deb http://apt.sonarr.tv/ master main" | sudo tee /etc/apt/sources.list.d/sonarr.list
sudo apt-get update
sudo apt-get install -y nzbdrone
```
{% picture center /images/moto-plex/moto-plex-004.png %}


Before we configure Sonarr, we'll setup Jackett. Jackett can be used to connect a torrent search site as a [Torznab feed](https://github.com/Sonarr/Sonarr/wiki/Supported-Indexers#torznab) to Sonarr.

For the purposes of this test I just setup The Pirate Bay, but Jackett supports a number of sites that may better suit your needs ;)

To start Jackett, we'll need to run it using Mono:

```
mono --debug ~/Jackett/JackettConsole.exe
```

Jackett will be available at http://phone-ip:9117. Once you've configured a search site in Jackett, you can start Sonarr and begin configuration.

```
mono --debug ~/Jackett/JackettConsole.exe
```

Sonarr will start up at http://phone-ip:8989. First we'll setup an *Indexer* (from *Settings -> Indexers*). This is where we'll plug in the details we configured in Jackett. You'll need exact url from Jackett, as well as the API key. This information is all easy to find from the Jackett interface.

Next, setup a TV show from the *Series* section. Once added we'll need to configure way to download content automatically when Sonarr detects a new episode. This is done under *Settings -> Download Client*.

Create a new [Transmission](https://transmissionbt.com/) client, give it a name and leave the default settings.

The only issue now though is that we don't have Transmission setup ...

## Setting Up Transmission and Filebot

Both of these are going to be a bit challenging, as [Filebot](https://www.filebot.net/) (which we'll be using to move and organize our downloads) needs [Java](https://www.java.com/en/), and Transmission requires a display server (can't be run from SSH).

First, let's install whatever we can from our existing SSH session:

```
sudo echo "deb http://ppa.launchpad.net/webupd8team/java/ubuntu precise main" | sudo tee -a /etc/apt/sources.list
sudo echo "deb-src http://ppa.launchpad.net/webupd8team/java/ubuntu precise main" | sudo tee -a /etc/apt/sources.list
sudo apt-key adv --keyserver keyserver.ubuntu.com --recv-keys EEA14886
sudo apt-get update
sudo apt-get install -y curl oracle-java8-installer transmission
curl -L -O https://downloads.sourceforge.net/project/filebot/filebot/FileBot_4.7.9/filebot_4.7.9_armhf.deb
sudo dpkg -i  filebot_4.7.9_armhf.deb
```

**NOTE:** if you get an error installing the key via `apt-key`, try the following:

```
sudo apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv-keys EEA14886
```

In order to use Filebot, we'll need a script we can call from Transmission. The script I'm working with is as follows:

```
#!/bin/bash
filebot -non-strict -script fn:amc --output /home/android/Media --log-file /home/android/amc.log --action move --conflict auto --def music=n --def subtitles=n --def artwork=y --def backdrops=n --def clean=y "seriesFormat= /home/android/Media/TV/{n}/{fn}" "ut_dir=$TR_TORRENT_DIR/$TR_TORRENT_NAME" "ut_kind=multi" "ut_title=$TR_TORRENT_NAME"
```

This script assumes that (a) your home directory is `/home/android`, and (b) you will be storing your media for Plex at `/home/android/Media/TV`. Feel free to modify the values to fit your particular installation.

Let's save this script as **transmission-postprocess** and make it executable using `chmod +x transmission-postprocess`.

Next, we'll need to actually VNC into our Linux distro. This is due to Transmission being a GTK application so we'll need to interact with it in a desktop environment.

{% picture center /images/moto-plex/moto-plex-005.png %}

From the desktop, launch Transmission and go to *Edit -> Preferences*. We want to do two things now:

- Setup Remote Access
- Under *Downloading* setup the script we created above to be called when a torrent completes

## Putting It All Together

{% picture center /images/moto-plex/moto-plex-006.png %}
<small>open in new tab to see full size</small>

Going back to our Plex Media Server url, we can now setup a library that points to our downloaded media directory.

When Sonarr detects a new episode, it will send the torrent link it finds from our TPB indexer to Transmission, and on completion Filebot will analyze the file and move it to the appropriate series/season folder for the show that was downloaded.

Enjoy!