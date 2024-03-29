---
layout: post
title: "Recovering a WiredTiger collection from a corrupt MongoDB installation"
date: 2016-02-10 20:38:38 -0500
comments: true
pin: true
categories: [MongoDB]
tags: [mongodb, wiredtiger, data-corruption, troubleshooting]
image: /images/mongodb-logo.png
---

> **April, 1 2019**: I've received a LOT of feedback on this article since it was published. I would like to point out that although the methods described here may still work, MongoDB introduced a `--repair` flag in 4.0.3 that simplifies this process significantly.
>
> I would recommend reading their ["Recover a Standalone after an Unexpected Shutdown"](https://docs.mongodb.com/manual/tutorial/recover-data-following-unexpected-shutdown) tutorial to see if it applies to your recovery scenario.
{: .prompt-info }


Recently at work, we experienced a series of events that could have proven to be catastrophic for one of our datasets. We have a daily process that does daily cleanup, but relies on the presence of control data that is ETL'd in from another process.

The secondary process failed, and as a result, *everything* was "cleaned" ... aka, we purged an entire dataset.

This data happens to be on a 5 node replicaset (primary-secondary-secondary-arbiter-hidden), and the hidden node died over the holidays and I waited too long to recover it, so it was unable to ever catch up to the primary (always stuck in a RECOVERING state).

My incredible foresight (... laziness ... ) resulted in us having a backup of the data ready to be extracted from the out of sync hidden node. All we had to do was start up **mongod** ... right?

```
2016-01-29T21:06:05.180-0500 I CONTROL  ***** SERVER RESTARTED *****
2016-01-29T21:06:05.241-0500 I CONTROL  [initandlisten] MongoDB starting : pid=1745 port=27021 dbpath=/data 64-bit host=xxx
2016-01-29T21:06:05.241-0500 I CONTROL  [initandlisten] db version v3.0.8
2016-01-29T21:06:05.241-0500 I CONTROL  [initandlisten] git version: 83d8cc25e00e42856924d84e220fbe4a839e605d
2016-01-29T21:06:05.241-0500 I CONTROL  [initandlisten] build info: Linux build3.ny.cbi.10gen.cc 2.6.32-431.3.1.el6.x86_64 #1 SMP Fri Jan 3 21:39:27 UTC 2014 x86_64 BOOST_LIB_VERSION=1_49
2016-01-29T21:06:05.241-0500 I CONTROL  [initandlisten] allocator: tcmalloc
...
2016-01-29T21:06:05.315-0500 W -        [initandlisten] Detected unclean shutdown - /data/mongod.lock is not empty.
2016-01-29T21:06:05.315-0500 W STORAGE  [initandlisten] Recovering data from the last clean checkpoint.
2016-01-29T21:06:05.324-0500 I STORAGE  [initandlisten] wiredtiger_open config: create,cache_size=13G,session_max=20000,eviction=(threads_max=4),statistics=(fast),log=(enabled=true,archive=true
,path=journal,compressor=snappy),file_manager=(close_idle_time=100000),checkpoint=(wait=60,log_size=2GB),statistics_log=(wait=0),
2016-01-29T21:06:05.725-0500 E STORAGE  [initandlisten] WiredTiger (0) [1454119565:724960][1745:0x7f2ac9534bc0], file:WiredTiger.wt, cursor.next: read checksum error for 4096B block at offset 6
799360: block header checksum of 1769173605 doesn't match expected checksum of 4176084783
2016-01-29T21:06:05.725-0500 E STORAGE  [initandlisten] WiredTiger (0) [1454119565:725067][1745:0x7f2ac9534bc0], file:WiredTiger.wt, cursor.next: WiredTiger.wt: encountered an illegal file form
at or internal value
2016-01-29T21:06:05.725-0500 E STORAGE  [initandlisten] WiredTiger (-31804) [1454119565:725088][1745:0x7f2ac9534bc0], file:WiredTiger.wt, cursor.next: the process must exit and restart: WT_PANI
C: WiredTiger library panic
2016-01-29T21:06:05.725-0500 I -        [initandlisten] Fatal Assertion 28558
```

Aw crap. I could not for the life of me get the node back up and running. Since this was a replica-set member, I thought maybe if I just copied the failing file from the (working) primary it would just work. Apparently that's not the way MongoDB or WiredTiger works :P. Back to the drawing board.

<!-- more -->

I could see that my data directory contained a bunch of `collection-*.wt` and `index-*.wt` files, so I assumed these were the WiredTiger collection and index files. These are binary files so `grep`-ing didn't help me identify the collection I needed.

I wanted to next see if I could just copy the collection's backing file directly to a new (working) MongoDB installation, so I started up a new `mongod`, created a new collection with a document in it, then copied over any `collection-*.wt` file to see what would happen.

Guess what ... didn't work.

## Identify the WiredTiger collection's backing file

Since we had access to a working node, plus the collection hadn't been dropped (just purged), I thought maybe the files on each node would be the same. I logged into the primary via the shell to get some info from my collection.

```js
db.getCollection('borkedCollection').stats()

{
    "ns" : "production.borkedCollection",
    "count" : 0,
    "size" : 0,
    "storageSize" : 1138688,
    "capped" : false,
    "wiredTiger" : {
        "metadata" : {
            "formatVersion" : 1
        },
        "creationString" : "allocation_size=4KB,app_metadata=(formatVersion=1),block_allocation=best,block_compressor=snappy,cache_resident=0,checkpoint=(WiredTigerCheckpoint.5149=(addr=\"01808080808080c0b081e40ebe4855808080e3113fc0e401417fc0\",order=5149,time=1454966060,size=21078016,write_gen=119495)),checkpoint_lsn=(224134,44112768),checksum=on,collator=,columns=,dictionary=0,format=btree,huffman_key=,huffman_value=,id=178668,internal_item_max=0,internal_key_max=0,internal_key_truncate=,internal_page_max=4KB,key_format=q,key_gap=10,leaf_item_max=0,leaf_key_max=0,leaf_page_max=32KB,leaf_value_max=1MB,memory_page_max=10m,os_cache_dirty_max=0,os_cache_max=0,prefix_compression=0,prefix_compression_min=4,split_deepen_min_child=0,split_deepen_per_child=0,split_pct=90,value_format=u,version=(major=1,minor=1)",
        "type" : "file",
        "uri" : "statistics:table:collection-7895--1435676552983097781",
        "LSM" : {
            //...
        },
        "block-manager" : {
            //...
        },
        "btree" : {
            // ...
        },
        // ...
    },
    "nindexes" : 4,
    "totalIndexSize" : 1437696,
    "indexSizes" : {
        "_id_" : 212992,
        // ...
    },
    "ok" : 1
}
```

That `"uri" : "statistics:table:collection-7895--1435676552983097781"` entry looked promising.

I started hunting for a way to extract the data from this file without having to "mount" the file in another MongoDB installation, as I assumed this was not possible. I stumbled across a command line utility for WiredTiger that [happened to have a 'salvage' command](http://source.wiredtiger.com/2.7.0/command_line.html#util_salvage).

## Salvaging the WiredTiger collection

In order to use the `wt` utility, you have to build it from source. Being comfortable in Linux, this was not daunting ;)

    wget http://source.wiredtiger.com/releases/wiredtiger-2.7.0.tar.bz2
    tar xvf wiredtiger-2.7.0.tar.bz2
    cd wiredtiger-2.7.0
    sudo apt-get install libsnappy-dev build-essential
    ./configure --enable-snappy
    make

> Adding support for Google's [snappy](https://github.com/google/snappy) compressor when building WiredTiger will save you some errors that I initially encountered when trying to salvage the data.
{: .prompt-tip }

Now that I had a `wt` utility, I wanted to test it out on the collection file. It turns out that you need additional supporting files before you can do this. Once I'd copied over the necessary files, my working directory (called `mongo-bak`) looked like this:

    -rw-r--r-- 1 root      root      4738772992 Feb  9 14:06 collection-2657--1723320556100349955.wt
    -rw-r--r-- 1 root      root         1155072 Feb  9 14:05 _mdb_catalog.wt
    -rw-r--r-- 1 root      root        26935296 Feb  9 14:05 sizeStorer.wt
    -rw-r--r-- 1 root      root              95 Feb  9 14:05 storage.bson
    -rw-r--r-- 1 root      root              46 Feb  9 14:04 WiredTiger
    -rw-r--r-- 1 root      root             495 Feb  9 14:04 WiredTiger.basecfg
    -rw-r--r-- 1 root      root              21 Feb  9 14:04 WiredTiger.lock
    -rw-r--r-- 1 root      root             916 Feb  9 14:04 WiredTiger.turtle
    -rw-r--r-- 1 root      root        10436608 Feb  9 14:04 WiredTiger.wt

Now, from the directory where we compiled WiredTiger, we started salvaging the collection:

    ./wt -v -h ../mongo-bak -C "extensions=[./ext/compressors/snappy/.libs/libwiredtiger_snappy.so]" -R salvage collection-2657--1723320556100349955.wt

You know it's working if you see output along the lines of:

    WT_SESSION.salvage 639400

which I believe is just counting up the number of documents recovered. Once the operation has completed, it will have overwritten the source `*.wt` collection file with whatever it could salvage.

The only issue is that you still can't load this into MongoDB yet.

## Importing the WiredTiger collection via dump/load into MongoDB

In order to get the data into MongoDB, first we need to generate a dump file from the WiredTiger collection file. This is done using the `wt` utility:

    ./wt -v -h ../data -C "extensions=[./ext/compressors/snappy/.libs/libwiredtiger_snappy.so]" -R dump -f ../collection.dump collection-2657--1723320556100349955

This operation produces no output, so you'll just have to sit tight and wait a while. You can always `watch ls -l` in another console if you want to make sure it's working ;)

