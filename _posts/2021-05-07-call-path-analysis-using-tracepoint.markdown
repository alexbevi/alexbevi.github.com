---
layout: post
title: "Ruby Call Path Analysis using TracePoint"
date: 2021-05-07 09:56:11 -0400
comments: true
categories: [Programming]
tags: [ruby, mongodb]
---

During a recent diagnostic analysis exercise I needed to identify if there was additional "work" being done based on a single option being changed. As Ruby offers numerous productivity tools for developers it should come as no surprise that a mechanism to easily produce a full call stack for one to many operations exists.

The code below is using the [MongoDB Ruby Driver](https://docs.mongodb.com/ruby-driver/master/) and [Mongoid ODM](https://docs.mongodb.com/mongoid/current/) to [`$sample`](https://docs.mongodb.com/manual/reference/operator/aggregation/sample/) a single document with a [Read Preference](https://docs.mongodb.com/manual/core/read-preference) passed in from the command line. The collection likely won't exist however the goal of this analysis was simply to see what differences changing the read preference would expose.

For the purposes of my analysis I wanted to produce a [diff](https://en.wikipedia.org/wiki/Diff) of two call stacks to try and see "where" there may be a difference in the amount of "work" being performed. To do this the first step was to introduce instrumentation via a [TracePoint](https://ruby-doc.org/core-2.7.0/TracePoint.html).

```ruby
# test.rb
# ruby test.rb [primary|secondary]
require 'bundler/inline'
gemfile do
  source 'https://rubygems.org'

  gem 'mongoid', '7.0.4'
  gem 'mongo', '2.11.1'
end

Mongoid.configure do |config|
  config.clients.default = { uri: "mongodb+srv://..." }
end

class Sample
  include Mongoid::Document
end

def with_tracepoint
  trace = []
  tp = TracePoint.new(:call) do |x|
    trace << "#{x.defined_class}##{x.method_id.to_s} @ #{x.path}"
  end
  tp.enable
  yield
  return trace
ensure
  tp.disable unless tp.nil?
end

# first argument to symbol
read_pref = ARGV[0].nil? ? :primary : ARGV[0].to_sym
# run first command to establish a connection
Sample.collection.aggregate([{ :'$sample' => { size: 1 } }], read: { mode: read_pref }).first
trace = with_tracepoint do
  Sample.collection.aggregate([{ :'$sample' => { size: 1 } }], read: { mode: read_pref }).first
end

puts trace
```

The above will trace all Ruby method calls executed within the block and push them into an array. By running the above script twice with different options and feeding the results into a `diff` tool (such as [`icdiff`](https://www.jefftk.com/icdiff)) a visual representation of how the call stacks differ can be generated.

```bash
icdiff -N <(ruby test.rb primary) <(ruby test.rb secondary) | less
```

![](/images/ruby-diff-tp.png)

(Open screenshot in a new tab to get a better look)

The `with_tracepoint` helper method in the script above is only filtering on `:call`s, however can easily be modified to filter based on your particular needs (see [TracePoint Events](https://ruby-doc.org/core-2.7.0/TracePoint.html#class-TracePoint-label-Events) for the full list).

Let me know if this approach helped you troubleshoot a particular issue or identify an interesting defect.

Happy Coding!
