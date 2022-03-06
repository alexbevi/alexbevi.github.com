---
layout: post
title: "Performance Analysis of Resuming a MongoDB Change Stream"
date: 2022-03-02 06:50:39 -0500
comments: true
categories: [MongoDB]
tags: [mongodb, changestream, performance]
image:
  src: /images/mongodb-logo.png
  alt: MongoDB Logo
---

[Change Streams](https://docs.mongodb.com/manual/changeStreams/) allow applications to access real-time data changes without the complexity and risk of tailing the [oplog](https://docs.mongodb.com/manual/reference/glossary/#std-term-oplog). Applications can use change streams to subscribe to all data changes on a single collection, a database, or an entire deployment, and immediately react to them.

For applications that rely on change streams, ensuring continuity on process restart can be accomplished by specifying a [resume token to resume the change stream](https://docs.mongodb.com/manual/changeStreams/#resume-a-change-stream). Depending on how many events have been recorded in the oplog after the resume token, the time taken to resume the stream can take longer than expected.

This article will attempt to explain the default behavior of change streams when resumed and how performance can potentially improved. Note that all scripts used in this article are shared in the _Reproduction_ section at the end.

## Capturing Our First Change Event

The `nodejs-capture-first-event.js` script uses the [MongoDB Node Driver](https://docs.mongodb.com/drivers/node/current/) to connect to the cluster we just created and listen for changes. First ensure you have Node.js installed, then using `npm` install the [`mongo` package](https://www.npmjs.com/package/mongodb) and run the script:

```bash
npm install mongo
node capture-first-event.js
```

Once the script is watching the collection connect to the cluster and run the `setupEnvironment()` function to setup the cluster and insert a test document:

```bash
mongo --quiet --eval "load('shell-configure-test.js'); setupEnvironment();"
```

Once this document is inserted, the Node.js should produce a result similar to the following, then exit:

```js
// output
2022-02-15T12:13:26.173Z Change received:  {
  _id: {
    _data: '82620B98E5000000022B022C0100296E5A1004437FB549CFDD45269DD59B9BF0EB354746645F69640064620B98E564DA118651C642000004'
  },
  operationType: 'insert',
  clusterTime: new Timestamp({ t: 1644927205, i: 2 }),
  fullDocument: {
    _id: new ObjectId("620b98e564da118651c64200"),
    msg: 'We expect our filter to match this'
  },
  ns: { db: 'test', coll: 'foo' },
  documentKey: { _id: new ObjectId("620b98e564da118651c64200") }
}
```

Note the `_id` value of the [change event](https://docs.mongodb.com/manual/reference/change-events/) as this will be used to resume the change stream later.

## Seeding the Collection

The `nodejs-capture-first-event.js` script should have terminated after the change event was detected and printed. Next we want to fill the collection with content prior to attempting to resume processing, which can be done using our setup script from a `mongo`/`mongosh` shell:

```bash
mongo --quiet --eval "load('shell-configure-test.js'); seedCollection();"
```

The function above will push 3000 "junk" documents (~ 6MB in size) to the collection along with a few additional documents mixed in that should match our initial change stream filter. Once the collection is seeded, we can use the [`$collStats`](https://docs.mongodb.com/manual/reference/operator/aggregation/collStats/) aggregation stage to get an idea as to how much data we've just generated. This should be run from a `mongo`/`mongosh` shell connected to the cluster:

```bash
$ mongosh --quiet --eval "db.foo.aggregate([ { $collStats: { storageStats: {} }}, { $project: { 'storageStats.wiredTiger': 0, 'storageStats.indexDetails': 0 } }]).pretty();"

[
  {
    ns: 'test.foo',
    host: 'Alexs-MacBook-Pro.local:27018',
    localTime: ISODate("2022-02-15T21:36:13.752Z"),
    storageStats: {
      size: Long("16993324327"), // 16.99GB
      count: 2711,
      avgObjSize: 6268286, // 6.26MB
      storageSize: Long("17022169088"),
      freeStorageSize: 17760256,
      capped: false,
      nindexes: 1,
      indexBuilds: [],
      totalIndexSize: 114688,
      totalSize: Long("17022283776"),
      indexSizes: { _id_: 114688 },
      scaleFactor: 1
    }
  }
]
```

## Resuming a Change Stream with a `ResumeToken`

Change streams can be resumed by using a [`ResumeToken`](https://docs.mongodb.com/manual/changeStreams/#resume-tokens). To [`resumeAfter`](https://docs.mongodb.com/manual/changeStreams/#resumeafter-for-change-streams) you use the `_id` value of the last change stream event as this acts as the `resumeToken`. This can be inspected via the `mongosh` shell using the `resumetoken` snippet (see [`mongodb-js/mongodb-resumetoken-decoder`](https://github.com/mongodb-js/mongodb-resumetoken-decoder))

```js
Enterprise replset [direct: primary] test> decodeResumeToken('82620B98E5000000022B022C0100296E5A1004437FB549CFDD45269DD59B9BF0EB354746645F69640064620B98E564DA118651C642000004')
{
  timestamp: new Timestamp({ t: 1644927205, i: 2 }),
  version: 1,
  tokenType: 128,
  txnOpIndex: 0,
  fromInvalidate: false,
  uuid: new UUID("437fb549-cfdd-4526-9dd5-9b9bf0eb3547"),
  documentKey: { _id: new ObjectId("620b98e564da118651c64200") }
}
```

To use the resume token, the `nodejs-resume-changestream.js` script can be adjusted to use our token we found earlier.

## Performance Using Cursor Defaults

When the above script is run, the output should be similar to the following:

```bash
$ node capture-first-event.js

2022-03-02T11:38:37.014Z Resuming Change Stream ...
2022-03-02T11:38:49.888Z Change received: "This document will be 1Kb" (token: 82621F54B3000000012B022C0100296E5A1004D9EC8991B42F4F71BA61FC5BA26E2DED46645F69640064621F54B33284546A99670EFD0004)
2022-03-02T11:38:49.888Z Change received: "100 6MB documents, then another 1Kb document" (token: 82621F54C4000000062B022C0100296E5A1004D9EC8991B42F4F71BA61FC5BA26E2DED46645F69640064621F54C43284546A99670F620004)
2022-03-02T11:38:49.889Z Change received: "And another 100 6MB documents, then another 1Kb document" (token: 82621F54D4000000072B022C0100296E5A1004D9EC8991B42F4F71BA61FC5BA26E2DED46645F69640064621F54D43284546A99670FC70004)
2022-03-02T11:38:49.889Z Change received: "... followed immediately by a 1MB document" (token: 82621F54D5000000012B022C0100296E5A1004D9EC8991B42F4F71BA61FC5BA26E2DED46645F69640064621F54D53284546A99670FC80004)
2022-03-02T11:38:49.889Z Change received: "100 6MB documents preceded this 3MB document" (token: 82621F54E8000000012B022C0100296E5A1004D9EC8991B42F4F71BA61FC5BA26E2DED46645F69640064621F54E83284546A9967102D0004)
2022-03-02T11:38:49.889Z Change received: "... followed by another 1MB document" (token: 82621F54E9000000012B022C0100296E5A1004D9EC8991B42F4F71BA61FC5BA26E2DED46645F69640064621F54E93284546A9967102E0004)
2022-03-02T11:38:49.890Z Change received: "500 6MB documents added" (token: 82621F5531000000072B022C0100296E5A1004D9EC8991B42F4F71BA61FC5BA26E2DED46645F69640064621F55313284546A996712230004)
2022-03-02T11:38:49.890Z Change received: "200 6MB documents added" (token: 82621F554D000000052B022C0100296E5A1004D9EC8991B42F4F71BA61FC5BA26E2DED46645F69640064621F554D3284546A996712EC0004)
2022-03-02T11:38:49.890Z Change received: "Adding 2000 more 6MB documents..." (token: 82621F554D000000062B022C0100296E5A1004D9EC8991B42F4F71BA61FC5BA26E2DED46645F69640064621F554D3284546A996712ED0004)
2022-03-02T11:38:49.891Z Change received: "This is the last document we'd expect" (token: 82621F5724000000012B022C0100296E5A1004D9EC8991B42F4F71BA61FC5BA26E2DED46645F69640064621F57243284546A99671ABE0004)
```

Note that ~12 seconds elapse between the cursor being opened and the results all being returned apparently at once.

Reviewing the logs for this operation show that a single `aggregate` command was executed that returned about 5MB of data ([`reslen`](https://docs.mongodb.com/manual/reference/database-profiler/#mongodb-data-system.profile.responseLength)) in 10 documents ([`nreturned`](https://docs.mongodb.com/manual/reference/database-profiler/#mongodb-data-system.profile.nreturned)). 3060 documents were scanned to identify these results and that required 19GB ([`bytesRead`](https://docs.mongodb.com/manual/reference/database-profiler/#mongodb-data-system.profile.storage.data.bytesRead)) to be read from disk into cache.

> {"t":{"$date":"2022-03-02T06:38:47.825-05:00"},"s":"I",  "c":"COMMAND",  "id":51803,   "ctx":"conn53","msg":"Slow query","attr":{"type":"command","ns":"test.foo","command":{`"aggregate":"foo"`,"pipeline":[{"$changeStream":{"fullDocument":"default","resumeAfter":{"_data":"82621F5485000000022B022C0100296E5A1004D9EC8991B42F4F71BA61FC5BA26E2DED46645F69640064621F54853284546A99670EFC0004"}}},{"$match":{"fullDocument.msg":{"$exists":true}}},{"$project":{"fullDocument":1}}],"cursor":{},"lsid":{"id":{"$uuid":"14c4f916-957f-4245-8106-b617b17fa603"}},"$clusterTime":{"clusterTime":{"$timestamp":{"t":1646221107,"i":1}},"signature":{"hash":{"$binary":{"base64":"AAAAAAAAAAAAAAAAAAAAAAAAAAA=","subType":"0"}},"keyId":0}},"$db":"test"},"planSummary":"COLLSCAN","cursorid":8835322801609070020,"keysExamined":0,"docsExamined":3039,"numYields":636,`"nreturned":10`,"queryHash":"7C2ADF3A",`"reslen":5248534`,"locks":{"Global":{"acquireCount":{"r":640}},"Mutex":{"acquireCount":{"r":4}}},"readConcern":{"level":"majority"},"writeConcern":{"w":"majority","wtimeout":0,"provenance":"implicitDefault"},"storage":{"data":{`"bytesRead":19528768718`,"timeReadingMicros":9979872},"timeWaitingMicros":{"cache":4991}},"remote":"192.168.2.100:61953","protocol":"op_msg","durationMillis":12356}}

The entire operation took 12.36 seconds ([`durationMillis`](https://docs.mongodb.com/manual/reference/database-profiler/#mongodb-data-system.profile.millis)) to complete.

## Performance Using a Smaller Cursor `batchSize`

According to the previous log entry, all outstanding results following the resume token were returned in a single [cursor batch](https://docs.mongodb.com/manual/tutorial/iterate-a-cursor/#cursor-batches). By default, `find()` and `aggregate()` operations have an initial batch size of 101 documents. Subsequent [`getMore`](https://docs.mongodb.com/manual/reference/command/getMore/) operations issued against the resulting cursor have no default batch size, so they are limited only by the 16 megabyte message size (the [BSON Max Size](https://docs.mongodb.com/manual/reference/limits/#std-label-limit-bson-document-size)).

Let's try adjusting `nodejs-resume-changestream.js` with a [`cursor.batchSize()`](https://docs.mongodb.com/manual/reference/method/cursor.batchSize) of 1, as this should return documents as they're found.

```js
var changeStream = collection.watch([
  { $match: { "fullDocument.msg": { $exists: true } } },
  { $project: { fullDocument: 1 } }
  ], { resumeAfter: resumeToken, batchSize: 1 }); // <-- add `batchSize: 1`
```

```bash
2022-03-02T11:47:26.743Z Resuming Change Stream ...
2022-03-02T11:47:27.952Z Change received: "This document will be 1Kb" (token: 82621F54B3000000012B022C0100296E5A1004D9EC8991B42F4F71BA61FC5BA26E2DED46645F69640064621F54B33284546A99670EFD0004)
2022-03-02T11:47:27.958Z Change received: "100 6MB documents, then another 1Kb document" (token: 82621F54C4000000062B022C0100296E5A1004D9EC8991B42F4F71BA61FC5BA26E2DED46645F69640064621F54C43284546A99670F620004)
2022-03-02T11:47:27.962Z Change received: "And another 100 6MB documents, then another 1Kb document" (token: 82621F54D4000000072B022C0100296E5A1004D9EC8991B42F4F71BA61FC5BA26E2DED46645F69640064621F54D43284546A99670FC70004)
2022-03-02T11:47:28.097Z Change received: "... followed immediately by a 1MB document" (token: 82621F54D5000000012B022C0100296E5A1004D9EC8991B42F4F71BA61FC5BA26E2DED46645F69640064621F54D53284546A99670FC80004)
2022-03-02T11:47:28.364Z Change received: "100 6MB documents preceded this 3MB document" (token: 82621F54E8000000012B022C0100296E5A1004D9EC8991B42F4F71BA61FC5BA26E2DED46645F69640064621F54E83284546A9967102D0004)
2022-03-02T11:47:28.463Z Change received: "... followed by another 1MB document" (token: 82621F54E9000000012B022C0100296E5A1004D9EC8991B42F4F71BA61FC5BA26E2DED46645F69640064621F54E93284546A9967102E0004)
2022-03-02T11:47:30.474Z Change received: "500 6MB documents added" (token: 82621F5531000000072B022C0100296E5A1004D9EC8991B42F4F71BA61FC5BA26E2DED46645F69640064621F55313284546A996712230004)
2022-03-02T11:47:31.234Z Change received: "200 6MB documents added" (token: 82621F554D000000052B022C0100296E5A1004D9EC8991B42F4F71BA61FC5BA26E2DED46645F69640064621F554D3284546A996712EC0004)
2022-03-02T11:47:31.239Z Change received: "Adding 2000 more 6MB documents..." (token: 82621F554D000000062B022C0100296E5A1004D9EC8991B42F4F71BA61FC5BA26E2DED46645F69640064621F554D3284546A996712ED0004)
2022-03-02T11:47:39.334Z Change received: "This is the last document we'd expect" (token: 82621F5724000000012B022C0100296E5A1004D9EC8991B42F4F71BA61FC5BA26E2DED46645F69640064621F57243284546A99671ABE0004)
```

Unlike the first example that returned all results as they fit into the initial batch size, now a `getMore` is being issued for each result returned from the cursor. Checking the logs again we can verify this as we expect there to be 10 log entries associated with the change stream's cursor id (`8620417026431980160` in this case):

```log
{"t":{"$date":"2022-03-02T06:47:26.367-05:00"},"s":"I",  "c":"COMMAND",  "id":51803,   "ctx":"conn66","msg":"Slow query","attr":{"type":"command","ns":"test.foo","command":{"aggregate":"foo","pipeline":[{"$changeStream":{"fullDocument":"default","resumeAfter":{"_data":"82621F5485000000022B022C0100296E5A1004D9EC8991B42F4F71BA61FC5BA26E2DED46645F69640064621F54853284546A99670EFC0004"}}},{"$match":{"fullDocument.msg":{"$exists":true}}},{"$project":{"fullDocument":1}}],"cursor":{"batchSize":1},"lsid":{"id":{"$uuid":"4a230956-9cbe-48a9-9093-8c2fae2b659f"}},"$clusterTime":{"clusterTime":{"$timestamp":{"t":1646221637,"i":1}},"signature":{"hash":{"$binary":{"base64":"AAAAAAAAAAAAAAAAAAAAAAAAAAA=","subType":"0"}},"keyId":0}},"$db":"test"},"planSummary":"COLLSCAN","cursorid":8620417026431980160,"keysExamined":0,"docsExamined":309,"numYields":59,"nreturned":1,"queryHash":"7C2ADF3A","reslen":1618,"locks":{"Global":{"acquireCount":{"r":61}},"Mutex":{"acquireCount":{"r":2}}},"readConcern":{"level":"majority"},"writeConcern":{"w":"majority","wtimeout":0,"provenance":"implicitDefault"},"storage":{"data":{"bytesRead":1942084556,"timeReadingMicros":951431},"timeWaitingMicros":{"cache":3195}},"remote":"192.168.2.100:53792","protocol":"op_msg","durationMillis":1181}}
{"t":{"$date":"2022-03-02T06:47:26.375-05:00"},"s":"I",  "c":"COMMAND",  "id":51803,   "ctx":"conn66","msg":"Slow query","attr":{"type":"command","ns":"test.foo","command":{"getMore":8620417026431980160,"collection":"foo","batchSize":1,"lsid":{"id":{"$uuid":"4a230956-9cbe-48a9-9093-8c2fae2b659f"}},"$clusterTime":{"clusterTime":{"$timestamp":{"t":1646221637,"i":1}},"signature":{"hash":{"$binary":{"base64":"AAAAAAAAAAAAAAAAAAAAAAAAAAA=","subType":"0"}},"keyId":0}},"$db":"test"},"originatingCommand":{"aggregate":"foo","pipeline":[{"$changeStream":{"fullDocument":"default","resumeAfter":{"_data":"82621F5485000000022B022C0100296E5A1004D9EC8991B42F4F71BA61FC5BA26E2DED46645F69640064621F54853284546A99670EFC0004"}}},{"$match":{"fullDocument.msg":{"$exists":true}}},{"$project":{"fullDocument":1}}],"cursor":{"batchSize":1},"lsid":{"id":{"$uuid":"4a230956-9cbe-48a9-9093-8c2fae2b659f"}},"$clusterTime":{"clusterTime":{"$timestamp":{"t":1646221637,"i":1}},"signature":{"hash":{"$binary":{"base64":"AAAAAAAAAAAAAAAAAAAAAAAAAAA=","subType":"0"}},"keyId":0}},"$db":"test"},"planSummary":"COLLSCAN","cursorid":8620417026431980160,"keysExamined":0,"docsExamined":0,"numYields":0,"nreturned":1,"queryHash":"7C2ADF3A","reslen":1636,"locks":{},"readConcern":{"level":"majority"},"writeConcern":{"w":"majority","wtimeout":0,"provenance":"implicitDefault"},"remote":"192.168.2.100:53792","protocol":"op_msg","durationMillis":0}}
{"t":{"$date":"2022-03-02T06:47:26.380-05:00"},"s":"I",  "c":"COMMAND",  "id":51803,   "ctx":"conn66","msg":"Slow query","attr":{"type":"command","ns":"test.foo","command":{"getMore":8620417026431980160,"collection":"foo","batchSize":1,"lsid":{"id":{"$uuid":"4a230956-9cbe-48a9-9093-8c2fae2b659f"}},"$clusterTime":{"clusterTime":{"$timestamp":{"t":1646221637,"i":1}},"signature":{"hash":{"$binary":{"base64":"AAAAAAAAAAAAAAAAAAAAAAAAAAA=","subType":"0"}},"keyId":0}},"$db":"test"},"originatingCommand":{"aggregate":"foo","pipeline":[{"$changeStream":{"fullDocument":"default","resumeAfter":{"_data":"82621F5485000000022B022C0100296E5A1004D9EC8991B42F4F71BA61FC5BA26E2DED46645F69640064621F54853284546A99670EFC0004"}}},{"$match":{"fullDocument.msg":{"$exists":true}}},{"$project":{"fullDocument":1}}],"cursor":{"batchSize":1},"lsid":{"id":{"$uuid":"4a230956-9cbe-48a9-9093-8c2fae2b659f"}},"$clusterTime":{"clusterTime":{"$timestamp":{"t":1646221637,"i":1}},"signature":{"hash":{"$binary":{"base64":"AAAAAAAAAAAAAAAAAAAAAAAAAAA=","subType":"0"}},"keyId":0}},"$db":"test"},"planSummary":"COLLSCAN","cursorid":8620417026431980160,"keysExamined":0,"docsExamined":0,"numYields":0,"nreturned":1,"queryHash":"7C2ADF3A","reslen":1648,"locks":{},"readConcern":{"level":"majority"},"writeConcern":{"w":"majority","wtimeout":0,"provenance":"implicitDefault"},"remote":"192.168.2.100:53792","protocol":"op_msg","durationMillis":0}}
{"t":{"$date":"2022-03-02T06:47:26.385-05:00"},"s":"I",  "c":"COMMAND",  "id":51803,   "ctx":"conn66","msg":"Slow query","attr":{"type":"command","ns":"test.foo","command":{"getMore":8620417026431980160,"collection":"foo","batchSize":1,"lsid":{"id":{"$uuid":"4a230956-9cbe-48a9-9093-8c2fae2b659f"}},"$clusterTime":{"clusterTime":{"$timestamp":{"t":1646221637,"i":1}},"signature":{"hash":{"$binary":{"base64":"AAAAAAAAAAAAAAAAAAAAAAAAAAA=","subType":"0"}},"keyId":0}},"$db":"test"},"originatingCommand":{"aggregate":"foo","pipeline":[{"$changeStream":{"fullDocument":"default","resumeAfter":{"_data":"82621F5485000000022B022C0100296E5A1004D9EC8991B42F4F71BA61FC5BA26E2DED46645F69640064621F54853284546A99670EFC0004"}}},{"$match":{"fullDocument.msg":{"$exists":true}}},{"$project":{"fullDocument":1}}],"cursor":{"batchSize":1},"lsid":{"id":{"$uuid":"4a230956-9cbe-48a9-9093-8c2fae2b659f"}},"$clusterTime":{"clusterTime":{"$timestamp":{"t":1646221637,"i":1}},"signature":{"hash":{"$binary":{"base64":"AAAAAAAAAAAAAAAAAAAAAAAAAAA=","subType":"0"}},"keyId":0}},"$db":"test"},"planSummary":"COLLSCAN","cursorid":8620417026431980160,"keysExamined":0,"docsExamined":0,"numYields":0,"nreturned":1,"queryHash":"7C2ADF3A","reslen":1049186,"locks":{},"readConcern":{"level":"majority"},"writeConcern":{"w":"majority","wtimeout":0,"provenance":"implicitDefault"},"remote":"192.168.2.100:53792","protocol":"op_msg","durationMillis":0}}
{"t":{"$date":"2022-03-02T06:47:26.521-05:00"},"s":"I",  "c":"COMMAND",  "id":51803,   "ctx":"conn66","msg":"Slow query","attr":{"type":"command","ns":"test.foo","command":{"getMore":8620417026431980160,"collection":"foo","batchSize":1,"lsid":{"id":{"$uuid":"4a230956-9cbe-48a9-9093-8c2fae2b659f"}},"$clusterTime":{"clusterTime":{"$timestamp":{"t":1646221637,"i":1}},"signature":{"hash":{"$binary":{"base64":"AAAAAAAAAAAAAAAAAAAAAAAAAAA=","subType":"0"}},"keyId":0}},"$db":"test"},"originatingCommand":{"aggregate":"foo","pipeline":[{"$changeStream":{"fullDocument":"default","resumeAfter":{"_data":"82621F5485000000022B022C0100296E5A1004D9EC8991B42F4F71BA61FC5BA26E2DED46645F69640064621F54853284546A99670EFC0004"}}},{"$match":{"fullDocument.msg":{"$exists":true}}},{"$project":{"fullDocument":1}}],"cursor":{"batchSize":1},"lsid":{"id":{"$uuid":"4a230956-9cbe-48a9-9093-8c2fae2b659f"}},"$clusterTime":{"clusterTime":{"$timestamp":{"t":1646221637,"i":1}},"signature":{"hash":{"$binary":{"base64":"AAAAAAAAAAAAAAAAAAAAAAAAAAA=","subType":"0"}},"keyId":0}},"$db":"test"},"planSummary":"COLLSCAN","cursorid":8620417026431980160,"keysExamined":0,"docsExamined":0,"numYields":0,"nreturned":1,"queryHash":"7C2ADF3A","reslen":3146340,"locks":{},"readConcern":{"level":"majority"},"writeConcern":{"w":"majority","wtimeout":0,"provenance":"implicitDefault"},"remote":"192.168.2.100:53792","protocol":"op_msg","durationMillis":2}}
{"t":{"$date":"2022-03-02T06:47:26.790-05:00"},"s":"I",  "c":"COMMAND",  "id":51803,   "ctx":"conn66","msg":"Slow query","attr":{"type":"command","ns":"test.foo","command":{"getMore":8620417026431980160,"collection":"foo","batchSize":1,"lsid":{"id":{"$uuid":"4a230956-9cbe-48a9-9093-8c2fae2b659f"}},"$clusterTime":{"clusterTime":{"$timestamp":{"t":1646221637,"i":1}},"signature":{"hash":{"$binary":{"base64":"AAAAAAAAAAAAAAAAAAAAAAAAAAA=","subType":"0"}},"keyId":0}},"$db":"test"},"originatingCommand":{"aggregate":"foo","pipeline":[{"$changeStream":{"fullDocument":"default","resumeAfter":{"_data":"82621F5485000000022B022C0100296E5A1004D9EC8991B42F4F71BA61FC5BA26E2DED46645F69640064621F54853284546A99670EFC0004"}}},{"$match":{"fullDocument.msg":{"$exists":true}}},{"$project":{"fullDocument":1}}],"cursor":{"batchSize":1},"lsid":{"id":{"$uuid":"4a230956-9cbe-48a9-9093-8c2fae2b659f"}},"$clusterTime":{"clusterTime":{"$timestamp":{"t":1646221637,"i":1}},"signature":{"hash":{"$binary":{"base64":"AAAAAAAAAAAAAAAAAAAAAAAAAAA=","subType":"0"}},"keyId":0}},"$db":"test"},"planSummary":"COLLSCAN","cursorid":8620417026431980160,"keysExamined":0,"docsExamined":1,"numYields":0,"nreturned":1,"queryHash":"7C2ADF3A","reslen":1049180,"locks":{"Global":{"acquireCount":{"r":1}},"Mutex":{"acquireCount":{"r":1}}},"readConcern":{"level":"majority"},"writeConcern":{"w":"majority","wtimeout":0,"provenance":"implicitDefault"},"storage":{"data":{"bytesRead":1048977,"timeReadingMicros":1974}},"remote":"192.168.2.100:53792","protocol":"op_msg","durationMillis":3}}
{"t":{"$date":"2022-03-02T06:47:28.885-05:00"},"s":"I",  "c":"COMMAND",  "id":51803,   "ctx":"conn66","msg":"Slow query","attr":{"type":"command","ns":"test.foo","command":{"getMore":8620417026431980160,"collection":"foo","batchSize":1,"lsid":{"id":{"$uuid":"4a230956-9cbe-48a9-9093-8c2fae2b659f"}},"$clusterTime":{"clusterTime":{"$timestamp":{"t":1646221637,"i":1}},"signature":{"hash":{"$binary":{"base64":"AAAAAAAAAAAAAAAAAAAAAAAAAAA=","subType":"0"}},"keyId":0}},"$db":"test"},"originatingCommand":{"aggregate":"foo","pipeline":[{"$changeStream":{"fullDocument":"default","resumeAfter":{"_data":"82621F5485000000022B022C0100296E5A1004D9EC8991B42F4F71BA61FC5BA26E2DED46645F69640064621F54853284546A99670EFC0004"}}},{"$match":{"fullDocument.msg":{"$exists":true}}},{"$project":{"fullDocument":1}}],"cursor":{"batchSize":1},"lsid":{"id":{"$uuid":"4a230956-9cbe-48a9-9093-8c2fae2b659f"}},"$clusterTime":{"clusterTime":{"$timestamp":{"t":1646221637,"i":1}},"signature":{"hash":{"$binary":{"base64":"AAAAAAAAAAAAAAAAAAAAAAAAAAA=","subType":"0"}},"keyId":0}},"$db":"test"},"planSummary":"COLLSCAN","cursorid":8620417026431980160,"keysExamined":0,"docsExamined":501,"numYields":104,"nreturned":1,"queryHash":"7C2ADF3A","reslen":583,"locks":{"Global":{"acquireCount":{"r":105}},"Mutex":{"acquireCount":{"r":1}}},"readConcern":{"level":"majority"},"writeConcern":{"w":"majority","wtimeout":0,"provenance":"implicitDefault"},"storage":{"data":{"bytesRead":3246578426,"timeReadingMicros":1613240},"timeWaitingMicros":{"cache":2390}},"remote":"192.168.2.100:53792","protocol":"op_msg","durationMillis":2000}}
{"t":{"$date":"2022-03-02T06:47:29.651-05:00"},"s":"I",  "c":"COMMAND",  "id":51803,   "ctx":"conn66","msg":"Slow query","attr":{"type":"command","ns":"test.foo","command":{"getMore":8620417026431980160,"collection":"foo","batchSize":1,"lsid":{"id":{"$uuid":"4a230956-9cbe-48a9-9093-8c2fae2b659f"}},"$clusterTime":{"clusterTime":{"$timestamp":{"t":1646221647,"i":1}},"signature":{"hash":{"$binary":{"base64":"AAAAAAAAAAAAAAAAAAAAAAAAAAA=","subType":"0"}},"keyId":0}},"$db":"test"},"originatingCommand":{"aggregate":"foo","pipeline":[{"$changeStream":{"fullDocument":"default","resumeAfter":{"_data":"82621F5485000000022B022C0100296E5A1004D9EC8991B42F4F71BA61FC5BA26E2DED46645F69640064621F54853284546A99670EFC0004"}}},{"$match":{"fullDocument.msg":{"$exists":true}}},{"$project":{"fullDocument":1}}],"cursor":{"batchSize":1},"lsid":{"id":{"$uuid":"4a230956-9cbe-48a9-9093-8c2fae2b659f"}},"$clusterTime":{"clusterTime":{"$timestamp":{"t":1646221637,"i":1}},"signature":{"hash":{"$binary":{"base64":"AAAAAAAAAAAAAAAAAAAAAAAAAAA=","subType":"0"}},"keyId":0}},"$db":"test"},"planSummary":"COLLSCAN","cursorid":8620417026431980160,"keysExamined":0,"docsExamined":201,"numYields":38,"nreturned":1,"queryHash":"7C2ADF3A","reslen":583,"locks":{"Global":{"acquireCount":{"r":39}},"Mutex":{"acquireCount":{"r":1}}},"readConcern":{"level":"majority"},"writeConcern":{"w":"majority","wtimeout":0,"provenance":"implicitDefault"},"storage":{"data":{"bytesRead":1289823601,"timeReadingMicros":625733},"timeWaitingMicros":{"cache":15}},"remote":"192.168.2.100:53792","protocol":"op_msg","durationMillis":754}}
{"t":{"$date":"2022-03-02T06:47:29.656-05:00"},"s":"I",  "c":"COMMAND",  "id":51803,   "ctx":"conn66","msg":"Slow query","attr":{"type":"command","ns":"test.foo","command":{"getMore":8620417026431980160,"collection":"foo","batchSize":1,"lsid":{"id":{"$uuid":"4a230956-9cbe-48a9-9093-8c2fae2b659f"}},"$clusterTime":{"clusterTime":{"$timestamp":{"t":1646221647,"i":1}},"signature":{"hash":{"$binary":{"base64":"AAAAAAAAAAAAAAAAAAAAAAAAAAA=","subType":"0"}},"keyId":0}},"$db":"test"},"originatingCommand":{"aggregate":"foo","pipeline":[{"$changeStream":{"fullDocument":"default","resumeAfter":{"_data":"82621F5485000000022B022C0100296E5A1004D9EC8991B42F4F71BA61FC5BA26E2DED46645F69640064621F54853284546A99670EFC0004"}}},{"$match":{"fullDocument.msg":{"$exists":true}}},{"$project":{"fullDocument":1}}],"cursor":{"batchSize":1},"lsid":{"id":{"$uuid":"4a230956-9cbe-48a9-9093-8c2fae2b659f"}},"$clusterTime":{"clusterTime":{"$timestamp":{"t":1646221637,"i":1}},"signature":{"hash":{"$binary":{"base64":"AAAAAAAAAAAAAAAAAAAAAAAAAAA=","subType":"0"}},"keyId":0}},"$db":"test"},"planSummary":"COLLSCAN","cursorid":8620417026431980160,"keysExamined":0,"docsExamined":1,"numYields":0,"nreturned":1,"queryHash":"7C2ADF3A","reslen":593,"locks":{"Global":{"acquireCount":{"r":1}},"Mutex":{"acquireCount":{"r":1}}},"readConcern":{"level":"majority"},"writeConcern":{"w":"majority","wtimeout":0,"provenance":"implicitDefault"},"storage":{},"remote":"192.168.2.100:53792","protocol":"op_msg","durationMillis":0}}
{"t":{"$date":"2022-03-02T06:47:37.751-05:00"},"s":"I",  "c":"COMMAND",  "id":51803,   "ctx":"conn66","msg":"Slow query","attr":{"type":"command","ns":"test.foo","command":{"getMore":8620417026431980160,"collection":"foo","batchSize":1,"lsid":{"id":{"$uuid":"4a230956-9cbe-48a9-9093-8c2fae2b659f"}},"$clusterTime":{"clusterTime":{"$timestamp":{"t":1646221647,"i":1}},"signature":{"hash":{"$binary":{"base64":"AAAAAAAAAAAAAAAAAAAAAAAAAAA=","subType":"0"}},"keyId":0}},"$db":"test"},"originatingCommand":{"aggregate":"foo","pipeline":[{"$changeStream":{"fullDocument":"default","resumeAfter":{"_data":"82621F5485000000022B022C0100296E5A1004D9EC8991B42F4F71BA61FC5BA26E2DED46645F69640064621F54853284546A99670EFC0004"}}},{"$match":{"fullDocument.msg":{"$exists":true}}},{"$project":{"fullDocument":1}}],"cursor":{"batchSize":1},"lsid":{"id":{"$uuid":"4a230956-9cbe-48a9-9093-8c2fae2b659f"}},"$clusterTime":{"clusterTime":{"$timestamp":{"t":1646221637,"i":1}},"signature":{"hash":{"$binary":{"base64":"AAAAAAAAAAAAAAAAAAAAAAAAAAA=","subType":"0"}},"keyId":0}},"$db":"test"},"planSummary":"COLLSCAN","cursorid":8620417026431980160,"keysExamined":0,"docsExamined":2024,"numYields":411,"nreturned":1,"queryHash":"7C2ADF3A","reslen":597,"locks":{"Global":{"acquireCount":{"r":412}},"Mutex":{"acquireCount":{"r":1}}},"readConcern":{"level":"majority"},"writeConcern":{"w":"majority","wtimeout":0,"provenance":"implicitDefault"},"storage":{"data":{"bytesRead":13017774068,"timeReadingMicros":6513189},"timeWaitingMicros":{"cache":19677}},"remote":"192.168.2.100:53792","protocol":"op_msg","durationMillis":8090}}
```

From start to finish both approaches will take approximately the same amount of time, however from an application responsiveness point of view processing events as they're found compared to waiting for a batch is likely a better user experience.

## How Internal Aggregation Batching Logic Affects `batchSize`

Expanding on this further, let's say we wanted to resume after the third last entry (_"200 6MB documents added"_):

```
2022-03-02T11:47:31.234Z Change received: "200 6MB documents added" (token: 82621F554D000000052B022C0100296E5A1004D9EC8991B42F4F71BA61FC5BA26E2DED46645F69640064621F554D3284546A996712EC0004)
2022-03-02T11:47:31.239Z Change received: "Adding 2000 more 6MB documents..." (token: 82621F554D000000062B022C0100296E5A1004D9EC8991B42F4F71BA61FC5BA26E2DED46645F69640064621F554D3284546A996712ED0004)
2022-03-02T11:47:39.334Z Change received: "This is the last document we'd expect" (token: 82621F5724000000012B022C0100296E5A1004D9EC8991B42F4F71BA61FC5BA26E2DED46645F69640064621F57243284546A99671ABE0004)
```

To do this we'd supply the `resumeToken` (`82621F554D000000052B022C0100296E5A1004D9EC8991B42F4F71BA61FC5BA26E2DED46645F69640064621F554D3284546A996712EC0004` as seen above) to the code sample and run again. The expectation in this case would be that _"Adding 2000 more 6MB documents..."_ would almost immediately return, followed after a brief delay by _"This is the last document we'd expect"_, however when we run the code ... that's not what we see. Instead after 6+ seconds _both_ documents are returned:

```
2022-03-02T12:15:49.134Z Resuming Change Stream ...
2022-03-02T12:15:55.831Z Change received: "Adding 2000 more 6MB documents..." (token: 82621F554D000000062B022C0100296E5A1004D9EC8991B42F4F71BA61FC5BA26E2DED46645F69640064621F554D3284546A996712ED0004)
2022-03-02T12:15:55.838Z Change received: "This is the last document we'd expect" (token: 82621F5724000000012B022C0100296E5A1004D9EC8991B42F4F71BA61FC5BA26E2DED46645F69640064621F57243284546A99671ABE0004)
```

As an optimization, MongoDB's query engine internally caches data from a cursor before pipeline processing. This is controlled by the [`internalDocumentSourceCursorBatchSizeBytes` query execution knob](https://github.com/mongodb/mongo/blob/a94caa502cf94fa6c8fcfea7283d7eaf3bd55ad5/src/mongo/db/query/query_knobs.idl#L391-L399) which defaults to 4MB (lowered from 16MB in MongoDB 3.4.2 via [SERVER-27406](https://jira.mongodb.org/browse/SERVER-27406)).

<div class="note warning">
  <span>WARNING</span>
  <p>I'm not recommending changing <code>internalDocumentSourceCursorBatchSizeBytes</code>, but instead highlighting how this option affects the behavior of the change stream.<br>Any MongoDB Server parameter that has an <code>internal</code> prefix should only be adjusted after thorough lower-environment testing or consultation with MongoDB Support</p>
</div>

We can verify this tuneable is in fact affecting the behavior of our change stream by lowering the value from 4194304 to 128 (via the `mongosh` shell):

```js
db.adminCommand({
  setParameter: 1,
  internalDocumentSourceCursorBatchSizeBytes: 128
});
```

After making this change, resuming our change stream returns _"Adding 2000 more 6MB documents..."_ almost instantly whereas _"This is the last document we'd expect"_ returns 7 seconds later.

```
2022-03-02T14:11:41.416Z Resuming Change Stream ...
2022-03-02T14:11:41.445Z Change received: "Adding 2000 more 6MB documents..." (token: 82621F554D000000062B022C0100296E5A1004D9EC8991B42F4F71BA61FC5BA26E2DED46645F69640064621F554D3284546A996712ED0004)
2022-03-02T14:11:48.054Z Change received: "This is the last document we'd expect" (token: 82621F5724000000012B022C0100296E5A1004D9EC8991B42F4F71BA61FC5BA26E2DED46645F69640064621F57243284546A99671ABE0004)
```

## Summary

If you're using MongoDB Change Streams and filtering for events that occur infrequently (compared to other activity within the oplog) resuming the change stream may appear "sluggish" using the defaults. Consider specifying a custom `batchSize` based on your workload to potentially improve the time to returning the first event.

## Reproduction

The scripts used in this article can be found below. I configured a local environment running a MongoDB 5.2.0 3 node replica set using the [`m` version manager](https://github.com/aheckmann/m) as well as [`mtools`](https://github.com/rueckstiess/mtools).

```bash
m 5.2.0-ent
mlaunch init --replicaset --nodes 3 --bind_ip_all --binarypath $(m bin 5.2.0-ent)
```

To use the scripts below save them locally and execute the associated commands from the same directory.

### `shell-configure-test.js`

This script for the `mongo`/`mongosh` shell contains the helper functions used in this article to configure the environment and generate the write load.

```js
// filename: shell-configure-test.js
//
function setupEnvironment() {
  // set the oplog to at least 20GB (20480MB) so our workload doesn't roll out
  db.adminCommand({ replSetResizeOplog: 1, size: 20480 });

  // insert one document and observe the result from the change stream cursor
  db.getSiblingDB("test").foo.insertOne({ msg: "We expect our filter to match this" });
}

function randomString(length) {
   var result           = '';
   var characters       = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
   var charactersLength = characters.length;
   for ( var i = 0; i < length; i++ ) {
      result += characters.charAt(Math.floor(Math.random() * charactersLength));
   }
   return result;
}

function writeJunk(count, stringLength) {
  print("Pushing " + count + " junk docs of size " + stringLength);
  var data = [];
  // doesn't matter what the string is so just reuse it
  var string = randomString(stringLength);
  for (var i = 0; i < count; i++) {
    data.push({ i: i, s: string });
  }
  db.getSiblingDB("test").foo.insertMany(data);
}

function seedCollection() {
  db.foo.insertOne({ msg: "This document will be 1Kb", s: randomString(1024) });
  writeJunk(100, 1048576 * 6);
  db.foo.insertOne({ msg: "100 6MB documents, then another 1Kb document", s: randomString(1024) });
  writeJunk(100, 1048576 * 6);
  db.foo.insertOne({ msg: "And another 100 6MB documents, then another 1Kb document", s: randomString(1024) });
  db.foo.insertOne({ msg: "... followed immediately by a 1MB document", s: randomString(1024 * 1024) });
  writeJunk(100, 1048576 * 6);
  db.foo.insertOne({ msg: "100 6MB documents preceded this 3MB document", s: randomString(1024 * 1024 * 3) });
  db.foo.insertOne({ msg: "... followed by another 1MB document", s: randomString(1024 * 1024) });
  writeJunk(500, 1048576 * 6);
  db.foo.insertOne({ msg: "500 6MB documents added" });
  writeJunk(200, 1048576 * 6);
  db.foo.insertOne({ msg: "200 6MB documents added" });
  db.foo.insertOne({ msg: "Adding 2000 more 6MB documents..." });
  writeJunk(2000, 1048576 * 6);
  db.foo.insertOne({ msg: "This is the last document we'd expect" });
}
```

### `nodejs-capture-first-event.js`

This Node.js script should be used to listen for the first change event from which we'll extract a resume token for later use.

```js
// file: nodejs-capture-first-event.js
//
// Configure the `MongoClient` with connection details appropriate to your environment
const { MongoClient } = require("mongodb");
const client = new MongoClient("mongodb://localhost:27017/test?replicaSet=replset");

async function run() {
  await client.connect();
  const database = client.db("test");
  const collection = database.collection("foo");
  var changeStream = collection.watch([ { $match: { "fullDocument.msg": { $exists: true } } }]);
  changeStream.on("change", next => {
    console.log(`${new Date().toISOString()} Change received: `, next);
    process.exit(0);
  });
}
run().catch(console.dir);
```

### `nodejs-resume-changestream.js`

The resume token found when running `nodejs-capture-first-event.js` can be plugged into this script to capture matching events following the token.

```js
// file: nodejs-resume-changestream.js
//
// Configure the `MongoClient` with connection details appropriate to your environment
const { MongoClient } = require("mongodb");
const client = new MongoClient("mongodb://localhost:27017/test?replicaSet=replset");

async function run() {
  await client.connect();
  const database = client.db("test");
  const collection = database.collection("foo");
  // replace the resume token with the value from your own tests
  var resumeToken = { _data: '82620B98E5000000022B022C0100296E5A1004437FB549CFDD45269DD59B9BF0EB354746645F69640064620B98E564DA118651C642000004' }
  console.log(`${new Date().toISOString()} Resuming Change Stream ...`);
  var changeStream = collection.watch([
    { $match: { "fullDocument.msg": { $exists: true } } },
    { $project: { fullDocument: 1 } }
  ], { resumeAfter: resumeToken });
  changeStream.on("change", next => {
    console.log(`${new Date().toISOString()} Change received: ${next.fullDocument.msg} (token: ${next._id._data})`);
  });
}
run().catch(console.dir);
```