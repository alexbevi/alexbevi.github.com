---
layout: post
title: "Retryable Writes, findAndModify and the impact on the MongoDB Oplog"
date: 2021-08-23 15:18:09 -0400
comments: true
categories: MongoDB
tags: [mongodb, replication]
---

![](/images/retrywrites6.png)

When you're monitoring your cluster using [Ops Manager](https://www.mongodb.com/products/ops-manager) or [MongoDB Atlas](https://docs.atlas.mongodb.com/reference/alert-resolutions/replication-oplog/) and the [`Replication Oplog Window is (X)`](https://docs.atlas.mongodb.com/reference/alert-conditions/#mongodb-alert-Replication-Oplog-Window-is) drastically drops, what can you do?

Having a very short [operations log (oplog)](https://docs.mongodb.com/manual/core/replica-set-oplog/) window increases the likelihood that a SECONDARY member can fall off the oplog an require a full resync, however if the window remains small the resync may fail as the oplog window must be larger than the time needed to resync.

One scenario that can result in the oplog window shrinking is the use of `findAndModify` operations when retryable writes are enabled, but how do we identify that they are the culprit?

## Overview

MongoDB introduced [Retryable Writes](https://docs.mongodb.com/manual/core/retryable-writes/) in 3.6 as a way to allow [Drivers](https://docs.mongodb.com/drivers/) (that have implemented the [Retryable Write specification](https://github.com/mongodb/specifications/blob/master/source/retryable-writes/retryable-writes.rst)) a mechanism to retry certain write operations a single time if they encounter network errors, or if they cannot find a healthy primary in the replica sets or sharded cluster.

When the [`findAndModify`](https://docs.mongodb.com/manual/reference/command/findAndModify/) command was made retryable (via [SERVER-30407](https://jira.mongodb.org/browse/SERVER-30407)), the implementation involved writing an additional no-op to the oplog that would contain a pre (or post) image of an update (or delete) operation.

Prior to MongoDB 4.4, the [oplog size](https://docs.mongodb.com/manual/core/replica-set-oplog/#oplog-size) was configured in megabytes. As it is a [capped collection](https://docs.mongodb.com/manual/core/capped-collections/), once the configured size was filled the oldest entries were removed as new entries were written.

With MongoDB 4.4 an option was added to configure a [minimum oplog retention period (in hours)](https://docs.mongodb.com/manual/core/replica-set-oplog/#minimum-oplog-retention-period), however this is not presently the default behavior when configuring a replica set.

In this article we'll be exploring the impact of retryable `findAndModify` operations on a local MongoDB 5.0.2 replica set running a Ruby script (see _Appendix_).

## Retryable Writes enabled

With the series of MongoDB Drivers that support MongoDB 4.2 [Retryable Writes are enabled by default](https://docs.mongodb.com/manual/release-notes/4.2-compatibility/#4.2-drivers-enable-retryable-writes-by-default), however setting the [`retryWrites`](https://docs.mongodb.com/manual/reference/connection-string/#mongodb-urioption-urioption.retryWrites) URI option can still be used to explicitly toggle this feature.

![](/images/retrywrites1.png)

When the script is run for the first time it will update the document configured during setup (see _Appendix_) and increment a value 300 times.

Before the script runs the first event time (in the oplog) is `2021-08-23 11:31:38`. After the script runs, the first event time is `2021-08-23 11:32:39`. As our oplog is configured at 990MB this would imply MORE than 990MB were written as the oldest events appear to start _after_ the script began.

As a result, the oplog has fully churned during the course of this script running.

The sample document we're incrementing a value on is 5MB, and if we're running 300 updates approximately 1.5GB of uncompressed would have been written to the oplog.

## Retryable Writes disabled

![](/images/retrywrites2.png)

For this test run the application was modified to disable `retryWrites` from the connection string:

```ruby
# ...
client = Mongo::Client.new("mongodb://localhost:27017/?retryWrites=false")
# ...
```

As retryable writes are disabled there is no pre/post-image data being written to the oplog. This can be seen in the first event times being the same before and after the script runs (`2021-08-23 11:32:39`).

**NOTE**: For Atlas clusters where `setParameter` is an [Unsupported Command](https://docs.atlas.mongodb.com/reference/unsupported-commands/#unsupported-commands), disabling retryable writes or refactoring the `findAndModify` to instead perform a `find` followed by an `update` would be the best paths forward.

## Server Parameters and Retryable Writes

As a result of the impact on the oplog when using `findAndModify`, [SERVER-56372](https://jira.mongodb.org/browse/SERVER-56372) was created to allow the pre/post-image storage to be moved to a non-oplog collection.

**This functionality is available in MongoDB 5.0+, and was backported to MongoDB 4.4.7 and MongoDB 4.2.15.**

To enable this functionality two (currently undocumented) [Server Parameters](https://docs.mongodb.com/manual/reference/parameters/) must be enabled at startup using the [`setParameter`](https://docs.mongodb.com/manual/reference/command/setParameter/) command as follows:

```bash
mongod <.. other options ..> \
  --setParameter featureFlagRetryableFindAndModify=true \
  --setParameter storeFindAndModifyImagesInSideCollection=true
```

These parameters would need to be set on each `mongod` node in the cluster. By doing this the pre/post-images will instead be saved to the `config.image_collection` namespace.

![](/images/retrywrites3.png)

When the script is run now with retryable writes enabled, the impact on the oplog should be as negligible as it was when `retryWrites=false` was set previously.

For those that are curious, the `config.image_collection` namespace contains documents such as the following:

![](/images/retrywrites5.png)

(Due to the size of the `data` field it's been projected out)

## Conclusion

If your applications are using `findAndModify` heavily and your cluster's oplog is churning, there are a number of options to consider:

1. Disable retryable writes (`retryWrites=false` in the connection string)
2. Split the `findAndModify` operations into `find` and `update` operations
3. Configure `featureFlagRetryableFindAndModify` and `storeFindAndModifyImagesInSideCollection` (assuming your version of MongoDB is 4.2.15+, 4.4.7+ or 5.0+)

Let me know if you found this article useful in the comments below.

Happy Coding!

## Appendix

The test script and steps to configure a local cluster are below if you want to validate the findings in this article yourself.

### Setup

We'll be using [`m`](https://github.com/aheckmann/m) and [`mtools`](https://github.com/rueckstiess/mtools) to setup the cluster, along with a Javascript script to automate configuration.

```bash
# download and install MongoDB 5.0.2 enterprise
m 5.0.2-ent
# initialize a 3 node replicaset using MongoDB 5.0.2
mlaunch init --replicaset --nodes 3 --binarypath $(m bin 5.0.2-ent)
# wait about 30 seconds before running the script
mongo setup.js
```

The contents of the `setup.js` script above are:
```js
function generate_random_data(size){
    var chars = 'abcdefghijklmnopqrstuvwxyz'.split('');
    var len = chars.length;
    var random_data = [];
    while (size--) { random_data.push(chars[Math.random()*len | 0]); }
    return random_data.join('');
}

function setup() {
  // setup oplog with the minimum size of 990MB
  db.adminCommand({ replSetResizeOplog: 1, size: 990 })
  db.foo.drop();
  // setup 1 document with 5MB of junk data
  db.foo.insertOne({ _id: 1, pos: 1, data: generate_random_data(5 * 1024 * 1024) })
}

setup();
```

The `test.foo` namespace is being setup with a single document that contains 5MB of junk data and a `pos` field we'll be incrementing via the script below.

### Test Script

We'll be using a standalone Ruby script that uses the latest [MongoDB Ruby Driver](https://docs.mongodb.com/ruby-driver/v2.15/) (version 2.15 at time of writing).

At a high level, the script does the following:

1. Connect to the cluster
2. Print replication info
3. Using `findAndModify` increment (via [`$inc`](https://docs.mongodb.com/manual/reference/operator/update/inc/)) a value 300 times
4. Print replication info again

This script (see below) can be executed as follows:

```bash
ruby test.rb
```

```ruby
# !/usr/bin/env ruby
#
# filename: test.rb
#
require "bundler/inline"
gemfile do
  source "https://rubygems.org"
  gem "mongo"
  gem "progress_bar"
end

def get_seconds(ts)
  (ts.seconds && ts.increment) ? ts.seconds : ts / 4294967296 # low 32 bits are ordinal #s within a second
end

def get_replication_info(client)
  db = client.use(:local).database
  olStats = db.command({ collStats: "oplog.rs" }).documents.first
  logSizeMB = olStats["maxSize"] / (1024 * 1024)
  usedMB = olStats["size"] / (1024 * 1024)

  coll = db["oplog.rs"]
  first = coll.find.sort("$natural": 1).first
  last = coll.find.sort("$natural": -1).first

  tfirst = get_seconds(first["ts"])
  tlast = get_seconds(last["ts"])
  timeDiff = tlast - tfirst
  timeDiffHours = ((timeDiff / 36) / 100).round

  puts "configured oplog size:   #{logSizeMB}MB\n"
  puts "log length start to end: #{timeDiff}secs (#{timeDiffHours}hrs)\n"
  puts "oplog first event time:  #{Time.at(tfirst)}\n"
  puts "oplog last event time:   #{Time.at(tlast)}\n"
  puts "now:                     #{Time.now}\n"
end

def update_docs_with_junk(coll)
  coll.find_one_and_update({ _id: 1 }, { "$inc": { pos: 1 } })
end

def print_field_value(coll)
  v = coll.find(_id: 1).first["pos"]
  puts "value of pos: #{v}\n"
end

client = Mongo::Client.new("mongodb://localhost:27017/?retryWrites=true")
puts get_replication_info(client)

coll = client.use(:test).database[:foo]
print_field_value(coll)

max = 300
pb = ProgressBar.new(max)
max.times do
  pb.increment!
  update_docs_with_junk(coll)
end

print_field_value(coll)
puts get_replication_info(client)
```
