---
layout: post
title: "Bug Hunting with the MongoDB Haskell Community"
date: 2022-09-21 06:21:02 -0400
comments: true
categories: MongoDB
published: true
tags: ["drivers", "haskell", "mongodb"]
image:
  src: /images/mongodb-logo.png
  alt: MongoDB Logo
---

MongoDB currently maintains 10 programming language [Drivers](https://www.mongodb.com/docs/drivers/) in-house, including a [Ruby](https://www.mongodb.com/docs/ruby-driver/current/) driver for which I'm presently the Product Manager. Additionally we also have a library of [community maintained drivers](https://www.mongodb.com/docs/drivers/community-supported-drivers/), built using the [MongoDB Driver specifications](https://github.com/mongodb/specifications/tree/master/source) our engineers maintain and publish.

It was brought to my attention that one of these community drivers - the [Haskell driver](https://github.com/mongodb-haskell/mongodb) - was experiencing an issue whereby queries were no longer returning results from the [MongoDB Atlas](https://www.mongodb.com/docs/atlas/) clusters their applications were connected to.

Though I've never worked with [Haskell](https://www.haskell.org/), before joining the team I worked in [Technical Services]({% post_url 2018-10-01-technical-services-engineering-at-mongodb %}) providing support for customers experiencing problems with their applications via our drivers. This seemed like an interesting problem we could hopefully solve for our developer community so I'd like to share the diagnostic journey that lead us to the issue and ultimately enabled a resolution.

## Overview

When [Adrien](https://github.com/why-not-try-calmer) first reported [issue #131 on GitHub](https://github.com/mongodb-haskell/mongodb/issues/131) the initial assessment was that their application could successfully connect to a MongoDB Atlas cluster and write new content, but when trying to read those results back the result set was always empty. This had happened suddenly causing existing applications and workloads to break however no new code had been introduced which could potentially be the culprit.

As I'm unfamiliar with Haskell Adrien kindly provided a [Dockerized reproduction](https://github.com/why-not-try-calmer/test-mongo) I could use to test this issue against my own Atlas clusters. This reproduction would write 3 documents to a collection, then try to read 3 documents back. To begin testing I setup an M10 cluster and ran the tests a few times.

```
Failures:

  src/Lib.hs:101:33:
  1) Reads Ensures reads work
       expected: 3
        but got: 9
```

Each time I ran the test it would fail, but the number of documents in the _"Ensures reads work"_ that were received kept increasing. The cluster I was testing on was a dedicated cluster, however MongoDB Atlas also offers free and shared tier clusters so for completeness of testing I configured an M0 next and re-ran the tests.

```
Failures:

  src/Lib.hs:101:33:
  1) Reads Ensures reads work
       expected: 3
        but got: 0
```

No matter how many times I ran the tests against my M0 (also tested M2 and M5) the results were always 0.

Just to make sure this wasn't a larger issue I tested with a script that uses the Ruby driver against an M0 cluster to verify the behavior didn't reproduce there:

```ruby
require 'bundler/inline'

gemfile do
  source 'https://rubygems.org'
  gem 'mongo'
end

client = Mongo::Client.new('mongodb+srv://....mongodb.net/test')
collection = client[:foo]
collection.drop

puts "Found #{collection.find.to_a.length} documents"
# => Found 0 documents

collection.insert_many([].fill({ "bar": "baz" },0,3))
puts "Found #{collection.find.to_a.length} documents"
# => Found 3 documents
```

The script would produce the expected result, which further pointed to a potential issue on the Atlas side that was specific to free and shared tier clusters.

MongoDB Atlas imposes some [limitations on free and shared tier](https://www.mongodb.com/docs/atlas/reference/free-shared-limitations/) clusters, which in some cases are enforced by a proxy layer between the application and the underlying infrastructure backing the cluster.

## Analysis

Now that the issue was narrowed down, working with a Cloud Operations Engineer to create an isolated M2 cluster in a development environment, we increased the [log verbosity](https://www.mongodb.com/docs/manual/reference/log-messages/#verbosity-levels) for that cluster for [`QUERY`](https://www.mongodb.com/docs/manual/reference/log-messages/#mongodb-data-QUERY) and [`COMMAND`](https://www.mongodb.com/docs/manual/reference/log-messages/#mongodb-data-COMMAND) log components.

With this information, when we download logs for the node our test is targeting we should be able to get a lot more information as to what was being executed and where it might be failing.

```js
// Test #1
{"t":{"$date":"2022-08-18T11:19:16.985+00:00"},"s":"D2", "c":"COMMAND",  "id":5578800, "ctx":"conn24194","msg":"Deprecated operation requested. The client driver may require an upgrade in order to ensure compatibility with future server versions. For more details see https://dochub.mongodb.org/core/legacy-opcode-compatibility","attr":{"op":"query","clientInfo":{"driver":{"name":"mongo-go-driver","version":"v1.7.2+prerelease"},"os":{"type":"linux","architecture":"arm64"},"platform":"go1.18.2","application":{"name":"Atlas Proxy v20220824.0.0.1660656950"}}}}
{"t":{"$date":"2022-08-18T11:19:16.986+00:00"},"s":"D2", "c":"QUERY",    "id":20914,   "ctx":"conn24194","msg":"Running query","attr":{"query":"ns: 62fe1f7d37518e1c32149694_haskell.test123 query: { comment: { AtlasProxyAppName: \"\", AtlasProxyClientMetadata: {} } } sort: {} projection: {}"}}
{"t":{"$date":"2022-08-18T11:19:16.986+00:00"},"s":"D5", "c":"QUERY",    "id":20917,   "ctx":"conn24194","msg":"Not caching executor but returning results","attr":{"numResults":0}}
```

Based on log analysis we could not only verify the issue existed, but why it was affecting these operations from the Haskell driver:

**A deprecated operation was being run**

MongoDB uses a [wire protocol](https://www.mongodb.com/docs/manual/reference/mongodb-wire-protocol/) when sending/receiving messages internally and externally (via Drivers). Initially a number of [opcodes](https://www.mongodb.com/docs/manual/reference/mongodb-wire-protocol/#opcodes) existed, but starting with MongoDB 5.0 most of these were deprecated in favor of [`OP_MSG`](https://www.mongodb.com/docs/manual/reference/mongodb-wire-protocol/#op_msg).

Prior to MongoDB 3.6 when [`OP_MSG` was introduced](https://www.mongodb.com/docs/v5.0/release-notes/3.6/#wire-protocol-and-compression) to subsume existing opcodes, query operations were executed via [`OP_QUERY`](https://www.mongodb.com/docs/manual/legacy-opcodes/#op_query), which the Haskell driver is apparently still using for query execution.

Note that though `OP_QUERY` is deprecated, it would still be supported in the version of MongoDB we were testing (5.0) and as such is not the cause of this problem.

**The logs confirm no results are being returned by the query**

At the default level, the [Database Profiler](https://www.mongodb.com/docs/manual/tutorial/manage-the-database-profiler/) will only output queries to the `mongod` logs if they exceed the slow query threshold ([`slowms`](https://www.mongodb.com/docs/manual/reference/method/db.setProfilingLevel/#std-label-set-profiling-level-options-slowms)) of 100ms. The tests we were running would likely have completed in under 10ms, which prevented anything useful from being logged.

> `{"t":{"$date":"2022-08-18T11:19:16.986+00:00"},"s":"D5", "c":"QUERY",    "id":20917,   "ctx":"conn24194","msg":"Not caching executor but returning results","attr":{"numResults":0}}`

Once the log level was increased it was apparent that the operation in question was being executed, but was not returning any results.

**The logs highlight an issue with the query itself**

With the log level increased however the `QUERY` component logs showed clearly that not only were no results being returned, but the query _shape_ that was being sent to the server didn't match what we expected:

> `{"t":{"$date":"2022-08-18T11:19:16.986+00:00"},"s":"D2", "c":"QUERY",    "id":20914,   "ctx":"conn24194","msg":"Running query","attr":{"query":"ns: 62fe1f7d37518e1c32149694_haskell.test123 query: { comment: { AtlasProxyAppName: \"\", AtlasProxyClientMetadata: {} } } sort: {} projection: {}"}}`

It appeared that the query's filter - which we expected to be empty - was in fact filtering for `comment: { AtlasProxyAppName: "", AtlasProxyClientMetadata: {} }`. Since none of the sample documents that were being created as part of this test matched these criteria, the query returned 0 results.

## Findings

From our log analysis it would appear our operations were being rewritten to append a filter criteria for a `comment` field with a value of `{ AtlasProxyAppName: "", AtlasProxyClientMetadata: {} }`. As `comment` has a specific meaning within the context of MongoDB commands it was becoming apparent what the issue was and where it may have originated.

Starting with [MongoDB 4.4, a `comment` option was added to all database commands](https://www.mongodb.com/docs/manual/release-notes/4.4/#comment-option-available-to-all-database-commands) (see [SERVER-29794](https://jira.mongodb.org/browse/SERVER-29794)).
This was not be confused with the [`$comment` meta operator](https://www.mongodb.com/docs/v4.2/reference/operator/meta/comment/) that has been available [since MongoDB 2.0](https://jira.mongodb.org/browse/SERVER-2515) for propagating metadata to query logs.

The Atlas team introduced a feature (released `2022-06-22`) that would utilize these comments to improve the [`currentOp`](https://www.mongodb.com/docs/manual/reference/command/currentOp/) output in free/shared clusters. As all "official" MongoDB Drivers communicate with modern MongoDB clusters using `OP_MSG`, when this feature was being tested there were no issues.

Unfortunately, drivers that still use `OP_QUERY` to make queries were negatively impacted as a result of the metadata comment injection occurring in the filter instead of one level above as is the case for `OP_MSG`.

Now that the issue could be verified, additional logic was introduced to use the `$comment` meta operator if an `OP_QUERY` was detected instead of improperly applying a `comment` option.

## Outcome

With the assistance of the Haskell community we were able to identify and address a deficiency in the free and shared tiers of MongoDB Atlas. The fix for this was released in version `8ed75a4810@v20220914` on 2022-09-21, and any Haskell application using the community maintained Haskell driver should have started working as expected without the need for additional intervention.

We truly appreciate the investment our developer communities make when they put time and effort into building something as powerful as a MongoDB driver and want to ensure we do what we can to offer assistance if possible.

<div class="note info">
<small><em>Cross posted to <a href="https://dev.to/alexbevi/bug-hunting-with-the-mongodb-haskell-community-469j">DEV</a></em></small>
</div>