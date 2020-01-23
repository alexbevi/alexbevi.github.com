---
layout: post
title: "Troubleshooting and Fixing Invariant Failure !_featureTracker on MongoDB Startup"
date: 2020-01-23 05:34:53 -0500
comments: true
categories: [mongodb]
---
I recently found myself troubleshooting another [MongoDB](https://www.mongodb.com/) startup issue due to potential corruption within a [WiredTiger](https://docs.mongodb.com/manual/core/wiredtiger/) file. As I have previously covered this topic (see ["Recovering a WiredTiger collection from a corrupt MongoDB installation"]({% post_url 2016-02-10-recovering-a-wiredtiger-collection-from-a-corrupt-mongodb-installation %})), I wanted to share the diagnostic and troubleshooting journey in case it helps anyone who experiences this issue in the future.

To ensure I could troubleshoot this issue in isolation, I first collected a backup of the necessary files from the affected installation as follows:

```bash
tar -czvf metadata.tar.gz --exclude=WiredTigerStat* WiredTiger* _mdb_catalog.wt sizeStorer.wt
```

Once I had this backup I extracted it to a new location, then using [m](https://github.com/aheckmann/m) to select the versions of MongoDB to use tried to startup a standalone instance to see if I could reproduce the issue:

```bash
mkdir -p /tmp/repro
cd /tmp/repro
# move archive from earlier to the new directory first
tar xvf metadata.tar.gz
# This is the version of MongoDB reported to be crashing
m 3.4.18
mongod --dbpath .
```

Once the `mongod` started, we were able to see the failure and the process aborts (clipped log sample below).

```
2020-01-23T03:58:19.828-0500 I CONTROL  [initandlisten] db version v3.4.18
2020-01-23T03:58:19.828-0500 I CONTROL  [initandlisten] git version: 4410706bef6463369ea2f42399e9843903b31923
...
2020-01-23T03:58:20.187-0500 I -        [initandlisten] Invariant failure !_featureTracker src/mongo/db/storage/kv/kv_catalog.cpp 305
2020-01-23T03:58:20.187-0500 I -        [initandlisten]

***aborting after invariant() failure

2020-01-23T03:58:20.198-0500 F -        [initandlisten] Got signal: 6 (Aborted).
...
 mongod(_ZN5mongo15printStackTraceERSo+0x41) [0x55bb45c92111]
 mongod(+0x153F329) [0x55bb45c91329]
 mongod(+0x153F80D) [0x55bb45c9180d]
 libpthread.so.0(+0x12890) [0x7f5b7bee5890]
 libc.so.6(gsignal+0xC7) [0x7f5b7bb20e97]
 libc.so.6(abort+0x141) [0x7f5b7bb22801]
 mongod(_ZN5mongo17invariantOKFailedEPKcRKNS_6StatusES1_j+0x0) [0x55bb44f5b234]
 mongod(_ZN5mongo9KVCatalog4initEPNS_16OperationContextE+0x568) [0x55bb458db5e8]
 mongod(_ZN5mongo15KVStorageEngineC1EPNS_8KVEngineERKNS_22KVStorageEngineOptionsE+0x807) [0x55bb458e79f7]
 mongod(+0x124DFFA) [0x55bb4599fffa]
 mongod(_ZN5mongo20ServiceContextMongoD29initializeGlobalStorageEngineEv+0x697) [0x55bb45891627]
 mongod(+0x7F62AC) [0x55bb44f482ac]
 mongod(main+0x96B) [0x55bb44f66a6b]
 libc.so.6(__libc_start_main+0xE7) [0x7f5b7bb03b97]
 mongod(+0x86FFB1) [0x55bb44fc1fb1]
-----  END BACKTRACE  -----
Aborted (core dumped)
```

<!-- more -->

The `mongod` is failing to startup successfully due to an invariant failure during `KVCatalog::init`. We are able to determine this as the `mongod` log above tells us:

1. The MongoDB version in used (3.4.18)
2. The path to the source file where the failure occurred (file: `src/mongo/db/storage/kv/kv_catalog.cpp`, line: 305)

As MongoDB is open source, we can view the source for this release by going to https://github.com/mongodb/mongo/blob/r3.4.18/src/mongo/db/storage/kv/kv_catalog.cpp#L305, which will show us the following:

```cpp
if (FeatureTracker::isFeatureDocument(obj)) {
    // There should be at most one version document in the catalog.
    invariant(!_featureTracker);

    // Initialize the feature tracker and skip over the version document because it doesn't
    // correspond to a namespace entry.
    _featureTracker = FeatureTracker::get(opCtx, this, record->id);
    continue;
}
```

The comment preceding the invariant<sup id="f1">[1](#fn1)</sup> indicates that there's only one feature document to be present in the catalog, but what's the catalog?

```bash
ls -l *catalog*
-rw-r--r-- 1 alex 249856 Jan 23 03:58 _mdb_catalog.wt
```

As there's only one file that contains the word "catalog" this is good a place as any to start. The `_mdb_catalog` is a WiredTiger file, so to interact with it directly (outside of MongoDB) we will need to use the [WiredTiger command line utility](http://source.wiredtiger.com/mongodb-3.4/command_line.html), also know as `wt`.

The documentation link for `mongodb-3.4` points us to WiredTiger 2.9.2, so following the [build and installation instructions](http://source.wiredtiger.com/mongodb-3.4/build-posix.html) we compile a `wt` binary with support for the snappy compressor. This is due to MongoDB's WiredTiger storage engine using snappy as the default block compressor (see ["Compression"](https://docs.mongodb.com/manual/core/wiredtiger/#compression)).

```bash
cd /tmp/repro
git clone git://github.com/wiredtiger/wiredtiger.git
cd wiredtiger
git checkout 2.9.2
sh autogen.sh
# ensure you have the necessary development headers for the snapy compression
# library before compiling
./configure --enable-snappy && make
```

Once we've successfully build the `wt` utility with snappy compression we can dump our catalog to see if we can find a duplicate entry for teh feature document.

```bash
cd /tmp/repro
# to shorten the amount of typing required, wrap the wt utility invocation in
# a function we can call instead
WT() { /tmp/repro/wiredtiger/wt -v -C "extensions=[\"/tmp/repro/wiredtiger/ext/compressors/snappy/.libs/libwiredtiger_snappy.so\"]" $@; }
# write the catalog dump out to a file
WT dump _mdb_catalog > dump.txt
```

NOTE: If you receive the following error, just re-run the command.

```
[1579773800:589375][9348:0x7fc9a8e17140], txn-recover: Recovery failed: WT_RUN_RECOVERY: recovery must be run to continue
wt: WT_RUN_RECOVERY: recovery must be run to continue
```

This error is due to the presence of content in the `journal/` that was created when we last ran the `mongod`.

With the catalog dumped we can now search it for the feature document:

```bash
grep isFeatureDoc dump.txt -B 1 -n

935-\c2\e5
936:C\00\00\00\08isFeatureDoc\00\01\0ans\00\12nonRepairable\00\00\00\00\00\00\00\00\00\12repairable\00\01\00\00\00\00\00\00\00\00
937-\c2\e6
938:C\00\00\00\08isFeatureDoc\00\01\0ans\00\12nonRepairable\00\00\00\00\00\00\00\00\00\12repairable\00\01\00\00\00\00\00\00\00\00
```

INTERESTING! I'm not really sure how the catalog was able to get into a state where two feature documents exist, but since we have a dump of the catalog let's try to remove one of those entries and then load the dump back into the catalog.

As the results appear to be identical, we'll just drop the first one and then try to load it back into the catalog.

```bash
# remove lines 935-936 and overwrite the file
sed -i -e '935,936d' dump.txt
# drop the contents of the _mdb_catalog table
WT truncate _mdb_catalog
# reload the table from the dump file
WT load -f dump.txt
```

If the table loaded successfully the output of the command should be something like `table:_mdb_catalog: 822`.

With a reloaded catalog, let's try spinning up the `mongod` again:

```
2020-01-23T05:24:54.911-0500 I CONTROL  [initandlisten] db version v3.4.18
...
2020-01-23T05:24:56.247-0500 E STORAGE  [initandlisten] no cursor for uri: table:SomeCollection/collection/34-1349843775853912065
2020-01-23T05:24:56.247-0500 F -        [initandlisten] Invalid access at address: 0x58
2020-01-23T05:24:56.259-0500 F -        [initandlisten] Got signal: 11 (Segmentation fault).
```

SUCCESS! The `mongod` is still crashing as the backing files for the database don't exist, but we should now be able to take our recovered files back to our node that was previously failing.

From our recovered directory compress the following files:

```
tar -czvf recovered.tar.gz --exclude=WiredTigerStat* WiredTiger* _mdb_catalog.wt sizeStorer.wt
```

Note that if the `mongod` fails to start with the recovered files you may have to clear out the `journal/` directory.

Hopefully this helps someone someday ;)

<hr/>
<small><b id="fn">1</b> An invariant is a condition to test, that on failure will log the test condition, source file and line of code. [↩](#f1)</small>
