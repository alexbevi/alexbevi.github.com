---
layout: post
title: "Why Cloudflare Workers Don't Work With MongoDB"
date: 2024-09-11 13:09:40 -0400
comments: true
categories: MongoDB
tags: [mongodb, drivers, node, nodejs, javascript, typescript]
image: /images/mongodb-cloudflare.png
---
> As of early 2025 Cloudflare Workers not only [work with MongoDB]({% post_url 2025-03-25-cloudflare-workers-and-mongodb %}), but can be tuned to [work well using Durable Objects]({% post_url 2025-04-11-performance-profiling-mongodb-on-cloudflare-workers %})!
{: .prompt-info }

[Cloudflare Workers](https://workers.cloudflare.com/) is a great platform for deploying serverless JavaScript code, but has historically never supported raw sockets. In May of 2023 they [announced support for a `connect()` API](https://blog.cloudflare.com/workers-tcp-socket-api-connect-databases/) which allows [TCP Sockets](https://developers.cloudflare.com/workers/runtime-apis/tcp-sockets/) to be created within Workers, but is not a direct replacement for Node.js' [`net.Socket`](https://nodejs.org/api/net.html#class-netsocket) API.

Many NPM packages - including MongoDB's [Node.js driver](https://www.mongodb.com/docs/drivers/node/current/) - rely on `net.Socket` or [`tls.TLSSocket`](https://nodejs.org/api/tls.html#class-tlstlssocket) to connect to and communicate with remote systems. Using these libraries directly from Cloudflare Workers [has not been possible](https://www.mongodb.com/community/forums/t/cloudflare-workers-integration-is-now-possible/226708/11?u=alexbevi) as a result of these missing APIs.

Cloudflare recently announced that [more NPM packages would be supported on Cloudflare Workers](https://blog.cloudflare.com/more-npm-packages-on-cloudflare-workers-combining-polyfills-and-native-code/), but for libraries that need `net.Socket` or `tls.TLSocket` access, will they work in a Cloudflare Workers environment?

> Packages that could not be imported with `nodejs_compat`, even as a dependency of another package, will now load. This includes popular packages such as [...] **`mongodb`**, [...] and many more.

Based on the blog post the Node.js driver should load, but can it be used?

> Note that the fact that Workers can load, but not use the `mongodb` package was reported to Cloudflare at [https://github.com/cloudflare/workers-sdk/issues/6684](https://github.com/cloudflare/workers-sdk/issues/6684)
>
> The Cloudflare blog post has since been updated to remove `mongod` from the list of useable packages to avoid further confusion.
{: .prompt-tip }

## Sample Application

To test the latest iteration of Cloudflare Workers [compatibility flags](https://developers.cloudflare.com/workers/configuration/compatibility-dates/#setting-compatibility-flags) we'll be working with the following configuration:

**`src/worker.ts`**
```ts
import { BSON, MongoClient } from 'mongodb';

export interface Env {
  MONGODB_URI: string;
}

let client = null;
let requestCount = 0;

export default {
  async fetch(request: Request, env: Env, _ctx: ExecutionContext): Promise<Response> {
    console.log(JSON.stringify({ requestCount }));
    requestCount += 1;
    client ??= new MongoClient(env.MONGODB_URI, {
      maxPoolSize: 1, minPoolSize: 0,
      serverSelectionTimeoutMS: 5000,
    });

    const db = client.db('test');
    const coll = db.collection('test');

    if ((await coll.countDocuments()) > 10) {
      await coll.drop().catch(() => null);
    }

    await coll.insertOne({ a: 1 });

    return new Response(BSON.EJSON.stringify(await coll.findOne({ a: 1 }), null, '  ', { relaxed: false }));
  },
};
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
  "devDependencies": {
    "@cloudflare/workers-types": "^4.20240603.0",
    "ts-node": "^10.9.1",
    "typescript": "^5.0.4",
    "wrangler": "^3.59.0"
  },
  "dependencies": {
    "mongodb": "^6.8.1"
  }
}
```

**`wrangler.toml`**
```toml
name = "mongodb-cloudflare-example"
main = "src/worker.ts"
compatibility_flags = ["nodejs_compat_v2"]

[vars]
MONGODB_URI = "mongodb+srv://..."
```

To test the code above you would need to do the following:

```bash
npm install
npm run start
```

## Evaluation

The default connection string format when [connecting to your Atlas cluster](https://www.mongodb.com/docs/atlas/connect-to-database-deployment/#connect-to-your-cloud-cluster) is `mongodb+srv`, which is what we included initially in the `wrangler.toml` file.

The first time we run our test code however we're unable to resolve the [SRV connection format](https://www.mongodb.com/docs/manual/reference/connection-string/#srv-connection-format) as it appears that [`dns.resolveTxt`](https://nodejs.org/api/dns.html#dnsresolvetxthostname-callback) is not implemented:

```
⎔ Starting local server...
{"requestCount":0}
[wrangler:err] Error: [unenv] dns.resolveTxt is not implemented yet!
```

Since Atlas allows you to also connect using the [standard connection string format](https://www.mongodb.com/docs/manual/reference/connection-string/#standard-connection-string-format), let's update the `MONGODB_URI` in the `wrangler.toml` to instead be `mongodb://...`:

```
⎔ Starting local server...
{"requestCount":0}
[wrangler:err] MongoServerSelectionError: socket.once is not a function
```

Based on the above it appears [`events.once`](https://nodejs.org/api/events.html#eventsonceemitter-name-options) is missing, which Node.js' `net` module exposes from an `EventEmitter` import. I don't think we'd be able to polyfill all this if that were considered the path forward 😓.

What about trying to configure `wrangler` to connect to a local MongoDB instance (ex: `mongodb://localhost:27017`)? Well in that case it will still fail, but at least it will fail differently:

```
⎔ Starting local server...
{"requestCount":0}
[wrangler:err] MongoServerSelectionError: [unenv] net.createConnection is not implemented yet!
```

## Alternatives?

If you happen upon the article called ["Create a REST API with Cloudflare Workers and MongoDB Atlas"](https://www.mongodb.com/developer/products/atlas/cloudflare-worker-rest-api/) you may be thinking there's an alternate solution to be explored. MongoDB offered a REST-based interface to your data in Atlas via the [Atlas Data API](https://www.mongodb.com/docs/atlas/app-services/data-api/), however this product was recently deprecated and will be sunset.

A custom REST-based API would be a solution to working with your MongoDB data from within Cloudflare Workers, so until the runtime is updated to better support Node.js' socket APIs, see the [Data API deprecation](https://www.mongodb.com/docs/atlas/app-services/data-api/data-api-deprecation) page for some ideas.

[Neurelo seems like a good option](https://docs.neurelo.com/guides/mongodb-atlas-migrate-rest-data-apis-to-neurelo) for getting a REST-based API off the ground with little effort.

## Summary

Though [module aliasing](https://developers.cloudflare.com/workers/wrangler/configuration/#module-aliasing) and polyfills might be an option for some functionality, it really seems like Cloudflare Workers just aren't meant to work with Node.js' socket APIs. As a result, libraries such as MongoDB's Node.js driver simply won't be able to connect to anything.

Some work [was proposed](https://jira.mongodb.org/browse/NODE-4785) by MongoDB's team to allow a custom transport layer to be provided, however this would still require Cloudflare Workers to support Node.js' [TLS](https://nodejs.org/api/tls.html) API as [TLS cannot, for good reasons, be disabled for Atlas deployments](https://www.mongodb.com/docs/atlas/reference/faq/security/#can-i-disable-tls-on-my-deployment-).