Once completed, you'll have a `collection.dump` file, but this *still* can't be loaded directly into MongoDB. You can however, using the `wt` utility one more time, load the dump back into a WiredTiger collection.

First, let's startup a new `mongod` instance that we can try this out on.

    mongod --dbpath tmp-mongo --storageEngine wiredTiger --nojournal

Next, let's connect to this instance via the mongo shell and create a new collection:

    use Recovery
    db.borkedCollection.insert({test: 1})
    db.borkedCollection.remove({})
    db.borkedCollection.stats()

I've created a new db called *Recovery*, and inserted/removed a document so the collection's backing file would be generated. You can use the `stats()` method to get the collection name, but since we're only using one collection, it's easy enough to find just using `ls`.

Now we're going to take the backing file name of the collection we just created and use that to load our WiredTiger dump file:

    ./wt -v -h ../data -C "extensions=[./ext/compressors/snappy/.libs/libwiredtiger_snappy.so]" -R load -f ../collection.dump -r collection-2-880383588247732034

Note that we drop the `.wt` extension from the collection file above. Also, the `-h` flag needs to point to the directory where our `mongod` has it's `dbPath`. Finally, `mongod` should not be running.

This operation also provides a progress indicator showing how much data has been loaded:

    table:collection-4--4286091263744514813: 1386220

