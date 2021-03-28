---
layout: post
title: "Fixing Broken Sudo"
date: 2012-10-30 14:58
comments: true
categories: [Linux]
tags: [linux, ubuntu]
---

This is pretty much a transcription of [http://www.psychocats.net/ubuntu/fixsudo](http://www.psychocats.net/ubuntu/fixsudo), which is just such a good article I wanted to keep a copy for reference.

## How does _sudo_ work?

The way that Ubuntu has implemented _sudo_, the `/etc/sudoers` file says that users in the admin group can (after a password authentication) temporarily escalate to system-wide privileges for particular tasks. And then the `/etc/groups` file says which users are in the admin group.

You can read more on [the community documentation](https://help.ubuntu.com/community/RootSudo) about Ubuntu's implementation of _sudo_.

<!-- more -->

## Cause and Symptoms

_sudo_ breaks when one or more of the following occurs:

* the `/etc/sudoers` file has been altered to no longer allow users in the admin group to escalate privilege
* the permissions on the `/etc/sudoers` file are changed to something other than 0440
* a user who should not have been has been taken out of the _admin_ group

![](/images/fixsudoprecise01.jpg)

If _sudo_ is broken this way, you may notice an error saying you're not in the _sudo_ers file and the incident is going to be reported. Or you may just see the next command prompt without any action being executed.


## Booting into recovery mode

Since fixing _sudo_ involves editing system files, and you would otherwise need _sudo_ to do so, you'll have to boot into recovery mode to gain root (system-wide) access in order to repair _sudo_.

If you have a single-boot (Ubuntu is the only operating system on your computer), to get the boot menu to show, you have to hold down the Shift key during bootup.

If you have a dual-boot (Ubuntu is installed next to Windows, another Linux operating system, or Mac OS X; and you choose at boot time which operating system to boot into), the boot menu should appear without the need to hold down the _Shift_ key.

![](/images/fixsudoprecise02.jpg)

From the boot menu, select _recovery mode_, which is usually the second boot option.

![](/images/fixsudoprecise03.jpg)

After you select recovery mode and wait for all the boot-up processes to finish, you'll be presented with a few options. In this case, you want the *Drop to root shell* prompt option so press the Down arrow to get to that option, and then press Enter to select it.

The root account is the ultimate administrator and can do anything to the Ubuntu installation (including erase it), so please be careful with what commands you enter in the root terminal.

In recent versions of Ubuntu, the filesystem is mounted as read-only, so you need to enter the follow command to get it to remount as read-write, which will allow you to make changes:

    mount -o rw,remount /

## Do the actual repair

### Case 1

If you'd removed your last _admin_ user from the _admin_ group, then type

    adduser username admin

where _username_ is your actual username.

### Case 2

If you had previously edited the /etc/_sudo_ers file and screwed it up, then type

    sudo cp /etc/sudoers /etc/sudoers.backup
    sudo nano /etc/sudoers

(the proper command is actually `sudo visudo`, which checks syntax before you save the `/etc/sudoers` file, but in some older versions of Ubuntu, that command uses the vi editor, which can be confusing to new users, as opposed to nano, which is more straightforward)
and make it sure it looks like this:

    #
    # This file MUST be edited with the 'visudo' command as root.
    #
    # Please consider adding local content in /etc/sudoers.d/ instead of
    # directly modifying this file.
    #
    # See the man page for details on how to write a sudoers file.
    #
    Defaults  env_reset
    Defaults  secure_path="/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
    # Host alias specification

    # User alias specification

    # Cmnd alias specification

    # User privilege specification
    root  ALL=(ALL:ALL) ALL

    # Members of the admin group may gain root privileges
    %admin ALL=(ALL) ALL

    # Allow members of group sudo to execute any command
    %sudo ALL=(ALL:ALL) ALL

    # See sudoers(5) for more information on "#include" directives:

    #includedir /etc/sudoers.d

When you're done making changes, press _Control-X, Y, Enter_.

### Case 3

If you are trying to fix the error where it says _sudo_ is mode _____, should be 0440, then you'll want to type

    chmod 0440 /etc/sudoers

When you're done with whatever commands you needed to enter, type

    exit

This will bring you back to the recovery menu.

![](/images/fixsudoprecise04.jpg)
![](/images/fixsudoprecise05.jpg)

Choose to resume a normal boot. Then you should be able to _sudo_ again.