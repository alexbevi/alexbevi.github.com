---
layout: post
title: "Analysis and Optimization of an N+1 Scenario in Mongoid"
date: 2021-03-26 09:16:09 -0400
comments: true
categories: [Ruby]
tags: [mongodb, mongoid, ruby]
image: /images/mongodb-logo.png
---

The `N + 1` queries problem is a common issue Rails applications face whereby iterating an array of models and accessing an association results in a sub-optimal pattern of recurring queries.

To address this Rails offers [Eager Loading Associations](https://guides.rubyonrails.org/active_record_querying.html#eager-loading-associations) and there are gems (such as [bullet](https://github.com/flyerhzm/bullet)) that can be used to detect the `N + 1` pattern in an application.

This `N + 1` problem can manifest in any [ODM or ORM](https://medium.com/spidernitt/orm-and-odm-a-brief-introduction-369046ec57eb), including when working with MongoDB and Ruby.

For the purposes of this example we have a Ruby application that is using the [Mongoid](https://docs.mongodb.com/mongoid/current/) ODM with a minimal [Document](https://docs.mongodb.com/mongoid/current/tutorials/mongoid-documents/) model that contains a single [Field](https://docs.mongodb.com/mongoid/current/tutorials/mongoid-documents/#fields) definition. The scripts to setup the cluster and seed the data are shared at the end of this article (see _Reproduction_).

<!-- MORE -->

Our model only defines a single field, but an external process updates the underlying document in the MongoDB cluster with telemetry entries. As no schema is enforced, this is perfectly valid however the documents may grow too large over time for which we've written the following Ruby application to periodically clean up:

```ruby
#
# mongoid_n_plus_1.rb
#
require 'benchmark'
require 'bundler/inline'

gemfile do
  source 'https://rubygems.org'

  gem 'mongoid'
  gem 'mongo'
end

Mongoid.configure do |config|
  config.clients.default = {
    uri: "mongodb://localhost:27017,localhost:27018,localhost:27019/test"
  }
end

class Test
  include Mongoid::Document

  field :name, type: String

  # return all entries from the document that aren't defined as Mongoid fields
  def entries
    attr = self.attributes.dup
    attr.delete_if { |k, v| self.fields.key?(k) }
    attr.sort
  end

  def compact!
    # unset each field that doesn't belong to the Mongoid document as an
    # explicitly defined field
    self.entries.each do |entry|
      self.unset entry.first
    end
  end
end
```

Using a Ruby REPL we can require the above code and verify it's connecting to our cluster and interacting with our document:

```ruby
> require_relative 'mongoid_n_plus_1'
 => true
> t = Test.first
=> #<Test _id: 1.0, name: "Alex">
> t.entries.length
=> 10000
> t.entries[0..15]
=> [["2021-03-25T10:30:21", 1.0],
 ["2021-03-25T10:30:22", 2.0],
 ["2021-03-25T10:30:23", 3.0],
 ["2021-03-25T10:30:24", 4.0],
 ["2021-03-25T10:30:25", 5.0],
 ["2021-03-25T10:30:26", 6.0],
 ["2021-03-25T10:30:27", 7.0],
 ["2021-03-25T10:30:28", 8.0],
 ["2021-03-25T10:30:29", 9.0],
 ["2021-03-25T10:30:30", 10.0],
 ["2021-03-25T10:30:31", 11.0],
 ["2021-03-25T10:30:32", 12.0],
 ["2021-03-25T10:30:33", 13.0],
 ["2021-03-25T10:30:34", 14.0],
 ["2021-03-25T10:30:35", 15.0],
 ["2021-03-25T10:30:36", 16.0]]
```

Next let's measure our `compact!` operations:

```ruby
> puts Benchmark.measure { t.compact! }
  17.319826   1.025931  18.345757 ( 55.004495)
```

We're only modifying a single document, after reviewing the FTDC<sup>[1](#fn1)</sup> it appears there are about 10K update operations issued, which is taking about a minute to completed.

![](/images/nplus1-1.png)

After reviewing the documentation for MongoDB's [`$unset`](https://docs.mongodb.com/manual/reference/operator/update/unset/) update operator it appears we can pass more than one field at a time. If this is the case, we can send a single command with a list of 10K fields as opposed to 10K commands with a single field each.

To test this we modify our `compact!` method as follow:

```ruby
  def compact!
    # each field in the `entries` array is a [k,v] array
    # map the `k` (field) values into a single array and send them all
    # as a single unset command
    self.unset self.entries.map(&:first)
  end
```

After testing this the result confirms our theory and the performance is significantly better:

```ruby
> puts Benchmark.measure { t.compact! }
  0.150776   0.002509   0.153285 (  0.273297)
```

Reviewing the FTDC again shows only a single command was issued:

![](/images/nplus1-2.png)

Anytime operations are being sent to the server from within a loop there may be an opportunity to group/batch actions in a more efficient manner. The first step to improving performance is being able to identify an opportunity for improvement, which I hope this article helps you do.

Happy Coding!

### Reproduction

First, we spin up a local [replica set](https://docs.mongodb.com/manual/replication) using some open source MongoDB helper utilities (see [`m`](https://github.com/aheckmann/m) and [`mtools`](https://github.com/rueckstiess/mtools)):

```bash
m 4.2.13
mlaunch init --replicaset --nodes 3 --binarypath $(m bin 4.2.13) --host localhost --bind_ip_all
mongo "mongodb://localhost:27017,localhost:27018,localhost:27019/test" test.js
```

The JavaScript file (`test.js`) above is used to seed the collection with a single document and 10,000 telemetry entries:

```js
// test.js
db.tests.drop();
db.tests.insert({ _id: 1, name: "Alex" });

var d = new Date();
var update = {};
for (var i = 0; i < 10000; i++) {
   d.setSeconds(d.getSeconds() + 1);
   update[d.toISOString().split('.')[0]] = i+1;
}
db.tests.update({ _id: 1 }, { $set: update })
```

From the [`mongo`](https://docs.mongodb.com/manual/mongo/) or [`mongosh`](https://docs.mongodb.com/mongodb-shell/) the result of this script can be verified:

```bash
 mongo "mongodb://localhost:27017,localhost:27018,localhost:27019/test" --quiet --eval 'db.tests.find().pretty()'
{
  "_id": 1,
  "name": "Alex",
  "2021-03-25T10:55:23": 1,
  "2021-03-25T10:55:24": 2,
  "2021-03-25T10:55:25": 3,
  "2021-03-25T10:55:26": 4,
  ...
  "2021-03-25T13:41:59": 9997,
  "2021-03-25T13:42:00": 9998,
  "2021-03-25T13:42:01": 9999,
  "2021-03-25T13:42:02": 10000
}
```

<hr>
<small><a name="fn1">1</a>: As a MongoDB Technical Services engineer I have access to tools we can use to parse the cluster's `FTDC` (see ["What is MongoDB FTDC (aka. diagnostic.data)"]({% post_url 2020-01-26-what-is-mongodb-ftdc-aka-diagnostic-dot-data %}) for more info) and visualize time series performance telemetry, which were used to generate the following charts.</small>
