---
layout: post
title: "Comparing MongoDB to not-MongoDB (ex: DocumentDB or Cosmos DB)"
date: 2023-03-29 13:12:37 -0400
comments: true
categories: MongoDB
tags:
image:
  src: /images/mongodb-logo.png
  alt: MongoDB Logo
---

Let's start off first with [what is MongoDB?](https://www.mongodb.com/what-is-mongodb) MongoDB’s [document model](https://www.mongodb.com/document-databases) is simple for developers to learn and use, while still providing all the capabilities needed to meet the most complex requirements at any scale. To enable developers to quickly integrate their data with their applications, [drivers for 10+ languages](https://www.mongodb.com/docs/drivers/) as well dozens more [community supported libraries](https://www.mongodb.com/docs/drivers/community-supported-drivers/) exist that expose idiomatic interfaces and intuitive APIs.

The ease of use of the drivers and the low barrier to entry to working with your data programmatically has been a huge draw for developers coming to MongoDB, however there are now choices in the market as big names such as Microsoft and Amazon release similar offerings that expose a MongoDB "compatibility layer" atop cloud database products.

According to the product blurb for [Amazon DocumentDB (with MongoDB compatibility)](https://aws.amazon.com/documentdb/), _Amazon DocumentDB (with MongoDB compatibility) is a fully managed native JSON document database that makes it easy and cost effective to operate critical document workloads at virtually any scale without managing infrastructure. Amazon DocumentDB simplifies your architecture by providing built-in security best practices, continuous backups, and native integrations with other AWS services._

Note that the branding for DocumentDB includes **"with MongoDB compatibility"** right in the product name, and in a similar fashion Azure's Cosmos DB provides a variation called [Azure Cosmos DB for MongoDB](https://learn.microsoft.com/en-us/azure/cosmos-db/mongodb/). [MongoDB Atlas](https://www.mongodb.com/atlas/database), which is MongoDB's cloud database service can make the same claims Amazon and Microsoft make, however with the main differentiating factor being that it offers the MOngoDB Server natively - not through some abstraction layer.

The major area of focus for developers is on building software using MongoDB's drivers, so we'll be focusing this article on the availability of MongoDB's [database commands](https://www.mongodb.com/docs/manual/reference/command/) across both Amazon Document DB as well as Azure Cosmos DB. The drivers use these commands internally to deliver consistent API experiences (based on published specifications such as the [Driver CRUD API](https://github.com/mongodb/specifications/blob/master/source/crud/crud.rst)) and inconsistencies in implementation or outright omissions could effect an application using MongoDB's drivers as a result.

# AWS DocumentDB

As of 2022-08-22, [Amazon DocumentDB is 35.31% compatible](https://www.isdocumentdbreallymongodb.com/). This number is being established based on the result of [compatibility tests](https://github.com/mongodb-developer/service-tests) that can be run by anyone to validate the results, but what does compatibility really mean here to the end user?

![](/images/notmdb-01.png)

According to the [MongoDB Software Lifecycle Schedules](https://www.mongodb.com/support-policy/lifecycles) the versions of MongoDB that DocumentDB lists as supported reached end of life in 2021 and 2022. At the time of writing [MongoDB 6.0](https://www.mongodb.com/docs/manual/release-notes/6.0/) is the latest version available, with 7.0 scheduled for sometime during the second half of 2023. As such, it's important to check your selected driver's compatibility to ensure you're potentially using features that won't be supported or exist (for example, see the [Ruby Driver Compatibility](https://www.mongodb.com/docs/ruby-driver/master/reference/driver-compatibility/) documentation).

Minor frustration - provisioning either an elastic or instance based DocumentDB cluster takes 10+ minutes. I also found the network restrictions made it extremely difficult to connect to the cluster even after downloading the PEM file for the security group. To interact with the cluster in any meaningful way I setup an Amazon Linux EC2 container, which I then installed the [MongoDB Shell](https://www.mongodb.com/try/download/shell) on.

To do this, connect to the container, get a download url for `mongosh` for _"RHEL / CentOS / Fedora / Suse 64-bit"_ and install that in the container to connect to the cluster.

```bash
   ,     #_
   ~\_  ####_        Amazon Linux 2023
  ~~  \_#####\
  ~~     \###|
  ~~       \#/ ___   https://aws.amazon.com/linux/amazon-linux-2023
   ~~       V~' '->
    ~~~         /
      ~~._.   _/
         _/ _/
       _/m/'
[ec2-user@ip-172-31-7-1 ~]$ wget https://downloads.mongodb.com/compass/mongodb-mongosh-1.8.0.x86_64.rpm
[ec2-user@ip-172-31-7-1 ~]$ sudo rpm -i mongodb-mongosh-1.8.0.x86_64.rpm
[ec2-user@ip-172-31-7-1 ~]$ mongosh mongodb://<user>:<pass>@ab-elastic-docdb-051834932553.us-east-1.docdb-elastic.amazonaws.com:27017 -ssl
WARNING: argument --ssl is deprecated and will be removed. Use --tls instead.
Current Mongosh Log ID: 64247c7a6aaa0a9d29f5ada3
Connecting to:          mongodb://<credentials>@ab-elastic-docdb-051834932553.us-east-1.docdb-elastic.amazonaws.com:27017/?directConnection=true&tls=true&appName=mongosh+1.8.0
Using MongoDB:          5.0.0
Using Mongosh:          1.8.0

[direct: mongos] test>
```

The two cluster types you can create effectively map to either a [replica set](https://www.mongodb.com/docs/manual/replication/) or [sharded cluster](https://www.mongodb.com/docs/manual/sharding/#sharded-cluster). To see what commands are supported by each cluster type, from a `mongosh` session we run the following script that uses the [`listCommands`](https://www.mongodb.com/docs/manual/reference/command/listCommands/) command generate the list:

```js
JSON.stringify(Object.keys(db.runCommand({ listCommands: 1 })["commands"]).sort())

// instance based (commands: 69)
["abortTransaction","aggregate","authenticate","buildInfo","collMod","collStats","commitTransaction","connectionStatus","count","create","createIndexes","createRole","createUser","currentOp","dataSize","dbStats","delete","deleteIndexes","distinct","driverOIDTest","drop","dropAllRolesFromDatabase","dropAllUsersFromDatabase","dropDatabase","dropIndexes","dropRole","dropUser","explain","find","findAndModify","forceerror","getLastError","getMaxChangeStreamTimestamp","getMore","getnonce","grantPrivilegesToRole","grantRolesToRole","grantRolesToUser","hello","hostInfo","insert","isMaster","killAllSessions","killCursors","killOp","killSessions","listCollections","listCommands","listCursors","listDatabases","listIndexes","logout","modifyChangeStreams","ping","replSetGetConfig","replSetGetStatus","revokePrivilegesFromRole","revokeRolesFromRole","revokeRolesFromUser","rolesInfo","saslContinue","saslStart","serverStatus","top","update","updateRole","updateUser","usersInfo","whatsmyuri"]

// elastic (commands: 50)
["aggregate","buildinfo","collStats","count","create","createIndexes","createUser","currentOp","dataSize","dbStats","delete","deleteIndexes","distinct","drop","dropAllUsersFromDatabase","dropDatabase","dropIndexes","dropUser","enablesharding","endsessions","find","findandmodify","getMore","getcmdlineopts","getengineversion","getfreemonitoringstatus","getlasterror","getlog","grantRolesToUser","hello","insert","isMaster","killCursors","killOp","listCollections","listCommands","listDatabases","listIndexes","logout","ping","replsetgetstatus","revokeRolesFromUser","rolesInfo","saslstart","serverStatus","shardcollection","update","updateUser","usersInfo","whatsmyuri"]
```

For sake of comparison I setup a sharded cluster using MongoDB 5.0.15 and using `mongosh` ran the following command against both a `mongos` as well as a `mongod`:

```js
JSON.stringify(Object.keys(db.runCommand({ listCommands: 1 })["commands"]).filter(item => !item.startsWith("_")).sort())

// mongod (commands: 152, unfiltered: 224)
["abortTransaction","aggregate","appendOplogNote","applyOps","authenticate","autoSplitVector","availableQueryOptions","buildInfo","checkShardingIndex","cleanupOrphaned","cloneCollectionAsCapped","collMod","collStats","commitTransaction","compact","connPoolStats","connPoolSync","connectionStatus","convertToCapped","coordinateCommitTransaction","count","create","createIndexes","createRole","createUser","currentOp","dataSize","dbCheck","dbHash","dbStats","delete","distinct","donorAbortMigration","donorForgetMigration","donorStartMigration","driverOIDTest","drop","dropAllRolesFromDatabase","dropAllUsersFromDatabase","dropConnections","dropDatabase","dropIndexes","dropRole","dropUser","endSessions","explain","exportCollection","features","filemd5","find","findAndModify","flushRouterConfig","fsync","fsyncUnlock","getAuditConfig","getCmdLineOpts","getDatabaseVersion","getDefaultRWConcern","getDiagnosticData","getFreeMonitoringStatus","getLastError","getLog","getMore","getParameter","getShardMap","getShardVersion","getnonce","grantPrivilegesToRole","grantRolesToRole","grantRolesToUser","hello","hostInfo","importCollection","insert","internalRenameIfOptionsAndIndexesMatch","invalidateUserCache","isMaster","killAllSessions","killAllSessionsByPattern","killCursors","killOp","killSessions","listCollections","listCommands","listDatabases","listIndexes","lockInfo","logApplicationMessage","logRotate","logout","mapReduce","mergeChunks","moveChunk","ping","planCacheClear","planCacheClearFilters","planCacheListFilters","planCacheSetFilter","prepareTransaction","profile","reIndex","recipientForgetMigration","recipientSyncData","refreshSessions","renameCollection","replSetAbortPrimaryCatchUp","replSetFreeze","replSetGetConfig","replSetGetRBID","replSetGetStatus","replSetHeartbeat","replSetInitiate","replSetMaintenance","replSetReconfig","replSetRequestVotes","replSetResizeOplog","replSetStepDown","replSetStepUp","replSetSyncFrom","replSetUpdatePosition","revokePrivilegesFromRole","revokeRolesFromRole","revokeRolesFromUser","rolesInfo","rotateCertificates","saslContinue","saslStart","serverStatus","setAuditConfig","setDefaultRWConcern","setFeatureCompatibilityVersion","setIndexCommitQuorum","setParameter","setShardVersion","shardingState","shutdown","splitChunk","splitVector","startRecordingTraffic","startSession","stopRecordingTraffic","top","update","updateRole","updateUser","usersInfo","validate","validateDBMetadata","voteCommitImportCollection","voteCommitIndexBuild","waitForFailPoint","whatsmyuri"]

// mongos (commands: 133, unfiltered: 137)
["abortReshardCollection","abortTransaction","addShard","addShardToZone","aggregate","appendOplogNote","authenticate","availableQueryOptions","balancerCollectionStatus","balancerStart","balancerStatus","balancerStop","buildInfo","cleanupReshardCollection","clearJumboFlag","collMod","collStats","commitReshardCollection","commitTransaction","compact","connPoolStats","connPoolSync","connectionStatus","convertToCapped","count","create","createIndexes","createRole","createUser","currentOp","dataSize","dbStats","delete","distinct","drop","dropAllRolesFromDatabase","dropAllUsersFromDatabase","dropConnections","dropDatabase","dropIndexes","dropRole","dropUser","enableSharding","endSessions","explain","features","filemd5","find","findAndModify","flushRouterConfig","fsync","getAuditConfig","getCmdLineOpts","getDefaultRWConcern","getDiagnosticData","getLastError","getLog","getMore","getParameter","getShardMap","getShardVersion","getnonce","grantPrivilegesToRole","grantRolesToRole","grantRolesToUser","hello","hostInfo","insert","invalidateUserCache","isMaster","isdbgrid","killAllSessions","killAllSessionsByPattern","killCursors","killOp","killSessions","listCollections","listCommands","listDatabases","listIndexes","listShards","logApplicationMessage","logRotate","logout","mapReduce","mergeChunks","moveChunk","movePrimary","netstat","ping","planCacheClear","planCacheClearFilters","planCacheListFilters","planCacheSetFilter","profile","refineCollectionShardKey","refreshSessions","removeShard","removeShardFromZone","renameCollection","repairShardedCollectionChunksHistory","replSetGetStatus","reshardCollection","revokePrivilegesFromRole","revokeRolesFromRole","revokeRolesFromUser","rolesInfo","rotateCertificates","saslContinue","saslStart","serverStatus","setAllowMigrations","setAuditConfig","setDefaultRWConcern","setFeatureCompatibilityVersion","setIndexCommitQuorum","setParameter","shardCollection","shutdown","split","splitVector","startRecordingTraffic","startSession","stopRecordingTraffic","update","updateRole","updateUser","updateZoneKeyRange","usersInfo","validate","validateDBMetadata","waitForFailPoint","whatsmyuri"]
```

The above output filters internal commands (commands prefixed with an underscore), however these are visible to the `listCommands` command. As Amazon controls the output of the commands and the source code for this compatibility layer is not public we cannot confirm or deny if any additional commands exist beyond what is listed.

# Azure Cosmos DB

_["What is Azure Cosmos DB for MongoDB"](https://learn.microsoft.com/en-us/azure/cosmos-db/mongodb/introduction)_ you might be asking. From their documentation, _Cosmos DB for MongoDB implements the [wire protocol](https://www.mongodb.com/docs/manual/reference/mongodb-wire-protocol/) for MongoDB. This implementation allows transparent compatibility with MongoDB client SDKs, drivers, and tools. Azure Cosmos DB doesn't host the MongoDB database engine. Any MongoDB client driver compatible with the API version you're using should be able to connect, with no special configuration._

What's notable about the above claim is _"**should** be able to connect"_. This type of hedging language is typical of marketing copy that doesn't want to provide guarantees, but focus on a desired outcome without drawing attention to any of the underlying negative connotations of the statement.

For example, the [`hello`](https://www.mongodb.com/docs/manual/reference/command/hello/) command was introduced in MongoDB 5.0, but backported to versions 4.4.2, 4.2.10, 4.0.21, and 3.6.21. Cosmos DB currently doesn't offer 5.0 API compatibility (except in limited preview), given the backport list I'd expect using this command to work. I don't see it listed in the ["Azure Cosmos DB for MongoDB (4.2 server version): supported features and syntax"](https://learn.microsoft.com/en-us/azure/cosmos-db/mongodb/feature-support-42) documentation, however as it's an internal command (used for initial connections or monitoring) it might have been excluded on purpose.

If you try and connect to your Cosmos DB cluster using a connection string the includes a [Stable API](https://www.mongodb.com/docs/manual/reference/stable-api/) version, the lack of the `hello` command will cause the connection to outright fail.

```bash
mongosh ab-cosmosdb1.mongo.cosmos.azure.com:10255 -u ab-cosmosdb1 -p <redacted> --ssl --sslAllowInvalidCertificates --apiVersion 1
WARNING: argument --ssl is deprecated and will be removed. Use --tls instead.
WARNING: argument --sslAllowInvalidCertificates is deprecated and will be removed. Use --tlsAllowInvalidCertificates instead.
Current Mongosh Log ID: 642472c47f4e6cdad20312b0
Connecting to:          mongodb://<credentials>@ab-cosmosdb1.mongo.cosmos.azure.com:10255/?directConnection=true&tls=true&tlsAllowInvalidCertificates=true&appName=mongosh+1.6.0
MongoServerSelectionError: Command hello not supported prior to authentication.
```

Similar to what we did with DocumentDB, let's try and identify what commands exist in Cosmos DB. Unfortunately, similar to the `hello` command it appears `listCommands` is also not supported:

```js
globaldb [direct: primary] test> db.runCommand({ listCommands: 1 })
MongoServerError: Command listCommands not supported.
```

Since we generated the command list from a `mongod` process earlier, let's assign those results to a variable below and try executing each of the 152 command with a `null` value to see how they fail. This can be used to build out a (somewhat) representative view of what commands are available.

```js
// commands from 5.0.15 mongod
var commands = ["abortTransaction","aggregate","appendOplogNote","applyOps","authenticate","autoSplitVector","availableQueryOptions","buildInfo","checkShardingIndex","cleanupOrphaned","cloneCollectionAsCapped","collMod","collStats","commitTransaction","compact","connPoolStats","connPoolSync","connectionStatus","convertToCapped","coordinateCommitTransaction","count","create","createIndexes","createRole","createUser","currentOp","dataSize","dbCheck","dbHash","dbStats","delete","distinct","donorAbortMigration","donorForgetMigration","donorStartMigration","driverOIDTest","drop","dropAllRolesFromDatabase","dropAllUsersFromDatabase","dropConnections","dropDatabase","dropIndexes","dropRole","dropUser","endSessions","explain","exportCollection","features","filemd5","find","findAndModify","flushRouterConfig","fsync","fsyncUnlock","getAuditConfig","getCmdLineOpts","getDatabaseVersion","getDefaultRWConcern","getDiagnosticData","getFreeMonitoringStatus","getLastError","getLog","getMore","getParameter","getShardMap","getShardVersion","getnonce","grantPrivilegesToRole","grantRolesToRole","grantRolesToUser","hello","hostInfo","importCollection","insert","internalRenameIfOptionsAndIndexesMatch","invalidateUserCache","isMaster","killAllSessions","killAllSessionsByPattern","killCursors","killOp","killSessions","listCollections","listCommands","listDatabases","listIndexes","lockInfo","logApplicationMessage","logRotate","logout","mapReduce","mergeChunks","moveChunk","ping","planCacheClear","planCacheClearFilters","planCacheListFilters","planCacheSetFilter","prepareTransaction","profile","reIndex","recipientForgetMigration","recipientSyncData","refreshSessions","renameCollection","replSetAbortPrimaryCatchUp","replSetFreeze","replSetGetConfig","replSetGetRBID","replSetGetStatus","replSetHeartbeat","replSetInitiate","replSetMaintenance","replSetReconfig","replSetRequestVotes","replSetResizeOplog","replSetStepDown","replSetStepUp","replSetSyncFrom","replSetUpdatePosition","revokePrivilegesFromRole","revokeRolesFromRole","revokeRolesFromUser","rolesInfo","rotateCertificates","saslContinue","saslStart","serverStatus","setAuditConfig","setDefaultRWConcern","setFeatureCompatibilityVersion","setIndexCommitQuorum","setParameter","setShardVersion","shardingState","shutdown","splitChunk","splitVector","startRecordingTraffic","startSession","stopRecordingTraffic","top","update","updateRole","updateUser","usersInfo","validate","validateDBMetadata","voteCommitImportCollection","voteCommitIndexBuild","waitForFailPoint","whatsmyuri"];
var supported = [];
commands.forEach(function(cmd) {
  try {
    /* command doesn't fail when null is passed */
    if (db.runCommand({ [cmd]: null }).ok == 1) {
      supported.push(cmd);
    }
  } catch(ex) {
    /* 59: command not found */
    if (ex.code != 59 && !ex.message.endsWith("not supported.")) {
      supported.push(cmd);
    }
  }
});
JSON.stringify(supported);

// commands: 47
["abortTransaction","aggregate","authenticate","buildInfo","collStats","commitTransaction","connectionStatus","count","create","createIndexes","currentOp","dbStats","delete","distinct","drop","dropDatabase","dropIndexes","endSessions","explain","filemd5","find","findAndModify","getCmdLineOpts","getLastError","getLog","getMore","getParameter","getnonce","hello","hostInfo","insert","isMaster","killCursors","listCollections","listDatabases","listIndexes","logout","ping","reIndex","renameCollection","replSetGetStatus","saslContinue","saslStart","serverStatus","update","validate","whatsmyuri"]
```

# Conclusion

By reviewing the database commands that Microsoft and Amazon have chosen to implement we can get a sense of what features may be accessible via MongoDB drivers. Though the bare minimum commands required to satisfy the CRUD API appear to be available, the feature set is still limited when it comes to administration and data manipulation.

Azure documents which [aggregation stages](https://learn.microsoft.com/en-us/azure/cosmos-db/mongodb/feature-support-42#aggregation-pipeline) aren't available, and AWS also documents the [limitations of their MongoDB APIs and operation types](https://docs.aws.amazon.com/documentdb/latest/developerguide/mongo-apis.html).

Though there are definitely benefits to working with AWS and Azure, when it comes to MongoDB compatibility it is likely a better bet to simply use MongoDB.