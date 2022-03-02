---
layout: post
title: "Working around MongoDB Stitch's \"max async work queue\" limit"
date: 2020-03-30 05:19:32 -0400
comments: true
categories: [MongoDB]
tags: [mongodb, realm]
image:
  src: /images/mongodb-logo.png
  alt: MongoDB Logo
---

[MongoDB Stitch](https://www.mongodb.com/cloud/stitch) is a great way to build apps quickly with your data that's already managed by [MongoDB Atlas](https://www.mongodb.com/cloud/atlas). Though these services empower you to focus on development without having to worry about infrastructure, being a managed service there are occasionally limitations imposed by the vendor.

This article summarizes why this limit exists, as well as how to adapt your [MongoDB Stitch Functions](https://docs.mongodb.com/stitch/functions/) to work around it.

<!-- more -->

The following is an [HTTP Service](https://docs.mongodb.com/stitch/services/http) I've written that has an [incoming webhook](https://docs.mongodb.com/stitch/services/http/#incoming-webhooks). When this webhook is called a MongoDB Stitch Function is run which inserts a number of documents. The number to insert is defined by the `maxItems` [_query parameter_](https://en.wikipedia.org/wiki/Query_string) of the [request payload](https://docs.mongodb.com/stitch/services/http/#request-payload) provided to the incoming webhook.

**NOTE** When doing a number of `insertOne` operations in a loop an [`insertMany`](https://docs.mongodb.com/stitch/mongodb/actions/collection.insertMany/) would likely address the issue directly without requiring any additional workarounds. The following code is really best suited to a number of update or delete operations that have unique filters and cannot be logically grouped.

```javascript
// MongoDB Stitch Function code for the Incoming Webhook
exports = function (payload, response) {
  let maxItems = parseInt(payload.query.maxItems);

  const CLUSTER    = 'mongodb-atlas';
  const DB         = 'test';
  const COLLECTION = 'web_worker_queue_failures';
  const collection = context.services.get(CLUSTER).db(DB).collection(COLLECTION);

  let items = [];
  for(let i = 0; i < maxItems; i++) {
    items.push({ a: i });
  }

  let results = [];
  items.forEach((item) => {
    collection.insertOne(item).then(res => {
      results.push(res);
    }, error => {
      results.push({ error: error });
      console.log(error);
    });
  });

  return { "Processed": items.length };
};
```

When the webhook is executed, the number of items processed is returned. In the following example we'll specify that we want 900 items to be inserted:

```bash
curl -w "\nTotal Time: %{time_total}s\n" \
     -H "Content-Type: application/json" -d '{}' \
     https://webhooks.mongodb-stitch.com/api/client/v2.0/app/cluster0-app0-abcde/service/WebWorkerFailureTest/incoming_webhook/webhook0?maxItems=900
{"Processed":{"$numberInt":"900"}}
Total Time: 1.729469s
```

Based on the output returned from the webhook, 900 items were inserted. Next we'll try with 9000 items:

```bash
curl -w "\nTotal Time: %{time_total}s\n" \
     -H "Content-Type: application/json" -d '{}' \
     https://webhooks.mongodb-stitch.com/api/client/v2.0/app/cluster0-app0-abcde/service/WebWorkerFailureTest/incoming_webhook/webhook0?maxItems=9000
{"error":"exceeded max async work queue size of 1000","error_code":"FunctionExecutionError","link":"https://stitch.mongodb.com/groups/13c415400000000000000000/apps/13c415400000000000000000/logs?co_id=13c415400000000000000000"}
Total Time: 0.371383s
```

Following the `"link"` would redirect you to the [Application Log](https://docs.mongodb.com/stitch/logs/) for the application that the webhook belongs to. This can be useful for debugging.

![](/images/stitch-log01.png)

The reason this error is thrown has to do with how the MongoDB Stitch platform handles async request execution within functions using an internal work queue. Operations such as [`insertOne`](https://docs.mongodb.com/stitch/mongodb/actions/collection.insertOne/) return a [Promise](https://developer.mozilla.org/en/docs/Web/JavaScript/Reference/Global_Objects/Promise). To ensure these promises don't queue infinitely waiting to be resolved, MongoDB Stitch will limit the number that can be enqueued, and if this limit is exceeded queuing stops and the exception is raised.

To work around this limit we will adapt our earlier code to instead throttle our work loop to ensure batches of 1000 or less are processed before more work is attempted.

```javascript
const processWork = async function(items) {
  const CLUSTER    = 'mongodb-atlas';
  const DB         = 'test';
  const COLLECTION = 'web_worker_queue_failures';
  const collection = context.services.get(CLUSTER).db(DB).collection(COLLECTION);

  const BATCH_SIZE = 1000;
  const totalItems = items.length;

  for (let i = 0; i < totalItems; i += BATCH_SIZE) {
    const requests = items.slice(i, i + BATCH_SIZE).map(function(item) {
      return collection.insertOne(item).catch(e => console.log(e));
    });

    await Promise.all(requests).catch(e => console.log(`Errors in batch ${i}: ${e}`));
  }
}

// MongoDB Stitch Function code for the Incoming Webhook
exports = function (payload, response) {
  let maxItems = parseInt(payload.query.maxItems);
  let items = [];
  for(let i = 0; i < maxItems; i++) {
    items.push({ a: i });
  }

  processWork(items);

  return { "Processed": items.length };
};
```

The number of items to process (based on `maxItems` again) will now be broken up into batches (of `BATCH_SIZE` size). Following this, [`Promise.all`](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Promise/all) will execute all the operations in a batch and ensure they are all fulfilled before another batch is processed.

This method allows the workload to be artificially throttled to allow `maxItems` operations to be executed. Let's try running our webhook again for 9000 items:

```bash
curl -w "\nTotal Time: %{time_total}s\n" \
     -H "Content-Type: application/json" -d '{}' \
     https://webhooks.mongodb-stitch.com/api/client/v2.0/app/cluster0-app0-abcde/service/WebWorkerFailureTest/incoming_webhook/webhook0?maxItems=9000
{"Processed":{"$numberInt":"9000"}}
Total Time: 13.935162s
```

Note that although this strategy will work with an array of items (`maxItems`) of any size, MongoDB Stitch Functions still have runtime limit of 90 seconds (see ["Constraints"](https://docs.mongodb.com/stitch/functions/#constraints)) which cannot be circumvented. If we try running the function for 90000 items, if the function runs for > 90 seconds execution will be terminated:

```bash
curl -w "\nTotal Time: %{time_total}s\n" \
     -H "Content-Type: application/json" -d '{}' \
     https://webhooks.mongodb-stitch.com/api/client/v2.0/app/cluster0-app0-abcde/service/WebWorkerFailureTest/incoming_webhook/webhook0?maxItems=90000
{"error":"execution time limit exceeded","error_code":"ExecutionTimeLimitExceeded","link":"https://stitch.mongodb.com/groups/13c415400000000000000000/apps/13c415400000000000000000/logs?co_id=13c415400000000000000000"}
Total Time: 90.311827s
```

Happy Coding!