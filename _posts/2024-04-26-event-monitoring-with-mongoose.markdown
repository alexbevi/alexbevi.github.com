---
layout: post
title: "Event Monitoring with Mongoose"
date: 2024-04-26 09:58:52 -0400
comments: true
categories: MongoDB
tags: [mongodb, connections, drivers, monitoring, mongoose, node.js]
image: /images/mongodb-logo.png
---

I previously wrote about [MongoDB Driver Monitoring]({% post_url 2022-04-13-mongodb-driver-monitoring %}), but there are [ODM libraries]({% post_url 2022-11-02-mongodb-orms-odms-and-libraries %}) and framework integrations that are built atop the drivers that can take advantage of this functionality.

For example, [`mongoose`](https://mongoosejs.com/docs/guide.html) can be easily configured to expose [cluster monitoring](https://www.mongodb.com/docs/drivers/node/current/fundamentals/monitoring/cluster-monitoring/), [connection pool monitoring](https://www.mongodb.com/docs/drivers/node/current/fundamentals/monitoring/connection-monitoring/) and [command monitoring](https://www.mongodb.com/docs/drivers/node/current/fundamentals/monitoring/command-monitoring/) capabilities.

```js
const mongoose = require('mongoose');
const { Schema } = mongoose;

run().catch(err => console.log(err));

async function run() {
  await mongoose.connect('mongodb://localhost:27017/test');

  mongoose.connection.getClient().on('connectionCheckOutStarted', ev => console.log('Received: ', ev));

  const schema = Schema({ name: String });
  const Test = mongoose.model('Test', schema);
  await Test.create({ name: 'test' });
}
```

This was documented within a comment of [this GitHub issue](https://github.com/Automattic/mongoose/issues/9804) but for the sake of visibility I wanted to capture it here.