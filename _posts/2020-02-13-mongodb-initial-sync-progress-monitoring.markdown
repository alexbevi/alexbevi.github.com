---
layout: post
title: "MongoDB Initial Sync Progress Monitoring"
date: 2020-02-13 12:34:49 -0500
comments: true
categories: [MongoDB]
tags: [mongodb, replication, scripting]
---

Sometimes our replica set members fall off the [oplog](https://docs.mongodb.com/manual/core/replica-set-oplog/) and the node needs to be resynced. When this happens, an [Initial Sync](https://docs.mongodb.com/manual/core/replica-set-sync/#initial-sync) is required, which does the following:

1. Clones all databases except the local database. To clone, the `mongod` scans every collection in each source database and inserts all data into its own copies of these collections.
2. Applies all changes to the data set. Using the oplog from the source, the `mongod` updates its data set to reflect the current state of the replica set.

When the initial sync finishes, the member transitions from [`STARTUP2`](https://docs.mongodb.com/manual/reference/replica-states/#replstate.STARTUP2) to [`SECONDARY`](https://docs.mongodb.com/manual/reference/replica-states/#replstate.SECONDARY).

Some common questions when performing an initial sync of a [Replica Set Member](https://docs.mongodb.com/manual/core/replica-set-members/) are:

- How do I know if the sync is progressing?
- How long will this take to complete?

<!-- MORE -->

Determining if the sync is progressing can be done by either checking the size of the [`dbPath`](https://docs.mongodb.com/manual/reference/configuration-options/#storage.dbPath) of the syncing node or by running the [`db.adminCommand({ replSetGetStatus: 1, initialSync: 1 })`](https://docs.mongodb.com/manual/reference/command/replSetGetStatus/) command while connected to the SECONDARY via the mongo shell.

{% picture /images/initsync-001.png %}

Checking the directory size of the SECONDARY that is being initial sync'ed will provide a good approximation as to how much data still remains to be copied. Note that as the WiredTiger storage engine doesn't "release" space when documents are deleted there is a high probability that the SECONDARY will have a _smaller total directory size_ than the sync source.

The second step (after cloning) where the oplog entries are applied will also affect the overall time required to sync from the sync source.

The `replSetGetStatus` command will produce a JSON document similar to the following. This document contains extensive details as to how the database/collection cloning is progressing, as well as any errors that have occurred during the process.

{% gist alexbevi/d52ffd2e27068dcdcc616a5aaf814907 %}

Depending on the number of databases and collections being sync'ed, the size of this document can be quite large and difficult to visually parse.

To improve this situation I've created the following script.

{% gist alexbevi/422890f191f4bcb82c06fbb621c69331 %}

By running this against the SECONDARY from the mongo shell, a more concise representation of the `initialSyncStatus` document is produced:

{% picture /images/initsync-002.png %}

The script will also let you know if there have been any sync failures recorded, as well as what the last failure was.

{% picture /images/initsync-003.png %}

Hopefully you'll find this useful when the time comes to resync one of your nodes.