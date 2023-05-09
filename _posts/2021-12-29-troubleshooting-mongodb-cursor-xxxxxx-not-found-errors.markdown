---
layout: post
title: "Troubleshooting 'MongoDB Cursor xxxxxx not found' Errors"
date: 2021-12-29 09:26:53 -0500
comments: true
categories: [MongoDB]
tags: [mongodb, queries]
image: /images/mongodb-logo.png
---
Read operations that return multiple documents do not immediately return all values matching the query. Because a query can potentially match very large sets of documents, these operations rely upon an object called a cursor. A cursor fetches documents in batches to reduce both memory consumption and network bandwidth usage.

One category of issue you may observe occasionally in your application logs is a `CursorNotFound` entry such as the following (from an application using the [MongoDB Java Driver](https://docs.mongodb.com/drivers/java/sync/current/)):

> `com.mongodb.MongoCursorNotFoundException: Query failed with error code -5 and error message 'Cursor 4865637895305205821 not found on server prod-shard-00-00.xxxxx.mongodb.net:27017' on server prod-shard-00-00.xxxxx.mongodb.net:27017`

Depending on whether the [version](https://docs.mongodb.com/manual/release-notes/) of MongoDB your cluster is using is greater than 4.4.7 the _"cursor id xxxxxx not found"_ can refer to two possible timeouts.

### (1) `cursorTimeoutMillis` being exceeded

The [`cursorTimeoutMillis`](https://docs.mongodb.com/v4.4/reference/parameters/#mongodb-parameter-param.cursorTimeoutMillis) server parameter sets the expiration threshold (in milliseconds) for idle cursors before MongoDB removes them. The default value for `cursorTimeoutMillis` is 600000, or 10 minutes. Idle cursors are timed out using the [`ClientCursorMonitor`](https://github.com/mongodb/mongo/blob/r4.4.7/src/mongo/db/clientcursor.cpp) background job, whose thread is identified in the `mongod` logs as `clientcursormon`.

The `ClientCursorMonitor` identifies and reaps idle cursors every 4 seconds (the default value of [`clientCursorMonitorFrequencySecs`](https://github.com/mongodb/mongo/blob/r4.4.7/src/mongo/db/cursor_server_params.idl#L33-L38)).

When a cursor timeout is identified these can be found in the log with entries similar to the following:
```log
{"t":{"$date":"2021-12-29T09:22:41.937-05:00"},"s":"I","c":"COMMAND","id":51803,"ctx":"conn3","msg":"Slow query","attr":{"type":"command","ns":"admin.foo","appName":"MongoDB Shell","command":{"find":"foo","filter":{},"batchSize":1,"lsid":{"id":{"$uuid":"824bd767-4a7d-4240-a8cd-8f4c83c8cf99"}},"$db":"admin"},"planSummary":"COLLSCAN","cursorid":4225966264683133400,"keysExamined":0,"docsExamined":1,"numYields":0,"nreturned":1,"reslen":123,"locks":{"ReplicationStateTransition":{"acquireCount":{"w":1}},"Global":{"acquireCount":{"r":1}},"Database":{"acquireCount":{"r":1}},"Collection":{"acquireCount":{"r":1}},"Mutex":{"acquireCount":{"r":1}}},"storage":{},"protocol":"op_msg","durationMillis":0}}
{"t":{"$date":"2021-12-29T09:22:44.096-05:00"},"s":"I","c":"QUERY","id":20529,"ctx":"clientcursormon","msg":"Cursor timed out","attr":{"cursorId":4225966264683133400,"idleSince":{"$date":"2021-12-29T14:22:41.937Z"}}}
{"t":{"$date":"2021-12-29T09:22:48.031-05:00"},"s":"I","c":"COMMAND","id":51803,"ctx":"conn3","msg":"Slow query","attr":{"type":"command","ns":"admin.$cmd","appName":"MongoDB Shell","command":{"getMore":4225966264683133400,"collection":"foo","batchSize":1,"lsid":{"id":{"$uuid":"824bd767-4a7d-4240-a8cd-8f4c83c8cf99"}},"$db":"admin"},"cursorid":4225966264683133400,"numYields":0,"ok":0,"errMsg":"cursor id 4225966264683133185 not found","errName":"CursorNotFound","errCode":43,"reslen":129,"locks":{},"protocol":"op_msg","durationMillis":0}}
```

The [log messages](https://docs.mongodb.com/v4.4/reference/log-messages/) above have had their log component verbosity increased and were generated using the following script:

```bash
# bash
rm -rf data && mkdir data
$(m bin 4.4.7-ent)/mongod --dbpath data --bind_ip_all
```
```javascript
// mongo shell
db.runCommand({ setParameter: 1, cursorTimeoutMillis: 1000 });
db.runCommand({ setParameter: 1, clientCursorMonitorFrequencySecs: 2 });
db.foo.drop();
db.foo.insertMany([ {}, {} ]);
db.setLogLevel(4, 'command')
db.foo.find({}).batchSize(1).forEach(function(d) {
  printjson(d);
  sleep(1000 * 6);
});
db.setLogLevel(-1, 'command')
```

Note that the log contains a _..."s":"I","c":"QUERY","id":20529,"ctx":"clientcursormon","msg":"Cursor timed out..."_ entry, which is at the default [log verbosity](https://docs.mongodb.com/manual/reference/log-messages/#verbosity-levels). If this message is present the cursor timed out as a result of being idle longer than `cursorTimeoutMillis` and would have returned an error such as:

```js
Error: command failed: {
	"ok" : 0,
	"errmsg" : "cursor id 4225966264683133185 not found",
	"code" : 43,
	"codeName" : "CursorNotFound"
} with original command request: {
	"getMore" : NumberLong("4225966264683133185"),
	"collection" : "foo",
	"batchSize" : 1,
	"lsid" : {
		"id" : UUID("824bd767-4a7d-4240-a8cd-8f4c83c8cf99")
	}
}
```

### (2) `localLogicalSessionTimeoutMinutes` being exceeded

Starting with MongoDB 3.6 server sessions, or logical sessions, are the underlying framework used by [client sessions](https://docs.mongodb.com/manual/release-notes/3.6/#std-label-3.6-client-sessions) to support [Causal Consistency](https://docs.mongodb.com/manual/core/read-isolation-consistency-recency/#std-label-causal-consistency) and [retryable writes](https://docs.mongodb.com/manual/core/retryable-writes/#std-label-retryable-writes). When using a MongoDB Driver that is 3.6+ compatible implicit sessions are used (per the [Drivers Sessions](https://github.com/mongodb/specifications/blob/master/source/sessions/driver-sessions.rst) specification). As such, if your application is using a 3.6+ compatible driver, you are using sessions.

The default value of [`localLogicalSessionTimeoutMinutes`](https://docs.mongodb.com/v4.4/reference/parameters/#mongodb-parameter-param.localLogicalSessionTimeoutMinutes) is 30 minutes and controls the time (in minutes) that a [session](https://docs.mongodb.com/v4.4/core/read-isolation-consistency-recency/#std-label-sessions) remains active after its most recent use. Sessions that have not received a new read/write operation from the client or been refreshed with [`refreshSessions`](https://docs.mongodb.com/v4.4/reference/command/refreshSessions/#mongodb-dbcommand-dbcmd.refreshSessions) within this threshold are cleared from the cache.

Starting with MongoDB 4.4.8 (via [SERVER-6036](https://jira.mongodb.org/browse/SERVER-6036)) when a cursor is opened as part of a session, its lifetime will be tied to that session and as a result closing or timing out of a session will kill all associated cursors. This results in `cursorTimeoutMillis`/`clientcursormon` not being used to control cursor timeouts for any cursor with a [session id](https://docs.mongodb.com/manual/reference/server-sessions/#command-options).

When a cursor times out as a result of the session being reaped the error appears as follows:
```log
{"t":{"$date":"2021-12-29T08:02:04.942-05:00"},"s":"I","c":"COMMAND","id":51803,"ctx":"conn1","msg":"Slow query","attr":{"type":"command","ns":"admin.foo","appName":"MongoDB Shell","command":{"find":"foo","filter":{},"batchSize":1,"lsid":{"id":{"$uuid":"824bd767-4a7d-4240-a8cd-8f4c83c8cf99"}},"$db":"admin"},"planSummary":"COLLSCAN","cursorid":63169428846689080,"keysExamined":0,"docsExamined":1,"numYields":0,"nreturned":1,"reslen":123,"locks":{"ReplicationStateTransition":{"acquireCount":{"w":1}},"Global":{"acquireCount":{"r":1}},"Database":{"acquireCount":{"r":1}},"Collection":{"acquireCount":{"r":1}},"Mutex":{"acquireCount":{"r":1}}},"storage":{},"protocol":"op_msg","durationMillis":0}}
{"t":{"$date":"2021-12-29T08:03:53.030-05:00"},"s":"I","c":"QUERY","id":20528,"ctx":"LogicalSessionCacheRefresh","msg":"Killing cursor as part of killing session(s)","attr":{"cursorId":63169428846689080}}
{"t":{"$date":"2021-12-29T08:04:04.968-05:00"},"s":"I","c":"COMMAND","id":51803,"ctx":"conn1","msg":"Slow query","attr":{"type":"command","ns":"admin.$cmd","appName":"MongoDB Shell","command":{"getMore":63169428846689080,"collection":"foo","batchSize":1,"lsid":{"id":{"$uuid":"824bd767-4a7d-4240-a8cd-8f4c83c8cf99"}},"$db":"admin"},"cursorid":63169428846689080,"numYields":0,"ok":0,"errMsg":"cursor id 63169428846689082 not found","errName":"CursorNotFound","errCode":43,"reslen":127,"locks":{},"protocol":"op_msg","durationMillis":0}}
```

These log entries were generated by adjusting our previous example as seen below:

```bash
# bash
rm -rf data && mkdir data
$(m bin 4.4.11-ent)/mongod --dbpath data --bind_ip_all --setParameter logicalSessionRefreshMillis=1000 --setParameter localLogicalSessionTimeoutMinutes=1
```
```javascript
db.foo.drop();
db.foo.insertMany([ {}, {} ]);
db.setLogLevel(4, 'command')
db.foo.find({}).batchSize(1).forEach(function(d) {
  printjson(d);
  sleep(1000 * 120);
});
db.setLogLevel(-1, 'command')
```

Now the log entry that controls timing out the cursor is generated by the `LogicalSessionCacheRefresh` thread. Note that as the end result is the same (idle cursor is timed out) the error returned to the application would appear to be the same as well:

```js
uncaught exception: Error: command failed: {
	"ok" : 0,
	"errmsg" : "cursor id 63169428846689082 not found",
	"code" : 43,
	"codeName" : "CursorNotFound"
} with original command request: {
	"getMore" : NumberLong("63169428846689082"),
	"collection" : "foo",
	"batchSize" : 1,
	"lsid" : {
		"id" : UUID("824bd767-4a7d-4240-a8cd-8f4c83c8cf99")
	}
}
```

### Summary

Regardless of which MongoDB 3.6+ version is being used an idle cursor can time out with the failure bubbling up to the application with an error message such as _"cursor id 63169428846689082 not found"_, which is the same as if the cursor were timed out.

Note that setting the [`noCursorTimeout`](https://docs.mongodb.com/manual/reference/method/cursor.noCursorTimeout/) cursor option in a MongoDB 3.6+ cluster can still result in a cursor being closed as [Session Idle Timeout Overrides `noCursorTimeout`](https://docs.mongodb.com/manual/reference/method/cursor.noCursorTimeout/#session-idle-timeout-overrides-nocursortimeout).

For operations that return a cursor, if the cursor may be idle for longer than `localLogicalSessionTimeoutMinutes` minutes, issue the operation within an explicit session using [`Mongo.startSession()`](https://docs.mongodb.com/manual/reference/method/Mongo.startSession/#mongodb-method-Mongo.startSession) and periodically refresh the session using the [`refreshSessions`](https://docs.mongodb.com/manual/reference/command/refreshSessions/#mongodb-dbcommand-dbcmd.refreshSessions) command. For example:

```js
var session = db.getMongo().startSession()
var sessionId = session.getSessionId().id

var cursor = session.getDatabase("examples").getCollection("data").find().noCursorTimeout()
var refreshTimestamp = new Date() // take note of time at operation start

while (cursor.hasNext()) {

  // Check if more than 5 minutes have passed since the last refresh
  if ( (new Date()-refreshTimestamp)/1000 > 300 ) {
    print("refreshing session")
    db.adminCommand({"refreshSessions" : [sessionId]})
    refreshTimestamp = new Date()
  }

  // process cursor normally

}
```

Refreshing explicit sessions is one way to work around these timeouts, however this is only one approach. If there is a need to keep cursors idle for long periods of time these should be evaluated on a case by case basis to ensure refactoring isn't a better solution.

All examples in this article use the [`mongo` shell](https://docs.mongodb.com/manual/reference/program/mongo/#mongodb-binary-bin.mongo) however the logic could be adapted to your preferred language and used with the appropriate [MongoDB Driver](https://docs.mongodb.com/drivers/).

Have any questions or comments? Post them below ;)