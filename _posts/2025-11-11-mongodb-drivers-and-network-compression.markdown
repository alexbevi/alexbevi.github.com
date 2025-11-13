---
layout: post
title: "MongoDB Drivers and Network Compression"
date: 2025-11-11 16:44:22 -0500
comments: true
categories: MongoDB
tags: [mongodb, drivers, networking, compression]
image: /images/mongodb-compression.png
---

MongoDB's drivers communicate with a MongoDB process using the [Wire Protocol](https://www.mongodb.com/docs/manual/reference/mongodb-wire-protocol), which is a simple socket-based, request-response style protocol that primarily uses the [`OP_MSG`](https://www.mongodb.com/docs/manual/reference/mongodb-wire-protocol/#op_msg) opcode (though [prior to MongoDB 6.0](https://www.mongodb.com/docs/v6.0/release-notes/6.0-compatibility/#std-label-legacy-op-codes-removed) there were a number of addition [legacy opcodes](https://www.mongodb.com/docs/manual/legacy-opcodes)). Since the contents of `OP_MSG` messages was uncompressed, starting with MongoDB 3.4 a new opcode was introduced that would enable the Wire Protocol to support compressed messages as well: [`OP_COMPRESSED`](https://www.mongodb.com/docs/manual/reference/mongodb-wire-protocol/#op_compressed).

