---
layout: post
title: "Performance Profiling MongoDB on Cloudflare Workers"
date: 2025-04-11 06:23:55 -0400
comments: true
categories: MongoDB
tags: [mongodb, drivers, node, nodejs, javascript, typescript]
image: /images/mongodb-cloudflare.png
---
Cloudflare recently wrote about "[Your frontend, backend, and database — now in one Cloudflare Worker](https://blog.cloudflare.com/full-stack-development-on-cloudflare-workers/#node-js-compatibility)", which called out that the `mongodb` package should now work as expected. I validated that [Cloudflare Workers and MongoDB](https://alexbevi.com/blog/2025/03/25/cloudflare-workers-and-mongodb/) work together as well, but _how well_ do they work together.

Let's evaluate this by taking MongoDB's simple ["Find a Document"](https://www.mongodb.com/docs/drivers/node/current/usage-examples/findOne/) tutorial and adapting it to a Workers environment.

> TL;DR - MongoDB works perfectly from Cloudflare Workers, but you can significantly improve request latency by using Durable Objects
{: .prompt-info }

## Setup

First, [create a MongoDB Atlas](https://www.mongodb.com/resources/products/platform/mongodb-atlas-tutorial) cluster (free M0 works just fine), and [load the sample datasets](https://www.mongodb.com/docs/atlas/sample-data/#std-label-load-sample-data) once the cluster is provisioned. We'll be using the [`sample_mflix`](https://www.mongodb.com/docs/atlas/sample-data/sample-mflix/)dataset to return some information about a movie.

Next we'll want to [setup a Cloudflare Worker](https://developers.cloudflare.com/learning-paths/workers/get-started/first-worker/)to retrieve our movie information. I personally just created the Worker via the UI the using the [Git integration](https://developers.cloudflare.com/workers/ci-cd/builds/git-integration/) associated my worker with an existing repo.

![](/images/cf/Pasted image 20250403155514.png)

## Default Workers Experience

Our Worker will be using the [MongoDB Node.js driver](https://www.mongodb.com/docs/drivers/node/current/) to connect to the provisioned Atlas cluster using a [connection string](https://www.mongodb.com/docs/guides/atlas/connection-string/) stored as an [environment variable](https://developers.cloudflare.com/workers/configuration/environment-variables/).

```json
/**
 * wrangler.jsonc
 */
{
	"$schema": "node_modules/wrangler/config-schema.json",
	"name": "workers-mongodb-demo",
	"main": "src/index.ts",
	"compatibility_date": "2025-03-21",
	"compatibility_flags": [
		"nodejs_compat"
	]
}
```

```ts
// src/index.ts
import { MongoDBConnector } from './MongoDBConnector';

interface Env {
  MONGODB_URI: string;
}

export default {
  async fetch(request: Request, env: Env, ctx: ExecutionContext): Promise<Response> {
    try {
      let proxy = null;
      proxy = new MongoDBConnector(env);
      const result = await proxy.getMovie();
      return Response.json(result);
    } catch (error) {
      console.error('Error:', error);
      const message = error instanceof Error ? error.message : 'Unknown error';
      return new Response(`Error: ${message}`, { status: 500 });
    }
  }
} satisfies ExportedHandler<Env>;
```

The MongoDB-specific code will handle creating the `MongoClient`, performing all the networking and authentication round trips and retrieving a document from the cluster.

We'll do some basic instrumentation to capture the time between client connection and the result being returned in `queryTime`, which we'll return as part of the response.

```ts
// src/MongoDBConnector.ts
import { MongoClient } from 'mongodb';

interface Env {
  MONGODB_URI: string;
}

export class MongoDBConnector {
  private env: Env;
  private client: MongoClient;

  constructor(env: Env) {
    this.env = env;
    this.client = new MongoClient(this.env.MONGODB_URI);
  }

  async getMovie() {
    try {
      const queryStartTime = Date.now();
      await this.client.connect();

      const database = this.client.db("sample_mflix");
      const movies = database.collection("movies");
      const query = { title: "The Room" };
      const options = {
        sort: { "imdb.rating": -1 },
        projection: { _id: 0, title: 1, imdb: 1 },
      };
      const movie = await movies.findOne(query, options);

      const queryTime = Date.now() - queryStartTime;
      return {
        movie: {
          ...movie
        },
        queryTime
      };

    } catch (error) {
      console.error('MongoDB error:', error);
      throw error;
    }
  }
}
```

Once I had my code pushed to a repo and configured my Worker to use this repo, the CI/CD process would pick up any changes automatically.

### User in Toronto - Cluster in `us-east-1` (N. Virginia)

![](/images/cf/Pasted image 20250403155815.png)

My Atlas cluster is in the default region - which happens to be AWS' `us-east-1`. I'm located in Toronto, so I would expect the latency between my requests and my data to be fairly low.

```
$ curl https://workers-mongodb-demo.alex-fbd.workers.dev/
{"movie":{"title":"The Room","imdb":{"rating":3.4,"votes":25750,"id":368226}},"queryTime":429}

<repeat about 5 times>

$ curl https://workers-mongodb-demo.alex-fbd.workers.dev/
{"movie":{"title":"The Room","imdb":{"rating":3.4,"votes":25750,"id":368226}},"queryTime":302}
```

Using the extremely scientific method of curling the workers endpoint 5-6 times and averaging the `queryTime` values it seems my round trip time for an operation is 300ms, with the very first request being about 100ms slower than that.

I appreciate that there are [numerous round trips to required to authenticate](https://alexbevi.com/blog/2023/05/04/round-trips-to-authenticate-a-mongodb-client-connection/) a connection to Atlas, but MongoDB's drivers provide connection pooling out of the box so I'd sort of expect this time to go down much more - but it doesn't.

### User in Toronto - Cluster in `ap-northeast-1` (Tokyo)

![](/images/cf/Pasted image 20250404155042.png)

Just for comparison sake since Atlas [offers clusters in most AWS regions](https://www.mongodb.com/docs/atlas/reference/amazon-aws/#std-label-amazon-aws), I spun one up in `ap-northeast-1` and updated the connection string in my worker to see how this might impact the round trip time of an operation.

```
$ curl https://workers-mongodb-demo.alex-fbd.workers.dev/
{"movie":{"title":"The Room","imdb":{"rating":3.5,"votes":25673,"id":368226}},"queryTime":2044}

<repeat about 5 times>

$ curl https://workers-mongodb-demo.alex-fbd.workers.dev/
{"movie":{"title":"The Room","imdb":{"rating":3.5,"votes":25673,"id":368226}},"queryTime":1901}
```

These requests now take almost 2 seconds each.  Since Cloudflare Workers have a [Smart Placement](https://developers.cloudflare.com/workers/configuration/smart-placement/) feature I wanted to try that out to see if it would have any meaningful impact.

### Testing Workers and Smart Placement

After enabling the feature, Cloudflare [adds a `cf-placement` header to all requests](https://developers.cloudflare.com/workers/configuration/smart-placement/#cf-placement-header) so you can pretty easily verify where your worker has been placed.

```
$ curl -v https://workers-mongodb-demo.alex-fbd.workers.dev/
...
< cf-placement: local-YYZ
...
{"movie":{"title":"The Room","imdb":{"rating":3.5,"votes":25673,"id":368226}},"queryTime":2029}
```

I ran many tests, but my response times were always the same. Initially I thought it was an issue with the Smart Placement feature, but after reviewing with a Cloudflare team member it seems Smart Placement looks at your actual traffic patterns to determine where to place it, so I'd need traffic across many regions to trigger it.

## Maintaining State with Durable Objects

The nature of Workers is to provide "[serverless](https://www.cloudflare.com/en-ca/learning/serverless/what-is-serverless/) execution environments", so they're likely stateless and would require connections to be re-created for each request. If we could create and reuse our `MongoClient` and associated connection pool, maybe our round trip times could be improved by reducing our cold-start times.

[Durable Objects](https://www.cloudflare.com/en-ca/developer-platform/products/durable-objects/)  - which [are described](https://developers.cloudflare.com/durable-objects/what-are-durable-objects/) as being a _"special kind of Cloudflare Worker which uniquely combines compute with storage"_ - seem like they might be suitable for our needs. The [tutorial](https://developers.cloudflare.com/durable-objects/get-started/tutorial/) is a great resource to get us up and running quickly, which I've used to adapt our previous `MongoDBConnector` implementation:

```ts
// src/MongoDBDurableConnector.ts
import { DurableObject, DurableObjectState } from "cloudflare:workers";
import { MongoClient } from 'mongodb';

interface Env {
  MONGODB_URI: string;
}

export class MongoDBDurableConnector extends DurableObject {
  private env: Env;
  private client: MongoClient;

  constructor(state: DurableObjectState, env: Env) {
    super(state, env);
    this.env = env;
    this.client = new MongoClient(this.env.MONGODB_URI);
  }

  async getMovie() {
    try {
      const queryStartTime = Date.now();
      await this.client.connect();

      const database = this.client.db("sample_mflix");
      const movies = database.collection("movies");
      const query = { title: "The Room" };
      const options = {
        sort: { "imdb.rating": -1 },
        projection: { _id: 0, title: 1, imdb: 1 },
      };
      const movie = await movies.findOne(query, options);

      const queryTime = Date.now() - queryStartTime;
      return {
        movie: {
          ...movie
        },
        queryTime
      };

    } catch (error) {
      console.error('MongoDB error:', error);
      throw error;
    }
  }
}
```

Let's adapt our Worker code to be able to use either a Durable Object or the default at runtime by interpreting a query string parameter:

```ts
// src/index.ts
import { MongoDBConnector } from './MongoDBConnector';
import { MongoDBDurableConnector } from './MongoDBDurableConnector';

interface Env {
  MONGODB_URI: string;
  MY_DURABLE_OBJECT: DurableObjectNamespace<MongoDBDurableConnector>;
}

export default {
  async fetch(request: Request, env: Env, ctx: ExecutionContext): Promise<Response> {
    const { searchParams } = new URL(request.url)
    let durable = searchParams.get('durable')
    try {
      let proxy = null;

      if (durable === 'true') {
        const id = env.MY_DURABLE_OBJECT.idFromName("mongodb-connector");
        proxy = env.MY_DURABLE_OBJECT.get(id);
      } else {
        proxy = new MongoDBConnector(env);
      }

      const result = await proxy.getMovie();
      return Response.json(result);
    } catch (error) {
      console.error('Error:', error);
      const message = error instanceof Error ? error.message : 'Unknown error';
      return new Response(`Error: ${message}`, { status: 500 });
    }
  }
} satisfies ExportedHandler<Env>;

// need to export durable object from entrypoint
export { MongoDBDurableConnector };
```

We'll also need to update our `wrangler` configuration to ensure we've setup the appropriate bindings for our Durable objects:

```json
/**
 * wrangler.jsonc
 */
{
	"$schema": "node_modules/wrangler/config-schema.json",
	"name": "workers-mongodb-demo",
	"main": "src/index.ts",
	"compatibility_date": "2025-03-21",
	"compatibility_flags": [
		"nodejs_compat"
	],
	"durable_objects": {
    "bindings": [
      {
        "name": "MY_DURABLE_OBJECT",
        "class_name": "MongoDBDurableConnector"
      }
    ],
	},
	"migrations": [
    {
      "tag": "v1",
      "new_classes": [
        "MongoDBDurableConnector"
      ]
    }
  ]
}
```

Once our code is pushed and the Workers CI integration picks up the changes, we can test this out by passing `durable=true` to our Workers URL:

```
$ curl https://workers-mongodb-demo.alex-fbd.workers.dev/?durable=true
{"movie":{"title":"The Room","imdb":{"rating":3.5,"votes":25673,"id":368226}},"queryTime":317}

<repeat about 5 times>

$ curl https://workers-mongodb-demo.alex-fbd.workers.dev/?durable=true
{"movie":{"title":"The Room","imdb":{"rating":3.5,"votes":25673,"id":368226}},"queryTime":35}
```

Well that's a heck of a lot better! Using Durable Objects we were able to get the response time down almost 10x!

I ran a number of tests and periodically you'd still get a cold-start spike, but most requests benefit from the reduced latency maintaining a stateful Worker via Durable Objects provides.

It is worth calling out that Durable Objects come with some [limitations](https://developers.cloudflare.com/durable-objects/platform/limits/) such as a soft limit of 1,000 requests per second, but for _most_ use cases this is likely sufficient. I encourage you to try this out on your own and see how it works for you.