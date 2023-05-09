---
layout: post
title: "MongoDB Driver Monitoring"
date: 2022-05-15 08:27:09 -0400
comments: true
categories: [MongoDB]
tags: [mongodb, drivers]
image: /images/mongodb-logo.png
---

One of the great things about [MongoDB Drivers](https://www.mongodb.com/docs/drivers/) is that they are all built around a common set of [specifications](https://github.com/mongodb/specifications). Though these specifications exist to facilitate the development of new language drivers or to consistently implement new features across drivers, being aware of them can help when it comes to troubleshooting issues.

One of the more prominent specifications is the [Server Discovery and Monitoring](https://github.com/mongodb/specifications/blob/master/source/server-discovery-and-monitoring/server-discovery-and-monitoring.rst) (SDAM), which defines a set of behaviour in the drivers for providing runtime information about server discovery and monitoring events. These events are further codified in the associated [SDAM Monitoring Specification](https://github.com/mongodb/specifications/blob/master/source/server-discovery-and-monitoring/server-discovery-and-monitoring-monitoring.rst).

Examples exist within the MongoDB documentation (ex: [Node.js 3.6.x](https://www.mongodb.com/docs/drivers/node/v3.6/fundamentals/monitoring/), [Node.js 4.5.x](https://www.mongodb.com/docs/drivers/node/v4.5/fundamentals/monitoring/), [Java 4.3.x](https://www.mongodb.com/docs/drivers/java/sync/v4.3/fundamentals/monitoring/), [C# 2.15.x](https://mongodb.github.io/mongo-csharp-driver/2.15/reference/driver_core/sdamevents/)), however I wanted to collect as many as possible in one place.

Troubleshooting driver-level issues can be challenging, and the [DRIVERS-1204: _Easier debugging with standardized logging_](https://jira.mongodb.org/browse/DRIVERS-1204) initiative exists to improve this however for the time being instrumenting your code is the best form of introspection.

## Node.js

Starting with version 2.1.10 of the Node.js driver [SDAM Monitoring](https://mongodb.github.io/node-mongodb-native/3.6/reference/management/sdam-monitoring/) can be done by subscribing to various SDAM events. With version 3.2 and newer of the driver the [Unified Topology Design](https://mongodb.github.io/node-mongodb-native/3.3/reference/unified-topology/) was introduced, which is why the `useUnifiedTopology` flag is enabled in the sample below.

Note that with version 4.0 of the Node.js driver all legacy topologies were removed and only the unified topology remains. For more examples see the [Cluster Monitoring](https://www.mongodb.com/docs/drivers/node/current/fundamentals/monitoring/cluster-monitoring/) documentation.

```js
const { MongoClient } = require('mongodb');

const uri = 'mongodb+srv://......';
const client = new MongoClient(uri, {
    useUnifiedTopology: true
});
​
// For debugging commands
client.on('commandStarted', (event) => {
    // Will want to log the event somewhere here, ex: console.log('commandStarted', event)
});
client.on('commandFailed', (event) => {
    // Will want to log the event somewhere here.
});
client.on('commandSucceeded', (event) => {
    // Will want to log the event somewhere here.
});
​
client.on('serverDescriptionChanged', (event) => {
    // Will want to log the event somewhere here.
});
​
// For debugging SDAM events
client.on('serverHeartbeatFailed', (event) => {
    // Will want to log the event somewhere here.
});
​
client.on('serverOpening', (event) => {
    // Will want to log the event somewhere here.
});
​
client.on('serverClosed', (event) => {
    // Will want to log the event somewhere here.
});
​
client.on('topologyOpening', (event) => {
    // Will want to log the event somewhere here.
});
​
client.on('topologyClosed', (event) => {
    // Will want to log the event somewhere here.
});
​
client.on('topologyDescriptionChanged', (event) => {
    // Will want to log the event somewhere here.
});
​
// For debugging CMAP events
client.on('connectionCheckOutStarted', (event) => {
    // Will want to log the event somewhere here.
});
​
client.on('connectionCheckOutFailed', (event) => {
    // Will want to log the event somewhere here.
});
​
client.on('connectionCheckedIn', (event) => {
    // Will want to log the event somewhere here.
});
​
client.on('connectionPoolCleared', (event) => {
    // Will want to log the event somewhere here.
});
​
client.on('connectionClosed', (event) => {
    // Will want to log the event somewhere here.
});
​
client.on('connectionPoolClosed', (event) => {
    // Will want to log the event somewhere here.
});
​
await client.connect(uri);
​​
// Please modify each event listener above with the appropriate logging logic that will record the event name and result (ex: console.log('commandStarted', event)).
```

## Java

The driver documentation covers [Monitoring](https://www.mongodb.com/docs/drivers/java/sync/current/fundamentals/monitoring/) in detail, including examples such as the following:

```java
class CommandCounter implements CommandListener {
    private Map<String, Integer> commands = new HashMap<String, Integer>();
    @Override
    public synchronized void commandSucceeded(final CommandSucceededEvent event) {
        String commandName = event.getCommandName();
        int count = commands.containsKey(commandName) ? commands.get(commandName) : 0;
        commands.put(commandName, count + 1);
        System.out.println(commands.toString());
    }
    @Override
    public void commandFailed(final CommandFailedEvent event) {
        System.out.println(String.format("Failed execution of command '%s' with id %s",
                event.getCommandName(),
                event.getRequestId()));
    }
}
```
```java
class CommandCounter implements CommandListener {
    private Map<String, Integer> commands = new HashMap<String, Integer>();
    @Override
    public synchronized void commandSucceeded(final CommandSucceededEvent event) {
        String commandName = event.getCommandName();
        int count = commands.containsKey(commandName) ? commands.get(commandName) : 0;
        commands.put(commandName, count + 1);
        System.out.println(commands.toString());
    }
    @Override
    public void commandFailed(final CommandFailedEvent event) {
        System.out.println(String.format("Failed execution of command '%s' with id %s",
                event.getCommandName(),
                event.getRequestId()));
    }
}
```

My colleague Jorge has an example of this at [`jorge-imperial/MongoTopologyMonitor`](https://github.com/jorge-imperial/MongoTopologyMonitor).

## Go

The sample program below shows how you can use the `CommandMonitor`, `PoolMonitor` and `ServerMonitor`. The post ["MongoDB Cluster Monitoring in Go"](https://deeptiman.medium.com/mongodb-cluster-monitoring-in-go-f95a1230f9f7) offers additional examples you may find useful.

```go
// go run poc.go 2>&1 | tee go_test_$(date +%s).log
package main

import (
	"context"
	"encoding/json"
	"fmt"
	"os"
	"strings"
	"time"

	"github.com/google/uuid"
	"go.mongodb.org/mongo-driver/bson"
	"go.mongodb.org/mongo-driver/bson/primitive"
	"go.mongodb.org/mongo-driver/event"
	"go.mongodb.org/mongo-driver/mongo"
	"go.mongodb.org/mongo-driver/mongo/options"
	"go.mongodb.org/mongo-driver/mongo/readpref"
)

func pp(i interface{}) {
	s, _ := json.Marshal(i)
	fmt.Printf("%T: %s\n", i, string(s))
}

func main() {
	fmt.Println("starting")

  // Your connection string here
  uri := "mongodb+srv://..."
	//////////////////////////////

  ctx := context.Background()
	command_monitor := &event.CommandMonitor{
		Started: func(ctx context.Context, evt *event.CommandStartedEvent) { pp(evt) },
		Succeeded: func(ctx context.Context, evt *event.CommandSucceededEvent) { pp(evt) },
		Failed:    func(ctx context.Context, evt *event.CommandFailedEvent) { pp(evt) },
	}
	pool_monitor := &event.PoolMonitor{
		Event: func(evt *event.PoolEvent) {
			if strings.Contains(string(evt.Type), "Failed") {
				pp(evt)
			}
		},
	}
	server_monitor := &event.ServerMonitor{
		ServerDescriptionChanged:   func(evt *event.ServerDescriptionChangedEvent) { pp(evt) },
		ServerOpening:              func(evt *event.ServerOpeningEvent) { pp(evt) },
		ServerClosed:               func(evt *event.ServerClosedEvent) { pp(evt) },
		TopologyDescriptionChanged: func(evt *event.TopologyDescriptionChangedEvent) { pp(evt) },
		TopologyOpening:            func(evt *event.TopologyOpeningEvent) { pp(evt) },
		TopologyClosed:             func(evt *event.TopologyClosedEvent) { pp(evt) },
		ServerHeartbeatStarted:     func(evt *event.ServerHeartbeatStartedEvent) { pp(evt) },
		ServerHeartbeatSucceeded:   func(evt *event.ServerHeartbeatSucceededEvent) { pp(evt) },
		ServerHeartbeatFailed:      func(evt *event.ServerHeartbeatFailedEvent) { pp(evt) },
	}

	client, err := mongo.NewClient(
		options.Client().
			ApplyURI(uri).
			SetPoolMonitor(pool_monitor).
			SetServerMonitor(server_monitor).
			SetMonitor(command_monitor))
	if err != nil {
		fmt.Printf("error creating client: %v\n", err)
		os.Exit(1)
	}

	err = client.Connect(ctx)
	if err != nil {
		fmt.Printf("error connecting: %v\n", err)
		os.Exit(1)
	}

	err = client.Ping(ctx, readpref.Primary())
	if err != nil {
		fmt.Printf("error pinging: %v\n", err)
		os.Exit(1)
	}

	fmt.Println("connected")

	for {
		time.Sleep(2 * time.Second)
		fmt.Println("")
		fmt.Println(time.Now().String())

		collection := client.Database("test").Collection("items")
		id := uuid.New().String()
		_, err := collection.InsertOne(ctx, bson.D{
			{Key: "uuid", Value: id},
		})
		if err != nil {
			fmt.Printf("Insert error - %v\n", err)
			continue
		}
		findResult := collection.FindOne(ctx, bson.D{
			{Key: "uuid", Value: id},
		})

		if findResult.Err() != nil {
			fmt.Printf("Find error: %v\n", err)
			continue
		}
		result := struct {
			ID   primitive.ObjectID `bson:"_id"`
			UUID string             `bson:"uuid"`
		}{}

		err = findResult.Decode(&result)

		if err != nil {
			fmt.Printf("Error decoding: %v\n", err)
		}

		fmt.Printf("Got the result: %s\n", result.UUID)
	}
}
```

## Ruby

The [Ruby Driver's Monitoring](https://www.mongodb.com/docs/ruby-driver/master/reference/monitoring/index.html) documentation outlines how to create event subscribers in great detail. These are summarized in the sample application below.

```ruby
# ruby poc.rb 2>&1 | tee ruby_test_$(date +%s).log
require 'bundler/inline'
require 'securerandom'
gemfile do
  source 'https://rubygems.org'
  gem 'mongo'
end

class SDAMLogSubscriber
  include Mongo::Loggable

  def succeeded(event)
    log_debug(format_message(event.inspect))
  end

  private

  def logger
    Mongo::Logger.logger
  end

  def format_message(message)
    format("SDAM | %s".freeze, message)
  end
end

Mongo::Logger.logger.level = Logger::DEBUG
Mongo::Monitoring::Global.subscribe(Mongo::Monitoring::CONNECTION_POOL, Mongo::Monitoring::CmapLogSubscriber.new)
Mongo::Monitoring::Global.subscribe(Mongo::Monitoring::TOPOLOGY_OPENING, SDAMLogSubscriber.new)
Mongo::Monitoring::Global.subscribe(Mongo::Monitoring::SERVER_OPENING, SDAMLogSubscriber.new)
Mongo::Monitoring::Global.subscribe(Mongo::Monitoring::SERVER_DESCRIPTION_CHANGED, SDAMLogSubscriber.new)
Mongo::Monitoring::Global.subscribe(Mongo::Monitoring::TOPOLOGY_CHANGED, SDAMLogSubscriber.new)
Mongo::Monitoring::Global.subscribe(Mongo::Monitoring::SERVER_CLOSED, SDAMLogSubscriber.new)
Mongo::Monitoring::Global.subscribe(Mongo::Monitoring::TOPOLOGY_CLOSED, SDAMLogSubscriber.new)

# Your connection string here
client = Mongo::Client.new('mongodb+srv://...')
#############################

loop do
  sleep 2
  collection = client[:items]
  id = SecureRandom.uuid
  doc = { Key: "uuid", Value: id }
  begin
    collection.insert_one(doc)
  rescue => ex
    puts "Insert error - #{ex}\n"
  end
  begin
    response = collection.find(doc).first
    puts "Got the result: #{response}\n"
  rescue => ex
    puts "Find error - #{ex}\n"
  end
end
```

## C#/.NET

The C# driver allows the use of a [`MongoClientSettings.SdamLogFilename`](https://mongodb.github.io/mongo-csharp-driver/2.15/apidocs/html/P_MongoDB_Driver_MongoClientSettings_SdamLogFilename.htm) property to be set which will write most SDAM events to a log file without further configuration.

In the example below we use the [`IEventSubscriber`](https://mongodb.github.io/mongo-csharp-driver/2.15/apidocs/html/T_MongoDB_Driver_Core_Events_IEventSubscriber.htm) interface instead to build a custom event subscriber that can be used to emit event details to `STDOUT`.

```csharp
using MongoDB.Bson;
using MongoDB.Driver;
using MongoDB.Driver.Core.Events;
using System;
using System.Web.Script.Serialization;

namespace ConsoleApp1
{
    internal class Program
    {
        private static void Main(string[] args)
        {
            var settings = MongoClientSettings.FromConnectionString("mongodb://localhost:27017/test");
            settings.ClusterConfigurator = builder =>
            {
                builder.Subscribe(new CustomEventSubscriber());
            };

            var client = new MongoClient(settings);
            var database = client.GetDatabase("test");
            var collection = database.GetCollection<BsonDocument>("foo");
            var filter = Builders<BsonDocument>.Filter.Eq("bar", 1);

            var output = collection.CountDocuments(filter);

            Console.WriteLine(output); // 1
            Console.ReadKey();
        }
    }

    public class CustomEventSubscriber : IEventSubscriber
    {
        private readonly IEventSubscriber _subscriber;
        private readonly JavaScriptSerializer _serializer;

        public CustomEventSubscriber()
        {
            _subscriber = new ReflectionEventSubscriber(this);
            _serializer = new JavaScriptSerializer();
        }

        public bool TryGetEventHandler<TEvent>(out Action<TEvent> handler)
        {
            return _subscriber.TryGetEventHandler(out handler);
        }

        public void Handle(ClusterAddedServerEvent e)
        {
            Console.WriteLine($"{e.GetType().Name}: {_serializer.Serialize(e)}");
        }

        public void Handle(ClusterAddingServerEvent e)
        {
            Console.WriteLine($"{e.GetType().Name}: {_serializer.Serialize(e)}");
        }

        public void Handle(ClusterClosedEvent e)
        {
            Console.WriteLine($"{e.GetType().Name}: {_serializer.Serialize(e)}");
        }

        public void Handle(ClusterClosingEvent e)
        {
            Console.WriteLine($"{e.GetType().Name}: {_serializer.Serialize(e)}");
        }

        public void Handle(ClusterDescriptionChangedEvent e)
        {
            Console.WriteLine($"{e.GetType().Name}: Old = {e.OldDescription} / New = {e.NewDescription}");
        }

        public void Handle(ClusterOpenedEvent e)
        {
            Console.WriteLine($"{e.GetType().Name}: {_serializer.Serialize(e)}");
        }

        public void Handle(ClusterOpeningEvent e)
        {
            Console.WriteLine($"{e.GetType().Name}: {_serializer.Serialize(e)}");
        }

        public void Handle(ClusterRemovedServerEvent e)
        {
            Console.WriteLine($"{e.GetType().Name}: {_serializer.Serialize(e)}");
        }

        public void Handle(ClusterRemovingServerEvent e)
        {
            Console.WriteLine($"{e.GetType().Name}: {_serializer.Serialize(e)}");
        }

        public void Handle(ClusterSelectedServerEvent e)
        {
            Console.WriteLine($"{e.GetType().Name}: {_serializer.Serialize(e)}");
        }

        public void Handle(ClusterSelectingServerEvent e)
        {
            Console.WriteLine($"{e.GetType().Name}: {_serializer.Serialize(e)}");
        }

        public void Handle(ClusterSelectingServerFailedEvent e)
        {
            Console.WriteLine($"{e.GetType().Name}: {_serializer.Serialize(e)}");
        }

        public void Handle(CommandFailedEvent e)
        {
            Console.WriteLine($"{e.GetType().Name}: {_serializer.Serialize(e)}");
        }

        public void Handle(ConnectionClosedEvent e)
        {
            Console.WriteLine($"{e.GetType().Name}: {_serializer.Serialize(e)}");
        }

        public void Handle(ConnectionClosingEvent e)
        {
            Console.WriteLine($"{e.GetType().Name}: {_serializer.Serialize(e)}");
        }

        public void Handle(ConnectionCreatedEvent e)
        {
            Console.WriteLine($"{e.GetType().Name}: {_serializer.Serialize(e)}");
        }

        public void Handle(ConnectionFailedEvent e)
        {
            Console.WriteLine($"{e.GetType().Name}: {_serializer.Serialize(e)}");
        }

        public void Handle(ConnectionOpenedEvent e)
        {
            Console.WriteLine($"{e.GetType().Name}: {_serializer.Serialize(e)}");
        }

        public void Handle(ConnectionOpeningEvent e)
        {
            Console.WriteLine($"{e.GetType().Name}: {_serializer.Serialize(e)}");
        }

        public void Handle(ConnectionOpeningFailedEvent e)
        {
            Console.WriteLine($"{e.GetType().Name}: {_serializer.Serialize(e)}");
        }

        public void Handle(ConnectionPoolAddedConnectionEvent e)
        {
            Console.WriteLine($"{e.GetType().Name}: {_serializer.Serialize(e)}");
        }

        public void Handle(ConnectionPoolAddingConnectionEvent e)
        {
            Console.WriteLine($"{e.GetType().Name}: {_serializer.Serialize(e)}");
        }

        public void Handle(ConnectionPoolCheckedInConnectionEvent e)
        {
            Console.WriteLine($"{e.GetType().Name}: {_serializer.Serialize(e)}");
        }

        public void Handle(ConnectionPoolCheckedOutConnectionEvent e)
        {
            Console.WriteLine($"{e.GetType().Name}: {_serializer.Serialize(e)}");
        }

        public void Handle(ConnectionPoolCheckingInConnectionEvent e)
        {
            Console.WriteLine($"{e.GetType().Name}: {_serializer.Serialize(e)}");
        }

        public void Handle(ConnectionPoolCheckingOutConnectionEvent e)
        {
            Console.WriteLine($"{e.GetType().Name}: {_serializer.Serialize(e)}");
        }

        public void Handle(ConnectionPoolCheckingOutConnectionFailedEvent e)
        {
            Console.WriteLine($"{e.GetType().Name}: {_serializer.Serialize(e)}");
        }

        public void Handle(ConnectionPoolClearedEvent e)
        {
            Console.WriteLine($"{e.GetType().Name}: {_serializer.Serialize(e)}");
        }

        public void Handle(ConnectionPoolClearingEvent e)
        {
            Console.WriteLine($"{e.GetType().Name}: {_serializer.Serialize(e)}");
        }

        public void Handle(ConnectionPoolClosedEvent e)
        {
            Console.WriteLine($"{e.GetType().Name}: {_serializer.Serialize(e)}");
        }

        public void Handle(ConnectionPoolClosingEvent e)
        {
            Console.WriteLine($"{e.GetType().Name}: {_serializer.Serialize(e)}");
        }

        public void Handle(ConnectionPoolOpenedEvent e)
        {
            Console.WriteLine($"{e.GetType().Name}: {_serializer.Serialize(e)}");
        }

        public void Handle(ConnectionPoolOpeningEvent e)
        {
            Console.WriteLine($"{e.GetType().Name}: {_serializer.Serialize(e)}");
        }

        public void Handle(ConnectionPoolRemovedConnectionEvent e)
        {
            Console.WriteLine($"{e.GetType().Name}: {_serializer.Serialize(e)}");
        }

        public void Handle(ConnectionPoolRemovingConnectionEvent e)
        {
            Console.WriteLine($"{e.GetType().Name}: {_serializer.Serialize(e)}");
        }

        //public void Handle(ConnectionReceivedMessageEvent e)
        //{
        //    Console.WriteLine($"{e.GetType().Name}: {_serializer.Serialize(e)}");
        //}

        //public void Handle(ConnectionReceivingMessageEvent e)
        //{
        //    Console.WriteLine($"{e.GetType().Name}: {_serializer.Serialize(e)}");
        //}

        public void Handle(ConnectionReceivingMessageFailedEvent e)
        {
            Console.WriteLine($"{e.GetType().Name}: {_serializer.Serialize(e)}");
        }

        //public void Handle(ConnectionSendingMessagesEvent e)
        //{
        //    Console.WriteLine($"{e.GetType().Name}: {_serializer.Serialize(e)}");
        //}

        public void Handle(ConnectionSendingMessagesFailedEvent e)
        {
            Console.WriteLine($"{e.GetType().Name}: {_serializer.Serialize(e)}");
        }

        //public void Handle(ConnectionSentMessagesEvent e)
        //{
        //    Console.WriteLine($"{e.GetType().Name}: {_serializer.Serialize(e)}");
        //}

        public void Handle(SdamInformationEvent e)
        {
            Console.WriteLine($"{e.GetType().Name}: {_serializer.Serialize(e)}");
        }

        public void Handle(ServerClosedEvent e)
        {
            Console.WriteLine($"{e.GetType().Name}: {_serializer.Serialize(e)}");
        }

        public void Handle(ServerClosingEvent e)
        {
            Console.WriteLine($"{e.GetType().Name}: {_serializer.Serialize(e)}");
        }

        public void Handle(ServerDescriptionChangedEvent e)
        {
            Console.WriteLine($"{e.GetType().Name}: Old = {e.OldDescription} / New = {e.NewDescription}");
        }

        public void Handle(ServerHeartbeatFailedEvent e)
        {
            Console.WriteLine($"{e.GetType().Name}: {e.ConnectionId}");
        }

        public void Handle(ServerOpenedEvent e)
        {
            Console.WriteLine($"{e.GetType().Name}: {_serializer.Serialize(e)}");
        }

        public void Handle(ServerOpeningEvent e)
        {
            Console.WriteLine($"{e.GetType().Name}: {_serializer.Serialize(e)}");
        }
    }
}
```

## C++

This example requires a little more setup as the necessary versions of bot the [C Driver](https://www.mongodb.com/docs/drivers/c/) and [C++ Driver](https://www.mongodb.com/docs/drivers/cxx/) need to be compiled and installed.

```bash
# Setup environment for C/C++ drivers
export WORKDIR=$(pwd)
export CDRIVER_VERSION=1.17.4
export CPPDRIVER_VERSION=3.6.2
export LD_LIBRARY_PATH=/usr/local/lib
sudo apt-get update && sudo apt-get install -y build-essential wget cmake git pkg-config libssl-dev libsasl2-dev
mkdir -p ${WORKDIR} && cd ${WORKDIR}
wget https://github.com/mongodb/mongo-c-driver/releases/download/${CDRIVER_VERSION}/mongo-c-driver-${CDRIVER_VERSION}.tar.gz && \
  tar xzf mongo-c-driver-${CDRIVER_VERSION}.tar.gz
cd ${WORKDIR}/mongo-c-driver-${CDRIVER_VERSION} && \
  mkdir cmake-build && \
  cd cmake-build && \
  cmake -DENABLE_AUTOMATIC_INIT_AND_CLEANUP=OFF .. && \
  make && sudo make install
cd ${WORKDIR}
wget https://github.com/mongodb/mongo-cxx-driver/archive/r${CPPDRIVER_VERSION}.tar.gz && \
  tar -xzf r${CPPDRIVER_VERSION}.tar.gz
cd ${WORKDIR}/mongo-cxx-driver-r${CPPDRIVER_VERSION}/build && \
  echo $CPPDRIVER_VERSION > VERSION_CURRENT && \
  cmake -DCMAKE_BUILD_TYPE=Release -DBSONCXX_POLY_USE_BOOST=1 -DENABLE_UNINSTALL=ON \
  -DCMAKE_INSTALL_PREFIX=/usr/local -DCMAKE_PREFIX_PATH=/usr/local .. && \
  sudo cmake --build . --target install
```

Once the environment is setup, the following sample application can be used to monitor SDAM events. Note only the `ServerDescriptionChanged` is monitored, however this list can be expanded as needed (see [`mongocxx::options::apm` Class Reference](http://mongocxx.org/api/current/classmongocxx_1_1options_1_1apm.html) documentation for more information).

```cpp
// save as test.cpp and compile as follows:
//   c++ --std=c++11 test.cpp -o test $(pkg-config --cflags --libs libmongocxx)
#include <iostream>
#include <time.h>
#include <bsoncxx/builder/stream/document.hpp>
#include <bsoncxx/json.hpp>
#include <mongocxx/client.hpp>
#include <mongocxx/instance.hpp>
#include <mongocxx/pool.hpp>

void work(mongocxx::pool& pool) {
    auto conn = pool.acquire();
    auto collection = (*conn)["test"]["foo"];
/*
void work(const mongocxx::client& conn) {
    bsoncxx::builder::stream::document document{};
    auto collection = conn["test"]["foo"];
*/
    bsoncxx::builder::stream::document document{};
    document << "foo" << "bar";
    document << "t" << bsoncxx::types::b_date(std::chrono::system_clock::now());

    try {
        //collection.insert_one(document.view());
        bsoncxx::builder::stream::document order{};
        order << "_id" << -1;
        auto opts = mongocxx::options::find{};
        opts.sort(order.view());
        auto result = collection.find_one({}, opts);
        std::cout << "Last: " << bsoncxx::to_json(*result) << std::endl;
    } catch (std::exception& e) {
        std::cout << "Error: " << e.what() << std::endl;
    }
}

int main(int, char**) {
    mongocxx::options::apm apm_opts;
    mongocxx::options::client client_opts;

    // http://mongocxx.org/api/current/classmongocxx_1_1options_1_1apm.html for other options
    apm_opts.on_server_changed([&](const mongocxx::events::server_changed_event& event) {
      std::cout << "ServerDescriptionChanged " << bsoncxx::to_json(event.new_description().is_master()) << std::endl;
    });

    client_opts.apm_opts(apm_opts);
    mongocxx::instance inst{};

    mongocxx::uri uri{"mongodb://..."};

    mongocxx::pool pool{uri, client_opts};
    // mongocxx::client conn{uri, client_opts};

    int n = 2; // wait 2 seconds between loops
    int milli_seconds = n * 1000;
    time_t start, end;
    start = time(0);
    std::cout << "Starting. New document will be inserted every " << n << " second(s)." << std::endl;
    while (1) {
        if (time(0) - start == n) {
            work(pool);
            start = start + n;
            std::cout << "Tick: " << start << std::endl;
        }
    }
}
```

## PHP

**TODO**

* https://gist.github.com/jmikola/dfcad9bc4e512b22dbb04beed4dc0a99
* https://www.php.net/manual/en/mongodb.tutorial.apm.php


The goal will be to collect more examples over time and post them here. If you have anything you'd like to share that I haven't covered, please feel free to comment below ;)

Happy Coding!