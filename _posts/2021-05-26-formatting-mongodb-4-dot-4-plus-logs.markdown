---
layout: post
title: "Formatting MongoDB 4.4+ Logs"
date: 2021-05-26 08:21:00 -0400
comments: true
categories: MongoDB
tags: [mongodb]
---

MongoDB has always output log entries as plaintext.

![](/images/mdb-log-01.png)

Starting in MongoDB 4.4, `mongod` / `mongos` instances now output all log messages in [structured JSON format](https://docs.mongodb.com/manual/reference/log-messages/#std-label-log-message-json-output-format). This includes log output sent to the `file`, `syslog`, and `stdout` (standard out) log destinations, as well as the output of the [`getLog`](https://docs.mongodb.com/manual/reference/command/getLog/#mongodb-dbcommand-dbcmd.getLog) command.

![](/images/mdb-log-02.png)

The documentation includes [Log Parsing Examples](https://docs.mongodb.com/manual/reference/log-messages/#parsing-structured-log-messages) using the [`jq` command line utility](https://stedolan.github.io/jq/), but what if we want to [`tail`](https://en.wikipedia.org/wiki/Tail_(Unix)) the logs and produce a similar result as to what was present prior to the introduction of structured logging?

For the following example I've used the [`m` MongoDB Version Manager](https://github.com/aheckmann/m) to install [MongoDB 4.4.6](https://docs.mongodb.com/manual/release-notes/4.4/#4.4.6---may-10--2021):

```bash
m 4.4.6-ent
mkdir data
mongod --dbpath data --logpath data/mongodb.log --fork
```

Tailing the log now (`tail -n 30 data/mongodb.log`) will show the structured log output that is the default in MongoDB 4.4+, however using `jq` we can reformat (and colourize!!!) the output using one of the following:

```bash
# Windows
tail -f data\mongodb.log | jq-win64 --compact-output -r -C ".msg |= sub(\"\\n\";\"\") | .t.\"$date\"+\" \"+.c+\" [\"+.ctx+\"] \"+.msg, .attr | select(.!=null)
```
```bash
# Linux/OSX
tail -f data/mongodb.log | jq --compact-output -r -C '.msg |= sub("\n";"") | .t."$date"+" "+.c+" ["+.ctx+"] "+.msg, .attr | select(.!=null)'
```

![](/images/mdb-log-03.png)

This makes visually consuming the logs a lot easier! Some log messages, more commonly seen with increased [Logging Verbosity](https://docs.mongodb.com/manual/reference/log-messages/#verbosity-levels) may contain escape sequences (ex: `\n` and `\t`):

![](/images/mdb-log-04.png)

To render these escape sequences on screen while also tailing the logs in follow (`-f`) mode try the following:

```bash
# Linux/OSX
stdbuf -o0 tail -f mongod.log | stdbuf -o0 jq -r -C '.msg |= sub("\n";"") | .t."$date"+" "+.c+" ["+.ctx+"] "+.msg, .attr | select(.!=null)' | sed 's/\\n/\n/g; s/\\t/\t/g'
```

Note the [`stdbuf`](https://linux.die.net/man/1/stdbuf) and [`sed`](https://www.gnu.org/software/sed/manual/sed.html) commands can be installed on OSX via `brew install coreutils gnu-sed`.

![](/images/mdb-log-05.png)

I personally find this a lot easier when monitoring a node's logs while troubleshooting.

Let me know if you find this useful :)

