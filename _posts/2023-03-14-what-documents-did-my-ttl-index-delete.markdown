---
layout: post
title: "What documents did my TTL index delete?"
date: 2023-03-14 07:32:05 -0400
comments: true
categories: MongoDB
tags: [indexing, ttl, mongodb]
image:
  src: /images/mongodb-logo.png
  alt: MongoDB Logo
---

## Overview

[TTL indexes](https://www.mongodb.com/docs/manual/core/index-ttl/) are special single-field indexes that MongoDB can use to automatically remove documents from a collection after a certain amount of time or at a specific clock time. Data expiration is useful for certain types of information like machine generated event data, logs, and session information that only need to persist in a database for a finite amount of time.

The actual removal of documents is handled by a separate thread within the [`mongod`](https://www.mongodb.com/docs/v6.0/reference/program/mongod/#mongodb-binary-bin.mongod) process called the [`TTLMonitor`](https://github.com/mongodb/mongo/blob/r6.2.1/src/mongo/db/catalog/README.md#the-ttlmonitor) (enabled by default via [`ttlMonitorEnabled`](https://www.mongodb.com/docs/v5.0/reference/parameters/#mongodb-parameter-param.ttlMonitorEnabled)), which will wake up and check all TTL indexes for expired documents every 60 seconds (the default value of `ttlMonitorSleepSecs`).

Unfortunately the `mongod` logs won't record any information about TTL index activity unless the operation happens to exceed the [slow query threshold](https://www.mongodb.com/docs/manual/reference/command/profile/#command-fields) (default of `100ms`). For the purposes of this article we want to see more information regarding TTL index activity so we'll begin by increasing the [log verbosity for the `index` component](https://www.mongodb.com/docs/manual/reference/method/db.setLogLevel/#set-verbosity-level-for-a-component):

```js
db.setLogLevel(1, 'index');
```

Continue to monitor the `mongod` log we'll begin to see messages such as the following begin to be recorded:

```json
{"t":{"$date":"2023-03-14T06:41:26.314-04:00"},"s":"D1","c":"INDEX","id":22533,"ctx":"TTLMonitor","msg":"running TTL job for index","attr":{"namespace":"config.tenantMigrationRecipients","key":{"expireAt":1},"name":"TenantMigrationRecipientTTLIndex"}}
{"t":{"$date":"2023-03-14T06:41:26.314-04:00"},"s":"I","c":"INDEX","id":5479200,"ctx":"TTLMonitor","msg":"Deleted expired documents using index","attr":{"namespace":"config.tenantMigrationRecipients","index":"TenantMigrationRecipientTTLIndex","numDeleted":0,"durationMillis":0}}
{"t":{"$date":"2023-03-14T06:41:26.314-04:00"},"s":"D1","c":"INDEX","id":22533,"ctx":"TTLMonitor","msg":"running TTL job for index","attr":{"namespace":"config.external_validation_keys","key":{"ttlExpiresAt":1},"name":"ExternalKeysTTLIndex"}}
{"t":{"$date":"2023-03-14T06:41:26.315-04:00"},"s":"I","c":"INDEX","id":5479200,"ctx":"TTLMonitor","msg":"Deleted expired documents using index","attr":{"namespace":"config.external_validation_keys","index":"ExternalKeysTTLIndex","numDeleted":0,"durationMillis":0}}
{"t":{"$date":"2023-03-14T06:41:26.315-04:00"},"s":"D1","c":"INDEX","id":22533,"ctx":"TTLMonitor","msg":"running TTL job for index","attr":{"namespace":"config.tenantMigrationDonors","key":{"expireAt":1},"name":"TenantMigrationDonorTTLIndex"}}
{"t":{"$date":"2023-03-14T06:41:26.315-04:00"},"s":"I","c":"INDEX","id":5479200,"ctx":"TTLMonitor","msg":"Deleted expired documents using index","attr":{"namespace":"config.tenantMigrationDonors","index":"TenantMigrationDonorTTLIndex","numDeleted":0,"durationMillis":0}}
{"t":{"$date":"2023-03-14T06:41:26.315-04:00"},"s":"D1","c":"INDEX","id":22533,"ctx":"TTLMonitor","msg":"running TTL job for index","attr":{"namespace":"config.system.sessions","key":{"lastUse":1},"name":"lsidTTLIndex"}}
{"t":{"$date":"2023-03-14T06:41:26.315-04:00"},"s":"I","c":"INDEX","id":5479200,"ctx":"TTLMonitor","msg":"Deleted expired documents using index","attr":{"namespace":"config.system.sessions","index":"lsidTTLIndex","numDeleted":0,"durationMillis":0}}
```

This is due to MongoDB utilizing TTL indexes for some internal housekeeping tasks. As these indexes are out of scope for this article we'll skip over them for now and create a new TTL index:

```js
db.foo.drop();
db.foo.createIndex({ "created_at": 1 }, { expireAfterSeconds: 10 });
db.foo.insertOne({ created_at: new Date()});
```

Our new collection now has a single document, which should expire after 10 seconds of being created. Note that the timing will almost never be exact as the TTL monitor will only activate every minute.

The test cluster we're running on is a [replica set](https://www.mongodb.com/docs/manual/reference/glossary/#std-term-replica-set), and as such we're only monitoring the logs for the [`primary`](https://www.mongodb.com/docs/manual/reference/glossary/#std-term-primary) member. The reason for this can be found in the [TTL Indexes documentation regarding replica set behavior](https://www.mongodb.com/docs/manual/core/index-ttl/#replica-sets):

> On replica set members, the TTL background thread _only_ deletes documents when a member is in state `primary`. The TTL background thread is idle when a member is in state [`secondary`](https://www.mongodb.com/docs/manual/reference/glossary/#std-term-secondary). Secondary members replicate deletion operations from the primary.

Within a minute or two a log entry similar to the following will be recorded that indicates our `test.foo` namespace has been processed, the `created_at_1` index has been executed and our document was expired:

```json
{"t":{"$date":"2023-03-14T06:47:41.336-04:00"},"s":"D1","c":"INDEX","id":22533,"ctx":"TTLMonitor","msg":"running TTL job for index","attr":{"namespace":"test.foo","key":{"created_at":1},"name":"created_at_1"}}
{"t":{"$date":"2023-03-14T06:47:41.336-04:00"},"s":"I","c":"INDEX","id":5479200,"ctx":"TTLMonitor","msg":"Deleted expired documents using index","attr":{"namespace":"test.foo","index":"created_at_1","numDeleted":1,"durationMillis":0}}
```

Unfortunately all this presents us with is confirmation that _something_ was removed, but is it possible to find out _what_ was removed?

## Enter the Oplog

As the cluster we're connected to is a replica set all write operations are recorded in the [operations log (oplog)](https://www.mongodb.com/docs/manual/core/replica-set-oplog/). As the oplog is a [capped collection](https://www.mongodb.com/docs/manual/reference/glossary/#std-term-capped-collection) present on each replica set member, we can query it directly to see what write operations have propagated at a given time!

Using the log entry above that confirmed 1 document was deleted we can prepare the following operation to filter the contents of the oplog collection:

```js
// the namespace from the log entry indicating nDeleted > 0
// that we're interested in
var ns = "test.foo";
// the time (with timezone) from the log message
var t1 = new Date("2023-03-14T06:47:41.336-04:00");
// the number of seconds between TTLMonitor sweeps - default: 60
var ttlSleep = db.adminCommand({
  getParameter: 1,
  ttlMonitorSleepSecs: 1 }
).ttlMonitorSleepSecs;
// get the time (in milliseconds) of the starting time and convert
// the TTLMonitor sleep threshold to milliseconds
var t2 = new Date(t1.getTime() + (ttlSleep * 1000));
db.getSiblingDB("local").oplog.rs.find({
  op: "d",
  ns: ns,
  wall: { $gte: t1, $lt: t2 }
});
```

<div class="note warning">
<small>Any query targeting the oplog will perform a full collection scan as you cannot create indexes on the oplog collection!</small>
</div>

The above operation is purposely more verbose than necessary to illustrate where all the necessary pieces of information came from. Once this is executed it should return a single document as seen below, which represents the document that was deleted:

```js
[
  {
    "op": "d",
    "ns": "test.foo",
    "ui": {
      "$binary": {
        "base64": "K4vB+Oh9RgC5scSLCiYWiA==",
        "subType": "04"
      }
    },
    "o": {
      "_id": {
        "$oid": "641050bae52e6d96ee3c40fa"
      }
    },
    "ts": {
      "$timestamp": {
        "t": 1678790861,
        "i": 1
      }
    },
    "t": 8,
    "v": 2,
    "wall": {
      "$date": "2023-03-14T10:47:41.336Z"
    }
  }
]
```

The only information the oplog records for [`delete`](https://www.mongodb.com/docs/manual/reference/command/delete/) commands is the `_id` value of the document that was removed. Unless you manage your own custom `_id` generation, the values will likely just be generated [ObjectId](https://www.mongodb.com/docs/manual/reference/method/ObjectId/) values.

We can try to find out additional information about this deleted document by extracting the `_id` from the oplog document's `o` field, and using that to further filter the oplog:

```js
db.getSiblingDB("local").oplog.rs.find({
  // filter by namespace
  ns: "test.foo",
  // filter by insert or update
  op: { $in: ["i", "u"] },
  // filter on the o2._id field as it will be present
  // in both inserts and updates
  "o2._id": ObjectId("641050bae52e6d96ee3c40fa")
}).sort({ ts: -1 });
```

As documents within the [`local.oplog.rs`](https://www.mongodb.com/docs/manual/reference/local-database/#mongodb-data-local.oplog.rs) namespace will eventually roll over the above query is **not guaranteed to return anything**, however it's possible that document creation or update commands may still exist that can give you additional information regarding what this removed document contained:

```js
[
  {
    "lsid": {
      "id": {
        "$binary": {
          "base64": "SHocj0XsSTC25zlbzywaOA==",
          "subType": "04"
        }
      },
      "uid": {
        "$binary": {
          "base64": "47DEQpj8HBSa+/TImW+5JCeuQeRkm5NMpJWZG3hSuFU=",
          "subType": "00"
        }
      }
    },
    "txnNumber": 1,
    // an insert operation
    "op": "i",
    // the namespace the document was created in
    "ns": "test.foo",
    "ui": {
      "$binary": {
        "base64": "K4vB+Oh9RgC5scSLCiYWiA==",
        "subType": "04"
      }
    },
    // this field contains the values that were set when
    // the document was created
    "o": {
      "_id": {
        "$oid": "641050bae52e6d96ee3c40fa"
      },
      "created_at": {
        "$date": "2023-03-14T10:47:22.445Z"
      }
    },
    "o2": {
      "_id": {
        "$oid": "641050bae52e6d96ee3c40fa"
      }
    },
    "stmtId": 0,
    "ts": {
      "$timestamp": {
        "t": 1678790842,
        "i": 4
      }
    },
    "t": 8,
    "v": 2,
    // when the document was created
    "wall": {
      "$date": "2023-03-14T10:47:22.448Z"
    },
    "prevOpTime": {
      "ts": {
        "$timestamp": {
          "t": 0,
          "i": 0
        }
      },
      "t": -1
    }
  }
]
```

The result above represents an [`insert`](https://www.mongodb.com/docs/manual/reference/command/insert/) and under the `o` field contains the values that were initially set.

As stated earlier, this method is not guaranteed to work, however it may prove useful if you're trying to identify what document was deleted and your [oplog window]() is large enough that it still contains the document's creation. See [Change the Size of the Oplog](https://www.mongodb.com/docs/manual/tutorial/change-oplog-size/) for more information regarding sizing the oplog.