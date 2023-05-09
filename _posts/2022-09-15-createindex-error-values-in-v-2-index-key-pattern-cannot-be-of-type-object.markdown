---
layout: post
title: "Solving a mongorestore failure due to 'Values in v:2 index key pattern cannot be of type object.'"
date: 2022-09-15 06:47:26 -0400
comments: true
categories: MongoDB
tags: [mongodb, indexing, mongorestore, mongodump]
image: /images/mongodb-logo.png
---

Starting with MongoDB 4.4, the [MongoDB Database Tools](https://www.mongodb.com/docs/database-tools/) are now released separately from the MongoDB Server and use their own versioning, with an initial version of 100.0.0. Previously, these tools were released alongside the MongoDB Server and used matching versioning.

If you use `mongodump` to backup your data using these newer versions, if you try to use an older (pre-4.4) version of `mongorestore` you'll likely get an error such as the following:

```bash
$(m bin 4.0.28-ent)/mongorestore

2022-09-15T07:09:28.775-0400	using default 'dump' directory
2022-09-15T07:09:28.775-0400	preparing collections to restore from
2022-09-15T07:09:28.777-0400	reading metadata for test.foo from dump/test/foo.metadata.json
2022-09-15T07:09:28.777-0400	restoring test.foo from dump/test/foo.bson
2022-09-15T07:09:28.780-0400	restoring indexes for collection test.foo from metadata
2022-09-15T07:09:28.780-0400	Failed: test.foo: error creating indexes for test.foo: createIndex error: Error in specification { ns: "test.foo", name: "baz_1", key: { baz: { $numberDouble: "1.0" } } } :: caused by :: Values in v:2 index key pattern cannot be of type object. Only numbers > 0, numbers < 0, and strings are allowed.
```

In the example above we used the [`m` version manager](https://github.com/aheckmann/m) to try and restore a backup taken using a `mongodump` from a newer version of the database tools. If you see this error, it just means you need to use a newer version of `mongorestore`.

To verify what version of the tools you're using, run them with a `--version` parameter:

```bash
$ $(m bin 4.0.28-ent)/mongorestore --version
mongorestore version: r4.0.28
git version: af1a9dc12adcfa83cc19571cb3faba26eeddac92
Go version: go1.11.13
   os: darwin
   arch: amd64
   compiler: gc

$ mongorestore --version
mongorestore version: 100.6.0
git version: 1d46e6e7021f2f5668763dba624e34bb39208cb0
Go version: go1.17.10
   os: darwin
   arch: amd64
   compiler: gc
```