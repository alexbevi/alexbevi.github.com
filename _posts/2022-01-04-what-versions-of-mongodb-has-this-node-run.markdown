---
layout: post
title: "What Versions of MongoDB Has This Node Run?"
date: 2022-01-04 15:33:44 -0500
comments: true
categories: [MongoDB]
tags: [mongodb]
---

Ever wanted to know how many different versions of MongoDB the current node has run under? Assuming the node's [`local` database](https://docs.mongodb.com/manual/reference/local-database) hasn't been reset (for example via an [initial sync](https://docs.mongodb.com/manual/core/replica-set-sync/#std-label-replica-set-initial-sync)), it will contain a [`startup_log`](https://docs.mongodb.com/manual/reference/local-database/#mongodb-data-local.startup_log) collection. On startup, each `mongod` instance inserts a document into the `startup_log` [capped collection](https://docs.mongodb.com/manual/core/capped-collections/) (capped at 10MB) with diagnostic information about the `mongod` instance itself and host information.

This collection can be used to generate a report using this diagnostic information using the following script run from a `mongo` or `mongosh` shell connected to your cluster:

```js
var lastVersion = null;
print("Process Last Started\tMongoDB Version\tCommand Line Options");
db.getSiblingDB("local").startup_log.find({}).sort({ startTime: -1 }).forEach(function(d) {
  if (d.buildinfo.version != lastVersion) {
    lastVersion = d.buildinfo.version;
    print([d.startTime.toUTCString(), lastVersion, JSON.stringify(d.cmdLine)].join('\t'));
  }
});
```

The output above will return tab-delimited results, however these could be easily updated to produce a CSV or Markdown table similar to the following:

|Process Last Started|MongoDB Version|Command Line Options|
|--------------------|---------------|--------------------|
|Fri, 10 Dec 2021 19:18:30 GMT|4.4.10|{ "config": ... }|
|Thu, 14 Oct 2021 18:08:53 GMT|4.4.9|{ "config": ... }|
|Wed, 08 Sep 2021 18:22:50 GMT|4.4.8|{ "config": ... }|
|Sat, 10 Jul 2021 13:33:24 GMT|4.4.6|{ "config": ... }|
|Thu, 06 May 2021 18:12:19 GMT|4.4.5|{ "config": ... }|
|Sat, 27 Mar 2021 18:10:53 GMT|4.4.4|{ "config": ... }|
|Thu, 18 Mar 2021 18:47:19 GMT|4.2.12|{ "config": ... }|
|Thu, 21 Jan 2021 20:47:22 GMT|4.2.11|{ "config": ... }|
|Sat, 21 Nov 2020 15:41:39 GMT|4.2.10|{ "config": ... }|
|Wed, 16 Sep 2020 09:58:36 GMT|4.2.9|{ "config": ... }|
|Sun, 16 Aug 2020 10:52:48 GMT|4.2.8|{ "config": ... }|
|Sat, 30 May 2020 18:13:48 GMT|4.2.6|{ "config": ... }|
|Thu, 28 May 2020 18:23:28 GMT|4.2.7|{ "config": ... }|
|Thu, 21 May 2020 18:15:00 GMT|4.2.6|{ "config": ... }|
|Thu, 02 Apr 2020 18:27:14 GMT|4.2.5|{ "config": ... }|
|Thu, 02 Apr 2020 11:50:29 GMT|4.2.3|{ "config": ... }|
|Thu, 02 Apr 2020 11:47:16 GMT|4.0.16|{ "config": ... }|
|Wed, 01 Apr 2020 19:26:17 GMT|3.6.17|{ "config": ... }|
|Mon, 06 Jan 2020 19:19:03 GMT|3.6.16|{ "config": ... }|
|Tue, 26 Nov 2019 19:01:22 GMT|3.6.15|{ "config": ... }|
|Fri, 08 Nov 2019 19:30:40 GMT|3.6.14|{ "config": ... }|
|Fri, 26 Jul 2019 19:12:13 GMT|3.6.13|{ "config": ... }|
|Tue, 04 Jun 2019 19:19:59 GMT|3.6.12|{ "config": ... }|
|Thu, 28 Mar 2019 19:21:07 GMT|3.6.11|{ "config": ... }|

I ran this against one of my development [MongoDB Atlas](https://www.mongodb.com/atlas) clusters to show how version information persists regardless of the order of upgrade or major/minor version used.

ß