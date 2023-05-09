---
layout: post
title: "Cleaning Up ETL Results in MongoDB by Transposing Multiple Arrays"
date: 2022-02-07 09:05:00 -0500
comments: true
categories: [MongoDB]
tags: [mongodb, aggregation, etl]
image: /images/mongodb-logo.png
---

When performing an ETL from a normalized relational dataset there's a good chance a 1:1 conversion won't produce the desired results on the first pass. For example, if the goal is to [Model One-to-Many Relationships with Embedded Documents](https://docs.mongodb.com/manual/tutorial/model-embedded-one-to-many-relationships-between-documents/#std-label-data-modeling-example-one-to-many) but the dataset contains a number of relationships mapped to individual fields as arrays of scalar values, you'll likely want to convert these to subdocuments to facilitate access and interaction from your applications.

![](/images/punch_card_erd.png)

In this example, our data has been imported from a legacy system with the above design, and has produced documents in a `punch_cards` collection with the following schema:

```js
{
  "date": "December 1, 2020",
  "category": "AM",
  "events": {
    "employee": [ "Alex", "Max", "Will", "Sara" ],
    "action": [ "Punched In", "Punched In", "Punched Out", "Punched In" ],
    "timestamp": [ "2020/12/01 08:01", "2020/12/01 07:58", "2020/12/01 09:03", "2020/12/01 09:59"]
  }
},
{
  "date": "December 1, 2020",
  "category": "PM",
  "events": {
    "employee": [ "Alex", "Max", "Sara", "Will" ],
    "action": [ "Punched Out", "Punched Out", "Punched Out", "Punched In" ],
    "timestamp": [ "2020/12/01 16:00", "2020/12/01 16:30", "2020/12/01 20:00", "2020/12/01 23:58"]
  }
}
```

> The initial schema is a result of limitations with the initial import strategy. The goals of this article are to showcase how these limitations an be overcome once the initial ETL from source system to MongoDB has been completed.
{: .prompt-info }

The desired end state is a document with all events mapped to an array of subdocuments:

```js
{
    "events" : [
        {
            "employee" : "Alex",
            "action" : "Punched Out",
            "timestamp" : "2020/12/01 16:00"
        },
        {
            "employee" : "Max",
            "action" : "Punched Out",
            "timestamp" : "2020/12/01 16:30"
        },
        {
            "employee" : "Sara",
            "action" : "Punched Out",
            "timestamp" : "2020/12/01 20:00"
        },
        {
            "employee" : "Will",
            "action" : "Punched In",
            "timestamp" : "2020/12/01 23:58"
        }
    ]
}
```

Using MongoDB's [Aggregation](https://docs.mongodb.com/manual/aggregation/) functionality there are multiple ways to produce the desired results, two of which I'd like to share below.

## The "Easy" Way

Starting in MongoDB 3.4 the [`$zip`](https://docs.mongodb.com/manual/reference/operator/aggregation/zip/) operator was introduced, which could be used to transpose an array of input arrays so that the first element of the output array would be an array containing, the first element of the first input array, the first element of the second input array, etc. If only `$zip` is used the resulting documents would appear as an array of arrays:

```js
db.punch_cards.aggregate([
{ $project: {
  events: {
    $zip: {
      inputs: [
      "$events.employee", "$events.action", "$events.timestamp"
    ]}
  }
}}]);
```
```js
// output
{
    "events" : [
        [
            "Alex",
            "Punched Out",
            "2020/12/01 16:00"
        ],
        [
            "Max",
            "Punched Out",
            "2020/12/01 16:30"
        ],
        [
            "Sara",
            "Punched Out",
            "2020/12/01 20:00"
        ],
        [
            "Will",
            "Punched In",
            "2020/12/01 23:58"
        ]
    ]
}
```

By providing the output of the `$zip` as the input to a [`$map`](https://docs.mongodb.com/manual/reference/operator/aggregation/map/) the results can be easily rewritten to match our desired schema:

```js
db.punch_cards.aggregate([
{ $project: {
  events: {
    $map: {
      input: {
        $zip: {
          inputs: [
          "$events.employee", "$events.action", "$events.timestamp"
        ]}
      },
      as: "zipped",
      in: {
        employee:  { $arrayElemAt: [ "$$zipped", 0 ] },
        action:    { $arrayElemAt: [ "$$zipped", 1 ] },
        timestamp: { $arrayElemAt: [ "$$zipped", 2 ] }
      }
    }
  }
}}
]);
```

> These pipeline examples only project the `events` field. To include additional fields (ex: `date`, `category`) these would have to be included in the [`$project`](https://docs.mongodb.com/manual/reference/operator/aggregation/project) stage explicitly.</p>
{: .prompt-info }

## The "Hard" Way

Assuming you're running MongoDB 3.2 or earlier (which is highly unlikely) and don't have access to the `$zip` operator, a more complex aggregation pipeline can be created that [`$unwind`](https://docs.mongodb.com/manual/reference/operator/aggregation/unwind/)s each array, then tags each document emitted with a field indicating if all results are from the same array index for each document, then filters out matches and re-[`$group`](https://docs.mongodb.com/manual/reference/operator/aggregation/group/)s them:

```js
db.punch_cards.aggregate([
{ $unwind: { path: "$events.employee",  includeArrayIndex: "idx01" } },
{ $unwind: { path: "$events.action",    includeArrayIndex: "idx02" } },
{ $unwind: { path: "$events.timestamp", includeArrayIndex: "idx03" } },
{ $project: {
  events: 1,
  keep: { $cond: {
    if: { $and: [
      { $eq: ["$idx01", "$idx02" ] },
      { $eq: ["$idx02", "$idx03" ] } ,
      { $eq: ["$idx03", "$idx01" ] }
    ] }, then: true, else: false } }
}},
{ $match: { keep: true } },
{ $group: {
  _id: "$_id",
  events: { $push: "$events" }
}},
]);
```

I've included two variations of the pipeline to illustrate the different approaches you can take to solve the same problem. Depending on your use case the "hard" way may be more appropriate, however the "easy" way requires far less processing and should be more performant as a result.

## Updating the Data

The pipeline examples above don't acctually writing any changes back to disk. This is by design to ensure no copy/paste errors result in unanticipated data loss as a result.

Once you are satisfied with the transformations and are ready to write the results, either an [`$out`](https://docs.mongodb.com/manual/reference/operator/aggregation/out/) or [`$merge`](https://docs.mongodb.com/manual/reference/operator/aggregation/merge/) stage can be added as the final stage in the pipeline.
