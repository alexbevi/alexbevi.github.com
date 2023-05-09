---
layout: post
title: "MongoDB Stable API"
date: 2021-10-07 06:17:50 -0400
comments: true
categories: [MongoDB]
tags: [mongodb]
image: /images/mongodb-logo.png
---

> MongoDB's **Versioned API** was renamed to the **Stable API**, so this guide was updated to use the new terminology
{: .prompt-info }

The [Stable API For Drivers Specification](https://github.com/mongodb/specifications/blob/master/source/versioned-api/versioned-api.rst) states _"When applications interact with MongoDB, both the driver and the server participate in executing operations. Therefore, when determining application compatibility with MongoDB, both the driver and the server behavior must be taken into account."_

As MongoDB [moves toward more frequent releases (a.k.a. continuous delivery)](https://www.mongodb.com/blog/post/new-quarterly-releases-starting-with-mongodb-5-0), they want to enable users to take advantage of rapidly released features, without exposing applications to incompatible server changes due to automatic server upgrades. A Stable API will help accomplish that goal (see ["Upgrade Fearlessly with the MongoDB Stable API"](https://www.mongodb.com/developer/products/mongodb/upgrade-fearlessly-stable-api/)).

The Stable API encompasses the subset of MongoDB commands that applications commonly use to read and write data, create collections and indexes, and so on. We commit to keeping these commands backward-compatible in new MongoDB versions. We can add new features (such as new command parameters, new aggregation operators, new commands, etc.) to the Stable API, but only in backward-compatible ways.

## Identifying Stable API Commands
From a mongo or `mongosh` shell connected to a 5.0+ cluster the following helper function can be used to determine which commands are included in a specific API version.

```js
function printCommandsByAPIVersion(version) {
    version = version.toString();
    var result = db.runCommand({ listCommands: 1 })
    var keys = Object.keys(result.commands);
    var commands = [];
    for (var i = 0; i < keys.length; i++) {
        var cmd = result.commands[keys[i]];
        if (cmd.apiVersions.indexOf(version) >= 0  ) {
            commands.push(keys[i]);
        }
    }
    return { version: db.serverBuildInfo().version, apiVersion: version, commands: commands.sort() };
}
```

This can be used to print out the commands supported by a specific API Version (only version `"1"` for now):

```js
printCommandsByAPIVersion(1);
```

## API v1 Commands

Note this is also [documented](https://mongodb.com/docs/manual/reference/stable-api-changelog/#database-commands) now, however the output of the `printCommandsByAPIVersion` against a MongoDB 5.0 cluster would output the following:

`abortTransaction`, `aggregate`, `authenticate`, `collMod`, `commitTransaction`, `create`, `createIndexes`, `delete`, `drop`, `dropDatabase`, `dropIndexes`, `endSessions`, `explain`, `find`, `findAndModify`, `getMore`, `hello`, `insert`, `killCursors`, `listCollections`, `listDatabases`, `listIndexes`, `ping`, `refreshSessions`, `saslContinue`, `saslStart`, `update`

## Stable API Test

The following test using the latest `master` branch of the [Ruby Driver](https://github.com/mongodb/mongo-ruby-driver) can be used to test the behavior of an application with and without strict checking. This example sends a [`replSetGetStatus`](https://docs.mongodb.com/manual/reference/command/replSetGetStatus/) command to the server, and if the `strict` option is set shows the `APIStrictError` being raised:

```ruby
# test.rb
require 'bundler/inline'
gemfile do
 source 'https://rubygems.org'
 gem 'mongo', github: 'mongodb/mongo-ruby-driver', branch: "master"
end

strict_api = ARGV[0] == "true"
# connect to a MongoDB 5.0+ replica set
client = Mongo::Client.new([ 'alexs-mbp:27017' ], database: 'mydb', replica_set: 'rs0', server_api: { version: 1, strict: strict_api })
begin
 admin_client = client.use('admin')
 p admin_client.database.command(replSetGetStatus: 1).documents.first
rescue Mongo::Error::OperationFailure => ex
 puts ex
ensure
 client.close
end
```

The above script can be tested by passing `true`/`false` as the first argument to validate the behavior of the driver in strict mode:

```bash
$ ruby test.rb
{"set"=>"rs0", "date"=>2021-05-14 14:49:33 UTC, "myState"=>1, "term"=>7, "syncSourceHost"=>"", "syncSourceId"=>-1, "heartbeatIntervalMillis"=>2000, "majorityVoteCount"=>1, "writeMajorityCount"=>1, "votingMembersCount"=>1, "writableVotingMembersCount"=>1, "optimes"=>{"lastCommittedOpTime"=>{"ts"=>#<BSON::Timestamp:0x00007fb303a1dc78 @seconds=1621003767, @increment=1>, "t"=>7}, "lastCommittedWallTime"=>2021-05-14 14:49:27 UTC, "readConcernMajorityOpTime"=>{"ts"=>#<BSON::Timestamp:0x00007fb303a1d9d0 @seconds=1621003767, @increment=1>, "t"=>7}, "appliedOpTime"=>{"ts"=>#<BSON::Timestamp:0x00007fb303a1d868 @seconds=1621003767, @increment=1>, "t"=>7}, "durableOpTime"=>{"ts"=>#<BSON::Timestamp:0x00007fb303a1d700 @seconds=1621003767, @increment=1>, "t"=>7}, "lastAppliedWallTime"=>2021-05-14 14:49:27 UTC, "lastDurableWallTime"=>2021-05-14 14:49:27 UTC}, "lastStableRecoveryTimestamp"=>#<BSON::Timestamp:0x00007fb303a1d340 @seconds=1621003737, @increment=1>, "electionCandidateMetrics"=>{"lastElectionReason"=>"electionTimeout", "lastElectionDate"=>2021-05-14 14:27:57 UTC, "electionTerm"=>7, "lastCommittedOpTimeAtElection"=>{"ts"=>#<BSON::Timestamp:0x00007fb303a1cfa8 @seconds=0, @increment=0>, "t"=>-1}, "lastSeenOpTimeAtElection"=>{"ts"=>#<BSON::Timestamp:0x00007fb303a1ce40 @seconds=1620999663, @increment=1>, "t"=>6}, "numVotesNeeded"=>1, "priorityAtElection"=>1.0, "electionTimeoutMillis"=>10000, "newTermStartDate"=>2021-05-14 14:27:57 UTC, "wMajorityWriteAvailabilityDate"=>2021-05-14 14:27:57 UTC}, "members"=>[{"_id"=>0, "name"=>"Alexs-MBP:27017", "health"=>1.0, "state"=>1, "stateStr"=>"PRIMARY", "uptime"=>1300, "optime"=>{"ts"=>#<BSON::Timestamp:0x00007fb303a1c6c0 @seconds=1621003767, @increment=1>, "t"=>7}, "optimeDate"=>2021-05-14 14:49:27 UTC, "syncSourceHost"=>"", "syncSourceId"=>-1, "infoMessage"=>"", "electionTime"=>#<BSON::Timestamp:0x00007fb303a1c378 @seconds=1621002477, @increment=1>, "electionDate"=>2021-05-14 14:27:57 UTC, "configVersion"=>1, "configTerm"=>7, "self"=>true, "lastHeartbeatMessage"=>""}], "ok"=>1.0, "$clusterTime"=>{"clusterTime"=>#<BSON::Timestamp:0x00007fb3049dff30 @seconds=1621003767, @increment=1>, "signature"=>{"hash"=><BSON::Binary:0x70203426668280 type=generic data=0x0000000000000000...>, "keyId"=>0}}, "operationTime"=>#<BSON::Timestamp:0x00007fb3049dfd00 @seconds=1621003767, @increment=1>}

$ ruby test.rb true
[323:APIStrictError]: Provided apiStrict:true, but the command replSetGetStatus is not in API Version 1 (on alexs-mbp:27017)
```

There are presently no plans or schedules to deprecate version 1, which is reinforced by the following excerpt from the internal technical design document: _The Versioned API frees us from this bind. We say that today's semantics are part of the MongoDB API Version 1, and the new semantics are in Version 2. MongoDB servers will support both._

## Additional References:

* [Reference Documentation](https://www.mongodb.com/docs/manual/reference/stable-api/)
* [Architecture Documentation](https://github.com/mongodb/mongo/blob/master/src/mongo/db/STABLE_API_README.md)
* [DRIVERS-996: Versioned MongoDB API for Drivers](https://jira.mongodb.org/browse/DRIVERS-996)