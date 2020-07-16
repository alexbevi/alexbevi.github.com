---
layout: post
title: "MongoDB 4.4 Change Streams and Pre-Image 'Support'"
date: 2020-07-15 08:37:08 -0400
comments: true
categories:
  - mongodb
---

**Warning**

_MongoDB's source code is available (through an [SSPL license](https://www.mongodb.com/licensing/server-side-public-license)) and the [Core Server](https://jira.mongodb.org/projects/SERVER/issues) project in MongoDB's JIRA is publicly accessible, which is where I found this information._
_Until officially announced as stable/official the methods described herein should not be considered as "production ready". This post is for informational purposes and though at the time of writing it I am a MongoDB Inc. employee this should not be considered an official communication._

### Introduction

A feature that has long been requested since [Change Streams](https://docs.mongodb.com/manual/changeStreams/) were [introduced in MongoDB 3.6](https://www.mongodb.com/blog/post/an-introduction-to-change-streams) is the ability to support returning the n-1 state (or pre-image) of a document when it is changed.

In [`SERVER-36941`: _Option to provide "before image" with change streams_](https://jira.mongodb.org/browse/SERVER-36941) this request is captured, but at the time of writing this ticket is still in an _Open_ state which would imply no progress has been made.

Interestingly enough, there actually has been some progress due to efforts surrounding the support of [Realm Sync](https://www.mongodb.com/realm/mobile/sync), namely in the following tickets:

* [`SERVER-45806`: _Record pre-images on updates and deletes when recordPreImage is enabled_](https://jira.mongodb.org/browse/SERVER-45806)
* [`SERVER-45807`: _Add change stream stage to fetch pre-image for update/replace/delete events_](https://jira.mongodb.org/browse/SERVER-45807)

### Pre-Image Support

"Support" for this feature is only available in MongoDB 4.4+, so first we must ensure we are running a compatible version.

Next, as change streams are only supported in [replica sets](https://docs.mongodb.com/manual/replication/) or [sharded clusters](https://docs.mongodb.com/manual/sharding/) our cluster cannot be a standalone instance.

Before a pre-image can be returned in a change stream support for the feature must be enabled at _the collection level_.

#### Create a New Collection with Pre-Image Support

<!-- MORE -->

To enable pre-image support on a new (non-existent) collection, the `recordPreImages` flag needs to be set when calling the [`create`](https://docs.mongodb.com/manual/reference/command/create/#dbcmd.create) command or [`db.createCollection()`](https://docs.mongodb.com/manual/reference/method/db.createCollection/) shell method:

```js
db.coll1.drop();
// create command
db.runCommand({ create: "coll1", recordPreImages: true });
// or
// using the createCollection() helper
db.createCollection("coll1", { recordPreImages: true });
```

#### Updating an Existing Collection with Pre-Image Support

If the collection already exists, the `recordPreImages` flag can be set using the [`collMod`](https://docs.mongodb.com/manual/reference/command/collMod/) command:

```js
db.coll1.drop();
db.coll1.insert({ _id: 1, created_at: new Date() });
// update the collection's metadata using the collMod command
db.runCommand({ collMod: "coll1", recordPreImages: true });
```

### Pre-Image Support in Change Streams

First it's important to understand that a change stream is actually an [Aggregation Pipeline Stage](https://docs.mongodb.com/manual/reference/operator/aggregation-pipeline/), even if it doesn't appear as such in the documentation.

This can be easily verified by checking the source code for the [`Mongo.prototype.watch`](https://github.com/mongodb/mongo/blob/v4.4/src/mongo/shell/mongo.js#L686) implementation which coincides with [`db.collection.watch()`](https://docs.mongodb.com/manual/reference/method/db.collection.watch/) shell method.

We'll be using the `$changeStream` pipeline stage directly to review the impact of pre-image support.

First we'll being by opening a change stream cursor against our modified collection:

```js
db.coll1.drop();
db.createCollection("coll1", { recordPreImages: true });
db.coll1.insert({ _id: 1, created_at: new Date() });
var cursor = db.coll1.aggregate([{
    $changeStream: { fullDocumentBeforeChange: "whenAvailable" } }
]);
```

Note the options include a `fullDocumentBeforeChange` field, which can accept one of three (3) `fullDocumentBeforeChange` mode values:

* `off`: Disables support for the `fullDocumentBeforeChange` field
* `whenAvailable`: Only includes a `fullDocumentBeforeChange` document if it's available, but won't fail if it's not present
* `required`: Require the `fullDocumentBeforeChange` document, and errors out if it's not available

Since we have a change stream cursor open, we can update our test document and iterate the cursor to see the change this option produces:

```js
db.coll1.update({ _id: 1 }, { $set: { updated_at: new Date() } })
cursor.next()
/*
{
	"operationType" : "update",
	"fullDocumentBeforeChange" : {
		"_id" : 1,
		"created_at" : ISODate("2020-07-15T17:41:32.043Z")
	},
	"ns" : {
		"db" : "test",
		"coll" : "coll1"
	},
	"documentKey" : {
		"_id" : 1
	},
	"updateDescription" : {
		"updatedFields" : {
			"updated_at" : ISODate("2020-07-15T17:41:32.056Z")
		},
		"removedFields" : [ ]
	}
}
*/
```

The output contains a `fullDocumentBeforeChange` field which includes the full document _prior_ to the changes the update operation would apply. As this was the first update to this document and the field was being added for the first time the value here may not be apparent, but running the operation again produces result that contains our previous `created_at` value along with our updated `created_at` value in the `updateDescription`:

```js
db.coll1.update({ _id: 1 }, { $set: { updated_at: new Date() } })
cursor.next()
/*
{
	"operationType" : "update",
	"fullDocumentBeforeChange" : {
		"_id" : 1,
		"created_at" : ISODate("2020-07-15T17:41:32.043Z"),
		"updated_at" : ISODate("2020-07-15T17:41:32.056Z")
	},
	"ns" : {
		"db" : "test",
		"coll" : "coll1"
	},
	"documentKey" : {
		"_id" : 1
	},
	"updateDescription" : {
		"updatedFields" : {
			"updated_at" : ISODate("2020-07-15T17:44:29.494Z")
		},
		"removedFields" : [ ]
	}
}
*/
```

If the `fullDocumentBeforeChange` mode was set to `required` and the collection wasn't created with the `recordPreImages` flag set, the change stream cursor will error out when iterated.

```js
db.coll2.drop();
db.createCollection("coll2");
db.coll2.insert({ _id: 2, created_at: new Date() });
var cursor = db.coll2.aggregate([{
    $changeStream: { fullDocumentBeforeChange: "required" } }
]);
db.coll2.update({ _id: 2 }, { $set: { updated_at: new Date() } })
cursor.next()
/*
2020-07-16T07:03:37.657-0400 E  QUERY    [js] Error: command failed: {
	"ok" : 0,
	"errmsg" : "Change stream was configured to require a pre-image for all update, delete and replace events, but no pre-image optime was recorded for event: {_id: {_data: \"825F103409000000042B022C0100296E5A10044912D5BB665545B48DDAD38FCD774270461E5F6964002B040004\", _typeBits: BinData(0, \"40\")}, operationType: \"update\", clusterTime: Timestamp(1594897417, 4), ns: {db: \"test\", coll: \"coll2\"}, documentKey: {_id: 2}, updateDescription: {updatedFields: {updated_at: 2020-07-16T11:03:37.611Z}, removedFields: []}}",
	"code" : 51770,
}
*/
```

### Pre-Image and `{ fullDocument: "updateLookup" }`

The change stream cursors we've been opening have not been specifying a `fullDocument` options, which results in the default value of `{ fullDocument: "default" }` being used (or prior to [SPEC-909](https://jira.mongodb.org/browse/SPEC-909) a value of `none`).

When we set `{ fullDocument: "updateLookup" }`, the cursor will look up the most current majority-committed version of the updated document and include a `fullDocument` field with the document lookup in addition to the `updateDescription` delta.

```js
db.coll3.drop();
db.createCollection("coll3", { recordPreImages: true });
db.coll3.insert({ _id: 3, name: "Alex", role: "TSE", created_at: new Date() });
var cursor = db.coll3.aggregate([{
    $changeStream: { fullDocument: "updateLookup", fullDocumentBeforeChange: "whenAvailable" } }
]);
db.coll3.update({ _id: 3 }, { $set: { updated_at: new Date() } });
cursor.next()
/*
{
    "_id" : {
        "_data" : "825F103644000000042B022C0100296E5A100452A662230D6B4C08B0AF844900F3A335461E5F6964002B060004",
        "_typeBits" : BinData(0, "QA==")
    },
    "operationType" : "update",
    "clusterTime" : Timestamp(1594897988, 4),
    "fullDocument" : {
        "_id" : 3.0,
        "name" : "Alex",
        "role" : "TSE",
        "created_at" : ISODate("2020-07-16T11:13:08.180+0000"),
        "updated_at" : ISODate("2020-07-16T11:13:08.268+0000")
    },
    "fullDocumentBeforeChange" : {
        "_id" : 3.0,
        "name" : "Alex",
        "role" : "TSE",
        "created_at" : ISODate("2020-07-16T11:13:08.180+0000")
    },
    "ns" : {
        "db" : "test",
        "coll" : "coll3"
    },
    "documentKey" : {
        "_id" : 3.0
    },
    "updateDescription" : {
        "updatedFields" : {
            "updated_at" : ISODate("2020-07-16T11:13:08.268+0000")
        },
        "removedFields" : [

        ]
    }
}
*/
```

By including both `fullDocument` and `fullDocumentBeforeChange` options, the cursor now returns three fields that represent the state of the document before the change, after the change as well as a description of the changes in the form of the `updateDescription` field.

### What Could Go Wrong?

Since change streams are messages in the [oplog](https://docs.mongodb.com/manual/core/replica-set-oplog/), which are themselves [BSON documents](https://docs.mongodb.com/manual/reference/glossary/#term-document)  hey must adhere to the [BSON Document Size](https://docs.mongodb.com/manual/reference/limits/#bson-documents) limit of 16 megabytes.

```js
function randomString(length) {
   var result           = '';
   var characters       = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
   var charactersLength = characters.length;
   for ( var i = 0; i < length; i++ ) {
      result += characters.charAt(Math.floor(Math.random() * charactersLength));
   }
   return result;
}

// BSON max size - 512 bytes
var size = db.serverBuildInfo().maxBsonObjectSize - 512;

db.coll4.drop();
db.createCollection("coll4", { recordPreImages: true });
db.coll4.insert({ _id: 4, created_at: new Date(), junk: randomString(size) });
var cursor = db.coll4.aggregate([{
    $changeStream: { fullDocument: "updateLookup", fullDocumentBeforeChange: "off" } }
]);
db.coll4.update({ _id: 4 }, { $set: { updated_at: new Date() } });
cursor.next()
```

The above example has the `fullDocumentBeforeChange` disabled, which is the current default behavior of change streams. Though the result would be large (almost 16MB), iterating the change stream cursor would produce a result.

Modifying the cursor to now request a `fullDocumentBeforeChange` (either `required` or `whenAvailable`) would now raise an error when the cursor is iterated.

```js
// ...
db.coll4.drop();
db.createCollection("coll4", { recordPreImages: true });
db.coll4.insert({ _id: 4, created_at: new Date(), junk: randomString(size) });
var cursor = db.coll4.aggregate([{
    $changeStream: { fullDocument: "updateLookup", fullDocumentBeforeChange: "required" } }
]);
db.coll4.update({ _id: 4 }, { $set: { updated_at: new Date() } });
cursor.next();
/*
2020-07-16T07:40:38.307-0400 E  QUERY    [js] Error: command failed: {
	"errmsg" : "BSONObj size: 33553900 (0x1FFFDEC) is invalid. Size must be between 0 and 16793600(16MB) First element: _id: { _data: \"825F103CB5000000032B022C0100296E5A100484010E04E239427B8CBCA810283D05A5461E5F6964002B080004\", _typeBits: BinData(0, 40) }",
	"code" : 10334,
	"codeName" : "BSONObjectTooLarge",
}
*/
```

I personally look forward to pre-images being officially supported in MongoDB, however in the meantime be advised that this may not be ideal for production just yet.

Happy Coding!