---
layout: post
title: "Generate MongoDB Index Utilization Report"
date: 2022-01-24 09:49:50 -0500
comments: true
categories: [MongoDB]
tags: [mongodb, queries, indexing]
image:
  src: /images/mongodb-logo.png
  alt: MongoDB Logo
---
When MongoDB 3.2 introduced the [`$indexStats`](https://docs.mongodb.com/manual/reference/operator/aggregation/indexStats/) aggregation pipeline stage [`accesses` details](https://docs.mongodb.com/manual/reference/operator/aggregation/indexStats/#std-label-indexStats-output-accesses) were suddenly accessible to users. As a result, scripts could now be written to better understand how frequently [indexes](https://docs.mongodb.com/manual/indexes/) were being accessed by operations.

The following script will cycle through all databases and collections (omitting `admin`, `local` and `config`) to produce a delimited report of index utilization:

```js
var DELIMITER = '\t';
var IGNORE = ["admin", "local", "config"];
print(["Namespace", "Index Name", "Usage Count", "Last Used", "Index Size (bytes)", "Index Specification"].join(DELIMITER));
db.getMongo().getDBNames().forEach(function (dbname) {
    if (IGNORE.indexOf(dbname) < 0) {
        db.getSiblingDB(dbname).getCollectionNames().forEach(function (cname) {
            if (!cname.includes("system.")) {
                var coll = db.getSiblingDB(dbname).getCollection(cname);
                var stats = coll.stats();
                // make sure stats ran successfully (if it's a view it won't)
                if (stats.ok == 1) {
                    coll.aggregate([{ $indexStats: {} }]).forEach(function (ix) {
                        var ixname = ix.name;
                        var ns = dbname + "." + cname;
                        var ixsize = stats.indexSizes[ixname];
                        var ops = ix.accesses.ops;
                        var since = ix.accesses.since;
                        print([ns, ixname, ops, since, ixsize, JSON.stringify(ix.spec)].join(DELIMITER));
                    });
                }
            }
        });
    }
});
```

For example, I ran the above against a test cluster I have in MongoDB Atlas with a `DELIMITER` set as `|` to facilitate the generation of a Markdown table such as the following:

|Namespace|Index Name|Usage Count|Last Used|Index Size (bytes)|Index Specification|
|---------|----------|----------|-------------------|-----------|---------|
|data.users|age_1_address.state_1_name_1|NumberLong(0)|Tue Jan 18 2022 14:05:40 GMT-0500 (Eastern Standard Time)|48164864|{"v":2,"key":{"age":1,"address.state":1,"name":1},"name":"age_1_address.state_1_name_1","ns":"data.users"}|
|data.users|_id_|NumberLong(0)|Tue Jan 18 2022 14:05:40 GMT-0500 (Eastern Standard Time)|34496512|{"v":2,"key":{"_id":1},"name":"_id_","ns":"data.users"}|
|data.users|address.state_1_name_1_age_1|NumberLong(0)|Tue Jan 18 2022 14:05:40 GMT-0500 (Eastern Standard Time)|43565056|{"v":2,"key":{"address.state":1,"name":1,"age":1},"name":"address.state_1_name_1_age_1","ns":"data.users"}|
|data.users|age_1|NumberLong(0)|Tue Jan 18 2022 14:05:40 GMT-0500 (Eastern Standard Time)|13721600|{"v":2,"key":{"age":1},"name":"age_1","ns":"data.users"}|
|encryption.__keyVault|_id_|NumberLong(0)|Tue Jan 18 2022 14:05:40 GMT-0500 (Eastern Standard Time)|36864|{"v":2,"key":{"_id":1},"name":"_id_"}|
|medicalRecords.patients|_id_|NumberLong(0)|Tue Jan 18 2022 14:05:40 GMT-0500 (Eastern Standard Time)|36864|{"v":2,"key":{"_id":1},"name":"_id_"}|