Once completed, we can start `mongod` back up, shell in and have a look:

```js
$ mongo
MongoDB shell version: 3.2.1
connecting to: test
Mongo-Hacker 0.0.9
laptop(mongod-3.2.1) test> show dbs
Recovery → 0.087GB
local    → 0.000GB
laptop(mongod-3.2.1) test> use Recovery
switched to db Recovery
laptop(mongod-3.2.1) Recovery> show collections
borkedCollection → 0.000MB / 88.801MB
laptop(mongod-3.2.1) Recovery> db.borkedCollection.count()
0
```

WTF? The size looks right, but there are no documents???

```js
laptop(mongod-3.2.1) Recovery> db.borkedCollection.find({}, {_id: 1})
{
  "_id": ObjectId("55e07f3b2e967329c888ac74")
}
{
  "_id": ObjectId("55e07f3b2e967329c888ac76")
}
...
{
  "_id": ObjectId("55e07f402e967329c888ac85")
}
Fetched 20 record(s) in 29ms -- More[true]
```

Well that's promising, but the collection still hasn't been *properly* restored yet.

## Restoring the MongoDB collection to a usable state

This final part is pretty straightforward, as we're just going to do a `mongodump`, followed by a `mongorestore`.

> The `mongodump` will fail if you're using a version of MongoDB < 3.2, as 3.2 is built against WiredTiger 2.7. I initially tested this using MongoDB 3.0.9 and the dump operation just returned 0 results.
{: .prompt-tip }

