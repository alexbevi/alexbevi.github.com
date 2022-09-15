---
layout: post
title: "Performance Profiling a Mongoid Issue Using AppProfiler"
date: 2022-09-09 06:41:01 -0400
comments: true
categories: "Ruby"
tags: [mongoid, ruby, rails, mongodb]
---

In [MONGOID-4889](https://jira.mongodb.org/browse/MONGOID-4889) the claim was made that assignment of a large number of embedded documents to an instance of a model will take increasingly longer as the size of the list of documents to embed grows. This is notable as no database operations are being performed during this process, which points to potential issues with the library itself. The ticket author identified [`Mongoid::Association::Embedded::EmbedsMany::Proxy#object_already_related?`](https://github.com/mongodb/mongoid/blob/v8.0.0/lib/mongoid/association/embedded/embeds_many/proxy.rb#L359-L361) as the likely source of this performance issue, however I wanted to see how best to validate this.

While doing research on Ruby profiling I found Shopify's blog post on ["How to Fix Slow Code in Ruby"](https://shopify.engineering/how-fix-slow-code-ruby). Though the entire post was extremely insightful, it lead me to Shopify's [`app_profiler`](https://github.com/Shopify/app_profiler) library, which can be used to automatically profile code and redirect the output to a local instance of [speedscope](https://github.com/jlfwong/speedscope). Having worked previously with [Flame Graphs](https://www.brendangregg.com/flamegraphs.html) of CPU stack traces collected using [`perf`](https://man7.org/linux/man-pages/man1/perf.1.html).

Adapting the sample code in the Jira ticket results in the following:

```ruby
require 'bundler/inline'

gemfile do
  source 'https://rubygems.org'

  gem 'mongoid'
  gem 'app_profiler'
end

class Foo
  include Mongoid::Document
  embeds_many :bars
end

class Bar
  include Mongoid::Document
  embedded_in :foo
end

# AppProfiler forms the output filename using Time.zone.now
require 'active_support/core_ext/time/zones'
Time.zone = 'Pacific Time (US & Canada)'
AppProfiler.root = Pathname.new(__dir__)
AppProfiler.profile_root = Pathname.new(__dir__)

arr = Array.new(2000) { Bar.new }
report = AppProfiler.run(mode: :cpu) do
  Foo.new.bars = arr
end
report.view
```

Running the above code doesn't require a MongoDB connection string or an active cluster, but will attempt to embed 2000 new instances of `Bar` into the newly created instance of `Foo`. Once completed, the following chart is produced that reinforces the initial suspicion that the calls to `object_already_related?` are a likely candidate for further investigation.

![](/images/ruby-profiler.png)

AppProfiler was designed to be injected into a Rails application, however as can be seen above, it can easily be adapted to work on a standalone Ruby script as well.

<div class="note info">
<small><em>Cross posted to <a href="https://dev.to/alexbevi/performance-profiling-a-mongoid-issue-using-appprofiler-38p4">DEV</a></em></small>
</div>