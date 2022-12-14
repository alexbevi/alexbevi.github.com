---
layout: post
title: "Efficiently Identifying Duplicates using MongoDB"
date: 2022-11-29 10:50:52 -0500
comments: true
categories: MongoDB
tags: ["javascript", "mongodb", "scripting", "queries", "indexing"]
image:
  src: /images/mongodb-logo.png
  alt: MongoDB Logo
---

# Efficiently Identifying Duplicates using MongoDB

One question that comes up time and again on Stack Overflow or the MongoDB Developer Forums is _"how can I find duplicate X and get a list of Y that contains these duplicates"_ (ex: ["Query to find duplicate users (ip)"](https://www.mongodb.com/community/forums/t/query-to-find-duplicate-users-ip/202020)).

Using MongoDB's [Aggregation Framework](https://www.mongodb.com/docs/manual/aggregation/) this can be done easily.

```js
function generate_random_data(size){
    var chars = 'abcdefghijklmnopqrstuvwxyz'.split('');
    var len = chars.length;
    var random_data = [];

    while (size--) { random_data.push(chars[Math.random()*len | 0]); }

    return random_data.join('');
}

function setup() {
  db.foo.drop();
  db.foo.insertMany([
    { parent_id: 1, user_id: 1, junk: generate_random_data(512) },
    { parent_id: 1, user_id: 2, junk: generate_random_data(512) },
    { parent_id: 2, user_id: 3, junk: generate_random_data(512) },
    { parent_id: 3, user_id: 4, junk: generate_random_data(512) },
    { parent_id: 4, user_id: 5, junk: generate_random_data(512) },
    { parent_id: 3, user_id: 6, junk: generate_random_data(512) },
    { parent_id: 2, user_id: 7, junk: generate_random_data(512) }
  ]);
}

setup();
```

Given the above setup our collection will contain 7 documents. If we wanted to identify how many duplicate `parent_id` values there are and what the associated `user_id` values are we could do something like the following:

```js
db.foo.aggregate([
  { $group: { _id: "$parent_id", used: { $sum: 1 }, user_ids: { $push: "$user_id" } } },
  { $match: { used: { $gt: 1 } } },
  { $project: { _id: 0, parent_id: "$_id", user_ids: "$user_ids"} }
]);
/* ** output **
[
  { "parent_id": 3, "user_ids": [ 4, 6 ] },
  { "parent_id": 1, "user_ids": [ 1, 2 ] },
  { "parent_id": 2, "user_ids": [ 3, 7 ] }
]
*/
```

This will work pretty efficiently for our sample set of 7 documents, but what about millions (or billions)?

## Reviewing Performance

By generating [Explain Results](https://www.mongodb.com/docs/manual/reference/explain-results/) for the above operation we can better understand how this operation is performing:

```js
db.foo.explain("executionStats").aggregate([
  { $group: { _id: "$parent_id", used: { $sum: 1 }, user_ids: { $push: "$user_id" } } },
  { $match: { used: { $gt: 1 } } },
  { $project: { _id: 0, parent_id: "$_id", user_ids: "$user_ids"} }
]);
/* ** output **
"winningPlan": {
  ...
  "inputStage": {
    "stage": "COLLSCAN",
    "direction": "forward"
  }
},
...
"executionStats": {
  "nReturned": 7,
  "totalKeysExamined": 0,
  "totalDocsExamined": 7,
*/
```

According to the documentation we can [improve our pipeline's performance with indexes and document filters](https://www.mongodb.com/docs/manual/core/aggregation-pipeline-optimization/#indexes).

No index was available for use and as a result a full collection scan was required.

## Adding an Index

We know only 2 fields from our document are actually being used by the pipeline, so let's try again using a purpose-built [compound index](https://www.mongodb.com/docs/manual/core/index-compound) and review the explain plan again:

```js
db.foo.createIndex({ parent_id: 1, user_id: 1 });
db.foo.explain("executionStats").aggregate([
  { $group: { _id: "$parent_id", used: { $sum: 1 }, user_ids: { $push: "$user_id" } } },
  { $match: { used: { $gt: 1 } } },
  { $project: { _id: 0, parent_id: "$_id", user_ids: "$user_ids"} }
]);
/* ** output **
"winningPlan": {
  ...
  "inputStage": {
    "stage": "COLLSCAN",
    "direction": "forward"
  }
},
...
"executionStats": {
  "nReturned": 7,
  "totalKeysExamined": 0,
  "totalDocsExamined": 7,
*/
```

Even with what appears to be an ideal index a collection scan is being performed. What gives? Oh right .... even if following ["ESR Guidance"](https://www.mongodb.com/docs/manual/tutorial/equality-sort-range-rule/) for creating optimal indexes, an unfiltered `$group` must scan the entire collection anyway and wouldn't benefit directly from an index ..... or would it?

## Adding a `$sort` before the `$group`

Having a `$sort` stage prior to the `$group` will allow the pipeline take advantage of the index to group a sorted set.

```js
db.foo.explain("executionStats").aggregate([
  { $sort: { parent_id: 1 } },
  { $group: { _id: "$parent_id", used: { $sum: 1 }, user_ids: { $push: "$user_id" } } },
  { $match: { used: { $gt: 1 } } },
  { $project: { _id: 0, parent_id: "$_id", user_ids: "$user_ids"} }
]);
/* ** output **
"winningPlan": {
  ...
  "inputStage": {
    "stage": "IXSCAN",
    "keyPattern": {
      "parent_id": 1,
      "user_id": 1
    },
    ...
"executionStats": {
  "nReturned": 7,
  "totalKeysExamined": 7,
  "totalDocsExamined": 0,
*/
```

The explain plan for the above operation shows not only that an index was used, but the entire operation was a [covered query](https://www.mongodb.com/docs/manual/core/query-optimization/#covered-query).

## Conclusion

Now that we can identify duplicates further processing can be done with the results as needed. For example assume we wanted to remove all documents with a duplicate `parent_id` and only keep the first:

```js
db.foo.aggregate([
  { $sort: { parent_id: 1 } },
  { $group: { _id: "$parent_id", used: { $sum: 1 }, user_ids: { $push: "$user_id" } } },
  { $match: { used: { $gt: 1 } } },
  { $project: { _id: 0, parent_id: "$_id", user_ids: "$user_ids"} }
]).forEach((d) => db.foo.deleteMany({ user_id: { $in: d.user_ids.slice(1, d.user_ids.length) } }));
```

The above is taking the results of the aggregation pipeline and applying the following `deleteMany` command to each: `(d) => db.foo.deleteMany({ user_id: { $in: d.user_ids.slice(1, d.user_ids.length) } })`.

Note this could be further optimized for larger delete workloads by instead writing all duplicate `user_id` values to a single array and deleting those all at once:

```js
var toDelete = [];
db.foo.aggregate([
  { $sort: { parent_id: 1 } },
  { $group: { _id: "$parent_id", used: { $sum: 1 }, user_ids: { $push: "$user_id" } } },
  { $match: { used: { $gt: 1 } } },
  { $project: { _id: 0, parent_id: "$_id", user_ids: "$user_ids"} }
]).forEach((d) => toDelete.push(d.user_ids.slice(1, d.user_ids.length)));

db.foo.deleteMany({ user_id: { $in: toDelete.flat() } });
```

<div class="note warning">
Be very careful whenever batch removing data and test in a lower environment first!
</div>

Hopefully you found this helpful. If you did, feel free to drop a comment below ;)
