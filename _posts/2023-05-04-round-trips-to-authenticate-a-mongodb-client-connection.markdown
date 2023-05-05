---
layout: post
title: "Round Trips to Authenticate a MongoDB Client Connection"
date: 2023-05-04 14:40:52 -0400
comments: true
categories: MongoDB
tags: [mongodb, connections, drivers]
image:
  src: /images/mongodb-logo.png
  alt: MongoDB Logo
---

When [MongoDB Drivers](https://www.mongodb.com/docs/drivers/) establish a connection with a MongoDB cluster a number of network round trips are performed. This can result in increased latency when measuring the time to response of an operation following a cold start, so it's worth understanding what the anatomy of an authenticated connection is - as well as what can be done to improve an initial operations round trip time (RTT).

# Current State

![](/images/mongo-auth-01.png)


## Connection Protocol

Typically a MongoDB connection string will contain a [standard seed list](https://www.mongodb.com/docs/manual/reference/connection-string/#std-label-connections-standard-connection-string-format), which is represented by the `mongodb://` protocol followed by a list of server (ex: `mongodb://localhost:27017,localhost:27018....`).

Starting with MongoDB 3.6 instead of having to provide the seed list in the connection string manually a [DNS-constructed seed list](https://www.mongodb.com/docs/manual/reference/connection-string/#std-label-connections-dns-seedlist) could be used as well. With this configuration the `mongodb+srv://` protocol is used to communicate both the seed list as well as any options by performing two (2) DNS queries to resolve the following DNS records: [`SRV`](https://en.wikipedia.org/wiki/SRV_record) and [`TXT`](https://en.wikipedia.org/wiki/TXT_record).

See [_"MongoDB 3.6: Here to SRV you with easier replica set connections"_](https://www.mongodb.com/blog/post/mongodb-3-6-here-to-srv-you-with-easier-replica-set-connections) for more information regarding this topic.

Note that [DNS Caching](https://www.cloudns.net/blog/dns-cache-explained/) will likely improve the performance of these queries, but it's worth noting their presence within the connection establishment and authentication lifecycle.

```js
/* Network Round Trips */
  (0 | 2) // Protocol
```

## TCP Handshake

![](/images/mongo-auth-03.png)
_Source: [makeuseof.com](https://www.makeuseof.com/what-is-three-way-handshake-how-does-it-work/)_

Once a host is known from the seed list, next we need to connect to it. This is done using a standard [TCP 3-way Handshake](https://www.geeksforgeeks.org/tcp-3-way-handshake-process/), which constitutes 1 RTT. Note that As there is an `ACK` sent following the `SYN/ACK` this handshake is sometimes considered to be [1.5 RTT](https://networkengineering.stackexchange.com/a/76369).

```js
/* Network Round Trips */
  (0 | 2) // Protocol
+  1      // TCP
```
## TLS Handshake

![](/images/mongo-auth-02.png)
_Source: [cloudflare.com](https://www.cloudflare.com/en-gb/learning/ssl/what-happens-in-a-tls-handshake/)_

To ensure all connections to [MongoDB Atlas](https://www.mongodb.com/atlas/database) are secure, [Transport Layer Security (TLS)](https://en.wikipedia.org/wiki/Transport_Layer_Security) is enabled by default. Following a successful TCP handshake, a [TLS handshake](https://www.cloudflare.com/en-gb/learning/ssl/what-happens-in-a-tls-handshake/) will be performed.

```js
/* Network Round Trips */
  (0 | 2) // Protocol
+  1      // TCP
+  2      // TLS
```

## MongoDB Handshake

Now that we have established a TLS secured TCP socket connection to a MongoDB host (`mongos` or `mongod`), the MongoDB Driver will send a [`hello`](https://www.mongodb.com/docs/manual/reference/command/hello/) command to perform [the initial handshake](https://github.com/mongodb/specifications/blob/master/source/mongodb-handshake/handshake.rst).

This step is required to determine that the host at the other end of the socket is actually a MongoDB server. Assuming the version of the MongoDB Driver supports MongoDB 4.4+ the handshake will also include a [`speculativeAuthenticate`](https://github.com/mongodb/specifications/blob/master/source/mongodb-handshake/handshake.rst#speculative-authentication) argument. Specifying this argument to `hello` will speculatively include the first command of an authentication handshake, thus eliminating one round trip as the `saslStart` command doesn't need to be sent during the authentication handshake.

```js
/* Network Round Trips */
  (0 | 2) // Protocol
+  1      // TCP
+  2      // TLS
+  1      // MongoDB
```

## Authentication Handshake

MongoDB supports a number of [SASL (Simple Authentication and Security Layer)](https://en.wikipedia.org/wiki/Simple_Authentication_and_Security_Layer). By default the SASL mechanism that will be used will be a [SCRAM](https://www.mongodb.com/docs/manual/core/security-scram/) mechanism (either `SCRAM-SHA-1` or `SCRAM-SHA-256`), which effectively means "username and password".

As outlined in the [MongoDB Authentication specification](https://github.com/mongodb/specifications/blob/master/source/auth/auth.rst#id8), a `SCRAM-SHA-256` conversation will be made up of 2 round trips as follows:

```js
>> {saslStart: 1, mechanism:"SCRAM-SHA-256", options: {skipEmptyExchange: true}, payload: BinData(0, "...=")}
<< {conversationId: 1, payload: BinData(0, "...="), done: false, ok: 1}
>> {saslContinue: 1, conversationId: 1, payload: BinData(0, "...==")}
<< {conversationId: 1, payload: BinData(0, "...=="), done: true, ok: 1}
```

For [backwards compatibility](https://github.com/mongodb/specifications/blob/master/source/auth/auth.rst#backwards-compatibility) with MongoDB 4.2 or earlier, MongoDB Drivers support a longer `SCRAM` conversation which includes an additional `saslContinue` command being sent as follows:

```js
>> {saslStart: 1, mechanism: "SCRAM-SHA-1", payload: BinData(0, "..."), options: {skipEmptyExchange: true}}
<< {conversationId : 1, payload: BinData(0,"..."), done: false, ok: 1}
>> {saslContinue: 1, conversationId: 1, payload: BinData(0, "...")}
<< {conversationId: 1, payload: BinData(0,"..."), done: false, ok: 1}
>> {saslContinue: 1, conversationId: 1, payload: BinData(0, "")}
<< {conversationId: 1, payload: BinData(0,""), done: true, ok: 1}
```

RTT was improved with MongoDB 4.4+ as 2 round trips can potentially be avoided:

1. when `speculativeAuthenticate` is used the `saslStart` command is incorporated into the initial MongoDB handshake
2. when the `saslStart` command contains the `skipEmptyExchange: true` option, the second `saslContinue` command can be skipped

```js
/* Network Round Trips */
  (0 | 2) // Protocol
+  1      // TCP
+  2      // TLS
+  1      // MongoDB
+ (2 | 3) // Authentication
```

# Reducing Round Trips

As outlined above there are a number of network round trips required to authenticate a client connection to a MongoDB host using a username and password:

```js
/* Network Round Trips */
  (0 | 2) // Protocol
+  1      // TCP
+  2      // TLS
+  1      // MongoDB
+ (2 | 3) // Authentication
---------------------------
(6 | 7 | 8 | 11)
```

MongoDB 4.4 has been out since at least [September 2020](https://www.mongodb.com/docs/manual/release-notes/4.4/#4.4.1---sep-9--2020), so chances are most applications are connecting to at least this version or newer. This would put the average round trip count for authenticating a connection at 6 or 8 (depending on what protocol is being used).

Next let's review what can be done to reduce these round trips where possible.

## Use x.509 Authentication

When using [x.509 certificates to authenticate clients](https://www.mongodb.com/docs/manual/tutorial/configure-x509-client-authentication/), the [conversation](https://github.com/mongodb/specifications/blob/master/source/auth/auth.rst/#mongodb-x509) with the server does not require a `saslContinue`. Assuming this `speculativeAuthenticate` of the initial handshake succeeds (which it should), two full round trip can be removed!

```js
/* Network Round Trips */
  (0 | 2) // Protocol
+  1      // TCP
+  2      // TLS
+  1      // MongoDB
+  0      // Authentication
---------------------------
(4 | 6)
```

## Use TLS 1.3+

![](/images/mongo-auth-04.jpg)
_Source: [thesslstore.com](https://www.thesslstore.com/blog/tls-1-3-handshake-tls-1-2/)_

TLS 1.3 ([RFC 8446](https://datatracker.ietf.org/doc/html/rfc8446)) can authenticate a connection approximately twice as fast as TLS 1.2 ([RFC 5246](https://datatracker.ietf.org/doc/html/rfc5246)) by eliminating a full round trip. TLS 1.3 helps speed up encrypted connections using features such as [TLS false start](https://blogs.windows.com/msedgedev/2016/06/15/building-a-faster-and-more-secure-web-with-tcp-fast-open-tls-false-start-and-tls-1-3/) and [Zero Round Trip Time (0-RTT)](https://blog.cloudflare.com/introducing-0-rtt/).


```js
/* Network Round Trips */
  (0 | 2) // Protocol
+  1      // TCP
+  1      // TLS
+  1      // MongoDB
+ (0 - 3) // Authentication
---------------------------
(3 - 8)
```

# Conclusion

In some environments (such as [Function as a Service](https://en.wikipedia.org/wiki/Function_as_a_service)) the cold start time of an application is critically important. The time to authenticate a connection to a MongoDB host and how this can be improved can be useful in improving operational latency of applications.

Out of the box there may be upwards of 8 network round trips (`SRV+TCP+TLS+MONGODB+AUTH`), however this can potentially be cut in half (or more) by understanding what configuration and authentication options exist and how they can be applied.