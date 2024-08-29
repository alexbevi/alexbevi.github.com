---
layout: post
title: "Risk of data corruption when using Node v22.7.0 and the MongoDB Node.js driver"
date: 2024-08-29 07:18:44 -0400
comments: true
categories: MongoDB
tags: [mongodb, drivers, javascript, node]
image: /images/mongodb-logo.png
---

Within days of the [Node v22.7.0 release](https://nodejs.org/en/blog/release/v22.7.0), users were already reporting that UTF-8 [encodings were broken](https://github.com/nodejs/node/issues/54543). The issue results from the introduction of an incorrect optimization for `buffer.write` which can result in strings being encoded using ISO-8859-1 rather than UTF-8.

Though the use of the fast API for `buffer.write` [will be disabled](https://github.com/nodejs/node/pull/54565) with Node v22.8.0, developers using MongoDB’s Node.js driver could experience data corruption with Node v22.7.0.

## Mitigating the Issue

To avoid the possibility of data corruption due to this bug it is recommended that Node v22.7.0 **is not used at all.**

MongoDB recommends only using Node runtime versions [documented as compatible](https://www.mongodb.com/docs/drivers/node/current/compatibility/#language-compatibility) in production environments. At the time of writing, Node v22.x is not considered a compatible runtime for use with the MongoDB Node.js driver.

## How it Occurs

To illustrate how this can occur, consider the following reproduction:

```javascript
import { MongoClient } from "mongodb";

const client = new MongoClient("mongodb://...");
const value = 'bébé';

async function run() {
  try {
    console.log(`Running Node ${process.versions.node}`);
    const coll = client.db("test").collection("foo");
    await coll.drop();

    let i = 0;
    while (Buffer.from(value).length === 6 && i < 20000) { i++ }

    await coll.insertOne({ _id: 1, message: value });
    const doc = await coll.findOne({ _id: 1 });
    console.log(`Found doc ${JSON.stringify(doc)}`);
  } finally {
    await client.close();
  }
}
run().catch(console.dir);
```

When run using a previous version of Node, the `Buffer` length is consistently evaluated for 20K iterations, a document is inserted into a MongoDB collection then successfully retrieved.

```
Running Node 22.6.0
Found doc {"_id":1,"message":"bébé"}
```

When the same reproduction is run using Node v22.7.0 however, invalid UTF-8 string data can be produced, which would then be inserted into the MongoDB collection, resulting in subsequent retrieval attempts failing.

```
Running Node 22.7.0
BSONError: Invalid UTF-8 string in BSON document
    at parseUtf8 (/Users/alex/temp/test-node/node_modules/bson/lib/bson.cjs:148:19)
    at Object.toUTF8 (/Users/alex/temp/test-node/node_modules/bson/lib/bson.cjs:273:21)
    ... 6 lines matching cause stack trace ...
    at process.processTicksAndRejections (node:internal/process/task_queues:105:5)
    at async Collection.findOne (/Users/alex/temp/test-node/node_modules/mongodb/lib/collection.js:274:21) {
  [cause]: TypeError: The encoded data was not valid for encoding utf-8
      at TextDecoder.decode (node:internal/encoding:443:16)
      at parseUtf8 (/Users/alex/temp/test-node/node_modules/bson/lib/bson.cjs:145:37)
      at Object.toUTF8 (/Users/alex/temp/test-node/node_modules/bson/lib/bson.cjs:273:21)
      at deserializeObject (/Users/alex/temp/test-node/node_modules/bson/lib/bson.cjs:2952:31)
      at internalDeserialize (/Users/alex/temp/test-node/node_modules/bson/lib/bson.cjs:2863:12)
      at Object.deserialize (/Users/alex/temp/test-node/node_modules/bson/lib/bson.cjs:4335:12)
      at OnDemandDocument.toObject (/Users/alex/temp/test-node/node_modules/mongodb/lib/cmap/wire_protocol/on_demand/document.js:208:28)
      at CursorResponse.shift (/Users/alex/temp/test-node/node_modules/mongodb/lib/cmap/wire_protocol/responses.js:207:35)
      at FindCursor.next (/Users/alex/temp/test-node/node_modules/mongodb/lib/cursor/abstract_cursor.js:222:41)
      at process.processTicksAndRejections (node:internal/process/task_queues:105:5) {
    code: 'ERR_ENCODING_INVALID_ENCODED_DATA'
  }
}
```

Though MongoDB’s Node.js driver supports [UTF-8 validation](https://www.mongodb.com/docs/drivers/node/current/fundamentals/bson/utf8-validation/), that feature applies to *decoding* BSON strings that are being received from the MongoDB server. As the bug in Node v22.7.0 occurs when *encoding* strings as UTF-8, the invalid data can still be serialized to BSON and written to the database.