```
$ mongodump
2016-02-10T22:04:00.580-0500    writing Recovery.borkedCollection to
2016-02-10T22:04:03.579-0500    Recovery.borkedCollection  268219
2016-02-10T22:04:06.579-0500    Recovery.borkedCollection  340655
2016-02-10T22:04:09.579-0500    Recovery.borkedCollection  496787
2016-02-10T22:04:12.579-0500    Recovery.borkedCollection  670894
2016-02-10T22:04:15.579-0500    Recovery.borkedCollection  778539
2016-02-10T22:04:18.579-0500    Recovery.borkedCollection  848525
2016-02-10T22:04:21.579-0500    Recovery.borkedCollection  991277
2016-02-10T22:04:24.579-0500    Recovery.borkedCollection  1147718
2016-02-10T22:04:27.579-0500    Recovery.borkedCollection  1187600
2016-02-10T22:04:30.579-0500    Recovery.borkedCollection  1353665
2016-02-10T22:04:33.579-0500    Recovery.borkedCollection  1376255
2016-02-10T22:04:33.681-0500    Recovery.borkedCollection  1386220
2016-02-10T22:04:33.682-0500    done dumping Recovery.borkedCollection (1386220 documents)

$ mongorestore --drop
2016-02-10T22:05:51.959-0500    using default 'dump' directory
2016-02-10T22:05:51.960-0500    building a list of dbs and collections to restore from dump dir
2016-02-10T22:05:52.307-0500    reading metadata for Recovery.borkedCollection from dump/Recovery/borkedCollection.metadata.json
2016-02-10T22:05:52.330-0500    restoring Recovery.borkedCollection from dump/Recovery/borkedCollection.bson
2016-02-10T22:05:54.962-0500    [#.......................]  Recovery.borkedCollection  32.8 MB/569.8 MB  (5.8%)
2016-02-10T22:05:57.962-0500    [###.....................]  Recovery.borkedCollection  80.5 MB/569.8 MB  (14.1%)
2016-02-10T22:06:00.962-0500    [#####...................]  Recovery.borkedCollection  131.5 MB/569.8 MB  (23.1%)
2016-02-10T22:06:03.962-0500    [#######.................]  Recovery.borkedCollection  178.5 MB/569.8 MB  (31.3%)
2016-02-10T22:06:06.962-0500    [#########...............]  Recovery.borkedCollection  230.1 MB/569.8 MB  (40.4%)
2016-02-10T22:06:09.962-0500    [###########.............]  Recovery.borkedCollection  271.6 MB/569.8 MB  (47.7%)
2016-02-10T22:06:12.962-0500    [#############...........]  Recovery.borkedCollection  320.6 MB/569.8 MB  (56.3%)
2016-02-10T22:06:15.962-0500    [###############.........]  Recovery.borkedCollection  366.3 MB/569.8 MB  (64.3%)
2016-02-10T22:06:18.962-0500    [#################.......]  Recovery.borkedCollection  414.9 MB/569.8 MB  (72.8%)
2016-02-10T22:06:21.962-0500    [###################.....]  Recovery.borkedCollection  464.8 MB/569.8 MB  (81.6%)
2016-02-10T22:06:24.962-0500    [#####################...]  Recovery.borkedCollection  504.0 MB/569.8 MB  (88.4%)
2016-02-10T22:06:27.962-0500    [#######################.]  Recovery.borkedCollection  554.5 MB/569.8 MB  (97.3%)
2016-02-10T22:06:29.082-0500    [########################]  Recovery.borkedCollection  569.8 MB/569.8 MB  (100.0%)
2016-02-10T22:06:29.082-0500    restoring indexes for collection Recovery.borkedCollection from metadata
2016-02-10T22:06:29.104-0500    finished restoring Recovery.borkedCollection (1386220 documents)
2016-02-10T22:06:29.104-0500    done
```

Now that we've dumped and reloaded the collection *yet again*, we can shell back in and validate that our recovery attempt has succeeded:

```js
$ mongo
MongoDB shell version: 3.2.1
connecting to: test
Mongo-Hacker 0.0.9
laptop(mongod-3.2.1) test> show dbs
Recovery → 0.099GB
local    → 0.000GB
laptop(mongod-3.2.1) test> use Recovery
switched to db Recovery
laptop(mongod-3.2.1) Recovery> show collections
borkedCollection → 569.845MB / 88.594MB
laptop(mongod-3.2.1) Recovery> db.borkedCollection.count()
1386220
```

BOOYA! Everything is back and properly accessible.

The `mongorestore` could actually have been done to the primary node in order to recover the data for production purposes. Once that's done, just recreate the necessary indexes and you're back in business.