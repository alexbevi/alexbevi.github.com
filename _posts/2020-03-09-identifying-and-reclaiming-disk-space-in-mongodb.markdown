---
layout: post
title: "Identifying and Reclaiming Disk Space in MongoDB"
date: 2020-03-15 16:23:38 -0400
comments: true
categories: [MongoDB]
tags: [mongodb, wiredtiger, scripting]
image: /images/mongodb-logo.png
---

> **December 17, 2024**: Starting in MongoDB 8.0, you can use the new [`autoCompact`](https://www.mongodb.com/docs/manual/reference/command/autoCompact/) command to perform background compaction. If enabled, the server attempts to keep free space within each collection and index below the specified the `freeSpaceTargetMB` value.
{: .prompt-info }

A common question when it comes to MongoDB and the (default) storage engine ([WiredTiger](https://docs.mongodb.com/manual/core/wiredtiger/)) is "Why is it after I removed a bunch of documents my free space didn't increase"?

The WiredTiger storage engine maintains lists of empty records in data files as it deletes documents. This space can be reused by WiredTiger, but will not be returned to the operating system unless under very specific circumstances.

The amount of empty space available for reuse by WiredTiger is reflected in the output of [`db.collection.stats()`](https://docs.mongodb.com/manual/reference/method/db.collection.stats/#db.collection.stats) under the heading `wiredTiger.block-manager.file bytes available for reuse`.

To allow the WiredTiger storage engine to release this empty space to the operating system, you can de-fragment your data file. This can be achieved using the [`compact` command](https://docs.mongodb.com/manual/reference/command/compact/#dbcmd.compact).

As the `db.collection.stats()` command must be run one [collection](https://docs.mongodb.com/manual/reference/glossary/#term-collection) at a time I've written the following script to enhance this functionality as follows:

* scan all [namespaces](https://docs.mongodb.com/manual/reference/glossary/#term-namespace) ([databases](https://docs.mongodb.com/manual/reference/glossary/#term-database) + collections)
* include index space details
* support for sharded collections
* output to CSV

<!-- MORE -->

{% gist alexbevi/d89d8ce406e7fcea9f0915b7a7580c28 %}

Running this script from a `mongo` shell will produce output similar to the following:

```
---------------------
admin
---------------------
Namespace,Uncompressed,Compressed,Reusable from Collections,Indexes,Reusable from Indexes
admin.system.keys (config),255 Bytes,36 KB,16 KB,36 KB,16 KB
admin.system.version (config),59 Bytes,20 KB,0 Byte,20 KB,0 Byte
Total,314 Bytes,56 KB,16 KB,56 KB,16 KB
---------------------
config
---------------------
Namespace,Uncompressed,Compressed,Reusable from Collections,Indexes,Reusable from Indexes
config.actionlog (config),32 KB,40 KB,16 KB,40 KB,16 KB
config.changelog (config),346 KB,132 KB,52 KB,96 KB,44 KB
config.chunks (config),57 KB,52 KB,24 KB,144 KB,64 KB
config.collections (config),431 Bytes,36 KB,16 KB,36 KB,16 KB
config.databases (config),108 Bytes,20 KB,0 Byte,20 KB,0 Byte
config.lockpings (config),3 KB,36 KB,16 KB,72 KB,32 KB
config.locks (config),771 Bytes,36 KB,16 KB,108 KB,48 KB
config.migrations (config),0 Byte,24 KB,16 KB,48 KB,32 KB
config.mongos (config),342 Bytes,36 KB,16 KB,20 KB,0 Byte
config.settings (config),39 Bytes,20 KB,0 Byte,20 KB,0 Byte
config.shards (config),297 Bytes,20 KB,0 Byte,44 KB,4 KB
config.system.sessions (shard01),99 Bytes,36 KB,16 KB,60 KB,20 KB
config.tags (config),0 Byte,4 KB,0 Byte,24 KB,4 KB
config.transactions (config),0 Byte,24 KB,16 KB,12 KB,4 KB
config.version (config),83 Bytes,20 KB,0 Byte,20 KB,0 Byte
Total,441 KB,536 KB,204 KB,764 KB,284 KB
---------------------
test
---------------------
Namespace,Uncompressed,Compressed,Reusable from Collections,Indexes,Reusable from Indexes
test.test1 (shard01),37 MB,37 MB,27 MB,26 MB,16 MB
test.test1 (shard02),37 MB,8 MB,52 KB,5 MB,2 MB
test.test1 (shard03),38 MB,8 MB,56 KB,5 MB,2 MB
test.ups_test (shard01),0 Byte,24 KB,16 KB,72 KB,48 KB
Total,112 MB,54 MB,27 MB,36 MB,19 MB
```

This output can then being imported into your favourite spreadsheet for further manipulation.

Based on this sample output, the `test.test1` collection on `shard01` could reclaim approximately 27MB if `compact`ed. Note that the amount of space reclaimed will not necessarily be exactly what is reported here, but is generally a good guideline as to how much space may be reclaimed.
