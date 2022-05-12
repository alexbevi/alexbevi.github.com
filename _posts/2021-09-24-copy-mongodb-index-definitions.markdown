---
layout: post
title: "Copy MongoDB Index Definitions"
date: 2021-09-24 06:24:14 -0400
comments: true
categories: [MongoDB]
tags: [mongodb, indexes, queries]
image:
  src: /images/mongodb-logo.png
  alt: MongoDB Logo
---

To support your application's workload properly, you'll want to ensure you're [creating indexes to support your queries](https://docs.mongodb.com/manual/tutorial/create-indexes-to-support-queries/). When doing this in a development environment, unless the the [Driver or ODM](https://docs.mongodb.com/drivers/) in use allows you to manage index definitions via annotations in code (and you use that feature) it's possible your development cluster's indexes can diverge from that in production.

The following script will allow you to quickly generate all index creation commands for your cluster in a way that can be copy/pasted to another cluster.

```js
function generateCreateIndexesCommands(options) {
  var getIndexName = function(keys) {
    var name = "";
    var keyz = Object.keys(keys);
    for (var k = 0; k < keyz.length; k++) {
      var v = keys[keyz[k]];
      if (typeof v == "function")
        continue;

      if (name.length > 0)
        name += "_";
      name += keyz[k] + "_";

      name += v;
    }

    return name.substring(0, 126);
  };
  if (options === undefined) {
    options = {}
  }
  var truncateIndexName = options["truncateIndexName"] || true;
  var ensureBackground = options["ensureBackground"] || false;

  db.getMongo().getDBNames().filter(x => !["admin", "config", "local"].includes(x)).forEach(function (d) {
    db.getSiblingDB(d).getCollectionNames().forEach(function (c) {
      var keys = db.getSiblingDB(d).getCollection(c).getIndexes();
      var idPosition = -1;
      for (var i = 0; i < keys.length; i++) {
        if (keys[i].name == "_id_") {
          idPosition = i;
        } else {
          keys[i].name = (truncateIndexName) ? getIndexName(keys[i].key) : keys[i].key
          if (ensureBackground) {
            // force all indexes to be created in the background
            keys[i].background = true;
          }
        }
      }
      // remove the { _id: 1 } default index as it will exist already anyway
      keys.splice(idPosition, 1);
      if (keys.length > 0) {
        print("db.getSiblingDB('" + d + "')." + c + ".createIndexes(" + JSON.stringify(keys) + ")");
      }
    });
  })
}
```

The `generateCreateIndexesCommands` function will output all [`createIndexes`](https://docs.mongodb.com/manual/reference/command/createIndexes/) commands for the cluster including all options. The function can optionally be configured using the following parameters (in an object):

* `truncateIndexName`: Limits an index definitions `name` field to less than 128 characters. Prior to MongoDB 4.2 (see [SERVER-32959](https://jira.mongodb.org/browse/SERVER-32959)) this [Index Name Length limitation](https://docs.mongodb.com/v4.2/reference/limits/#Index-Name-Length) existed and under certain circumstances, [compound index](https://docs.mongodb.com/manual/core/index-compound/) auto naming could result in this limit being exceeded. (default: `true`)
* `ensureBackground`: Prior to MongoDB 4.2 (which introduced the [optimized build process](https://docs.mongodb.com/v4.2/core/index-creation/#index-build-process)) indexes could be built in either the foreground or the background. Foreground index builds were fast and produced more efficient index data structures, but required blocking all read-write access to the parent database of the collection being indexed for the duration of the build. Background index builds were slower and had less efficient results, but allowed read-write access to the database and its collections during the build process.<br>This option ensure index definitions contain a `{ background: true }` option in case you want to copy the commands to a MongoDB 4.0 cluster (or earlier) and ensure index builds occur in the background. (default: `false`)

```js
// run with no options
generateCreateIndexesCommands()
// run with options
generateCreateIndexesCommands({ truncateIndexName: true, ensureBackground: true });
```

Running this script will produce output such as the following:

```js
db.getSiblingDB('test').foo.createIndexes([{"v":2,"key":{"a":1,"b":1},"name":"a_1_b_1","background":true},{"v":2,"key":{"key":1},"name":"key_1","collation":{"locale":"en","caseLevel":false,"caseFirst":"off","strength":2,"numericOrdering":false,"alternate":"non-ignorable","maxVariable":"punct","normalization":false,"backwards":false,"version":"57.1"}}])
db.getSiblingDB('test').restaurants.createIndexes([{"v":2,"key":{"cuisine":1,"name":1},"name":"cuisine_1_name_1","partialFilterExpression":{"rating":{"$gt":5}}}])
```

Did this script help you? Do you have any other options you'd like to see added? Let me know in the comments below ... and happy coding ;)