All official [MongoDB drivers](https://www.mongodb.com/docs/drivers/) allow you to enable and configure [compression options](https://www.mongodb.com/docs/manual/reference/connection-string-options/#compression-options) via the connection string. To use any of the available compressors, they'd need to first be [enabled for each `mongod` or `mongos` instance through the `net.compression.compressors` option](https://www.mongodb.com/docs/manual/reference/configuration-options/#mongodb-setting-net.compression.compressors), however all compressors are currently enabled by default, so you'd really only need to modify this to remove support for a given compressor.

Enabling network compression for your workload is as easy as appending `compressors=xxx` (where `xxx` is one or more compressors as comma-separated values) to your connection string. For every `MongoClient` created with this connection string, _almost all_[^1] database commands will be compressed, which can result in massive reductions in the amount of data that needs to be sent back and forth to a MongoDB process.

As a simple demonstration, I've instrumented a Node.js-based workload (see [alexbevi/node-tcp-metrics](https://github.com/alexbevi/node-tcp-metrics)) to hook into [`net.createConnection()`](https://nodejs.org/api/net.html#netcreateconnection), [`net.Server`](https://nodejs.org/api/net.html#class-netserver) and [`tls.connect()`](https://nodejs.org/api/tls.html#tlsconnectoptions-callback) to track the number of bytes being sent/received:

```js
import "./tcp-metrics.js";

import { on } from "./tcp-metrics.js";
import { MongoClient } from "mongodb";
import Chance from "chance";

const uri = process.env.MONGODB_URI;
if (!uri) {
  throw new Error("MONGODB_URI environment variable is not set");
}
const client = new MongoClient(uri);
const delay = (ms: number): Promise<void> => new Promise(res => setTimeout(res, ms));

(async () => {
  try {
    await client.connect();
    const db = client.db("testdb");
    const collection = db.collection<{ _id: string; data: string }>("testcollection");
    const chance = new Chance(42); // Fixed seed for deterministic generation

    // Generate a complex document structure that's approximately 5MB
    const itemCount = 5000; // Adjust to control size
    const payload = {
      users: Array.from({ length: itemCount }, (_, i) => ({
      id: i,
      name: chance.name(),
      email: chance.email(),
      address: {
        street: chance.address(),
        city: chance.city(),
        state: chance.state(),
        zip: chance.zip(),
        country: chance.country()
      },
      phone: chance.phone(),
      company: chance.company(),
      bio: chance.paragraph({ sentences: 5 }),
      avatar: chance.url(),
      tags: Array.from({ length: 10 }, () => chance.word()),
      metadata: {
        createdAt: chance.date().toISOString(),
        lastLogin: chance.timestamp(),
        preferences: {
        theme: chance.pickone(['dark', 'light', 'auto']),
        language: chance.locale(),
        notifications: chance.bool()
        }
      }
      }))
    };
    const doc: any = { _id: "large-doc", ...payload };

    await collection.insertOne(doc);
    const result = await collection.findOne({ _id: "large-doc" });

    const buf = Buffer.from(JSON.stringify(result));
    console.log("Document insert and read complete, doc size (bytes):", buf.length);

    await collection.deleteOne({ _id: "large-doc" });
  } catch (err) {
    console.error("MongoDB error:", err);
  } finally {
    await client.close();
 }
})();

on("socketSummary", (s) => console.log(s));
```

When this is run, the workload will create a complex JSON document using [Chance](https://chancejs.com/), write it to a [MongoDB Atlas Database](https://www.mongodb.com/products/platform/atlas-database), then read it back before deleting it.

```bash
$ MONGODB_URI="mongodb+srv://USER:PASS@abc.cdefg.mongodb.net/" npm run dev

Document insert and read complete, doc size (bytes): 4725754
{ rx: 5058704, tx: 5058304, label: 'xxx.yyy.zzz.108:27017' }
{ rx: 1093, tx: 523, label: 'xxx.yyy.zzz.101:27017' }
{ rx: 1093, tx: 523, label: 'xxx.yyy.zzz.116:27017' }
{ rx: 1117, tx: 523, label: 'xxx.yyy.zzz.108:27017' }
```

> There are 4 open sockets in the example as the default Atlas configuration is a 3 member [replica set](https://www.mongodb.com/docs/manual/replication/). The driver has opened one socket to send commands to the server, and has also created dedicated monitoring connections to each host. If the workload were to remain active and not exit immediately, another 3 RTT connections would also be opened (one to each host in the replica set) for a total of 7 sockets. \
> See the [Server Monitoring specification](https://github.com/mongodb/specifications/blob/master/source/server-discovery-and-monitoring/server-monitoring.md), or ["How Many Connections is My Application Establishing to My MongoDB Cluster?"]({% post_url 2023-07-04-how-many-connections-is-my-application-establishing-to-my-mongodb-cluster %}) for more detail.
{: .prompt-info }

MongoDB supports 3 possible network compressors: [zlib](https://zlib.net/), ZStandard ([zstd](https://facebook.github.io/zstd/)) and [Snappy](https://google.github.io/snappy/). zlib is always supported out of the box, however some drivers may require an additional package to support additional compressors. For example, when using MongoDB's [Node.js driver](https://www.mongodb.com/docs/drivers/node/current/), the following would be required from `npm` to support snappy and zstd:

* [`snappy`](https://www.npmjs.com/package/snappy)
* [`@mongodb-js/zstd`](https://www.npmjs.com/package/@mongodb-js/zstd)

Our workload is using the default [read preference](https://www.mongodb.com/docs/manual/core/read-preference/), so with a baseline of `rx: 5058704, tx: 5058304` being sent to and received from the [replica set primary](https://www.mongodb.com/docs/manual/core/replica-set-primary/), let's explore the impact of network compression.

### zlib

zlib is a software library used for data compression as well as a data format. zlib was written by Jean-loup Gailly and Mark Adler and implements the DEFLATE compression algorithm used in their gzip file compression program. The first public version of Zlib, 0.9, was released on 1 May 1995 and was originally intended for use with the libpng image library. It is free software, distributed under the zlib License.

To test this compressor we append `compressors=zlib` to our connection string and re-run our script.

```bash
$ MONGODB_URI="mongodb+srv://USER:PASS@abc.cdefg.mongodb.net/?compressors=zlib" npm run dev

Document insert and read complete, doc size (bytes): 4725754
{ rx: 2417301, tx: 2361623, label: 'xxx.yyy.zzz.108:27017' }
{ rx: 1147, tx: 515, label: 'xxx.yyy.zzz.108:27017' }
{ rx: 1123, tx: 518, label: 'xxx.yyy.zzz.101:27017' }
{ rx: 1123, tx: 518, label: 'xxx.yyy.zzz.116:27017' }
```

With `zlib` compression enabled we can see about a **52% decrease** in the amount of data sent over the wire for this workload:

```
uncompressed:      rx: 5058704, tx: 5058304
compressed (zlib): rx: 2417301, tx: 2361623
```

### ZStandard (zstd)

Zstandard is a lossless data compression algorithm developed by Yann Collet at Facebook. Zstd is the corresponding reference implementation in C, released as open-source software on 31 August 2016. The algorithm was published in 2018 as RFC 8478, which also defines an associated media type "application/zstd", filename extension "zst", and HTTP content encoding "zstd".

To test this compressor we append `compressors=zstd` to our connection string and re-run our script.

```bash
$ MONGODB_URI="mongodb+srv://USER:PASS@abc.cdefg.mongodb.net/?compressors=zstd" npm run dev

Document insert and read complete, doc size (bytes): 4725754
{ rx: 2395239, tx: 2394798, label: 'xxx.yyy.zzz.108:27017' }
{ rx: 1147, tx: 519, label: 'xxx.yyy.zzz.108:27017' }
{ rx: 1123, tx: 519, label: 'xxx.yyy.zzz.101:27017' }
{ rx: 1123, tx: 519, label: 'xxx.yyy.zzz.116:27017' }
```

With `zstd` compression enabled we can see about a **53% decrease** in the amount of data sent over the wire for this workload:

```
uncompressed:      rx: 5058704, tx: 5058304
compressed (zstd): rx: 2395239, tx: 2394798
```

### Snappy

Snappy (previously known as Zippy) is a fast data compression and decompression library written in C++ by Google based on ideas from LZ77 and open-sourced in 2011. It does not aim for maximum compression, or compatibility with any other compression library; instead, it aims for very high speeds and reasonable compression. Compression speed is 250 MB/s and decompression speed is 500 MB/s using a single core of a circa 2011 "Westmere" 2.26 GHz Core i7 processor running in 64-bit mode. The compression ratio is 20–100% lower than gzip.

To test this compressor we append `compressors=snappy` to our connection string and re-run our script.

```bash
$ MONGODB_URI="mongodb+srv://USER:PASS@abc.cdefg.mongodb.net/?compressors=snappy" npm run dev

Document insert and read complete, doc size (bytes): 4725754
{ rx: 1125, tx: 527, label: 'xxx.yyy.zzz.116:27017' }
{ rx: 3807095, tx: 3797837, label: 'xxx.yyy.zzz.108:27017' }
{ rx: 1149, tx: 527, label: 'xxx.yyy.zzz.108:27017' }
{ rx: 1125, tx: 527, label: 'xxx.yyy.zzz.101:27017' }
```

With `snappy` compression enabled we can see about a **25% decrease** in the amount of data sent over the wire for this workload:

```
uncompressed:        rx: 5058704, tx: 5058304
compressed (snappy): rx: 3807095, tx: 3797837
```

## Summary

Though there may be a need for an additional dependency, Zstandard compression is likely the best option as it will provide good compression with a low memory footprint. For Node.js specifically this requirement will likely go away once the driver's minimum runtime version rises to Node 24 as [zstd support was added in 23.8.0](https://nodejs.org/en/blog/release/v23.8.0#support-for-the-zstd-compression-algorithm).

If you're running your workload in AWS (or anywhere really), [data transfer costs](https://aws.amazon.com/blogs/architecture/overview-of-data-transfer-costs-for-common-architectures/) will contribute to your overall costs. You can use tools like the [AWS pricing calculator](https://calculator.aws) to dig into cost projections, but given you can potentially slash those in half (at least for the data going to/from your cluster) with a simple connection string update it makes MongoDB a more cost-effective option for your application.


----

[^1]: <small>Per the [Wire Compression specification](https://github.com/mongodb/specifications/blob/master/source/compression/OP_COMPRESSED.md#messages-not-allowed-to-be-compressed), some commands should not be compressed. These include `hello`/`ismaster`, `saslStart`, `saslContinue`, `getnonce`, `authenticate`, `createUser`, `updateUser`, `copydbSaslStart`, `copydbgetnonce` and `copydb`.</small>