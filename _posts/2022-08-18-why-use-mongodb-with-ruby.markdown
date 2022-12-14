---
layout: post
title: "Why Use MongoDB with Ruby"
date: 2022-08-18 11:23:27 -0400
comments: true
categories: MongoDB
tags: ["ruby", "rails", "mongodb", "cross-post"]
image:
  src: /images/mongodb-logo.png
  alt: MongoDB Logo
canonical_url: https://www.mongodb.com/developer/products/mongodb/why-use-mongodb-with-ruby/
---
<div class="note info">
<small><em>Cross posted from <a href="https://www.mongodb.com/developer/products/mongodb/why-use-mongodb-with-ruby/">MongoDB Developer Center</a></em></small>
</div>

Before discovering Ruby and Ruby on Rails I was a .NET developer. At that time I'd make ad-hoc changes to my development database, export my table/function/stored procedure/view definitions to text files and check them into source control with any code changes. Using `diff` functionality I'd compare the schema changes that the DBAs needed to apply to production and we'd script that out separately.

I'm sure better tools existed (and I eventually started using some of [RedGate's tools](https://www.red-gate.com/solutions/role/development)), but I was looking for a change. At that time, the real magic of Ruby on Rails for me was the [Active Record Migrations](https://guides.rubyonrails.org/active_record_migrations.html) which made working with my database fit with my programming workflow. Schema management became less of a chore and there were `rake` tasks for anything I needed (applying migrations, rolling back changes, seeding a test database).

Schema versioning and management with Rails was leaps and bounds better than what I was used to, and I didn't think this could get any better - but then I found MongoDB.

When working with MongoDB there's no need to `CREATE TABLE foo (id integer, bar varchar(255), ...)`; if a collection (or associated database) doesn't exist, inserting a new document will automatically create it for you. This means Active Record migrations are no longer needed as this level of schema change management was no longer necessary.

Having the flexibility to define my data model directly within the code without needing to resort to the intermediary management that Active Record had facilitated just sort of made sense to me. I could now persist object state to my database directly, embed related model details and easily form queries around these structures to quickly retrieve my data.

## Flexible Schema

Data in MongoDB has a flexible schema as [collections](https://www.mongodb.com/docs/manual/reference/glossary/#std-term-collection) do not enforce a strict [document](https://www.mongodb.com/docs/manual/reference/glossary/#std-term-document) structure or schema by default. This flexibility gives you data-modeling choices to match your application and its performance requirements, which aligns perfectly with Ruby's focus on simplicity and productivity.

## Let's Try It Out

We can easily demonstrate how to quickly get started using the [MongoDB Ruby Driver](https://www.mongodb.com/docs/ruby-driver/master/) using the following simple Ruby script that will connect to a cluster, insert a document and read it back:

```ruby
require 'bundler/inline'

gemfile do
  source 'https://rubygems.org'
  gem 'mongo'
end

client = Mongo::Client.new('mongodb+srv://username:password@mycluster.mongodb.net/test')
collection = client[:foo]
collection.insert_one({ bar: "baz" })

puts collection.find.first
# => {"_id"=>BSON::ObjectId('62d83d9dceb023b20aff228a'), "bar"=>"baz"}
```

When the document above is inserted an `_id` value of `BSON::ObjectId('62d83d9dceb023b20aff228a')` is created. All documents must have an [`_id` field](https://www.mongodb.com/docs/manual/core/document/#the-_id-field), however if not provided a default `_id` of type [`ObjectId`](https://www.mongodb.com/docs/manual/reference/bson-types/#std-label-objectid) will be generated. When running the above you will get a different value for `_id`, or you may choose to explicitly set it to any value you like!

Feel free to give the above example a spin using your existing MongoDB cluster or [MongoDB Atlas](https://www.mongodb.com/atlas) cluster. If you don't have a MongoDB Atlas cluster, [sign up for an always free Free Tier](https://www.mongodb.com/cloud/atlas/signup) cluster to get started.

## Installation

The MongoDB Ruby Driver is hosted at [RubyGems](https://rubygems.org/gems/mongo), or if you'd like to explore the source code it can be found on [GitHub](https://github.com/mongodb/mongo-ruby-driver).

To simplify the example above we used `bundler/inline` to provide a [single-file solution using Bundler](https://bundler.io/guides/bundler_in_a_single_file_ruby_script.html), however the `mongo` gem can be just as easily added to an existing `Gemfile` or installed via [`gem install mongo`](https://guides.rubygems.org/rubygems-basics/#installing-gems).


## Basic CRUD operations

Our sample above demonstrated how to quickly create and read a document. Updating and deleting documents are just as painless as shown below:

```ruby
# set a new field 'counter' to 1
collection.update_one({ _id: BSON::ObjectId('62d83d9dceb023b20aff228a')}, :"$set" => { counter: 1 })

puts collection.find.first
# => {"_id"=>BSON::ObjectId('62d83d9dceb023b20aff228a'), "bar"=>"baz", "counter"=>1}

# increment the field 'counter' by one
collection.update_one({ _id: BSON::ObjectId('62d83d9dceb023b20aff228a')}, :"$inc" => { counter: 1 })

puts collection.find.first
# => {"_id"=>BSON::ObjectId('62d83d9dceb023b20aff228a'), "bar"=>"baz", "counter"=>2}

# remove the test document
collection.delete_one({ _id: BSON::ObjectId('62d83d9dceb023b20aff228a') })
```

## Object Document Mapper

Though all interaction with your Atlas cluster can be done directly using the MongoDB Ruby Driver, most developers prefer a layer of abstraction such as an [ORM or ODM](https://medium.com/spidernitt/orm-and-odm-a-brief-introduction-369046ec57eb). Ruby developers can use the [Mongoid ODM](https://www.mongodb.com/docs/mongoid/current/) to easily model MongoDB collections in their code and simplify interaction using a fluid API akin to [Active Record's Query Interface](https://guides.rubyonrails.org/active_record_querying.html).

The following example adapts the previous example to use Mongoid:
```ruby
require 'bundler/inline'

gemfile do
  source 'https://rubygems.org'

  gem 'mongoid'
end

Mongoid.configure do |config|
  config.clients.default = { uri: "mongodb+srv://username:password@mycluster.mongodb.net/test" }
end

class Foo
  include Mongoid::Document

  field :bar, type: String
  field :counter, type: Integer, default: 1
end

# create a new instance of 'Foo', which will assign a default value of 1 to the 'counter' field
foo = Foo.create bar: "baz"

puts foo.inspect
# => <Foo _id: 62d84be3ceb023b76a48df90, bar: "baz", counter: 1>

# interact with the instance variable 'foo' and modify fields programmatically
foo.counter += 1

# save the instance of the model, persisting changes back to MongoDB
foo.save!

puts foo.inspect
# => <Foo _id: 62d84be3ceb023b76a48df90, bar: "baz", counter: 2>
```

## Summary

Whether you're using Ruby/Rails to build a script/automation tool, a new web application or even the next [Coinbase](https://blog.coinbase.com/scaling-connections-with-ruby-and-mongodb-99204dbf8857) MongoDB has you covered with both a Driver that simplifies interaction with your data or an ODM that seamlessly integrates your data model with your application code.

## Conclusion

Interacting with your MongoDB data via Ruby - either using the Driver or the ODM - is straightforward, but you can also directly interface with your data from MongoDB Atlas using the built in [Data Explorer](https://www.mongodb.com/docs/atlas/atlas-ui/). Depending on your preferences though, there are options:

* [MongoDB for Visual Studio Code](https://www.mongodb.com/products/vs-code) allows you to connect to your MongoDB instance and enables you to interact in a way that fits into your native workflow and development tools. You can navigate and browse your MongoDB databases and collections, and prototype queries and aggregations for use in your applications.

* [MongoDB Compass](https://www.mongodb.com/products/compass) is an interactive tool for querying, optimizing, and analyzing your MongoDB data. Get key insights, drag and drop to build pipelines, and more.

* [Studio 3T](https://studio3t.com/) is an extremely easy to use 3rd party GUI for interacting with your MongoDB data.

* [MongoDB Atlas Data API](https://www.mongodb.com/docs/atlas/api/data-api/) lets you read and write data in Atlas with standard HTTPS requests. To use the Data API, all you need is an HTTPS client and a valid API key.

Ruby was recently added as a [language export option to both MongoDB Compass and the MongoDB VS Code Extension](https://www.mongodb.com/blog/post/ruby-added-mongodb-export-language-compass-vs-code). Using this integration you can easily convert an [aggregation pipeline](https://www.mongodb.com/docs/manual/core/aggregation-pipeline/) from either tool into code you can copy/paste into your Ruby application.