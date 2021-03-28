---
layout: post
title: "Current Date Math in MongoDB Aggregations"
date: 2020-01-17 06:30:17 -0500
comments: true
categories: [MongoDB, "Queries & Indexing"]
tags: [mongodb]
---

A challenge that I've had in the past while working with my data in MongoDB has been how to incorporate
date math into my aggregations.

``` javascript
db.foo.insertMany([
{ lastUpdated: new Date(new Date().setDate(new Date().getDate() - 1)) },
{ lastUpdated: new Date(new Date().setDate(new Date().getDate() - 5)) },
{ lastUpdated: new Date(new Date().setDate(new Date().getDate() - 9)) }
]);
db.foo.find();
/*
{ "_id" : ObjectId("5e219c6ecc99b35bb2975d9e"), "lastUpdated" : ISODate("2020-01-16T11:37:18.522Z") }
{ "_id" : ObjectId("5e219c6ecc99b35bb2975d9f"), "lastUpdated" : ISODate("2020-01-12T11:37:18.522Z") }
{ "_id" : ObjectId("5e219c6ecc99b35bb2975da0"), "lastUpdated" : ISODate("2020-01-08T11:37:18.522Z") }
*/
```

Given the 3 documents we've setup above, if I wanted to filter a pipeline to only [`$match`](https://docs.mongodb.com/manual/reference/operator/aggregation/match)
documents that are newer than 1 week old, I would have to resort to using Javascript:

``` javascript
// compare lastUpdated to a new Javascript Date object set to
// 7 days from the current date
db.foo.aggregate(
{ $match:
  { lastUpdated: { $gte: new Date(new Date().setDate(new Date().getDate() - 7)) } }
});
/*
{ "_id" : ObjectId("5e219c6ecc99b35bb2975d9e"), "lastUpdated" : ISODate("2020-01-16T11:37:18.522Z") }
{ "_id" : ObjectId("5e219c6ecc99b35bb2975d9f"), "lastUpdated" : ISODate("2020-01-12T11:37:18.522Z") }
*/
```

Now if your pipeline is running in a non-Javascript environment, the `new Date()` call within the pipeline
would likely throw an exception.

If you're working with MongoDB 4.2 or newer though, a new [`$$NOW` aggregation variable](https://docs.mongodb.com/manual/reference/aggregation-variables/#variable.NOW
) is available that can be combined with existing pipeline operators to [`$subtract`](https://docs.mongodb.com/manual/reference/operator/aggregation/subtract/index.html
) the number of milliseconds in the number of days to filter from the current date:

``` javascript
// compare lastUpdated to the number of milliseconds in
// 7 days subtracted from the current
db.foo.aggregate(
{ $match:
  { $expr:
    { $let:
      { vars:
        { start:
          { $subtract: ["$$NOW", (7 * 86400000)] }
        },
        in: { $gte: ["$lastUpdated", "$$start"] }
      }
    }
  }
});
/*
{ "_id" : ObjectId("5e219c6ecc99b35bb2975d9e"), "lastUpdated" : ISODate("2020-01-16T11:37:18.522Z") }
{ "_id" : ObjectId("5e219c6ecc99b35bb2975d9f"), "lastUpdated" : ISODate("2020-01-12T11:37:18.522Z") }
*/
```

I hope you find this as useful as I did. With each major release of MongoDB new features and functionality
are being introduced that reduce the "hacks" or "workarounds" we've had to do in the past.

If you're looking for more MongoDB tips and tricks, head on over to Asya's [Stupid Tricks With MongoDB](http://www.kamsky.org/stupid-tricks-with-mongodb).

Let me know in the comments below if you have any questions, or if you found this useful.
