---
layout: post
title: "querySrv errors when connecting to MongoDB Atlas"
date: 2023-11-13 14:42:13 -0500
comments: true
categories: [MongoDB]
tags: [mongodb, drivers, networking, connections]
image: /images/mongodb-logo.png
---

> **Updated: January 26, 2026**
> ```
> Error: querySrv ECONNREFUSED _mongodb._tcp.<cluster>.mongodb.net
>    at QueryReqWrap.onresolve [as oncomplete] (node:internal/dns/promises:294:17)
> ```    
> If you're seeing this error on Node.js v24 and you're on a Windows system, the issue may be due to Node not always using the Windows system DNS resolver. In this case you need to force DNS servers explicitly **before connecting to MongoDB** as follows:
> ```js
> require("node:dns/promises").setServers(["1.1.1.1", "8.8.8.8"]);
> ```
> Credit to this [Stack Overflow question](https://stackoverflow.com/questions/79873598/mongodb-atlas-srv-connection-fails-with-querysrv-econnrefused-after-switching-no)
{: .prompt-tip }

> **Updated: February 11, 2026**
> 
> [dns: fix Windows SRV ECONNREFUSED regression by correcting c-ares fallback detection #61453](https://github.com/nodejs/node/pull/61453) has been merged and will be available in Node.js v25.6.1, as well as backported to Node.js v24
{: .prompt-tip }

If your application us
es MongoDB's [Node.js driver](https://www.mongodb.com/docs/drivers/node/current/) or [Mongoose ODM](https://mongoosejs.com/), occasionally you may observe errors such as `querySrv ECONNREFUSED _mongodb._tcp.cluster0.abcde.mongodb.net` or `Error: querySrv ETIMEOUT _mongodb._tcp.cluster0.abcde.mongodb.net` being thrown. The MongoDB Atlas documentation outlines several methods to [troubleshoot connection issues](https://www.mongodb.com/docs/atlas/troubleshoot-connection/), including how to handle ["Connection Refused using SRV Connection String"](https://www.mongodb.com/docs/atlas/troubleshoot-connection/#connection-refused-using-srv-connection-string) scenarios, but why does this happen in the first place?

## About DNS seedlists

To coincide with the release of MongoDB 3.6, all drivers (at the time) implemented the [initial DNS seedlist discovery](https://github.com/mongodb/specifications/blob/master/source/initial-dns-seedlist-discovery/initial-dns-seedlist-discovery.rst) specification to ensure connections could be established using the new [`SRV` connection string format](https://www.mongodb.com/docs/manual/reference/connection-string/#std-label-connections-dns-seedlist), as well as the legacy [standard connection string format](https://www.mongodb.com/docs/manual/reference/connection-string/#standard-connection-string-format).

This functionality was introduced to abstract away the complexity of MongoDB's connection strings (for MongoDB Atlas users at least) by moving the component parts of a [connection string](https://www.mongodb.com/docs/manual/reference/connection-string/) to two DNS records: a [service record (`SRV`)](https://en.wikipedia.org/wiki/SRV_record) and a [text record (`TXT`)](https://en.wikipedia.org/wiki/TXT_record).

Users now only need to supply a connection string such as `mongodb+srv://<username>:<password>@cluster0.abcde.mongodb.net/myFirstDatabase`, and regardless as to whether the underlying cluster was a replica set or sharded, the connection string would remain the same. Furthermore, use of `mongodb+srv://` enables drivers to detect additions/removals of `mongos` in a sharded cluster[^1]

Tools such as [`nslookup`](https://linux.die.net/man/1/nslookup) or [`dig`](https://linux.die.net/man/1/dig) can be used to view the contents of these DNS records, such as in the following example:

```bash
$ dig srv _mongodb._tcp.cluster0.abcde.mongodb.net

; <<>> DiG 9.18.18-0ubuntu0.22.04.1-Ubuntu <<>> srv _mongodb._tcp.cluster0.abcde.mongodb.net
;; global options: +cmd
;; Got answer:
;; ->>HEADER<<- opcode: QUERY, status: NOERROR, id: 24529
;; flags: qr rd ra; QUERY: 1, ANSWER: 3, AUTHORITY: 0, ADDITIONAL: 1

;; OPT PSEUDOSECTION:
; EDNS: version: 0, flags:; udp: 65494
;; QUESTION SECTION:
;_mongodb._tcp.cluster0.abcde.mongodb.net. IN SRV

;; ANSWER SECTION:
_mongodb._tcp.cluster0.abcde.mongodb.net. 60 IN SRV 0 0 27017 cluster0-shard-00-01.abcde.mongodb.net.
_mongodb._tcp.cluster0.abcde.mongodb.net. 60 IN SRV 0 0 27017 cluster0-shard-00-02.abcde.mongodb.net.
_mongodb._tcp.cluster0.abcde.mongodb.net. 60 IN SRV 0 0 27017 cluster0-shard-00-00.abcde.mongodb.net.

$ dig txt cluster0.abcde.mongodb.net

; <<>> DiG 9.18.18-0ubuntu0.22.04.1-Ubuntu <<>> txt cluster0.abcde.mongodb.net
;; global options: +cmd
;; Got answer:
;; ->>HEADER<<- opcode: QUERY, status: NOERROR, id: 35223
;; flags: qr rd ra; QUERY: 1, ANSWER: 1, AUTHORITY: 0, ADDITIONAL: 1

;; OPT PSEUDOSECTION:
; EDNS: version: 0, flags:; udp: 65494
;; QUESTION SECTION:
;cluster0.abcde.mongodb.net.	IN	TXT

;; ANSWER SECTION:
cluster0.abcde.mongodb.net. 60 IN	TXT	"authSource=admin&replicaSet=atlas-abcde-shard-0"
```

## What can go wrong?

MongoDB's drivers require the information from _both_ DNS queries in order to successfully establish, authenticate and authorize a connection to a MongoDB Atlas cluster. If either of these queries fail, only part of the connection string details will be present, and if the driver doesn't error out right away, the subsequent connection attempt may be missing necessary information.

For example, per the [Authentication specification](https://github.com/mongodb/specifications/blob/master/source/auth/auth.rst#implementation) regarding connection string options, when it comes to selecting the authentication source:
1. if [`authSource`](https://www.mongodb.com/docs/manual/reference/connection-string/#mongodb-urioption-urioption.authSource) is specified, it is used.
2. otherwise, if database is specified (in the connection string), it is used.
3. otherwise, the `admin` database is used.

Given this order of operations, if the `SRV` record resolves, but the `TXT` record _doesn't_, assuming the driver doesn't error out first the database provided in the connection string will be used for authentication. Using our original example of `mongodb+srv://<username>:<password>@cluster0.abcde.mongodb.net/myFirstDatabase`, the `myFirstDatabase` database will be used to authenticate .... which will result in an authentication failure such as `MongoServerError: Authentication failed`.

Furthermore, though MongoDB's drivers support automatic retryability of [reads](https://www.mongodb.com/docs/manual/core/retryable-reads/) and [writes](https://www.mongodb.com/docs/manual/core/retryable-writes/), these DNS query failures aren't retryable. There is currently a project proposed ([DRIVERS-2757](https://jira.mongodb.org/browse/DRIVERS-2757)) to improve this in the future, but for now these errors bubble up to the application immediately.

## Can these issues be prevented?

The best way to avoid these issues entirely is to just use the legacy [standard connection string format](https://www.mongodb.com/docs/manual/reference/connection-string/#standard-connection-string-format). If you're connecting to a replica set, the [server discovery and monitoring](https://github.com/mongodb/specifications/blob/master/source/server-discovery-and-monitoring/server-discovery-and-monitoring.rst) functionality of each driver will ensure topology changes are automatically discovered.

Note that this will prevent new `mongos`' from being discovered in a sharded cluster, however if you don't anticipate these to change frequently this will likely be a non-issue as well.

## Are other drivers affected?

Failure to resolve DNS records can affect all MongoDB drivers, however it's highly unlikely you'll actually encounter this in a production setting. As there still remains a non-zero chance this issue will manifest, here are some examples of failures you may see from other drivers:

### Ruby driver

```
Mongo::Error::NoSRVRecords: The DNS query returned no SRV records for 'cluster0.abcde.mongodb.net'
```

### Java driver or Spring Boot MongoDB

```
# Example 1
Caused by: com.mongodb.MongoTimeoutException: Timed out after 30000 ms while waiting to connect. Client view of cluster state is {type=UNKNOWN, srvResolutionException=com.mongodb.MongoConfigurationException: Unable to look up SRV record for host cluster0-shard-00-01.abcde.mongodb.net, servers=[]}


# Example 2
Caused by: com.mongodb.MongoConfigurationException: Unable to look up SRV record for host cluster0.abcde.mongodb.net
        at com.mongodb.internal.dns.DnsResolver.resolveHostFromSrvRecords(DnsResolver.java:79)
        at com.mongodb.ConnectionString.<init>(ConnectionString.java:321)
        at com.mongodb.MongoClientURI.<init>(MongoClientURI.java:234)
```

### Python driver

```
# Example 1
pymongo.errors.ConfigurationError: The DNS query name does not exist: _mongodb._tcp.cluster0.abcde.mongodb.net.

# Example 2
Exception has occurred: ConfigurationError
The DNS operation timed out after 20.001205682754517 seconds
dns.exception.Timeout: The DNS operation timed out after 20.001205682754517 seconds
```

### C#/.NET driver

```
# Example 1
cluster0.abcde.mongodb.net IN TXT on x.x.x.x:53 timed out or is a transient error. A connection attempt failed because the connected party did not properly respond after a period of time, or established connection failed because connected host has failed to respond.

# Example 2
DnsClient.DnsResponseException:
at DnsClient.LookupClient.ResolveQuery (DnsClient, Version=1.6.0.0, Culture=neutral, PublicKeyToken=4574bb5573c51424)
at DnsClient.LookupClient.QueryInternal (DnsClient, Version=1.6.0.0, Culture=neutral, PublicKeyToken=4574bb5573c51424)
at DnsClient.LookupClient.Query (DnsClient, Version=1.6.0.0, Culture=neutral, PublicKeyToken=4574bb5573c51424)
at MongoDB.Driver.Core.Misc.DnsClientWrapper.ResolveTxtRecords (MongoDB.Driver.Core, Version=2.15.1.0, Culture=neutral, PublicKeyToken=null)
at MongoDB.Driver.Core.Configuration.ConnectionString.Resolve (MongoDB.Driver.Core, Version=2.15.1.0, Culture=neutral, PublicKeyToken=null)
at MongoDB.Driver.MongoUrl.Resolve (MongoDB.Driver, Version=2.15.1.0, Culture=neutral, PublicKeyToken=null)
at MongoDB.Driver.MongoClientSettings.FromUrl (MongoDB.Driver, Version=2.15.1.0, Culture=neutral, PublicKeyToken=null)

# Example 3
System.TimeoutException: A timeout occured after 30000ms selecting a server using CompositeServerSelector{ Selectors = MongoDB.Driver.MongoClient+AreSessionsSupportedServerSelector, LatencyLimitingServerSelector{ AllowedLatencyRange = 00:00:00.0200000 } }. Client view of cluster state is { ClusterId : "1", ConnectionMode : "Automatic", Type : "Unknown", State : "Disconnected", Servers : [], DnsMonitorException : "DnsClient.DnsResponseException: Query 54148 => _mongodb._tcp.cluster0.abcde.mongodb.net IN SRV on x.x.x.x:53 timed out or is a transient error.
 ---> System.Net.Sockets.SocketException (110): Connection timed out
   at System.Net.Sockets.Socket.Receive(Byte[] buffer, Int32 offset, Int32 size, SocketFlags socketFlags)
   at DnsClient.DnsUdpMessageHandler.Query(IPEndPoint server, DnsRequestMessage request, TimeSpan timeout)
   at DnsClient.LookupClient.ResolveQuery(IReadOnlyList`1 servers, DnsQuerySettings settings, DnsMessageHandler handler, DnsRequestMessage request, LookupClientAudit audit)
   --- End of inner exception stack trace ---
   at DnsClient.LookupClient.ResolveQuery(IReadOnlyList`1 servers, DnsQuerySettings settings, DnsMessageHandler handler, DnsRequestMessage request, LookupClientAudit audit)
   at DnsClient.LookupClient.QueryInternal(DnsQuestion question, DnsQuerySettings queryOptions, IReadOnlyCollection`1 servers)
   at DnsClient.LookupClient.Query(DnsQuestion question)
   at DnsClient.LookupClient.Query(String query, QueryType queryType, QueryClass queryClass)
```

### PHP driver

```
Fatal error: Uncaught MongoDB\Driver\Exception\InvalidArgumentException: Failed to parse URI options: Failed to look up SRV record "_mongodb._tcp.cluster0.abcde.mongodb.net": The requested name is valid but does not have an IP address.
```

### Go driver

```
error parsing command line options: error parsing uri: lookup cluster0.abcde.mongodb.net on x.x.x.x:53: cannot unmarshal DNS message
```

Note that (per the [MongoDB Go driver documentation](https://pkg.go.dev/go.mongodb.org/mongo-driver/mongo#hdr-Potential_DNS_Issues)):
> Building with Go 1.11+ and using connection strings with the `mongodb+srv` scheme is unfortunately incompatible with some DNS servers in the wild due to the change introduced in https://github.com/golang/go/issues/10622. You may receive an error with the message "cannot unmarshal DNS message" while running an operation when using DNS servers that non-compliantly compress SRV records. Old versions of `kube-dns` and the native DNS resolver (`systemd-resolver`) on Ubuntu 18.04 are known to be non-compliant in this manner. We suggest using a different DNS server (8.8.8.8 is the common default), and, if that's not possible, avoiding the `mongodb+srv` scheme.

## DNS is hard ...

It sure can be, as intermittent/transient network events can also impact MongoDB drivers' ability to resolve DNS queries. The drivers (typically) rely on low-level OS APIs (such as [`getaddrinfo`](https://linux.die.net/man/3/getaddrinfo)) for network address and service translation. As such you may occasionally get errors such as `MongooseServerSelectionError: getaddrinfo EAI_AGAIN cluster0-shard-00-01.abcde.mongodb.net` even when using the legacy (`mongodb://`) URI scheme.

--------------

**Footnotes**

[^1]: <small>Sharded clusters could detect additions/removals of `mongos`' if the driver(s) have implemented the [polling `SRV` records for `mongos` discovery](https://github.com/mongodb/specifications/blob/master/source/polling-srv-records-for-mongos-discovery/polling-srv-records-for-mongos-discovery.rst) specification</small>
