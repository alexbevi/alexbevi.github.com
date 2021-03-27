---
layout: post
title: "MongoDB 5.0 Initial Sync Progress Monitoring Improvements"
date: 2020-11-20 10:31:26 -0500
comments: true
categories: [mongodb]
---

`<SHAMELESS_PLUG>`
<br>
My [previous article about initial sync progress monitoring]({% post_url 2020-02-13-mongodb-initial-sync-progress-monitoring %}) got some attention, and as I'm a [Technical Services Engineer]({% post_url 2018-10-01-technical-services-engineering-at-mongodb %}) at MongoDB, I got to provide direct feedback during the design phase of [SERVER-47863: _Initial Sync Progress Metrics_](https://jira.mongodb.org/browse/SERVER-47863)!.

You can be a part of this team and this awesome organization too! Head on over to [MongoDB's careers page](https://grnh.se/dcd90aac1) to see what's available, or feel free to ping me on [LinkedIn](https://www.linkedin.com/in/alexbevi/) if you have any questions.
<br>
`</SHAMELESS_PLUG>`

The goal of this post is to showcase a change that is coming in MongoDB 5.0 that will significantly improve the feedback loop regarding [initial sync](https://docs.mongodb.com/manual/core/replica-set-sync/#initial-sync) progress monitoring. With [SERVER-47863](https://jira.mongodb.org/browse/SERVER-47863) being completed, the results of the [`db.adminCommand({ replSetGetStatus: 1, initialSync: 1 })`](https://docs.mongodb.com/manual/reference/command/replSetGetStatus/) now include additional metrics that can be used to help determine how long (approximately) an initial sync will be running for.

**Though this feature is planned to be backported to versions 4.4.3 and 4.2.12, at the time of writing backports had not been completed.**

If you want to test this yourself, my setup was as follows:

1) [Build the server using the `install-mongod` SCons target](https://github.com/mongodb/mongo/blob/master/docs/building.md#scons-targets). My version of the server was `mongod-4.9.0-alpha-596-g4437864` as a result.
<br>
2) Start up a single node replicaset as follows:
```bash
mkdir data && build/install/bin/mongod --dbpath data --bind_ip_all --replSet rs0 --logpath data/mongod.log
```

3) Using the `mongo` shell, initialize the replica set:
```bash
mongo --eval 'rs.initiate()'
```

4) Seed the `test.data` namespace using the following [`mgeneratejs`](https://github.com/rueckstiess/mgeneratejs) and [`mongoimport`](https://docs.mongodb.com/database-tools/mongoimport/):
```bash
curl -s https://gist.githubusercontent.com/alexbevi/955c6675337107e16d637233f865b1e3/raw/0c48178e9c570b7594f207559744f07ecf87ac28/template.json | mgeneratejs -n 1000000 | mongoimport --collection data --numInsertionWorkers 4
```

5) Start another `mongod` and add it to the replica set
```bash
mkdir data2 && build/install/bin/mongod --port 27018 --dbpath data2 --bind_ip_all --replSet rs0 --logpath data2/mongod.log
mongo --eval 'rs.add("localhost:27018")'
```

