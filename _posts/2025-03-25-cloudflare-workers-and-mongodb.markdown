---
layout: post
title: "Cloudflare Workers and MongoDB"
date: 2025-03-25 13:21:42 -0400
comments: true
categories: MongoDB
tags: [mongodb, drivers, node, nodejs, javascript, typescript]
image: /images/mongodb-cloudflare.png
---

Previously I wrote about [_Why Cloudflare Workers Don't Work With MongoDB_]({% post_url 2024-09-11-why-cloudflare-workers-dont-work-with-mongodb %}), but since then the Cloudflare team has done some great work to add support for the missing Node.js features MongoDB's driver required to operate successfully from [Cloudflare Workers](https://workers.cloudflare.com/):

* [`cloudflare/workerd#3315`](https://github.com/cloudflare/workerd/pull/3315): add node:net module
* [`cloudflare/workerd#3594`](https://github.com/cloudflare/workerd/pull/3594): implement TLSSocket and connect from node:tls

Were these changes sufficient to make Cloudflare Workers and MongoDB Atlas work together? Let's revisit the example from the previous blog post to verify:

## Sample Application

Once again, we'll test the latest iteration of Cloudflare Workers by customizing the [compatibility flags](https://developers.cloudflare.com/workers/configuration/compatibility-dates/#setting-compatibility-flags) and [compatibility date](https://developers.cloudflare.com/workers/configuration/compatibility-dates/) in our configuration:

**`wrangler.toml`**
```toml
name = "mongodb-cloudflare-example"
main = "src/worker.ts"
compatibility_flags = ["nodejs_compat_v2"]
compatibility_date = "2025-03-20"

[vars]
MONGODB_URI = "mongodb+srv://..."
```

**`src/worker.ts`**
```ts
import { MongoClient } from 'mongodb';

export interface Env {
  MONGODB_URI: string;
}

let client = null;

export default {
  async fetch(request: Request, env: Env): Promise<Response> {
    client ??= new MongoClient(env.MONGODB_URI, {
      maxPoolSize: 1, minPoolSize: 0,
      serverSelectionTimeoutMS: 5000,
    });

    const db = client.db('test');
    const coll = db.collection('test_workers');

    await coll.drop().catch(() => null);
    await coll.insertOne({ a: new Date() });

    const result = await coll.findOne({});
    return Response.json(result);
  },
} satisfies ExportedHandler;
```

**`package.json`**
```json
{
  "name": "mongodb-cloudflare-example",
  "version": "0.0.0",
  "type": "module",
  "private": true,
  "scripts": {
    "start": "wrangler dev"
  },
  "dependencies": {
    "mongodb": "^6.15.0"
  },
  "devDependencies": {
    "wrangler": "^4.4.0"
  }
}
```

To test the code above you would need to do the following:

```bash
npm install
npm start
```

This will launch [Wrangler](https://developers.cloudflare.com/workers/wrangler/), the CLI for working with Cloudflare Workers.

## Evaluation

Now that our worker is running locally, it should be accessible via http://localhost:8787. The worker logic we wrote in `wrangler.ts` should perform the following actions:

* connect to the MongoDB cluster via the connection string configured in the `MONGODB_URI` environment variable (setup in `wrangler.toml`)
* drop the `test_workers` collection in the `test` database
* insert a new document in the `test_workers` collection
* retrieve the inserted document from the `test_workers` collection
* return a JSON representation of that document

Let's try it out and see what happens:

```bash
$ curl localhost:8787
{"_id":"67e2e4bb377816f2a78db326","a":"2025-03-25T17:15:39.957Z"}
```

SUCCESS!

We were able to connect to our cluster (using [SCRAM authentication](https://www.mongodb.com/docs/drivers/node/current/fundamentals/authentication/mechanisms/)) to interact with our data via the MongoDB Node.js driver from a Worker.

## Conclusion

Excitement for Cloudflare Workers support for MongoDB has been around in the [MongoDB developer forums](https://www.mongodb.com/community/forums/t/cloudflare-workers-integration-is-now-possible/226708) since May, 2023. As the Product Manager for MongoDB's JavaScript developer experience I've possibly been making more noise about this issue than most - including the initial blog post. I shared this with the Cloudflare team in a [bug report on the `workers-sdk`](https://github.com/cloudflare/workers-sdk/issues/6684), which ultimately triggered a [discussion on the `workerd` project](https://github.com/cloudflare/workerd/discussions/2721) that may have prompted the ensuing engineering effort.

I really look forward to seeing the amazing opportunities this integration can unlock for MongoDB developers that want to take advantage of the power and flexibility of Cloudflare Workers!

