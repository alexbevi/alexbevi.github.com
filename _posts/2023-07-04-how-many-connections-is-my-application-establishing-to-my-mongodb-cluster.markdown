---
layout: post
title: "How Many Connections is My Application Establishing to My MongoDB Cluster?"
date: 2023-07-04 10:16:14 -0400
comments: true
categories: MongoDB
tags: [mongodb, connections, drivers]
image: /images/mongodb-logo.png
---

[MongoDB Atlas](https://www.mongodb.com/atlas/database) is the best way to host your MongoDB data, but it's important to be aware that like any other managed service there can be limitations. For example, MongoDB Atlas - depending on the selected tier - will impose a [connection limit](https://www.mongodb.com/docs/atlas/reference/atlas-limits/#connection-limits-and-cluster-tier).

Depending on the architecture of your application and how you've configured your [connection pools](https://www.mongodb.com/docs/manual/administration/connection-pool-overview/) it's possible you've approached or exceeded these limits before and weren't really sure why. Thankfully MongoDB Atlas provides a number of configurable alerts (such as [`Connections % of configured limit`](https://www.mongodb.com/docs/atlas/reference/alert-conditions/#mongodb-alert-Connections---of-configured-limit-is)) which can notify you if you're approaching a limit, but where are these connections coming from in the first place?

## MongoDB Drivers

Your application has been built using one of [MongoDB's Drivers](https://www.mongodb.com/docs/drivers/), which are all built according to a number of [published specifications](https://github.com/mongodb/specifications). Most noteworthy when it comes to how many connections an application may establish to a MongoDB cluster are the [Server Monitoring](https://github.com/mongodb/specifications/blob/master/source/server-discovery-and-monitoring/server-monitoring.rst) and [Connection Monitoring and Pooling](https://github.com/mongodb/specifications/blob/master/source/connection-monitoring-and-pooling/connection-monitoring-and-pooling.rst) (CMAP) specifications.

These specifications help us understand how many connections may be opened, and what variables we should be aware of that can affect these connections such as:
* Is the MongoClient single-threaded or multi-threaded
* The MongoDB Server version (>= 4.4)
* The MongoDB Driver version (does it support MongoDB Server 4.4+)

Just a quick note regarding _Connection Pools_: the default value of [`minPoolSize`](https://github.com/mongodb/specifications/blob/master/source/connection-monitoring-and-pooling/connection-monitoring-and-pooling.rst#id1) is `0`, which means that using the defaults when a _Connection Pool_ is created it will not contain any connections. For the purposes of this article I imply that at least one connection has been created in the pool and ready for use.

### Single-Threaded `MongoClient`

The MongoDB [C Driver](https://www.mongodb.com/docs/drivers/c/) and [PHP Driver](https://www.mongodb.com/docs/drivers/php/) provide single-threaded `MongoClient` implementations. As such, they do not offer connection pools at all which makes understanding how many connections can be established straightforward[^1].

![](/images/mongo-conns-01.png)
_Connections from a Single Threaded `MongoClient`_

With this configuration, a single connection (`c1`) will be established to each [replica set member](https://www.mongodb.com/docs/manual/core/replica-set-members/), or if the cluster is [Sharded](https://www.mongodb.com/docs/manual/sharding/) each [`mongos`](https://www.mongodb.com/docs/manual/core/sharded-cluster-query-router/) present in the seed list when the `MongoClient` was created[^2]. This single connection will be used for data operations as well as to perform [server monitoring](https://github.com/mongodb/specifications/blob/master/source/server-discovery-and-monitoring/server-monitoring.rst#single-threaded-monitoring).

> Note that when connecting to a Sharded Cluster using a [DNS Seed List](https://www.mongodb.com/docs/manual/reference/connection-string/#dns-seed-list-connection-format) connection string, the [`srvMaxHosts`](https://github.com/mongodb/specifications/blob/master/source/initial-dns-seedlist-discovery/initial-dns-seedlist-discovery.rst#srvmaxhosts) URI option can be configured to limit the number of `mongos`' that will be connected to.
{: .prompt-tip }

> Assuming a cluster with 3 nodes, each `MongoClient` instance would create 3 connections.
{: .prompt-info }

### MongoDB Server 4.2 and earlier (Polling Monitoring)

Prior to MongoDB 4.4, MongoDB Drivers would use a [polling protocol to perform server monitoring](https://github.com/mongodb/specifications/blob/master/source/server-discovery-and-monitoring/server-monitoring.rst#polling-protocol). This process would involve opening a dedicated [monitor thread](https://github.com/mongodb/specifications/blob/master/source/server-discovery-and-monitoring/server-monitoring.rst#monitor-thread) per host, which would be polled (by default[^3]) every 10 seconds (multi-threaded) or 60 seconds (single-threaded) to determine if the state of the host or cluster topology had changed.

![](/images/mongo-conns-02.png)

This dedicated monitor thread (`m1`) as well as a the 1 or more connections in the connection pool (`p1`) result in at least 2 connections per host. Note that if [`minPoolSize`](https://www.mongodb.com/docs/manual/reference/connection-string/#mongodb-urioption-urioption.minPoolSize) (default: 0) is > 1 this number of connections will _always_ remain open against each host a connection pool has been created for.

> Assuming a cluster with 3 nodes, each `MongoClient` instance would create 6 connections.
{: .prompt-info }
> If `minPoolSize=5` then each `MongoClient` would create 18 connections (using the formula `(minPoolSize + 1) x nodes`)
{: .prompt-tip }

### MongoDB Server 4.4 and later (Streaming Monitoring)

Starting with MongoDB 4.4, MongoDB Drivers would begin using a [streaming protocol to perform server monitoring](https://github.com/mongodb/specifications/blob/master/source/server-discovery-and-monitoring/server-monitoring.rst#streaming-protocol) - assuming those Drivers were compatible with MongoDB 4.4. The goal of this new protocol was to ensure connected applications could discover topology changes in as close to realtime as possible.

As the polling protocol only polled at fixed intervals, it was possible for topology changes to go undiscovered for upwards of 10 seconds. The streaming protocol would "push" updates from the server to the clients, as opposed to the previous "pull" model, which allowed applications to update their view of the cluster far more quickly.

![](/images/mongo-conns-03.png)

Similar to the polling protocol, a dedicated monitor thread (`m1`) will be opened per host, as well as 1 or more connections in the connection pool (`p1`). Further to these connections though a third connection (`r1`) is opened per node for [measuring RTT](https://github.com/mongodb/specifications/blob/master/source/server-discovery-and-monitoring/server-monitoring.rst#measuring-rtt) (round trip time). This is needed as the monitor thread is open and listening once established, and will only receive updates from the server as they occur. Measuring RTT require the measurement of the time taken for an operation to travel from the client to the server and back, which the streaming monitor no longer provides.

> Assuming a cluster with 3 nodes, each `MongoClient` instance would create 9 connections.
{: .prompt-info }
> If `minPoolSize=5` then each `MongoClient` would create 21 connections (using the formula `(minPoolSize + 2) x nodes`)
{: .prompt-tip }

## What if I'm using AWS Lambda?

Depending on your application's architecture, it's possible to blow past your connection limits pretty quickly. This is one reason why the documented guidance for [managing connections with AWS Lambda](https://www.mongodb.com/docs/atlas/manage-connections-aws-lambda/) has the first bullet point of _"Define the client to the MongoDB server outside the [AWS Lambda handler function](http://docs.aws.amazon.com/lambda/latest/dg/nodejs-prog-model-handler.html)"_.

If each Lambda function were to connect to a MongoDB 4.4+ cluster using a connection string of `mongodb+srv://xxx.mongodb.net/?minPoolSize=5` and the cluster only had 3000 connections configured, within 150 near-concurrent function executions the cluster could potentially reach the connection limit! This is obviously an extreme scenario, but is meant to help illustrate the impact creating many `MongoClient` instances can potentially have on your cluster.

I plan on going into much more detail regarding AWS Lambda and MongoDB connection behavior in a future article.
----

[^1]: <small>The MongoDB C driver has two connection modes: single-threaded and [pooled](https://mongoc.org/libmongoc/current/connection-pooling.html#pooled-mode). Single-threaded mode is optimized for embedding the driver within languages like PHP. Multi-threaded programs should use pooled mode: this mode minimizes the total connection count, and in pooled mode background threads monitor the MongoDB server topology, so the program need not block to scan it.</small>
[^2]: <small>`MongoClient`s created using a [DNS Seed List](https://www.mongodb.com/docs/manual/reference/connection-string/#dns-seed-list-connection-format) connection string can [poll the `SRV` record to discover additional `mongos`'](https://github.com/mongodb/specifications/blob/master/source/polling-srv-records-for-mongos-discovery/polling-srv-records-for-mongos-discovery.rst)</small>
[^3]: <small>Polling interval can be configured via the [`heartbeatFrequencyMS`](https://github.com/mongodb/specifications/blob/master/source/server-discovery-and-monitoring/server-monitoring.rst#heartbeatfrequencyms) URI option, but must be more than the [`minHeartbeatFrequencyMS`](https://github.com/mongodb/specifications/blob/master/source/server-discovery-and-monitoring/server-monitoring.rst#minheartbeatfrequencyms) of 500ms. In MongoDB Atlas environments the `heartbeatFrequencyMS` is lowered from the default (10000) to 5000.