The above steps will build the `mongod` and start up 2 nodes in a replica set with one in a [`STARTUP2`](https://docs.mongodb.com/manual/reference/replica-states/#replstate.STARTUP2) (initial sync) state.

By connecting to the secondary node directly and issuing a [`replSetGetStatus`](https://docs.mongodb.com/manual/reference/command/replSetGetStatus/) command we can now review the progress of the copy. Note that this will need to be done _while_ the initial sync is in progress; once the node exits the `STARTUP2` state and enters a `SECONDARY` state, the `initialSyncStatus` details will be unavailable.

For example:

```
db.adminCommand({ replSetGetStatus: 1, initialSync: 1 });
```
```js
{
	"set" : "rs0",
	...
	"initialSyncStatus" : {
		"failedInitialSyncAttempts" : 0,
		"maxFailedInitialSyncAttempts" : 10,
		"initialSyncStart" : ISODate("2020-11-20T15:47:09.136Z"),
		"totalInitialSyncElapsedMillis" : 14925,               <-----------
		"initialSyncAttempts" : [ ],
		"approxTotalDataSize" : 311911892,                     <-----------
		"approxTotalBytesCopied" : 16811036,                   <-----------
		"remainingInitialSyncEstimatedMillis" : 0,             <-----------
		"appliedOps" : 0,
		"initialSyncOplogStart" : Timestamp(1605887228, 1),
		"totalTimeUnreachableMillis" : NumberLong(0),
		"databases" : {
			"databasesToClone" : 1,                              <-----------
			"databasesCloned" : 2,
			...
			},
			"test" : {
				"collections" : 1,
				"clonedCollections" : 0,
				"start" : ISODate("2020-11-20T15:47:13.968Z"),
				"test.data" : {
					"documentsToCopy" : 250000,
					"documentsCopied" : 13481,
					"indexes" : 1,
					"fetchedBatches" : 2,
					"bytesToCopy" : 311911663,                       <-----------
					"approxBytesCopied" : 16810807,                  <-----------
					"start" : ISODate("2020-11-20T15:47:13.968Z"),
					"receivedBatches" : 2
				}
			}
		}
	},
	...
}
```

The command output has been truncated to focus in on the new fields added to the `initialSyncStatus` document. The new metrics details are as follows:

<!-- MORE -->

`totalInitialSyncElapsedMillis`
> Current Time - Start Time

`remainingInitialSyncEstimatedMillis`
> (`totalInitialSyncElapsedMillis` / `approxTotalBytesCopied`) * (`approxTotalDataSize` - `approxTotalBytesCopied`)
>
> If (`approxBytesCopied` == 0), this field will not be shown

I've opened [SERVER-53017](https://jira.mongodb.org/browse/SERVER-53017) to review this particular entry as the value did not appear to be properly updated throughout the initial sync process. As MongoDB 5.0 is not expected to be GA until mid 2021, this will likely be addressed before then.

**Update 2021-01-26**: [SERVER-53017](https://jira.mongodb.org/browse/SERVER-53017) has been fixed.

`<collection>.bytesToCopy`
> = [`collStats.size`](https://docs.mongodb.com/manual/reference/command/collStats/#collStats.size)

`<collection>.approxBytesCopied`
> = [`collStats.avgObjSize`](https://docs.mongodb.com/manual/reference/command/collStats/#collStats.avgObjSize) * `documentsCopied`

`databasesToClone`
> = length of [`listDatabases`](https://docs.mongodb.com/manual/reference/command/listDatabases/index.html#output) response

`approxTotalDataSize`
> = Sum ([`dbStats.dataSize`](https://docs.mongodb.com/manual/reference/command/dbStats/index.html#dbStats.dataSize) for all databases)

`approxTotalBytesCopied`
> = Sum (`<collection>.approxBytesCopied` for all collections)

What can we do with all this useful information you ask? Well I've written the following script that can be used to poll a secondary replica set member in STARTUP2 to provide details regarding the progress of the initial sync. This script will also provide estimated throughput and a calculated ETA based on data transfer rates.

The output will appear similar to:

```bash
# start monitoring the initial sync (default refresh interval is 5 seconds)
mongo --host $SECONDARY_HOST --port $SECONDARY_PORT --quiet --eval "load('measureInitialSyncProgress.js'); measureInitialSyncProgress();"
# to use a custom refresh interval, the value is in milliseconds, so for a 1 second refresh
# pass 1000 to measureInitialSyncProgress as follows:
# mongo --host $SECONDARY_HOST --port $SECONDARY_PORT --quiet --eval "load('measureInitialSyncProgress.js'); measureInitialSyncProgress(1000);"
```

```
Initial Sync running for 00:18:05.2 (remainingInitialSyncEstimatedMillis 0). Cloned 1.1 GB of 1.2 GB (15.9 MB in past 5 second(s)) at a rate of 3.2 MB/second - 00:00:54.2 to go!
Initial Sync running for 00:18:10.8 (remainingInitialSyncEstimatedMillis 0). Cloned 1.1 GB of 1.2 GB (No progress in past 5 second(s))
Initial Sync running for 00:18:17.9 (remainingInitialSyncEstimatedMillis 0). Cloned 1.1 GB of 1.2 GB (No progress in past 5 second(s))
Initial Sync running for 00:18:22.9 (remainingInitialSyncEstimatedMillis 0). Cloned 1.1 GB of 1.2 GB (No progress in past 5 second(s))
Initial Sync running for 00:18:27.9 (remainingInitialSyncEstimatedMillis 0). Cloned 1.1 GB of 1.2 GB (No progress in past 5 second(s))
Initial Sync running for 00:18:33.1 (remainingInitialSyncEstimatedMillis 0). Cloned 1.1 GB of 1.2 GB (No progress in past 5 second(s))
Initial Sync running for 00:18:38.4 (remainingInitialSyncEstimatedMillis 0). Cloned 1.1 GB of 1.2 GB (15.9 MB in past 5 second(s)) at a rate of 3.2 MB/second - 00:00:49.1 to go!
Initial Sync running for 00:18:43.5 (remainingInitialSyncEstimatedMillis 0). Cloned 1.1 GB of 1.2 GB (No progress in past 5 second(s))
Initial Sync running for 00:18:48.5 (remainingInitialSyncEstimatedMillis 0). Cloned 1.1 GB of 1.2 GB (No progress in past 5 second(s))
Initial Sync running for 00:18:53.9 (remainingInitialSyncEstimatedMillis 0). Cloned 1.1 GB of 1.2 GB (No progress in past 5 second(s))
Initial Sync running for 00:18:59.5 (remainingInitialSyncEstimatedMillis 0). Cloned 1.1 GB of 1.2 GB (15.9 MB in past 5 second(s)) at a rate of 3.2 MB/second - 00:00:44.2 to go!
Initial Sync running for 00:19:05.3 (remainingInitialSyncEstimatedMillis 0). Cloned 1.1 GB of 1.2 GB (15.9 MB in past 5 second(s)) at a rate of 3.2 MB/second - 00:00:39.2 to go!
Initial Sync running for 00:19:11.0 (remainingInitialSyncEstimatedMillis 0). Cloned 1.1 GB of 1.2 GB (15.9 MB in past 5 second(s)) at a rate of 3.2 MB/second - 00:00:34.2 to go!
Initial Sync running for 00:19:16.6 (remainingInitialSyncEstimatedMillis 0). Cloned 1.2 GB of 1.2 GB (15.9 MB in past 5 second(s)) at a rate of 3.2 MB/second - 00:00:29.2 to go!
Initial Sync running for 00:19:22.3 (remainingInitialSyncEstimatedMillis 0). Cloned 1.2 GB of 1.2 GB (No progress in past 5 second(s))
Initial Sync running for 00:19:28.4 (remainingInitialSyncEstimatedMillis 0). Cloned 1.2 GB of 1.2 GB (15.9 MB in past 5 second(s)) at a rate of 3.2 MB/second - 00:00:24.2 to go!
Initial Sync running for 00:19:34.5 (remainingInitialSyncEstimatedMillis 0). Cloned 1.2 GB of 1.2 GB (15.9 MB in past 5 second(s)) at a rate of 3.2 MB/second - 00:00:19.2 to go!
Initial Sync running for 00:19:39.6 (remainingInitialSyncEstimatedMillis 0). Cloned 1.2 GB of 1.2 GB (15.9 MB in past 5 second(s)) at a rate of 3.2 MB/second - 00:00:14.2 to go!
Initial Sync running for 00:19:45.3 (remainingInitialSyncEstimatedMillis 0). Cloned 1.2 GB of 1.2 GB (No progress in past 5 second(s))
Initial Sync running for 00:19:54.6 (remainingInitialSyncEstimatedMillis 0). Cloned 1.2 GB of 1.2 GB (15.9 MB in past 5 second(s)) at a rate of 3.2 MB/second - 00:00:09.2 to go!
Initial Sync running for 00:20:01.9 (remainingInitialSyncEstimatedMillis 0). Cloned 1.2 GB of 1.2 GB (No progress in past 5 second(s))
Initial Sync running for 00:20:10.1 (remainingInitialSyncEstimatedMillis 0). Cloned 1.2 GB of 1.2 GB (15.9 MB in past 5 second(s)) at a rate of 3.2 MB/second - 00:00:04.2 to go!
Initial Sync running for 00:20:15.7 (remainingInitialSyncEstimatedMillis 0). Cloned 1.2 GB of 1.2 GB (No progress in past 5 second(s))
Initial Sync running for 00:20:20.7 (remainingInitialSyncEstimatedMillis 0). Cloned 1.2 GB of 1.2 GB (11.6 MB in past 5 second(s)) at a rate of 2.3 MB/second - 00:00:00.7 to go!
Node not currently performing an initial sync
```

~~Once [SERVER-53017](https://jira.mongodb.org/browse/SERVER-53017) has been addressed I will update this script so that the `remainingInitialSyncEstimatedMillis` values can be used consistently.~~

**Update 2021-01-26**: [SERVER-53017](https://jira.mongodb.org/browse/SERVER-53017) was addressed and the script has been modified to use the `remainingInitialSyncEstimatedMillis` value directly!

{% gist alexbevi/fc4f59621aee4efbae2c04187dcbf2c6 %}
