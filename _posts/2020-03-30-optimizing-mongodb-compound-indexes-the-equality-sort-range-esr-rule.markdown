---
title: "Optimizing MongoDB Compound Indexes - The \"Equality - Sort - Range\" (ESR) Rule"
date: 2020-05-16 07:35:11 -0400
comments: true
published: true
categories: [MongoDB, "Queries & Indexing"]
tags: [mongodb]
pin: true
image: /images/mongodb-logo.png
---


> **UPDATE**
>
> [DOCS-11790](https://jira.mongodb.org/browse/DOCS-11790) has finally been implemented and as a result the MongoDB public documentation now contains a tutorial for [The ESR (Equality, Sort, Range) Rule](https://www.mongodb.com/docs/manual/tutorial/equality-sort-range-rule)!
{: .prompt-info }

Working in Technical Services at MongoDB I find that time and again customers need assistance understanding why the operations they've created [indexes](https://docs.mongodb.com/manual/indexes/) for may not be performing optimally. When providing supplementary documentation, the go-to article is ["Optimizing MongoDB Compound Indexes"](https://emptysqua.re/blog/optimizing-mongodb-compound-indexes/) by MongoDB's [A. Jesse Jiryu Davis](https://emptysqua.re/blog/about/).

I've presented this topic now at [MongoDB.local Toronto 2019](https://mongodblocaltoronto2019.sched.com/event/VCf3/tips-and-tricks-for-effective-indexing-mongodb) (in ["Tips and Tricks for Effective Indexing"](https://www.slideshare.net/mongodb/mongodb-local-toronto-2019-tips-and-tricks-for-effective-indexing)) and at [MongoDB World 2019](https://mongodbworld2019.sched.com/event/OCX7/the-sights-and-smells-of-a-bad-query-mongodb) (in ["The Sights (and Smells) of a Bad Query"](https://www.slideshare.net/mongodb/mongodb-world-2019-the-sights-and-smells-of-a-bad-query)). My colleague [Chris Harris](https://www.linkedin.com/in/christopher-harris-483aa149/) has also covered this topic at MongoDB World 2019 (in ["Tips and Tricks++ for Querying and Indexing MongoDB"](https://www.slideshare.net/mongodb/mongodb-world-2019-tips-and-tricks-for-querying-and-indexing-mongodb)) and again at the MongoDB.local Houston 2019, for which [a video is available](https://www.youtube.com/watch?v=5mBY27wVau0&list=PL4RCxklHWZ9u_xtprouvxCvzq2m6q_0_E&index=9&t=0s).

Though we have Jesse's excellent (and still applicable and valid) article from 2012, I wanted to take this opportunity to collect some thoughts on this topic based on his work and previous presentations.

## The ESR "Rule"

The ordering of index keys in a compound index is critically important, and the ESR "Rule" can be used as a rule of thumb to identify the optimal order _in most cases_.

The reason we are putting "Rule" in quotations is because, though the guidance is applicable in most cases, there are exceptions to be aware of. These exceptions are covered in greater detail in my in ["Tips and Tricks for Effective Indexing"](https://www.slideshare.net/mongodb/mongodb-local-toronto-2019-tips-and-tricks-for-effective-indexing) presentation.

### The "Rules"

<!-- more -->

(1) _**Equality**_ predicates should be placed first

An equality predicate is any filter condition that is attempting to match a value _exactly_. For example:

```js
find({ x: 123 })
find({ x: { $eq: 123 } })
aggregate([ { $match:{ "x.y": 123 } } ])
```

These filters will be tightly bound when seen in the `indexBounds` of an [Explain Plan](https://docs.mongodb.com/manual/reference/explain-results/#explain-output):

```js
"indexBounds" : {
    "x" : [
        "[123.0, 123.0]"
    ]
}
```

Note that _multiple equality predicates **do not** have to be ordered from most selective to least selective_. This guidance has been provided in the past however it is erroneous due to the nature of B-Tree indexes and how in leaf pages, a B-Tree will store combinations of all field’s values. As such, _there is exactly the same number of combinations regardless of key order_.

(2) _**Sort**_ predicates follow _Equality_ predicates
Sort predicates represent the entire requested sort for the operation and determine the ordering of results. For example:

```js
find().sort({ a: 1 })
find().sort({ b: -1, a: 1 })
aggregate([ { $sort: { b: 1 } } ])
```

A sort predicate will be _unbounded_ as it requires the entire key range to be scanned to satisfy the sort requirements:

```js
"indexBounds" : {
    "b" : [
        "[MaxKey, MinKey]"
    ],
    "a" : [
        "[MinKey, MaxKey]"
    ]
}
```

(3) _**Range**_ predicates follow _Equality_ and _Sort_ predicates

Range predicates are filters that may scan multiple keys as they _are not_ testing for an exact match. For example:

```js
find({ z: { $gte: 5} })
find({ z: { $lt: 10 } })
find({ z: { $ne: null } })
```

The range predicates will be _loosely bounded_ as a subset of the key range will need to be scanned to satisfy the filter requirements:

```js
"indexBounds" : {
    "z" : [
        "[5.0, inf.0]"
    ]
}
"indexBounds" : {
    "z" : [
        "[-inf.0, 10.0)"
    ]
}
"indexBounds" : {
    "z" : [
        "[MinKey, undefined)",
        "(null, MaxKey]"
    ]
}
```

These three tenets of the "rule" have to do with how a query will traverse an index to identify the keys that match the query’s filter and sort criteria.

### Setup

For the duration of this section we’ll be working with the following data to help illustrate the various guiding principles:

```js
{ name: "Shakir", location: "Ottawa",    region: "AMER", joined: 2015 }
{ name: "Chris",  location: "Austin",    region: "AMER", joined: 2016 }
{ name: "III",    location: "Sydney",    region: "APAC", joined: 2016 }
{ name: "Miguel", location: "Barcelona", region: "EMEA", joined: 2017 }
{ name: "Alex",   location: "Toronto",   region: "AMER", joined: 2018 }
```

We will also be examining simplified (filtered) Explain Plan’s [`executionStats`](https://docs.mongodb.com/manual/reference/explain-results/#executionstats) from each operation using a variation of the following command:

```js
find({ ... }).sort({ ... }).explain("executionStats").executionStats
```

### (E) _Equality_ First

When [creating queries that ensure selectivity](https://docs.mongodb.com/manual/tutorial/create-queries-that-ensure-selectivity/), we learn that "selectivity" is the ability of a query to narrow results using the index. Effective indexes are more selective and allow MongoDB to use the index for a larger portion of the work associated with fulfilling the query.

_Equality_ fields should always form the prefix for the index to ensure selectivity.

### (E → S) _Equality_ before _Sort_

Placing _Sort_ predicates after sequential _Equality_ keys allow for the index to:

* Provide a non-blocking sort.
* Minimize the amount of scanning required.

To better understand why this is we will begin with the following example:

```js
// operation
createIndex({ name: 1, region: 1 })
find({ region: "AMER" }).sort({ name: 1 })
```

With the _Sort_ predicate first, the full key range would have to be scanned prior to the more selective equality filter being applied:

```js
// execution stats
"nReturned" : 3.0,
"totalKeysExamined" : 5.0,
"totalDocsExamined" : 5.0,
"executionStages" : {
    ...
    "inputStage" : {
        "stage" : "IXSCAN",
        ...
        "indexBounds" : {
            "name" : [
                "[MinKey, MaxKey]"
            ],
            "region" : [
                "[MinKey, MaxKey]"
            ]
        },
```

![](/images/esr01.png)

With this index, all 5 keys have to be scanned (`totalKeysExamined`) to identify the 3 matching documents (`nReturned`).

```js
// operation
createIndex({ region: 1, name: 1 })
find({ region: "AMER" }).sort({ name: 1 })
```

With the _Equality_ predict first, the tight bounds allow less keys to be scanned to satisfy the filter criteria:

```js
// execution stats
"nReturned" : 3.0,
"totalKeysExamined" : 3.0,
"totalDocsExamined" : 3.0,
"executionStages" : {
    ...
    "inputStage" : {
        "stage" : "IXSCAN",
        ...
        "indexBounds" : {
            "region" : [
                "[\"AMER\", \"AMER\"]"
            ],
            "name" : [
                "[MinKey, MaxKey]"
            ]
        },
```

![](/images/esr02.png)

### (E → R) _Equality_ before _Range_

Though _Range_ predicates scan a subset of keys (unlike _Sort_ predicates), they should still be placed after Equality predicates to ensure the key ordering is optimized for selectivity.

```js
// operation
createIndex({ joined: 1, region: 1 })
find({ region: "AMER", joined: { $gt: 2015 } })
```

Having the _Range_ before the _Equality_ predicate causes more keys to be scanned to identify the matching documents:

```js
// execution stats
"nReturned" : 2.0,
"totalKeysExamined" : 4.0,
"totalDocsExamined" : 2.0,
"executionStages" : {
    ...
    "inputStage" : {
        "stage" : "IXSCAN",
        ...
        "indexBounds" : {
            "joined" : [
                "(2015.0, inf.0]"
            ],
            "region" : [
                "[\"AMER\", \"AMER\"]"
            ]
        },
```

![](/images/esr03.png)

In this example, 4 keys had to be scanned to identify the 2 matches. Changing the order of the keys to place the Equality predicate first will reduce the amount of scanning required:

```js
// operation
createIndex({ region: 1, joined: 1 })
find({ region: "AMER", joined: { $gt: 2015 } })
```

```js
// execution stats
"nReturned" : 2.0,
"totalKeysExamined" : 2.0,
"totalDocsExamined" : 2.0,
"executionStages" : {
    ...
    "inputStage" : {
        "stage" : "IXSCAN",
        ...
        "indexBounds" : {
            "region" : [
                "[\"AMER\", \"AMER\"]"
            ],
            "joined" : [
                "(2015.0, inf.0]"
            ]
        },
```

![](/images/esr04.png)

After placing the _Equality_ predicate before the _Range_ predicate, only the number of keys necessary to satisfy the filter criteria are scanned.

### (S → R) _Sort_ before _Range_

Having a _Range_ predicate before the _Sort_ can result in a Blocking (In Memory) Sort being performed as the [index cannot be used to satisfy the sort criteria](https://docs.mongodb.com/manual/tutorial/sort-results-with-indexes/).

```js
// operation
createIndex({ joined: 1, region: 1 })
find({ joined: { $gt: 2015 } }).sort({ region: 1 })
```

```js
// execution stats
"nReturned" : 4.0,
"totalKeysExamined" : 4.0,
"totalDocsExamined" : 4.0,
"executionStages" : {
    ...
    "inputStage" : {
        "stage" : "SORT",
        ...
        "sortPattern" : {
            "region" : 1.0
        },
        "memUsage" : 136.0,
        "memLimit" : 33554432.0,
        "inputStage" : {
            "stage" : "SORT_KEY_GENERATOR",
            ...
            "inputStage" : {
                "stage" : "IXSCAN",
                ...
                "indexBounds" : {
                    "joined" : [
                        "(2015.0, inf.0]"
                    ],
                    "region" : [
                        "[MinKey, MaxKey]"
                    ]
                },
```

![](/images/esr05.png)

In this example, the filter was able to use the index selectively to identify the 4 keys needed to satisfy the query, however the results are not known to be in order. This results in the identified keys being sorted in memory prior to be returned to the calling stage in the execution plan.

By moving the _Sort_ predicate before the _Range_ predicate however, even though more keys may need to be scanned the keys will be returned correctly ordered.

```js
// operation
createIndex({ region: 1, joined: 1 })
find({ joined: { $gt: 2015 } }).sort({ region: 1 })
```

```js
// execution stats
"nReturned" : 4.0,
"totalKeysExamined" : 5.0,
"totalDocsExamined" : 5.0,
"executionStages" : {
    ...
    "inputStage" : {
        "stage" : "IXSCAN",
        ...
        "indexBounds" : {
            "region" : [
                "[MinKey, MaxKey]"
            ],
            "joined" : [
                "[MinKey, MaxKey]"
            ]
        },
```

![](/images/esr06.png)

Though this method requires scanning additional keys the lack of a blocking sort will generally be far more efficient/performant.

I hope that the _ESR "Rule"_ helps you optimize your MongoDB indexes and improve your query performance. If you have questions, feel free to hit me up in the comments, or check out the [MongoDB Developer Community forums](https://developer.mongodb.com/community/forums/).

If you need more timely assistance, consider MongoDB's [Atlas Developer Support](https://docs.atlas.mongodb.com/support/) or [Enterprise Support](https://www.mongodb.com/products/enterprise-grade-support).

Cheers, and happy optimizing!