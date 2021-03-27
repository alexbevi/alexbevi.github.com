---
layout: post
title: "What is MongoDB FTDC (aka. diagnostic.data)"
date: 2020-01-26 18:14:50 -0500
comments: true
categories: [mongodb]
---

[Full Time Diagnostic Data Capture (FTDC)](https://docs.mongodb.com/manual/administration/analyzing-mongodb-performance/#full-time-diagnostic-data-capture) was introduced in MongoDB 3.2 (via [SERVER-19585](https://jira.mongodb.org/browse/SERVER-19585)), to incrementally collect the results of certain diagnostic commands to assist MongoDB support with troubleshooting issues.

On log rotation or startup, a `mongod` or `mongos` will collect and log:

- [`getCmdLineOpts`](https://docs.mongodb.com/manual/reference/command/getCmdLineOpts/): `db.adminCommand({getCmdLineOpts: true})`
- [`buildInfo`](https://docs.mongodb.com/manual/reference/command/buildInfo/): `db.adminCommand({buildInfo: true})`
- [`hostInfo`](https://docs.mongodb.com/manual/reference/command/hostInfo/): `db.adminCommand({hostInfo: true})`

As configured by [`diagnosticDataCollectionPeriodMillis`](https://docs.mongodb.com/manual/reference/parameters/index.html#param.diagnosticDataCollectionPeriodMillis) and defaulting to every 1 second, FTDC will collect the output of the following commands:

- [`serverStatus`](https://docs.mongodb.com/manual/reference/command/serverStatus/): `db.serverStatus({tcmalloc: true})`
- [`replSetGetStatus`](https://docs.mongodb.com/manual/reference/command/replSetGetStatus/): `rs.status()`
- [`collStats`](https://docs.mongodb.com/manual/reference/command/collStats/) for the [`local.oplog.rs`](https://docs.mongodb.com/manual/reference/local-database/#local.oplog.rs) collection ([mongod](https://docs.mongodb.com/manual/reference/program/mongod/#bin.mongod) only)
- [`connPoolStats`](https://docs.mongodb.com/manual/reference/command/connPoolStats/#dbcmd.connPoolStats) ([mongos](https://docs.mongodb.com/manual/reference/program/mongos/#bin.mongos) only)

When FTDC is enabled (per [`diagnosticDataCollectionEnabled`](https://docs.mongodb.com/manual/reference/parameters/index.html#param.diagnosticDataCollectionEnabled)), the `metrics.xxxxxxx` files will be stored in [`diagnosticDataCollectionDirectoryPath`](https://docs.mongodb.com/manual/reference/parameters/index.html#param.diagnosticDataCollectionDirectoryPath) which by default is the _diagnostic.data_ directory within the [`systemLog.path`](https://docs.mongodb.com/manual/reference/configuration-options/#systemLog.path).

With [SERVER-21818](https://jira.mongodb.org/browse/SERVER-21818) (introduced in MongoDB 3.2.13) and [SERVER-31400](https://jira.mongodb.org/browse/SERVER-31400) (introduced in MongoDB 3.4.16) the diagnostic data capture scope was broadened to not only include internal diagnostic commands but system metrics as well. Depending on the host operating system, the diagnostic data may include one or more of the following statistics:

- CPU utilization (ex: [`/proc/stat`](http://www.linuxhowtos.org/System/procstat.htm))
- Memory utilization (ex: [`/proc/meminfo`](https://www.thegeekdiary.com/understanding-proc-meminfo-file-analyzing-memory-utilization-in-linux/))
- Disk utilization related to performance (ex: [`*/sys/block/\*/stat*`](https://www.kernel.org/doc/Documentation/block/stat.txt))
- Network performance statistics ([`/proc/net/netstat`](https://unix.stackexchange.com/questions/435579/is-there-documentation-for-proc-net-netstat-and-proc-net-snmp))

The `metrics.xxxxxxx` files in the `diagnostic.data` directory contain only statistics about the performance of the system and the database. They are stored in a compressed format, and are not human-readable.

Just a quick note regarding privacy, regardless of the version, the data in _diagnostic.data_ never contains:

- Samples of queries, query predicates, or query results
- Data sampled from any end-user collection or index
- System or MongoDB user credentials or security certificates

FTDC data contains certain host machine information such as hostnames, operating system information, and the options or settings used to start the `mongod` or `mongos`. This information may be considered protected or confidential by some organizations or regulatory bodies, but is not typically considered to be [Personally Identifiable Information (PII)](https://en.wikipedia.org/wiki/Personal_data).

If you want to have a closer look at the diagnostic data collection process, you can inspect the [FTDC code](https://github.com/mongodb/mongo/tree/master/src/mongo/db/ftdc).

## FTDC Structure

<!-- MORE -->

There are two types of FTDC documents: a [BSON metadata document](https://github.com/mongodb/mongo/blob/r4.2.3/src/mongo/db/ftdc/util.h#L136), or a [BSON metric chunk](https://github.com/mongodb/mongo/blob/r4.2.3/src/mongo/db/ftdc/util.h#L150).

Each document is made up of an `_id`, a `type` and either a `doc` or `data` field. The `type` field is used to identify the document type:

- 0: Metadata Document
- 1: Metric Chunk

The `doc` or `data` fields will contain "samples" in the form of:

```javascript
{
  "start" : DateTime, /* Time at which all collecting started */
  "name" : String, /* name is from name() in FTDCCollectorInterface */
  {
        "start" : DateTime, /* Time at which name() collection started */
        "data" : { ... },   /* data comes from collect() in FTDCCollectorInterface */
        "end" : DateTime,   /* Time at which name() collection ended */
  },
  ... /* more than 1 collector be sampled */
  "end" : DateTime /* Time at which all collecting ended */
}
```

Samples are [collected by `FTDCCollectorInterface`](https://github.com/mongodb/mongo/blob/r4.2.3/src/mongo/db/ftdc/collector.h#L110) instances.

### Metadata Document

```javascript
{
  "_id":  DateTime,
  "type": 0,
  "doc":  { .. } /* Samples from collectors */
}
```

On log rotation or startup, the first FTDC entry will be collected and stored. This is a BSON document that contains information sampled by running [`getCmdLineOpts`](https://docs.mongodb.com/manual/reference/command/getCmdLineOpts/), [`buildInfo`](https://docs.mongodb.com/manual/reference/command/buildInfo/) and [`hostInfo`](https://docs.mongodb.com/manual/reference/command/hostInfo/).

```javascript
// example
{
  "start": DateTime,
  "buildInfo": { ... },
  "getCmdLineOpts": { ... },
  "hostInfo": { ... },
  "end": DateTime
}
```

This sample will be stored in the `doc` field of the metadata document.

### Metric Chunk

```javascript
{
  "_id":  DateTime,
  "type": 1
  "data": BinData(...)
}
```

During each collection interval (as configured by [`diagnosticDataCollectionPeriodMillis`](https://docs.mongodb.com/manual/reference/parameters/index.html#param.diagnosticDataCollectionPeriodMillis)), a metric chunk will be created and a sample will be collected, compressed and stored to the `data` document as Binary Data.

This sample can contain the results of internal commands such as [`serverStatus`](https://docs.mongodb.com/manual/reference/command/serverStatus/),[`replSetGetStatus`](https://docs.mongodb.com/manual/reference/command/replSetGetStatus/), [`collStats`](https://docs.mongodb.com/manual/reference/command/collStats/) for the [`local.oplog.rs`](https://docs.mongodb.com/manual/reference/local-database/#local.oplog.rs) collection or [`connPoolStats`](https://docs.mongodb.com/manual/reference/command/connPoolStats/#dbcmd.connPoolStats), as well as external system metrics.

```javascript
// example
{
  "start": DateTime,
  "serverStatus": { ... },
  "connPoolStats": { ... },
  "systemMetrics": { ... },
  "end": DateTime
}
```

## Decoding FTDC `metrics.xxxxxxx` files

FTDC files, such as the `metrics.2019-10-28T19-02-23Z-00000` example file we'll be working with below are just [BSON](http://bsonspec.org/) files. As such, the [`bsondump`](https://docs.mongodb.com/manual/reference/program/bsondump/) utility can be used to inspect the contents:

```bash
METRICS=metrics.2019-10-28T19-02-23Z-00000
bsondump --quiet $METRICS | less
```

{% picture /images/ftdc-001.png %}

`bsondump` will default to emitting JSON, so we can interact with this using the [`jq`]() utility. For example, if we only want to review the _Metadata Document_ this could be done as follows:

```bash
# bsondump < 4.0
bsondump --quiet $METRICS | jq -s '.[] | select( .type == 0)' | less

# bsondump >= 4.0
bsondump --quiet $METRICS | jq -s '.[] | select( .type | ."$numberInt" == "0")' | less
```

{% picture /images/ftdc-002.png %}

Working with _Metric Chunks_ is a little more complicated as they are actually zlib compressed BSON documents. We'll use the `jq` utility to only select the first chunk and the [Ruby](https://www.ruby-lang.org/en/) interpreter to decompress the zlib data. Note that the following command can be altered to navigate to other chunks (not only the first) as needed:

```bash
# bsondump < 4.0
METRICS=metrics.2019-12-20T14-22-56Z-00000
bsondump --quiet $METRICS | \
  jq -s '.[] | select( .type == 1)' | \
  jq -s 'first | .data ."$binary"' -Mc | \
  ruby -rzlib -rbase64 -e 'd = STDIN.read; print Zlib::Inflate.new.inflate(Base64.decode64(d)[4..-1])' | \
  bsondump --quiet

# bsondump >= 4.0
METRICS=metrics.2019-12-20T14-22-56Z-00000
bsondump --quiet $METRICS | \
  jq -s '.[] | select( .type | ."$numberInt" == "1")' | \
  jq -s 'first | .data ."$binary" .base64' -Mc | \
  ruby -rzlib -rbase64 -e 'd = STDIN.read; print Zlib::Inflate.new.inflate(Base64.decode64(d)[4..-1])' | \
  bsondump --quiet
```

You eagle-eyed Rubyists will notice that we're clipping the first 4 bytes from the binary data we're reading from STDIN. This is to drop the header before we try to decompress the stream.

If you don't do this [zlib](https://www.zlib.net/) will complain and fail:

```
Traceback (most recent call last):
        1: from -e:1:in `<main>'
-e:1:in `inflate': incorrect header check (Zlib::DataError)
```

The binary data has now been decompressed, and being BSON data we run it through `bsondump` again and voila:

{% picture /images/ftdc-003.png %}

Hopefully this helps shed some light on what FTDC data is and what it contains. In a future post we'll look into doing something useful with this treasure trove of telemetry our clusters are generating every 1 second or so.